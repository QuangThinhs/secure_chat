from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models import Account
from datetime import datetime

status_bp = Blueprint("status", __name__)

@status_bp.route("/status", methods=["POST"])
@jwt_required()
def update_status():
    data = request.get_json()
    status = data.get("status")
    if status not in ["online", "offline"]:
        return jsonify({"msg": "Invalid status"}), 400

    user_id = int(get_jwt_identity())
    user = Account.query.get(user_id)
    user.status = status
    user.last_seen = datetime.utcnow() if status == "offline" else user.last_seen
    db.session.commit()
    return jsonify({"msg": "Status updated"}), 200

@status_bp.route("/status/<int:user_id>", methods=["GET"])
@jwt_required()
def get_status(user_id):
    user = Account.query.get(user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404
    return jsonify({
        "status": user.status,
        "last_seen": user.last_seen.isoformat() if user.last_seen else None
    })
