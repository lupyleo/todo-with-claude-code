# Flask Todo Web App

A Flask-based Todo web application with REST API and web UI.

## Tech Stack

- **Language**: Python 3.9
- **Framework**: Flask 3.0
- **ORM**: Flask-SQLAlchemy
- **Database**: SQLite
- **Templating**: Jinja2
- **Testing**: pytest
- **Server**: gunicorn
- **Architecture**: Flask app factory pattern

## Project Structure

```
.
├── CLAUDE.md
├── app/
│   ├── __init__.py          # Flask app factory (create_app)
│   ├── models.py            # SQLAlchemy models
│   ├── routes.py            # API & view routes
│   ├── templates/           # Jinja2 templates
│   └── static/              # CSS, JS, images
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Test fixtures
│   ├── test_models.py       # Model tests
│   └── test_api.py          # API endpoint tests
├── docs/
│   └── requirements.md      # Requirements & scenarios
├── config.py                # Flask configuration classes
├── wsgi.py                  # WSGI entry point
├── requirements.txt         # Python dependencies
└── .gitignore
```

## Team Roles & File Ownership

### PM (Product Manager)
- **Role**: Architect, coordinator, and task manager. Does NOT write code.
- **Owns**: `docs/`, `CLAUDE.md`
- **Does NOT touch**: `app/`, `tests/`

### Dev (Developer)
- **Role**: Feature implementation based on PM's task definitions.
- **Owns**: `app/`, `config.py`, `wsgi.py`, `requirements.txt`
- **Does NOT touch**: `tests/`, `docs/`

### QA (Quality Assurance)
- **Role**: Test writer and validator.
- **Owns**: `tests/`
- **Does NOT touch**: `app/`, `docs/`

## Coding Conventions

- Use type hints for all function signatures
- Follow PEP 8 style
- Keep functions small and single-purpose
- Use descriptive variable names

## Commit Conventions

- Use conventional commits: `feat:`, `fix:`, `test:`, `docs:`, `refactor:`
- Each commit should represent one logical unit of work
