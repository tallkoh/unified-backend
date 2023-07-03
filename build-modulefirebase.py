import json
import re
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore


# Initialize Firebase Admin SDK
cred = credentials.Certificate('./the-unifiers-firebase-adminsdk-vzs1p-06f0a83999.json')  # Replace with your actual JSON file path
firebase_admin.initialize_app(cred)
db = firestore.client()

with open("moduleList.json", "r") as file:
    data = json.load(file)

pattern = re.compile(r'^CS[0-9]|^IS[0-9]|^BT[0-9]', re.IGNORECASE)
mods_list = []

for module in data:
    module_code = module["moduleCode"]
    if pattern.match(module_code):
        mods_list.append(module_code)
        
doc_ref = db.collection("modules").document("module_list")
doc_ref.set({"modules": mods_list})
