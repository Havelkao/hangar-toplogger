from ..extensions import db
from flask import Blueprint


auth = Blueprint("auth", __name__)


@auth.post("/register")
def register():
    db.auth.sign_up()


@auth.get("/login")
def login():
    db.auth.sign_in_with_otp({"test": "mango@mango.cz"})
