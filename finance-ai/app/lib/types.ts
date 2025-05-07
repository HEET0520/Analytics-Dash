export interface PriceData {
    date: string;
    open: number;
    high: number;
    low: number;
    close: number;
    volume: number;
  }
  
  export interface PricesResponse {
    ticker: string;
    prices: PriceData[];
    error: string;
  }
  
  export interface NewsItem {
    title: string;
    source: string;
    published_at: string;
    description: string;
    url: string;
  }
  
  export interface MarketContextResponse {
    ticker: string;
    news: NewsItem[];
    error: string;
  }
  
  export interface AllDataResponse {
    ticker: string;
    historical_prices: PriceData[];
    fundamentals: Record<string, any>;
    technicals: Record<string, number>;
    basic_financials: Record<string, any>;
    financials_reported: Record<string, any>[];
    company_news: Record<string, any>[];
    timestamp: string;
    errors: string[];
  }
  
  export interface WatchlistItem {
    ticker: string;
    name: string;
    price: number;
    change: number;
  }
  
  export interface AnalysisResponse {
    summary: string;
    sentiment: string;
    confidence: number;
    keyFactors: string[];
    targetPrice: {
      low: number;
      mid: number;
      high: number;
    };
    recommendation: string;
    dataAvailability: string;
  }
  
  export interface DocumentAnalysisResponse {
    analysis_results: string;
    financial_metrics: string;
  }