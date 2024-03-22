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
        if request.method == 'GET':
            return get_activities(username)
        elif request.method == 'POST':
            return post_activity(request)

    def get_activities(username):
        try:
            messages = list(mongo.db.activities.find({"actor": f"{request.url_root}users/{username}"}, {'_id': False}))

            user_outbox = {
                "@context": "https://www.w3.org/ns/activitystreams",
                "id": f"{request.base_url}",
                "type": "OrderedCollection",
                "totalItems": len(messages),
                "orderedItems": messages
            }

            response = make_response(user_outbox, 200)
            response.headers['Content-Type'] = 'application/activity+json'
            return response
        except Exception as e:
            print(f"Error retrieving activities for user {username}: {e}")
            return make_response({"error": "Internal server error"}, 500)

    def post_activity(post_request):
        if post_request.headers.get("Content-Type") != "application/ld+json; profile='https://www.w3.org/ns/activitystreams'":
            return make_response({"error": "Invalid content type"}, 400)

        try:
            data = post_request.json
            if data is None or not isinstance(data, dict):
                return make_response({"error": "Invalid request body"}, 400)

            bto = data.get("bto")
            if bto is not None:
                del data["bto"]

            bcc = data.get("bcc")
            if bcc is not None:
                del data["bcc"]

            if data.get("object") is None:
                data = {
                    "@context": "https://www.w3.org/ns/activitystreams",
                    "type": "Create",
                    "actor": data.get("attributedTo"),
                    "object": data
                }

            data["id"] = f"{data.get('actor')}/posts/{uuid.uuid4()}"
            data["object"]["id"] = f"{data.get('actor')}/posts/{uuid.uuid4()}"

            mongo.db.activities.insert_one(data)
            return make_response("Ok", 201)
        except Exception as e:
            print(f"Error creating activity: {e}")
            return make_response({"error": "Internal server error"}, 500)

    @activitypub_bp.route('/users/<username>/inbox', methods=['POST'])
    def inbox(username):
        data = request.json

        activity_type = data.get("type")

        # if activity_type == "Create":
        #     print("test")
        #     activity_id = mongo.db.activities.insert_one({
        #         "type": activity_type,
        #         "actor": from_actor,
        #         "to": to_actor,
        #         "object": activity_object
        #     }).inserted_id

        return Response(status=201)

    app.register_blueprint(activitypub_bp)
