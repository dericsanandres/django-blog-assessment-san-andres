# Django Blog Assessment - Makefile
# Author: Deric San Andres

.PHONY: help setup install migrate test run clean admin demo all api-list api-create api-edit api-delete api-comment api-test

# default target shows help
help:
	@echo "Django Blog Assessment - Available Commands:"
	@echo ""
	@echo "Quick Start (Recommended):"
	@echo "  make start      - complete setup + create users + run tests + start server"
	@echo "  make full       - complete setup + demo data (no server start)"
	@echo ""
	@echo "Setup Commands:"
	@echo "  make setup      - create virtual environment and install dependencies"
	@echo "  make migrate    - run database migrations"
	@echo "  make admin      - create admin and test users"
	@echo ""
	@echo "Testing Commands:"
	@echo "  make test       - run all unit tests"
	@echo "  make test-v     - run tests with verbose output"
	@echo ""
	@echo "Development Commands:"
	@echo "  make run        - start Django development server only"
	@echo "  make demo       - create sample data for testing"
	@echo ""
	@echo "API Testing Commands (server must be running):"
	@echo "  make api-list   - list all posts with filters demo"
	@echo "  make api-create - create a new post via API"
	@echo "  make api-edit   - edit an existing post via API"
	@echo "  make api-delete - delete a post via API"
	@echo "  make api-comment - create a comment via API"
	@echo "  make api-test   - run all API commands in sequence"
	@echo ""
	@echo "Utility Commands:"
	@echo "  make clean      - clean up cache and temp files"
	@echo "  make shell      - open Django shell"

# complete setup from scratch
setup:
	@echo "[SETUP] Setting up Django blog assessment..."
	python3 -m venv venv
	@echo "[SETUP] Virtual environment created"
	. venv/bin/activate && pip install --upgrade pip
	. venv/bin/activate && pip install -r requirements.txt
	@echo "[SETUP] Dependencies installed successfully"

# install requirements only
install:
	@echo "[INSTALL] Installing requirements..."
	. venv/bin/activate && pip install -r requirements.txt
	@echo "[INSTALL] Requirements installed successfully"

# run database migrations
migrate:
	@echo "[MIGRATE] Running database migrations..."
	@. venv/bin/activate && python manage.py migrate --verbosity=0
	@echo "[MIGRATE] Database migrations completed successfully"

# run all unit tests
test:
	@echo "[TEST] Running unit tests with detailed output..."
	@. venv/bin/activate && export DJANGO_SETTINGS_MODULE=project.settings && python -m pytest blog/tests/test_blog.py -v -s --tb=short
	@echo "[TEST] All tests completed successfully"

# run tests with extra verbose output
test-v:
	@echo "[TEST] Running unit tests with verbose output..."
	. venv/bin/activate && export DJANGO_SETTINGS_MODULE=project.settings && python -m pytest blog/tests/test_blog.py -v -s
	@echo "[TEST] Verbose tests completed successfully"

# start development server
run:
	@echo "[SERVER] Starting Django development server..."
	@echo "[SERVER] Server will be available at: http://127.0.0.1:8000"
	@echo "[SERVER] API endpoints at: http://127.0.0.1:8000/api/posts/"
	@echo "[SERVER] Admin panel at: http://127.0.0.1:8000/admin/"
	@echo "[SERVER] Press Ctrl+C to stop the server"
	. venv/bin/activate && python manage.py runserver

# create admin and test users
admin:
	@echo "[ADMIN] Creating admin user..."
	@. venv/bin/activate && python manage.py shell -c "from django.contrib.auth.models import User; User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@example.com', 'admin123'); print('[ADMIN] Admin user ready: admin/admin123')" 2>/dev/null
	@echo "[ADMIN] Creating test user..."
	@. venv/bin/activate && python manage.py shell -c "from django.contrib.auth.models import User; from blog.models import Author; user, created = User.objects.get_or_create(username='testuser', defaults={'email': 'test@example.com'}); user.set_password('testpass123'); user.is_staff = True; user.save(); author, created = Author.objects.get_or_create(user=user, defaults={'name': 'Test User', 'email': 'test@example.com'}); print('[ADMIN] Test user ready: testuser/testpass123')" 2>/dev/null

# create demo data
demo:
	@. venv/bin/activate && python create_demo_data.py

# open Django shell
shell:
	@echo "[SHELL] Opening Django shell..."
	. venv/bin/activate && python manage.py shell

# clean up cache and temp files
clean:
	@echo "[CLEAN] Cleaning up cache and temp files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@echo "[CLEAN] Cleanup completed successfully"

