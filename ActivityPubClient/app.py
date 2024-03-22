# While creating the ActivityPub server it occurred to me that I need to create a new application to test the flow.
# So for this application I won't do any crazy methods, just some simple HTTP-requests to check if  understand the flow.
# Let's say that this application serves as the UI of the activitypub server.
# For this application I want to go through the ActivityPub flow

# Steps this application will take:
# 1. Login to an already existing account
# 2. I want to create a new post
# 3. This post do I want to send to the inbox of another user
# 4. Go through the /.well-known/webfinger endpoint to get the users resource
# 5. Get the users profile
# 6. Get the users outbox
# 7. Send the post to the users outbox


import requests

# There are currently two users in the database, Test123 and Karin which both have the same password `Test123`
# I will log in to the Test123 account

login_data = {
    "username": "Test123",
    "password": "Test123"
}

login_response = requests.post("http://localhost:5000/api/login", json=login_data)

if login_response.status_code != 200:
    print("Failed to login")

logged_in_user = login_response.json()

print(f"Successfully logged in: {logged_in_user}")

# Now we need to get the inbox and stuff of the logged-in user, maybe I should add this data to then user table in the db.

user_response = requests.get(f"http://localhost:5000/users/{logged_in_user['username']}")

if user_response.status_code != 200:
    print("Failed to login")

user_data = user_response.json()

print(f"Successfully retrieved user data: {user_data}")


# Next steps it to discover the inbox of the other user called Karin
# I will use the /.well-known/webfinger endpoint to get the users resource

webfinger_resource = "acct:Karin@127.0.0.1:5000"
webfinger_request_url = f"http://127.0.0.1:5000/.well-known/webfinger?resource={webfinger_resource}"
webfinger_response = requests.get(webfinger_request_url)

if webfinger_response.status_code != 200:
    print("Failed to get the webfinger resource")

webfinger_data = webfinger_response.json()
print(f"Successfully retrieved webfinger data: {webfinger_data}")

# Now I want to get the users profile
karin_profile = requests.get(webfinger_data["links"][0]["href"])

if karin_profile.status_code != 200:
    print("Failed to get the profile")

karin_profile_data = karin_profile.json()
print(f"Successfully retrieved Karin's profile data: {karin_profile_data}")

karin_inbox = karin_profile_data["inbox"]

# I as user Test123 will now send a message to my own outbox
# The attributedTo should be the user that sends the message, in this case, Test123
# The to should be the user that receives the message, in this case, Karin
# The type should be the type of the message, in this case, Note
# We only will send an object, this is not an activity, just a simple message
# The server should recognise it and create a new activity from it (Create)

message = {
    "attributedTo": user_data["id"],
    "to": karin_profile_data["id"],
    "type": "Note",
    "content": "Hello Karin, this is a message from Test123"
}

send_message = requests.post(user_data["outbox"], json=message)

if send_message.status_code != 200:
    print("Failed to send the message")

print("Successfully sent the message")
