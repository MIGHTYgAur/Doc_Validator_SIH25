from datetime import datetime
from bson import ObjectId

def create_issuer(mongo, data):
    issuer = {
        "name": data.get("name"),
        "email": data.get("email"),
        "password": data.get("password"),  # hashed later in route
        "institution": data.get("institution"),
        "documents": [],                   # List of document IDs issued
        "role": "issuer",
        "created_at": datetime.utcnow()
    }
    return mongo.db.issuers.insert_one(issuer).inserted_id

def get_issuer(mongo, issuer_id):
    return mongo.db.issuers.find_one({"_id": ObjectId(issuer_id)})

def get_issuer_by_email(mongo, email):
    return mongo.db.issuers.find_one({"email": email})
