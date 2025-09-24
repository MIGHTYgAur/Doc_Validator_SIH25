from datetime import datetime

def create_institute(mongo, data):
    institute = {
        "name": data.get("name"),
        "type": data.get("type"),        # school, university, etc.
        "secret_key": data.get("secret_key"),  # optional, for HMAC
        "created_at": datetime.utcnow(),

    }
    return mongo.db.institutes.insert_one(institute).inserted_id

def get_institute(mongo, institute_id):
    return mongo.db.institutes.find_one({"_id": institute_id})
