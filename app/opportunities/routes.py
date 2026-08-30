from flask import render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user

from . import opportunity_bp
from app.extensions import db
from app.models import Opportunity, OpportunityBookmark


CATEGORIES = [
    "Hackathons", "Scholarships", "Internships", "Fellowships",
    "Competitions", "Volunteering", "Free Courses", "Grants", "Events",
]


@opportunity_bp.route("/opportunities")
def opportunities_list():
    category = request.args.get("category", "")
    search = request.args.get("search", "").strip()

    query = Opportunity.query.filter_by(is_active=True)

    if category:
        query = query.filter_by(category=category)
    if search:
        query = query.filter(Opportunity.title.ilike(f"%{search}%"))

    opportunities = query.order_by(Opportunity.created_at.desc()).all()
    return render_template(
        "opportunities.html",
        opportunities=opportunities,
        categories=CATEGORIES,
        selected_category=category,
        search=search,
        auth_required=not current_user.is_authenticated,
    )


@opportunity_bp.route("/opportunities/<int:opportunity_id>")
def opportunity_detail(opportunity_id):
    opportunity = Opportunity.query.get_or_404(opportunity_id)
    is_saved = False
    if current_user.is_authenticated:
        is_saved = OpportunityBookmark.query.filter_by(
            user_id=current_user.id, opportunity_id=opportunity.id
        ).first() is not None
    return render_template(
        "opportunity_detail.html",
        opportunity=opportunity,
        is_saved=is_saved,
        auth_required=not current_user.is_authenticated,
    )


@opportunity_bp.route("/opportunities/<int:opportunity_id>/save", methods=["POST"])
@login_required
def save_opportunity(opportunity_id):
    existing = OpportunityBookmark.query.filter_by(
        user_id=current_user.id, opportunity_id=opportunity_id
    ).first()
    if existing:
        db.session.delete(existing)
        db.session.commit()
        flash("Opportunity removed from saved list.", "info")
    else:
        bookmark = OpportunityBookmark(user_id=current_user.id, opportunity_id=opportunity_id)
        db.session.add(bookmark)
        db.session.commit()
        flash("Opportunity saved!", "success")
    return redirect(url_for("opportunities.opportunity_detail", opportunity_id=opportunity_id))


@opportunity_bp.route("/saved")
@login_required
def saved_opportunities():
    bookmarks = OpportunityBookmark.query.filter_by(user_id=current_user.id).all()
    opportunities = [b.opportunity for b in bookmarks]
    return render_template(
        "opportunities.html",
        opportunities=opportunities,
        categories=CATEGORIES,
        selected_category="",
        search="",
        page_title="Saved Opportunities",
    )


@opportunity_bp.route("/create", methods=["GET", "POST"])
@login_required
def create_opportunity():
    if not current_user.is_organizer:
        flash("Only organizers can create opportunities.", "error")
        return redirect(url_for("opportunities.opportunities_list"))

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        category = request.form.get("category", "")
        organization = request.form.get("organization", "").strip()
        location = request.form.get("location", "Online").strip()
        deadline = request.form.get("deadline", "").strip()

        if not title or not description or not category:
            flash("Title, description, and category are required.", "error")
            return render_template("create_opportunity.html")

        opportunity = Opportunity(
            title=title,
            description=description,
            category=category,
            organization=organization,
            location=location,
            deadline=deadline,
        )
        db.session.add(opportunity)
        db.session.commit()
        flash("Opportunity created!", "success")
        return redirect(url_for("opportunities.opportunities_list"))

    return render_template("create_opportunity.html")
