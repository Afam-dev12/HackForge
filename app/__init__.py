from flask import Flask

from config import Config

from app.extensions import (
    db,
    login_manager,
    migrate
)

import app.login

#blue print 
from app.auth import auth_bp
from app.dashboard import dashboard_bp
from app.hackathons import hackathon_bp
from app.projects import project_bp
from app.teams import team_bp

def create_app():

    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    login_manager.login_view = "auth.login"

    #register bluprints 
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(hackathon_bp)
    app.register_blueprint(project_bp)
    app.register_blueprint(team_bp)
    
    return app