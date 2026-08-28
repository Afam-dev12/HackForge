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
