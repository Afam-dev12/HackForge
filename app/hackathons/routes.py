from flask import render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user

from . import hackathon_bp
from app.extensions import db
from app.models import (
    Hackathon, HackathonRegistration, Team, TeamMember, Submission
)


@hackathon_bp.route("/hackathons")
def hackathons_list():
    status_filter = request.args.get("status", "")
    search = request.args.get("search", "").strip()

    query = Hackathon.query

    if status_filter:
        query = query.filter_by(status=status_filter)
    if search:
        query = query.filter(Hackathon.title.ilike(f"%{search}%"))

    hackathons = query.order_by(Hackathon.created_at.desc()).all()
    return render_template(
        "hackathons.html",
        hackathons=hackathons,
        search=search,
        status_filter=status_filter,
    )


@hackathon_bp.route("/hackathons/<int:hackathon_id>")
def hackathon_detail(hackathon_id):
    hackathon = Hackathon.query.get_or_404(hackathon_id)
    is_registered = False
    if current_user.is_authenticated:
        is_registered = HackathonRegistration.query.filter_by(
            user_id=current_user.id, hackathon_id=hackathon.id
        ).first() is not None

    return render_template(
        "hackathon_detail.html",
        hackathon=hackathon,
        is_registered=is_registered,
    )


@hackathon_bp.route("/hackathons/<int:hackathon_id>/register", methods=["POST"])
@login_required
def register_for_hackathon(hackathon_id):
    hackathon = Hackathon.query.get_or_404(hackathon_id)

    existing = HackathonRegistration.query.filter_by(
        user_id=current_user.id, hackathon_id=hackathon.id
    ).first()
    if existing:
        flash("You are already registered for this hackathon.", "info")
        return redirect(url_for("hackathons.hackathon_detail", hackathon_id=hackathon.id))

    reg = HackathonRegistration(user_id=current_user.id, hackathon_id=hackathon.id)
    db.session.add(reg)
    db.session.commit()

    flash("Successfully registered for the hackathon!", "success")
    return redirect(url_for("hackathons.hackathon_detail", hackathon_id=hackathon.id))


@hackathon_bp.route("/hackathons/<int:hackathon_id>/unregister", methods=["POST"])
@login_required
def unregister_from_hackathon(hackathon_id):
    reg = HackathonRegistration.query.filter_by(
        user_id=current_user.id, hackathon_id=hackathon_id
    ).first()
    if reg:
        db.session.delete(reg)
        db.session.commit()
        flash("You have unregistered from the hackathon.", "info")
    return redirect(url_for("hackathons.hackathon_detail", hackathon_id=hackathon_id))


@hackathon_bp.route("/hackathons/create", methods=["GET", "POST"])
@login_required
def create_hackathon():
    if not current_user.is_organizer:
        flash("Only organizers can create hackathons.", "error")
        return redirect(url_for("hackathons.hackathons_list"))

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        rules = request.form.get("rules", "").strip()
        eligibility = request.form.get("eligibility", "").strip()
        prize_info = request.form.get("prize_info", "").strip()
        max_team_size = request.form.get("max_team_size", 5, type=int)
        location = request.form.get("location", "Online").strip()
        status = request.form.get("status", "draft")
        start_date = request.form.get("start_date", "")
        end_date = request.form.get("end_date", "")

        if not title or not description:
            flash("Title and description are required.", "error")
            return render_template("create_hackathon.html")

        hackathon = Hackathon(
            title=title,
            description=description,
            rules=rules,
            eligibility=eligibility,
            prize_info=prize_info,
            max_team_size=max_team_size,
            location=location,
            status=status,
            start_date=start_date,
            end_date=end_date,
            created_by=current_user.id,
        )
        db.session.add(hackathon)
        db.session.commit()

        flash("Hackathon created!", "success")
        return redirect(url_for("hackathons.hackathon_detail", hackathon_id=hackathon.id))

    return render_template("create_hackathon.html")


@hackathon_bp.route("/hackathons/<int:hackathon_id>/edit", methods=["GET", "POST"])
@login_required
def edit_hackathon(hackathon_id):
    hackathon = Hackathon.query.get_or_404(hackathon_id)
    if hackathon.created_by != current_user.id:
        flash("You can only edit your own hackathons.", "error")
        return redirect(url_for("hackathons.hackathon_detail", hackathon_id=hackathon.id))

    if request.method == "POST":
        hackathon.title = request.form.get("title", hackathon.title).strip()
        hackathon.description = request.form.get("description", hackathon.description).strip()
        hackathon.rules = request.form.get("rules", "").strip()
        hackathon.eligibility = request.form.get("eligibility", "").strip()
        hackathon.prize_info = request.form.get("prize_info", "").strip()
        hackathon.max_team_size = request.form.get("max_team_size", hackathon.max_team_size, type=int)
        hackathon.location = request.form.get("location", hackathon.location).strip()
        hackathon.status = request.form.get("status", hackathon.status)
        hackathon.start_date = request.form.get("start_date", "")
        hackathon.end_date = request.form.get("end_date", "")
        db.session.commit()

        flash("Hackathon updated!", "success")
        return redirect(url_for("hackathons.hackathon_detail", hackathon_id=hackathon.id))

    return render_template("edit_hackathon.html", hackathon=hackathon)


@hackathon_bp.route("/hackathons/<int:hackathon_id>/participants")
@login_required
def hackathon_participants(hackathon_id):
    hackathon = Hackathon.query.get_or_404(hackathon_id)
    if hackathon.created_by != current_user.id:
        flash("Only the organizer can view participants.", "error")
        return redirect(url_for("hackathons.hackathon_detail", hackathon_id=hackathon.id))

    registrations = HackathonRegistration.query.filter_by(hackathon_id=hackathon.id).all()
    participants = [r.user for r in registrations]

    return render_template(
        "hackathon_participants.html",
        hackathon=hackathon,
        participants=participants,
    )
