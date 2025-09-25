import { useState } from 'react';
import UserAuthForm from './userReg';
import InstituteRegisterForm from './InstituteReg';
import IssuerIssueDocument from './IssuerView';
import IssuerViewDocuments from './IssuerView';
import VerifierVerifyDocument from './VerifierForm';
import VerifierViewDocuments from './VerifierView';
import { Building } from 'lucide-react';

const DocumentAuthSystemDemo = () => {
  const [currentView, setCurrentView] = useState('login');
  const [isLogin, setIsLogin] = useState(true);

  // Sample data for demonstration
  const sampleIssuedDocs = [
    {
      title: "Bachelor's Degree Certificate",
      recipient: "John Doe",
      issueDate: "2024-05-15",
      validUntil: "2029-05-15",
      status: "active",
      description: "Computer Science Degree"
    },
    {
      title: "Employment Verification",
      recipient: "Jane Smith",
      issueDate: "2024-09-01",
      status: "active",
      description: "Software Engineer Position"
    }
  ];

  const sampleVerifiedDocs = [
    {
      title: "Master's Degree",
      issuer: "University of Technology",
      verificationDate: "2024-09-20",
      issueDate: "2023-06-10",
      isValid: true,
      notes: "Successfully verified through blockchain"
    },
    {
      title: "Professional Certificate",
      issuer: "Tech Institute",
      verificationDate: "2024-09-18",
      issueDate: "2024-01-15",
      isValid: false,
      notes: "Document signature could not be verified"
    }
  ];

  const renderCurrentView = () => {
    switch (currentView) {
      case 'login':
        return (
          <UserAuthForm
            isLogin={isLogin}
            onToggle={() => setIsLogin(!isLogin)}
            onSubmit={(data) => console.log('Auth submitted:', data)}
          />
        );
      case 'institute-register':
        return (
          <div className="min-h-screen bg-gradient-to-br from-green-50 to-emerald-100 flex items-center justify-center p-4">
            <InstituteRegisterForm
              onSubmit={(data) => console.log('Institute registered:', data)}
            />
          </div>
        );
      case 'issuer-issue':
        return (
          <div className="min-h-screen bg-gray-50 p-4">
            <IssuerIssueDocument
              onIssue={(data) => console.log('Document issued:', data)}
            />
          </div>
        );
      case 'issuer-view':
        return (
          <div className="min-h-screen bg-gray-50 p-4">
            <IssuerViewDocuments documents={sampleIssuedDocs} />
          </div>
        );
      case 'verifier-verify':
        return (
          <div className="min-h-screen bg-gray-50 p-4">
            <VerifierVerifyDocument
              onVerify={(file) => ({
                isValid: true,
                title: "Sample Certificate",
                issuer: "Demo University",
                issueDate: "2024-01-15",
                validUntil: "2029-01-15",
                status: "Valid and Verified"
              })}
            />
          </div>
        );
      case 'verifier-view':
        return (
          <div className="min-h-screen bg-gray-50 p-4">
            <VerifierViewDocuments verifiedDocuments={sampleVerifiedDocs} />
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen">
      {/* Navigation */}
      <div className="bg-white shadow-sm border-b p-4">
        <div className="max-w-4xl mx-auto flex flex-wrap gap-2">
          <button
            onClick={() => { setCurrentView('login'); setIsLogin(true); }}
            className={`px-4 py-2 rounded-lg transition-colors ${
              currentView === 'login' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Login
          </button>
          <button
            onClick={() => setCurrentView('institute-register')}
            className={`px-4 py-2 rounded-lg transition-colors ${
              currentView === 'institute-register' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Institute Register
          </button>
          <button
            onClick={() => setCurrentView('issuer-issue')}
            className={`px-4 py-2 rounded-lg transition-colors ${
              currentView === 'issuer-issue' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Issue Document
          </button>
          <button
            onClick={() => setCurrentView('issuer-view')}
            className={`px-4 py-2 rounded-lg transition-colors ${
              currentView === 'issuer-view' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            View Issued
          </button>
          <button
            onClick={() => setCurrentView('verifier-verify')}
            className={`px-4 py-2 rounded-lg transition-colors ${
              currentView === 'verifier-verify' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Verify Document
          </button>
          <button
            onClick={() => setCurrentView('verifier-view')}
            className={`px-4 py-2 rounded-lg transition-colors ${
              currentView === 'verifier-view' ? 'bg-blue-600 text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            View Verified
          </button>
        </div>
      </div>

      {/* Current View */}
      {renderCurrentView()}
    </div>
  );
};

export default DocumentAuthSystemDemo;