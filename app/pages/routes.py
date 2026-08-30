from flask import current_app, render_template

from app.pages import pages_bp


@pages_bp.route("/about")
def about():
    return render_template("about.html")


@pages_bp.route("/contact")
def contact():
    return render_template("contact.html", contact_email=current_app.config.get("CONTACT_EMAIL"))


@pages_bp.route("/privacy")
def privacy():
    return render_template("privacy.html")