from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.utils import timezone
from django.db.models import Count, ExpressionWrapper, FloatField, F
from datetime import timedelta

from .models import Hashtag, BlogPost
from .forms import PostForm

class Feed(View):
    model = BlogPost
    template_name = 'blogs/feed.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        time_threshold = timezone.now() - timedelta(days=7)
        
        queryset = BlogPost.objects.filter(created_at__gte=time_threshold).select_related('owner')
        
        queryset = queryset.annotate(
            likes_cnt=Count('likes', distinct=True),
            comments_cnt=Count('comments', distinct=True),
            views_cnt=Count('views', distinct=True)
        )
        
        queryset = queryset.annotate(
            rating_score=ExpressionWrapper(
                F('likes_cnt') * 10 + F('comments_cnt') * 5 + F('views_cnt') * 1,
                output_field=FloatField()
            )
        )
        
        return queryset.order_by('-rating_score', '-created_at')

    def get(self, request):
        self.object_list = self.get_queryset()
        return render(request=self.request, template_name="blogs/post_list.html", context={"page_title": "Лента", "posts": self.object_list})

class HashtagPosts(View):

    def get(self, request, slug):
        hashtag = get_object_or_404(
            Hashtag,
            slug=slug
        )

        posts_queryset = (
            BlogPost.objects
            .filter(hashtags=hashtag)
            .select_related('owner')
            .prefetch_related(
                'hashtags',
                'likes',
                'views',
                'comments',
                'files'
            )
            .annotate(
                likes_cnt=Count('likes', distinct=True),
                comments_cnt=Count('comments', distinct=True),
                views_cnt=Count('views', distinct=True),
            )
            .order_by('-created_at')
        )

        paginator = Paginator(posts_queryset, 20)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)

        context = {
            'page_title': f'#{hashtag.text}',
            'hashtag': hashtag,
            'posts': page_obj.object_list,
            'page_obj': page_obj,
        }

        return render(
            request,
            'blogs/posts_list.html',
            context
        )

class CreatePost(View):
    model = BlogPost

    def get(self, request):
        form = PostForm()
        return render(request=request, template_name="blogs/post_create.html", context={"page_title": "Создать пост", "form": form})