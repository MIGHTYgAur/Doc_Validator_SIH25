# 🛡️ Document Validator – Smart Digital Document Authentication  

## 🌟 Overview  
**Document Validator** is a digital authentication system to combat document forgery in education, employment, and identity verification. It combines **OCR, image-based fraud detection, and cryptographic hashing** to ensure documents are trustworthy.  

---

## 🎯 Problem  
- Rising cases of fake certificates and tampered documents  
- Lack of centralized, fast, and reliable verification  
- Manual checks are time-consuming and error-prone  

---

## ✨ Key Features  
- **Multi-role system**: Institutes (issuers), Verifiers, and Admins  
- **Cryptographic Hashing**: Detects tampering using HMAC-SHA512 hashing and encryption
- **OCR & AI Scoring**: Extracts text, checks quality, layout, and inconsistencies  
- **Suspicion Score**: Weighted analysis of fonts, logos, and clarity  
- **Cloud Storage**: Secure upload and storage (Cloudinary)  
- **Interactive Dashboard**: Upload, verify, and view results  

---

## 🔄 Workflow  

### 📤 Issuing Flow  
1. Institute registers → uploads document  
2. OCR extracts text → hash generated  
3. Document + metadata stored in DB with suspicion score = 0  

### 🔍 Verification Flow  
1. Verifier uploads document  
2. Hash compared with DB  
   - ✅ If match → authentic  
   - ❌ If mismatch → AI-based analysis → suspicion score shown  

---

## 🛠️ Technology Stack

- **Frontend**: React, TailwindCSS, React Router
- **Backend**: Flask, JWT, MongoDB Atlas
- **Processing**: Tesseract OCR, OpenCV, PyMuPDF, Pillow
- **Security**: HMAC, bcrypt, JWT
- **Storage**: Cloudinary

---

## 🔮 Future Enhancements

- **Blockchain Integration**: Immutable document records
- **Mobile Application**: Native iOS/Android apps
- **Advanced AI Models**: Deep learning for fraud detection
- **API Integration**: Third-party verification services
