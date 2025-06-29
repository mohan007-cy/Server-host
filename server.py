from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit, join_room
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# In-memory "DB"
users = {}         # {username: password}
sessions = {}      # {username: sid}
chat_history = {}  # {room: [msg1, msg2, ...]}

# ✅ Register
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    if username in users:
        return jsonify({"status": "fail", "msg": "User exists"}), 400
    users[username] = password
    return jsonify({"status": "success"})

# ✅ Login
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    if users.get(username) == password:
        return jsonify({"status": "success"})
    return jsonify({"status": "fail"}), 401

# ✅ WebSocket Events
@socketio.on("join")
def handle_join(data):
    username = data["username"]
    room = data["room"]
    join_room(room)
    sessions[username] = request.sid
    emit("status", f"{username} joined {room}", room=room)

@socketio.on("message")
def handle_message(data):
    username = data["username"]
    room = data["room"]
    msg = data["msg"]
    full_msg = f"{username}: {msg}"
    
    # Save message
    chat_history.setdefault(room, []).append(full_msg)
    
    # Broadcast
    emit("message", full_msg, room=room)

# Optional: get history (REST)
@app.route('/history/<room>')
def get_history(room):
    return jsonify(chat_history.get(room, []))

# ✅ Start Server
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)