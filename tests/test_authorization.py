"""Tests for authorization and role-based access control."""
from app.extensions import db
from app.models import User, Hackathon


def _register_and_login(client, username="testuser", email="test@test.com", role="participant"):
    client.get("/logout", follow_redirects=True)
    client.post(f"/register/{role}", data={
        "username": username, "email": email,
        "password": "pass123", "confirm_password": "pass123",
    }, follow_redirects=True)
    client.post("/login", data={"email": email, "password": "pass123"}, follow_redirects=True)


def test_participant_cannot_create_hackathon(client, db):
    _register_and_login(client, role="participant")
    resp = client.get("/hackathons/create", follow_redirects=True)
    assert b"Only organizers" in resp.data


def test_organizer_can_create_hackathon(client, db):
    _register_and_login(client, username="org_access", email="orga@test.com", role="organizer")
    resp = client.get("/hackathons/create")
    assert resp.status_code == 200
    assert b"Create hackathon" in resp.data


def test_unauthenticated_cannot_submit(client, db):
    resp = client.get("/projects/submit", follow_redirects=True)
    assert b"Log in" in resp.data or b"Welcome back" in resp.data


def test_unauthenticated_cannot_create_team(client, db):
    resp = client.get("/teams/create", follow_redirects=True)
    assert b"Log in" in resp.data or b"Welcome back" in resp.data


def test_unauthenticated_cannot_edit_profile(client, db):
    resp = client.get("/profile/edit", follow_redirects=True)
    assert b"Log in" in resp.data or b"Welcome back" in resp.data


def test_organizer_cannot_judge_others_hackathon(client, db):
    with client.application.app_context():
        owner = User(username="owner_auth", email="own@test.com", role="organizer")
        owner.set_password("pass123")
        db.session.add(owner)
        db.session.flush()
        h = Hackathon(title="Private Hack", description="Not yours", created_by=owner.id, status="active")
        db.session.add(h)
        db.session.commit()
        h_id = h.id

    _register_and_login(client, username="other_org", email="otherorg@test.com", role="organizer")
    resp = client.get(f"/judging/hackathon/{h_id}", follow_redirects=True)
    assert b"do not have access" in resp.data


def test_judge_can_access_judging(client, db):
    with client.application.app_context():
        org = User(username="org_judge_test", email="ojt@test.com", role="organizer")
        org.set_password("pass123")
        db.session.add(org)
        judge = User(username="judge_auth", email="jauth@test.com", role="judge")
        judge.set_password("pass123")
        db.session.add(judge)
        db.session.flush()
        h = Hackathon(title="Judge Access Hack", description="Judge me", created_by=org.id, status="active")
        db.session.add(h)
        db.session.commit()
        h_id = h.id

    _register_and_login(client, username="judge_auth", email="jauth@test.com", role="judge")
    resp = client.get(f"/judging/hackathon/{h_id}")
    assert resp.status_code == 200


def test_home_redirects_logged_in_user(client, db):
    _register_and_login(client)
    resp = client.get("/", follow_redirects=True)
    assert b"Welcome" in resp.data


def test_home_shows_landing_for_anonymous(client, db):
    client.get("/logout", follow_redirects=True)
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"Discover" in resp.data and b"Build" in resp.data


def test_404_page(client, db):
    resp = client.get("/nonexistent-page-xyz")
    assert resp.status_code == 404
    assert b"404" in resp.data


def test_cannot_register_for_completed_hackathon(client, db):
    with client.application.app_context():
        org = User(username="org_completed", email="orgc@test.com", role="organizer")
        org.set_password("pass123")
        db.session.add(org)
        db.session.flush()
        h = Hackathon(title="Completed Hack", description="Already done",
                       created_by=org.id, status="completed")
        db.session.add(h)
        db.session.commit()
        h_id = h.id

    _register_and_login(client, username="late_reg", email="lr@test.com")
    resp = client.post(f"/hackathons/{h_id}/register", follow_redirects=True)
    assert b"has ended" in resp.data


def test_cannot_unregister_from_completed_hackathon(client, db):
    with client.application.app_context():
        org = User(username="org_completed2", email="orgc2@test.com", role="organizer")
        org.set_password("pass123")
        db.session.add(org)
        db.session.flush()
        h = Hackathon(title="Completed Hack 2", description="Done too",
                       created_by=org.id, status="completed")
        db.session.add(h)
        db.session.commit()
        h_id = h.id

    _register_and_login(client, username="late_reg2", email="lr2@test.com")
    resp = client.post(f"/hackathons/{h_id}/unregister", follow_redirects=True)
    assert b"has ended" in resp.data
