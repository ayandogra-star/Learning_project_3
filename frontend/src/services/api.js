/**
 * API client for communicating with the backend
 */
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
});

export const fileAPI = {
  /**
   * Upload a file to the backend
   * @param {File} file - The file to upload
   * @param {Function} onProgress - Callback for upload progress
   * @returns {Promise} Response from the server
   */
  uploadFile: async (file, onProgress) => {
    const formData = new FormData();
    formData.append('file', file);

    return apiClient.post('/api/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (event) => {
        const percentCompleted = Math.round(
          (event.loaded * 100) / event.total
        );
        if (onProgress) {
          onProgress(percentCompleted);
        }
      },
    });
  },

  /**
   * Get dashboard metrics
   * @returns {Promise} Dashboard metrics data
   */
  getDashboardMetrics: async () => {
    return apiClient.get('/api/dashboard/metrics');
  },

  /**
   * Get all uploaded files
   * @returns {Promise} List of uploaded files
   */
  getAllFiles: async () => {
    return apiClient.get('/api/files');
  },

  /**
   * Health check
   * @returns {Promise} Health status
   */
  healthCheck: async () => {
    return apiClient.get('/health');
  },
};

export default apiClient;
