import pytest
import json
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
        
        print(f"\n{'='*60}")
        print(f"[TEST] Web View - Active Posts Only")
        print(f"{'='*60}")
        print(f"**GET** `/posts/` (Django ListView)")
        print(f"Testing that only active posts appear in web template")
        
        client = Client()
        response = client.get(reverse('blog:post_list'))
        
        print(f"\nResponse Status: {response.status_code}")
        print(f"[SHOULD APPEAR] Active post '{active_post.title}' - active: {active_post.active}")
        print(f"[SHOULD NOT APPEAR] Inactive post '{inactive_post.title}' - active: {inactive_post.active}")
        
        assert response.status_code == 200, "Post list page should load successfully"
        
        content = response.content.decode()
        active_in_content = active_post.title in content
        inactive_in_content = inactive_post.title in content
        
        print(f"\nContent Analysis:")
        print(f"[FOUND] Active post found in HTML: {active_in_content}")
        print(f"[NOT FOUND] Inactive post found in HTML: {inactive_in_content}")
        
        assert active_in_content, "Active post should appear in the list"
        assert not inactive_in_content, "Inactive post should not appear in the list"
        
        print(f"\n[SUCCESS] Web view correctly shows only active posts")
    
    def test_api_post_list_shows_only_active_posts(self, api_client, active_post, inactive_post):
        print(f"\n{'='*60}")
        print(f"[TEST 1] API - Active Posts Only")
        print(f"{'='*60}")
        print(f"**GET** `/api/posts/`")
        
        response = api_client.get('/api/posts/')
        
        print(f"\nResponse Status: {response.status_code}")
        print(f"[SHOULD APPEAR] Active post '{active_post.title}' - active: {active_post.active}")
        print(f"[SHOULD NOT APPEAR] Inactive post '{inactive_post.title}' - active: {inactive_post.active}")
        
        assert response.status_code == 200, "API should return success status"
        
        print(f"\nAPI Response JSON:")
        print("```json")
        print(json.dumps(response.data, indent=2))
        print("```")
        
        titles = [post['title'] for post in response.data['results']]
        
        assert active_post.title in titles, "Active post should be in API response"
        assert inactive_post.title not in titles, "Inactive post should not be in API response"
        
        print(f"\n[EXCLUDED] Inactive post '{inactive_post.title}' NOT in results")
        print(f"\n[SUCCESS] API correctly filters to active posts only")


