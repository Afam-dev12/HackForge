from flask import Flask
from config import Config
from models import db

app = Flask(__name__)

app.config.from_object(Config)

db.init_app(app)

with app.app_context():
    db.create_all()


@app.route("/")   
def home():
    return """
    <h1>HackForge</h1>
    <p>Forge Ideas. Build the Future.
    """

if __name__ == "__main__":
    app.run(debug=True)