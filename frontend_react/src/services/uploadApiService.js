/**
 * Service for interacting with the SWIFT Code Upload API.
 */

import axios from 'axios';

const UPLOAD_API_URL = process.env.REACT_APP_UPLOAD_API_URL || 'http://localhost:8001';

const uploadApiClient = axios.create({
    baseURL: UPLOAD_API_URL,
    headers: {
        'Accept': 'application/json',
    },
});

/**
 * Upload a CSV file containing SWIFT codes.
 * 
 * @param {File} file - The CSV file to upload
 * @returns {Promise<Object>} - The upload response
 */
export const uploadSwiftCodesFile = async (file) => {
    try {
        const formData = new FormData();
        formData.append('file', file);

        const response = await uploadApiClient.post('/api/v1/upload/', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });

        return response.data;
    } catch (error) {
        console.error('Error uploading SWIFT codes file:', error);
        throw error;
    }
};

/**
 * Get the status of a SWIFT code upload.
 * 
 * @param {string} uploadId - ID of the upload
 * @returns {Promise<Object>} - The upload status
 */
export const getUploadStatus = async (uploadId) => {
    try {
        const response = await uploadApiClient.get(`/api/v1/upload/${uploadId}`);
        return response.data;
    } catch (error) {
        console.error(`Error getting upload status for ${uploadId}:`, error);
        throw error;
    }
};

/**
 * List all SWIFT code uploads with optional filtering.
 * 
 * @param {Object} params - Query parameters
 * @param {number} params.limit - Maximum number of uploads to return
 * @param {number} params.skip - Number of uploads to skip
 * @param {string} params.status - Filter by upload status
 * @returns {Promise<Array>} - List of uploads
 */
export const listUploads = async (params = {}) => {
    try {
        const { limit = 10, skip = 0, status } = params;

        const queryParams = new URLSearchParams();
        queryParams.append('limit', limit.toString());
        queryParams.append('skip', skip.toString());

        if (status) {
            queryParams.append('status', status);
        }

        const response = await uploadApiClient.get(`/api/v1/upload/?${queryParams.toString()}`);
        return response.data;
    } catch (error) {
        console.error('Error listing uploads:', error);
        throw error;
    }
};

/**
 * Get upload statistics.
 * 
 * @returns {Promise<Object>} 
 */
export const getUploadStats = async () => {
    try {
        const response = await uploadApiClient.get('/api/v1/upload/stats/summary');
        return response.data;
    } catch (error) {
        console.error('Error getting upload stats:', error);
        throw error;
    }
};

/**
 * Check if the Upload API is healthy.
 * 
 * @returns {Promise<boolean>}
 */
export const checkUploadApiHealth = async () => {
    try {
        const response = await uploadApiClient.get('/health');
        return response.status === 200;
    } catch (error) {
        console.error('Error checking upload API health:', error);
        return false;
    }
};