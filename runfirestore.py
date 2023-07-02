# -*- coding: utf-8 -*-

# import modules
import datetime
import pandas as pd
import argparse
import asyncio
import json
import time as t
import sys
import os

# import Telegram API submodules
from api import *
from datetime import timedelta
from utils import (
	get_config_attrs, JSONEncoder, create_dirs, cmd_request_type,
	write_collected_chats
)

# import firebase submodules
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

'''

Arguments

'''

parser = argparse.ArgumentParser(description='Arguments.')
parser.add_argument(
	'--telegram-channel',
	type=str,
	required='--batch-file' not in sys.argv,
	help='Specifies a Telegram Channel.'
)
parser.add_argument(
	'--batch-file',
	type=str,
	required='--telegram-channel' not in sys.argv,
	help='File containing Telegram Channels, one channel per line.'
)
parser.add_argument(
	'--limit-download-to-channel-metadata',
	action='store_true',
	help='Will collect channels metadata only, not posts data.'
)

'''

Output
'''
parser.add_argument(
	'--output',
	'-o',
	type=str,
	required=False,
	help='Folder to save collected data. Default: `./output/data`'
)




'''

Updating data
'''
parser.add_argument(
	'--min-id',
	type=int,
	help='Specifies the offset id. This will update Telegram data with new posts.'
)



# parse arguments
args = vars(parser.parse_args())
config_attrs = get_config_attrs()

args = {**args, **config_attrs}

if all(i is not None for i in args.values()):
	parser.error('Select either --telegram-channel or --batch-file options only.')


# log results
text = f'''
Init program at {t.ctime()}

'''
print (text)


'''

Variables

'''

# Telegram API credentials

'''

FILL API KEYS
'''
sfile = 'session_file'
api_id = args['api_id']
api_hash = args['api_hash']
phone = args['phone']

# event loop
loop = asyncio.get_event_loop()

# data collection
counter = {}

'''

> Get Client <API connection>

'''

# get `client` connection
client = loop.run_until_complete(
	get_connection(sfile, api_id, api_hash, phone)
)

# request type
req_type, req_input = cmd_request_type(args)
if req_type == 'batch':
	req_input = [
		i.rstrip() for i in open(
			req_input, encoding='utf-8', mode='r'
		)
	]
else:
	req_input = [req_input]

# reading | Creating an output folder
if args['output']:
	output_folder = args['output']
	if output_folder.endswith('/'):
		output_folder = output_folder[:-1]
	else:
		pass
else:
	output_folder = './output/data'

# create dirs
create_dirs(output_folder)


'''

Methods

- GetHistoryRequest
- SearchGlobalRequest

'''

