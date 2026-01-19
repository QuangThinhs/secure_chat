from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app import db
from models import Account, UserProfile
from datetime import datetime

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()
    public_key = data.get("public_key", "").strip()
    full_name = data.get("full_name")
    gender = data.get("gender", "other")
    date_of_birth = data.get("date_of_birth")
    avatar_url = data.get("avatar_url")
    bio = data.get("bio")

    if not username or not password or not public_key:
        return jsonify({"msg": "Username, password and public_key are required"}), 400

    if Account.query.filter_by(username=username).first():
        return jsonify({"msg": "Username already exists"}), 400

    hashed_pw = generate_password_hash(password)
    account = Account(
        username=username,
        password_hash=hashed_pw,
        public_key=public_key,
        status="offline"
    )
    db.session.add(account)
    db.session.commit()

    profile = UserProfile(
        account_id=account.id,
        full_name=full_name,
        gender=gender if gender in ["male","female","other"] else "other",
        date_of_birth=datetime.strptime(date_of_birth, "%Y-%m-%d").date() if date_of_birth else None,
        avatar_url=avatar_url,
        bio=bio
    )
    db.session.add(profile)
    db.session.commit()

    return jsonify({"msg": "User created", "user_id": account.id}), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    account = Account.query.filter_by(username=username).first()
    if not account or not check_password_hash(account.password_hash, password):
        return jsonify({"msg": "Invalid credentials"}), 401

    account.status = "online"
    account.last_seen = datetime.utcnow()
    db.session.commit()

    token = create_access_token(identity=str(account.id))
    return jsonify({"token": token, "user_id": account.id})

@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    account_id = get_jwt_identity()
    account = Account.query.get(account_id)
    if account:
        account.status = "offline"
        account.last_seen = datetime.utcnow()
        db.session.commit()
    return jsonify({"msg": "Logged out"}), 200
