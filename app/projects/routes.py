from flask import render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user

from . import project_bp
from app.extensions import db
from app.models import Submission, Team, TeamMember, Hackathon, Score


@project_bp.route("/projects")
def projects_list():
    submissions = Submission.query.order_by(Submission.created_at.desc()).all()
    return render_template("projects.html", submissions=submissions)


@project_bp.route("/projects/<int:project_id>")
def project_detail(project_id):
    submission = Submission.query.get_or_404(project_id)
    return render_template("project_detail.html", submission=submission)


@project_bp.route("/projects/submit", methods=["GET", "POST"])
@login_required
def submit_project():
    hackathon_id = request.args.get("hackathon_id", request.form.get("hackathon_id", type=int))

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        problem = request.form.get("problem", "").strip()
        solution = request.form.get("solution", "").strip()
        technologies = request.form.get("technologies", "").strip()
        github_url = request.form.get("github_url", "").strip()
        demo_url = request.form.get("demo_url", "").strip()
        extra_links = request.form.get("extra_links", "").strip()
        hackathon_id = request.form.get("hackathon_id", type=int)
        team_id = request.form.get("team_id", type=int)

        if not title or not description or not hackathon_id:
            flash("Title, description, and hackathon are required.", "error")
            return render_template("submit_project.html", hackathon_id=hackathon_id)

        if team_id:
            team = Team.query.get(team_id)
            if not team or team.hackathon_id != hackathon_id:
                flash("Invalid team for this hackathon.", "error")
                return render_template("submit_project.html", hackathon_id=hackathon_id)
            if not team.is_member(current_user.id):
                flash("You are not a member of this team.", "error")
                return render_template("submit_project.html", hackathon_id=hackathon_id)

        hackathon = Hackathon.query.get_or_404(hackathon_id)

        existing = Submission.query.filter_by(
            hackathon_id=hackathon_id, author_id=current_user.id
        ).first()
        if existing:
            flash("You already have a submission for this hackathon.", "error")
            return redirect(url_for("projects.project_detail", project_id=existing.id))

        submission = Submission(
            title=title,
            description=description,
            problem=problem,
            solution=solution,
            technologies=technologies,
            github_url=github_url,
            demo_url=demo_url,
            extra_links=extra_links,
            hackathon_id=hackathon_id,
            team_id=team_id,
            author_id=current_user.id,
        )
        db.session.add(submission)
        db.session.commit()

        flash("Project submitted!", "success")
        return redirect(url_for("projects.project_detail", project_id=submission.id))

    my_teams = []
    if hackathon_id:
        my_teams = (
            db.session.query(Team)
            .join(TeamMember, TeamMember.team_id == Team.id)
            .filter(Team.hackathon_id == hackathon_id, TeamMember.user_id == current_user.id)
            .all()
        )

    hackathons = Hackathon.query.filter_by(status="active").all()
    return render_template(
        "submit_project.html",
        hackathons=hackathons,
        selected_hackathon=hackathon_id,
        my_teams=my_teams,
    )
