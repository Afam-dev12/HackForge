from . import dashboard_bp

@dashboard_bp.route("/dashboard")
def dashboard():
    return "Dashboard"