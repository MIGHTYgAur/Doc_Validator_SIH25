import { Eye, FileText } from 'lucide-react';
import { useState } from 'react';


const IssuerViewDocuments = ({ documents = [] }) => {
  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-white rounded-xl shadow-lg p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Issued Documents</h2>
        
        <div className="space-y-4">
          {documents.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <FileText className="mx-auto h-12 w-12 mb-2" />
              <p>No documents issued yet</p>
            </div>
          ) : (
            documents.map((doc, index) => (
              <div key={index} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="font-semibold text-lg text-gray-900">{doc.title}</h3>
                    <p className="text-gray-600">Recipient: {doc.recipient}</p>
                    <p className="text-sm text-gray-500">Issued: {doc.issueDate}</p>
                    {doc.validUntil && <p className="text-sm text-gray-500">Valid Until: {doc.validUntil}</p>}
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className={`px-2 py-1 rounded-full text-xs ${
                      doc.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                    }`}>
                      {doc.status}
                    </span>
                    <button className="text-blue-600 hover:text-blue-800">
                      <Eye className="h-4 w-4" />
                    </button>
                  </div>
                </div>
                {doc.description && (
                  <p className="text-gray-700 mt-2">{doc.description}</p>
                )}
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};


export default IssuerViewDocuments;