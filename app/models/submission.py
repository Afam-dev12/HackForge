from app.extensions import db


class Submission(db.Model):
    __tablename__ = "submission"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    problem = db.Column(db.Text, default="")
    solution = db.Column(db.Text, default="")
    technologies = db.Column(db.String(300), default="")
    github_url = db.Column(db.String(200), default="")
    demo_url = db.Column(db.String(200), default="")
    extra_links = db.Column(db.Text, default="")

    hackathon_id = db.Column(db.Integer, db.ForeignKey("hackathon.id"), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey("team.id"), nullable=True)
    author_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    scores = db.relationship("Score", backref="submission", lazy=True, cascade="all, delete-orphan")

    @property
    def technologies_list(self):
        if self.technologies:
            return [t.strip() for t in self.technologies.split(",") if t.strip()]
        return []

    @property
    def average_score(self):
        if not self.scores:
            return 0
        total = sum(s.score for s in self.scores)
        return round(total / len(self.scores), 2)

    @property
    def total_score(self):
        return sum(s.score for s in self.scores)


class Score(db.Model):
    __tablename__ = "score"

    id = db.Column(db.Integer, primary_key=True)
    submission_id = db.Column(db.Integer, db.ForeignKey("submission.id"), nullable=False)
    criteria_id = db.Column(db.Integer, db.ForeignKey("judging_criteria.id"), nullable=False)
    judge_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    feedback = db.Column(db.Text, default="")

    judge = db.relationship("User", backref="scores_given")

    __table_args__ = (
        db.UniqueConstraint("submission_id", "criteria_id", "judge_id", name="unique_score"),
    )
