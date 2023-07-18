import asyncio
import subprocess
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase Admin SDK
cred = credentials.Certificate('./unified-acf08-firebase-adminsdk-xytc6-0f7c8f724e.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

async def run_subprocess_put(channel_username, min_id):
    try:
        process = await asyncio.create_subprocess_exec(
            'python', 'runfirestore.py', '--telegram-channel', channel_username, '--min-id', min_id,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
    except Exception as e:
        print(e)

    stdout, stderr = await process.communicate()

# Function to update a channel
async def update_channel(channel_username):
    try:
        messages_ref = db.collection('news').where('channel_username', '==', channel_username).order_by('message_id', direction=firestore.Query.DESCENDING).limit(1)
        query = messages_ref.get()
        last_message_id = None

        # Check if there is a message for the channel
        if len(query) > 0:
            last_message = query[0]
            last_message_id = str(last_message.get('message_id'))

        await run_subprocess_put(channel_username, last_message_id)
        print(f"Channel '{channel_username}' updated successfully")
    
    except Exception as e:
        print(f"Failed to update channel '{channel_username}': {e}")
    
# Function to update all channels
async def update_all_channels():
    try:
        channels = db.collection('channels').get()
        channelUsernames = [doc.get('channel_username') for doc in channels]
        tasks = [update_channel(username) for username in channelUsernames]
        await asyncio.gather(*tasks)

    except Exception as e:
        print(f"error: {e}")

# Test function
def main():
    asyncio.run(update_all_channels())

if __name__ == "__main__":
    main()
