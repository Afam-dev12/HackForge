"""Tests for user profiles."""
from app.extensions import db
from app.models import User


def _register_and_login(client, username="testuser", email="test@test.com", role="participant"):
    client.get("/logout", follow_redirects=True)
    client.post(f"/register/{role}", data={
        "username": username, "email": email,
        "password": "pass123", "confirm_password": "pass123",
    }, follow_redirects=True)
    client.post("/login", data={"email": email, "password": "pass123"}, follow_redirects=True)


def test_profile_view(client, db):
    with client.application.app_context():
        user = User(username="profileuser", email="profile@test.com", role="participant")
        user.set_password("pass123")
        db.session.add(user)
        db.session.commit()
        user_id = user.id

    resp = client.get(f"/profile/{user_id}")
    assert resp.status_code == 200
    assert b"profileuser" in resp.data


def test_profile_edit(client, db):
    _register_and_login(client)
    resp = client.post("/profile/edit", data={
        "bio": "I am a developer",
        "skills": "Python, Flask",
        "interests": "AI, Web",
        "experience_level": "Intermediate",
        "location": "Lagos, Nigeria",
        "github_url": "https://github.com/test",
        "portfolio_url": "https://test.dev",
    }, follow_redirects=True)
    assert resp.status_code == 200
    assert b"Profile updated" in resp.data
    assert b"I am a developer" in resp.data


def test_profile_edit_requires_login(client, db):
    resp = client.get("/profile/edit", follow_redirects=True)
    assert b"Login" in resp.data or b"Welcome Back" in resp.data


def test_builders_page(client, db):
    with client.application.app_context():
        user = User(username="builder1", email="b1@test.com", role="participant",
                    skills="Python, React", location="Nairobi")
        user.set_password("pass123")
        db.session.add(user)
        db.session.commit()

    resp = client.get("/builders")
    assert resp.status_code == 200
    assert b"builder1" in resp.data


def test_builders_search(client, db):
    with client.application.app_context():
        for name in ["alice", "bob"]:
            u = User(username=name, email=f"{name}@test.com", role="participant")
            u.set_password("pass123")
            db.session.add(u)
        db.session.commit()

    resp = client.get("/builders?search=alice")
    assert b"alice" in resp.data
    assert b"bob" not in resp.data


def test_skills_list_property(client, db):
    with client.application.app_context():
        user = User(username="skilltest", email="skill@test.com", role="participant")
        user.skills = "Python, Flask, React"
        assert user.skills_list == ["Python", "Flask", "React"]

        user2 = User(username="noskill", email="noskill@test.com", role="participant")
        assert user2.skills_list == []
