import os
from dotenv import load_dotenv

load_dotenv()

INDEX_ID = os.getenv("TWELVELABS_INDEX_ID")

if not INDEX_ID:
    raise ValueError("INDEX_ID is missing")