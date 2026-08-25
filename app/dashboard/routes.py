from flask import render_template, redirect, url_for
from flask_login import login_required, current_user

from . import dashboard_bp
from app.models import Hackathon, TeamMember, Submission, HackathonRegistration


@dashboard_bp.route("/dashboard")
@login_required
def dashboard_page():
    if current_user.is_organizer:
        hackathons = Hackathon.query.filter_by(created_by=current_user.id).all()
    else:
        registrations = HackathonRegistration.query.filter_by(user_id=current_user.id).all()
        hackathon_ids = [r.hackathon_id for r in registrations]
        hackathons = Hackathon.query.filter(Hackathon.id.in_(hackathon_ids)).all()

    team_count = TeamMember.query.filter_by(user_id=current_user.id).count()
    submission_count = Submission.query.filter_by(author_id=current_user.id).count()

    return render_template(
        "dashboard.html",
        user=current_user,
        hackathons=hackathons,
        team_count=team_count,
        submission_count=submission_count,
    )
