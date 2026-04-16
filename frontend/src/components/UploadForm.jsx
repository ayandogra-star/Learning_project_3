import { useState, useRef } from 'react';
import { fileAPI } from '../services/api';

function UploadForm({ onSuccess, onCancel }) {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);

  const handleFileSelect = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      // Validate file type
      const validTypes = ['application/pdf', 'text/plain', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
      if (!validTypes.includes(selectedFile.type)) {
        setError('Invalid file type. Please upload PDF, TXT, or DOC files only.');
        return;
      }

      // Validate file size (50MB max)
      if (selectedFile.size > 50 * 1024 * 1024) {
        setError('File is too large. Maximum size is 50MB.');
        return;
      }

      setFile(selectedFile);
      setError(null);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) {
      // Trigger file validation through input
      const dataTransfer = new DataTransfer();
      dataTransfer.items.add(droppedFile);
      fileInputRef.current.files = dataTransfer.files;
      
      // Manually call handler
      handleFileSelect({ target: { files: dataTransfer.files } });
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file first');
      return;
    }

    setUploading(true);
    setError(null);
    setProgress(0);

    try {
      const response = await fileAPI.uploadFile(file, (percent) => {
        setProgress(percent);
      });

      // Success - file uploaded
      setProgress(100);
      
      // Wait a moment for visual feedback
      setTimeout(() => {
        onSuccess(response.data);
      }, 500);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
        err.message ||
        'Upload failed. Please try again.'
      );
      setUploading(false);
      setProgress(0);
    }
  };

  if (uploading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
        <div className="max-w-md w-full">
          <div className="bg-white rounded-lg shadow-2xl p-8 text-center">
            <div className="mb-6">
              <div className="inline-flex items-center justify-center">
                <svg
                  className="w-16 h-16 text-blue-500 spinner"
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
              </div>
            </div>

            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              Analyzing Contract
            </h2>
            <p className="text-gray-600 mb-6">
              {file?.name}
            </p>

            <div className="bg-gray-100 rounded-full h-4 overflow-hidden mb-4">
              <div
                className="bg-gradient-to-r from-blue-500 to-indigo-600 h-full progress-bar"
                style={{ width: `${progress}%` }}
              />
            </div>

            <p className="text-lg font-semibold text-gray-700">
              {progress}%
            </p>
            <p className="text-sm text-gray-500 mt-4">
              Extracting KPIs and analyzing compliance...
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="max-w-md w-full">
        <div className="bg-white rounded-lg shadow-2xl p-8">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold text-gray-900">Analyze Contract</h2>
            <button
              onClick={onCancel}
              className="text-gray-400 hover:text-gray-600 transition-colors"
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
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>

          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-700 text-sm">{error}</p>
            </div>
          )}

          {/* Drop Zone */}
          <div
            onDragOver={handleDragOver}
            onDrop={handleDrop}
            className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-500 hover:bg-blue-50 transition-all duration-300 cursor-pointer mb-6"
            onClick={() => fileInputRef.current?.click()}
          >
            <div className="mb-4">
              <svg
                className="w-12 h-12 text-gray-400 mx-auto"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={1.5}
                  d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3v-8"
                />
              </svg>
            </div>

            <p className="text-gray-700 font-semibold">
              {file ? file.name : 'Upload contract for analysis'}
            </p>
            <p className="text-sm text-gray-500 mt-2">
              or click to select
            </p>

            <input
              ref={fileInputRef}
              type="file"
              onChange={handleFileSelect}
              accept=".pdf,.txt,.doc,.docx"
              className="hidden"
            />
          </div>

          {/* File Info */}
          {file && (
            <div className="bg-blue-50 rounded-lg p-4 mb-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <svg
                    className="w-8 h-8 text-blue-600"
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
                  <div>
                    <p className="font-semibold text-gray-900 text-sm">{file.name}</p>
                    <p className="text-xs text-gray-600">
                      {(file.size / 1024).toFixed(2)} KB
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => setFile(null)}
                  className="text-gray-400 hover:text-gray-600"
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
                      d="M6 18L18 6M6 6l12 12"
                    />
                  </svg>
                </button>
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex gap-3">
            <button
              onClick={onCancel}
              className="flex-1 py-3 px-4 border border-gray-300 rounded-lg text-gray-700 font-semibold hover:bg-gray-50 transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={handleUpload}
              disabled={!file}
              className="flex-1 py-3 px-4 bg-gradient-to-r from-blue-500 to-indigo-600 rounded-lg text-white font-semibold hover:from-blue-600 hover:to-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              Analyze
            </button>
          </div>

          <p className="text-xs text-gray-500 text-center mt-4">
            Extracts 18 KPIs • Max file size: 50MB • PDF, TXT, DOC, DOCX
          </p>
        </div>
      </div>
    </div>
  );
}

export default UploadForm;
