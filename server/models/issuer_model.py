from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

def create_issuer(mongo, data):
    issuer = {
        "name": data.get("name"),
        "institution": data.get("institution"),
        "documents": [],            # List of document IDs issued
        "role": "issuer",
        "created_at": datetime.utcnow()
    }
    return mongo.db.issuers.insert_one(issuer).inserted_id

def get_issuer(mongo, issuer_id):
    return mongo.db.issuers.find_one({"_id": issuer_id})
