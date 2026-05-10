import os
import ssl
import sys
from datetime import datetime

import certifi
from mongoengine import Document, StringField, DateTimeField, connect, disconnect
from mongoengine.connection import get_connection
from dotenv import load_dotenv

load_dotenv()

def clean_env(value):
    if not value:
        return None
    return value.strip().strip('"').strip("'")

def env_flag(name, default=False):
    value = clean_env(os.environ.get(name))
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}

MONGO_URI = clean_env(os.environ.get("MONGO_URI") or os.environ.get("MONGO_DB"))
DB_NAME = clean_env(os.environ.get("DB_NAME")) or "visitor_db"
MONGO_TLS_ALLOW_INVALID_CERTIFICATES = env_flag(
    "MONGO_TLS_ALLOW_INVALID_CERTIFICATES"
)
MONGO_TLS_DISABLE_OCSP_ENDPOINT_CHECK = env_flag(
    "MONGO_TLS_DISABLE_OCSP_ENDPOINT_CHECK",
    True,
)
DB_CONNECTED = False

def connect_db():
    global DB_CONNECTED

    disconnect(alias="default")

    if not MONGO_URI:
        # Fallback for local
        print("Connecting to local MongoDB...")
        connect(db=DB_NAME, host="mongodb://localhost:27017/")
        get_connection().admin.command("ping")
        DB_CONNECTED = True
    else:
        try:
            # Atlas connection
            print("Connecting to MongoDB Atlas...")
            print(f"Python runtime: {sys.version.split()[0]}, OpenSSL: {ssl.OPENSSL_VERSION}")
            connect(
                host=MONGO_URI,
                db=DB_NAME,
                tls=True,
                tlsCAFile=certifi.where(),
                tlsAllowInvalidCertificates=MONGO_TLS_ALLOW_INVALID_CERTIFICATES,
                tlsDisableOCSPEndpointCheck=MONGO_TLS_DISABLE_OCSP_ENDPOINT_CHECK,
                connectTimeoutMS=30000,
                socketTimeoutMS=30000,
                serverSelectionTimeoutMS=30000,
                retryWrites=True,
            )
            get_connection().admin.command("ping")
            DB_CONNECTED = True
            print("Successfully connected to MongoDB Atlas!")
        except Exception as e:
            DB_CONNECTED = False
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
