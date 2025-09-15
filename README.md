# Django Blog Assessment

Good Day BlueDrive Team, this is my submission for the Assessment problem.

This implements a blog system with Author/Post/Comment models, REST API endpoints, and comprehensive test coverage. Built with Django 5.2.6 and DRF 3.16.1.

## Problem

You can refer to this problem statement: https://docs.google.com/document/d/1ue5NmW5OHawQ6jxTQEreIeUcDuHGbAdTQxOPPZgmbNY/edit?tab=t.0

Create a blogging system with:
- **Models**: Author, Post, Comment with proper relationships and indexing
- **Views**: Django CBVs (ListView, DetailView, CreateView) with URL patterns
- **REST API**: Full CRUD operations with filtering, authentication, and permissions
- **Testing**: Unit tests covering all API endpoints and business logic
- **Bonus**: Docker deployment with testing instructions

Also we have two users who are instantly created when we run the makefile locally:
- **admin** / **admin123** (superuser)
- **testuser** / **testpass123** (staff user)

In the docker deployment we already have these users, feel free to test the creation of posts using the endpoints.

## Running Locally

So in here to make things easier I added a makefile to quickly install the packages and run the program.

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

## Docker Deployment

For the docker deployment currently, I deployed it on my own free tier AWS EC2 server. You can access it via: **http://44.201.81.169:8000**

For the docker deployment, clone the repo:
```bash
git clone https://github.com/dericsanandres/django-blog-assessment-san-andres.git
```

Then install docker. Here are the commands that I ran in the server:

Don't forget to modify the security groups in AWS (you can use any hosting platform, mine I just used AWS).

```bash
# Local
docker-compose up -d --build
docker-compose exec web python manage.py migrate
docker-compose exec web python create_demo_data.py

# Production (add your server IP to ALLOWED_HOSTS first)
git clone https://github.com/dericsanandres/django-blog-assessment-san-andres.git
cd django-blog-assessment-san-andres
docker-compose up -d --build
docker-compose exec web python manage.py migrate
```
Screenshots During Deployment:
<img width="954" height="295" alt="Screenshot 2025-09-15 at 12 02 00 PM" src="https://github.com/user-attachments/assets/24bcbed3-be06-4bae-882a-b278940f4a2d" />
<img width="945" height="427" alt="Screenshot 2025-09-15 at 12 00 46 PM" src="https://github.com/user-attachments/assets/daf66f2a-91b9-43a6-a2ba-024160eb52ca" />
<img width="955" height="278" alt="Screenshot 2025-09-15 at 12 00 27 PM" src="https://github.com/user-attachments/assets/6ee96268-b356-4467-a4b4-3a3209e963d1" />
<img width="1072" height="1080" alt="Screenshot 2025-09-15 at 11 59 27 AM" src="https://github.com/user-attachments/assets/0ff96299-05ad-4076-9e48-9fca851e8f29" />
<img width="1065" height="547" alt="Screenshot 2025-09-15 at 5 20 38 AM" src="https://github.com/user-attachments/assets/e4054915-9a0a-4658-9d08-8d9b98c43bf9" />

Also don't forget to update the ALLOWED_HOSTS[] in project/settings.py so that when we deploy it your IP address will be recognized.

## Testing

```bash
# Local
make test

# Docker
docker-compose exec web python -m pytest blog/tests/test_blog.py -v
```

## API Endpoints

For local: `http://127.0.0.1:8000`
For Docker deployment: example my server is `http://44.201.81.169:8000`

### Quick Access (Live Server)
- http://44.201.81.169:8000/api/posts/ - [List Posts](http://44.201.81.169:8000/api/posts/)
- http://44.201.81.169:8000/api/posts/1/ - [Post Detail (ID: 1)](http://44.201.81.169:8000/api/posts/1/)
- http://44.201.81.169:8000/api/comments/ - [Create Comment](http://44.201.81.169:8000/api/comments/)
- http://44.201.81.169:8000/ - [Blog Homepage](http://44.201.81.169:8000/)
- http://44.201.81.169:8000/admin/ - [Admin Panel](http://44.201.81.169:8000/admin/)

### All Endpoints
- `GET /api/posts/` - List active posts (filter by author, date range)
- `POST /api/posts/` - Create post (auth required)
- `GET /api/posts/{id}/` - Post details with comments
- `PATCH /api/posts/{id}/edit/` - Edit post (owner only)
- `DELETE /api/posts/{id}/delete/` - Delete post (owner only)
- `POST /api/comments/` - Create comment (auth optional)

## Implementation Notes

**Models** (`blog/models.py`):
- Author: name, email, user FK
- Post: title, content, published_date, author FK, status, active
- Comment: post FK, content, user FK, created
- Database indexes on foreign keys and common query fields

**Authentication**: Owner-based permissions for post editing/deletion. Anonymous commenting allowed.

**Validation**: Posts must be active for commenting. Date range filtering on published_date.

**Testing**: 10 test cases covering filtering, CRUD operations, permissions, and edge cases.
