from flask import Blueprint

project_bp = Blueprint(
    "projects",
    __name__
)

from . import routes