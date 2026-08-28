"""Tests for teams: create, join, leave."""
from app.extensions import db
from app.models import User, Hackathon, Team, TeamMember


def _register_and_login(client, username="testuser", email="test@test.com", role="participant"):
    client.get("/logout", follow_redirects=True)
    client.post(f"/register/{role}", data={
        "username": username, "email": email,
        "password": "pass123", "confirm_password": "pass123",
    }, follow_redirects=True)
    client.post("/login", data={"email": email, "password": "pass123"}, follow_redirects=True)


def _setup_hackathon(client, db):
    with client.application.app_context():
        org = User(username="org_team", email="orgt@test.com", role="organizer")
        org.set_password("pass123")
        db.session.add(org)
        db.session.flush()
        h = Hackathon(title="Team Hack", description="Teams test", created_by=org.id, status="active")
        db.session.add(h)
        db.session.commit()
        return h.id


def test_create_team(client, db):
    h_id = _setup_hackathon(client, db)
    _register_and_login(client)
    resp = client.post("/teams/create", data={
        "name": "Test Team",
        "description": "We build stuff",
        "hackathon_id": h_id,
    }, follow_redirects=True)
    assert resp.status_code == 200
    assert b"Test Team" in resp.data


def test_join_team(client, db):
    h_id = _setup_hackathon(client, db)

    _register_and_login(client, username="leader", email="leader@test.com")
    client.post("/teams/create", data={
        "name": "Joinable Team", "description": "Join us", "hackathon_id": h_id,
    }, follow_redirects=True)

    with client.application.app_context():
        team = Team.query.filter_by(name="Joinable Team").first()
        team_id = team.id

    _register_and_login(client, username="joiner", email="joiner@test.com")
    resp = client.post(f"/teams/{team_id}/join", follow_redirects=True)
    assert b"joined the team" in resp.data


def test_leave_team(client, db):
    h_id = _setup_hackathon(client, db)

    _register_and_login(client, username="leaver", email="leaver@test.com")
    client.post("/teams/create", data={
        "name": "Leave Team", "description": "Leave test", "hackathon_id": h_id,
    }, follow_redirects=True)

    with client.application.app_context():
        team = Team.query.filter_by(name="Leave Team").first()
        team_id = team.id

    resp = client.post(f"/teams/{team_id}/leave", follow_redirects=True)
    assert b"Team deleted" in resp.data or b"left the team" in resp.data


def test_team_detail(client, db):
    h_id = _setup_hackathon(client, db)
    _register_and_login(client, username="detailer", email="det@test.com")
    client.post("/teams/create", data={
        "name": "Detail Team", "description": "Detail view", "hackathon_id": h_id,
    }, follow_redirects=True)

    with client.application.app_context():
        team = Team.query.filter_by(name="Detail Team").first()
        team_id = team.id

    resp = client.get(f"/teams/{team_id}")
    assert resp.status_code == 200
    assert b"Detail Team" in resp.data


def test_cannot_join_same_hackathon_twice(client, db):
    h_id = _setup_hackathon(client, db)

    _register_and_login(client, username="double1", email="d1@test.com")
    client.post("/teams/create", data={
        "name": "First Team", "description": "First", "hackathon_id": h_id,
    }, follow_redirects=True)

    _register_and_login(client, username="double2", email="d2@test.com")
    client.post("/teams/create", data={
        "name": "Second Team", "description": "Second", "hackathon_id": h_id,
    }, follow_redirects=True)

    with client.application.app_context():
        team1 = Team.query.filter_by(name="First Team").first()
        resp = client.post(f"/teams/{team1.id}/join", follow_redirects=True)
        assert b"already in a team" in resp.data


def test_teams_list(client, db):
    h_id = _setup_hackathon(client, db)
    _register_and_login(client, username="listmaker", email="lm@test.com")
    client.post("/teams/create", data={
        "name": "List Team", "description": "In list", "hackathon_id": h_id,
    }, follow_redirects=True)

    resp = client.get("/teams")
    assert resp.status_code == 200
    assert b"List Team" in resp.data


def test_create_team_requires_login(client, db):
    resp = client.get("/teams/create", follow_redirects=True)
    assert b"Log in" in resp.data or b"Welcome back" in resp.data


def test_max_team_size_enforced(client, db):
    h_id = _setup_hackathon(client, db)

    with client.application.app_context():
        hackathon = Hackathon.query.get(h_id)
        hackathon.max_team_size = 2
        db.session.commit()

    _register_and_login(client, username="leader1", email="l1@test.com")
    client.post("/teams/create", data={
        "name": "Small Team", "description": "Max 2", "hackathon_id": h_id,
    }, follow_redirects=True)

    with client.application.app_context():
        team = Team.query.filter_by(name="Small Team").first()
        team_id = team.id

    _register_and_login(client, username="member1", email="m1@test.com")
    resp = client.post(f"/teams/{team_id}/join", follow_redirects=True)
    assert b"joined the team" in resp.data

    _register_and_login(client, username="member2", email="m2@test.com")
    resp = client.post(f"/teams/{team_id}/join", follow_redirects=True)
    assert b"team is full" in resp.data
