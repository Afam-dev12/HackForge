from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db


class User(UserMixin, db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default="participant")

    # Profile fields
    bio = db.Column(db.Text, default="")
    skills = db.Column(db.Text, default="")
    interests = db.Column(db.Text, default="")
    experience_level = db.Column(db.String(50), default="")
    location = db.Column(db.String(100), default="")
    github_url = db.Column(db.String(200), default="")
    portfolio_url = db.Column(db.String(200), default="")
    avatar_url = db.Column(db.String(200), default="")

    created_at = db.Column(db.DateTime, server_default=db.func.now())

    # Relationships
    hackathons_created = db.relationship("Hackathon", backref="organizer", lazy=True)
    team_memberships = db.relationship("TeamMember", backref="user", lazy=True)
    submissions = db.relationship("Submission", backref="author", lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def skills_list(self):
        if self.skills:
            return [s.strip() for s in self.skills.split(",") if s.strip()]
        return []

    @property
    def interests_list(self):
        if self.interests:
            return [i.strip() for i in self.interests.split(",") if i.strip()]
        return []

    @property
    def is_organizer(self):
        return self.role == "organizer"

    @property
    def is_judge(self):
        return self.role == "judge"

    @property
    def is_admin(self):
        return self.role == "admin"
