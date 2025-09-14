from django.contrib import admin
from .models import Author, Post, Comment


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'user', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'email']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'status', 'active', 'published_date']
    list_filter = ['status', 'active', 'published_date', 'author']
    search_fields = ['title', 'content']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'published_date'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['post', 'user', 'is_approved', 'created']
    list_filter = ['is_approved', 'created', 'post']
    search_fields = ['content']
    readonly_fields = ['created']
