import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import json

# Initialize Firebase Admin SDK
cred = credentials.Certificate('./the-unifiers-firebase-adminsdk-vzs1p-06f0a83999.json')  # Replace with your actual JSON file path
firebase_admin.initialize_app(cred)
db = firestore.client()

# Read the JSON file
with open('./output/data/socfreshmen2324/socfreshmen2324_messages.json') as json_file:
    data = json.load(json_file)

# Extract and store the data in Firestore
messages = data.get('messages', [])
chats = data.get('chats', [])

channel_messages = []

for message in messages:
    message_id = message.get('id')
    channel_id = message.get('peer_id', {}).get('channel_id')
    message_text = message.get('message')

    """ channel_messages.append({
        'message_id': message_id,
        'channel_id': channel_id,
        'message_text': message_text
    }) """
    
    doc_ref = db.collection('news').document()
    
    if message_text is not None and message_text != '':
        doc_ref.set({
            'channel_id': channel_id,
            'message_id': message_id,
            'message_text': message_text
        })

""" if channel_messages:
    # Create a new document in the Firestore collection
    doc_ref = db.collection('news').document()
    doc_ref.set({
        'channel_id': channel_id,
        'messages': channel_messages
    }) """

""" for chat in chats:
    channel_id = chat.get('id')
    channel_name = chat.get('title')

    # Create a new document in the Firestore collection
    doc_ref = db.collection('news').document()
    doc_ref.set({
        'channel_id': channel_id,
        'channel_name': channel_name
    }) """