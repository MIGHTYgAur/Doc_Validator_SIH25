from database import mongo
from flask import Blueprint, request, jsonify
from models.institute_model import create_institute, get_institute
from datetime import datetime

institute_bp = Blueprint("institutes", __name__)

@institute_bp.route("/register", methods=["POST"])
def register_institute():
    try:
        data = request.json
        
        # Validate required fields
        if not data.get("name"):
            return jsonify({"success": False, "error": "Institute name is required"}), 400
        if not data.get("type"):
            return jsonify({"success": False, "error": "Institute type is required"}), 400
        if not data.get("secret_key"):
            return jsonify({"success": False, "error": "Secret key is required"}), 400
        
        # Check if institute name already exists
        existing_institute = mongo.db.institutes.find_one({"name": data.get("name")})
        if existing_institute:
            return jsonify({"success": False, "error": "Institute with this name already exists"}), 409
        
        institute = {
            "name": data.get("name"),
            "type": data.get("type"),        # school, university, etc.
            "secret_key": data.get("secret_key"),  # optional, for HMAC
            "created_at": datetime.utcnow()
        }
        
        institute_id = create_institute(mongo, institute)
        
        return jsonify({
            "success": True,
            "message": "Institute registered successfully",
            "institute_id": str(institute_id),
            "institute_name": data.get("name")
        }), 201
        
    except Exception as e:
        print(f"❌ Error registering institute: {e}")
        return jsonify({"success": False, "error": "Failed to register institute"}), 500
  

@institute_bp.route("/<institute_id>", methods=["GET"])
def get_institute_by_id(institute_id):
    return get_institute(mongo, institute_id)

@institute_bp.route("/list", methods=["GET"])
def list_institutes():
    """Get list of all registered institutes for dropdown selection"""
    try:
        institutes = list(mongo.db.institutes.find(
            {}, 
            {"name": 1, "type": 1, "_id": 1}  # Only return necessary fields
        ))
        
        # Format for frontend dropdown
        institute_options = [
            {
                "id": str(institute["_id"]),
                "name": institute["name"],
                "type": institute.get("type", "")
            }
            for institute in institutes
        ]
        
        return jsonify({
            "success": True,
            "institutes": institute_options
        }), 200
        
    except Exception as e:
        print(f"❌ Error fetching institutes: {e}")
        return jsonify({
            "success": False, 
            "error": "Failed to fetch institutes"
        }), 500

# create_institute(mongo, data = {
#     "name": "VJTI",
#     "type": "university",
#     "secret_key": "supersecretkey"
# })