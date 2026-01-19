# routes/chats_bp.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models import Chat, ChatMember, Account, UserProfile, MessageRecipient, Message
from sqlalchemy import and_, func
from datetime import datetime

chats_bp = Blueprint("chats", __name__)

def _serialize_chat_for_user(chat, user_id):
    """
    Helper: Trả về tên chat và thông tin đã được tùy chỉnh
    cho người dùng (user_id) đang xem.
    """
    members_ids = [m.account_id for m in chat.members]
    chat_name = chat.name
    
    if not chat.is_group:
        # Tìm người còn lại trong chat 1-1
        other_member_id = next((mid for mid in members_ids if mid != user_id), None)
        
        if other_member_id:
            other_user = Account.query.get(other_member_id)
            if other_user and other_user.profile:
                # SỬA: Sử dụng full_name làm tên chat
                chat_name = other_user.profile.full_name or other_user.username
            elif other_user:
                chat_name = other_user.username
        else:
            chat_name = "My Notes"

    # SỬA: Logic đếm tin chưa đọc
    unread_count = db.session.query(func.count(MessageRecipient.id)).join(Message).filter(
        Message.chat_id == chat.id,
        MessageRecipient.receiver_id == user_id,
        MessageRecipient.read_at == None,
        Message.sender_id != user_id # Chỉ đếm tin của người khác
    ).scalar()

    return {
        "chat_id": chat.id,
        "name": chat_name,
        "is_group": chat.is_group,
        "members": members_ids,
        "created_at": chat.created_at.isoformat(),
        "unread_count": unread_count # Trả về count
    }


@chats_bp.route("", methods=["POST"])
@jwt_required()
def create_chat():
    data = request.get_json()
    name = data.get("name")
    is_group = data.get("is_group", False)
    members_ids = data.get("members", []) 
    creator_id = int(get_jwt_identity())

    if not is_group:
        # ======================================================
        # SỬA: LOGIC GỘP CHAT (TÌM HOẶC TẠO)
        # ======================================================
        if len(members_ids) != 1:
            return jsonify({"msg": "Chat 1-1 yêu cầu chính xác 1 member"}), 400
        
        other_member_id = members_ids[0]
        if other_member_id == creator_id:
             return jsonify({"msg": "Không thể tự tạo chat với chính mình theo cách này"}), 400

        # Tìm các chat 1-1 hiện có giữa 2 người
        creator_chats_subq = db.session.query(ChatMember.chat_id).filter(
            ChatMember.account_id == creator_id
        ).subquery()
        
        existing_chat = db.session.query(Chat).join(ChatMember).filter(
            ChatMember.chat_id.in_(creator_chats_subq),
            ChatMember.account_id == other_member_id,
            Chat.is_group == False
        ).first()
        
        if existing_chat:
            # Đã tìm thấy! Trả về chat cũ (HTTP 200)
            return jsonify(_serialize_chat_for_user(existing_chat, creator_id)), 200
        
        # Không tìm thấy, tạo chat mới
        other_user = Account.query.get(other_member_id)
        if not other_user:
            return jsonify({"msg": f"User {other_member_id} không tồn tại"}), 404
        
        name = other_user.profile.full_name or other_user.username
        
    # Tạo chat (cho group hoặc 1-1 mới)
    chat = Chat(name=name, is_group=is_group)
    db.session.add(chat)
    db.session.commit() # Commit để lấy chat.id

    # Thêm người tạo
    db.session.add(ChatMember(chat_id=chat.id, account_id=creator_id))
    # Thêm các thành viên khác
    for m_id in members_ids:
        if m_id != creator_id and Account.query.get(m_id):
            db.session.add(ChatMember(chat_id=chat.id, account_id=m_id))
    
    db.session.commit()

    # Trả về chat mới (HTTP 201)
    return jsonify(_serialize_chat_for_user(chat, creator_id)), 201


@chats_bp.route("", methods=["GET"])
@jwt_required()
def get_chats():
    user_id = int(get_jwt_identity())
    memberships = ChatMember.query.filter_by(account_id=user_id).all()
    
    chats_data = []
    for m in memberships:
        chat = m.chat
        # SỬA: Sử dụng helper để lấy tên chính xác và unread_count
        chats_data.append(_serialize_chat_for_user(chat, user_id))
        
    return jsonify(chats_data)


@chats_bp.route("/<int:chat_id>", methods=["GET"])
@jwt_required()
def get_chat_detail(chat_id):
    user_id = int(get_jwt_identity())
    chat = Chat.query.get(chat_id)
    if not chat:
        return jsonify({"msg": "Chat not found"}), 404

    membership = ChatMember.query.filter_by(chat_id=chat_id, account_id=user_id).first()
    if not membership:
        return jsonify({"msg": "You are not a member of this chat"}), 403

    # SỬA: Sử dụng helper để trả về dữ liệu
    return jsonify(_serialize_chat_for_user(chat, user_id)), 200


# <--- SỬA ĐỔI: THÊM ROUTE MỚI NÀY --->
@chats_bp.route("/<int:chat_id>/mark_read", methods=["POST"])
@jwt_required()
def mark_chat_as_read(chat_id):
    user_id = int(get_jwt_identity())

    # Tìm tất cả MessageRecipient chưa đọc của user này trong chat này
    unread_messages = db.session.query(MessageRecipient).join(Message).filter(
        Message.chat_id == chat_id,
        MessageRecipient.receiver_id == user_id,
        MessageRecipient.read_at == None
    ).all()

    count = 0
    for msg_recipient in unread_messages:
        # Chỉ đánh dấu đã đọc tin nhắn của người khác
        if msg_recipient.message.sender_id != user_id:
            msg_recipient.read_at = datetime.utcnow()
            count += 1

    db.session.commit()
    return jsonify({"msg": f"Marked {count} messages as read"}), 200