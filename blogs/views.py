from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView, ListView
from django.views.generic.edit import FormMixin
from django.utils import timezone
from django.db.models import Count, ExpressionWrapper, FloatField, F
from django.urls import reverse_lazy
from django.http import JsonResponse
from datetime import timedelta

from .models import Hashtag, BlogPost, File, Comment
from .forms import PostForm, CommentForm
from .services.redis_service import *

class Feed(ListView):
    model = BlogPost
    template_name = 'blogs/posts_list.html'
    context_object_name = 'posts'
    paginate_by = 10
    
    def get_queryset(self):
        time_threshold = timezone.now() - timedelta(days=7)
        
        queryset = ( 
            BlogPost.objects
            .filter(created_at__gte=time_threshold, is_published=True)
            .select_related('owner')
            .prefetch_related('hashtags', 'files')
        )
        
        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        current_page_posts = context['posts']
        post_ids = [post.id for post in current_page_posts]
        
        redis_stats = {}
        for post_id in post_ids: redis_stats[post_id] = get_post_stats(post_id)
        
        for post in current_page_posts:
            stats = redis_stats.get(post.id, {'likes': 0, 'views': 0, 'comments': 0})
            post.likes_cnt = stats['likes']
            post.views_cnt = stats['views']
            post.comments_cnt = 0# stats['comments'] 
            
            post.rating_score = post.likes_cnt * 10 + post.comments_cnt * 5 + post.views_cnt

        context['page_title'] = 'Лента'
        return context
    
class HashtagPosts(ListView):
    model = BlogPost
    template_name = 'blogs/posts_list.html'
    context_object_name = 'posts'
    paginate_by = 10
    
    def get_queryset(self, slug):
        hashtag = get_object_or_404( Hashtag, slug=slug )
        queryset = (
            BlogPost.objects
            .filter( hashtags=hashtag, is_published=True )
            .select_related('owner')
            .prefetch_related( 'hashtags', 'files' )
            .order_by('-created_at')
            )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        current_page_posts = context['posts']
        post_ids = [post.id for post in current_page_posts]
        
        redis_stats = {}
        for post_id in post_ids: redis_stats[post_id] = get_post_stats(post_id)
        
        for post in current_page_posts:
            stats = redis_stats.get(post.id, {'likes': 0, 'views': 0, 'comments': 0})
            post.likes_cnt = stats['likes']
            post.views_cnt = stats['views']
            post.comments_cnt = 0# stats['comments'] 
            
            post.rating_score = post.likes_cnt * 10 + post.comments_cnt * 5 + post.views_cnt

        context['page_title'] = f'#{post.hashtag.text}'
        return context
    
    def get(self, request, slug):
        hashtag = get_object_or_404( Hashtag, slug=slug )
        posts = self.get_queryset(slug)
        context = { 'page_title': f'#{hashtag.text}', 'hashtag': hashtag, 'posts': posts, }
        return render( request, self.template_name, context )

class CreatePost(LoginRequiredMixin, CreateView):
    model = BlogPost
    form_class = PostForm
    template_name = 'blogs/post_create.html'

    def form_valid(self, form):
        post = form.save(commit=False)
        post.owner = self.request.user
        post.save()

        for uploaded_file in form.cleaned_data['files']:
            File.objects.create(
                post=post,
                title=uploaded_file.name[:50],
                file_path=uploaded_file
            )

        return redirect('blogs-post-detail', pk=post.pk)
    
class PostDetail(LoginRequiredMixin, FormMixin, DetailView):
    model = BlogPost
    form_class = CommentForm
    template_name = 'blogs/post_detail.html'
    context_object_name = 'post'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.object
        context['comments'] = self.object.comments.select_related('creator').all()
        
        post_stats = get_post_stats(self.object.id)
        stats = post_stats.get(post.id, {'likes': 0, 'views': 0, 'comments': 0})
        post.likes_cnt = stats['likes']
        post.views_cnt = stats['views']
        post.comments_cnt = 0# stats['comments'] 
            
        post.rating_score = post.likes_cnt * 10 + post.comments_cnt * 5 + post.views_cnt

        context['page_title'] = f'Пост - {post.title}'
        return context

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Unauthorized'}, status=401)
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def form_valid(self, form):
        comment = form.save(commit=False)
        comment.post = self.object
        comment.creator = self.request.user
        comment.save()
        
        return JsonResponse({
            'success': 1,
            'comment': {
                'id': comment.id,
                'body': comment.text,
                'creator': comment.creator.username,
            }
        }, status=201)

    def form_invalid(self, form):
        return JsonResponse({
            'success': 0,
            'errors': form.errors
        }, status=400)

    def get_success_url(self):
        return reverse_lazy('blogs-post-detail', kwargs={'pk': self.object.pk})

class PostEdit(LoginRequiredMixin, UpdateView):
    model = BlogPost
    form_class = PostForm
    template_name = 'blogs/post_edit.html'
    context_object_name = 'post'

    def form_valid(self, form):
        post = form.save()

        for uploaded_file in form.cleaned_data['files']:
            File.objects.create(
                post=post,
                title=uploaded_file.name[:50],
                file_path=uploaded_file
            )

        return redirect('blogs-post-detail', pk=post.pk)

class PostDelete(LoginRequiredMixin, DeleteView):
    model = BlogPost
    template_name = 'blogs/post_confirm_delete.html'
    context_object_name = 'post'
    success_url = reverse_lazy('blogs-post-list')
    
class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment
    
    def get_success_url(self):
        return reverse_lazy('blogs-post-detail', kwargs={'pk': self.object.post.pk})

    def test_func(self):
        comment = self.get_object()
        return self.request.user == comment.creator
    
@require_POST
def track_view_ajax(request, post_id):
    post = get_object_or_404(BlogPost, id=post_id)
    
    view_post(post_id=post.id, user_id=request.user.id)
    
    counts = get_post_stats(post_id=post.id) 
    
    return JsonResponse({
        'status': 'success',
        'views_count': counts.get('views', 0)
    })

@login_required
@require_POST
def toggle_like_ajax(request, post_id):
    post = get_object_or_404(BlogPost, id=post_id)
    
    is_liked = like_post(post_id=post.id, user_id=request.user.id)
    counts = get_post_stats(post_id=post.id)
    
    return JsonResponse({
        'status': 'success',
        'is_liked': is_liked,
        'likes_count': counts.get('likes', 0)
    })