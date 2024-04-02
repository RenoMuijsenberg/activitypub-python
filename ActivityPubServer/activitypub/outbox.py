import uuid
from flask import Blueprint, request, make_response


def register_outbox_blueprint(app, mongo):
    outbox_bp = Blueprint('outbox_bp', __name__)

    @outbox_bp.route('/users/<username>/outbox', methods=['GET', 'POST'])
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

    app.register_blueprint(outbox_bp)


