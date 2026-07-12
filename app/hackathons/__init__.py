from flask import Blueprint

hackathon_bp = Blueprint(
    "hackathons",
    __name__
)

from . import routes