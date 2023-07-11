import subprocess
import asyncio
import os
from aiohttp import web
from flask import Flask, request, jsonify
from flask_restful import Resource, Api

# import firebase submodules
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

app = Flask(__name__)
api = Api(app)

# Initialize Firebase Admin SDK
cred = credentials.Certificate('./unified-acf08-firebase-adminsdk-xytc6-0f7c8f724e.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

async def run_subprocess(channel_username):
    process = await asyncio.create_subprocess_exec(
        'python', 'runfirestore.py', '--telegram-channel', channel_username,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )

    stdout, stderr = await process.communicate()
    
async def run_subprocess_put(channel_username, min_id):
    print("this is running")
    try:
        process = await asyncio.create_subprocess_exec(
            'python', 'runfirestore.py', '--telegram-channel', channel_username, '--min-id', min_id,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
    except Exception as e:
        print(e)

    stdout, stderr = await process.communicate()

@app.route('/channels/<channel_username>', methods=['POST'])
def add_channel(channel_username):
    print("you got here")
    channels_collection = db.collection('channels')
    query = channels_collection.where('channel_username', '==', channel_username).get()
    if len(query) > 0:
        return jsonify({'message':'Channel already exists'}), 400
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_subprocess(channel_username))
    return jsonify({'message':'Channel added successfully'}), 200
    
@app.route('/channels/<channel_username>', methods=['PUT'])
def update_channel(channel_username):
    try:
        messages_ref = db.collection('news').where('channel_username', '==', channel_username).order_by('message_id', direction=firestore.Query.DESCENDING).limit(1)
        query = messages_ref.get()
        last_message_id = None

        for q in query:
            print(f"{q.id} => {q.to_dict()}")
        # Check if there is a message for the channel
        if len(query) > 0:
            last_message = query[0]
            last_message_id = str(last_message.get('message_id'))

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(run_subprocess_put(channel_username, last_message_id))
        return jsonify({'success': True, 'message': 'Channel updated successfully'}), 202

    except Exception as e:
        print(e)
        return jsonify({'success': False, 'error': str(e)}), 400    
    
@app.route('/channels', methods=['GET'])
def get_scraping(channel_username):
    return jsonify({'message': 'Scraping updated successfully'})
    
@app.route('/channels/<channel_username>', methods=['DELETE'])
def delete_channel(channel_username):
    return jsonify({'message': f'Channel with ID {channel_id} deleted successfully'})
    
if __name__ == "__main__":
    app.run()