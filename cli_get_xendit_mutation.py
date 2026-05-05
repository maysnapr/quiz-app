import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("XENDIT_API_KEY")

url = "https://api.xendit.co/balance"
response = requests.get(url, auth=(API_KEY, ""))

print(response.status_code)
print(response.text)