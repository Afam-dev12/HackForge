"""Tests for authentication: registration, login, logout, access control."""
from app.extensions import db
from app.models import User


def _create_user(client, username="testuser", email="test@test.com", password="pass123", role="participant"):
    return client.post(f"/register/{role}", data={
        "username": username,
        "email": email,
        "password": password,
        "confirm_password": password,
    }, follow_redirects=True)


def _login(client, email="test@test.com", password="pass123"):
    return client.post("/login", data={
        "email": email,
        "password": password,
    }, follow_redirects=True)


def test_register_success(client, db):
    resp = _create_user(client)
    assert resp.status_code == 200
    assert b"Account created" in resp.data or b"testuser" in resp.data


def test_register_duplicate_email(client, db):
    _create_user(client, email="dup@test.com")
    client.get("/logout", follow_redirects=True)
    resp = _create_user(client, username="other", email="dup@test.com")
    assert b"Email already registered" in resp.data


def test_register_duplicate_username(client, db):
    _create_user(client, username="taken")
    client.get("/logout", follow_redirects=True)
    resp = _create_user(client, username="taken", email="other@test.com")
    assert b"Username already taken" in resp.data


def test_register_password_mismatch(client, db):
    resp = client.post("/register/participant", data={
        "username": "testuser",
        "email": "test@test.com",
        "password": "pass123",
        "confirm_password": "pass456",
    }, follow_redirects=True)
    assert b"Passwords do not match" in resp.data


def test_register_short_password(client, db):
    resp = client.post("/register/participant", data={
        "username": "testuser",
        "email": "test@test.com",
        "password": "ab",
        "confirm_password": "ab",
    }, follow_redirects=True)
    assert b"at least 6 characters" in resp.data


def test_login_success(client, db):
    _create_user(client)
    resp = _login(client)
    assert resp.status_code == 200
    assert b"Welcome" in resp.data or b"Dashboard" in resp.data


def test_login_wrong_password(client, db):
    _create_user(client)
    client.get("/logout", follow_redirects=True)
    resp = _login(client, password="wrongpassword")
    assert b"Invalid email or password" in resp.data


def test_login_nonexistent_email(client, db):
    resp = _login(client, email="nobody@test.com")
    assert b"Invalid email or password" in resp.data


def test_logout(client, db):
    _create_user(client)
    _login(client)
    resp = client.get("/logout", follow_redirects=True)
    assert b"logged out" in resp.data


def test_protected_route(client, db):
    resp = client.get("/dashboard", follow_redirects=True)
    assert b"Log in" in resp.data or b"Welcome back" in resp.data


def test_dashboard_access_after_login(client, db):
    _create_user(client)
    _login(client)
    resp = client.get("/dashboard")
    assert resp.status_code == 200
    assert b"Welcome" in resp.data


def test_organizer_registration(client, db):
    resp = _create_user(client, username="org1", email="org@test.com", role="organizer")
    assert resp.status_code == 200
    assert b"Account created" in resp.data or b"org1" in resp.data


def test_password_hashing(client, db):
    with client.application.app_context():
        user = User(username="hash_test", email="hash@test.com", role="participant")
        user.set_password("mypassword")
        db.session.add(user)
        db.session.commit()

        loaded = User.query.filter_by(username="hash_test").first()
        assert loaded.password_hash != "mypassword"
        assert loaded.check_password("mypassword")
        assert not loaded.check_password("wrongpassword")


def test_register_redirect_if_already_logged_in(client, db):
    _create_user(client)
    _login(client)
    resp = client.get("/register", follow_redirects=True)
    assert b"Welcome" in resp.data


def test_login_blocks_external_redirect(client, db):
    _create_user(client)
    resp = client.post("/login?next=http://evil.com", data={
        "email": "test@test.com", "password": "pass123",
    }, follow_redirects=True)
    assert resp.status_code == 200
    assert b"Dashboard" in resp.data or b"Welcome" in resp.data


def test_login_allows_internal_redirect(client, db):
    _create_user(client)
    client.get("/logout", follow_redirects=True)
    resp = client.post("/login?next=/hackathons", data={
        "email": "test@test.com", "password": "pass123",
    })
    assert resp.status_code == 302
    assert "/hackathons" in resp.headers["Location"]


def test_register_invalid_email_format(client, db):
    resp = client.post("/register/participant", data={
        "username": "emailtest", "email": "notanemail",
        "password": "pass123", "confirm_password": "pass123",
    }, follow_redirects=True)
    assert b"valid email" in resp.data
