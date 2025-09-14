from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Author(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'blog_author'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['user']),
        ]
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Post(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]
    
    title = models.CharField(max_length=200)
    content = models.TextField()
    published_date = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='posts')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'blog_post'
        indexes = [
            models.Index(fields=['author']),
            models.Index(fields=['status']),
            models.Index(fields=['active']),
            models.Index(fields=['published_date']),
            models.Index(fields=['status', 'active']),  # compound index for filtering
        ]
        ordering = ['-published_date']
    
    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created = models.DateTimeField(default=timezone.now)
    is_approved = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'blog_comment'
        indexes = [
            models.Index(fields=['post']),
            models.Index(fields=['user']),
            models.Index(fields=['created']),
            models.Index(fields=['is_approved']),
            models.Index(fields=['post', 'is_approved']),  # for filtering approved comments per post
        ]
        ordering = ['-created']
    
    def __str__(self):
        return f'Comment on "{self.post.title}" by {self.user.username if self.user else "Anonymous"}'
