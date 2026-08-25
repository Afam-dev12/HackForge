from flask import Blueprint

opportunity_bp = Blueprint("opportunities", __name__)

from . import routes
