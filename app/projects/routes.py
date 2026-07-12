from . import project_bp

@project_bp.route("/projects")
def projects():
    return "Projects"