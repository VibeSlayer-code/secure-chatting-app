from gevent import monkey
monkey.patch_all()

from flask import Flask, jsonify
from flask_socketio import SocketIO, emit
from datetime import datetime
import base64
import secrets
import os

app = Flask(__name__)
app.config["SECRET_KEY"] = secrets.token_hex(16)
socketio = SocketIO(app, async_mode="gevent")

class MessageStore:
    def __init__(self):
        self.messages = []
        self.max_messages = 50

    def add_message(self, encrypted_message: bytes, salt: bytes, sender: str):
        if len(self.messages) >= self.max_messages:
            self.messages.pop(0)
        message_data = {
            "id": secrets.token_hex(8),
            "sender": sender,
            "encrypted_message": base64.b64encode(encrypted_message).decode(),
            "salt": base64.b64encode(salt).decode(),
            "timestamp": datetime.now().isoformat()
        }
        self.messages.append(message_data)
        socketio.emit("new_message", message_data)

    def get_messages(self):
        return self.messages

    def clear_store(self):
        self.messages = []

store = MessageStore()

@app.route("/messages")
def get_messages():
    return jsonify(store.get_messages())

@app.route("/clear")
def clear_session():
    store.clear_store()
    socketio.emit("clear", {"status": "Session cleared"})
    return jsonify({"status": "Session cleared"})

@socketio.on("connect")
def handle_connect():
    emit("new_message", {
        "sender": "System",
        "timestamp": datetime.now().isoformat(),
        "message": "Connected to secure server"
    })

@socketio.on("message")
def handle_message(data):
    encrypted_message = base64.b64decode(data["encrypted_message"])
    salt = base64.b64decode(data["salt"])
    store.add_message(encrypted_message, salt, data["sender"])

@socketio.on("disconnect")
def handle_disconnect():
    pass

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
