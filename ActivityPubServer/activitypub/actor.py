from flask import Blueprint, request


def register_actor_blueprint(app, mongo):
    actor_bp = Blueprint('actor_bp', __name__)

    @actor_bp.route("/users/<username>", methods=["GET"])
    def actor(username):
        user = mongo.db.users.find_one({"username": username})

        if not user:
            return {"error": "User not found"}, 404

        user_name = user.get("username")
        public_key = user.get("public_key")
        base_url = f"{request.url_root}users/{user_name}"

        response = {
            "@context": "https://www.w3.org/ns/activitystreams",
            "type": "Person",
            "id": base_url,
            "name": user_name,
            "preferredUsername": user_name,
            "summary": "A test account for testing tests",
            "inbox": f"{base_url}/inbox",
            "outbox": f"{base_url}/outbox",
            "publicKey": {
                "id": f"{base_url}#main-key",
                "owner": base_url,
                "publicKeyPem": public_key
            }
        }

        return response, 200, {'Content-Type': 'application/activity+json'}

    app.register_blueprint(actor_bp)


