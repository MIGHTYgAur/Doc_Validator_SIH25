import { useState, useEffect } from 'react';
import { Shield, Building } from 'lucide-react';
import ApiService from '../services/ApiService';

const UserAuthForm = ({ isLogin = true, onToggle, onSubmit, userType = 'individual' }) => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    institution: '', // Changed from 'institute' to 'institution' to match backend
    role: 'issuer'
  });

  const [institutes, setInstitutes] = useState([]);
  const [loading, setLoading] = useState(false);

  // Fetch institutes on component mount
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

    if (!isLogin && userType === 'individual') {
      fetchInstitutes();
    }
  }, [isLogin, userType]);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = () => {
    onSubmit(formData);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="bg-white rounded-xl shadow-lg p-8 w-full max-w-md">
        <div className="text-center mb-8">
          {userType === 'institute' ? (
            <Building className="mx-auto h-12 w-12 text-green-600 mb-4" />
          ) : (
            <Shield className="mx-auto h-12 w-12 text-blue-600 mb-4" />
          )}
          <h2 className="text-3xl font-bold text-gray-900">
            {isLogin ? 'Welcome Back' : 'Create Account'}
          </h2>
          <p className="text-gray-600 mt-2">
            {userType === 'institute' ? 'Institute Login' : 'Individual Login'} - Document Authenticity System
          </p>
        </div>

        <div className="space-y-6">
          {!isLogin && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Full Name
              </label>
              <input
                type="text"
                name="name"
                value={formData.name}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required={!isLogin}
              />
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Email Address
            </label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Password
            </label>
            <input
              type="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            />
          </div>

          {!isLogin && userType === 'individual' && (
            <>
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

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Role
                </label>
                <select
                  name="role"
                  value={formData.role}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="issuer">Issuer</option>
                  <option value="verifier">Verifier</option>
                </select>
              </div>
            </>
          )}

          <button
            onClick={handleSubmit}
            className={`w-full py-2 px-4 rounded-lg focus:ring-2 focus:ring-offset-2 transition duration-200 ${userType === 'institute'
                ? 'bg-green-600 text-white hover:bg-green-700 focus:ring-green-500'
                : 'bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500'
              }`}
          >
            {isLogin ? 'Sign In' : 'Create Account'}
          </button>
        </div>

        <div className="text-center mt-6">
          <span className="text-gray-600">
            {isLogin ? "Don't have an account?" : "Already have an account?"}
          </span>
          <button
            onClick={onToggle}
            className="ml-1 text-blue-600 hover:text-blue-800 font-medium"
          >
            {isLogin ? 'Sign up' : 'Sign in'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default UserAuthForm;
