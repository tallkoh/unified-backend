import requests

BASE = "https://unified-nus-2b9aee59f9d9.herokuapp.com/"

response = requests.post(BASE + "channels/nuswomeninbusiness")

print(response.status_code)
print(response.content)