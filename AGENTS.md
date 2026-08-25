# HACKFORGE — AGENTS.md

## Product
HACKFORGE — ecosystem for young builders. **DISCOVER → CONNECT → BUILD → LAUNCH → GROW**.

## Stack
Python 3.12, Flask, Flask Blueprints, Flask-SQLAlchemy, Flask-Migrate, Flask-Login, PostgreSQL, Jinja2, HTML/CSS/JS.

## Architecture
- **App factory** in `app/__init__.py`
- **Extensions** in `app/extensions.py` (db, login_manager, migrate)
- **Models** in `app/models/` (user.py, hackathon.py, team.py, submission.py, opportunity.py, judging.py)
- **Blueprints**: auth, dashboard, hackathons, teams, projects, opportunities, judging
- **Services** pattern: each blueprint has routes.py + services.py
- **Templates** in `app/templates/` (Jinja2, extend base.html)
- **Static** in `app/static/css/style.css`

## Rules
1. Never store plaintext passwords. Use werkzeug password hashing.
2. CSRF on all state-changing forms.
3. Role-based access: participant, organizer, judge, admin.
4. Never commit .env or secrets.
5. PostgreSQL for all database operations.
6. Use Flask-Migrate for schema changes.
7. Preserve existing architecture. Add, don't replace.
8. Tests in `tests/` directory using pytest.
9. Africa-first focus with global reach.
10. MVP scope only — no AI, chat, payments, or complex analytics.

## Starting the App
```bash
# Install dependencies
pip install -r requirements.txt

# Set up database (PostgreSQL)
# Create .env with DATABASE_URL and SECRET_KEY

# Run migrations
flask db upgrade

# Start app
python run.py
```

## Running Tests
```bash
pytest tests/ -v
```
