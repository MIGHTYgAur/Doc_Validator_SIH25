from flask import Blueprint, request, jsonify
from models.document_model import create_document, get_document
# from services.ocr_service import extract_text
# from services.watermark_service import add_watermark
from database import mongo
doc_bp = Blueprint("documents", __name__)

@doc_bp.route("/register", methods=["POST"])
def register_document():
    data = request.form.to_dict()
    file = request.files.get("file")
    
    # Save uploaded file
    filepath = f"uploads/{file.filename}"
    file.save(filepath)
    
    # # Extract OCR text
    # ocr_text = extract_text(filepath)
    # data["ocr_text"] = ocr_text
    
    # # Add watermark
    # watermark_text = f"{data.get('issued_by')}_{data.get('cert_id')}"
    # add_watermark(filepath, watermark_text)
    # data["watermark"] = watermark_text
    
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
