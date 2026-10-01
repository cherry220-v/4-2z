from rest_framework import serializers
from .models import BlogPost, Hashtag

class HashtagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hashtag
        fields = ['text', 'slug']

class BlogPostSerializer(serializers.ModelSerializer):
    author_email = serializers.EmailField(source='owner.email', read_only=True)
    created_at = serializers.DateTimeField(format="%d.%m.%Y %H:%M")
    views_count = serializers.IntegerField(source='views.count', read_only=True)
    likes_count = serializers.IntegerField(source='likes.count', read_only=True)
    hashtags = HashtagSerializer(many=True, read_only=True)

    class Meta:
        model = BlogPost
        fields = ['id', 'title', 'text', 'author_email', 'created_at', 'hashtags', 'views_count', 'likes_count']