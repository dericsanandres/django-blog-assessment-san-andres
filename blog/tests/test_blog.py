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
        
        print(f"\n[TEST] API Response Status: {response.status_code}")
        print(f"[TEST] Total posts returned: {response.data['count']}")
        print(f"[TEST] Active post '{active_post.title}' - Should appear: {active_post.active}")
        print(f"[TEST] Inactive post '{inactive_post.title}' - Should NOT appear: {inactive_post.active}")
        
        assert response.status_code == 200, "API should return success status"
        
        titles = [post['title'] for post in response.data['results']]
        print(f"[TEST] Posts in API response: {titles}")
        
        assert active_post.title in titles, "Active post should be in API response"
        assert inactive_post.title not in titles, "Inactive post should not be in API response"
        
        print(f"[TEST] ✓ Only active posts are shown in API")


@pytest.mark.django_db  
class TestPostListFiltering:
    
    def test_api_post_list_date_range_filtering(self, api_client, active_post, old_post):
        recent_date = (timezone.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        
        print(f"\n[TEST] Testing date range filtering with recent_date >= {recent_date}")
        print(f"[TEST] Recent post '{active_post.title}' published: {active_post.published_date.strftime('%Y-%m-%d')}")
        print(f"[TEST] Old post '{old_post.title}' published: {old_post.published_date.strftime('%Y-%m-%d')}")
        
        response = api_client.get(f'/api/posts/?published_date__gte={recent_date}')
        
        print(f"[TEST] Date filter API Response Status: {response.status_code}")
        print(f"[TEST] Posts matching date filter: {response.data['count']}")
        
        assert response.status_code == 200, "Filtered API request should succeed"
        
        titles = [post['title'] for post in response.data['results']]
        print(f"[TEST] Filtered results: {titles}")
        
        assert active_post.title in titles, "Recent post should appear in date-filtered results"
        assert old_post.title not in titles, "Old post should not appear in recent date filter"
        
        print(f"[TEST] ✓ Date range filtering works correctly")
        
    def test_api_post_list_author_filtering(self, api_client, active_post):
        print(f"\n[TEST] Testing author filtering for author: '{active_post.author.name}'")
        
        response = api_client.get(f'/api/posts/?author__name={active_post.author.name}')
        
        print(f"[TEST] Author filter API Response Status: {response.status_code}")
        print(f"[TEST] Posts by author '{active_post.author.name}': {response.data['count']}")
        
        assert response.status_code == 200, "Author filtering should work"
        assert len(response.data['results']) >= 1, "Should return posts by the specified author"
        
        if response.data['results']:
            print(f"[TEST] First result author: '{response.data['results'][0]['author_name']}'")
            assert response.data['results'][0]['author_name'] == active_post.author.name, "Returned post should match author filter"
        
        print(f"[TEST] ✓ Author filtering works correctly")


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
        
        print(f"\n[TEST] Testing post creation by authenticated user: {user.username}")
        print(f"[TEST] Post data: {post_data}")
        
        response = api_client.post('/api/posts/', post_data, format='json')
        
        print(f"[TEST] Post creation API Response Status: {response.status_code}")
        if response.status_code == status.HTTP_201_CREATED:
            print(f"[TEST] Created post ID: {response.data.get('id', 'N/A')}")
            print(f"[TEST] Created post title: '{response.data.get('title', 'N/A')}'")
        else:
            print(f"[TEST] Error response: {response.data}")
        
        assert response.status_code == status.HTTP_201_CREATED, f"Post creation should succeed, got {response.status_code}: {response.data}"
        
        created_post = Post.objects.get(title='New Test Post')
        print(f"[TEST] Verifying created post in database...")
        print(f"[TEST] Post content matches: {created_post.content == post_data['content']}")
        print(f"[TEST] Author name: '{created_post.author.name}'")
        print(f"[TEST] Author linked to user: {created_post.author.user == user}")
        
        assert created_post.content == post_data['content'], "Post content should match submitted data"
        assert created_post.author.name == 'API Test Author', "Author should be created or linked correctly"
        assert created_post.author.user == user, "Author should be linked to the authenticated user"
        
        print(f"[TEST] ✓ Authenticated user can create posts successfully")
    
    def test_unauthenticated_user_cannot_create_post(self, api_client):
        post_data = {
            'title': 'Unauthorized Post',
            'content': 'This should not be created',
            'author_name': 'Unauthorized User'
        }
        
        print(f"\n[TEST] Testing post creation by unauthenticated user")
        print(f"[TEST] Attempting to create: '{post_data['title']}'")
        
        response = api_client.post('/api/posts/', post_data, format='json')
        
        print(f"[TEST] Unauthenticated creation API Response Status: {response.status_code}")
        print(f"[TEST] Expected: 403 Forbidden")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN, "Unauthenticated users should not be able to create posts"
        
        post_exists = Post.objects.filter(title='Unauthorized Post').exists()
        print(f"[TEST] Post created in database: {post_exists}")
        assert not post_exists, "Post should not be created without authentication"
        
        print(f"[TEST] ✓ Unauthenticated users correctly blocked from creating posts")


@pytest.mark.django_db
class TestPostEditingAPI:
    
    def test_author_can_edit_own_post(self, api_client, user, active_post):
        api_client.force_authenticate(user=user)
        
        update_data = {
            'title': 'Updated Post Title',
            'content': 'Updated post content',
            'active': False
        }
        
        print(f"\n[TEST] Testing post editing by owner: {user.username}")
        print(f"[TEST] Original post: '{active_post.title}' (active: {active_post.active})")
        print(f"[TEST] Update data: {update_data}")
        
        response = api_client.patch(f'/api/posts/{active_post.id}/edit/', update_data, format='json')
        
        print(f"[TEST] Post edit API Response Status: {response.status_code}")
        if response.status_code == status.HTTP_200_OK:
            print(f"[TEST] Updated post response: {response.data}")
        else:
            print(f"[TEST] Error response: {response.data}")
        
        assert response.status_code == status.HTTP_200_OK, f"Post update should succeed, got {response.status_code}: {response.data}"
        
        updated_post = Post.objects.get(id=active_post.id)
        print(f"[TEST] Verifying changes in database...")
        print(f"[TEST] Title updated: '{active_post.title}' → '{updated_post.title}'")
        print(f"[TEST] Content updated: {len(updated_post.content)} chars")
        print(f"[TEST] Active status: {active_post.active} → {updated_post.active}")
        
        assert updated_post.title == 'Updated Post Title', "Post title should be updated"
        assert updated_post.content == 'Updated post content', "Post content should be updated"  
        assert updated_post.active == False, "Post active status should be updated"
        
        print(f"[TEST] ✓ Post owner can edit their own posts successfully")
    
    def test_non_author_cannot_edit_post(self, api_client, active_post):
        other_user = User.objects.create_user(username='other', email='other@test.com', password='pass')
        api_client.force_authenticate(user=other_user)
        
        print(f"\n[TEST] Testing post editing by non-owner: {other_user.username}")
        print(f"[TEST] Target post: '{active_post.title}' owned by {active_post.author.user.username}")
        print(f"[TEST] Attempting unauthorized edit...")
        
        update_data = {'title': 'Hacked Title'}
        response = api_client.patch(f'/api/posts/{active_post.id}/edit/', update_data, format='json')
        
        print(f"[TEST] Unauthorized edit API Response Status: {response.status_code}")
        print(f"[TEST] Expected: 403 Forbidden")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN, "Non-authors should not be able to edit posts"
        
        unchanged_post = Post.objects.get(id=active_post.id)
        print(f"[TEST] Post title unchanged: '{unchanged_post.title}' (original: '{active_post.title}')")
        assert unchanged_post.title == active_post.title, "Post title should remain unchanged"
        
        print(f"[TEST] ✓ Non-owners correctly blocked from editing posts")


@pytest.mark.django_db
class TestPostDeletionAPI:
    
    def test_author_can_delete_own_post(self, api_client, user, active_post):
        api_client.force_authenticate(user=user)
        post_id = active_post.id
        
        print(f"\n[TEST] Testing post deletion by owner: {user.username}")
        print(f"[TEST] Target post: '{active_post.title}' (ID: {post_id})")
        
        response = api_client.delete(f'/api/posts/{post_id}/delete/')
        
        print(f"[TEST] Post deletion API Response Status: {response.status_code}")
        print(f"[TEST] Expected: 204 No Content")
        
        assert response.status_code == status.HTTP_204_NO_CONTENT, f"Post deletion should succeed, got {response.status_code}"
        
        post_exists = Post.objects.filter(id=post_id).exists()
        print(f"[TEST] Post still exists in database: {post_exists}")
        assert not post_exists, "Post should be completely removed from database"
        
        print(f"[TEST] ✓ Post owner can delete their own posts successfully")
    
    def test_non_author_cannot_delete_post(self, api_client, active_post):
        other_user = User.objects.create_user(username='deleter', email='del@test.com', password='pass')
        api_client.force_authenticate(user=other_user)
        
        print(f"\n[TEST] Testing post deletion by non-owner: {other_user.username}")
        print(f"[TEST] Target post: '{active_post.title}' owned by {active_post.author.user.username}")
        print(f"[TEST] Attempting unauthorized deletion...")
        
        response = api_client.delete(f'/api/posts/{active_post.id}/delete/')
        
        print(f"[TEST] Unauthorized deletion API Response Status: {response.status_code}")
        print(f"[TEST] Expected: 403 Forbidden")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN, "Non-authors should not be able to delete posts"
        
        post_exists = Post.objects.filter(id=active_post.id).exists()
        print(f"[TEST] Post still exists in database: {post_exists}")
        assert post_exists, "Post should still exist in database"
        
        print(f"[TEST] ✓ Non-owners correctly blocked from deleting posts")


@pytest.mark.django_db
class TestCommentCreationAPI:
    
    def test_authenticated_user_can_create_comment(self, api_client, user, active_post):
        api_client.force_authenticate(user=user)
        
        comment_data = {
            'post': active_post.id,
            'content': 'This is a test comment from authenticated user'
        }
        
        print(f"\n[TEST] Testing comment creation by authenticated user: {user.username}")
        print(f"[TEST] Target post: '{active_post.title}' (ID: {active_post.id})")
        print(f"[TEST] Comment data: {comment_data}")
        
        response = api_client.post('/api/comments/', comment_data, format='json')
        
        print(f"[TEST] Comment creation API Response Status: {response.status_code}")
        if response.status_code == status.HTTP_201_CREATED:
            print(f"[TEST] Created comment ID: {response.data.get('id', 'N/A')}")
        else:
            print(f"[TEST] Error response: {response.data}")
        
        assert response.status_code == status.HTTP_201_CREATED, f"Comment creation should succeed, got {response.status_code}: {response.data}"
        
        created_comment = Comment.objects.get(content=comment_data['content'])
        print(f"[TEST] Verifying created comment in database...")
        print(f"[TEST] Comment linked to correct post: {created_comment.post == active_post}")
        print(f"[TEST] Comment linked to user: {created_comment.user == user}")
        print(f"[TEST] Comment approval status: {created_comment.is_approved} (should be False)")
        
        assert created_comment.post == active_post, "Comment should be linked to the correct post"
        assert created_comment.user == user, "Comment should be linked to the authenticated user"
        assert created_comment.is_approved == False, "New comments should default to unapproved"
        
        print(f"[TEST] ✓ Authenticated user can create comments successfully")
    
    def test_anonymous_user_can_create_comment(self, api_client, active_post):
        
        comment_data = {
            'post': active_post.id,
            'content': 'This is an anonymous comment'
        }
        
        print(f"\n[TEST] Testing comment creation by anonymous user")
        print(f"[TEST] Target post: '{active_post.title}' (ID: {active_post.id})")
        print(f"[TEST] Comment data: {comment_data}")
        
        response = api_client.post('/api/comments/', comment_data, format='json')
        
        print(f"[TEST] Anonymous comment creation API Response Status: {response.status_code}")
        if response.status_code == status.HTTP_201_CREATED:
            print(f"[TEST] Created anonymous comment ID: {response.data.get('id', 'N/A')}")
        else:
            print(f"[TEST] Error response: {response.data}")
        
        assert response.status_code == status.HTTP_201_CREATED, f"Anonymous comment creation should succeed, got {response.status_code}: {response.data}"
        
        created_comment = Comment.objects.get(content=comment_data['content'])
        print(f"[TEST] Verifying created anonymous comment in database...")
        print(f"[TEST] Comment linked to correct post: {created_comment.post == active_post}")
        print(f"[TEST] Comment user field: {created_comment.user} (should be None)")
        print(f"[TEST] Comment approval status: {created_comment.is_approved} (should be False)")
        
        assert created_comment.post == active_post, "Anonymous comment should be linked to the correct post"
        assert created_comment.user is None, "Anonymous comment should have no user linked"
        assert created_comment.is_approved == False, "Anonymous comments should default to unapproved"
        
        print(f"[TEST] ✓ Anonymous users can create comments successfully")
    
    def test_cannot_comment_on_inactive_post(self, api_client, user, inactive_post):
        api_client.force_authenticate(user=user)
        
        comment_data = {
            'post': inactive_post.id,
            'content': 'This comment should fail'
        }
        
        print(f"\n[TEST] Testing comment creation on inactive post by user: {user.username}")
        print(f"[TEST] Target post: '{inactive_post.title}' (active: {inactive_post.active})")
        print(f"[TEST] Comment data: {comment_data}")
        
        response = api_client.post('/api/comments/', comment_data, format='json')
        
        print(f"[TEST] Comment on inactive post API Response Status: {response.status_code}")
        print(f"[TEST] Expected: 400 Bad Request")
        print(f"[TEST] Error response: {response.data}")
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST, "Comment creation on inactive post should fail"
        assert 'Comments can only be created on active posts' in str(response.data), "Should provide helpful error message"
        
        comment_exists = Comment.objects.filter(content=comment_data['content']).exists()
        print(f"[TEST] Comment created in database: {comment_exists}")
        assert not comment_exists, "Comment should not be created on inactive post"
        
        print(f"[TEST] ✓ Users correctly blocked from commenting on inactive posts")