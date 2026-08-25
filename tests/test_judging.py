"""Tests for judging: scoring, criteria, results."""
from app.extensions import db
from app.models import User, Hackathon, Submission, JudgingCriteria, Score


def _setup_judging_env(client, db):
    """Create organizer, judge, hackathon, criteria, and submission."""
    with client.application.app_context():
        org = User(username="org_judge", email="orgj@test.com", role="organizer")
        org.set_password("pass123")
        db.session.add(org)

        judge = User(username="judge1", email="j1@test.com", role="judge")
        judge.set_password("pass123")
        db.session.add(judge)

        builder = User(username="builder_j", email="bj@test.com", role="participant")
        builder.set_password("pass123")
        db.session.add(builder)
        db.session.flush()

        h = Hackathon(title="Judge Hack", description="Judge test", created_by=org.id, status="active")
        db.session.add(h)
        db.session.flush()

        c1 = JudgingCriteria(hackathon_id=h.id, name="Innovation", description="Originality", max_score=10)
        c2 = JudgingCriteria(hackathon_id=h.id, name="Impact", description="Real-world impact", max_score=10)
        db.session.add_all([c1, c2])
        db.session.flush()

        sub = Submission(
            title="Judgeable Proj", description="Score me",
            hackathon_id=h.id, author_id=builder.id,
        )
        db.session.add(sub)
        db.session.commit()

        return {
            "org_id": org.id,
            "judge_id": judge.id,
            "builder_id": builder.id,
            "hackathon_id": h.id,
            "criteria_id": c1.id,
            "submission_id": sub.id,
        }


def _login(client, email, password="pass123"):
    client.get("/logout", follow_redirects=True)
    client.post("/login", data={"email": email, "password": password}, follow_redirects=True)


def test_judging_dashboard(client, db):
    env = _setup_judging_env(client, db)
    _login(client, "orgj@test.com")
    resp = client.get(f"/judging/hackathon/{env['hackathon_id']}")
    assert resp.status_code == 200
    assert b"Judging Dashboard" in resp.data


def test_unauthorized_judging(client, db):
    env = _setup_judging_env(client, db)
    client.post("/register/participant", data={
        "username": "outsider", "email": "out@test.com",
        "password": "pass123", "confirm_password": "pass123",
    }, follow_redirects=True)
    _login(client, "out@test.com")
    resp = client.get(f"/judging/hackathon/{env['hackathon_id']}", follow_redirects=True)
    assert b"do not have access" in resp.data


def test_add_criteria(client, db):
    env = _setup_judging_env(client, db)
    _login(client, "orgj@test.com")
    resp = client.post(f"/judging/hackathon/{env['hackathon_id']}/criteria", data={
        "name": "Design",
        "description": "UI/UX quality",
        "max_score": 10,
    }, follow_redirects=True)
    assert b"Design" in resp.data


def test_judge_submission(client, db):
    env = _setup_judging_env(client, db)
    _login(client, "j1@test.com")
    resp = client.post(f"/judging/submission/{env['submission_id']}", data={
        "criteria_id": env["criteria_id"],
        "score": 8,
        "feedback": "Great work!",
    }, follow_redirects=True)
    assert b"Score saved" in resp.data


def test_score_out_of_range(client, db):
    env = _setup_judging_env(client, db)
    _login(client, "j1@test.com")
    resp = client.post(f"/judging/submission/{env['submission_id']}", data={
        "criteria_id": env["criteria_id"],
        "score": 999,
    }, follow_redirects=True)
    assert b"must be between" in resp.data


def test_results(client, db):
    env = _setup_judging_env(client, db)
    _login(client, "j1@test.com")
    client.post(f"/judging/submission/{env['submission_id']}", data={
        "criteria_id": env["criteria_id"],
        "score": 8,
    }, follow_redirects=True)

    resp = client.get(f"/results/hackathon/{env['hackathon_id']}")
    assert resp.status_code == 200
    assert b"Results" in resp.data
    assert b"Judgeable Proj" in resp.data


def test_calculate_average_score(client, db):
    env = _setup_judging_env(client, db)
    with client.application.app_context():
        sub = Submission.query.get(env["submission_id"])
        c1 = JudgingCriteria.query.get(env["criteria_id"])
        c2 = JudgingCriteria.query.filter(
            JudgingCriteria.hackathon_id == env["hackathon_id"],
            JudgingCriteria.name == "Impact",
        ).first()
        judge = User.query.get(env["judge_id"])

        s1 = Score(submission_id=sub.id, criteria_id=c1.id, judge_id=judge.id, score=8)
        s2 = Score(submission_id=sub.id, criteria_id=c2.id, judge_id=judge.id, score=6)
        db.session.add_all([s1, s2])
        db.session.commit()

        assert sub.total_score == 14
        assert sub.average_score == 7.0
