import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { MockAuthService } from './services/mockAuth'
import MockLogin from './components/MockLogin'
import IssuerHomepage from './components/IssuerHomepage'
import VerifierHomepage from './components/VerifierHomepage'

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user is already logged in
    const currentUser = MockAuthService.getCurrentUser();
    if (currentUser) {
      setUser(currentUser);
    }
    setLoading(false);
  }, []);

  const handleLogin = (userData, isLogin) => {
    let result;
    
    if (isLogin) {
      result = MockAuthService.login(userData.email, userData.password, userData.userType);
    } else {
      result = MockAuthService.register(userData);
    }
    
    if (result.success) {
      setUser(result.user);
    } else {
      alert('Login failed: ' + result.error);
    }
  };

  const handleLogout = () => {
    MockAuthService.logout();
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
    <Router>
      <Routes>
        {!user ? (
          <>
            <Route path="/login" element={<MockLogin onLogin={handleLogin} />} />
            <Route path="*" element={<Navigate to="/login" replace />} />
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
    </Router>
  );
}

export default App;
