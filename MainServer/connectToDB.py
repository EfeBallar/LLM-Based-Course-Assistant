"""THIS FUNCTION CONNECTS TO THE MONGODB SERVER AND RETURNS A REFERENCE TO THE DATABASE"""
from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os

def connect_to_database():
    # Get info from .env file
    load_dotenv()

    # Mongo Related Variables
    USERNAME = os.getenv("DB_USERNAME")
    PASSWORD = os.getenv("PASSWORD")
    CLUSTER_ADDRESS = os.getenv("CLUSTER_ADDRESS")
    APP_NAME = os.getenv("APP_NAME")

   
    uri = f"mongodb+srv://{USERNAME}:{PASSWORD}@{CLUSTER_ADDRESS}/?retryWrites=true&w=majority&appName={APP_NAME}"

    # Create a new client and connect to the server
    client = MongoClient(uri, server_api=ServerApi('1'))

    # Reference to the database and collection
    db = client.CourseAssistantDB
    print("Connection with database is established")
    return db
