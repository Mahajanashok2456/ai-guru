import os
from dotenv import load_dotenv
from pymongo import MongoClient
import sys

# Load environment variables
load_dotenv()

atlas_uri = os.getenv("ATLAS_URI")
print(f"ATLAS_URI found: {'Yes' if atlas_uri else 'No'}")

if atlas_uri:
    # Print first few chars to verify format (don't print full secret)
    print(f"ATLAS_URI prefix: {atlas_uri[:15]}...")
    
    try:
        print("Attempting to connect...")
        client = MongoClient(atlas_uri, serverSelectionTimeoutMS=5000)
        client.admin.command('ping')
        print("Connection SUCCESS!")
    except Exception as e:
        print(f"Connection FAILED: {e}")
else:
    print("ATLAS_URI is missing from .env")
