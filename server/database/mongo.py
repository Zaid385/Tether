import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

class MongoDB:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MongoDB, cls).__new__(cls)
            cls._instance._connect()
        return cls._instance

    def _connect(self):
        uri = os.getenv("MONGODB_URI", "mongodb://127.0.0.1:27017/")
        db_name = os.getenv("MONGODB_DB", "tether_db")
        
        try:
            self.client = MongoClient(uri, serverSelectionTimeoutMS=2000)
            self.db = self.client[db_name]
            # Force a call to verify connection
            self.client.admin.command('ping')
            
            # Collections
            self.users = self.db["users"]
            self.messages = self.db["messages"]
            self.groups = self.db["groups"]
            self.notifications = self.db["notifications"]
            self.logs = self.db["logs"]
            
            print(f"✅ Connected to MongoDB: {db_name}")
        except Exception as e:
            print(f"❌ CRITICAL: Could not connect to MongoDB at {uri}")
            print("Ensure that the MongoDB service is running.")
            print("Run: 'sudo systemctl start mongodb' (on Arch Linux)")
            raise e

    def close(self):
        self.client.close()
