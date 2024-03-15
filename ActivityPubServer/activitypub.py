from flask import Blueprint, request, make_response, Response


def register_activitypub_blueprint(app, mongo):
    activitypub_bp = Blueprint('activitypub_bp', __name__)

    def split_resource(resource):
        return resource.split(":")[1].split("@")[0]

    @activitypub_bp.route("/.well-known/webfinger", methods=["GET"])
    def webfinger():
        resource = request.args.get("resource")
        account = split_resource(resource)

        response = make_response({
            "subject": resource,
            "links": [
                {
                    "rel": "self",
                    "type": "application/activity+json",
                    "href": f"http://127.0.0.1:5000/users/{account}"
                }
            ]
        })

        response.headers['Content-Type'] = 'application/jrd+json'

        return response

    @activitypub_bp.route("/users/<username>", methods=["GET"])
    def actor(username):
        # Instead of returning a static actor object, we can query the database for the user's details

        public_key = "-----BEGIN PUBLIC KEY-----MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAp01dR3Ubnt8pCzEh0hkxMnuTo6/OB6Wlhu5RheZSPL3+aW6XL4seNCRIJQiS7HegO5VQxg9d3v69WK1Lb+nPABo8MjWJzExYtlqAyRhhzlUMyf+DIjWmcbyFOMdpVHcY1Vi44niJWqCLwDp1FyBiQAMVaGSQH6DccNEaKS7XZoPs6cEUX1ZzeIHxeltZLur7L5ASKkyQm0d91C22rJaNJ/z4Uk1YmW3MhBPjwtYHy0PaJvmw9LTcYWa/SXRrO5yft6S1MVObuljWzvYA0YztDmnrkoKoYHX68m9+qIbAGxgT2Uy2cgrUEXKdCSA5axUgTjvcOEsV/OOQnKcbGwZAPwIDAQAB-----END PUBLIC KEY-----"

        response = make_response({
            "@context": "https://www.w3.org/ns/activitystreams",
            "type": "Person",
            "id": f"http://127.0.0.1:5000/users/{username}",
            "name": f"{username}",
            "preferredUsername": f"{username}",
            "summary": "A test account for testing tests",
            "inbox": f"http://127.0.0.1:5000/users/{username}/inbox",
            "outbox": f"http://127.0.0.1:5000/users/{username}/outbox",
            "publicKey": {
                "id": f"http://127.0.0.1:5000/users/{username}#main-key",
                "owner": f"http://127.0.0.1:5000/users/{username}",
                "publicKeyPem": public_key
            }
        })

        response.headers['Content-Type'] = 'application/activity+json'

        return response

    @activitypub_bp.route('/users/<username>/outbox', methods=['GET'])
    def user_inbox(username):
        return make_response()

    @activitypub_bp.route('/users/<username>/inbox', methods=['POST'])
    def outbox(username):
        data = request.json

        existing_data = [data]

        # Save data into the database

        return Response(status=201)

    app.register_blueprint(activitypub_bp)
