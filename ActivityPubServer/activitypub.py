import json
from bson import json_util
from flask import Blueprint, request, make_response, Response


def register_activitypub_blueprint(app, mongo):
    activitypub_bp = Blueprint('activitypub_bp', __name__)

    def split_resource(resource):
        return resource.split(":")[1].split("@")[0]

    @activitypub_bp.route("/.well-known/webfinger", methods=["GET"])
    def webfinger():
        resource = request.args.get("resource")

        if not resource:
            return make_response({
                "error": "Resource not found"
            }, 404)

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

        response.headers['Content-Type'] = 'application/activity+json'

        return response

    @activitypub_bp.route("/users/<username>", methods=["GET"])
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

    @activitypub_bp.route('/users/<username>/outbox', methods=['GET'])
    def inbox(username):

        activities = mongo.db.activities.find({
            "to": {
                "$in": [
                    f"http://localhost:5000/users/{username}/"
                ]
            }
        })

        activities = json.loads(json_util.dumps(activities))

        response = make_response(activities, 200)

        response.headers['Content-Type'] = 'application/activity+json'

        return response

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
