from flask import request, jsonify, Blueprint


def register_auth_blueprint(app, mongo):
    auth_bp = Blueprint('auth_bp', __name__)

    @auth_bp.route("/register", methods=["POST"])
    def register():
        username = request.json.get("username")

        existing_user = mongo.db.users.find_one({"username": username})

        if existing_user:
            return jsonify({"error": "Username already exists"}), 400
        else:
            mongo.db.users.insert_one({"username": username})
            return jsonify({"message": "User registered successfully"}), 201

    app.register_blueprint(auth_bp)
