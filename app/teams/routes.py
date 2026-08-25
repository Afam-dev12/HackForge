from flask import render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user

from . import team_bp
from app.extensions import db
from app.models import Team, TeamMember, Hackathon, HackathonRegistration


@team_bp.route("/teams")
@login_required
def teams_list():
    user_teams = (
        db.session.query(Team)
        .join(TeamMember, TeamMember.team_id == Team.id)
        .filter(TeamMember.user_id == current_user.id)
        .all()
    )
    return render_template("teams.html", teams=user_teams)


@team_bp.route("/teams/hackathon/<int:hackathon_id>")
@login_required
def teams_by_hackathon(hackathon_id):
    hackathon = Hackathon.query.get_or_404(hackathon_id)
    teams = Team.query.filter_by(hackathon_id=hackathon_id).all()
    return render_template(
        "teams.html",
        teams=teams,
        hackathon=hackathon,
    )


@team_bp.route("/teams/create", methods=["GET", "POST"])
@login_required
def create_team():
    hackathon_id = request.args.get("hackathon_id", request.form.get("hackathon_id", type=int))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        hackathon_id = request.form.get("hackathon_id", type=int)

        if not name or not hackathon_id:
            flash("Team name and hackathon are required.", "error")
            hackathons = Hackathon.query.filter_by(status="active").all()
            return render_template("create_team.html", hackathons=hackathons)

        hackathon = Hackathon.query.get_or_404(hackathon_id)

        existing_member = (
            db.session.query(TeamMember)
            .join(Team, Team.id == TeamMember.team_id)
            .filter(Team.hackathon_id == hackathon_id, TeamMember.user_id == current_user.id)
            .first()
        )
        if existing_member:
            flash("You are already in a team for this hackathon.", "error")
            return redirect(url_for("hackathons.hackathon_detail", hackathon_id=hackathon_id))

        team = Team(
            name=name,
            description=description,
            hackathon_id=hackathon_id,
            created_by=current_user.id,
        )
        db.session.add(team)
        db.session.flush()

        member = TeamMember(team_id=team.id, user_id=current_user.id, role="leader")
        db.session.add(member)
        db.session.commit()

        flash(f"Team '{name}' created!", "success")
        return redirect(url_for("teams.team_detail", team_id=team.id))

    hackathons = Hackathon.query.filter_by(status="active").all()
    return render_template("create_team.html", hackathons=hackathons, selected_hackathon=hackathon_id)


@team_bp.route("/teams/<int:team_id>")
def team_detail(team_id):
    team = Team.query.get_or_404(team_id)
    return render_template("team_detail.html", team=team)


@team_bp.route("/teams/<int:team_id>/join", methods=["POST"])
@login_required
def join_team(team_id):
    team = Team.query.get_or_404(team_id)

    existing = TeamMember.query.filter_by(team_id=team.id, user_id=current_user.id).first()
    if existing:
        flash("You are already in this team.", "info")
        return redirect(url_for("teams.team_detail", team_id=team.id))

    hackathon_id = team.hackathon_id
    existing_other = (
        db.session.query(TeamMember)
        .join(Team, Team.id == TeamMember.team_id)
        .filter(Team.hackathon_id == hackathon_id, TeamMember.user_id == current_user.id)
        .first()
    )
    if existing_other:
        flash("You are already in a team for this hackathon.", "error")
        return redirect(url_for("teams.team_detail", team_id=team.id))

    member = TeamMember(team_id=team.id, user_id=current_user.id, role="member")
    db.session.add(member)
    db.session.commit()

    flash("You joined the team!", "success")
    return redirect(url_for("teams.team_detail", team_id=team.id))


@team_bp.route("/teams/<int:team_id>/leave", methods=["POST"])
@login_required
def leave_team(team_id):
    member = TeamMember.query.filter_by(team_id=team_id, user_id=current_user.id).first()
    if not member:
        flash("You are not in this team.", "error")
        return redirect(url_for("teams.teams_list"))

    team = Team.query.get(team_id)
    if member.role == "leader":
        remaining = TeamMember.query.filter(
            TeamMember.team_id == team_id, TeamMember.user_id != current_user.id
        ).all()
        if remaining:
            remaining[0].role = "leader"
            db.session.delete(member)
            db.session.commit()
            flash("Leadership transferred. You left the team.", "info")
        else:
            db.session.delete(member)
            db.session.delete(team)
            db.session.commit()
            flash("Team deleted (no members remaining).", "info")
            return redirect(url_for("teams.teams_list"))
    else:
        db.session.delete(member)
        db.session.commit()
        flash("You left the team.", "info")

    return redirect(url_for("teams.teams_list"))
