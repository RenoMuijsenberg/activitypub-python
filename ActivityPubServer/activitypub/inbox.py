from flask import Blueprint, request, Response


def register_inbox_blueprint(app, mongo):
    inbox_bp = Blueprint('inbox_bp', __name__)

    @inbox_bp.route('/users/<username>/inbox', methods=['POST'])
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

    app.register_blueprint(inbox_bp)


