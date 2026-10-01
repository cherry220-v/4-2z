from django.urls import path
from django.views import View

from .views import Feed, HashtagPosts

class TView(View): pass

urlpatterns = [
    path('tag/<slug:slug>/', HashtagPosts.as_view(), name='hashtag-posts'),
    path('', Feed.as_view(), name='posts-list'),
    path('', Feed.as_view(), name='post_create'),
    path('detail/<int:pk>/', Feed.as_view(), name='post_detail'),
    path('detail/<int:pk>/edit/', Feed.as_view(), name='post_edit'),
    path('detail/<int:pk>/delete/', Feed.as_view(), name='post_delete'),
]