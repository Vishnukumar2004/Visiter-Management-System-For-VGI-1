import os
import ssl
import sys
from datetime import datetime
from urllib.parse import parse_qs, urlparse

import certifi
from dotenv import load_dotenv
from mongoengine import DateTimeField, Document, StringField, connect, disconnect
from mongoengine.connection import get_connection

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
IS_RENDER = env_flag("RENDER") or bool(
    os.environ.get("RENDER_SERVICE_ID") or os.environ.get("RENDER_EXTERNAL_URL")
)
MONGO_TLS_ALLOW_INVALID_CERTIFICATES = env_flag(
    "MONGO_TLS_ALLOW_INVALID_CERTIFICATES"
)
MONGO_TLS_DISABLE_OCSP_ENDPOINT_CHECK = env_flag(
    "MONGO_TLS_DISABLE_OCSP_ENDPOINT_CHECK",
    True,
)
DB_CONNECTED = False
DB_ERROR = None


def get_mongo_host():
    if not MONGO_URI:
        return None

    parsed_uri = urlparse(MONGO_URI)
    return parsed_uri.hostname


def get_mongo_uri_options():
    if not MONGO_URI:
        return {}

    parsed_uri = urlparse(MONGO_URI)
    return {key.lower(): values for key, values in parse_qs(parsed_uri.query).items()}


def get_database_status():
    uri_options = get_mongo_uri_options()
    return {
        "connected": DB_CONNECTED,
        "db_name": DB_NAME,
        "mongo_uri_configured": bool(MONGO_URI),
        "mongo_host": get_mongo_host(),
        "mongo_uri_tls_allow_invalid_certificates": (
            "tlsallowinvalidcertificates" in uri_options
        ),
        "mongo_uri_tls_disable_ocsp_endpoint_check": (
            "tlsdisableocspendpointcheck" in uri_options
        ),
        "running_on_render": IS_RENDER,
        "tls_disable_ocsp_endpoint_check": MONGO_TLS_DISABLE_OCSP_ENDPOINT_CHECK,
        "tls_allow_invalid_certificates": MONGO_TLS_ALLOW_INVALID_CERTIFICATES,
        "error": DB_ERROR,
    }


def connect_db():
    global DB_CONNECTED, DB_ERROR

    disconnect(alias="default")

    if not MONGO_URI:
        if IS_RENDER:
            DB_CONNECTED = False
            DB_ERROR = "MONGO_URI environment variable is not set on Render."
            raise RuntimeError(DB_ERROR)

        print("Connecting to local MongoDB...")
        connect(db=DB_NAME, host="mongodb://localhost:27017/")
        get_connection().admin.command("ping")
        DB_CONNECTED = True
        DB_ERROR = None
        return

    try:
        print("Connecting to MongoDB Atlas...")
        print(f"Python runtime: {sys.version.split()[0]}, OpenSSL: {ssl.OPENSSL_VERSION}")

        uri_options = get_mongo_uri_options()
        uri_has_invalid_cert_option = "tlsallowinvalidcertificates" in uri_options
        uri_has_ocsp_option = "tlsdisableocspendpointcheck" in uri_options

        connection_options = {
            "host": MONGO_URI,
            "db": DB_NAME,
            "tls": True,
            "tlsCAFile": certifi.where(),
            "connectTimeoutMS": 30000,
            "socketTimeoutMS": 30000,
            "serverSelectionTimeoutMS": 30000,
            "retryWrites": True,
        }

        if MONGO_TLS_ALLOW_INVALID_CERTIFICATES:
            connection_options["tlsAllowInvalidCertificates"] = True
        elif not uri_has_invalid_cert_option and not uri_has_ocsp_option:
            connection_options["tlsDisableOCSPEndpointCheck"] = (
                MONGO_TLS_DISABLE_OCSP_ENDPOINT_CHECK
            )

        connect(**connection_options)
        get_connection().admin.command("ping")
        DB_CONNECTED = True
        DB_ERROR = None
        print("Successfully connected to MongoDB Atlas!")
    except Exception as exc:
        DB_CONNECTED = False
        DB_ERROR = str(exc)
        print(f"Error connecting to MongoDB: {exc}")
        raise


class Visitor(Document):
    student_name = StringField(required=True)
    student_number = StringField(required=True, unique=True)
    course_name = StringField(required=True)
    parent_name = StringField(required=True)
    parent_contact = StringField(required=True)
    created_at = DateTimeField(default=datetime.utcnow)

    meta = {
        "collection": "visitors",
        "indexes": [
            "student_number",
            "-created_at",
        ],
    }


class Admin(Document):
    email = StringField(required=True, unique=True)
    password_hash = StringField(required=True)
    created_at = DateTimeField(default=datetime.utcnow)

    meta = {
        "collection": "admins",
        "indexes": [
            "email",
        ],
    }
