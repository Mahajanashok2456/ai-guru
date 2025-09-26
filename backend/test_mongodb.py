#!/usr/bin/env python3
"""Test MongoDB Connection"""

from pymongo import MongoClient
from dotenv import load_dotenv
import os
from datetime import datetime
import uuid

# Load environment variables
load_dotenv()

def test_mongodb_connection():
    try:
        # MongoDB connection
        MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb+srv://Mahajan:2456@cluster0.api5hwq.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
        print(f"Connecting to MongoDB...")
        
        client = MongoClient(MONGODB_URI)
        
        # Test the connection
        client.admin.command('ping')
        print("✅ MongoDB connection successful!")
        
        # Get database and collection
        db = client.guru_multibot
        chat_collection = db.chat_history
        
        # Test inserting a document
        test_doc = {
            "_id": str(uuid.uuid4()),
            "input_type": "text",
            "user_input": "Test message from Python",
            "bot_response": "Test response",
            "session_id": "test_session",
            "timestamp": datetime.utcnow()
        }
        
        result = chat_collection.insert_one(test_doc)
        print(f"✅ Test document inserted with ID: {result.inserted_id}")
        
        # Test querying documents
        count = chat_collection.count_documents({})
        print(f"✅ Total documents in collection: {count}")
        
        # Test finding the test document
        found_doc = chat_collection.find_one({"session_id": "test_session"})
        if found_doc:
            print(f"✅ Test document found: {found_doc['user_input']}")
        
        # Clean up - delete test document
        chat_collection.delete_one({"_id": test_doc["_id"]})
        print("✅ Test document cleaned up")
        
        print("\n🎉 All MongoDB tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ MongoDB connection failed: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    test_mongodb_connection()