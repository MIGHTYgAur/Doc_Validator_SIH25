import pytesseract
from PIL import Image
import os
import io
import fitz  # PyMuPDF for PDF processing
import requests
import tempfile

# Configure Tesseract path (Windows-specific fix)
# Uncomment and modify the path if Tesseract is not in your PATH
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def pdf_to_images(pdf_path):
    """
    Convert PDF pages to PIL Images
    
    Args:
        pdf_path (str): Path to the PDF file
        
    Returns:
        list: List of PIL Image objects
    """
    try:
        doc = fitz.open(pdf_path)
        images = []
        
        for page_num in range(doc.page_count):
            # Get page
            page = doc[page_num]
            
            # Convert page to image (300 DPI for better OCR)
            pix = page.get_pixmap(matrix=fitz.Matrix(300/72, 300/72))
            
            # Convert to PIL Image
            img_data = pix.tobytes("ppm")
            img = Image.open(io.BytesIO(img_data))
            images.append(img)
        
        doc.close()
        print(f"📄 Converted {len(images)} pages from PDF to images")
        return images
        
    except Exception as e:
        print(f"❌ PDF conversion error: {str(e)}")
        return []

def extract_text(file_path):
    """
    Extract text from image or PDF using Tesseract OCR
    
    Args:
        file_path (str): Path to the image/PDF file or URL
        
    Returns:
        str: Extracted text or empty string if error
    """
    try:
        temp_file_path = None
        
        # Handle URL downloads
        if file_path.startswith(('http://', 'https://')):
            print(f"🌐 Downloading file from URL: {file_path}")
            response = requests.get(file_path, timeout=30)
            response.raise_for_status()
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".tmp") as temp_file:
                temp_file.write(response.content)
                temp_file_path = temp_file.name
            
            # Use the temporary file for processing
            working_file_path = temp_file_path
        else:
            # Local file
            if not os.path.exists(file_path):
                print(f"❌ OCR Error: File not found: {file_path}")
                return ""
            working_file_path = file_path
        
        print(f"🔤 Extracting text from: {working_file_path}")
        
        # Check file extension to determine processing method
        file_ext = working_file_path.lower()[-4:]
        if file_ext == '.pdf':
            # Handle PDF files
            print("📄 Processing PDF file...")
            images = pdf_to_images(working_file_path)
            
            if not images:
                print("❌ Failed to convert PDF to images")
                return ""
            
            # Extract text from all pages
            all_text = []
            for i, image in enumerate(images):
                print(f"🔤 Processing page {i+1}...")
                
                # Convert to RGB if necessary
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                
                # Extract text using Tesseract
                page_text = pytesseract.image_to_string(image, lang='eng')
                all_text.append(page_text.strip())
            
            # Combine all pages
            extracted_text = '\n\n'.join(all_text)
            
        else:
            # Handle image files (PNG, JPG, etc.)
            print("🖼️ Processing image file...")
            image = Image.open(working_file_path)
            
            # Convert to RGB if necessary (for better OCR results)
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Extract text using Tesseract
            extracted_text = pytesseract.image_to_string(image, config='--psm 6')
        
        print(f"✅ OCR completed. Extracted {len(extracted_text)} characters")
        
        # Clean up temporary file if we created one
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
                print(f"🗑️ Temporary OCR file cleaned up")
            except Exception as e:
                print(f"⚠️ Failed to clean up OCR temp file: {e}")
        
        return extracted_text.strip()
        
    except pytesseract.TesseractNotFoundError:
        error_msg = "❌ Tesseract OCR not found. Please install Tesseract OCR and add it to your PATH"
        print(error_msg)
        return f"ERROR: {error_msg}"
        
    except Exception as e:
        error_msg = f"❌ OCR Error: {str(e)}"
        print(error_msg)
        
        # Clean up temporary file if we created one
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except:
                pass
        
        return f"ERROR: {error_msg}"

def test_tesseract_installation():
    """
    Test if Tesseract is properly installed and accessible
    """
    try:
        version = pytesseract.get_tesseract_version()
        print(f"✅ Tesseract version: {version}")
        return True
    except pytesseract.TesseractNotFoundError:
        print("❌ Tesseract OCR not found!")
        return False
    except Exception as e:
        print(f"❌ Tesseract test error: {e}")
        return False

# Test the OCR functionality
if __name__ == "__main__":
    print("🧪 Testing OCR Service")
    print("=" * 30)
    
    # Test Tesseract installation
    if test_tesseract_installation():
        # Test with existing image
        test_file = "uploads/image.png"
        if os.path.exists(test_file):
            result = extract_text(test_file)
            print("\n📄 OCR Result:")
            print("-" * 30)
            print(result[:500] + "..." if len(result) > 500 else result)
        else:
            print(f"❌ Test file not found: {test_file}")
    else:
        print("Cannot test OCR - Tesseract not properly installed")