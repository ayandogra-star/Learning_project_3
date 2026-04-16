import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { fileAPI } from '../services/api';

function Dashboard() {
  const navigate = useNavigate();
  const [metrics, setMetrics] = useState(null);
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [metricsRes, filesRes] = await Promise.all([
          fileAPI.getDashboardMetrics(),
          fileAPI.getAllFiles(),
        ]);

        setMetrics(metricsRes.data);
        setFiles(filesRes.data);
        setError(null);
      } catch (err) {
        setError('Failed to load dashboard data. Please try again.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <svg
            className="w-16 h-16 text-blue-500 spinner mx-auto mb-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <p className="text-lg text-gray-600">Loading contract analysis...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-lg text-red-600 mb-4">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  const kpis = metrics?.kpis || {};

  // Group KPIs by category
  const kpiCategories = [
    {
      name: 'Contract Overview',
      kpis: [
        { key: 'totalContractsProcessed', label: 'Total Contracts Processed', icon: '📋' },
        { key: 'contractType', label: 'Contract Type', icon: '🏷️' },
        { key: 'contractStatus', label: 'Contract Status', icon: '✓' },
        { key: 'totalContractValue', label: 'Total Contract Value', icon: '💰' },
      ]
    },
    {
      name: 'Compliance & Risk',
      kpis: [
        { key: 'complianceScore', label: 'Compliance Score', icon: '📊' },
        { key: 'controlCoveragePercentage', label: 'Control Coverage', icon: '🛡️' },
        { key: 'incidentReadinessScore', label: 'Incident Readiness', icon: '🚨' },
        { key: 'highRiskIssuesCount', label: 'High-Risk Issues', icon: '⚠️' },
      ]
    },
    {
      name: 'Risk & Obligations',
      kpis: [
        { key: 'openRisksCount', label: 'Open Risks', icon: '🔴' },
        { key: 'averageTimeToRemediate', label: 'Avg Time to Remediate', icon: '⏳' },
        { key: 'revenueAtRisk', label: 'Revenue at Risk', icon: '📉' },
        { key: 'totalObligationsExtracted', label: 'Total Obligations', icon: '✅' },
      ]
    },
    {
      name: 'Security & Obligations',
      kpis: [
        { key: 'dataResidencyCompliance', label: 'Data Residency', icon: '🌍' },
        { key: 'encryptionCompliance', label: 'Encryption Compliance', icon: '🔐' },
        { key: 'mfaCoverage', label: 'MFA Coverage', icon: '🔑' },
        { key: 'obligationsCompletionRate', label: 'Obligations Completion', icon: '📈' },
      ]
    },
    {
      name: 'Processing & Accuracy',
      kpis: [
        { key: 'averageProcessingTime', label: 'Processing Time', icon: '⏱️' },
        { key: 'clauseExtractionAccuracy', label: 'Clause Accuracy', icon: '🎯' },
        { key: 'upcomingExpirations', label: 'Upcoming Expirations', icon: '📅' },
      ]
    },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                Contract Analysis Dashboard
              </h1>
              <p className="text-gray-600 mt-2">
                AI-powered contract analysis and compliance monitoring
              </p>
            </div>
            <button
              onClick={() => navigate('/')}
              className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors inline-flex items-center gap-2"
            >
              <svg
                className="w-5 h-5"
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
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* KPI Sections */}
        {kpiCategories.map((category, categoryIndex) => (
          <div key={categoryIndex} className="mb-12">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">{category.name}</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {category.kpis.map((kpiItem, itemIndex) => (
                <div
                  key={itemIndex}
                  className="bg-white rounded-lg shadow p-6 card-hover border border-gray-200 animate-fade-in hover:shadow-lg transition-all"
                  style={{ animationDelay: `${(categoryIndex * 4 + itemIndex) * 50}ms` }}
                >
                  <div className="flex items-start justify-between mb-4">
                    <h3 className="text-sm font-semibold text-gray-700 leading-tight">
                      {kpiItem.label}
                    </h3>
                    <span className="text-2xl">{kpiItem.icon}</span>
                  </div>
                  <p
                    className={`text-2xl font-bold ${
                      kpis[kpiItem.key] === 'Not Present'
                        ? 'text-gray-400'
                        : 'text-blue-600'
                    }`}
                  >
                    {kpis[kpiItem.key] || 'Not Present'}
                  </p>
                  {kpis[kpiItem.key] !== 'Not Present' && (
                    <p className="text-xs text-green-600 mt-2">✓ Extracted</p>
                  )}
                </div>
              ))}
            </div>
          </div>
        ))}

        {/* Files List */}
        {files.length > 0 && (
          <div className="bg-white rounded-lg shadow overflow-hidden animate-fade-in mt-12">
            <div className="px-6 py-4 border-b">
              <h2 className="text-xl font-bold text-gray-900">
                Analyzed Contracts
              </h2>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b">
                  <tr>
                    <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">
                      Contract
                    </th>
                    <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">
                      Size
                    </th>
                    <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">
                      Analysis Date
                    </th>
                    <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">
                      Status
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y">
                  {files.map((file) => (
                    <tr
                      key={file.id}
                      className="hover:bg-gray-50 transition-colors"
                    >
                      <td className="px-6 py-4 text-sm text-gray-900">
                        <div className="flex items-center gap-3">
                          <svg
                            className="w-5 h-5 text-gray-400"
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
                          {file.filename}
                        </div>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-600">
                        {(file.file_size / 1024).toFixed(2)} KB
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-600">
                        {new Date(file.upload_time).toLocaleString()}
                      </td>
                      <td className="px-6 py-4 text-sm">
                        <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-xs font-semibold">
                          {file.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {files.length === 0 && (
          <div className="bg-white rounded-lg shadow p-8 text-center mt-12">
            <svg
              className="w-16 h-16 text-gray-300 mx-auto mb-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.5}
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              No contracts analyzed yet
            </h3>
            <p className="text-gray-600 mb-4">
              Upload your first contract to extract KPIs and analyze compliance
            </p>
            <button
              onClick={() => navigate('/')}
              className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors inline-flex items-center gap-2"
            >
              <svg
                className="w-5 h-5"
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
          </div>
        )}
      </main>
    </div>
  );
}

export default Dashboard;
