from django.contrib import admin
from django.db.models import Count

from .models import (
    Hashtag,
    ReportReason,
    BlogPost,
    File,
    Comment,
)

class ReportsCountFilter(admin.SimpleListFilter):
    title = 'Количество жалоб'
    parameter_name = 'reports_qty'

    def lookups(self, request, model_admin):
        return (
            ('zero', 'Нет жалоб'),
            ('has_any', 'Есть жалобы'),
            ('many', 'Много жалоб (больше 5)'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'zero':
            return queryset.filter(_reports_count=0)
        if self.value() == 'has_any':
            return queryset.filter(_reports_count__gt=0)
        if self.value() == 'many':
            return queryset.filter(_reports_count__gt=5)
        return queryset

@admin.register(Hashtag)
class HashtagAdmin(admin.ModelAdmin):
    list_display = ('text', 'is_active')
    prepopulated_fields = {'slug': ('text',)}
    search_fields = ('text',) 

@admin.register(ReportReason)
class ReportReasonAdmin(admin.ModelAdmin):
    list_display = ('text', 'created_at')
    list_filter = ('created_at',)

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'text', 'get_user_email', 'views_count', 'likes_count', 'files_count', 'reports_count', 'get_tags', 'created_at')
    filter_horizontal = ('hashtags',)
    list_filter = ('created_at', ReportsCountFilter)
    search_fields = ('title', 'hashtags__text__icontains', 'owner__email', 'owner__username')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.select_related('owner').prefetch_related('hashtags')
        queryset = queryset.annotate(
            _files_count=Count('files', distinct=True),
            _likes_count=Count('likes', distinct=True),
            _views_count=Count('views', distinct=True),
            _reports_count=Count('reports', distinct=True),
        )
        return queryset

    @admin.display(ordering='owner__email', description='Email пользователя')
    def get_user_email(self, obj):
        return obj.owner.email

    @admin.display(description='Хэштеги')
    def get_tags(self, obj):
        return ', '.join([t.text for t in obj.hashtags.all()])

    @admin.display(description='Лайки', ordering='_likes_count')
    def likes_count(self, obj):
        return obj._likes_count

    @admin.display(description='Просмотры', ordering='_views_count')
    def views_count(self, obj):
        return obj._views_count

    @admin.display(description='Файлы', ordering='_files_count')
    def files_count(self, obj):
        return obj._files_count

    @admin.display(description='Жалобы', ordering='_reports_count')
    def reports_count(self, obj):
        return obj._reports_count

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("get_post_title", "get_user_email", "cutted_text", "created_at")
    search_fields = ("post__title", "creator__email", "creator__username")
    list_filter = ("created_at",)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('creator', 'post')

    @admin.display(ordering='creator__email', description='Email пользователя')
    def get_user_email(self, obj):
        return obj.creator.email

    @admin.display(ordering="post__title", description="Название поста")
    def get_post_title(self, obj):
        return obj.post.title
    
    @admin.display(ordering="text", description="Текст")
    def cutted_text(self, obj):
        if len(obj.text) > 35:
            return f"{obj.text[:35]}..."
        return obj.text

@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = ("get_post_title", "file_path", "created_at")
    list_filter = ("created_at",)
    search_fields = ("post__title", "file_path")

    @admin.display(ordering="post__title", description="Название поста")
    def get_post_title(self, obj):
        return obj.post.title