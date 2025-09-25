import { useState } from 'react';
import { CheckCircle, AlertCircle } from 'lucide-react';
import DocumentUpload from './docUpload';

const VerifierVerifyDocument = ({ onVerify }) => {
  const [verificationResult, setVerificationResult] = useState(null);
  
  const handleVerify = async (file) => {
    const result = await onVerify(file);
    setVerificationResult(result);
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div className="bg-white rounded-xl shadow-lg p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Verify Document</h2>
        <DocumentUpload 
          onUpload={handleVerify} 
          title="Upload Document to Verify" 
        />
      </div>

      {verificationResult && (
        <div className={`bg-white rounded-xl shadow-lg p-6 border-l-4 ${
          verificationResult.isValid ? 'border-green-500' : 'border-red-500'
        }`}>
          <div className="flex items-center space-x-2 mb-4">
            {verificationResult.isValid ? (
              <CheckCircle className="h-6 w-6 text-green-600" />
            ) : (
              <AlertCircle className="h-6 w-6 text-red-600" />
            )}
            <h3 className={`text-lg font-semibold ${
              verificationResult.isValid ? 'text-green-800' : 'text-red-800'
            }`}>
              {verificationResult.isValid ? 'Document Verified' : 'Verification Failed'}
            </h3>
          </div>
          
          <div className="space-y-2">
            <p><strong>Document:</strong> {verificationResult.title}</p>
            <p><strong>Issuer:</strong> {verificationResult.issuer}</p>
            <p><strong>Issue Date:</strong> {verificationResult.issueDate}</p>
            {verificationResult.validUntil && (
              <p><strong>Valid Until:</strong> {verificationResult.validUntil}</p>
            )}
            <p><strong>Status:</strong> 
              <span className={`ml-1 px-2 py-1 rounded text-xs ${
                verificationResult.isValid ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
              }`}>
                {verificationResult.status}
              </span>
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default VerifierVerifyDocument;