from flask import current_app as app
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure

"""
We use mongo to store all the webhook events
"""

__mongo_client = None


def _get_connection_string():
    hostname = app.config['mongo_host']
    port = app.config['mongo_port']
    username = app.config['mongo_username']
    password = app.config['mongo_password']
    dbname = app.config['mongo_database']
    return f"mongodb://{username}:{password}@{hostname}:{port}/{dbname}?authSource=admin"


def connect():
    global __mongo_client
    __mongo_client = MongoClient(_get_connection_string(), serverSelectionTimeoutMS=5000)
    return __mongo_client


def available():
    try:
        # The ismaster command is cheap and does not require auth.
        client = MongoClient(_get_connection_string(), serverSelectionTimeoutMS=1000)
        client.admin.command('ismaster')
        return True
    except ConnectionFailure:
        # print("Server not available")
        return False

def save_event(event_type, event_data, event_error):
    if __mongo_client is None:
        connect()
    dbname = app.config['mongo_database']
    db = __mongo_client[dbname]
    collection = db['events']
    collection.insert_one({
        "event_type": event_type,
        "event_data": event_data,
        "event_error": event_error
    })
