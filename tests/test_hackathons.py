"""Tests for hackathons: create, discover, detail, register."""
from app.extensions import db
from app.models import User, Hackathon, HackathonRegistration


def _register_and_login(client, username="testuser", email="test@test.com", role="participant"):
    client.post(f"/register/{role}", data={
        "username": username, "email": email,
        "password": "pass123", "confirm_password": "pass123",
    }, follow_redirects=True)
    client.post("/login", data={"email": email, "password": "pass123"}, follow_redirects=True)


def test_hackathons_list(client, db):
    resp = client.get("/hackathons")
    assert resp.status_code == 200
    assert b"Hackathons" in resp.data


def test_organizer_can_create_hackathon(client, db):
    _register_and_login(client, role="organizer")
    resp = client.post("/hackathons/create", data={
        "title": "Test Hack",
        "description": "A test hackathon",
        "rules": "No rules",
        "eligibility": "Everyone",
        "prize_info": "$1000",
        "max_team_size": 4,
        "location": "Online",
        "status": "active",
        "start_date": "2026-09-01",
        "end_date": "2026-09-03",
    }, follow_redirects=True)
    assert resp.status_code == 200
    assert b"Test Hack" in resp.data


def test_participant_cannot_create_hackathon(client, db):
    _register_and_login(client, role="participant")
    resp = client.post("/hackathons/create", data={
        "title": "Should Fail",
        "description": "Not allowed",
    }, follow_redirects=True)
    assert b"Only organizers" in resp.data


def test_hackathon_detail(client, db):
    with client.application.app_context():
        user = User(username="org1", email="org@test.com", role="organizer")
        user.set_password("pass123")
        db.session.add(user)
        db.session.flush()
        h = Hackathon(title="Detail Hack", description="Details here", created_by=user.id, status="active")
        db.session.add(h)
        db.session.commit()
        h_id = h.id

    resp = client.get(f"/hackathons/{h_id}")
    assert resp.status_code == 200
    assert b"Detail Hack" in resp.data
    assert b"Details here" in resp.data


def test_register_for_hackathon(client, db):
    with client.application.app_context():
        org = User(username="org2", email="org2@test.com", role="organizer")
        org.set_password("pass123")
        db.session.add(org)
        db.session.flush()
        h = Hackathon(title="Reg Hack", description="Register me", created_by=org.id, status="active")
        db.session.add(h)
        db.session.commit()
        h_id = h.id

    _register_and_login(client, username="participant1", email="p1@test.com")
    resp = client.post(f"/hackathons/{h_id}/register", follow_redirects=True)
    assert resp.status_code == 200
    assert b"Successfully registered" in resp.data


def test_duplicate_registration(client, db):
    with client.application.app_context():
        org = User(username="org3", email="org3@test.com", role="organizer")
        org.set_password("pass123")
        db.session.add(org)
        db.session.flush()
        h = Hackathon(title="Dup Hack", description="Dup test", created_by=org.id, status="active")
        db.session.add(h)
        db.session.commit()
        h_id = h.id

    _register_and_login(client)
    client.post(f"/hackathons/{h_id}/register", follow_redirects=True)
    resp = client.post(f"/hackathons/{h_id}/register", follow_redirects=True)
    assert b"already registered" in resp.data


def test_unregister_from_hackathon(client, db):
    with client.application.app_context():
        org = User(username="org4", email="org4@test.com", role="organizer")
        org.set_password("pass123")
        db.session.add(org)
        db.session.flush()
        h = Hackathon(title="Unreg Hack", description="Unreg test", created_by=org.id, status="active")
        db.session.add(h)
        db.session.commit()
        h_id = h.id

    _register_and_login(client, username="leaver", email="leaver@test.com")
    client.post(f"/hackathons/{h_id}/register", follow_redirects=True)
    resp = client.post(f"/hackathons/{h_id}/unregister", follow_redirects=True)
    assert b"unregistered" in resp.data


def test_edit_hackathon(client, db):
    _register_and_login(client, username="editor", email="editor@test.com", role="organizer")
    client.post("/hackathons/create", data={
        "title": "Old Title", "description": "Old Desc", "status": "draft",
        "location": "Online", "max_team_size": 5,
    }, follow_redirects=True)

    with client.application.app_context():
        h = Hackathon.query.filter_by(title="Old Title").first()
        assert h is not None, "Hackathon was not created"
        h_id = h.id

    resp = client.post(f"/hackathons/{h_id}/edit", data={
        "title": "New Title", "description": "New Desc", "status": "active",
        "location": "Online", "max_team_size": 5,
    }, follow_redirects=True)
    assert b"New Title" in resp.data
    assert b"Hackathon updated" in resp.data


def test_cannot_edit_others_hackathon(client, db):
    with client.application.app_context():
        owner = User(username="owner", email="owner@test.com", role="organizer")
        owner.set_password("pass123")
        db.session.add(owner)
        db.session.flush()
        h = Hackathon(title="Owned Hack", description="Mine", created_by=owner.id, status="active")
        db.session.add(h)
        db.session.commit()
        h_id = h.id

    _register_and_login(client, username="intruder", email="intruder@test.com", role="organizer")
    resp = client.post(f"/hackathons/{h_id}/edit", data={
        "title": "Hacked", "description": "Stolen",
    }, follow_redirects=True)
    assert b"only edit your own" in resp.data


def test_search_hackathons(client, db):
    with client.application.app_context():
        org = User(username="searchorg", email="sorg@test.com", role="organizer")
        org.set_password("pass123")
        db.session.add(org)
        db.session.flush()
        db.session.add(Hackathon(title="Unique Alpha", description="A", created_by=org.id, status="active"))
        db.session.add(Hackathon(title="Unique Beta", description="B", created_by=org.id, status="draft"))
        db.session.commit()

    resp = client.get("/hackathons?search=Alpha")
    assert b"Unique Alpha" in resp.data
    assert b"Unique Beta" not in resp.data


def test_filter_by_status(client, db):
    with client.application.app_context():
        org = User(username="filtorg", email="forg@test.com", role="organizer")
        org.set_password("pass123")
        db.session.add(org)
        db.session.flush()
        db.session.add(Hackathon(title="Active One", description="A", created_by=org.id, status="active"))
        db.session.add(Hackathon(title="Draft One", description="B", created_by=org.id, status="draft"))
        db.session.commit()

    resp = client.get("/hackathons?status=active")
    assert b"Active One" in resp.data
    assert b"Draft One" not in resp.data
