from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Author, Post, Comment


# basic author info for API responses, returns id/name/email
class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ['id', 'name', 'email']


# comment data when showing them in post details, includes username or anonymous
class CommentSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = ['id', 'content', 'user', 'user_name', 'created', 'is_approved']
        read_only_fields = ['created', 'is_approved']
    
    def get_user_name(self, obj):
        return obj.user.username if obj.user else 'Anonymous'


# lightweight version for post listings without heavy data, just title/content/author
class PostListSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.name', read_only=True)
    
    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'published_date', 'author_name']


# full post details including all comments, everything for single view
class PostDetailSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.name', read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    
    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'published_date', 'author_name', 
                 'status', 'active', 'comments']


# handles new post creation via API, accepts author name and creates author if needed
class PostCreateSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(write_only=True)
    
    class Meta:
        model = Post
        fields = ['title', 'content', 'published_date', 'author_name']
    
    def create(self, validated_data):
        author_name = validated_data.pop('author_name')
        
        # Find or create author based on the authenticated user
        user = self.context['request'].user
        try:
            author = Author.objects.get(user=user)
            # Update author name if different
            if author.name != author_name:
                author.name = author_name
                author.save()
        except Author.DoesNotExist:
            author = Author.objects.create(
                name=author_name,
                email=user.email,
                user=user
            )
        
        validated_data['author'] = author
        return Post.objects.create(**validated_data)


# editing posts restricts to safe fields only, title/content/active allowed
class PostUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['title', 'content', 'active']


# new comment submissions, validates post is active before creating
class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['post', 'content', 'user']
        read_only_fields = ['user']
    
    def validate_post(self, value):
        if not value.active:
            raise serializers.ValidationError(
                "Comments can only be created on active posts."
            )
        return value
    
    def create(self, validated_data):
        # Set user from request context if authenticated
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['user'] = request.user
        
        return Comment.objects.create(**validated_data)