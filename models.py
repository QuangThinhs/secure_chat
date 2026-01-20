# models.py
from app import db
from datetime import datetime

# ======================================================
# Account model (tương đương User)
# ======================================================
class Account(db.Model):
    __tablename__ = "accounts"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    public_key = db.Column(db.Text, nullable=False)
    status = db.Column(db.Enum('online', 'offline'), default='offline')
    last_seen = db.Column(db.DateTime, default=None)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    sent_messages = db.relationship("Message", back_populates="sender", cascade="all, delete-orphan")
    chat_memberships = db.relationship("ChatMember", back_populates="account", cascade="all, delete-orphan")
    received_messages = db.relationship("MessageRecipient", back_populates="receiver", cascade="all, delete-orphan")
    profile = db.relationship("UserProfile", back_populates="account", uselist=False, cascade="all, delete-orphan")


# ======================================================
# UserProfile model (thông tin cá nhân)
# ======================================================
class UserProfile(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    account_id = db.Column(db.Integer, db.ForeignKey("accounts.id", ondelete="CASCADE"), unique=True, nullable=False)
    full_name = db.Column(db.String(100), default=None)
    gender = db.Column(db.Enum('male','female','other'), default='other')
    date_of_birth = db.Column(db.Date, default=None)
    avatar_url = db.Column(db.String(255), default=None)
    bio = db.Column(db.Text, default=None)

    account = db.relationship("Account", back_populates="profile")


# ======================================================
# Chat model
# ======================================================
class Chat(db.Model):
    __tablename__ = "chats"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), default=None)
    is_group = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    members = db.relationship("ChatMember", back_populates="chat", cascade="all, delete-orphan")
    messages = db.relationship("Message", back_populates="chat", cascade="all, delete-orphan")


# ======================================================
# ChatMember model
# ======================================================
class ChatMember(db.Model):
    __tablename__ = "chat_members"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    chat_id = db.Column(db.Integer, db.ForeignKey("chats.id", ondelete="CASCADE"), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)

    chat = db.relationship("Chat", back_populates="members")
    account = db.relationship("Account", back_populates="chat_memberships")

    __table_args__ = (db.UniqueConstraint("chat_id", "account_id", name="chat_id_account_id_unique"),)


# ======================================================
# Message model
# ======================================================
class Message(db.Model):
    __tablename__ = "messages"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    chat_id = db.Column(db.Integer, db.ForeignKey("chats.id", ondelete="CASCADE"), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False)
    content = db.Column(db.Text, nullable=False)
    aes_key_encrypted = db.Column(db.Text, nullable=False)
    iv = db.Column(db.Text, default=None)
    tag = db.Column(db.Text, default=None)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    chat = db.relationship("Chat", back_populates="messages")
    sender = db.relationship("Account", back_populates="sent_messages")
    recipients = db.relationship("MessageRecipient", back_populates="message", cascade="all, delete-orphan")


# ======================================================
# MessageRecipient model
# ======================================================
class MessageRecipient(db.Model):
    __tablename__ = "message_recipients"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    message_id = db.Column(db.Integer, db.ForeignKey("messages.id", ondelete="CASCADE"), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False)

    # <--- SỬA ĐỔI: Thêm trường này
    read_at = db.Column(db.DateTime, nullable=True, default=None)

    message = db.relationship("Message", back_populates="recipients")
    receiver = db.relationship("Account", back_populates="received_messages")

    __table_args__ = (db.UniqueConstraint("message_id", "receiver_id", name="message_id_receiver_id_unique"),)