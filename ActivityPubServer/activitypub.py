from flask import Blueprint, request, make_response, Response


def register_activitypub_blueprint(app, mongo):
    activitypub_bp = Blueprint('activitypub_bp', __name__)

    def split_resource(resource):
        return resource.split(":")[1].split("@")[0]

    @activitypub_bp.route("/.well-known/webfinger", methods=["GET"])
    def webfinger():
        resource = request.args.get("resource")
        account = split_resource(resource)

        user = mongo.db.users.find_one({"username": account})

        if not user:
            return make_response({
                "error": "Resource not found"
            }, 404)

        response = make_response({
            "subject": resource,
            "links": [
                {
                    "rel": "self",
                    "type": "application/activity+json",
                    "href": f"http://127.0.0.1:5000/users/{account}"
                }
            ]
        }, 200)

        response.headers['Content-Type'] = 'application/jrd+json'

        return response

    @activitypub_bp.route("/users/<username>", methods=["GET"])
    def actor(username):
        user = mongo.db.users.find_one({"username": username})

        if user is None:
            return make_response({
                "error": "User not found"
            }, 404)

        user_name = user.get("username")
        public_key = user.get("public_key")

        response = make_response({
            "@context": "https://www.w3.org/ns/activitystreams",
            "type": "Person",
            "id": f"http://127.0.0.1:5000/users/{user_name}",
            "name": f"{user_name}",
            "preferredUsername": f"{user_name}",
            "summary": "A test account for testing tests",
            "inbox": f"http://127.0.0.1:5000/users/{user_name}/inbox",
            "outbox": f"http://127.0.0.1:5000/users/{user_name}/outbox",
            "publicKey": {
                "id": f"http://127.0.0.1:5000/users/{user_name}#main-key",
                "owner": f"http://127.0.0.1:5000/users/{user_name}",
                "publicKeyPem": public_key
            }
        })

        response.headers['Content-Type'] = 'application/activity+json'

        return response

    @activitypub_bp.route('/users/<username>/outbox', methods=['GET'])
    def inbox(username):
        return mongo.db.activities.find({"to": "username"})

    @activitypub_bp.route('/users/<username>/inbox', methods=['POST'])
    def outbox(username):
        data = request.json
        activity_type = data.get("type")
        from_actor = data.get("actor")
        to_actor = data.get("to")
        activity_object = data.get("object")

        print(data)
        print(activity_type)

        if activity_type == "Create":
            print("test")
            activity_id = mongo.db.activities.insert_one({
                "type": activity_type,
                "actor": from_actor,
                "to": to_actor,
                "object": activity_object
            }).inserted_id

        return Response(status=201)

    app.register_blueprint(activitypub_bp)
