import { useState, useEffect } from 'react';
import { Upload, FileText, Plus, User, LogOut, CheckCircle, Clock, AlertCircle } from 'lucide-react';
import ApiService from '../services/ApiService';

const IssuerHomepage = ({ user, onLogout }) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [documentType, setDocumentType] = useState('certificate');
  const [isUploading, setIsUploading] = useState(false);
  const [uploadedDocs, setUploadedDocs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Load documents on component mount
  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    try {
      setLoading(true);
      const response = await ApiService.getIssuerDocuments(user.id);
      setUploadedDocs(response.documents || []);
    } catch (err) {
      console.error('Failed to load documents:', err);
      setError('Failed to load documents');
    } finally {
      setLoading(false);
    }
  };

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    setSelectedFile(file);
    setError(null);
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!selectedFile) return;

    setIsUploading(true);
    setError(null);
    
    try {
      const response = await ApiService.issuerUpload(selectedFile, user.id, documentType);
      
      // Add new document to the list
      const newDoc = {
        document_id: response.document_id,
        filename: response.filename,
        document_type: documentType,
        issue_time: response.upload_timestamp,
        status: response.status,
        suspicion_score: response.suspicion_score,
        ocr_text_preview: response.ocr_text_preview
      };
      
      setUploadedDocs([newDoc, ...uploadedDocs]);
      setSelectedFile(null);
      
      // Reset form
      document.getElementById('file-input').value = '';
      
      alert('Document uploaded successfully!');
    } catch (err) {
      console.error('Upload failed:', err);
      setError('Failed to upload document. Please try again.');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center mr-3">
                <FileText className="w-5 h-5 text-blue-600" />
              </div>
              <h1 className="text-xl font-semibold text-gray-900">Document Issuer Portal</h1>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="flex items-center text-sm text-gray-600">
                <User className="w-4 h-4 mr-2" />
                <span>{user.name}</span>
              </div>
              <button
                onClick={onLogout}
                className="flex items-center text-sm text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md hover:bg-gray-100"
              >
                <LogOut className="w-4 h-4 mr-2" />
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Upload Form */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <Plus className="w-5 h-5 mr-2 text-blue-600" />
                Issue New Document
              </h2>
              
              <form onSubmit={handleUpload} className="space-y-4">
                {/* Document Type */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Document Type
                  </label>
                  <select
                    value={documentType}
                    onChange={(e) => setDocumentType(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="certificate">Certificate</option>
                    <option value="diploma">Diploma</option>
                    <option value="transcript">Transcript</option>
                    <option value="license">License</option>
                    <option value="other">Other</option>
                  </select>
                </div>

                {/* File Upload */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Upload Document
                  </label>
                  <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-blue-400 transition-colors">
                    <Upload className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                    <input
                      id="file-input"
                      type="file"
                      onChange={handleFileSelect}
                      accept=".pdf,.jpg,.jpeg,.png"
                      className="hidden"
                    />
                    <label htmlFor="file-input" className="cursor-pointer">
                      <span className="text-blue-600 hover:text-blue-700 font-medium">
                        Click to upload
                      </span>
                      <span className="text-gray-500"> or drag and drop</span>
                    </label>
                    <p className="text-xs text-gray-500 mt-1">
                      PDF, PNG, JPG up to 16MB
                    </p>
                  </div>
                  
                  {selectedFile && (
                    <div className="mt-2 p-2 bg-blue-50 border border-blue-200 rounded-md">
                      <p className="text-sm text-blue-800">
                        Selected: {selectedFile.name}
                      </p>
                    </div>
                  )}
                </div>

                {/* Submit Button */}
                <button
                  type="submit"
                  disabled={!selectedFile || isUploading}
                  className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
                >
                  {isUploading ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      Processing...
                    </>
                  ) : (
                    <>
                      <Upload className="w-4 h-4 mr-2" />
                      Issue Document
                    </>
                  )}
                </button>
              </form>
            </div>
          </div>

          {/* Documents List */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow">
              <div className="px-6 py-4 border-b border-gray-200">
                <h2 className="text-lg font-semibold text-gray-900 flex items-center">
                  <FileText className="w-5 h-5 mr-2 text-gray-600" />
                  Issued Documents ({uploadedDocs.length})
                </h2>
              </div>
              
              <div className="p-6">
                {error && (
                  <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md flex items-center">
                    <AlertCircle className="w-5 h-5 text-red-600 mr-2" />
                    <span className="text-red-800">{error}</span>
                  </div>
                )}
                
                {loading ? (
                  <div className="text-center py-8">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-3"></div>
                    <p className="text-gray-500">Loading documents...</p>
                  </div>
                ) : uploadedDocs.length === 0 ? (
                  <div className="text-center py-8">
                    <FileText className="w-12 h-12 text-gray-300 mx-auto mb-3" />
                    <p className="text-gray-500">No documents issued yet</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {uploadedDocs.map((doc) => (
                      <div key={doc.document_id} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center">
                            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center mr-3">
                              <FileText className="w-5 h-5 text-blue-600" />
                            </div>
                            <div>
                              <h3 className="font-medium text-gray-900">{doc.filename}</h3>
                              <div className="flex items-center text-sm text-gray-500 mt-1">
                                <span className="capitalize">{doc.document_type || doc.type}</span>
                                <span className="mx-2">•</span>
                                <span>{new Date(doc.issue_time || doc.uploadDate).toLocaleDateString()}</span>
                              </div>
                              {/* {doc.ocr_text_preview && (
                                <p className="text-xs text-gray-400 mt-1 truncate">
                                  OCR: {doc.ocr_text_preview}
                                </p>
                              )} */}
                            </div>
                          </div>
                          <div className="flex items-center space-x-3">
                            {/* Suspicion Score */}
                            <div className="text-sm text-gray-600">
                              Score: <span className="font-medium text-green-600">{doc.suspicion_score || 0.0}</span>
                            </div>
                            {/* Status Badge */}
                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                              (doc.status || 'verified') === 'verified' 
                                ? 'bg-green-100 text-green-800' 
                                : 'bg-yellow-100 text-yellow-800'
                            }`}>
                              <CheckCircle className="w-3 h-3 mr-1" />
                              {(doc.status || 'verified').charAt(0).toUpperCase() + (doc.status || 'verified').slice(1)}
                            </span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default IssuerHomepage;