from base64 import b64encode

import rsa
from bson import json_util
from cryptography.hazmat.primitives.ciphers.algorithms import AES
from flask import request, jsonify, Blueprint
from werkzeug.security import generate_password_hash, check_password_hash
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad


def register_auth_blueprint(app, mongo):
    auth_bp = Blueprint('auth_bp', __name__)

    @auth_bp.route('/api/register', methods=['POST'])
    def register():
        data = request.get_json()
        username, password = data.get("username"), data.get("password")

        if not username or not password or mongo.db.users.find_one({"username": username}):
            return jsonify({"message": "Incorrect data or username already exists"}), 400

        hashed_password = generate_password_hash(password)

        (public_key, private_key) = rsa.newkeys(2048)

        # Convert the private key to a string
        private_key_str = private_key.save_pkcs1().decode()

        # Encrypt the private key
        cipher = AES.new('This is a key123'.encode(), AES.MODE_ECB)  # Use a secure key
        padded_data = pad(private_key_str.rjust(64).encode(), AES.block_size)
        encrypted_private_key = b64encode(cipher.encrypt(padded_data))

        # Store the encrypted private key in the database
        user = mongo.db.users.insert_one({
            "username": username,
            "password": hashed_password,
            "public_key": public_key.save_pkcs1().decode(),
            "private_key": encrypted_private_key.decode()  # Store as a string
        })

        return jsonify({"message": "User registered successfully"}), 201

    @auth_bp.route('/api/login', methods=['POST'])
    def login():
        data = request.get_json()
        username, password = data.get("username"), data.get("password")

        user = mongo.db.users.find_one({"username": username})
        if not user or not check_password_hash(user["password"], password):
            return jsonify({"message": "Incorrect username or password"}), 401

        return json_util.dumps(user), 200

    app.register_blueprint(auth_bp)
