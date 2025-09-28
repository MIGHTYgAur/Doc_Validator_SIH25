from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
import tempfile
from datetime import datetime
from models.verifier_model import get_verifier
from models.document_model import create_document
from services.ocr import extract_text
from services.hmac_hash import hash_document
from services.cloudinary_service import upload_document
from database import mongo
from bson import ObjectId
from services.doc_proccess import process_document

verifier_bp = Blueprint("verifier", __name__)

# Allowed file extensions for document upload
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'tiff', 'bmp'}

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@verifier_bp.route("/upload", methods=["POST"])
def verifier_upload_document():
    """
    Verifier uploads document - Hash verification first, then analysis
    """
    try:
        # Check if file is uploaded
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Validate file type
        if not allowed_file(file.filename):
            return jsonify({
                "error": "Invalid file type", 
                "allowed_types": list(ALLOWED_EXTENSIONS)
            }), 400
        
        # Get verifier ID from request
        verifier_id = request.form.get('verifier_id')
        if not verifier_id:
            return jsonify({"error": "Verifier ID is required"}), 400
        
        # Validate verifier exists
        verifier = get_verifier(mongo, verifier_id)
        if not verifier:
            return jsonify({"error": "Verifier not found"}), 404
        
        # Upload document to Cloudinary
        print(f"📸 Uploading document to Cloudinary...")
        cloudinary_result = upload_document(file, folder=f"verifiers/{verifier_id}")
        
        if not cloudinary_result["success"]:
            return jsonify({
                "error": "Failed to upload document to cloud storage",
                "details": cloudinary_result["error"]
            }), 500
        
        document_url = cloudinary_result["secure_url"]
        public_id = cloudinary_result["public_id"]
        
        print(f"✅ Document uploaded to Cloudinary: {document_url}")
        
        # Create temporary file for processing
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{cloudinary_result['format']}") as temp_file:
            # Reset file pointer and save to temp file
            file.seek(0)
            temp_file.write(file.read())
            temp_filepath = temp_file.name
        
        # Step 1: Generate HMAC hash using institute secret key for verification
        institute_secret = "supersecretkey"  # Default VJTI secret key
        try:
            document_hash = hash_document(temp_filepath, institute_secret)
            print(f"🔐 Document hash generated: {document_hash[:16]}...")
        except Exception as e:
            print(f"⚠️ Hash generation failed: {e}")
            document_hash = None
        
        # Step 2: Hash verification - Check if document exists in database
        existing_doc = None
        verification_status = "new_document"
        if document_hash:
            existing_doc = mongo.db.documents.find_one({"hash": document_hash})
            if existing_doc:
                verification_status = "hash_verified"
                print(f"✅ Document hash found in database - issued by: {existing_doc.get('issuer_id')}")
            else:
                verification_status = "hash_not_found" 
                print(f"❌ Document hash not found in database - potentially fraudulent")
        
        # Step 3: Extract OCR text for analysis
        print(f"🔤 Extracting OCR text from: {document_url}")
        ocr_text = extract_text(document_url)
        
        # Step 4: Determine verification result based on hash check
        if verification_status == "hash_verified":
            # Document exists in DB - GUARANTEED AUTHENTIC
            suspicion_score = 0.0  # Zero suspicion for hash-verified docs
            status = "verified"
            verdict = "authentic"
            analysis_explanation = f"✅ AUTHENTIC: Document hash verified in database. Originally issued by issuer ID: {existing_doc.get('issuer_id')}"
            
        elif verification_status == "hash_not_found":
            # Hash not found - run detailed analysis
            print(f"🔍 Hash not found - running detailed analysis: {document_url}")
            doc_analysis = process_document(document_url, ocr_text)
            suspicion_score = min(0.8, doc_analysis.get('suspicion_score', 0.5) + 0.3)  # Increase suspicion for unknown hash
            verdict = "hash_not_verified"
            analysis_explanation = f"Document hash not found in database. Visual analysis: {doc_analysis.get('explanation', 'Document analyzed')}"
            
            # Status based on combined analysis
            if suspicion_score < 0.4:
                status = "pending_review"  # Even if analysis looks good, hash missing is concerning
            else:
                status = "suspicious"
                
        else:
            # Hash generation failed - run analysis only
            print(f"🔍 Hash generation failed - running visual analysis only: {temp_filepath}")
            doc_analysis = process_document(temp_filepath, ocr_text)
            suspicion_score = doc_analysis.get('suspicion_score', 0.5)
            verdict = doc_analysis.get('verdict', 'requires_review')
            analysis_explanation = f"Hash verification unavailable. Visual analysis: {doc_analysis.get('explanation', 'Document analyzed')}"
            
            # Standard status determination
            if verdict == "likely_authentic":
                status = "pending_review"  # Downgrade since no hash verification
            elif verdict == "requires_review":
                status = "pending_review"
            else:
                status = "suspicious"
        
        # Prepare document data as per verifier model requirements
        document_data = {
            "source": document_url,  # Cloudinary URL
            "status": status,
            "issuer_id": None,  # Unknown issuer for verifier uploads
            "verified_by": [ObjectId(verifier_id)],  # Verified by this verifier
            "issue_time": datetime.utcnow(),
            "ocr_data": {
                "extracted_text": ocr_text,
                "text_length": len(ocr_text),
                "extraction_method": "tesseract_ocr"
            },
            "ai_score": suspicion_score,  # Suspicion score from analysis
            "metaData": {
                "original_filename": file.filename,
                "file_size": cloudinary_result.get("bytes", 0),
                "upload_method": "verifier_upload",
                "verifier_name": verifier.get("name", ""),
                "verifier_institution": verifier.get("institution", ""),
                "document_type": request.form.get("document_type", "unknown"),
                "verification_notes": f"Document uploaded for verification with suspicion score: {suspicion_score}",
                "cloudinary_public_id": public_id,
                "storage_type": "cloudinary"
            },
            "hash": document_hash  # HMAC hash for document integrity
        }
        
        # Create document in database
        doc_id = create_document(mongo, document_data)
        
        # Update verifier's documents list
        mongo.db.verifiers.update_one(
            {"_id": ObjectId(verifier_id)},
            {"$push": {"documents": doc_id}}
        )
        
        # Clean up temporary file
        try:
            os.unlink(temp_filepath)
            print(f"🗑️ Temporary file cleaned up")
        except Exception as e:
            print(f"⚠️ Failed to clean up temp file: {e}")
        
        # Comprehensive response with verification details
        response_data = {
            "success": True,
            "document_id": str(doc_id),
            "filename": file.filename,
            "document_url": document_url,  # Cloudinary URL
            "cloudinary_public_id": public_id,
            "hash": document_hash,
            "verification_status": verification_status,
            "suspicion_score": suspicion_score,
            "status": status,
            "verdict": verdict,
            "analysis": {
                "explanation": analysis_explanation,
                "hash_verified": verification_status == "hash_verified",
                "existing_issuer": str(existing_doc.get('issuer_id')) if existing_doc else None,
                "ocr_text_preview": ocr_text[:200] + "..." if len(ocr_text) > 200 else ocr_text
            },
            "verdict": verdict,
            "analysis_explanation": analysis_explanation,
            "upload_timestamp": datetime.utcnow().isoformat(),
            "ocr_text_preview": ocr_text[:100] + "..." if len(ocr_text) > 100 else ocr_text,
            "verification_notes": f"Analysis completed: {analysis_explanation}"
        }
        
        print(f"✅ Document uploaded and analyzed by verifier: {doc_id} (Score: {suspicion_score})")
        return jsonify(response_data), 201
        
    except Exception as e:
        print(f"❌ Error in verifier document upload: {str(e)}")
        return jsonify({
            "error": "Failed to upload document",
            "details": str(e)
        }), 500

