from flask import Flask
from config import Config
from models import db, User, Hackathon
from flask_migrate import Migrate
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.config.from_object(Config)

db.init_app(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)

login_manager.login_view = "login"

@app.route("/")   
def home():
    return render_template("index.html")

@app.route("/register/organizer")
def register_organizer():

    return render_template(
        "register.html",
        role="organizer"
    )

@app.route("/register/participant")
def register_participant():

    return render_template(
        "register.html",
        role="participant"
    )

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

@app.route("/register", methods=["GET", "POST"])    
def register():

    if request.method == "POST":

        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        role = request.form["role"]

        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            flash("An account with that email already exists")
            return redirect(url_for("register"))

        hashed_password = generate_password_hash(password)

        user = User(
            username=username,
            email=email,
            password=hashed_password,
            role=role
        )

        db.session.add(user)
        db.session.commit()

        login_user(user)

        flash("Registration successful. Welcome to HackForge!")

        return redirect(url_for("dashboard"))
    
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):

            login_user(user)

            flash(f"Welcome back, {user.username}")

            return redirect(url_for("dashboard"))
        flash("incorrect email or password.")

    return render_template("login.html")


@app.route("/dashboard")
@login_required
def dashboard():

    hackathons = Hackathon.query.filter_by(
        created_by=current_user.id
    ).all()

    return render_template(
        "dashboard.html",
        user=current_user,
        hackathons=hackathons
    )

@app.route("/logout")
@login_required
def logout():

    logout_user()

    flash("You have been logged out.")

    return redirect(url_for("login"))

@app.route("/create-hackathon", methods=["Get", "POST"])
@login_required
def create_hackathon():

    if request.method == "POST":

        title = request.form["title"]
        description = request.form["description"]
        start_date = request.form["start_date"]
        end_date = request.form["end_date"]

        hackathon = Hackathon(
            title=title,
            description=description,
            start_date=start_date,
            end_date=end_date,
            created_by=current_user.id
        )

        db.session.add(hackathon)
        db.session.commit()

        return redirect(url_for("dashboard"))
    return render_template("create_hackathon.html")

if __name__ == "__main__":
    app.run(debug=True)