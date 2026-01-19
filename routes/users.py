from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models import Account, UserProfile
from datetime import datetime

users_bp = Blueprint("users", __name__)

@users_bp.route("/<int:user_id>", methods=["GET"])
@jwt_required()
def get_user(user_id):
    user = Account.query.get(user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404
    profile = user.profile
    return jsonify({
        "user_id": user.id,
        "username": user.username,
        "full_name": profile.full_name if profile else None,
        "gender": profile.gender if profile else "other",
        "date_of_birth": profile.date_of_birth.isoformat() if profile and profile.date_of_birth else None,
        "avatar_url": profile.avatar_url if profile else None,
        "bio": profile.bio if profile else None,
        "status": user.status,
        "last_seen": user.last_seen.isoformat() if user.last_seen else None,
        "public_key": user.public_key
    })

@users_bp.route("/me", methods=["PUT"])
@jwt_required()
def update_profile():
    user_id = int(get_jwt_identity())
    user = Account.query.get(user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404

    data = request.get_json()
    profile = user.profile
    if not profile:
        profile = UserProfile(account_id=user.id)
        db.session.add(profile)

    profile.full_name = data.get("full_name", profile.full_name)
    profile.gender = data.get("gender", profile.gender)
    dob = data.get("date_of_birth")
    if dob:
        profile.date_of_birth = datetime.   strptime(dob, "%Y-%m-%d").date()
    profile.avatar_url = data.get("avatar_url", profile.avatar_url)
    profile.bio = data.get("bio", profile.bio)

    db.session.commit()
    return jsonify({"msg": "Profile updated"}), 200
