from mongoengine import Document, StringField, DateTimeField, connect
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.environ.get("MONGO_URI") or os.environ.get("MONGO_DB")
DB_NAME = os.environ.get("DB_NAME", "visitor_db")

def connect_db():
    if not MONGO_URI:
        # Fallback for local
        print("Connecting to local MongoDB...")
        connect(db=DB_NAME, host="mongodb://localhost:27017/")
    else:
        try:
            # Atlas connection
            print("Connecting to MongoDB Atlas...")
            connect(host=MONGO_URI, db=DB_NAME)
            print("Successfully connected to MongoDB Atlas!")
        except Exception as e:
            print(f"Error connecting to MongoDB: {e}")
            raise e

class Visitor(Document):
    student_name = StringField(required=True)
    student_number = StringField(required=True, unique=True)
    course_name = StringField(required=True)
    parent_name = StringField(required=True)
    parent_contact = StringField(required=True)
    created_at = DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'visitors',
        'indexes': [
            'student_number',
            '-created_at'
        ]
    }

class Admin(Document):
    email = StringField(required=True, unique=True)
    password_hash = StringField(required=True)
    created_at = DateTimeField(default=datetime.utcnow)

    meta = {
        'collection': 'admins',
        'indexes': [
            'email'
        ]
    }
