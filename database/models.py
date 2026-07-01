from datetime import datetime
from database.db import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    email = db.Column(db.String(120), unique=True, nullable=False)

    password_hash = db.Column(db.String(255), nullable=False)

    phone = db.Column(db.String(20))

    gender = db.Column(db.String(20))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)