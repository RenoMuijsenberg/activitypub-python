import requests
from flask import Blueprint, request, make_response


def register_webfinger_blueprint(app, mongo):
    webfinger_bp = Blueprint('webfinger_bp', __name__)

    @webfinger_bp.route("/.well-known/webfinger", methods=["GET"])
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

    app.register_blueprint(webfinger_bp)
