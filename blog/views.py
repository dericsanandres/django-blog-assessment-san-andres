from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

from rest_framework import generics, permissions, filters, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend

from .models import Post, Comment, Author
from .serializers import (
    PostListSerializer, PostDetailSerializer, PostCreateSerializer,
    PostUpdateSerializer, CommentCreateSerializer
)


# Django Class-Based Views
# main blog page with paginated posts, shows 10 active published posts
class PostListView(ListView):
    model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    paginate_by = 10
    
    def get_queryset(self):
        return Post.objects.filter(active=True, status='published').select_related('author')


# individual post pages, single post with author info
class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'
    
    def get_queryset(self):
        return Post.objects.filter(active=True, status='published').select_related('author')


# lets authenticated users create posts, auto creates author profile
class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    template_name = 'blog/post_form.html'
    fields = ['title', 'content', 'status']
    success_url = reverse_lazy('blog:post_list')
    
    def form_valid(self, form):
        # Ensure user has an Author profile
        author, created = Author.objects.get_or_create(
            user=self.request.user,
            defaults={
                'name': self.request.user.get_full_name() or self.request.user.username,
                'email': self.request.user.email
            }
        )
        form.instance.author = author
        return super().form_valid(form)


# ensures only post owners can edit/delete their content, checks author.user match
class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Read permissions for any request
        if request.method in permissions.SAFE_METHODS:
            return True
        # Write permissions only to the owner
        return obj.author.user == request.user


# REST API Views
# /api/posts/ endpoint for listing and creating posts, supports filtering and search
class PostListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['author__name', 'published_date']
    search_fields = ['title', 'author__name']
    ordering_fields = ['published_date', 'title']
    ordering = ['-published_date']
    
    def get_queryset(self):
        return Post.objects.filter(active=True).select_related('author')
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PostCreateSerializer
        return PostListSerializer
    
    def perform_create(self, serializer):
        serializer.save()


# serves individual post with comments included, full detail view
class PostDetailAPIView(generics.RetrieveAPIView):
    serializer_class = PostDetailSerializer
    
    def get_queryset(self):
        return Post.objects.filter(active=True).select_related('author').prefetch_related('comments__user')


# API post editing, owner only updates title/content/active
class PostUpdateAPIView(generics.UpdateAPIView):
    serializer_class = PostUpdateSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    
    def get_queryset(self):
        return Post.objects.all().select_related('author')


# API post deletion, owner only removes entire post
class PostDeleteAPIView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    
    def get_queryset(self):
        return Post.objects.all().select_related('author')


# processes comment submissions via API, allows anonymous comments on active posts
class CommentCreateAPIView(generics.CreateAPIView):
    serializer_class = CommentCreateSerializer
    permission_classes = [permissions.AllowAny]  # Allow anonymous comments
    
    def get_queryset(self):
        return Comment.objects.all()
