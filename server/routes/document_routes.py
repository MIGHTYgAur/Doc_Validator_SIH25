from flask import Blueprint, request, jsonify
from models.document_model import create_document, get_document
from services.ocr import extract_text
from services.watermark import add_watermark
# from services.process import process_document_complete_flow
from database import mongo
import os
doc_bp = Blueprint("documents", __name__)


@doc_bp.route("/register", methods=["POST"])
def register_document():
    data = request.form.to_dict()
    file = request.files.get("file")
    
    # Save uploaded file
    filepath = f"uploads/{file.filename}"
    file.save(filepath)
    
    # Extract OCR text
    ocr_text = extract_text(filepath)
    data["ocr_text"] = ocr_text
    
    # Add watermark
    watermark_text = f"{data.get('issued_by')}_{data.get('cert_id')}"
    add_watermark(filepath, watermark_text)
    data["watermark"] = watermark_text
    
    # Save to DB
    doc_id = create_document(mongo, data)
    return jsonify({"message": "Document registered", "doc_id": str(doc_id)}), 201

@doc_bp.route("/<doc_id>", methods=["GET"])
def get_doc(doc_id):
    doc = get_document(mongo, doc_id)
    if doc:
        doc["_id"] = str(doc["_id"])
        return jsonify(doc), 200
    return jsonify({"error": "Document not found"}), 404

@doc_bp.route("/verify/<doc_id>", methods=["GET"])
def verify_doc(doc_id):
    result = verify_document(mongo, doc_id)
    return jsonify(result), 200

@doc_bp.route("/process", methods=["POST"])
def process_document_complete():
    """
    Complete document processing endpoint with OCR, ML analysis, and validation
    """
    try:
        # Check if file is uploaded
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Validate file type
        allowed_extensions = {'.pdf', '.png', '.jpg', '.jpeg'}
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in allowed_extensions:
            return jsonify({"error": f"File type {file_ext} not supported. Allowed: {allowed_extensions}"}), 400
        
        # Create uploads directory if it doesn't exist
        uploads_dir = "uploads"
        if not os.path.exists(uploads_dir):
            os.makedirs(uploads_dir)
        
        # Save uploaded file
        filepath = os.path.join(uploads_dir, file.filename)
        file.save(filepath)
        
        # Get additional metadata from form
        metadata = {
            'issuer': request.form.get('issuer', ''),
            'document_type': request.form.get('document_type', 'certificate'),
            'expected_text': request.form.get('expected_text', ''),
        }
        
        print(f"🚀 Processing uploaded file: {filepath}")
        
        # Process the document using our complete flow
        processing_results = process_document_complete_flow(filepath)
        
        # Add metadata to results
        processing_results['metadata'] = metadata
        processing_results['original_filename'] = file.filename
        
        # Save processing results to database
        document_data = {
            'filename': file.filename,
            'filepath': filepath,
            'processing_results': processing_results,
            'metadata': metadata,
            'status': processing_results['status']
        }
        
        doc_id = create_document(mongo, document_data)
        processing_results['document_id'] = str(doc_id)
        
        # Return results
        if processing_results['status'] == 'completed':
            return jsonify({
                "message": "Document processed successfully",
                "document_id": str(doc_id),
                "results": processing_results
            }), 200
        else:
            return jsonify({
                "message": "Document processing completed with errors",
                "document_id": str(doc_id),
                "results": processing_results
            }), 206  # Partial Content
            
    except Exception as e:
        print(f"❌ Error in document processing endpoint: {str(e)}")
        return jsonify({
            "error": "Internal server error during document processing",
            "details": str(e)
        }), 500

@doc_bp.route("/test-process", methods=["GET"])
def test_process_existing():
    """
    Test endpoint to process an existing file
    """
    try:
        # Test with existing file
        test_file = "uploads/sem1_marksheet.pdf"
        
        if not os.path.exists(test_file):
            return jsonify({"error": f"Test file not found: {test_file}"}), 404
        
        print(f"🧪 Testing document processing with: {test_file}")
        
        # Process the document
        results = process_document_complete_flow(test_file)
        
        return jsonify({
            "message": "Test processing completed",
            "results": results
        }), 200
        
    except Exception as e:
        print(f"❌ Error in test processing: {str(e)}")
        return jsonify({
            "error": "Test processing failed",
            "details": str(e)
        }), 500
