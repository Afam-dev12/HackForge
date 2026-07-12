from flask import Blueprint

team_bp = Blueprint(
    "teams",
    __name__
)

from . import routes