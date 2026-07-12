from . import hackathon_bp

@hackathon_bp.route("/hackathons")
def hackathons():
    return "Hackathons"