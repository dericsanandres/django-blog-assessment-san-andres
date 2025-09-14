import pytest
from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from blog.models import Author, Post, Comment


@pytest.fixture
def user():
    return User.objects.create_user(
        username='testuser', 
        email='test@example.com', 
        password='testpass123'
    )


@pytest.fixture
def author(user):
    return Author.objects.create(
        name='Test Author',
        email=user.email,
        user=user
    )


@pytest.fixture
def active_post(author):
    return Post.objects.create(
        title='Active Post',
        content='This is an active post content',
        author=author,
        status='published',
        active=True,
        published_date=timezone.now()
    )


@pytest.fixture
def inactive_post(author):
    return Post.objects.create(
        title='Inactive Post', 
        content='This post is inactive',
        author=author,
        status='published',
        active=False,
        published_date=timezone.now()
    )


@pytest.fixture
def old_post(author):
    old_date = timezone.now() - timedelta(days=30)
    return Post.objects.create(
        title='Old Post',
        content='This is an old post',
        author=author,
        status='published',
        active=True,
        published_date=old_date
    )


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
class TestPostListView:
    
    def test_post_list_shows_only_active_posts(self, active_post, inactive_post):
        from django.test import Client
        
        client = Client()
        response = client.get(reverse('blog:post_list'))
        
        assert response.status_code == 200, "Post list page should load successfully"
        assert active_post.title in response.content.decode(), "Active post should appear in the list"
        assert inactive_post.title not in response.content.decode(), "Inactive post should not appear in the list"
    
    def test_api_post_list_shows_only_active_posts(self, api_client, active_post, inactive_post):
        response = api_client.get('/api/posts/')
        
        assert response.status_code == 200, "API should return success status"
        
        titles = [post['title'] for post in response.data['results']]
        assert active_post.title in titles, "Active post should be in API response"
        assert inactive_post.title not in titles, "Inactive post should not be in API response"


