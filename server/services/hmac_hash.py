import hashlib
import hmac
import requests
from typing import Union

def hash_document(document_path: str, secret_key: str) -> str:
    """
    Calculate HMAC-SHA512 hash for a document.
    
    Args:
        document_path (str): File path or URL to the document
        secret_key (str): Secret key for HMAC (string format)
    
    Returns:
        str: HMAC-SHA512 hash in hexadecimal format
    
    Raises:
        Exception: If file cannot be read or hash cannot be calculated
    """
    try:
        # Read document content
        if document_path.startswith(('http://', 'https://')):
            # Handle URL
            response = requests.get(document_path, timeout=30)
            response.raise_for_status()
            document_content = response.content
        else:
            # Handle local file
            with open(document_path, 'rb') as file:
                document_content = file.read()
        
        # Convert secret key to bytes
        secret_bytes = secret_key.encode('utf-8')
        
        # Calculate HMAC-SHA512
        hmac_hash = hmac.new(
            secret_bytes, 
            document_content, 
            hashlib.sha512
        ).hexdigest()
        
        return hmac_hash
        
    except Exception as e:
        raise Exception(f"Error hashing document: {str(e)}")

# Usage examples:
if __name__ == "__main__":
    # Example 1: Local file
    try:
        hash_result = hash_document("uploads/sem1_marksheet.pdf", "your_secret_key")
        print(f"Document hash: {hash_result}")
    except Exception as e:
        print(f"Error: {e}")
    
    # # Example 2: URL
    # try:
    #     hash_result = hash_document("https://example.com/document.pdf", "your_secret_key")
    #     print(f"Document hash: {hash_result}")
    # except Exception as e:
    #     print(f"Error: {e}")