from flask import Flask
from flask_cors import CORS
from database import initialize_db
import config
import dotenv
dotenv.load_dotenv()

app = Flask(__name__)
app.config["MONGO_URI"] = config.MONGO_URI
app.config["CLOUDINARY_CLOUD_NAME"] = config.CLOUDINARY_CLOUD_NAME
app.config["CLOUDINARY_API_KEY"] = config.CLOUDINARY_API_KEY
app.config["CLOUDINARY_API_SECRET"] = config.CLOUDINARY_API_SECRET
app.config["PORT"] = config.PORT

CORS(app)
# Initialize database
initialize_db(app)

#test
@app.route('/')
def home(): 
    return "Backend is running!"

#Import and register routes
from routes.document_routes import doc_bp
app.register_blueprint(doc_bp, url_prefix="/api/documents")



if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=config.PORT)

