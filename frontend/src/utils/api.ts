import axios from 'axios';

// Alpha Vantage API configuration
const ALPHA_VANTAGE_API_KEY = 'YOUR_ALPHA_VANTAGE_API_KEY'; // Replace with your actual API key
const ALPHA_VANTAGE_BASE_URL = 'https://www.alphavantage.co/query';

// News API configuration
const NEWS_API_KEY = 'YOUR_NEWS_API_KEY'; // Replace with your actual API key
const NEWS_API_BASE_URL = 'https://newsapi.org/v2';

// Local AI model API endpoint
const LOCAL_AI_MODEL_URL = 'http://0.0.0.0:8000/'; // Replace with your actual local API endpoint

// Alpha Vantage API functions
export const fetchStockData = async (symbol: string, interval: string = 'daily') => {
  try {
    const response = await axios.get(ALPHA_VANTAGE_BASE_URL, {
      params: {
        function: 'TIME_SERIES_DAILY',
        symbol,
        outputsize: 'full',
        apikey: ALPHA_VANTAGE_API_KEY,
      },
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching stock data:', error);
    throw error;
  }
};

export const fetchStockQuote = async (symbol: string) => {
  try {
    const response = await axios.get(ALPHA_VANTAGE_BASE_URL, {
      params: {
        function: 'GLOBAL_QUOTE',
        symbol,
        apikey: ALPHA_VANTAGE_API_KEY,
      },
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching stock quote:', error);
    throw error;
  }
};

export const searchStocks = async (keywords: string) => {
  try {
    const response = await axios.get(ALPHA_VANTAGE_BASE_URL, {
      params: {
        function: 'SYMBOL_SEARCH',
        keywords,
        apikey: ALPHA_VANTAGE_API_KEY,
      },
    });
    return response.data;
  } catch (error) {
    console.error('Error searching stocks:', error);
    throw error;
  }
};

// News API functions
export const fetchStockNews = async (symbol: string) => {
  try {
    const response = await axios.get(`${NEWS_API_BASE_URL}/everything`, {
      params: {
        q: symbol,
        language: 'en',
        sortBy: 'publishedAt',
        apiKey: NEWS_API_KEY,
      },
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching stock news:', error);
    throw error;
  }
};

// Local AI model API functions
export const analyzeStock = async (symbol: string, data: any) => {
  try {
    const response = await axios.post(`${LOCAL_AI_MODEL_URL}/analyze-stock`, {
      symbol,
      data,
    });
    return response.data;
  } catch (error) {
    console.error('Error analyzing stock:', error);
    throw error;
  }
};

export const analyzeDocument = async (file: File) => {
  try {
    const formData = new FormData();
    formData.append('document', file);
    
    const response = await axios.post(`${LOCAL_AI_MODEL_URL}/analyze`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error) {
    console.error('Error analyzing document:', error);
    throw error;
  }
};

export const getStockRecommendation = async (symbol: string) => {
  try {
    const response = await axios.get(`${LOCAL_AI_MODEL_URL}/recommendation`, {
      params: {
        symbol,
      },
    });
    return response.data;
  } catch (error) {
    console.error('Error getting stock recommendation:', error);
    throw error;
  }
};