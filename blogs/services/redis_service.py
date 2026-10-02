import redis
import redis.exceptions

from blogs.models import BlogPost
from users.models import User

from .redis_client import get_redis

VIEW_TTL = 3 * 60 * 60  # 3 часа


def _post_likes_add_key(post_id):
    return f"post:{post_id}:likes:add"


def _post_likes_remove_key(post_id):
    return f"post:{post_id}:likes:remove"


def _post_views_add_key(post_id):
    return f"post:{post_id}:views:add"


def _post_view_lock_key(post_id, user_id):
    return f"view:{post_id}:{user_id}"


def _post_notification_likes_key(post_id):
    return f"notification:post:{post_id}:likes"


def like_post(post_id, user_id):
    """
    Ставит лайк посту.

    Redis:
        SREM post:{id}:likes:remove user_id
        SADD post:{id}:likes:add user_id
        SADD notification:post:{id}:likes user_id

    Возвращает:
        True  - операция успешно записана в Redis
        False - Redis недоступен / произошла ошибка
    """

    r = get_redis()

    if r is None:
        return False

    add_key = _post_likes_add_key(post_id)
    remove_key = _post_likes_remove_key(post_id)
    notification_key = _post_notification_likes_key(post_id)

    try:
        pipe = r.pipeline(transaction=True)

        pipe.srem(remove_key, user_id)

        pipe.sadd(add_key, user_id)

        pipe.sadd(notification_key, user_id)

        pipe.execute()

        return True

    except redis.exceptions.RedisError:
        return False


def unlike_post(post_id, user_id):
    """
    Убирает лайк с поста.

    Redis:
        SREM post:{id}:likes:add user_id
        SADD post:{id}:likes:remove user_id

    Возвращает:
        True  - операция успешно записана
        False - Redis недоступен / произошла ошибка
    """

    r = get_redis()

    if r is None:
        return False

    add_key = _post_likes_add_key(post_id)
    remove_key = _post_likes_remove_key(post_id)

    try:
        pipe = r.pipeline(transaction=True)

        pipe.srem(add_key, user_id)

        pipe.sadd(remove_key, user_id)

        pipe.execute()

        return True

    except redis.exceptions.RedisError:
        return False


def view_post(post_id, user_id):
    """
    Регистрирует просмотр поста.

    Один пользователь может засчитать просмотр
    одного поста максимум один раз за 3 часа.

    Используется:

        SET view:{post_id}:{user_id} 1 NX EX 10800

    Если ключ уже существует:
        просмотр не добавляется.

    Возвращает:

        True  - новый просмотр зарегистрирован
        False - просмотр уже был / Redis недоступен
    """

    r = get_redis()

    if r is None:
        return False

    lock_key = _post_view_lock_key(post_id, user_id)
    views_key = _post_views_add_key(post_id)

    try:
        created = r.set(
            lock_key,
            "1",
            nx=True,
            ex=VIEW_TTL,
        )

        if not created:
            return False

        r.sadd(views_key, user_id)

        return True

    except redis.exceptions.RedisError:
        return False


def get_post_stats(post_id):
    """
    Возвращает актуальную статистику поста.

    Учитываются:
        - данные из MySQL;
        - pending likes в Redis;
        - pending unlikes в Redis;
        - pending views в Redis.

    Результат:

        {
            "likes": int,
            "views": int,
        }
    """

    try:
        post = (
            BlogPost.objects
            .prefetch_related("likes", "views")
            .get(pk=post_id)
        )
    except BlogPost.DoesNotExist:
        return None

    db_likes = post.likes.count()
    db_views = post.views.count()

    r = get_redis()

    if r is None:
        return {
            "likes": db_likes,
            "views": db_views,
        }

    try:
        add_key = _post_likes_add_key(post_id)
        remove_key = _post_likes_remove_key(post_id)
        views_key = _post_views_add_key(post_id)

        pending_likes = r.scard(add_key) or 0
        pending_unlikes = r.scard(remove_key) or 0
        pending_views = r.scard(views_key) or 0

        likes = db_likes + pending_likes - pending_unlikes
        views = db_views + pending_views

        likes = max(likes, 0)
        views = max(views, 0)

        return {
            "likes": likes,
            "views": views,
        }

    except redis.exceptions.RedisError:
        return {
            "likes": db_likes,
            "views": db_views,
        }

def get_like_notification_users(post_id):
    """
    Возвращает пользователей, которые поставили лайк посту
    и были записаны в Redis notification set.

    Redis хранит только ID:

        notification:post:{id}:likes
            -> {1, 15, 28, 42, ...}

    Затем ID преобразуются в User QuerySet.

    Возвращает:
        QuerySet[User]

    При ошибке Redis:
        пустой QuerySet.
    """

    r = get_redis()

    if r is None:
        return User.objects.none()

    key = _post_notification_likes_key(post_id)

    try:
        user_ids = r.smembers(key)

        if not user_ids:
            return User.objects.none()

        user_ids = list(user_ids)

        return User.objects.filter(
            id__in=user_ids
        )

    except redis.exceptions.RedisError:
        return User.objects.none()