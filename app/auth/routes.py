from flask import render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user

from . import auth_bp
from app.extensions import db
from app.models import User


@auth_bp.route("/")
def home():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.dashboard_page"))
    return render_template("index.html")


@auth_bp.route("/register/<role>", methods=["GET", "POST"])
@auth_bp.route("/register", methods=["GET", "POST"])
def register(role="participant"):
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.dashboard_page"))

    if role not in ("participant", "organizer"):
        role = "participant"

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        errors = []
        if not username:
            errors.append("Username is required.")
        if not email:
            errors.append("Email is required.")
        if len(password) < 6:
            errors.append("Password must be at least 6 characters.")
        if password != confirm_password:
            errors.append("Passwords do not match.")
        if User.query.filter_by(username=username).first():
            errors.append("Username already taken.")
        if User.query.filter_by(email=email).first():
            errors.append("Email already registered.")

        if errors:
            for e in errors:
                flash(e, "error")
            return render_template("register.html", role=role)

        user = User(
            username=username,
            email=email,
            role=role,
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash("Account created! Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html", role=role)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.dashboard_page"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            flash("Welcome back!", "success")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("dashboard.dashboard_page"))
        else:
            flash("Invalid email or password.", "error")

    return render_template("login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.home"))


@auth_bp.route("/profile/<int:user_id>")
def profile(user_id):
    user = User.query.get_or_404(user_id)
    from app.models import HackathonRegistration, TeamMember, Submission
    registrations = HackathonRegistration.query.filter_by(user_id=user.id).all()
    team_memberships = TeamMember.query.filter_by(user_id=user.id).all()
    submissions = Submission.query.filter_by(author_id=user.id).all()
    return render_template(
        "profile.html",
        profile_user=user,
        registrations=registrations,
        team_memberships=team_memberships,
        submissions=submissions,
    )


@auth_bp.route("/profile/edit", methods=["GET", "POST"])
@login_required
def edit_profile():
    if request.method == "POST":
        current_user.bio = request.form.get("bio", "").strip()
        current_user.skills = request.form.get("skills", "").strip()
        current_user.interests = request.form.get("interests", "").strip()
        current_user.experience_level = request.form.get("experience_level", "").strip()
        current_user.location = request.form.get("location", "").strip()
        current_user.github_url = request.form.get("github_url", "").strip()
        current_user.portfolio_url = request.form.get("portfolio_url", "").strip()
        db.session.commit()
        flash("Profile updated!", "success")
        return redirect(url_for("auth.profile", user_id=current_user.id))

    return render_template("edit_profile.html")


@auth_bp.route("/builders")
def builders():
    from app.models import User as UserModel
    users = UserModel.query.filter(UserModel.role != "admin").all()
    search = request.args.get("search", "").strip().lower()
    skill_filter = request.args.get("skill", "").strip().lower()

    if search:
        users = [
            u for u in users
            if search in u.username.lower() or search in u.email.lower() or search in (u.bio or "").lower()
        ]
    if skill_filter:
        users = [
            u for u in users
            if any(skill_filter in s.lower() for s in u.skills_list)
        ]

    return render_template("builders.html", users=users, search=search, skill_filter=skill_filter)
