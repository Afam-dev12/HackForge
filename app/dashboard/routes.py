from flask import render_template, redirect, url_for
from flask_login import login_required, current_user

from . import dashboard_bp
from app.models import Hackathon, TeamMember, Submission, HackathonRegistration, Team


@dashboard_bp.route("/dashboard")
@login_required
def dashboard_page():
    if current_user.is_organizer:
        hackathons = Hackathon.query.filter_by(created_by=current_user.id).all()
    else:
        registrations = HackathonRegistration.query.filter_by(user_id=current_user.id).all()
        hackathon_ids = [r.hackathon_id for r in registrations]
        hackathons = Hackathon.query.filter(Hackathon.id.in_(hackathon_ids)).all() if hackathon_ids else []

    team_memberships = (
        TeamMember.query.filter_by(user_id=current_user.id).all()
    )
    my_teams = []
    for tm in team_memberships:
        team = Team.query.get(tm.team_id)
        if team:
            my_teams.append(team)

    submissions = Submission.query.filter_by(author_id=current_user.id).all()
    team_count = len(my_teams)
    submission_count = len(submissions)

    profile_complete = bool(current_user.bio and current_user.skills)
    profile_items = ["bio", "skills", "experience_level", "location"]
    completed = sum(1 for f in profile_items if getattr(current_user, f, ""))
    profile_percent = int((completed / len(profile_items)) * 100)

    return render_template(
        "dashboard.html",
        user=current_user,
        hackathons=hackathons,
        my_teams=my_teams,
        submissions=submissions,
        team_count=team_count,
        submission_count=submission_count,
        profile_complete=profile_complete,
        profile_percent=profile_percent,
    )
