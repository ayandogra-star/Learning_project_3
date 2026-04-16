import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import UploadForm from './UploadForm';

function LandingPage() {
  const [showUpload, setShowUpload] = useState(false);
  const navigate = useNavigate();

  const handleUploadSuccess = () => {
    // Wait a moment for visual feedback, then navigate
    setTimeout(() => {
      navigate('/dashboard');
    }, 500);
  };

  if (showUpload) {
    return (
      <UploadForm
        onSuccess={handleUploadSuccess}
        onCancel={() => setShowUpload(false)}
      />
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="max-w-2xl w-full text-center animate-fade-in">
        {/* Header Section */}
        <div className="mb-12">
          <div className="flex justify-center mb-6">
            <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center shadow-lg">
              <svg
                className="w-8 h-8 text-white"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"
                />
              </svg>
            </div>
          </div>

          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
            Contract Analysis Agent
          </h1>
          <p className="text-lg md:text-xl text-gray-600 mb-2">
            AI-powered contract extraction and compliance monitoring
          </p>
          <p className="text-md text-gray-500">
            Extract KPIs, analyze compliance, and identify risks automatically
          </p>
        </div>

        {/* Features Section */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
          <div className="bg-white rounded-lg p-6 shadow-md card-hover">
            <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg
                className="w-6 h-6 text-blue-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              KPI Extraction
            </h3>
            <p className="text-gray-600 text-sm">
              Automatically extract 18+ contract KPIs including compliance scores and risk metrics
            </p>
          </div>

          <div className="bg-white rounded-lg p-6 shadow-md card-hover">
            <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg
                className="w-6 h-6 text-green-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 9v2m0 4v2m0 4v2m0-14v2m0-4v2m0-4v2m6-9a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Compliance Analysis
            </h3>
            <p className="text-gray-600 text-sm">
              Monitor compliance scores, control coverage, and security compliance status
            </p>
          </div>

          <div className="bg-white rounded-lg p-6 shadow-md card-hover">
            <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg
                className="w-6 h-6 text-purple-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Risk Management
            </h3>
            <p className="text-gray-600 text-sm">
              Identify high-risk issues, open risks, and revenue at risk automatically
            </p>
          </div>
        </div>

        {/* CTA Button */}
        <button
          onClick={() => setShowUpload(true)}
          className="bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-600 hover:to-indigo-700 text-white font-bold py-4 px-8 rounded-lg transition-all duration-300 transform hover:scale-105 shadow-lg inline-flex items-center gap-3 text-lg"
        >
          <svg
            className="w-6 h-6"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 4v16m8-8H4"
            />
          </svg>
          Analyze Contract
        </button>

        {/* Footer Info */}
        <div className="mt-12 text-sm text-gray-600">
          <p>Supported formats: PDF, TXT, DOC, DOCX</p>
          <p className="mt-2">Max file size: 50MB | Extracts 18+ KPIs</p>
        </div>
      </div>
    </div>
  );
}

export default LandingPage;
