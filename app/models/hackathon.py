from app.extensions import db

class Hackathon(db.Model):
    __tablename__ = "hackathon"

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(
        db.String(200),
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=False
    )

    start_date = db.Column(db.String(50))

    end_date = db.Column(db.String(50))

    created_by = db.Column(
        db.Integer,
        db.ForeignKey("user.id")
    )