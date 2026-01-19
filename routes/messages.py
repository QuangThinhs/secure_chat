from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models import Message, MessageRecipient, ChatMember

messages_bp = Blueprint("messages", __name__)

@messages_bp.route("/chats/<int:chat_id>/messages", methods=["POST"])
@jwt_required()
def send_message(chat_id):
    data = request.get_json()
    required = ["content", "aes_key_encrypted", "iv", "tag"]
    for f in required:
        if f not in data:
            return jsonify({"msg": f"Missing {f}"}), 400

    sender_id = int(get_jwt_identity())
    chat_members = ChatMember.query.filter_by(chat_id=chat_id).all()
    if sender_id not in [m.account_id for m in chat_members]:
        return jsonify({"msg": "Not in chat"}), 403

    message = Message(
        chat_id=chat_id,
        sender_id=sender_id,
        content=data["content"],
        aes_key_encrypted=data["aes_key_encrypted"],
        iv=data["iv"],
        tag=data["tag"]
    )
    db.session.add(message)
    db.session.commit()

    # tạo recipients cho tất cả thành viên
    for m in chat_members:
        db.session.add(MessageRecipient(message_id=message.id, receiver_id=m.account_id))
    db.session.commit()

    return jsonify({"msg": "Sent", "message_id": message.id}), 201

@messages_bp.route("/chats/<int:chat_id>/messages", methods=["GET"])
@jwt_required()
def get_messages(chat_id):
    messages = Message.query.filter_by(chat_id=chat_id).order_by(Message.timestamp.asc()).all()
    result = []
    for m in messages:
        result.append({
            "id": m.id,
            "sender_id": m.sender_id,
            "content": m.content,
            "aes_key_encrypted": m.aes_key_encrypted,
            "iv": m.iv,
            "tag": m.tag,
            "timestamp": m.timestamp.isoformat(),
            "recipients": [r.receiver_id for r in m.recipients]
        })
    return jsonify(result)