# Initialize Firebase Admin SDK
cred = credentials.Certificate('./the-unifiers-firebase-adminsdk-vzs1p-06f0a83999.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

# iterate channels
for channel in req_input:

	'''

	Process arguments
	-> channels' data

	-> Get Entity <Channel's attrs>
	-> Get Full Channel request.
	-> Get Posts <Request channels' posts>

	'''

	# new line
	print ('')
	print (f'> Collecting data from Telegram Channel -> {channel}')
	print ('> ...')
	print ('')

	# Channel's attributes
	entity_attrs = loop.run_until_complete(
		get_entity_attrs(client, channel)
	)

	if entity_attrs:

		# Get Channel ID | convert output to dict
		channel_id = entity_attrs.id
		entity_attrs_dict = entity_attrs.to_dict()

		# Collect Source -> GetFullChannelRequest
		channel_request = loop.run_until_complete(
			full_channel_req(client, channel_id)
		)

		# save full channel request
		full_channel_data = channel_request.to_dict()

		# JsonEncoder
		full_channel_data = JSONEncoder().encode(full_channel_data)
		full_channel_data = json.loads(full_channel_data)

		# save data
		print ('> Writing channel data...')
		print ('> done.')
		print ('')

		# collect chats
		""" chats_path = f'{output_folder}/chats.txt'
		chats_file = open(chats_path, mode='a', encoding='utf-8')

		# channel chats
		counter = write_collected_chats(
			full_channel_data['chats'],
			chats_file,
			channel,
			counter,
			'channel_request',
			client,
			output_folder
		) """

		if not args['limit_download_to_channel_metadata']:

			# Collect posts
			if not args['min_id']:
				posts = loop.run_until_complete(
					get_posts(client, channel_id)
				)

			else:
				min_id = args['min_id']
				posts = loop.run_until_complete(
					get_posts(client, channel_id, min_id=min_id)
				)

			data = posts.to_dict()

			# Get offset ID | Get messages
			offset_id = min([i['id'] for i in data['messages']])

			while len(posts.messages) > 0:
				
				if args['min_id']:
					posts = loop.run_until_complete(
						get_posts(
							client,
							channel_id,
							min_id=min_id,
							offset_id=offset_id
						)
					)	
				else:
					posts = loop.run_until_complete(
						get_posts(
							client,
							channel_id,
							offset_id=offset_id
						)
					)

				# Update data dict
				if posts.messages:
					tmp = posts.to_dict()
					data['messages'].extend(tmp['messages'])

					# Adding unique chats objects
					all_chats = [i['id'] for i in data['chats']]
					chats = [
						i for i in tmp['chats']
						if i['id'] not in all_chats
					]

					# channel chats in posts
					""" counter = write_collected_chats(
						tmp['chats'],
						chats_file,
						channel,
						counter,
						'from_messages',
						client,
						output_folder
					) """

					# Adding unique users objects
					all_users = [i['id'] for i in data['users']]
					users = [
						i for i in tmp['users']
						if i['id'] not in all_users
					]

					# extend UNIQUE chats & users
					data['chats'].extend(chats)
					data['users'].extend(users)

					# Get offset ID
					offset_id = min([i['id'] for i in tmp['messages']])

			# JsonEncoder
			data = JSONEncoder().encode(data)
			data = json.loads(data)

			""" print('> Writing posts data...')
			file_path = f'{output_folder}/{channel}/{channel}_messages.json'
			obj = json.dumps(
                data,
                ensure_ascii=False,
                separators=(',', ':')
            )

			# write data to JSON file
			with open(file_path, 'w') as json_file:
				json.dump(data, json_file)

            # read JSON file and extract data
			with open(file_path) as json_file:
				data = json.load(json_file) """

            # extract and store data in Firestore
			messages = data.get('messages', [])
			chats = data.get('chats', [])
			for chat in chats:
				channel_id = chat.get('id')
				channel_name = chat.get('title')

				# Create a new document in the Firestore collection
				doc_ref = db.collection('channels').document()
				doc_ref.set({
					'channel_id': channel_id,
					'channel_name': channel_name
				})
			for message in messages:
				message_id = message.get('id')
				channel_id = message.get('peer_id', {}).get('channel_id')
				message_text = message.get('message')
				timestamp = message.get('date')
				current_date = datetime.datetime.now().date()
				two_weeks_prior = current_date - timedelta(days=14)
				message_date = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S%z").date()
                
				doc_ref = db.collection('news').document()
                
				if message_text is not None and message_text != '' and two_weeks_prior <= message_date <= current_date:
					doc_ref.set({
						'channel_id': channel_id,
						'message_id': message_id,
						'timestamp': datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S%z"),
						'message_text': message_text
					})

            # writer
			""" writer = open(file_path, mode='w', encoding='utf-8')
			writer.write(obj)
			writer.close() """
			print('> done.')
			print('')
        
        # sleep program for a few seconds    
		if len(req_input) > 1:
			time.sleep(2)
	else:
		'''

		Channels not found
		'''
		""" exceptions_path = f'{output_folder}/_exceptions-channels-not-found.txt'
		w = open(exceptions_path, encoding='utf-8', mode='a')
		w.write(f'{channel}\n')
		w.close() """
'''

Clean generated chats text file

'''

# close chat file
# chats_file.close()

""" # get collected chats
collected_chats = list(set([
	i.rstrip() for i in open(chats_path, mode='r', encoding='utf-8')
]))

# re write collected chats
chats_file = open(chats_path, mode='w', encoding='utf-8')
for c in collected_chats:
	chats_file.write(f'{c}\n') """

# close file
# chats_file.close()


""" # Process counter
counter_df = pd.DataFrame.from_dict(
	counter,
	orient='index'
).reset_index().rename(
	columns={
		'index': 'id'
	}
)

# save counter
counter_df.to_csv(
	f'{output_folder}/counter.csv',
	encoding='utf-8',
	index=False
)

# merge dataframe
df = pd.read_csv(
	f'{output_folder}/collected_chats.csv',
	encoding='utf-8'
)

del counter_df['username']
df = df.merge(counter_df, how='left', on='id', suffixes=('_df', '_counter'))
df.to_csv(
	f'{output_folder}/collected_chats.csv',
	index=False,
	encoding='utf-8'
) """


# log results
text = f'''
End program at {t.ctime()}

'''
print (text)
