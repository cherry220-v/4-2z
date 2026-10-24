from django.urls import path

from .views import Feed, HashtagPosts, CreatePost, PostDetail, PostDelete, PostEdit

urlpatterns = [
    path('tag/<slug:slug>/', HashtagPosts.as_view(), name='blogs-post-hashtag'),
    path('search/', HashtagPosts.as_view(),          name='blogs-post-search'),
    path('', Feed.as_view(),                         name='blogs-post-list'),

    path('create/', CreatePost.as_view(),            name='blogs-post-create'),
    path('<int:pk>/', PostDetail.as_view(),          name='blogs-post-detail'),
    path('<int:pk>/edit/', PostEdit.as_view(),       name='blogs-post-edit'),
    path('<int:pk>/delete/', PostDelete.as_view(),   name='blogs-post-delete'),
    path('<int:pk>/report/', Feed.as_view(),         name='blogs-post-report'),

    path('<int:pk>/comment/', PostDetail.as_view(),        name='blogs-comment-create'),
    path('comment/<int:cid>/delete/', Feed.as_view(),name='blogs-comment-delete'),

    path('<int:pk>/view/', Feed.as_view(),           name='blogs-post-like'),
    path('<int:pk>/like/', Feed.as_view(),           name='blogs-post-view'),
]