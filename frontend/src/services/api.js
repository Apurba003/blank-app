import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests if available
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Handle responses and errors
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('authToken');
      window.location.href = '/';
    }
    return Promise.reject(error);
  }
);

export const authAPI = {
  register: (userData) => api.post('/register', userData),
  
  enrollKeystroke: (userId, sessions) => 
    api.post('/enroll/keystroke', { user_id: userId, sessions }),
  
  enrollFace: (userId, images) => 
    api.post('/enroll/face', { user_id: userId, images }),
  
  authenticateKeystroke: (userId, keystrokeData) => 
    api.post('/authenticate/keystroke', { user_id: userId, keystroke_data: keystrokeData }),
  
  authenticateFace: (userId, image) => 
    api.post('/authenticate/face', { user_id: userId, image }),
  
  authenticateMFA: (userId, keystrokeData, faceImage, fusionMethod = 'weighted_sum') => 
    api.post('/authenticate/mfa', {
      user_id: userId,
      keystroke_data: keystrokeData,
      face_image: faceImage,
      fusion_method: fusionMethod,
    }),
  
  getUserStatus: (userId) => api.get(`/user/${userId}/status`),
  
  getSystemMetrics: () => api.get('/metrics'),
  
  healthCheck: () => api.get('/health'),
};

export default api;
