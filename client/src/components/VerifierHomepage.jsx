import { useState } from 'react';
import { Upload, Search, FileText, User, LogOut, CheckCircle, AlertTriangle, Clock, Shield } from 'lucide-react';

const VerifierHomepage = ({ user, onLogout }) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [isVerifying, setIsVerifying] = useState(false);
  const [verifiedDocs, setVerifiedDocs] = useState([
    {
      id: 1,
      name: 'University_Degree.pdf',
      uploadDate: '2025-01-15',
      suspicionScore: 0.2,
      status: 'verified',
      result: 'Document appears authentic'
    },
    {
      id: 2,
      name: 'Professional_License.jpg',
      uploadDate: '2025-01-14',
      suspicionScore: 0.7,
      status: 'suspicious',
      result: 'Potential alterations detected'
    }
  ]);

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    setSelectedFile(file);
  };

  const handleVerify = async (e) => {
    e.preventDefault();
    if (!selectedFile) return;

    setIsVerifying(true);
    
    // Mock verification delay
    setTimeout(() => {
      const suspicionScore = Math.random();
      const newDoc = {
        id: Date.now(),
        name: selectedFile.name,
        uploadDate: new Date().toISOString().split('T')[0],
        suspicionScore: suspicionScore,
        status: suspicionScore < 0.3 ? 'verified' : suspicionScore < 0.7 ? 'pending' : 'suspicious',
        result: suspicionScore < 0.3 
          ? 'Document appears authentic' 
          : suspicionScore < 0.7 
          ? 'Requires manual review'
          : 'Potential alterations detected'
      };
      
      setVerifiedDocs([newDoc, ...verifiedDocs]);
      setSelectedFile(null);
      setIsVerifying(false);
      
      // Reset form
      document.getElementById('verify-file-input').value = '';
    }, 3000);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'verified':
        return 'bg-green-100 text-green-800';
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      case 'suspicious':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'verified':
        return <CheckCircle className="w-3 h-3 mr-1" />;
      case 'pending':
        return <Clock className="w-3 h-3 mr-1" />;
      case 'suspicious':
        return <AlertTriangle className="w-3 h-3 mr-1" />;
      default:
        return <FileText className="w-3 h-3 mr-1" />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <div className="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center mr-3">
                <Shield className="w-5 h-5 text-green-600" />
              </div>
              <h1 className="text-xl font-semibold text-gray-900">Document Verifier Portal</h1>
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
          {/* Verification Form */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <Search className="w-5 h-5 mr-2 text-green-600" />
                Verify Document
              </h2>
              
              <form onSubmit={handleVerify} className="space-y-4">
                {/* File Upload */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Upload Document to Verify
                  </label>
                  <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-green-400 transition-colors">
                    <Upload className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                    <input
                      id="verify-file-input"
                      type="file"
                      onChange={handleFileSelect}
                      accept=".pdf,.jpg,.jpeg,.png"
                      className="hidden"
                    />
                    <label htmlFor="verify-file-input" className="cursor-pointer">
                      <span className="text-green-600 hover:text-green-700 font-medium">
                        Click to upload
                      </span>
                      <span className="text-gray-500"> or drag and drop</span>
                    </label>
                    <p className="text-xs text-gray-500 mt-1">
                      PDF, PNG, JPG up to 16MB
                    </p>
                  </div>
                  
                  {selectedFile && (
                    <div className="mt-2 p-2 bg-green-50 border border-green-200 rounded-md">
                      <p className="text-sm text-green-800">
                        Selected: {selectedFile.name}
                      </p>
                    </div>
                  )}
                </div>

                {/* Submit Button */}
                <button
                  type="submit"
                  disabled={!selectedFile || isVerifying}
                  className="w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
                >
                  {isVerifying ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      Analyzing...
                    </>
                  ) : (
                    <>
                      <Search className="w-4 h-4 mr-2" />
                      Verify Document
                    </>
                  )}
                </button>
              </form>

              {/* Info Box */}
              <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <h3 className="text-sm font-medium text-blue-900 mb-2">How it works:</h3>
                <ul className="text-xs text-blue-800 space-y-1">
                  <li>• Upload document for analysis</li>
                  <li>• AI checks for authenticity</li>
                  <li>• Get suspicion score (0-1)</li>
                  <li>• Review verification results</li>
                </ul>
              </div>
            </div>
          </div>

          {/* Verification Results */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow">
              <div className="px-6 py-4 border-b border-gray-200">
                <h2 className="text-lg font-semibold text-gray-900 flex items-center">
                  <FileText className="w-5 h-5 mr-2 text-gray-600" />
                  Verification History ({verifiedDocs.length})
                </h2>
              </div>
              
              <div className="p-6">
                {verifiedDocs.length === 0 ? (
                  <div className="text-center py-8">
                    <Shield className="w-12 h-12 text-gray-300 mx-auto mb-3" />
                    <p className="text-gray-500">No documents verified yet</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {verifiedDocs.map((doc) => (
                      <div key={doc.id} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50">
                        <div className="flex items-start justify-between">
                          <div className="flex items-start">
                            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center mr-3 mt-1">
                              <FileText className="w-5 h-5 text-green-600" />
                            </div>
                            <div className="flex-1">
                              <h3 className="font-medium text-gray-900">{doc.name}</h3>
                              <p className="text-sm text-gray-600 mt-1">{doc.result}</p>
                              <div className="flex items-center text-sm text-gray-500 mt-2">
                                <span>Verified on {doc.uploadDate}</span>
                                <span className="mx-2">•</span>
                                <span>Suspicion Score: {(doc.suspicionScore * 100).toFixed(1)}%</span>
                              </div>
                            </div>
                          </div>
                          <div className="flex flex-col items-end">
                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(doc.status)}`}>
                              {getStatusIcon(doc.status)}
                              {doc.status.charAt(0).toUpperCase() + doc.status.slice(1)}
                            </span>
                            {/* Suspicion Score Bar */}
                            <div className="w-16 mt-2">
                              <div className="bg-gray-200 rounded-full h-1.5">
                                <div 
                                  className={`h-1.5 rounded-full ${
                                    doc.suspicionScore < 0.3 ? 'bg-green-500' : 
                                    doc.suspicionScore < 0.7 ? 'bg-yellow-500' : 'bg-red-500'
                                  }`}
                                  style={{ width: `${doc.suspicionScore * 100}%` }}
                                ></div>
                              </div>
                            </div>
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

export default VerifierHomepage;