# recipe-app-api

Recipe API: a Django REST Framework backend for managing recipes.

## Overview
This repo contains a Django 3.2 project (REST API) with PostgreSQL as the database. The project is configured to run with Docker Compose (recommended) and can also be run locally in a Python virtual environment.

## Tech stack
- Python 3.9
- Django 3.2
- Django REST Framework
- drf-spectacular (OpenAPI + Swagger)
- PostgreSQL
- Docker / Docker Compose (recommended)

## Prerequisites
- Docker & Docker Compose (recommended)
- OR: Python 3.9+, pip, virtualenv, and a running PostgreSQL instance

## Environment variables
The app reads database connection details from environment variables. Use these names:
- DB_HOST (e.g. db or localhost)
- DB_NAME (e.g. devdb)
- DB_USER (e.g. devuser)
- DB_PASS (e.g. changeme)
Optional (production):
- SECRET_KEY (provide a secure value)
- DEBUG (0/1 or true/false)

Example .env file (for local dev):
DB_HOST=localhost
DB_NAME=devdb
DB_USER=devuser
DB_PASS=changeme
SECRET_KEY=replace-with-secure-key
DEBUG=1

Note: docker-compose.yml uses POSTGRES_* env vars for the DB service and sets the app service DB_* env vars.

## Quickstart (recommended: Docker Compose)
1. Build and start services (from project root):
   docker-compose up --build
2. API available at: http://localhost:8000/
3. Swagger UI (interactive API docs): http://localhost:8000/api/docs/
4. Useful commands:
   - Run in background: docker-compose up -d
   - Stop and remove containers: docker-compose down
   - Remove the database volume (reset DB): docker-compose down -v

Default DB credentials in docker-compose.yml:
- POSTGRES_DB=devdb
- POSTGRES_USER=devuser
- POSTGRES_PASSWORD=changeme

The app service runs these on start: wait_for_db, migrate, runserver. When first starting, the DB will be created automatically by the Postgres image.

## Deployment

### Server Setup

#### Creating an SSH Deploy Key
To create a new SSH key that can be used as the deploy key, run the command below:

```bash
ssh-keygen -t ed25519 -b 4096
```

Note: This will create a new ed25519 key, which is the recommended key for GitHub.

To display the public key, run:

```bash
cat ~/.ssh/id_ed25519.pub
```

#### Install and Configure Dependencies
Use the commands below to configure the EC2 virtual machine running Amazon Linux 2.

Install Git:

```bash
sudo yum install git -y
```

Install Docker, enable it to start automatically, and give the `ec2-user` permission to use it:

```bash
sudo amazon-linux-extras install docker -y
sudo systemctl enable docker.service
sudo systemctl start docker.service
sudo usermod -aG docker ec2-user
```

Note: After running the above, you need to log out by typing `exit` and reconnect to the server for the permissions to take effect.

Install Docker Compose:

```bash
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### Running Docker Service

##### Cloning Code
Use Git to clone your project:

```bash
git clone <project ssh url>
```

Note: Ensure you create an `.env` file before starting the service.

##### Running Service
To start the service, run:

```bash
docker compose -f docker-compose-deploy.yml up -d
```

##### Stopping Service
To stop the service, run:

```bash
docker compose -f docker-compose-deploy.yml down
```

To stop the service and remove all data, run:

```bash
docker compose -f docker-compose-deploy.yml down --volumes
```

##### Viewing Logs
To view container logs, run:

```bash
docker compose -f docker-compose-deploy.yml logs
```

Add `-f` to the end of the command to follow the log output as it comes in.

##### Updating App
If you push new versions, pull the latest changes to the server by running the following command:

```bash
git pull origin
```

Then rebuild the app image so it includes the latest code:

```bash
docker compose -f docker-compose-deploy.yml build app
```

To apply the update, run:

```bash
docker compose -f docker-compose-deploy.yml up --no-deps -d app
```

The `--no-deps -d` option ensures that dependent services (such as the proxy) do not restart.

## Local development (without Docker)
1. Create and activate virtualenv:
   python3 -m venv .venv
   source .venv/bin/activate
2. Install dependencies:
   pip install --upgrade pip
   pip install -r requirements.txt
3. Ensure PostgreSQL is running and create a DB & user, or set env vars from an .env file or shell exports:
   export DB_HOST=localhost
   export DB_NAME=devdb
   export DB_USER=devuser
   export DB_PASS=changeme
4. Apply migrations and start server:
   python manage.py wait_for_db
   python manage.py migrate
   python manage.py createsuperuser  # optional: create admin user
   python manage.py runserver 0.0.0.0:8000

## Common management commands
- Wait for DB (helper provided): python manage.py wait_for_db
- Run migrations: python manage.py migrate
- Create admin user: python manage.py createsuperuser
- Run tests: python manage.py test
- Django shell: python manage.py shell

## Running tests
- With Docker: docker-compose run --rm app python manage.py test
- Locally (venv): python manage.py test

## Linting & development tools
- Dev dependencies are listed in requirements.dev.txt (e.g. flake8).
- Install and run flake8:
  pip install -r requirements.dev.txt
  flake8

## API docs
- OpenAPI JSON: /api/schema/
- Swagger UI: /api/docs/

## Troubleshooting & tips
- If ports are busy, adjust docker compose or pass a different host/port to runserver.
- If container fails on build due to dependencies, ensure build args are set correctly (docker-compose.yml passes DEV=true for dev deps).
- To run management commands inside the app container:
  docker compose -f docker-compose-deploy.yml run --rm app python manage.py <command>

## Security & production notes
- SECRET_KEY in settings.py is a development key. DO NOT use it in production — set SECRET_KEY via environment variables.
- DEBUG must be False in production.
- For production deployments, use a production-grade WSGI server (gunicorn/uvicorn) and a reverse proxy. This repo's Dockerfile is minimal and intended for development.
