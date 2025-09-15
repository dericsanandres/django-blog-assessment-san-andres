#!/usr/bin/env python3
"""
Demo Data Creation Script for Django Blog Assessment
Creates sample users, posts, and comments for demonstration
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from django.contrib.auth.models import User
from blog.models import Author, Post, Comment
from django.utils import timezone


def create_demo_data():
    print("[DEMO] Creating demo data...")
    
    # Create test users
    admin_user = User.objects.get_or_create(
        username='admin', 
        defaults={
            'email': 'admin@example.com', 
            'is_staff': True, 
            'is_superuser': True
        }
    )[0]
    admin_user.set_password('admin123')
    admin_user.save()
    
    test_user, created = User.objects.get_or_create(
        username='testuser', 
        defaults={
            'email': 'test@example.com', 
            'is_staff': True
        }
    )
    test_user.set_password('testpass123')
    test_user.save()
    
    # Create authors
    admin_author = Author.objects.get_or_create(
        user=admin_user, 
        defaults={
            'name': 'Admin User', 
            'email': 'admin@example.com'
        }
    )[0]
    
    test_author = Author.objects.get_or_create(
        user=test_user, 
        defaults={
            'name': 'Test User', 
            'email': 'test@example.com'
        }
    )[0]
    
    # Create sample posts
    post1 = Post.objects.get_or_create(
        title='Welcome to Django Blog', 
        defaults={
            'content': 'This is a comprehensive Django blog application with REST API functionality. The application demonstrates proper authentication, permissions, and CRUD operations for blog posts and comments.',
            'author': admin_author,
            'status': 'published',
            'active': True
        }
    )[0]
    
    post2 = Post.objects.get_or_create(
        title='API Testing and Documentation', 
        defaults={
            'content': 'This post demonstrates the REST API functionality including filtering by date ranges, author names, and proper pagination. The API supports both authenticated and anonymous access where appropriate.',
            'author': test_author,
            'status': 'published',
            'active': True
        }
    )[0]
    
    post3 = Post.objects.get_or_create(
        title='Draft Post (Inactive)', 
        defaults={
            'content': 'This is an inactive post that should not appear in the public listings but can be seen in admin panel.',
            'author': admin_author,
            'status': 'draft',
            'active': False
        }
    )[0]
    
    # Create sample comments
    Comment.objects.get_or_create(
        post=post1, 
        user=test_user, 
        defaults={
            'content': 'Great blog post! The authentication system works perfectly.',
            'is_approved': True
        }
    )
    
    Comment.objects.get_or_create(
        post=post2, 
        user=admin_user, 
        defaults={
            'content': 'Nice work on the API documentation and filtering features!',
            'is_approved': True
        }
    )
    
    Comment.objects.get_or_create(
        post=post1, 
        defaults={
            'content': 'Anonymous comment: This blog looks very professional!',
            'is_approved': False
        }
    )
    
    Comment.objects.get_or_create(
        post=post2, 
        user=test_user, 
        defaults={
            'content': 'The date filtering functionality is exactly what we needed.',
            'is_approved': True
        }
    )
    
    print('[DEMO] Demo data created successfully:')
    print('[DEMO]   - 2 users: admin/admin123, testuser/testpass123')
    print('[DEMO]   - 2 authors with linked users')
    print('[DEMO]   - 3 posts (2 active, 1 inactive for testing)')
    print('[DEMO]   - 4 comments (3 approved, 1 pending)')


if __name__ == '__main__':
    create_demo_data()