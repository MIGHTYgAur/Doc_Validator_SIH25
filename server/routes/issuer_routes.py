from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
import tempfile
from datetime import datetime
from models.issuer_model import get_issuer
from models.document_model import create_document
from services.ocr import extract_text
from services.hmac_hash import hash_document
from services.cloudinary_service import upload_document
from database import mongo
from bson import ObjectId

issuer_bp = Blueprint("issuer", __name__)

# Allowed file extensions for document upload
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'tiff', 'bmp'}

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@issuer_bp.route("/upload", methods=["POST"])
def issuer_upload_document():
    """
    Issuer uploads document - OCR extraction with suspicion score = 0
    """
    try:
        # Check if file is uploaded
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        print("hi")
        # Validate file type
        if not allowed_file(file.filename):
            return jsonify({
                "error": "Invalid file type", 
                "allowed_types": list(ALLOWED_EXTENSIONS)
            }), 400
        
        # Get issuer ID from request
        issuer_id = request.form.get('issuer_id')
        if not issuer_id:
            return jsonify({"error": "Issuer ID is required"}), 400
        
        # Validate issuer exists
        issuer = get_issuer(mongo, issuer_id)
        if not issuer:
            return jsonify({"error": "Issuer not found"}), 404
        
        # Upload document to Cloudinary
        print(f"� Uploading document to Cloudinary...")
        cloudinary_result = upload_document(file, folder=f"issuers/{issuer_id}")
        
        if not cloudinary_result["success"]:
            return jsonify({
                "error": "Failed to upload document to cloud storage",
                "details": cloudinary_result["error"]
            }), 500
        
        document_url = cloudinary_result["secure_url"]
        public_id = cloudinary_result["public_id"]
        
        print(f"✅ Document uploaded to Cloudinary: {document_url}")
        
        # Create temporary file for OCR processing
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{cloudinary_result['format']}") as temp_file:
            # Reset file pointer and save to temp file
            file.seek(0)
            temp_file.write(file.read())
            temp_filepath = temp_file.name
        
        # Extract OCR text from temporary file
        print(f"🔤 Extracting OCR text from temporary file...")
        ocr_text = extract_text(temp_filepath)
        
        # Generate HMAC hash using institute secret key
        institute_secret = "supersecretkey"  # Default VJTI secret key
        try:
            document_hash = hash_document(temp_filepath, institute_secret)
            print(f"🔐 Document hash generated: {document_hash[:16]}...")
        except Exception as e:
            print(f"⚠️ Hash generation failed: {e}")
            document_hash = None
        
        # Clean up temporary file
        try:
            os.unlink(temp_filepath)
            print(f"🗑️ Temporary file cleaned up")
        except Exception as e:
            print(f"⚠️ Failed to clean up temp file: {e}")
        
        # Prepare document data as per issuer model requirements
        document_data = {
            "source": document_url,  # Cloudinary URL
            "status": "verified",  # Issuer documents are pre-verified
            "issuer_id": ObjectId(issuer_id),
            "verified_by": [ObjectId(issuer_id)],  # Self-verified by issuer
            "issue_time": datetime.utcnow(),
            "ocr_data": {
                "extracted_text": ocr_text,
                "text_length": len(ocr_text),
                "extraction_method": "tesseract_ocr"
            },
            "ai_score": 0.0,  # Suspicion score = 0 for issuer uploads
            "metaData": {
                "original_filename": file.filename,
                "file_size": cloudinary_result.get("bytes", 0),
                "upload_method": "issuer_upload",
                "issuer_name": issuer.get("name", ""),
                "issuer_institution": issuer.get("institution", ""),
                "document_type": request.form.get("document_type", "certificate"),
                "cloudinary_public_id": public_id,
                "storage_type": "cloudinary"
            },
            "hash": document_hash  # HMAC hash for document integrity
        }
        
        # Create document in database
        doc_id = create_document(mongo, document_data)
        
        # Update issuer's documents list
        mongo.db.issuers.update_one(
            {"_id": ObjectId(issuer_id)},
            {"$push": {"documents": doc_id}}
        )
        
        # Simplified response
        response_data = {
            "success": True,
            "document_id": str(doc_id),
            "filename": file.filename,
            "document_url": document_url,  # Cloudinary URL
            "cloudinary_public_id": public_id,
            "hash": document_hash,
            "suspicion_score": 0.0,
            "status": "verified",
            "upload_timestamp": datetime.utcnow().isoformat(),
            "ocr_text_preview": ocr_text[:100] + "..." if len(ocr_text) > 100 else ocr_text
        }
        
        print(f"✅ Document uploaded successfully by issuer: {doc_id}")
        return jsonify(response_data), 201
        
    except Exception as e:
        print(f"❌ Error in issuer document upload: {str(e)}")
        return jsonify({
            "error": "Failed to upload document",
            "details": str(e)
        }), 500

@issuer_bp.route("/documents/<issuer_id>", methods=["GET"])
def get_issuer_documents(issuer_id):
    """
    Get all documents uploaded by a specific issuer
    """
    try:
        # Validate issuer exists
        issuer = get_issuer(mongo, issuer_id)
        if not issuer:
            return jsonify({"error": "Issuer not found"}), 404
        
        # Get all documents issued by this issuer
        documents = list(mongo.db.documents.find({"issuer_id": ObjectId(issuer_id)}))
        
        # Format documents for response
        formatted_docs = []
        for doc in documents:
            formatted_doc = {
                "document_id": str(doc["_id"]),
                "filename": doc.get("metaData", {}).get("original_filename", "Unknown"),
                "status": doc.get("status", "unknown"),
                "issue_time": doc.get("issue_time"),
                "document_type": doc.get("metaData", {}).get("document_type", "certificate"),
                "ocr_text_preview": doc.get("ocr_data", {}).get("extracted_text", "")[:100] + "...",
                "suspicion_score": doc.get("ai_score", 0.0)
            }
            formatted_docs.append(formatted_doc)
        
        return jsonify({
            "issuer_id": issuer_id,
            "issuer_name": issuer.get("name", ""),
            "institution": issuer.get("institution", ""),
            "total_documents": len(formatted_docs),
            "documents": formatted_docs
        }), 200
        
    except Exception as e:
        print(f"❌ Error getting issuer documents: {str(e)}")
        return jsonify({
            "error": "Failed to retrieve documents",
            "details": str(e)
        }), 500