@verifier_bp.route("/documents/<verifier_id>", methods=["GET"])
def get_verifier_documents(verifier_id):
    """
    Get all documents analyzed by a specific verifier
    """
    try:
        # Validate verifier exists
        verifier = get_verifier(mongo, verifier_id)
        if not verifier:
            return jsonify({"error": "Verifier not found"}), 404
        
        # Get all documents verified by this verifier
        documents = list(mongo.db.documents.find({"verified_by": ObjectId(verifier_id)}))
        
        # Format documents for response
        formatted_docs = []
        for doc in documents:
            formatted_doc = {
                "document_id": str(doc["_id"]),
                "filename": doc.get("metaData", {}).get("original_filename", "Unknown"),
                "status": doc.get("status", "unknown"),
                "verification_time": doc.get("issue_time"),
                "document_type": doc.get("metaData", {}).get("document_type", "unknown"),
                "ocr_text_preview": doc.get("ocr_data", {}).get("extracted_text", "")[:100] + "...",
                "suspicion_score": doc.get("ai_score", 0.0),
                "verification_method": doc.get("metaData", {}).get("upload_method", "unknown")
            }
            formatted_docs.append(formatted_doc)
        
        # Categorize documents by status
        status_summary = {
            "verified": len([d for d in formatted_docs if d["status"] == "verified"]),
            "pending_review": len([d for d in formatted_docs if d["status"] == "pending_review"]),
            "suspicious": len([d for d in formatted_docs if d["status"] == "suspicious"])
        }
        
        return jsonify({
            "verifier_id": verifier_id,
            "verifier_name": verifier.get("name", ""),
            "institution": verifier.get("institution", ""),
            "total_documents": len(formatted_docs),
            "status_summary": status_summary,
            "documents": formatted_docs
        }), 200
        
    except Exception as e:
        print(f"❌ Error getting verifier documents: {str(e)}")
        return jsonify({
            "error": "Failed to retrieve documents",
            "details": str(e)
        }), 500

