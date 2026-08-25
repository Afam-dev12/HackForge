"""Tests for opportunity hub."""
from app.extensions import db
from app.models import User, Opportunity, OpportunityBookmark


def _register_and_login(client, username="testuser", email="test@test.com"):
    client.get("/logout", follow_redirects=True)
    client.post(f"/register/participant", data={
        "username": username, "email": email,
        "password": "pass123", "confirm_password": "pass123",
    }, follow_redirects=True)
    client.post("/login", data={"email": email, "password": "pass123"}, follow_redirects=True)


def _create_opportunity(client, db, **kwargs):
    defaults = {
        "title": "Test Scholarship",
        "description": "A test opportunity",
        "category": "Scholarships",
        "organization": "Test Org",
        "location": "Africa",
        "url": "https://test.com",
        "deadline": "2026-12-31",
        "eligibility": "African students",
    }
    defaults.update(kwargs)
    with client.application.app_context():
        opp = Opportunity(**defaults)
        db.session.add(opp)
        db.session.commit()
        return opp.id


def test_opportunities_list(client, db):
    resp = client.get("/opportunities")
    assert resp.status_code == 200
    assert b"Opportunity Hub" in resp.data


def test_opportunity_detail(client, db):
    opp_id = _create_opportunity(client, db)
    resp = client.get(f"/opportunities/{opp_id}")
    assert resp.status_code == 200
    assert b"Test Scholarship" in resp.data


def test_filter_by_category(client, db):
    _create_opportunity(client, db, title="Scholarship One", category="Scholarships")
    _create_opportunity(client, db, title="Internship One", category="Internships")

    resp = client.get("/opportunities?category=Scholarships")
    assert b"Scholarship One" in resp.data
    assert b"Internship One" not in resp.data


def test_search_opportunities(client, db):
    _create_opportunity(client, db, title="Google Africa Scholarship")
    _create_opportunity(client, db, title="Flutterwave Internship")

    resp = client.get("/opportunities?search=Google")
    assert b"Google Africa Scholarship" in resp.data
    assert b"Flutterwave Internship" not in resp.data


def test_save_opportunity(client, db):
    opp_id = _create_opportunity(client, db)
    _register_and_login(client, username="saver", email="saver@test.com")
    resp = client.post(f"/opportunities/{opp_id}/save", follow_redirects=True)
    assert b"saved" in resp.data


def test_unsave_opportunity(client, db):
    opp_id = _create_opportunity(client, db)
    _register_and_login(client, username="unsaver", email="unsaver@test.com")
    client.post(f"/opportunities/{opp_id}/save", follow_redirects=True)
    resp = client.post(f"/opportunities/{opp_id}/save", follow_redirects=True)
    assert b"removed from saved" in resp.data


def test_saved_opportunities_page(client, db):
    opp_id = _create_opportunity(client, db)
    _register_and_login(client, username="page_saver", email="ps@test.com")
    client.post(f"/opportunities/{opp_id}/save", follow_redirects=True)

    resp = client.get("/saved")
    assert resp.status_code == 200
    assert b"Test Scholarship" in resp.data


def test_save_requires_login(client, db):
    opp_id = _create_opportunity(client, db)
    resp = client.post(f"/opportunities/{opp_id}/save", follow_redirects=True)
    assert b"Login" in resp.data or b"Welcome Back" in resp.data


def test_opportunity_categories(client, db):
    from app.opportunities.routes import CATEGORIES
    assert "Scholarships" in CATEGORIES
    assert "Hackathons" in CATEGORIES
    assert "Internships" in CATEGORIES
    assert "Fellowships" in CATEGORIES
    assert "Grants" in CATEGORIES
    assert "Events" in CATEGORIES
    assert "Free Courses" in CATEGORIES
    assert "Volunteering" in CATEGORIES
    assert "Competitions" in CATEGORIES
