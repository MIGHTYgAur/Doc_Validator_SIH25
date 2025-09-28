const API_BASE_URL = 'http://127.0.0.1:5000/api';

class ApiService {
  // Generic API call method
  static async apiCall(endpoint, options = {}) {
    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('API call failed:', error);
      throw error;
    }
  }

  // File upload method
  static async uploadFile(endpoint, formData) {
    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('File upload failed:', error);
      throw error;
    }
  }

  // Health check
  static async healthCheck() {
    return this.apiCall('/health');
  }

  // Issuer APIs
  static async issuerUpload(file, issuerId, documentType = 'certificate') {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('issuer_id', issuerId);
    formData.append('document_type', documentType);

    return this.uploadFile('/issuer/upload', formData);
  }

  static async getIssuerDocuments(issuerId) {
    return this.apiCall(`/issuer/documents/${issuerId}`);
  }

  // Verifier APIs
  static async verifierUpload(file, verifierId, documentType = 'unknown') {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('verifier_id', verifierId);
    formData.append('document_type', documentType);

    return this.uploadFile('/verifier/upload', formData);
  }

  static async getVerifierDocuments(verifierId) {
    return this.apiCall(`/verifier/documents/${verifierId}`);
  }

  static async verifyDocumentById(documentId, verifierId) {
    return this.apiCall(`/verifier/verify/${documentId}`, {
      method: 'POST',
      body: JSON.stringify({ verifier_id: verifierId }),
    });
  }

  static async getDocumentAnalysis(documentId) {
    return this.apiCall(`/verifier/analysis/${documentId}`);
  }

  // Real User Authentication APIs
  static async registerUser(userData) {
    return this.apiCall('/users/register', {
      method: 'POST',
      body: JSON.stringify({
        name: userData.name,
        email: userData.email,
        password: userData.password,
        role: userData.userType, // userType -> role for backend
        institution: userData.institution
      }),
    });
  }

  static async loginUser(email, password, userType) {
    return this.apiCall('/users/login', {
      method: 'POST',
      body: JSON.stringify({
        email: email,
        password: password,
        role: userType // userType -> role for backend
      }),
    });
  }


  /* Institute APIs*/ 
  static async SubmitInstitute (formData){
      // Map form data to API expected format
      const apiData = {
        name: formData.name,
        type: formData.type,
        secret_key: formData.secretPin
      };
      return this.apiCall('/institutes/register', {
        method: 'POST',
        headers:{
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(apiData),
      })
    }

  static async getInstitutesList() {
    return this.apiCall('/institutes/list');
  }

}

export default ApiService;