from datetime import datetime

def create_verifier(mongo, data):
    verifier = {
        "name": data.get("name"),
        "organization": data.get("organization"),
        "uploads": [],             # List of documents verified/uploaded
        "role": "verifier",
        "created_at": datetime.utcnow()
    }
    return mongo.db.verifiers.insert_one(verifier).inserted_id

def get_verifier(mongo, verifier_id):
    return mongo.db.verifiers.find_one({"_id": verifier_id})