@pytest.mark.django_db  
class TestPostListFiltering:
    
    def test_api_post_list_date_range_filtering(self, api_client, active_post, old_post):
        recent_date = (timezone.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        
        response = api_client.get(f'/api/posts/?published_date__gte={recent_date}')
        
        assert response.status_code == 200, "Filtered API request should succeed"
        
        titles = [post['title'] for post in response.data['results']]
        assert active_post.title in titles, "Recent post should appear in date-filtered results"
        assert old_post.title not in titles, "Old post should not appear in recent date filter"
        
    def test_api_post_list_author_filtering(self, api_client, active_post):
        response = api_client.get(f'/api/posts/?author__name={active_post.author.name}')
        
        assert response.status_code == 200, "Author filtering should work"
        assert len(response.data['results']) >= 1, "Should return posts by the specified author"
        assert response.data['results'][0]['author_name'] == active_post.author.name, "Returned post should match author filter"


@pytest.mark.django_db
class TestPostCreationAPI:
    
    def test_authenticated_user_can_create_post(self, api_client, user):
        api_client.force_authenticate(user=user)
        
        post_data = {
            'title': 'New Test Post',
            'content': 'This is a test post created via API',
            'author_name': 'API Test Author',
            'published_date': timezone.now().isoformat()
        }
        
        response = api_client.post('/api/posts/', post_data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED, f"Post creation should succeed, got {response.status_code}: {response.data}"
        
        created_post = Post.objects.get(title='New Test Post')
        assert created_post.content == post_data['content'], "Post content should match submitted data"
        assert created_post.author.name == 'API Test Author', "Author should be created or linked correctly"
        assert created_post.author.user == user, "Author should be linked to the authenticated user"
    
    def test_unauthenticated_user_cannot_create_post(self, api_client):
        post_data = {
            'title': 'Unauthorized Post',
            'content': 'This should not be created',
            'author_name': 'Unauthorized User'
        }
        
        response = api_client.post('/api/posts/', post_data, format='json')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN, "Unauthenticated users should not be able to create posts"
        assert not Post.objects.filter(title='Unauthorized Post').exists(), "Post should not be created without authentication"


@pytest.mark.django_db
class TestPostEditingAPI:
    
    def test_author_can_edit_own_post(self, api_client, user, active_post):
        api_client.force_authenticate(user=user)
        
        update_data = {
            'title': 'Updated Post Title',
            'content': 'Updated post content',
            'active': False
        }
        
        response = api_client.patch(f'/api/posts/{active_post.id}/edit/', update_data, format='json')
        
        assert response.status_code == status.HTTP_200_OK, f"Post update should succeed, got {response.status_code}: {response.data}"
        
        updated_post = Post.objects.get(id=active_post.id)
        assert updated_post.title == 'Updated Post Title', "Post title should be updated"
        assert updated_post.content == 'Updated post content', "Post content should be updated"  
        assert updated_post.active == False, "Post active status should be updated"
    
    def test_non_author_cannot_edit_post(self, api_client, active_post):
        other_user = User.objects.create_user(username='other', email='other@test.com', password='pass')
        api_client.force_authenticate(user=other_user)
        
        update_data = {'title': 'Hacked Title'}
        response = api_client.patch(f'/api/posts/{active_post.id}/edit/', update_data, format='json')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN, "Non-authors should not be able to edit posts"
        
        unchanged_post = Post.objects.get(id=active_post.id)
        assert unchanged_post.title == active_post.title, "Post title should remain unchanged"


@pytest.mark.django_db
class TestPostDeletionAPI:
    
    def test_author_can_delete_own_post(self, api_client, user, active_post):
        api_client.force_authenticate(user=user)
        post_id = active_post.id
        
        response = api_client.delete(f'/api/posts/{post_id}/delete/')
        
        assert response.status_code == status.HTTP_204_NO_CONTENT, f"Post deletion should succeed, got {response.status_code}"
        assert not Post.objects.filter(id=post_id).exists(), "Post should be completely removed from database"
    
    def test_non_author_cannot_delete_post(self, api_client, active_post):
        other_user = User.objects.create_user(username='deleter', email='del@test.com', password='pass')
        api_client.force_authenticate(user=other_user)
        
        response = api_client.delete(f'/api/posts/{active_post.id}/delete/')
        
        assert response.status_code == status.HTTP_403_FORBIDDEN, "Non-authors should not be able to delete posts"
        assert Post.objects.filter(id=active_post.id).exists(), "Post should still exist in database"


@pytest.mark.django_db
class TestCommentCreationAPI:
    
    def test_authenticated_user_can_create_comment(self, api_client, user, active_post):
        api_client.force_authenticate(user=user)
        
        comment_data = {
            'post': active_post.id,
            'content': 'This is a test comment from authenticated user'
        }
        
        response = api_client.post('/api/comments/', comment_data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED, f"Comment creation should succeed, got {response.status_code}: {response.data}"
        
        created_comment = Comment.objects.get(content=comment_data['content'])
        assert created_comment.post == active_post, "Comment should be linked to the correct post"
        assert created_comment.user == user, "Comment should be linked to the authenticated user"
        assert created_comment.is_approved == False, "New comments should default to unapproved"
    
    def test_anonymous_user_can_create_comment(self, api_client, active_post):
        
        comment_data = {
            'post': active_post.id,
            'content': 'This is an anonymous comment'
        }
        
        response = api_client.post('/api/comments/', comment_data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED, f"Anonymous comment creation should succeed, got {response.status_code}: {response.data}"
        
        created_comment = Comment.objects.get(content=comment_data['content'])
        assert created_comment.post == active_post, "Anonymous comment should be linked to the correct post"
        assert created_comment.user is None, "Anonymous comment should have no user linked"
        assert created_comment.is_approved == False, "Anonymous comments should default to unapproved"
    
    def test_cannot_comment_on_inactive_post(self, api_client, user, inactive_post):
        api_client.force_authenticate(user=user)
        
        comment_data = {
            'post': inactive_post.id,
            'content': 'This comment should fail'
        }
        
        response = api_client.post('/api/comments/', comment_data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST, "Comment creation on inactive post should fail"
        assert 'Comments can only be created on active posts' in str(response.data), "Should provide helpful error message"
        assert not Comment.objects.filter(content=comment_data['content']).exists(), "Comment should not be created on inactive post"