# Variables
PYTHON = python3
PIP = pip3
DJANGO_MANAGE = $(PYTHON) manage.py
NPM = npm
FRONTEND_DIR = frontend
BACKEND_DIR = backend

# Default target
install: install-backend install-frontend

# install backend from backend/requirements.txt
install-backend:
	cd $(BACKEND_DIR) && $(PIP) install -r requirements.txt

# install frontend from frontend/package.json
install-frontend:
	cd $(FRONTEND_DIR) && $(NPM) install && $(NPM) install plotly.js-dist mitt

# clean artifacts
clean:
	rm -rf $(BACKEND_DIR)/__pycache__ $(FRONTEND_DIR)/dist

# start both servers concurrently
start:
	$(FRONTEND_DIR)/node_modules/.bin/concurrently --kill-others-on-fail "make runserver" "make rundev"

# start backend server
runserver:
	cd $(BACKEND_DIR) && $(DJANGO_MANAGE) runserver

# start frontend server
rundev:
	cd $(FRONTEND_DIR) && $(NPM) run dev

# this build frontend can additionally be used for a final production build (instead of run serve it will just build)
build-frontend:
	cd $(FRONTEND_DIR) && $(NPM) run build

# prevent errors from common names in case
.PHONY: install install-backend install-frontend build-frontend migrate runserver rundev clean start