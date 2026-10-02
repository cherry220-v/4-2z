from django.db import models
from django.urls import reverse
from django.conf import settings
import os

class Hashtag(models.Model):
    text = models.CharField(max_length=30, verbose_name="Хэштег")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    created_at = models.DateTimeField(verbose_name="Дата создания", auto_now=True)
    slug = models.SlugField(null=False, unique=True)

    class Meta:
        verbose_name = "Хэштег"
        verbose_name_plural = "Хэштеги"

    def __str__(self):
        return self.text

    def get_absolute_url(self):
        return reverse('hashtag_posts', kwargs={'slug': self.slug})

class ReportReason(models.Model):
    text = models.CharField(max_length=30, verbose_name="Хэштег")
    created_at = models.DateTimeField(verbose_name="Дата создания", auto_now=True)

    class Meta:
        verbose_name = "Жалоба"
        verbose_name_plural = "Жалобы"

    def __str__(self):
        return self.text
    
class BlogPost(models.Model):
    title = models.CharField(max_length=50, null=False, blank=False, verbose_name="Заголовок поста")
    text = models.TextField(max_length=5000, default="-", verbose_name="Текст поста")
    owner = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True)
    
    comments_allowed = models.BooleanField(verbose_name="Разрешено ли комментировать", default=True)

    files = models.ManyToManyField("blogs.File", blank=True, related_name="post_file", verbose_name="Прикрепленные файлы")
    hashtags = models.ManyToManyField("blogs.Hashtag", blank=True, related_name="hashtag_posts", verbose_name="Хэштеги")
    likes = models.ManyToManyField("users.User", blank=True, related_name="liked_posts", verbose_name="Лайки")
    views = models.ManyToManyField("users.User", blank=True, related_name="viewed_posts", verbose_name="Просмотры")
    reports = models.ManyToManyField("blogs.ReportReason", blank=True, related_name="report_posts", verbose_name="Жалобы")
    is_published = models.BooleanField(verbose_name="Опубликовано", default=False)

    created_at = models.DateTimeField(verbose_name="Дата создания", auto_now=True)
    updated_at = models.DateTimeField(verbose_name="Дата изменения", null=True)

    class Meta:
        verbose_name = "Пост"
        verbose_name_plural = "Посты"

    def __str__(self):
        return self.title

class Draft(models.Model):
    post = models.OneToOneField(
        "blogs.BlogPost",
        on_delete=models.CASCADE,
        related_name="draft",
        verbose_name="Пост"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата изменения"
    )

class File(models.Model):
    post = models.ForeignKey("blogs.BlogPost", on_delete=models.CASCADE)
    title = models.CharField(max_length=50, null=False, verbose_name="Заголовок файла")
    file_path = models.FileField(upload_to=os.path.join(settings.MEDIA_ROOT), null=True, blank=True, verbose_name="Файл прикрепления")

    created_at = models.DateTimeField(verbose_name="Дата создания", auto_now=True)

    class Meta:
        verbose_name = "Файл"
        verbose_name_plural = "Файлы"

    def __str__(self):
        return self.title

class Comment(models.Model):
    post = models.ForeignKey("blogs.BlogPost", related_name="comments", on_delete=models.CASCADE)
    creator = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True)

    text = models.TextField(max_length=2000, verbose_name="Текст комментария", blank=False, null=False)

    created_at = models.DateTimeField(verbose_name="Дата создания", auto_now=True)

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"

    def __str__(self):
        return self.text
