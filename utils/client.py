import os
from dotenv import load_dotenv
from twelvelabs import TwelveLabs

load_dotenv()

API_KEY = os.getenv("TWELVELABS_API_KEY")

def get_client():
    if not API_KEY:
        raise ValueError("API KEY is missing")
    return TwelveLabs(api_key=API_KEY)