from flask import Blueprint

judging_bp = Blueprint("judging", __name__)

from . import routes
