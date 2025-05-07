import axios from 'axios';
import {
  PricesResponse,
  MarketContextResponse,
  AllDataResponse,
  AnalysisResponse,
  DocumentAnalysisResponse,
} from './types';

const API_BASE_URL = 'http://localhost:8000';

export const fetchStockPrices = async (ticker: string): Promise<PricesResponse> => {
  const response = await axios.get(`${API_BASE_URL}/prices/${ticker}`);
  return response.data;
};

export const fetchMarketContext = async (ticker: string): Promise<MarketContextResponse> => {
  const response = await axios.get(`${API_BASE_URL}/market-context/${ticker}`);
  return response.data;
};

export const fetchAllData = async (ticker: string): Promise<AllDataResponse> => {
  const response = await axios.get(`${API_BASE_URL}/all-data/${ticker}`);
  return response.data;
};

export const analyzeStock = async (ticker: string): Promise<AnalysisResponse> => {
  const response = await axios.get(`${API_BASE_URL}/analyze/${ticker}`);
  return response.data;
};

export const analyzeDocument = async (file: File): Promise<DocumentAnalysisResponse> => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await axios.post(`${API_BASE_URL}/analyze_sync/`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
};