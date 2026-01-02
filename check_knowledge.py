
import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

atlas_uri = os.getenv("ATLAS_URI")
client = MongoClient(atlas_uri)
db = client["mahabharata_db"]
collection = db["texts"]

count = collection.count_documents({})
print(f"Total documents in knowledge base: {count}")

if count > 0:
    doc = collection.find_one()
    print("Sample document source:", doc.get("source"))
    print("Sample document text length:", len(doc.get("content", "")))
