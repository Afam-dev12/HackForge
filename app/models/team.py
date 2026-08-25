from app.extensions import db


class Team(db.Model):
    __tablename__ = "team"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, default="")
    hackathon_id = db.Column(db.Integer, db.ForeignKey("hackathon.id"), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    members = db.relationship("TeamMember", backref="team", lazy=True, cascade="all, delete-orphan")
    submission = db.relationship("Submission", backref="team", uselist=False, lazy=True)
    creator = db.relationship("User", foreign_keys=[created_by], backref="teams_created")

    @property
    def member_count(self):
        return len(self.members)

    def is_member(self, user_id):
        return any(m.user_id == user_id for m in self.members)

    def is_leader(self, user_id):
        return any(m.user_id == user_id and m.role == "leader" for m in self.members)


class TeamMember(db.Model):
    __tablename__ = "team_member"

    id = db.Column(db.Integer, primary_key=True)
    team_id = db.Column(db.Integer, db.ForeignKey("team.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    role = db.Column(db.String(20), default="member")
    joined_at = db.Column(db.DateTime, server_default=db.func.now())

    __table_args__ = (
        db.UniqueConstraint("team_id", "user_id", name="unique_team_user"),
    )