@pytest.mark.django_db  
class TestPostListFiltering:
    
    def test_api_post_list_date_range_filtering(self, api_client, active_post, old_post):
        recent_date = (timezone.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        
        print(f"\n{'='*60}")
        print(f"[TEST 2] API - Date Range Filter")
        print(f"{'='*60}")
        print(f"**GET** `/api/posts/?published_date__gte={recent_date}`")
        
        print(f"\nTest Data:")
        print(f"[RECENT] Recent post '{active_post.title}' published: {active_post.published_date.strftime('%Y-%m-%d')}")
        print(f"[OLD] Old post '{old_post.title}' published: {old_post.published_date.strftime('%Y-%m-%d')}")
        print(f"[FILTER] Posts >= {recent_date}")
        
        response = api_client.get(f'/api/posts/?published_date__gte={recent_date}')
        
        print(f"\nResponse Status: {response.status_code}")
        
        assert response.status_code == 200, "Filtered API request should succeed"
        
        print(f"\nAPI Response JSON:")
        print("```json")
        print(json.dumps(response.data, indent=2))
        print("```")
        
        titles = [post['title'] for post in response.data['results']]
        
        assert active_post.title in titles, "Recent post should appear in date-filtered results"
        assert old_post.title not in titles, "Old post should not appear in recent date filter"
        
        print(f"\n[INCLUDED] Recent post included")
        print(f"[EXCLUDED] Old post excluded")
        print(f"\n[SUCCESS] Date range filtering works correctly")
        
    def test_api_post_list_author_filtering(self, api_client, active_post):
        print(f"\n{'='*60}")
        print(f"[TEST 3] API - Author Filter")
        print(f"{'='*60}")
        print(f"**GET** `/api/posts/?author__name={active_post.author.name}`")
        
        print(f"\nTest Data:")
        print(f"[AUTHOR] Filtering by author: '{active_post.author.name}'")
        
        response = api_client.get(f'/api/posts/?author__name={active_post.author.name}')
        
        print(f"\nResponse Status: {response.status_code}")
        
        assert response.status_code == 200, "Author filtering should work"
        assert len(response.data['results']) >= 1, "Should return posts by the specified author"
        
        print(f"\nAPI Response JSON:")
        print("```json")
        print(json.dumps(response.data, indent=2))
        print("```")
        
        if response.data['results']:
            assert response.data['results'][0]['author_name'] == active_post.author.name, "Returned post should match author filter"
        
        print(f"\n[SUCCESS] Author filtering works correctly")


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
        
        print(f"\n{'='*60}")
        print(f"[TEST 4] API - Create Post (Authenticated)")
        print(f"{'='*60}")
        print(f"**POST** `/api/posts/`")
        print(f"[AUTH] Authenticated as: {user.username}")
        
        print(f"\nRequest JSON:")
        print("```json")
        print(json.dumps(post_data, indent=2))
        print("```")
        
        response = api_client.post('/api/posts/', post_data, format='json')
        
        print(f"\nResponse Status: {response.status_code} {'[PASS]' if response.status_code == 201 else '[FAIL]'}")
        
        if response.status_code == status.HTTP_201_CREATED:
            print(f"\nResponse JSON (201 Created):")
            print("```json")
            print(json.dumps(response.data, indent=2))
            print("```")
        else:
            print(f"\nError Response:")
            print("```json")
            print(json.dumps(response.data, indent=2))
            print("```")
        
        assert response.status_code == status.HTTP_201_CREATED, f"Post creation should succeed, got {response.status_code}: {response.data}"
        
        created_post = Post.objects.get(title='New Test Post')
        print(f"\n[DATABASE] Database Verification:")
        print(f"[VERIFY] Post content matches: {created_post.content == post_data['content']}")
        print(f"[VERIFY] Author name: '{created_post.author.name}'")
        print(f"[VERIFY] Author linked to user: {created_post.author.user == user}")
        
        assert created_post.content == post_data['content'], "Post content should match submitted data"
        assert created_post.author.name == 'API Test Author', "Author should be created or linked correctly"
        assert created_post.author.user == user, "Author should be linked to the authenticated user"
        
        print(f"\n[SUCCESS] Authenticated user can create posts successfully")
    
    def test_unauthenticated_user_cannot_create_post(self, api_client):
        post_data = {
            'title': 'Unauthorized Post',
            'content': 'This should not be created',
            'author_name': 'Unauthorized User'
        }
        
        print(f"\n{'='*60}")
        print(f"[TEST 5] API - Create Post (Unauthenticated)")
        print(f"{'='*60}")
        print(f"**POST** `/api/posts/` (No Authentication)")
        print(f"[SECURITY] Testing security: Unauthenticated access")
        
        print(f"\nRequest JSON:")
        print("```json")
        print(json.dumps(post_data, indent=2))
        print("```")
        
        response = api_client.post('/api/posts/', post_data, format='json')
        
        print(f"\nResponse Status: {response.status_code} {'[PASS]' if response.status_code == 403 else '[FAIL]'}")
        print(f"Expected: 403 Forbidden")
        
        print(f"\nResponse JSON (403 Forbidden):")
        print("```json")
        print(json.dumps(response.data, indent=2))
        print("```")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN, "Unauthenticated users should not be able to create posts"
        
        post_exists = Post.objects.filter(title='Unauthorized Post').exists()
        print(f"\n[DATABASE] Database Verification:")
        print(f"[VERIFY] Post NOT created in database: {not post_exists}")
        assert not post_exists, "Post should not be created without authentication"
        
        print(f"\n[SUCCESS] Unauthenticated users correctly blocked from creating posts")


@pytest.mark.django_db
class TestPostEditingAPI:
    
    def test_author_can_edit_own_post(self, api_client, user, active_post):
        api_client.force_authenticate(user=user)
        
        update_data = {
            'title': 'Updated Post Title',
            'content': 'Updated post content',
            'active': False
        }
        
        print(f"\n{'='*60}")
        print(f"[TEST 6] API - Edit Post (Owner)")
        print(f"{'='*60}")
        print(f"**PATCH** `/api/posts/{active_post.id}/edit/`")
        print(f"[AUTH] Authenticated as: {user.username} (post owner)")
        
        print(f"\nOriginal Post:")
        print(f"[ORIGINAL] Title: '{active_post.title}'")
        print(f"[ORIGINAL] Active: {active_post.active}")
        
        print(f"\nRequest JSON:")
        print("```json")
        print(json.dumps(update_data, indent=2))
        print("```")
        
        response = api_client.patch(f'/api/posts/{active_post.id}/edit/', update_data, format='json')
        
        print(f"\nResponse Status: {response.status_code} {'[PASS]' if response.status_code == 200 else '[FAIL]'}")
        
        if response.status_code == status.HTTP_200_OK:
            print(f"\nResponse JSON (200 OK):")
            print("```json")
            print(json.dumps(response.data, indent=2))
            print("```")
        else:
            print(f"\nError Response:")
            print("```json")
            print(json.dumps(response.data, indent=2))
            print("```")
        
        assert response.status_code == status.HTTP_200_OK, f"Post update should succeed, got {response.status_code}: {response.data}"
        
        updated_post = Post.objects.get(id=active_post.id)
        print(f"\n[DATABASE] Database Verification:")
        print(f"[VERIFY] Title: '{active_post.title}' → '{updated_post.title}'")
        print(f"[VERIFY] Content updated: {len(updated_post.content)} chars")
        print(f"[VERIFY] Active: {active_post.active} → {updated_post.active}")
        
        assert updated_post.title == 'Updated Post Title', "Post title should be updated"
        assert updated_post.content == 'Updated post content', "Post content should be updated"  
        assert updated_post.active == False, "Post active status should be updated"
        
        print(f"\n[SUCCESS] Post owner can edit their own posts successfully")
    
    def test_non_author_cannot_edit_post(self, api_client, active_post):
        other_user = User.objects.create_user(username='other', email='other@test.com', password='pass')
        api_client.force_authenticate(user=other_user)
        
        print(f"\n{'='*60}")
        print(f"[TEST 7: API - Edit Post (Non-Owner)")
        print(f"{'='*60}")
        print(f"**PATCH** `/api/posts/{active_post.id}/edit/`")
        print(f"[SECURITY] Testing security: Non-owner access")
        print(f"[AUTH] Authenticated as: {other_user.username}")
        print(f"[TARGET] Target post owned by: {active_post.author.user.username}")
        
        update_data = {'title': 'Hacked Title'}
        print(f"\nRequest JSON:")
        print("```json")
        print(json.dumps(update_data, indent=2))
        print("```")
        
        response = api_client.patch(f'/api/posts/{active_post.id}/edit/', update_data, format='json')
        
        print(f"\nResponse Status: {response.status_code} {'[PASS]' if response.status_code == 403 else '[FAIL]'}")
        print(f"Expected: 403 Forbidden")
        
        print(f"\nResponse JSON (403 Forbidden):")
        print("```json")
        print(json.dumps(response.data, indent=2))
        print("```")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN, "Non-authors should not be able to edit posts"
        
        unchanged_post = Post.objects.get(id=active_post.id)
        print(f"\n[DATABASE] Database Verification:")
        print(f"[VERIFY] Post title unchanged: '{unchanged_post.title}' (original: '{active_post.title}')")
        assert unchanged_post.title == active_post.title, "Post title should remain unchanged"
        
        print(f"\n[SUCCESS] Non-owners correctly blocked from editing posts")


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
        
        print(f"\n{'='*60}")
        print(f"[TEST 8: API - Create Comment (Authenticated)")
        print(f"{'='*60}")
        print(f"**POST** `/api/comments/`")
        print(f"[AUTH] Authenticated as: {user.username}")
        print(f"[TARGET] Target post: '{active_post.title}' (ID: {active_post.id})")
        
        print(f"\nRequest JSON:")
        print("```json")
        print(json.dumps(comment_data, indent=2))
        print("```")
        
        response = api_client.post('/api/comments/', comment_data, format='json')
        
        print(f"\nResponse Status: {response.status_code} {'[PASS]' if response.status_code == 201 else '[FAIL]'}")
        
        if response.status_code == status.HTTP_201_CREATED:
            print(f"\nResponse JSON (201 Created):")
            print("```json")
            print(json.dumps(response.data, indent=2))
            print("```")
        else:
            print(f"\nError Response:")
            print("```json")
            print(json.dumps(response.data, indent=2))
            print("```")
        
        assert response.status_code == status.HTTP_201_CREATED, f"Comment creation should succeed, got {response.status_code}: {response.data}"
        
        created_comment = Comment.objects.get(content=comment_data['content'])
        print(f"\n[DATABASE] Database Verification:")
        print(f"[VERIFY] Comment linked to correct post: {created_comment.post == active_post}")
        print(f"[VERIFY] Comment linked to user: {created_comment.user == user}")
        print(f"[VERIFY] Comment approval status: {created_comment.is_approved} (should be False)")
        
        assert created_comment.post == active_post, "Comment should be linked to the correct post"
        assert created_comment.user == user, "Comment should be linked to the authenticated user"
        assert created_comment.is_approved == False, "New comments should default to unapproved"
        
        print(f"\n[SUCCESS] Authenticated user can create comments successfully")
    
    def test_anonymous_user_can_create_comment(self, api_client, active_post):
        
        comment_data = {
            'post': active_post.id,
            'content': 'This is an anonymous comment'
        }
        
        print(f"\n{'='*60}")
        print(f"[TEST 9: API - Create Comment (Anonymous)")
        print(f"{'='*60}")
        print(f"**POST** `/api/comments/` (No Authentication)")
        print(f"[ANONYMOUS] Anonymous user")
        print(f"[TARGET] Target post: '{active_post.title}' (ID: {active_post.id})")
        
        print(f"\nRequest JSON:")
        print("```json")
        print(json.dumps(comment_data, indent=2))
        print("```")
        
        response = api_client.post('/api/comments/', comment_data, format='json')
        
        print(f"\nResponse Status: {response.status_code} {'[PASS]' if response.status_code == 201 else '[FAIL]'}")
        
        if response.status_code == status.HTTP_201_CREATED:
            print(f"\nResponse JSON (201 Created):")
            print("```json")
            print(json.dumps(response.data, indent=2))
            print("```")
        else:
            print(f"\nError Response:")
            print("```json")
            print(json.dumps(response.data, indent=2))
            print("```")
        
        assert response.status_code == status.HTTP_201_CREATED, f"Anonymous comment creation should succeed, got {response.status_code}: {response.data}"
        
        created_comment = Comment.objects.get(content=comment_data['content'])
        print(f"\n[DATABASE] Database Verification:")
        print(f"[VERIFY] Comment linked to correct post: {created_comment.post == active_post}")
        print(f"[VERIFY] Comment user field: {created_comment.user} (should be None)")
        print(f"[VERIFY] Comment approval status: {created_comment.is_approved} (should be False)")
        
        assert created_comment.post == active_post, "Anonymous comment should be linked to the correct post"
        assert created_comment.user is None, "Anonymous comment should have no user linked"
        assert created_comment.is_approved == False, "Anonymous comments should default to unapproved"
        
        print(f"\n[SUCCESS] Anonymous users can create comments successfully")
    
    def test_cannot_comment_on_inactive_post(self, api_client, user, inactive_post):
        api_client.force_authenticate(user=user)
        
        comment_data = {
            'post': inactive_post.id,
            'content': 'This comment should fail'
        }
        
        print(f"\n{'='*60}")
        print(f"[TEST 10: API - Validation Error (Inactive Post)")
        print(f"{'='*60}")
        print(f"**POST** `/api/comments/`")
        print(f"[SECURITY] Testing validation: Comment on inactive post")
        print(f"[AUTH] Authenticated as: {user.username}")
        print(f"[TARGET] Target post: '{inactive_post.title}' (active: {inactive_post.active})")
        
        print(f"\nRequest JSON:")
        print("```json")
        print(json.dumps(comment_data, indent=2))
        print("```")
        
        response = api_client.post('/api/comments/', comment_data, format='json')
        
        print(f"\nResponse Status: {response.status_code} {'[PASS]' if response.status_code == 400 else '[FAIL]'}")
        print(f"Expected: 400 Bad Request")
        
        print(f"\nResponse JSON (400 Bad Request):")
        print("```json")
        print(json.dumps(response.data, indent=2))
        print("```")
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST, "Comment creation on inactive post should fail"
        assert 'Comments can only be created on active posts' in str(response.data), "Should provide helpful error message"
        
        comment_exists = Comment.objects.filter(content=comment_data['content']).exists()
        print(f"\n[DATABASE] Database Verification:")
        print(f"[VERIFY] Comment NOT created in database: {not comment_exists}")
        assert not comment_exists, "Comment should not be created on inactive post"
        
        print(f"\n[SUCCESS] Users correctly blocked from commenting on inactive posts")