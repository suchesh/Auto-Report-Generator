from pymongo import MongoClient
from datetime import datetime



class Database:
    """Handles MongoDB connection, data storage, and retrieval."""

    def __init__(self, uri="mongodb://localhost:27017/", db_name="suchesh", collection_name="uploads"):
        """Initialize the database connection."""
        try:
            self.client = MongoClient(uri)  # Connect to MongoDB
            self.db = self.client[db_name]  # Select database
            self.collection = self.db[collection_name]  # Select collection
            print("Database configured successfully!")
        except Exception as e:
            print(f"Error configuring DB: {e}")

    def store_data(self, file_name, summary):
        """Stores data in MongoDB."""
        try:
            data = {
                "timestamp": datetime.utcnow(),
                "file_uploaded": file_name,
                "summary": summary
            }
            self.collection.insert_one(data)
            print("Data stored successfully!")
        except Exception as e:
            print(f"Error storing data: {e}")

    def retrieve_data(self):
        """Retrieves all records from MongoDB."""
        try:
            records = list(self.collection.find({}, {"_id": 0, "file_uploaded": 0}))  # Excluding `_id` from output
            if records:
                print("Retrived Successsfully")
            return records
        except Exception as e:
            print(f"Error retrieving data: {e}")
            return None
