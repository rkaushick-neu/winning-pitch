import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY_REF=os.getenv("OPENROUTER_API_KEY")

response = requests.get(
    "https://openrouter.ai/api/v1/key",
    headers={"Authorization": f"Bearer {API_KEY_REF}"}
)
print(response.json())
