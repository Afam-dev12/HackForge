from flask import Flask, render_template

from config import Config

from app.extensions import db, login_manager, migrate, csrf

import app.login

from app.auth import auth_bp
from app.dashboard import dashboard_bp
from app.hackathons import hackathon_bp
from app.projects import project_bp
from app.teams import team_bp
from app.opportunities import opportunity_bp
from app.judging import judging_bp
from app.pages import pages_bp


def create_app(config_class=None):
    app = Flask(__name__)

    if config_class:
        app.config.from_object(config_class)
    else:
        app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    login_manager.login_view = "auth.login"

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(hackathon_bp)
    app.register_blueprint(project_bp)
    app.register_blueprint(team_bp)
    app.register_blueprint(opportunity_bp)
    app.register_blueprint(judging_bp)
    app.register_blueprint(pages_bp)

    @app.errorhandler(404)
    def not_found(e):
        return render_template("404.html"), 404

    @app.errorhandler(403)
    def forbidden(e):
        return render_template("403.html"), 403

    @app.errorhandler(500)
    def server_error(e):
        return render_template("500.html"), 500

    with app.app_context():
        db.create_all()

    return app
