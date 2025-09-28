import cloudinary
import cloudinary.uploader
import cloudinary.api
from werkzeug.utils import secure_filename
import os
import config

# Configure Cloudinary
cloudinary.config(
    cloud_name=config.CLOUDINARY_CLOUD_NAME,
    api_key=config.CLOUDINARY_API_KEY,
    api_secret=config.CLOUDINARY_API_SECRET
)

def upload_document(file, folder="documents"):
    """
    Upload a document to Cloudinary
    
    Args:
        file: File object from Flask request
        folder: Folder name in Cloudinary (default: 'documents')
    
    Returns:
        dict: Contains secure_url, public_id, and other metadata
    """
    try:
        # Secure the filename
        filename = secure_filename(file.filename)
        
        # Upload to Cloudinary
        result = cloudinary.uploader.upload(
            file,
            folder=folder,
            resource_type="auto",  # Automatically detect file type
            public_id=f"{filename}_{os.urandom(8).hex()}",  # Unique identifier
            overwrite=False,
            transformation=[
                {"quality": "auto"},  # Optimize quality
                {"fetch_format": "auto"}  # Optimize format
            ]
        )
        
        return {
            "success": True,
            "secure_url": result.get("secure_url"),
            "public_id": result.get("public_id"),
            "format": result.get("format"),
            "resource_type": result.get("resource_type"),
            "bytes": result.get("bytes"),
            "width": result.get("width"),
            "height": result.get("height"),
            "created_at": result.get("created_at")
        }
        
    except Exception as e:
        print(f"❌ Cloudinary upload error: {e}")
        return {
            "success": False,
            "error": str(e)
        }

def delete_document(public_id):
    """
    Delete a document from Cloudinary
    
    Args:
        public_id: The public ID of the document to delete
    
    Returns:
        dict: Success status and result
    """
    try:
        result = cloudinary.uploader.destroy(public_id)
        return {
            "success": True,
            "result": result
        }
    except Exception as e:
        print(f"❌ Cloudinary delete error: {e}")
        return {
            "success": False,
            "error": str(e)
        }

def get_document_url(public_id, transformation=None):
    """
    Get a transformed URL for a document
    
    Args:
        public_id: The public ID of the document
        transformation: Optional transformation parameters
    
    Returns:
        str: The transformed URL
    """
    try:
        if transformation:
            return cloudinary.CloudinaryImage(public_id).build_url(transformation=transformation)
        else:
            return cloudinary.CloudinaryImage(public_id).build_url()
    except Exception as e:
        print(f"❌ Cloudinary URL generation error: {e}")
        return None

def upload_temp_file(file_path, folder="temp"):
    """
    Upload a temporary file to Cloudinary (for OCR processing)
    
    Args:
        file_path: Path to the temporary file
        folder: Folder name in Cloudinary
    
    Returns:
        dict: Upload result
    """
    try:
        result = cloudinary.uploader.upload(
            file_path,
            folder=folder,
            resource_type="auto"
        )
        
        return {
            "success": True,
            "secure_url": result.get("secure_url"),
            "public_id": result.get("public_id")
        }
        
    except Exception as e:
        print(f"❌ Cloudinary temp upload error: {e}")
        return {
            "success": False,
            "error": str(e)
        }