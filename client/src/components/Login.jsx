import { useState, useEffect } from 'react';
import { User, Lock, UserCheck, Building2 } from 'lucide-react';
import ApiService from '../services/ApiService';

const Login = ({ onLogin }) => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    institution: '',
    role: 'issuer'
  });
  const [isLogin, setIsLogin] = useState(true);
  const [institutes, setInstitutes] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    const userData = isLogin 
      ? { email: formData.email, password: formData.password, userType: formData.role }
      : { ...formData, userType: formData.role };
    
    // Call parent login handler
    onLogin(userData, isLogin);
  };

  // Fetch institutes on component mount for registration
  useEffect(() => {
    const fetchInstitutes = async () => {
      try {
        setLoading(true);
        const response = await ApiService.getInstitutesList();
        if (response.success) {
          setInstitutes(response.institutes);
        } else {
          console.error('Failed to fetch institutes:', response.error);
        }
      } catch (error) {
        console.error('Error fetching institutes:', error);
      } finally {
        setLoading(false);
      }
    };

    if (!isLogin) {
      fetchInstitutes();
    }
  }, [isLogin]);


  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-xl p-8 w-full max-w-md">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <Building2 className="w-8 h-8 text-blue-600" />
          </div>
          <h2 className="text-2xl font-bold text-gray-900">
            {isLogin ? 'Welcome Back' : 'Create Account'}
          </h2>
          <p className="text-gray-600 mt-2">
            {isLogin ? 'Sign in to your account' : 'Join our document verification system'}
          </p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* User Type Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Account Type
            </label>
            <div className="grid grid-cols-2 gap-3">
              <button
                type="button"
                onClick={() => setFormData({...formData, role: 'issuer'})}
                className={`p-3 rounded-lg border-2 transition-all ${
                  formData.role === 'issuer'
                    ? 'border-blue-500 bg-blue-50 text-blue-700'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <UserCheck className="w-5 h-5 mx-auto mb-1" />
                <div className="text-sm font-medium">Issuer</div>
              </button>
              <button
                type="button"
                onClick={() => setFormData({...formData, role: 'verifier'})}
                className={`p-3 rounded-lg border-2 transition-all ${
                  formData.role === 'verifier'
                    ? 'border-green-500 bg-green-50 text-green-700'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <Building2 className="w-5 h-5 mx-auto mb-1" />
                <div className="text-sm font-medium">Verifier</div>
              </button>
            </div>
          </div>

          {/* Institute field for registration */}
          { !isLogin && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Institute
              </label>
              {loading ? (
                <div className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-100">
                  Loading institutes...
                </div>
              ) : (
                <select
                  name="institution"
                  value={formData.institution}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required={!isLogin}
                >
                  <option value="">Select an institute</option>
                  {institutes.map((institute) => (
                    <option key={institute.id} value={institute.name}>
                      {institute.name} ({institute.type})
                    </option>
                  ))}
                </select>
              )}
              <p className="text-xs text-gray-500 mt-1">
                If your institute is not listed, contact admin to register it first.
              </p>
            </div>
          )}

          {/* Name field for registration */}
          {!isLogin && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Full Name
              </label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Enter your full name"
                  required
                />
              </div>
            </div>
          )}

          {/* Email */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Email Address
            </label>
            <div className="relative">
              <User className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Enter your email"
                required
              />
            </div>
          </div>

          {/* Password */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Password
            </label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Enter your password"
                required
              />
            </div>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            className="w-full bg-blue-600 text-white py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors"
          >
            {isLogin ? 'Sign In' : 'Create Account'}
          </button>
        </form>

        {/* Toggle between login/register */}
        <div className="text-center mt-6">
          <button
            onClick={() => setIsLogin(!isLogin)}
            className="text-blue-600 hover:text-blue-700 text-sm font-medium"
          >
            {isLogin ? "Don't have an account? Sign up" : "Already have an account? Sign in"}
          </button>
        </div>

        {/* Demo Notice */}
        {/* <div className="mt-6 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
          <p className="text-sm text-yellow-800 text-center">
            🎭 <strong>Demo Mode:</strong> Use any email/password to login
          </p>
        </div> */}
      </div>
    </div>
  );
};

export default Login;