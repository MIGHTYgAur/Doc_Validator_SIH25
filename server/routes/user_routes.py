from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from models.issuer_model import create_issuer, get_issuer_by_email
from models.verifier_model import create_verifier, get_verifier_by_email
from database import mongo

user_bp = Blueprint("users", __name__)

# Register route
@user_bp.route("/register", methods=["POST"])
def register_user():
    try:
        data = request.get_json()
        
        # Validate input data
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        name = data.get("name")
        email = data.get("email")
        password = data.get("password")
        role = data.get("role")  # "issuer" or "verifier"
        institution = data.get("institution")

        # Check required fields
        if not all([name, email, password, role]):
            return jsonify({"error": "All fields (name, email, password, role) are required"}), 400

        # Validate role
        if role not in ["issuer", "verifier"]:
            return jsonify({"error": "Role must be either 'issuer' or 'verifier'"}), 400

        # Hash password
        hashed_pw = generate_password_hash(password)

        # Create user based on role
        if role == "issuer":
            # Check if issuer already exists
            existing_issuer = get_issuer_by_email(mongo, email)
            if existing_issuer:
                return jsonify({"error": "Issuer with this email already exists"}), 400
            
            # Create new issuer
            user_id = create_issuer(mongo, {
                "name": name,
                "email": email,
                "password": hashed_pw,
                "institution": institution or ""
            })

        elif role == "verifier":
            # Check if verifier already exists
            existing_verifier = get_verifier_by_email(mongo, email)
            if existing_verifier:
                return jsonify({"error": "Verifier with this email already exists"}), 400
            
            # Create new verifier
            user_id = create_verifier(mongo, {
                "name": name,
                "email": email,
                "password": hashed_pw,
                "institution": institution or ""
            })

        return jsonify({
            "message": f"{role.capitalize()} registered successfully", 
            "id": str(user_id),
            "role": role
        }), 201

    except Exception as e:
        print(f"Error in register_user: {str(e)}")
        return jsonify({"error": "Internal server error occurred during registration"}), 500


# Login route
@user_bp.route("/login", methods=["POST"])
def login_user():
    try:
        data = request.get_json()
        
        # Validate input data
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        email = data.get("email")
        password = data.get("password")
        role = data.get("role")

        # Check required fields
        if not all([email, password, role]):
            return jsonify({"error": "Email, password, and role are required"}), 400

        # Validate role
        if role not in ["issuer", "verifier"]:
            return jsonify({"error": "Role must be either 'issuer' or 'verifier'"}), 400

        # Get user based on role
        user = None
        if role == "issuer":
            user = get_issuer_by_email(mongo, email)
        elif role == "verifier":
            user = get_verifier_by_email(mongo, email)

        # Check if user exists and password is correct
        if not user:
            return jsonify({"error": "User not found"}), 404
            
        if not check_password_hash(user["password"], password):
            return jsonify({"error": "Invalid password"}), 401

        # Create JWT token
        token = create_access_token(identity={
            "_id": str(user["_id"]),
            "email": user["email"],
            "role": role,
            "name": user.get("name", ""),
            "institution": user.get("institution", "")
        })

        return jsonify({
            "message": "Login successful",
            "access_token": token, 
            "role": role,
            "user": {
                "id": str(user["_id"]),
                "name": user.get("name", ""),
                "email": user["email"],
                "institution": user.get("institution", "")
            }
        }), 200

    except Exception as e:
        print(f"Error in login_user: {str(e)}")
        return jsonify({"error": "Internal server error occurred during login"}), 500
