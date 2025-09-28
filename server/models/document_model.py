from datetime import datetime
from bson import ObjectId

def create_document(mongo, data):
    """
    Create a new document in the database
    
    Args:
        mongo: Database connection
        data: Dictionary containing document information
    
    Returns:
        ObjectId: The ID of the created document
    """
    try:
        document = {
            "source": data.get("source"),             # URL or public link
            "status": data.get("status", "pending"), # e.g., pending, verified, invalid
            "issuer_id": data.get("issuer_id"),
            "verified_by": data.get("verified_by", []),  # List of verifier IDs
            "issue_time": data.get("issue_time", datetime.utcnow()),  # Fixed datetime call
            "ocr_data": data.get("ocr_data", {}),     # text extracted by OCR
            "ai_score": data.get("ai_score", 0.0),   # anomaly detection score
            "metaData": data.get("metaData", {}),    # watermark info, metadata
            "hash": data.get("hash"),                 # optional HMAC hash
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        result = mongo.db.documents.insert_one(document)
        print(f"✅ Document created with ID: {result.inserted_id}")
        return result.inserted_id
    except Exception as e:
        print(f"❌ Error creating document: {str(e)}")
        raise e

def get_document(mongo, doc_id):
    """
    Retrieve a document by ID
    
    Args:
        mongo: Database connection
        doc_id: String or ObjectId of the document
    
    Returns:
        dict: Document data or None if not found
    """
    try:
        if isinstance(doc_id, str):
            doc_id = ObjectId(doc_id)
        return mongo.db.documents.find_one({"_id": doc_id})
    except Exception as e:
        print(f"❌ Error retrieving document: {str(e)}")
        return None

def add_verifier(mongo, doc_id, verifier_id):
    """
    Add a verifier to a document's verified_by list
    
    Args:
        mongo: Database connection
        doc_id: String or ObjectId of the document
        verifier_id: String or ObjectId of the verifier
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        if isinstance(doc_id, str):
            doc_id = ObjectId(doc_id)
        if isinstance(verifier_id, str):
            verifier_id = ObjectId(verifier_id)
            
        result = mongo.db.documents.update_one(
            {"_id": doc_id},
            {
                "$push": {"verified_by": verifier_id},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        return result.modified_count > 0
    except Exception as e:
        print(f"❌ Error adding verifier to document: {str(e)}")
        return False

def get_documents_by_issuer(mongo, issuer_id):
    """
    Get all documents issued by a specific issuer
    
    Args:
        mongo: Database connection
        issuer_id: String or ObjectId of the issuer
    
    Returns:
        list: List of documents
    """
    try:
        if isinstance(issuer_id, str):
            issuer_id = ObjectId(issuer_id)
        
        documents = list(mongo.db.documents.find({"issuer_id": issuer_id}))
        return documents
    except Exception as e:
        print(f"❌ Error retrieving documents by issuer: {str(e)}")
        return []

def get_documents_by_verifier(mongo, verifier_id):
    """
    Get all documents verified by a specific verifier
    
    Args:
        mongo: Database connection
        verifier_id: String or ObjectId of the verifier
    
    Returns:
        list: List of documents
    """
    try:
        if isinstance(verifier_id, str):
            verifier_id = ObjectId(verifier_id)
        
        documents = list(mongo.db.documents.find({"verified_by": verifier_id}))
        return documents
    except Exception as e:
        print(f"❌ Error retrieving documents by verifier: {str(e)}")
        return []

def update_document_status(mongo, document_id, new_status):
    """
    Update the status of a document
    
    Args:
        mongo: Database connection
        document_id: String or ObjectId of the document
        new_status: New status for the document
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        if isinstance(document_id, str):
            document_id = ObjectId(document_id)
        
        result = mongo.db.documents.update_one(
            {"_id": document_id},
            {
                "$set": {
                    "status": new_status,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        return result.modified_count > 0
    except Exception as e:
        print(f"❌ Error updating document status: {str(e)}")
        return False