# complete setup for assessors  
all: setup migrate admin demo test
	@echo ""
	@echo "[SUCCESS] Complete setup finished successfully!"
	@echo ""
	@echo "Next steps:"
	@echo "  make start      - setup + start server immediately"
	@echo "  make run        - start server only"
	@echo ""
	@echo "Available URLs:"
	@echo "  http://127.0.0.1:8000/          - Blog homepage"
	@echo "  http://127.0.0.1:8000/api/posts/ - Posts API"
	@echo "  http://127.0.0.1:8000/admin/     - Admin panel (admin/admin123)"
	@echo ""
	@echo "[READY] Assessment ready for evaluation!"

# priority setup - complete setup and start server immediately
start: setup migrate admin demo test
	@echo ""
	@echo "[SUCCESS] Setup completed successfully!"
	@echo "[SUCCESS] Users created: admin/admin123 and testuser/testpass123"
	@echo "[SUCCESS] Demo data created: 3 posts and 4 comments"
	@echo "[SUCCESS] All tests passed"
	@echo ""
	@echo "[START] Launching development server..."
	@echo "[START] Server will be available at: http://127.0.0.1:8000"
	@echo "[START] API endpoints: http://127.0.0.1:8000/api/posts/"
	@echo "[START] Admin panel: http://127.0.0.1:8000/admin/"
	@echo "[START] Press Ctrl+C to stop the server"
	@echo ""
	@. venv/bin/activate && python manage.py runserver

# complete setup with demo data (for comprehensive testing)
full: setup migrate admin demo test
	@echo ""
	@echo "[SUCCESS] Full setup with demo data completed!"
	@echo ""
	@echo "Next steps:"
	@echo "  make run        - start server only"
	@echo ""
	@echo "Available URLs:"
	@echo "  http://127.0.0.1:8000/          - Blog homepage"
	@echo "  http://127.0.0.1:8000/api/posts/ - Posts API"
	@echo "  http://127.0.0.1:8000/admin/     - Admin panel (admin/admin123)"
	@echo ""
	@echo "[READY] Assessment ready for evaluation!"

# API Testing Commands
# Prerequisites: Server must be running (make run)
# Authentication: Uses predefined users (admin:admin123, testuser:testpass123)

# List posts with filtering capabilities
api-list:
	@echo "===================================================================================="
	@echo "API Test: List Posts with Filtering"
	@echo "===================================================================================="
	@echo ""
	@echo "Test 1: List all active posts"
	@echo "Command: curl -X GET http://127.0.0.1:8000/api/posts/"
	@echo "------------------------------------------------------------------------------------"
	@curl -s http://127.0.0.1:8000/api/posts/ \
		-w "\nHTTP Status: %{http_code}\n" | \
		(python -m json.tool 2>/dev/null || echo "Error: Server not running. Execute 'make run' first.")
	@echo ""
	@echo "Test 2: Filter posts by title containing 'django'"
	@echo "Command: curl -X GET 'http://127.0.0.1:8000/api/posts/?title=django'"
	@echo "------------------------------------------------------------------------------------"
	@curl -s "http://127.0.0.1:8000/api/posts/?title=django" -w "\nHTTP Status: %{http_code}\n" | python -m json.tool 2>/dev/null
	@echo ""
	@echo "Test 3: Filter posts by author name containing 'admin'"
	@echo "Command: curl -X GET 'http://127.0.0.1:8000/api/posts/?author__name=admin'"
	@echo "------------------------------------------------------------------------------------"
	@curl -s "http://127.0.0.1:8000/api/posts/?author__name=admin" -w "\nHTTP Status: %{http_code}\n" | python -m json.tool 2>/dev/null
	@echo ""

# Create a new post via API
api-create:
	@echo "===================================================================================="
	@echo "API Test: Create New Post"
	@echo "===================================================================================="
	@echo ""
	@echo "Authentication: admin:admin123"
	@echo "Endpoint: POST /api/posts/"
	@echo "Required fields: title, content, published_date, author_name"
	@echo ""
	@echo "Command:"
	@echo "curl -X POST http://127.0.0.1:8000/api/posts/ \\"
	@echo "  -H 'Content-Type: application/json' \\"
	@echo "  -u admin:admin123 \\"
	@echo "  -d '{\"title\":\"API Test Post\",\"content\":\"Post created via API\",\"published_date\":\"2025-09-15T10:00:00Z\",\"author_name\":\"API Tester\"}'"
	@echo "------------------------------------------------------------------------------------"
	@curl -X POST http://127.0.0.1:8000/api/posts/ \
		-H "Content-Type: application/json" \
		-u admin:admin123 \
		-d '{"title":"API Test Post","content":"This post was created via Makefile API automation.","published_date":"2025-09-15T10:00:00Z","author_name":"API Tester"}' \
		-w "\nHTTP Status: %{http_code}\n" -s | python -m json.tool 2>/dev/null
	@echo ""

