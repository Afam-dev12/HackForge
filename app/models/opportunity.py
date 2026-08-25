from app.extensions import db


class Opportunity(db.Model):
    __tablename__ = "opportunity"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    organization = db.Column(db.String(200), default="")
    location = db.Column(db.String(200), default="Online")
    url = db.Column(db.String(300), default="")
    deadline = db.Column(db.String(50), default="")
    eligibility = db.Column(db.Text, default="")
    is_active = db.Column(db.Boolean, default=True)

    created_at = db.Column(db.DateTime, server_default=db.func.now())

    bookmarks = db.relationship("OpportunityBookmark", backref="opportunity", lazy=True, cascade="all, delete-orphan")

    @property
    def bookmark_count(self):
        return len(self.bookmarks)


class OpportunityBookmark(db.Model):
    __tablename__ = "opportunity_bookmark"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    opportunity_id = db.Column(db.Integer, db.ForeignKey("opportunity.id"), nullable=False)
    saved_at = db.Column(db.DateTime, server_default=db.func.now())

    user = db.relationship("User", backref="saved_opportunities")

    __table_args__ = (
        db.UniqueConstraint("user_id", "opportunity_id", name="unique_user_opportunity"),
    )
