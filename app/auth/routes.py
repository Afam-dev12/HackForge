from flask import render_template

from . import auth_bp

@auth_bp.route("/")
def home():
    return render_template("index.html")

@auth_bp.route("/login")
def login():
    return "Login Page"

@auth_bp.route("/register")
def register():
    return "Register Page"