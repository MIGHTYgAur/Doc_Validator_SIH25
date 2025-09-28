import React, { useState, useEffect } from 'react';
import ApiService from '../services/ApiService';

const AnalysisDialog = ({ isOpen, onClose, documentId }) => {
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (isOpen && documentId) {
      fetchAnalysis();
    }
  }, [isOpen, documentId]);

  const fetchAnalysis = async () => {
    setLoading(true);
    setError(null);
    try {
      console.log('🔍 Fetching analysis for document:', documentId);
      const response = await ApiService.getDocumentAnalysis(documentId);
      console.log('📊 Analysis response:', response);
      
      if (response && response.analysis) {
        setAnalysis(response.analysis);
      } else {
        setError('No analysis data received');
      }
    } catch (err) {
      console.error('❌ Analysis fetch error:', err);
      setError(err.message || 'Failed to load analysis');
    } finally {
      setLoading(false);
    }
  };

  const getSuspicionColor = (score) => {
    if (score <= 0.2) return 'text-green-600';
    if (score <= 0.5) return 'text-yellow-600';
    if (score <= 0.8) return 'text-orange-600';
    return 'text-red-600';
  };

  const getSuspicionBg = (score) => {
    if (score <= 0.2) return 'bg-green-100';
    if (score <= 0.5) return 'bg-yellow-100';
    if (score <= 0.8) return 'bg-orange-100';
    return 'bg-red-100';
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'verified':
        return '✅';
      case 'suspicious':
        return '⚠️';
      case 'rejected':
        return '❌';
      default:
        return '❓';
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="bg-blue-600 text-white p-6 flex justify-between items-center">
          <h2 className="text-xl font-bold">Document Analysis</h2>
          <button
            onClick={onClose}
            className="text-white hover:text-gray-200 text-2xl font-bold"
            aria-label="Close"
          >
            ×
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-120px)]">
          {loading && (
            <div className="flex items-center justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              <span className="ml-2">Loading analysis...</span>
            </div>
          )}

          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
              {error}
            </div>
          )}

          {analysis && (
            <div className="space-y-6">
              {/* Document Overview */}
              <div className="bg-gray-50 rounded-lg p-4">
                <h3 className="font-semibold text-lg mb-3">Document Overview</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <p><strong>Filename:</strong> {analysis.filename}</p>
                    {/* <p><strong>Document ID:</strong> {analysis.document_id}</p> */}
                    <p><strong>Verified Count:</strong> {analysis.verified_by}</p>
                  </div>
                  <div>
                    <p><strong>Issue Time:</strong> {analysis.issue_time ? new Date(analysis.issue_time).toLocaleString() : 'N/A'}</p>
                    {/* <p><strong>Hash:</strong> <code className="text-xs bg-gray-200 px-1 rounded">{analysis.hash.substring(0, 16)}...</code></p> */}
                  </div>
                </div>
              </div>

              {/* Document Preview */}
              {analysis.file_path && (
                <div className="bg-white border rounded-lg p-4">
                  <h3 className="font-semibold text-lg mb-3">Document Preview</h3>
                  <div className="flex justify-center">
                    <div className="max-w-full">
                      <img 
                        src={`${analysis.file_path}`}
                        alt="Document Preview"
                        className="max-w-full max-h-96 object-contain border rounded shadow-sm"
                        onError={(e) => {
                          e.target.style.display = 'none';
                          e.target.nextSibling.style.display = 'block';
                        }}
                      />
                      <div className="hidden text-center p-8 bg-gray-100 rounded border-2 border-dashed">
                        <p className="text-gray-500">📄 Preview not available</p>
                        <p className="text-sm text-gray-400 mt-1">File: {analysis.filename}</p>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Verification Status */}
              <div className="bg-white border rounded-lg p-4">
                <h3 className="font-semibold text-lg mb-3">Verification Status</h3>
                <div className="flex items-center space-x-4 mb-4">
                  <div className={`px-3 py-2 rounded-full ${getSuspicionBg(analysis.suspicion_score)}`}>
                    <span className="font-medium">
                      {getStatusIcon(analysis.status)} {analysis.status.toUpperCase()}
                    </span>
                  </div>
                  <div className="flex items-center">
                    <span className="text-gray-600 mr-2">Suspicion Score:</span>
                    <span className={`font-bold text-lg ${getSuspicionColor(analysis.suspicion_score)}`}>
                      {(analysis.suspicion_score * 100).toFixed(1)}%
                    </span>
                  </div>
                </div>

                {analysis.hash_verified && (
                  <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-3">
                    <div className="flex items-center">
                      <span className="mr-2">🔒</span>
                      <strong>Hash Verified:</strong> This document exists in the database with matching hash
                    </div>
                  </div>
                )}

                <div className="bg-blue-50 border border-blue-200 rounded p-3">
                  <h4 className="font-medium mb-2">Analysis Notes:</h4>
                  <p className="text-gray-700">{analysis.analysis_explanation}</p>
                </div>
              </div>

              {/* OCR Data */}
              {analysis.ocr_data && Object.keys(analysis.ocr_data).length > 0 && (
                <div className="bg-white border rounded-lg p-4">
                  <h3 className="font-semibold text-lg mb-3">Extracted Text (OCR)</h3>
                  <div className="bg-gray-50 rounded p-3 max-h-60 overflow-y-auto">
                    <pre className="whitespace-pre-wrap text-sm text-gray-700">
                      {analysis.ocr_data || 'No text extracted'}
                    </pre>
                  </div>
                  {analysis.ocr_data.confidence && (
                    <div className="mt-2 text-sm text-gray-600">
                      <strong>OCR Confidence:</strong> {analysis.ocr_data.confidence}%
                    </div>
                  )}
                </div>
              )}

              {/* Security Information */}
              <div className="bg-white border rounded-lg p-4">
                <h3 className="font-semibold text-lg mb-3">Security Analysis</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <h4 className="font-medium mb-2">Hash Verification</h4>
                    <div className={`p-3 rounded ${analysis.hash_verified ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}`}>
                      {analysis.hash_verified ? (
                        <div className="flex items-center">
                          <span className="mr-2">✅</span>
                          Document hash found in database
                        </div>
                      ) : (
                        <div className="flex items-center">
                          <span className="mr-2">⚠️</span>
                          Document not found in hash database
                        </div>
                      )}
                    </div>
                  </div>
                  <div>
                    <h4 className="font-medium mb-2">Risk Assessment</h4>
                    <div className={`p-3 rounded ${getSuspicionBg(analysis.suspicion_score)}`}>
                      <div className="flex items-center">
                        <span className="mr-2">
                          {analysis.suspicion_score <= 0.2 ? '🟢' : 
                           analysis.suspicion_score <= 0.5 ? '🟡' : 
                           analysis.suspicion_score <= 0.8 ? '🟠' : '🔴'}
                        </span>
                        {analysis.suspicion_score <= 0.2 ? 'Low Risk' : 
                         analysis.suspicion_score <= 0.5 ? 'Medium Risk' : 
                         analysis.suspicion_score <= 0.8 ? 'High Risk' : 'Very High Risk'}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="bg-gray-50 px-6 py-4 flex justify-end">
          <button
            onClick={onClose}
            className="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default AnalysisDialog;