import json
import uuid

import requests
from bson import json_util
from flask import Blueprint, request, make_response, Response


def register_activitypub_blueprint(app, mongo):
    activitypub_bp = Blueprint('activitypub_bp', __name__)

    @activitypub_bp.route("/.well-known/webfinger", methods=["GET"])
    def webfinger():
        resource = request.args.get("resource")

        if not resource:
            return make_response({"error": "Resource not found"}, 404)

        domain = resource.split("@")[1]

        if domain != request.host:
            return get_non_local_webfinger(domain, resource)
        else:
            return get_local_webfinger(resource)

    def get_non_local_webfinger(domain, resource):
        search_domain = f"https://{domain}/.well-known/webfinger?resource={resource}"

        response = requests.get(search_domain)

        if response.status_code != 200:
            return make_response({"error": f"Failed to retrieve data from {search_domain}"}, response.status_code)

        return response.json()

    def get_local_webfinger(resource):
        username = resource.split(":")[1].split("@")[0]

        user = mongo.db.users.find_one({"username": username})

        if not user:
            return make_response({"error": "User not found"}, 404)

        user_name = user.get("username")
        base_url = f"{request.url_root}users/{user_name}"

        response = {
            "subject": f"acct:{user_name}@{request.host}",
            "links": [
                {
                    "rel": "self",
                    "type": "application/activity+json",
                    "href": base_url
                }
            ]
        }

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

    @activitypub_bp.route('/users/<username>/outbox', methods=['GET', 'POST'])
    def outbox(username):
        # If posted to outbox im posting to my own outbox
        if request.method == 'POST':
            data = request.json
            post_to_own_outbox(data)
        else:
            get_from_own_outbox(username)

    def post_to_own_outbox(data):
        activity_type = data.get("type")

        if activity_type is not "Create":
            create_activity(data)

    def get_from_own_outbox(username):
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
    def inbox(username):
        data = request.json

        activity_type = data.get("type")

        if activity_type is not "Create":
            create_activity(data)

        # if activity_type == "Create":
        #     print("test")
        #     activity_id = mongo.db.activities.insert_one({
        #         "type": activity_type,
        #         "actor": from_actor,
        #         "to": to_actor,
        #         "object": activity_object
        #     }).inserted_id

        return Response(status=201)

    def create_activity(data):
        attributed_to = data.get("attributedTo")  # The user that sends the message
        to = data.get("to")  # Array of users that receives the message
        object_type = data.get("type")

        new_message = {
            "@context": "https://www.w3.org/ns/activitystreams",
            "type": "Create",
            "id": f"{attributed_to}/posts/{uuid.uuid4()}",
            "to": to,
            "actor": attributed_to,
            "object": {
                "type": object_type,
                "id": f"{attributed_to}/posts/{uuid.uuid4()}",
                "attributedTo": attributed_to,
                "to": to,
                "content": data.get("content")
            }
        }

        print(new_message)

    app.register_blueprint(activitypub_bp)
