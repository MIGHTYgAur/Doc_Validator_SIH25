import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate } from 'react-router-dom'
import { AuthService } from './services/AuthService'
import Login from './components/Login'
import IssuerHomepage from './components/IssuerHomepage'
import LandingPage from './components/Landing'
import VerifierHomepage from './components/VerifierHomepage'
import InstituteRegisterForm from './components/InstituteReg'
import ApiService from './services/ApiService.js'

// Landing page wrapper component to handle navigation
function LandingWrapper() {
  const navigate = useNavigate();

  const handleGetStarted = () => {
    navigate('/login');
  };

  const handleRegisterInstitute = () => {
    navigate('/register-institute');
  };

  return <LandingPage onGetStarted={handleGetStarted} onRegisterInstitute={handleRegisterInstitute} />;
}

// Institute registration wrapper
function InstituteRegWrapper() {
  const navigate = useNavigate();

  const handleBackToHome = () => {
    navigate('/');
  };

  const handleInstituteSubmit = async (formData) => {
    try {
      const response = await ApiService.SubmitInstitute(formData);
      if (response.success) {
        alert('Institute registered successfully!');
        navigate('/login');
      } else {
        alert('Institute registration failed: ' + response.error);
      }
    } catch (error) {
      console.error('Institute registration error:', error);
      alert('Institute registration failed: ' + error.message);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-md mx-auto">
        <button
          onClick={handleBackToHome}
          className="mb-4 text-blue-600 hover:text-blue-800 font-medium"
        >
          ← Back to Home
        </button>
        <InstituteRegisterForm onSubmit={handleInstituteSubmit} />
      </div>
    </div>
  );
}

function AppContent() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is already logged in
    const currentUser = AuthService.getCurrentUser();
    if (currentUser) {
      setUser(currentUser);
    }
    setLoading(false);
  }, []);

  const handleLogin = async (userData, isLogin) => {
    try {
      let result;
      
      if (isLogin) {
        result = await AuthService.login(userData.email, userData.password, userData.userType);
      } else {
        result = await AuthService.register(userData);
      }
      
      if (result.success) {
        setUser(result.user);
      } else {
        alert('Authentication failed: ' + result.error);
      }
    } catch (error) {
      console.error('Authentication error:', error);
      alert('Authentication failed: ' + error.message);
    }
  };

  const handleLogout = () => {
    AuthService.logout();
    setUser(null);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <Routes>
      {!user ? (
        <>
          <Route path="/login" element={<Login onLogin={handleLogin} />} />
          <Route path="/register-institute" element={<InstituteRegWrapper />} />
          <Route path="/" element={<LandingWrapper />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </>
      ) : (
        <>
          <Route 
            path="/dashboard" 
            element={
              user.userType === 'issuer' ? (
                <IssuerHomepage user={user} onLogout={handleLogout} />
              ) : (
                <VerifierHomepage user={user} onLogout={handleLogout} />
              )
            } 
          />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </>
      )}
    </Routes>
  );
}

function App() {
  return (
    <Router>
      <AppContent />
    </Router>
  );
}
export default App;