@verifier_bp.route("/verify/<document_id>", methods=["POST"])
def verify_document_by_id(document_id):
    """
    Verify a specific document by ID (for cross-verification)
    """
    try:
        # Get verifier ID from request
        verifier_id = request.json.get('verifier_id')
        if not verifier_id:
            return jsonify({"error": "Verifier ID is required"}), 400
        
        # Validate verifier exists
        verifier = get_verifier(mongo, verifier_id)
        if not verifier:
            return jsonify({"error": "Verifier not found"}), 404
        
        # Find the document
        document = mongo.db.documents.find_one({"_id": ObjectId(document_id)})
        if not document:
            return jsonify({"error": "Document not found"}), 404
        
        # Re-analyze document for new suspicion score
        document_path = document.get('source', '')
        ocr_text = document.get('ocr_data', {}).get('extracted_text', '')
        
        if document_path and ocr_text:
            doc_analysis = process_document(document_path, ocr_text)
            new_suspicion_score = doc_analysis.get('suspicion_score', 0.5)
        else:
            # Fallback if we can't re-analyze
            new_suspicion_score = 0.5
        
        # Update document with new verifier
        mongo.db.documents.update_one(
            {"_id": ObjectId(document_id)},
            {
                "$addToSet": {"verified_by": ObjectId(verifier_id)},
                "$set": {"ai_score": new_suspicion_score}
            }
        )
        
        # Update verifier's documents list
        mongo.db.verifiers.update_one(
            {"_id": ObjectId(verifier_id)},
            {"$addToSet": {"documents": ObjectId(document_id)}}
        )
        
        return jsonify({
            "message": "Document re-verified successfully",
            "document_id": document_id,
            "verifier_id": verifier_id,
            "new_suspicion_score": new_suspicion_score,
            "verification_timestamp": datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        print(f"❌ Error in document verification: {str(e)}")
        return jsonify({
            "error": "Failed to verify document",
            "details": str(e)
        }), 500

@verifier_bp.route("/analysis/<document_id>", methods=["GET"])
def get_document_analysis(document_id):
    """
    Get detailed analysis for a specific document (for frontend dialog)
    """
    try:
        # Find the document
        document = mongo.db.documents.find_one({"_id": ObjectId(document_id)})
        if not document:
            return jsonify({"error": "Document not found"}), 404
        
        # Get detailed analysis data
        analysis_data = {
            "document_id": document_id,
            "filename": document.get("metaData", {}).get("original_filename", "Unknown"),
            "file_path": document.get("source", ""),
            "verification_status": document.get("metaData", {}).get("verification_status", "unknown"),
            "hash_verified": document.get("status") == "verified",
            "suspicion_score": document.get("ai_score", 0.0),
            "status": document.get("status", "unknown"),
            "analysis_explanation": document.get("metaData", {}).get("verification_notes", "No analysis available"),
            "ocr_data": document.get("ocr_data", {}).get("extracted_text", ""),
            "issue_time": document.get("issue_time"),
            "verified_by": len(document.get("verified_by", [])),
            "existing_issuer": str(document.get("issuer_id")) if document.get("issuer_id") else None,
            "hash": document.get("hash", "Not generated")
        }
        
        return jsonify({
            "success": True,
            "analysis": analysis_data
        }), 200
        
    except Exception as e:
        print(f"❌ Error getting document analysis: {str(e)}")
        return jsonify({
            "error": "Failed to get analysis",
            "details": str(e)
        }), 500
