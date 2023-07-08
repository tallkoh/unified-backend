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
cred = credentials.Certificate('./the-unifiers-firebase-adminsdk-vzs1p-06f0a83999.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

async def run_subprocess(channel_username):
	process = await asyncio.create_subprocess_exec(
		'python', 'runfirestore.py', '--telegram-channel', channel_username,
		stdout=subprocess.PIPE, stderr=subprocess.PIPE
	)

	stdout, stderr = await process.communicate()
	
async def run_subprocess_put(channel_username, min_id):
	process = await asyncio.create_subprocess_exec(
		'python', 'runfirestore.py', '--telegram-channel', channel_username, '--min-id', min_id,
		stdout=subprocess.PIPE, stderr=subprocess.PIPE
	)

	stdout, stderr = await process.communicate()

@app.route('/channels/<channel_username>', methods=['POST'])
def add_channel(channel_username):
	# channel_name = request.form['channel_name']
	print("you got here")
	loop = asyncio.new_event_loop()
	asyncio.set_event_loop(loop)
	loop.run_until_complete(run_subprocess(channel_username))
	return jsonify({'message': 'Channel added successfully'})
	
@app.route('/channels/<channel_username>', methods=['PUT'])
def update_channel(channel_username):
	try:
		# channel_name = request.form['channel_name']
		# Query Firestore to get the latest message for the channel
		messages_ref = db.collection('news').where('channel_username', '==', channel_username).order_by('message_id', direction='desc').limit(1)
		query = messages_ref.get()

		last_message_id = None

		# Check if there is a message for the channel
		if not query.empty:
			last_message = query.docs[0]
			last_message_id = last_message.get('message_id')

		loop = asyncio.new_event_loop()
		asyncio.set_event_loop(loop)
		loop.run_until_complete(run_subprocess(channel_username, last_message_id))
		return jsonify({'success': True, 'message': 'Channel updated successfully'})

	except Exception as e:
		return jsonify({'success': False, 'error': str(e)})    

	# return jsonify({'message': f'Channel with ID {channel_id} updated successfully'})
	
@app.route('/channels', methods=['GET'])
def get_scraping(channel_username):
	return jsonify({'message': 'Scraping updated successfully'})
	
@app.route('/channels/<channel_username>', methods=['DELETE'])
def delete_channel(channel_username):
	# Code to delete the channel with the given channel_id
	# ...

	return jsonify({'message': f'Channel with ID {channel_id} deleted successfully'})
	
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))