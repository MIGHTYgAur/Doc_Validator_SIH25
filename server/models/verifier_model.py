from datetime import datetime
from bson import ObjectId

def create_verifier(mongo, data):
    verifier = {
        "name": data.get("name"),
        "email": data.get("email"),
        "password": data.get("password"),  # hashed later in route
        "institution": data.get("institution"),
        "documents": [],                   # List of document IDs verified
        "role": "verifier",
        "created_at": datetime.utcnow()
    }
    return mongo.db.verifiers.insert_one(verifier).inserted_id

def get_verifier(mongo, verifier_id):
    return mongo.db.verifiers.find_one({"_id": ObjectId(verifier_id)})

def get_verifier_by_email(mongo, email):
    return mongo.db.verifiers.find_one({"email": email})
