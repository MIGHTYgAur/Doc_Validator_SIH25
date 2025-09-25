import { Shield, CheckCircle, Users } from 'lucide-react';

const LandingPage = ({ onGetStarted, onRegisterInstitute }) => (
  <div className="min-h-screen">
    {/* Hero Section */}
    <section className="relative bg-gradient-to-br from-blue-900 via-blue-800 to-indigo-900 text-white">
      <div className="absolute inset-0 bg-black opacity-20"></div>
      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 lg:py-32">
        <div className="text-center">
          <h1 className="text-4xl sm:text-6xl font-bold leading-tight mb-6">
            Secure Document
            <span className="text-blue-300"> Authentication</span>
          </h1>
          <p className="text-xl sm:text-2xl text-blue-100 mb-8 max-w-3xl mx-auto">
            Verify and authenticate documents with blockchain-powered security.
            Trusted by institutions worldwide.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button
              onClick={onGetStarted}
              className="bg-white text-blue-900 px-8 py-3 rounded-lg font-semibold text-lg hover:bg-blue-50 transition duration-300 shadow-lg"
            >
              Get Started
            </button>
            <button
              onClick={onRegisterInstitute}
              className="border-2 border-white text-white px-8 py-3 rounded-lg font-semibold text-lg hover:bg-white hover:text-blue-900 transition duration-300"
            >
              Register Institute
            </button>
          </div>
        </div>
      </div>
    </section>

    {/* Features Section */}
    <section className="py-20 bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
            Why Choose Our Platform?
          </h2>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Advanced security features and user-friendly interface for all your document authentication needs.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          <div className="text-center p-6 bg-white rounded-xl shadow-lg hover:shadow-xl transition-shadow">
            <Shield className="h-12 w-12 text-blue-600 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-3">Blockchain Security</h3>
            <p className="text-gray-600">Immutable document records secured by blockchain technology for ultimate authenticity.</p>
          </div>

          <div className="text-center p-6 bg-white rounded-xl shadow-lg hover:shadow-xl transition-shadow">
            <CheckCircle className="h-12 w-12 text-green-600 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-3">Instant Verification</h3>
            <p className="text-gray-600">Verify documents in seconds with our advanced cryptographic algorithms.</p>
          </div>

          <div className="text-center p-6 bg-white rounded-xl shadow-lg hover:shadow-xl transition-shadow">
            <Users className="h-12 w-12 text-purple-600 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-3">Multi-Institution</h3>
            <p className="text-gray-600">Connect universities, employers, and verifiers in one secure ecosystem.</p>
          </div>
        </div>
      </div>
    </section>

    {/* Stats Section */}
    <section className="py-16 bg-blue-900 text-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid md:grid-cols-4 gap-8 text-center">
          <div>
            <div className="text-3xl sm:text-4xl font-bold text-blue-300 mb-2">10,000+</div>
            <div className="text-blue-100">Documents Verified</div>
          </div>
          <div>
            <div className="text-3xl sm:text-4xl font-bold text-blue-300 mb-2">500+</div>
            <div className="text-blue-100">Registered Institutes</div>
          </div>
          <div>
            <div className="text-3xl sm:text-4xl font-bold text-blue-300 mb-2">99.9%</div>
            <div className="text-blue-100">Uptime</div>
          </div>
          <div>
            <div className="text-3xl sm:text-4xl font-bold text-blue-300 mb-2">24/7</div>
            <div className="text-blue-100">Support</div>
          </div>
        </div>
      </div>
    </section>

    {/* CTA Section */}
    <section className="py-20 bg-white">
      <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
        <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-6">
          Ready to Secure Your Documents?
        </h2>
        <p className="text-xl text-gray-600 mb-8">
          Join thousands of institutions and individuals who trust our platform for document authentication.
        </p>
        <button
          onClick={onGetStarted}
          className="bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold text-lg hover:bg-blue-700 transition duration-300 shadow-lg"
        >
          Start Today
        </button>
      </div>
    </section>
  </div>
);

export default LandingPage;
