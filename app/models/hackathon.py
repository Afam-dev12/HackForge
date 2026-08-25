from app.extensions import db


class Hackathon(db.Model):
    __tablename__ = "hackathon"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    rules = db.Column(db.Text, default="")
    eligibility = db.Column(db.Text, default="")
    prize_info = db.Column(db.Text, default="")
    max_team_size = db.Column(db.Integer, default=5)
    location = db.Column(db.String(200), default="Online")
    status = db.Column(db.String(20), default="draft")
    start_date = db.Column(db.String(50))
    end_date = db.Column(db.String(50))
    created_by = db.Column(db.Integer, db.ForeignKey("user.id"))

    created_at = db.Column(db.DateTime, server_default=db.func.now())

    # Relationships
    registrations = db.relationship("HackathonRegistration", backref="hackathon", lazy=True, cascade="all, delete-orphan")
    teams = db.relationship("Team", backref="hackathon", lazy=True, cascade="all, delete-orphan")
    submissions = db.relationship("Submission", backref="hackathon", lazy=True, cascade="all, delete-orphan")
    criteria = db.relationship("JudgingCriteria", backref="hackathon", lazy=True, cascade="all, delete-orphan")

    @property
    def registration_count(self):
        return len(self.registrations)

    @property
    def team_count(self):
        return len(self.teams)

    @property
    def submission_count(self):
        return len(self.submissions)

    @property
    def status_display(self):
        return self.status.replace("_", " ").title()


class HackathonRegistration(db.Model):
    __tablename__ = "hackathon_registration"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    hackathon_id = db.Column(db.Integer, db.ForeignKey("hackathon.id"), nullable=False)
    registered_at = db.Column(db.DateTime, server_default=db.func.now())

    user = db.relationship("User", backref="hackathon_registrations")

    __table_args__ = (
        db.UniqueConstraint("user_id", "hackathon_id", name="unique_user_hackathon"),
    )


class JudgingCriteria(db.Model):
    __tablename__ = "judging_criteria"

    id = db.Column(db.Integer, primary_key=True)
    hackathon_id = db.Column(db.Integer, db.ForeignKey("hackathon.id"), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, default="")
    max_score = db.Column(db.Integer, default=10)

    scores = db.relationship("Score", backref="criteria", lazy=True, cascade="all, delete-orphan")
