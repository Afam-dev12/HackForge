"""Tests for project submissions."""
from app.extensions import db
from app.models import User, Hackathon, Submission, Team, TeamMember


def _register_and_login(client, username="testuser", email="test@test.com", role="participant"):
    client.get("/logout", follow_redirects=True)
    client.post(f"/register/{role}", data={
        "username": username, "email": email,
        "password": "pass123", "confirm_password": "pass123",
    }, follow_redirects=True)
    client.post("/login", data={"email": email, "password": "pass123"}, follow_redirects=True)


def _setup_hackathon(client, db):
    with client.application.app_context():
        org = User(username="org_sub", email="orgs@test.com", role="organizer")
        org.set_password("pass123")
        db.session.add(org)
        db.session.flush()
        h = Hackathon(title="Submit Hack", description="Submit test", created_by=org.id, status="active")
        db.session.add(h)
        db.session.commit()
        return h.id


def test_submit_project(client, db):
    h_id = _setup_hackathon(client, db)
    _register_and_login(client)
    resp = client.post("/projects/submit", data={
        "title": "My Project",
        "description": "A cool project",
        "problem": "Solving X",
        "solution": "By doing Y",
        "technologies": "Python, Flask",
        "github_url": "https://github.com/test/project",
        "demo_url": "https://demo.test.dev",
        "hackathon_id": h_id,
    }, follow_redirects=True)
    assert resp.status_code == 200
    assert b"My Project" in resp.data


def test_submit_requires_title(client, db):
    h_id = _setup_hackathon(client, db)
    _register_and_login(client)
    resp = client.post("/projects/submit", data={
        "title": "",
        "description": "No title",
        "hackathon_id": h_id,
    }, follow_redirects=True)
    assert b"required" in resp.data


def test_duplicate_submission(client, db):
    h_id = _setup_hackathon(client, db)
    _register_and_login(client, username="dup_sub", email="dups@test.com")
    client.post("/projects/submit", data={
        "title": "First Submit", "description": "First", "hackathon_id": h_id,
    }, follow_redirects=True)
    resp = client.post("/projects/submit", data={
        "title": "Second Submit", "description": "Second", "hackathon_id": h_id,
    }, follow_redirects=True)
    assert b"already have a submission" in resp.data


def test_project_detail(client, db):
    h_id = _setup_hackathon(client, db)
    _register_and_login(client, username="det_sub", email="dets@test.com")
    client.post("/projects/submit", data={
        "title": "Detail Proj", "description": "Details here",
        "problem": "Problem X", "solution": "Solution Y",
        "technologies": "React, Node.js",
        "hackathon_id": h_id,
    }, follow_redirects=True)

    with client.application.app_context():
        sub = Submission.query.filter_by(title="Detail Proj").first()
        sub_id = sub.id

    resp = client.get(f"/projects/{sub_id}")
    assert resp.status_code == 200
    assert b"Detail Proj" in resp.data


def test_projects_list(client, db):
    resp = client.get("/projects")
    assert resp.status_code == 200
    assert b"Project showcase" in resp.data


def test_submit_requires_login(client, db):
    resp = client.get("/projects/submit", follow_redirects=True)
    assert b"Log in" in resp.data or b"Welcome back" in resp.data


def test_submit_with_invalid_team_rejected(client, db):
    h_id = _setup_hackathon(client, db)
    _register_and_login(client, username="team_hacker", email="th@test.com")

    with client.application.app_context():
        other_org = User(username="other_org", email="oo@test.com", role="organizer")
        other_org.set_password("pass123")
        db.session.add(other_org)
        db.session.flush()
        other_h = Hackathon(title="Other Hack", description="Different", created_by=other_org.id, status="active")
        db.session.add(other_h)
        db.session.flush()
        other_team = Team(name="Other Team", hackathon_id=other_h.id, created_by=other_org.id)
        db.session.add(other_team)
        db.session.commit()
        other_team_id = other_team.id

    resp = client.post("/projects/submit", data={
        "title": "Sneaky Project", "description": "Try to use other team",
        "hackathon_id": h_id, "team_id": other_team_id,
    }, follow_redirects=True)
    assert b"Invalid team" in resp.data


def test_submit_with_non_member_team_rejected(client, db):
    h_id = _setup_hackathon(client, db)
    _register_and_login(client, username="team_owner", email="to@test.com")

    client.post("/teams/create", data={
        "name": "Owner Team", "description": "My team", "hackathon_id": h_id,
    }, follow_redirects=True)

    with client.application.app_context():
        team = Team.query.filter_by(name="Owner Team").first()
        team_id = team.id

    _register_and_login(client, username="outsider", email="os@test.com")
    resp = client.post("/projects/submit", data={
        "title": "Intruder Project", "description": "Try to submit to other team",
        "hackathon_id": h_id, "team_id": team_id,
    }, follow_redirects=True)
    assert b"not a member" in resp.data
