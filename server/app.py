from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from database import initialize_db
from services.cloudinary_service import cloudinary
import config
import dotenv
import os
dotenv.load_dotenv()

app = Flask(__name__)
app.config["MONGO_URI"] = config.MONGO_URI
app.config["CLOUDINARY_CLOUD_NAME"] = config.CLOUDINARY_CLOUD_NAME
app.config["CLOUDINARY_API_KEY"] = config.CLOUDINARY_API_KEY
app.config["CLOUDINARY_API_SECRET"] = config.CLOUDINARY_API_SECRET
app.config["PORT"] = config.PORT

# JWT Configuration
app.config['JWT_SECRET_KEY'] = 'your-secret-string'  # Change this in production
jwt = JWTManager(app)

# File upload configuration
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize Cloudinary configuration
print("📸 Cloudinary configured for document storage")

CORS(app, origins="*", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"], 
     allow_headers=["Content-Type", "Authorization"])
# Initialize database
initialize_db(app)

# Health check routes
@app.route('/')
def home(): 
    return {"message": "Doc Validator Backend is running!", "status": "active"}

@app.route('/health')
def health_check():
    return {
        "status": "healthy",
        "storage": "Cloudinary",
        "max_file_size": f"{app.config['MAX_CONTENT_LENGTH'] / (1024*1024)}MB",
        "endpoints": {
            "issuer_upload": "/api/issuer/upload",
            "verifier_upload": "/api/verifier/upload"
        }
    }

# File serving is now handled by Cloudinary URLs
# No need for local file serving endpoint

#Import and register routes
from routes.document_routes import doc_bp
app.register_blueprint(doc_bp, url_prefix="/api/documents")

from routes.institute_route import institute_bp
app.register_blueprint(institute_bp, url_prefix="/api/institutes")

from routes.user_routes import user_bp
app.register_blueprint(user_bp, url_prefix="/api/users")


## issuer and verifier routes
from routes.issuer_routes import issuer_bp
app.register_blueprint(issuer_bp, url_prefix="/api/issuer")

from routes.verifier_routes import verifier_bp
app.register_blueprint(verifier_bp, url_prefix="/api/verifier")

if __name__ == "__main__":
    # Windows-friendly configuration to avoid socket issues
    app.run(
        debug=True, 
        host="127.0.0.1",  # Use localhost instead of 0.0.0.0 for Windows
        port=config.PORT,
        use_reloader=True,
        use_debugger=True,
        threaded=True
    )

