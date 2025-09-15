# Django Blog Assessment - Makefile
# Author: Deric San Andres

.PHONY: help setup install migrate test run clean admin demo all

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