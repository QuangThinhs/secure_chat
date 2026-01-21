# services/api_client.py
import requests
import json

BASE_URL = "http://127.0.0.1:5000"

# -----------------------------
# Helper
# -----------------------------
def _request(method, endpoint, token=None, json_data=None, params=None):
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        r = requests.request(method, f"{BASE_URL}{endpoint}", headers=headers, json=json_data, params=params)
        print(f"[DEBUG] {_method_name(method)} {endpoint} -> {r.status_code}")
        try:
            data = r.json()
        except json.JSONDecodeError:
            data = {"msg": r.text}
        # Bỏ log response data để đỡ rối
        # print(f"[DEBUG] Response: {data}") 
        return r.status_code, data
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Request failed: {e}")
        return None, {"msg": str(e)}

def _method_name(method):
    return method.upper()

# -----------------------------
# Auth
# -----------------------------
def register(username, password, public_key, full_name=None, gender=None, date_of_birth=None, avatar_url=None, bio=None):
    print(f"[DEBUG] Registering user: {username}")
    payload = {
        "username": username,
        "password": password,
        "public_key": public_key,
        "full_name": full_name,
        "gender": gender,
        "date_of_birth": date_of_birth,
        "avatar_url": avatar_url,
        "bio": bio
    }
    return _request("POST", "/auth/register", json_data=payload)

def login(username, password):
    print(f"[DEBUG] Logging in user: {username}")
    payload = {"username": username, "password": password}
    status, data = _request("POST", "/auth/login", json_data=payload)
    token = data.get("token")
    user_id = data.get("user_id")
    return token, user_id, status, data

def logout(token):
    print(f"[DEBUG] Logging out")
    return _request("POST", "/auth/logout", token=token)

# -----------------------------
# Users
# -----------------------------
def get_user_info(token, user_id):
    print(f"[DEBUG] Getting user info for ID: {user_id}")
    return _request("GET", f"/users/{user_id}", token=token)

def update_profile(token, full_name=None, gender=None, date_of_birth=None, avatar_url=None, bio=None):
    print(f"[DEBUG] Updating profile")
    payload = {
        "full_name": full_name,
        "gender": gender,
        "date_of_birth": date_of_birth,
        "avatar_url": avatar_url,
        "bio": bio
    }
    payload = {k: v for k, v in payload.items() if v is not None}
    return _request("PUT", "/users/me", token=token, json_data=payload)

# -----------------------------
# Chats
# -----------------------------
def create_chat(token, name=None, is_group=False, members=None):
    members = members or []
    print(f"[DEBUG] Creating chat: name={name}, is_group={is_group}, members={members}")
    payload = {"name": name, "is_group": is_group, "members": members}
    return _request("POST", "/chats", token=token, json_data=payload)

def get_chats(token):
    print(f"[DEBUG] Getting chats")
    return _request("GET", "/chats", token=token)

def get_chat_detail(token, chat_id):
    print(f"[DEBUG] Getting chat detail for chat_id={chat_id}")
    return _request("GET", f"/chats/{chat_id}", token=token)

# <--- SỬA ĐỔI: THÊM HÀM MỚI NÀY --->
def mark_chat_read(token, chat_id):
    print(f"[DEBUG] Marking chat {chat_id} as read")
    return _request("POST", f"/chats/{chat_id}/mark_read", token=token)

def add_member(token, chat_id, member_id):
    print(f"[DEBUG] Adding member {member_id} to chat {chat_id}")
    return _request("POST", f"/chats/{chat_id}/add_member", token=token, json_data={"member_id": member_id})

def remove_member(token, chat_id, member_id):
    print(f"[DEBUG] Removing member {member_id} from chat {chat_id}")
    return _request("POST", f"/chats/{chat_id}/remove_member", token=token, json_data={"member_id": member_id})

# -----------------------------
# Messages
# -----------------------------
def send_message(token, chat_id, content, aes_key_encrypted, iv, tag):
    print(f"[DEBUG] Sending message to chat {chat_id}")
    payload = {
        "content": content,
        "aes_key_encrypted": aes_key_encrypted,
        "iv": iv,
        "tag": tag
    }
    return _request("POST", f"/chats/{chat_id}/messages", token=token, json_data=payload)

def get_messages(token, chat_id):
    print(f"[DEBUG] Getting messages for chat {chat_id}")
    return _request("GET", f"/chats/{chat_id}/messages", token=token)

# -----------------------------
# Status
# -----------------------------
def update_status(token, status):
    print(f"[DEBUG] Updating status to {status}")
    payload = {"status": status}
    return _request("POST", "/status", token=token, json_data=payload)

def get_status(token, user_id):
    print(f"[DEBUG] Getting status for user {user_id}")
    return _request("GET", f"/status/{user_id}", token=token)