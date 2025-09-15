# Django Blog Assessment

Here's my Django blog implementation for the assessment.

Built a complete blog system with Author/Post/Comment models, REST API endpoints, and comprehensive test coverage. Used Django 5.2.6 with DRF for solid, maintainable code.

## Bonus Features

Included a complete web interface alongside the required API, makes testing and demonstration much easier:
- Post browsing with pagination
- Full CRUD operations through web forms

You can interact through either the web interface (http://127.0.0.1:8000/) or the REST API (/api/posts/).

<img width="784" height="823" alt="Screenshot 2025-09-15 at 5 08 42 PM" src="https://github.com/user-attachments/assets/e03eaebf-9afe-43c2-9748-f879c0a7d942" />
<img width="775" height="449" alt="Screenshot 2025-09-15 at 5 08 46 PM" src="https://github.com/user-attachments/assets/0d6f31b3-3058-4458-9439-2503d6bbbac5" />


## The Brief

[Assessment doc](https://docs.google.com/document/d/1ue5NmW5OHawQ6jxTQEreIeUcDuHGbAdTQxOPPZgmbNY/edit?tab=t.0)

Standard blog setup:
- Models with proper relationships
- Class-based views
- REST API with auth & permissions
- Unit tests
- Bonus: Docker + Web UI

## Test Users

Created two users for immediate testing:
- `admin` / `admin123` (superuser)
- `testuser` / `testpass123` (regular user)

**Note**: Authentication uses Django's admin panel at `/admin/` - login there first, then navigate to the main blog interface.

<img width="477" height="352" alt="Screenshot 2025-09-15 at 1 19 52 PM" src="https://github.com/user-attachments/assets/f50cb665-a546-4357-baa2-ad9f61b3f575" />


## Running Locally

Created a Makefile for streamlined setup:

```bash
# Quick setup
make start

# Manual setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

**Important**: Keep the server running in one terminal and use a separate terminal for executing tests or API calls.



## Docker Deployment

Deployed on AWS EC2 for demonstration: **http://44.201.81.169:8000**

To deploy locally:

```bash
git clone https://github.com/dericsanandres/django-blog-assessment-san-andres.git
cd django-blog-assessment-san-andres

# Local development
docker-compose up -d --build
docker-compose exec web python manage.py migrate
docker-compose exec web python create_demo_data.py

# Production deployment
docker-compose up -d --build
docker-compose exec web python manage.py migrate
```

For production deployment, remember to update `ALLOWED_HOSTS` in settings.py and configure appropriate firewall rules.



## Screenshots During Docker Deployment
<img width="1655" height="678" alt="Screenshot 2025-09-15 at 12 37 53 PM" src="https://github.com/user-attachments/assets/aba134c4-fa3c-4047-942b-09cc1de1d030" />
<img width="954" height="295" alt="Screenshot 2025-09-15 at 12 02 00 PM" src="https://github.com/user-attachments/assets/24bcbed3-be06-4bae-882a-b278940f4a2d" />
<img width="945" height="427" alt="Screenshot 2025-09-15 at 12 00 46 PM" src="https://github.com/user-attachments/assets/daf66f2a-91b9-43a6-a2ba-024160eb52ca" />
<img width="955" height="278" alt="Screenshot 2025-09-15 at 12 00 27 PM" src="https://github.com/user-attachments/assets/6ee96268-b356-4467-a4b4-3a3209e963d1" />
<img width="1072" height="1080" alt="Screenshot 2025-09-15 at 11 59 27 AM" src="https://github.com/user-attachments/assets/0ff96299-05ad-4076-9e48-9fca851e8f29" />
<img width="1425" height="1081" alt="Screenshot 2025-09-15 at 12 39 05 PM" src="https://github.com/user-attachments/assets/fed9f86e-7a65-4373-8248-653428839535" />

## Testing

Test coverage follows the specification exactly. All Stage 3 requirements are covered in `blog/tests/test_blog.py`:

### What's Covered

**Requirement 2.1 - Post List Functionality:**
- Test that post list only shows `Post.active=True`
  - Function: `test_api_post_list_shows_only_active_posts()`
  - Run: `python -m pytest blog/tests/test_blog.py::TestPostListView::test_api_post_list_shows_only_active_posts -v`
- Test post list filtering by `published_date` (date range filtering)
  - Function: `test_api_post_list_date_range_filtering()`
  - Run: `python -m pytest blog/tests/test_blog.py::TestPostListFiltering::test_api_post_list_date_range_filtering -v`

**Requirement 3.3 - Comment Creation:**
- Test creating comments as logged-in users
  - Function: `test_authenticated_user_can_create_comment()`
  - Run: `python -m pytest blog/tests/test_blog.py::TestCommentCreationAPI::test_authenticated_user_can_create_comment -v`
- Test creating comments as non-logged-in users (now properly blocks unauthorized access)
  - Function: `test_anonymous_user_cannot_create_comment()`
  - Run: `python -m pytest blog/tests/test_blog.py::TestCommentCreationAPI::test_anonymous_user_cannot_create_comment -v`

**Requirement 3.4 - Post Creation:**
- Test creating posts as authenticated authors via API
  - Function: `test_authenticated_user_can_create_post()`
  - Run: `python -m pytest blog/tests/test_blog.py::TestPostCreationAPI::test_authenticated_user_can_create_post -v`

**Requirement 3.5 - Post Editing:**
- Test editing posts as authors via API (owner permissions)
  - Function: `test_author_can_edit_own_post()`
  - Run: `python -m pytest blog/tests/test_blog.py::TestPostEditingAPI::test_author_can_edit_own_post -v`

**Requirement 3.6 - Post Deletion:**
- Test deleting posts as authors via API (owner permissions)
  - Function: `test_author_can_delete_own_post()`
  - Run: `python -m pytest blog/tests/test_blog.py::TestPostDeletionAPI::test_author_can_delete_own_post -v`

All tests include comprehensive assertions with clear error messages for easy debugging.

### Running Tests

```bash
# Run all tests
make test

# Docker environment
docker-compose exec web python -m pytest blog/tests/test_blog.py -v

# Verbose output
make test-v
```

**Individual Test Categories:**
```bash
# Test post listing and filtering (Requirements 2.1)
python -m pytest blog/tests/test_blog.py::TestPostListView -v
python -m pytest blog/tests/test_blog.py::TestPostListFiltering -v

# Test comment creation (Requirement 3.3)
python -m pytest blog/tests/test_blog.py::TestCommentCreationAPI -v

# Test post CRUD operations (Requirements 3.4, 3.5, 3.6)
python -m pytest blog/tests/test_blog.py::TestPostCreationAPI -v
python -m pytest blog/tests/test_blog.py::TestPostEditingAPI -v
python -m pytest blog/tests/test_blog.py::TestPostDeletionAPI -v
```

**Specific Documentation Requirements:**
```bash
# Requirement 2.1 tests
python -m pytest blog/tests/test_blog.py::TestPostListView::test_api_post_list_shows_only_active_posts -v
python -m pytest blog/tests/test_blog.py::TestPostListFiltering::test_api_post_list_date_range_filtering -v

# Requirement 3.3 tests
python -m pytest blog/tests/test_blog.py::TestCommentCreationAPI::test_authenticated_user_can_create_comment -v
python -m pytest blog/tests/test_blog.py::TestCommentCreationAPI::test_anonymous_user_cannot_create_comment -v

# Requirement 3.4 test
python -m pytest blog/tests/test_blog.py::TestPostCreationAPI::test_authenticated_user_can_create_post -v

# Requirement 3.5 test
python -m pytest blog/tests/test_blog.py::TestPostEditingAPI::test_author_can_edit_own_post -v

# Requirement 3.6 test
python -m pytest blog/tests/test_blog.py::TestPostDeletionAPI::test_author_can_delete_own_post -v
```

## API Endpoints

Local: `http://127.0.0.1:8000` | Live demo: `http://44.201.81.169:8000`

### Try These Links
- [All Posts](http://44.201.81.169:8000/api/posts/)
- [Single Post](http://44.201.81.169:8000/api/posts/1/)
- [Comments API](http://44.201.81.169:8000/api/comments/)
- [Web Interface](http://44.201.81.169:8000/)
- [Admin Panel](http://44.201.81.169:8000/admin/)

### All Endpoints
- `GET /api/posts/` - List active posts (filter by author, date range)
- `POST /api/posts/` - Create post (auth required)
- `GET /api/posts/{id}/` - Post details with comments
- `PATCH /api/posts/{id}/edit/` - Edit post (owner only)
- `DELETE /api/posts/{id}/delete/` - Delete post (owner only)
- `POST /api/comments/` - Create comment (auth required)

### API Testing Commands

For easy testing, I've added professional-grade Makefile commands that demonstrate all API functionality:

**Individual API Operations:**
```bash
# List posts with filtering examples
make api-list

# Create a new post via API
make api-create

# Edit an existing post via API
make api-edit

# Delete a post via API (with confirmation)
make api-delete

# Create a comment via API
make api-comment

# Run all API tests in sequence
make api-test
```

Each command shows:
- Exact curl command being executed
- Professional formatted output
- HTTP status codes
- JSON response formatting
- Authentication details
- Error handling

**Prerequisites:** Server must be running (`make run`)

## Technical Implementation

**Models**: Author, Post, and Comment models with proper relationships and database indexes on frequently queried fields.

**Authentication**: Owner-based permissions for post editing and deletion. Comment creation requires authentication.

**Validation**: Posts must be active for commenting. Date range filtering implemented on published_date field.

**Testing**: Comprehensive test suite with 10 test cases covering all specified requirements.
