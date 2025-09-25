import { CheckCircle, AlertCircle, Shield } from 'lucide-react';
import React from 'react';

const VerifierViewDocuments = ({ verifiedDocuments = [] }) => {
  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-white rounded-xl shadow-lg p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Verified Documents</h2>
        
        <div className="space-y-4">
          {verifiedDocuments.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <Shield className="mx-auto h-12 w-12 mb-2" />
              <p>No documents verified yet</p>
            </div>
          ) : (
            verifiedDocuments.map((doc, index) => (
              <div key={index} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="font-semibold text-lg text-gray-900">{doc.title}</h3>
                    <p className="text-gray-600">Issuer: {doc.issuer}</p>
                    <p className="text-sm text-gray-500">Verified: {doc.verificationDate}</p>
                    <p className="text-sm text-gray-500">Original Issue Date: {doc.issueDate}</p>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className={`px-2 py-1 rounded-full text-xs ${
                      doc.isValid ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                    }`}>
                      {doc.isValid ? 'Valid' : 'Invalid'}
                    </span>
                    {doc.isValid ? (
                      <CheckCircle className="h-4 w-4 text-green-600" />
                    ) : (
                      <AlertCircle className="h-4 w-4 text-red-600" />
                    )}
                  </div>
                </div>
                {doc.notes && (
                  <p className="text-gray-700 mt-2 text-sm bg-gray-50 p-2 rounded">{doc.notes}</p>
                )}
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default VerifierViewDocuments;