# Edit an existing post
api-edit:
	@echo "===================================================================================="
	@echo "API Test: Edit Existing Post"
	@echo "===================================================================================="
	@echo ""
	@echo "Authentication: admin:admin123 (post owner only)"
	@echo "Endpoint: PATCH /api/posts/1/edit/"
	@echo "Editable fields: title, content, active"
	@echo ""
	@echo "Command:"
	@echo "curl -X PATCH http://127.0.0.1:8000/api/posts/1/edit/ \\"
	@echo "  -H 'Content-Type: application/json' \\"
	@echo "  -u admin:admin123 \\"
	@echo "  -d '{\"title\":\"Updated Post Title\",\"content\":\"Updated content\",\"active\":true}'"
	@echo "------------------------------------------------------------------------------------"
	@curl -X PATCH http://127.0.0.1:8000/api/posts/1/edit/ \
		-H "Content-Type: application/json" \
		-u admin:admin123 \
		-d '{"title":"Updated API Post","content":"This post was updated via Makefile automation.","active":true}' \
		-w "\nHTTP Status: %{http_code}\n" -s | python -m json.tool 2>/dev/null
	@echo ""

# Delete a post with confirmation
api-delete:
	@echo "===================================================================================="
	@echo "API Test: Delete Post"
	@echo "===================================================================================="
	@echo ""
	@echo "Authentication: admin:admin123 (post owner only)"
	@echo "Endpoint: DELETE /api/posts/3/delete/"
	@echo "WARNING: This operation permanently removes the post and all associated comments."
	@echo ""
	@read -p "Proceed with deletion of post ID 3? (y/N): " confirm && [ "$$confirm" = "y" ] || exit 1
	@echo ""
	@echo "Command:"
	@echo "curl -X DELETE http://127.0.0.1:8000/api/posts/3/delete/ \\"
	@echo "  -u admin:admin123"
	@echo "------------------------------------------------------------------------------------"
	@curl -X DELETE http://127.0.0.1:8000/api/posts/3/delete/ \
		-u admin:admin123 \
		-w "HTTP Status: %{http_code}\n" \
		-s -o /dev/null
	@echo "Post deletion completed."
	@echo ""

# Create a comment on an existing post
api-comment:
	@echo "===================================================================================="
	@echo "API Test: Create Comment"
	@echo "===================================================================================="
	@echo ""
	@echo "Authentication: testuser:testpass123 (authentication required)"
	@echo "Endpoint: POST /api/comments/"
	@echo "Required fields: post (ID), content"
	@echo "Target: Post ID 1"
	@echo ""
	@echo "Command:"
	@echo "curl -X POST http://127.0.0.1:8000/api/comments/ \\"
	@echo "  -H 'Content-Type: application/json' \\"
	@echo "  -u testuser:testpass123 \\"
	@echo "  -d '{\"post\":1,\"content\":\"Comment via API automation\"}'"
	@echo "------------------------------------------------------------------------------------"
	@curl -X POST http://127.0.0.1:8000/api/comments/ \
		-H "Content-Type: application/json" \
		-u testuser:testpass123 \
		-d '{"post":1,"content":"This comment was posted via Makefile API automation. Excellent post!"}' \
		-w "\nHTTP Status: %{http_code}\n" -s | python -m json.tool 2>/dev/null
	@echo ""

# Execute comprehensive API test suite
api-test:
	@echo "===================================================================================="
	@echo "Comprehensive API Test Suite"
	@echo "===================================================================================="
	@echo "Executing all API operations in sequence:"
	@echo "1. List posts with filters"
	@echo "2. Create new post"
	@echo "3. Edit existing post"
	@echo "4. Create comment"
	@echo ""
	@echo "Note: Delete operation excluded from automated suite for safety."
	@echo "      Run 'make api-delete' manually if needed."
	@echo ""
	@$(MAKE) api-list
	@$(MAKE) api-create
	@$(MAKE) api-edit
	@$(MAKE) api-comment
	@echo "===================================================================================="
	@echo "API Test Suite Completed"
	@echo "===================================================================================="
	@echo "Summary: All operations executed successfully."
	@echo "Review the output above for detailed results."
	@echo "Execute 'make api-list' to view updated post data."