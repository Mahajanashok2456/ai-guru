import os
import google.generativeai as genai
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import time

# --- 1. CONFIGURATION ---
# IMPORTANT: Set these as environment variables
ATLAS_URI = os.environ.get("ATLAS_URI")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# The path to your file (raw string 'r' is critical)
FILE_PATH = r"C:\Users\MAHAJAN ASHOK\OneDrive\Desktop\therapist\mahabharath and ramanayan.txt"

# --- Markers You Provided ---
START_MAHABHARATA = "--- START OF MAHABHARATA ---"
END_MAHABHARATA = "--- END OF MAHABHARATA ---"
START_RAMAYANA = "--- START OF RAMAYANA ---"
END_RAMAYANA = "--- END OF RAMAYANA ---"

# --- Database and Model Config ---
DB_NAME = "mahabharata_db"
COLLECTION_NAME = "texts"
EMBEDDING_MODEL = "models/text-embedding-004"
CHUNK_SIZE_WORDS = 400 # How many words per chunk (approx)

# --- 2. INITIALIZE MODELS AND DB ---

print("Connecting to services...")

# Initialize Gemini
try:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(EMBEDDING_MODEL)
    print("Gemini initialized.")
except Exception as e:
    print(f"Error initializing Gemini: {e}")
    print("Please check your GEMINI_API_KEY environment variable.")
    exit()

# Initialize MongoDB
try:
    client = MongoClient(ATLAS_URI)
    db = client[DB_NAME]
    texts_collection = db[COLLECTION_NAME]
    # Test connection
    client.admin.command('ping')
    print("MongoDB connected.")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    print("Please check your ATLAS_URI environment variable.")
    exit()

# --- 3. THE INGESTION LOGIC ---

def process_and_embed():
    print(f"Starting ingestion from: {FILE_PATH}")
    
    # This variable tracks which epic we are currently in
    # None = we are not inside an epic's text
    current_epic = None 
    
    chunk_buffer = ""
    docs_inserted = 0
    total_lines = 0
    
    try:
        with open(FILE_PATH, 'r', encoding='utf-8') as f:
            for line in f:
                total_lines += 1
                clean_line = line.strip() # Remove whitespace

                # --- State Machine Logic ---
                if clean_line == START_RAMAYANA:
                    print(f"\nFound Start: RAMAYANA (Line {total_lines})")
                    current_epic = "ramayana"
                    # Process last chunk of whatever came before
                    if chunk_buffer.strip():
                        docs_inserted = embed_and_store_chunk(chunk_buffer, "unknown", docs_inserted)
                    chunk_buffer = ""
                    continue # Skip this marker line
                
                elif clean_line == START_MAHABHARATA:
                    print(f"\nFound Start: MAHABHARATA (Line {total_lines})")
                    current_epic = "mahabharata"
                    # Process last chunk of whatever came before
                    if chunk_buffer.strip():
                        docs_inserted = embed_and_store_chunk(chunk_buffer, "ramayana", docs_inserted) # Assumes Ramayana ended
                    chunk_buffer = ""
                    continue # Skip this marker line

                elif clean_line == END_RAMAYANA or clean_line == END_MAHABHARATA:
                    print(f"\nFound End: {current_epic} (Line {total_lines})")
                    # Process the final chunk of the epic
                    if chunk_buffer.strip():
                         docs_inserted = embed_and_store_chunk(chunk_buffer, current_epic, docs_inserted)
                    current_epic = None # We are now "outside" an epic
                    chunk_buffer = ""
                    continue # Skip this marker line

                # --- Process Text Logic ---
                # Only add text if we are "inside" an epic
                if current_epic is not None:
                    chunk_buffer += line + " "
                    
                    # Check if buffer is "full"
                    if len(chunk_buffer.split()) > CHUNK_SIZE_WORDS:
                        docs_inserted = embed_and_store_chunk(chunk_buffer, current_epic, docs_inserted)
                        chunk_buffer = "" # Reset the buffer

            # Process the final remaining chunk in the buffer (if any)
            if chunk_buffer.strip() and current_epic is not None:
                docs_inserted = embed_and_store_chunk(chunk_buffer, current_epic, docs_inserted)

    except FileNotFoundError:
        print(f"ERROR: File not found at {FILE_PATH}")
        print("Please check the path and try again.")
        return
    except Exception as e:
        print(f"An error occurred during file processing: {e}")
        return

    print(f"\n--- Ingestion Complete ---")
    print(f"Total lines processed: {total_lines}")
    print(f"Total documents inserted: {docs_inserted}")

def embed_and_store_chunk(chunk_text, epic_source, docs_inserted):
    """Takes text, gets embedding, and stores in MongoDB."""
    
    try:
        # 1. Get embedding from Gemini
        response = genai.embed_content(
            model=EMBEDDING_MODEL,
            content=chunk_text,
            task_type="RETRIEVAL_DOCUMENT" # Important for RAG
        )
        embedding = response['embedding']
        
        # 2. Create the document
        document = {
            "content": chunk_text,
            "text_embedding": embedding,
            "source": epic_source # The "ramayana" or "mahabharata" tag
        }
        
        # 3. Insert into MongoDB
        texts_collection.insert_one(document)
        docs_inserted += 1
        
        if docs_inserted % 10 == 0:
            print(f"Inserted {docs_inserted} chunks... (current epic: {epic_source})")
        
        # API Rate Limiting - be nice to the free API
        time.sleep(1) # Wait 1 second between API calls
        
    except Exception as e:
        print(f"Warning: Could not embed chunk. Error: {e}")
        print("Skipping this chunk and continuing...")
        time.sleep(5) # Wait longer if there was an error
        
    return docs_inserted

# --- 4. RUN THE SCRIPT ---
if __name__ == "__main__":
    process_and_embed()