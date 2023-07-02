import subprocess
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

class Scraping(Resource):
    @app.route('/channels', methods=['POST'])
    def add_channel(channel_id):
        channel_name = request.form['channel_name']
        subprocess.run(['python', 'runfirestore.py', '--telegram-channel', channel_name])
        return jsonify({'message': 'Channel added successfully'})
    
    @app.route('/channels/<channel_id>', methods=['PUT'])
    def update_channel(channel_id):
        try:
            channel_name = request.form['channel_name']

            # Query Firestore to get the latest message for the channel
            messages_ref = db.collection('news').where('channel_id', '==', channel_id).order_by('message_id', direction='desc').limit(1)
            query = messages_ref.get()

            last_message_id = None

            # Check if there is a message for the channel
            if not query.empty:
                last_message = query.docs[0]
                last_message_id = last_message.get('message_id')

            # Do something with the last_message_id
            # ...

            return jsonify({'success': True, 'message': 'Channel updated successfully'})

        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})    

        # return jsonify({'message': f'Channel with ID {channel_id} updated successfully'})
    
    @app.route('/channels', methods=['GET'])
    def get_scraping(channel_id):
        return jsonify({'message': 'Scraping updated successfully'})
    
    @app.route('/channels/<channel_id>', methods=['DELETE'])
    def delete_channel(channel_id):
        # Code to delete the channel with the given channel_id
        # ...

        return jsonify({'message': f'Channel with ID {channel_id} deleted successfully'})
    
api.add_resource(Scraping, '/scraping/<string:channel_id>')

if __name__ == "__main__":
    app.run(debug=True)