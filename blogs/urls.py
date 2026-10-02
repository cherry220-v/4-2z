from django.urls import path

from .views import Feed, HashtagPosts, CreatePost

urlpatterns = [
    path('tag/<slug:slug>/', HashtagPosts.as_view(), name='blogs-post-hashtag'),
    path('search/', HashtagPosts.as_view(),          name='blogs-post-search'),
    path('', Feed.as_view(),                         name='blogs-post-list'),

    path('create/', CreatePost.as_view(),            name='blogs-post-create'),
    path('<int:pk>/', Feed.as_view(),                name='blogs-post-detail'),
    path('<int:pk>/edit/', Feed.as_view(),           name='blogs-post-edit'),
    path('<int:pk>/delete/', Feed.as_view(),         name='blogs-post-delete'),
    path('<int:pk>/report/', Feed.as_view(),         name='blogs-post-report'),

    path('<int:pk>/comment/', Feed.as_view(),        name='blogs-comment-create'),
    path('comment/<int:cid>/delete/', Feed.as_view(),name='blogs-comment-delete'),

    path('<int:pk>/view/', Feed.as_view(),           name='blogs-post-like'),
    path('<int:pk>/like/', Feed.as_view(),           name='blogs-post-view'),
]