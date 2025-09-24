// frontend/lib/api.js
import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 20000,
  headers: {
    'Accept': 'application/json',
  },
});

// Interceptor for centralized error formatting
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error?.response?.status;
    const message = error?.response?.data?.detail || error.message || 'Unknown error';
    return Promise.reject({ status, message });
  }
);

// Helper to safely GET with params
const get = async (url, config = {}) => {
  const res = await api.get(url, config);
  return res.data;
};

// Helper to safely POST (handles FormData automatically)
const post = async (url, data, config = {}) => {
  const res = await api.post(url, data, config);
  return res.data;
};

// --- API functions ---
export const analyzeSyncDocument = async (file) => {
  const formData = new FormData();
  formData.append('file', file);

  return post('/analyze_sync/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    maxBodyLength: 10 * 1024 * 1024, // 10MB
  });
};

export const getAnalyze = (ticker) => get(`/analyze/${encodeURIComponent(ticker)}`);
export const getPrices = (ticker) => get(`/prices/${encodeURIComponent(ticker)}`);
export const getMarketContext = (ticker) => get(`/market-context/${encodeURIComponent(ticker)}`);
export const getAllData = (ticker) => get(`/all-data/${encodeURIComponent(ticker)}`);
export const validateTicker = (ticker) => get(`/validate-ticker/${encodeURIComponent(ticker)}`);
export const getHealth = () => get('/health');
export const getSnapshots = (tickers) => post('/snapshots', { tickers });

export default api;


