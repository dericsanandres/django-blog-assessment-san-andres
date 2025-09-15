from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    # Django Class-Based Views
    path('', views.PostListView.as_view(), name='post_list'),
    path('post/<int:pk>/', views.PostDetailView.as_view(), name='post_detail'),
    path('post/create/', views.PostCreateView.as_view(), name='post_create'),
    path('post/<int:pk>/edit/', views.PostEditView.as_view(), name='post_edit'),
    path('post/<int:pk>/delete/', views.PostDeleteView.as_view(), name='post_delete'),
    
    # REST API Endpoints
    path('api/posts/', views.PostListCreateAPIView.as_view(), name='api_post_list_create'),
    path('api/posts/<int:pk>/', views.PostDetailAPIView.as_view(), name='api_post_detail'),
    path('api/posts/<int:pk>/edit/', views.PostUpdateAPIView.as_view(), name='api_post_update'),
    path('api/posts/<int:pk>/delete/', views.PostDeleteAPIView.as_view(), name='api_post_delete'),
    path('api/comments/', views.CommentCreateAPIView.as_view(), name='api_comment_create'),
]