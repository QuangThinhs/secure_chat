from flask import Flask, request
from flask_socketio import SocketIO, emit, join_room
from flask_jwt_extended import decode_token
from app import create_app, db
from models import Chat, ChatMember, Message, MessageRecipient
import json
import logging

flask_app = create_app()
socketio = SocketIO(flask_app, cors_allowed_origins="*", async_mode="threading")
connected_users = {}

def get_user_id_from_token(token):
    try:
        return int(decode_token(token)["sub"])
    except: return None

def broadcast_online_users():
    users = list(connected_users.keys())
    socketio.emit("online_users", users)

@socketio.on("connect")
def handle_connect(auth):
    token = auth.get("token") if auth else request.args.get("token")
    if not token: return False
    user_id = get_user_id_from_token(token)
    if not user_id: return False
    connected_users[user_id] = request.sid
    broadcast_online_users()
    return True

@socketio.on("disconnect")
def handle_disconnect():
    sid = request.sid
    removed = [uid for uid, u_sid in list(connected_users.items()) if u_sid == sid]
    for uid in removed: connected_users.pop(uid, None)
    broadcast_online_users()

@socketio.on("join_chat")
def handle_join_chat(data):
    chat_id = data.get("chat_id")
    user_id = data.get("user_id")
    if chat_id and user_id:
        join_room(f"chat_{chat_id}")

@socketio.on("send_message")
def handle_send_message(data):
    chat_id = data.get("chat_id")
    sender_id = data.get("sender_id")
    content = data.get("content")
    aes_key_encrypted = data.get("aes_key_encrypted")
    iv = data.get("iv")
    tag = data.get("tag")

    if not all([chat_id, sender_id, content, iv, tag]) or not isinstance(aes_key_encrypted, dict):
        emit("error", {"msg": "Invalid data"})
        return

    # LƯU DB: dict → JSON string
    message = Message(
        chat_id=chat_id,
        sender_id=sender_id,
        content=content,
        aes_key_encrypted=json.dumps(aes_key_encrypted),
        iv=iv,
        tag=tag
    )
    db.session.add(message)
    db.session.flush()

    for m in ChatMember.query.filter_by(chat_id=chat_id).all():
        db.session.add(MessageRecipient(message_id=message.id, receiver_id=m.account_id))
    db.session.commit()

    # EMIT: dict nguyên bản
    event = {
        "id": message.id,
        "chat_id": chat_id,
        "sender_id": sender_id,
        "content": content,
        "aes_key_encrypted": aes_key_encrypted,
        "iv": iv,
        "tag": tag,
        "timestamp": message.timestamp.isoformat()
    }
    emit("receive_message", event, room=f"chat_{chat_id}", include_self=True)

@flask_app.route("/_connected_users")
def list_connected():
    return {"connected_users": list(connected_users.keys())}

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    socketio.run(flask_app, host="0.0.0.0", port=5001, debug=True)