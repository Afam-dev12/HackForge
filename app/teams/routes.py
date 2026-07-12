from . import team_bp

@team_bp.route("/teams")
def teams():
    return "Teams"