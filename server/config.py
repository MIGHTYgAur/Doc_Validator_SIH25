import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB connection URI
MONGO_URI = os.environ.get('MONGO_URI')
# Cloudinary credentials from environment variables
CLOUDINARY_CLOUD_NAME = os.environ.get('CLOUDINARY_CLOUD_NAME')
CLOUDINARY_API_KEY = os.environ.get('CLOUDINARY_API_KEY')
CLOUDINARY_API_SECRET = os.environ.get('CLOUDINARY_API_SECRET')

# Server port
PORT = int(os.environ.get('PORT', 5000))  # Default to 5000 if not set

# Debug: Print loaded config (without sensitive data)
print(f"🔧 Config loaded:")
print(f"   MONGO_URI: {'✅ Set' if MONGO_URI else '❌ Missing'}")
print(f"   CLOUDINARY: {'✅ Set' if CLOUDINARY_CLOUD_NAME else '❌ Missing'}")
print(f"   PORT: {PORT}") 