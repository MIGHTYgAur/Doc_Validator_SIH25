from datetime import datetime
def create_document(mongo, data):
    document = {
        "source": data.get("source"),             # URL or public link
        "status": data.get("status", "pending"), # e.g., pending, verified, invalid
        "issuer_id": data.get("issuer_id"),
        "verified_by": [],                        # List of verifier IDs
        "issue_time": datetime.now(datetime.utcnow()),
        "ocr_data": data.get("ocr_data", {}),     # text extracted by OCR
        "ai_score": data.get("ai_score", 0.0),   # anomaly detection score
        "metaData": data.get("metaData", {}),    # watermark info, metadata
        "hash": data.get("hash"),                 # optional HMAC hash
    }
    return mongo.db.documents.insert_one(document).inserted_id

def get_document(mongo, doc_id):
    return mongo.db.documents.find_one({"_id": doc_id})

def add_verifier(mongo, doc_id, verifier_id):
    mongo.db.documents.update_one(
        {"_id": doc_id},
        {"$push": {"verified_by": verifier_id}}
    )
