import { Shield, Building } from 'lucide-react';

const LoginTypeModal = ({ isOpen, onClose, onSelectType }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-lg max-w-md w-full p-6">
        <h3 className="text-xl font-bold text-gray-900 mb-6 text-center">Choose Login Type</h3>
        <div className="space-y-4">
          <button
            onClick={() => onSelectType('individual')}
            className="w-full p-4 border-2 border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors text-left"
          >
            <div className="flex items-center space-x-3">
              <Shield className="h-8 w-8 text-blue-600" />
              <div>
                <h4 className="font-semibold text-gray-900">Individual User</h4>
                <p className="text-sm text-gray-600">Login as an issuer or verifier</p>
              </div>
            </div>
          </button>

          <button
            onClick={() => onSelectType('institute')}
            className="w-full p-4 border-2 border-gray-200 rounded-lg hover:border-green-500 hover:bg-green-50 transition-colors text-left"
          >
            <div className="flex items-center space-x-3">
              <Building className="h-8 w-8 text-green-600" />
              <div>
                <h4 className="font-semibold text-gray-900">Institute</h4>
                <p className="text-sm text-gray-600">Login as an institution</p>
              </div>
            </div>
          </button>
        </div>

        <button
          onClick={onClose}
          className="w-full mt-4 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
        >
          Cancel
        </button>
      </div>
    </div>
  );
};

export default LoginTypeModal;
