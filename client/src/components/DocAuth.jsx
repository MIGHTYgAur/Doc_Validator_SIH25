import { useState } from 'react';
import { Shield, FileText, CheckCircle, Users, Building, ChevronDown, Menu, X } from 'lucide-react';
import UserAuthForm from './userReg';
import InstituteRegisterForm from './InstituteReg';
import LoginTypeModal from './loginType';
import LandingPage from './Landing';

const DocumentAuthSystem = () => {
  const [currentView, setCurrentView] = useState('landing');
  const [isLogin, setIsLogin] = useState(true);
  const [userType, setUserType] = useState('individual');
  const [showLoginModal, setShowLoginModal] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const handleLoginTypeSelect = (type) => {
    setUserType(type);
    setShowLoginModal(false);
    setCurrentView('login');
  };

  const renderCurrentView = () => {
    switch (currentView) {
      case 'landing':
        return <LandingPage />;
      case 'login':
        return (
          <UserAuthForm
            isLogin={isLogin}
            userType={userType}
            onToggle={() => setIsLogin(!isLogin)}
            onSubmit={(data) => console.log('Auth submitted:', data)}
          />
        );
      case 'institute-register':
        return (
          <InstituteRegisterForm
            onSubmit={(data) => console.log('Institute registered:', data)}
          />
        );
      default:
        return <LandingPage />;
    }
  };

  return (
    <div className="min-h-screen bg-white">
      {/* Navigation */}
      <nav className="bg-white shadow-lg border-b sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <div className="flex items-center">
              <Shield className="h-8 w-8 text-blue-600 mr-2" />
              <span className="text-xl font-bold text-gray-900">DocAuth</span>
            </div>

            {/* Desktop Navigation */}
            <div className="hidden lg:flex items-center space-x-6">
              <button
                onClick={() => setCurrentView('landing')}
                className={`px-3 py-2 rounded-lg transition-colors ${currentView === 'landing' ? 'bg-blue-100 text-blue-700' : 'text-gray-700 hover:text-blue-600'
                  }`}
              >
                Home
              </button>

              <div className="relative group">
                <button className="flex items-center px-3 py-2 text-gray-700 hover:text-blue-600 transition-colors">
                  Services <ChevronDown className="ml-1 h-4 w-4" />
                </button>
                <div className="absolute top-full left-0 mt-1 w-48 bg-white rounded-lg shadow-lg border opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200">
                  <button
                    onClick={() => setCurrentView('issue-document')}
                    className="block w-full text-left px-4 py-2 text-gray-700 hover:bg-gray-50 first:rounded-t-lg"
                  >
                    Issue Document
                  </button>
                  <button
                    onClick={() => setCurrentView('view-issued')}
                    className="block w-full text-left px-4 py-2 text-gray-700 hover:bg-gray-50"
                  >
                    View Issued
                  </button>
                  <button
                    onClick={() => setCurrentView('verify-document')}
                    className="block w-full text-left px-4 py-2 text-gray-700 hover:bg-gray-50"
                  >
                    Verify Document
                  </button>
                  <button
                    onClick={() => setCurrentView('view-verified')}
                    className="block w-full text-left px-4 py-2 text-gray-700 hover:bg-gray-50 last:rounded-b-lg"
                  >
                    View Verified
                  </button>
                </div>
              </div>

              <button
                onClick={() => setCurrentView('institute-register')}
                className="text-gray-700 hover:text-blue-600 px-3 py-2 transition-colors"
              >
                Register Institute
              </button>
            </div>

            {/* Desktop Auth Buttons */}
            <div className="hidden lg:flex items-center space-x-4">
              <button
                onClick={() => setShowLoginModal(true)}
                className="text-blue-600 hover:text-blue-800 font-medium px-4 py-2 transition-colors"
              >
                Login
              </button>
              <button
                onClick={() => {
                  setIsLogin(false);
                  setShowLoginModal(true);
                }}
                className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
              >
                Sign Up
              </button>
            </div>

            {/* Mobile menu button */}
            <button
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="lg:hidden p-2 rounded-md text-gray-700 hover:text-blue-600"
            >
              {isMobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
            </button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {isMobileMenuOpen && (
          <div className="lg:hidden border-t">
            <div className="px-4 py-2 space-y-2">
              <button
                onClick={() => {
                  setCurrentView('landing');
                  setIsMobileMenuOpen(false);
                }}
                className="block w-full text-left px-3 py-2 text-gray-700 hover:bg-gray-50 rounded-lg"
              >
                Home
              </button>
              <button
                onClick={() => {
                  setCurrentView('issue-document');
                  setIsMobileMenuOpen(false);
                }}
                className="block w-full text-left px-3 py-2 text-gray-700 hover:bg-gray-50 rounded-lg"
              >
                Issue Document
              </button>
              <button
                onClick={() => {
                  setCurrentView('view-issued');
                  setIsMobileMenuOpen(false);
                }}
                className="block w-full text-left px-3 py-2 text-gray-700 hover:bg-gray-50 rounded-lg"
              >
                View Issued
              </button>
              <button
                onClick={() => {
                  setCurrentView('verify-document');
                  setIsMobileMenuOpen(false);
                }}
                className="block w-full text-left px-3 py-2 text-gray-700 hover:bg-gray-50 rounded-lg"
              >
                Verify Document
              </button>
              <button
                onClick={() => {
                  setCurrentView('view-verified');
                  setIsMobileMenuOpen(false);
                }}
                className="block w-full text-left px-3 py-2 text-gray-700 hover:bg-gray-50 rounded-lg"
              >
                View Verified
              </button>
              <button
                onClick={() => {
                  setCurrentView('institute-register');
                  setIsMobileMenuOpen(false);
                }}
                className="block w-full text-left px-3 py-2 text-gray-700 hover:bg-gray-50 rounded-lg"
              >
                Register Institute
              </button>
              <div className="border-t pt-2 mt-2">
                <button
                  onClick={() => {
                    setShowLoginModal(true);
                    setIsMobileMenuOpen(false);
                  }}
                  className="block w-full text-left px-3 py-2 text-blue-600 hover:bg-blue-50 rounded-lg font-medium"
                >
                  Login
                </button>
                <button
                  onClick={() => {
                    setIsLogin(false);
                    setShowLoginModal(true);
                    setIsMobileMenuOpen(false);
                  }}
                  className="block w-full text-left px-3 py-2 bg-blue-600 text-white rounded-lg mt-2 hover:bg-blue-700"
                >
                  Sign Up
                </button>
              </div>
            </div>
          </div>
        )}
      </nav>

      {/* Main Content */}
      {renderCurrentView()}

      {/* Login Type Modal */}
      <LoginTypeModal
        isOpen={showLoginModal}
        onClose={() => setShowLoginModal(false)}
        onSelectType={handleLoginTypeSelect}
      />
    </div>
  );
};

export default DocumentAuthSystem;
