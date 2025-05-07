'use client';

import { useState, useEffect } from 'react';
import { StockChart } from './../components/StockChart';
import { Watchlist } from './../components/Watchlist';
import { NewsFeed } from './../components/NewsFeed';
import { fetchStockPrices, fetchMarketContext, fetchAllData, analyzeStock } from './../lib/api';
import { PriceData, NewsItem, AllDataResponse, AnalysisResponse } from './../lib/types';

export default function Dashboard() {
  const [ticker, setTicker] = useState<string>('BRDCY');
  const [prices, setPrices] = useState<PriceData[]>([]);
  const [news, setNews] = useState<NewsItem[]>([]);
  const [allData, setAllData] = useState<AllDataResponse | null>(null);
  const [analysis, setAnalysis] = useState<AnalysisResponse | null>(null);
  const [chartType, setChartType] = useState<'line' | 'candlestick' | 'bar'>('line');
  const [duration, setDuration] = useState<string>('1y');
  const [error, setError] = useState<string>('');

  const fetchData = async (selectedTicker: string) => {
    try {
      const [pricesData, newsData, allDataResponse, analysisData] = await Promise.all([
        fetchStockPrices(selectedTicker),
        fetchMarketContext(selectedTicker),
        fetchAllData(selectedTicker),
        analyzeStock(selectedTicker),
      ]);

      if (pricesData.error) {
        setError(pricesData.error);
        setPrices([]);
      } else {
        setPrices(pricesData.prices);
        setError('');
      }

      if (newsData.error) {
        setNews([]);
      } else {
        setNews(newsData.news);
      }

      setAllData(allDataResponse);
      setAnalysis(analysisData);
    } catch (err) {
      setError('Failed to fetch data');
      setPrices([]);
      setNews([]);
      setAnalysis(null);
    }
  };

  useEffect(() => {
    fetchData(ticker);
  }, [ticker]);

  const handleSearch = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    const newTicker = formData.get('ticker') as string;
    setTicker(newTicker.toUpperCase());
  };

  return (
    <div>
      <h1 className="text-3xl font-bold mb-4">Market Dashboard</h1>
      <p className="text-gray-400 mb-6">Real-time market analysis and AI-powered stock predictions</p>

      <div className="flex gap-6">
        <div className="w-1/4">
          <div className="bg-card-bg p-4 rounded-lg mb-4">
            <form onSubmit={handleSearch}>
              <input
                type="text"
                name="ticker"
                placeholder="Search by symbol (e.g., AAPL)"
                className="w-full p-2 rounded-lg bg-gray-700 text-white"
              />
            </form>
          </div>
          <Watchlist onSelectTicker={setTicker} />
        </div>

        <div className="w-3/4">
          <div className="bg-card-bg p-4 rounded-lg mb-4">
            <div className="flex justify-between items-center mb-4">
              <div>
                <h2 className="text-xl font-semibold">{ticker}</h2>
                <p className="text-gray-400">
                  {allData?.basic_financials?.name || ticker} • $
                  {prices.length > 0 ? prices[prices.length - 1].close : 'N/A'}
                </p>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => setChartType('line')}
                  className={`p-2 ${chartType === 'line' ? 'bg-primary-blue' : 'bg-gray-600'} rounded-lg`}
                >
                  Line
                </button>
                <button
                  onClick={() => setChartType('candlestick')}
                  className={`p-2 ${chartType === 'candlestick' ? 'bg-primary-blue' : 'bg-gray-600'} rounded-lg`}
                >
                  Candlestick
                </button>
                <button
                  onClick={() => setChartType('bar')}
                  className={`p-2 ${chartType === 'bar' ? 'bg-primary-blue' : 'bg-gray-600'} rounded-lg`}
                >
                  Bar
                </button>
                <select
                  value={duration}
                  onChange={(e) => setDuration(e.target.value)}
                  className="p-2 bg-gray-700 rounded-lg text-white"
                >
                  <option value="1y">1 Year</option>
                  <option value="6m">6 Months</option>
                  <option value="1m">1 Month</option>
                  <option value="1w">1 Week</option>
                  <option value="1d">1 Day</option>
                </select>
                <button onClick={() => fetchData(ticker)} className="p-2 bg-gray-600 rounded-lg">
                  Refresh
                </button>
              </div>
            </div>
            {error ? (
              <p className="text-red-500">{error}</p>
            ) : prices.length === 0 ? (
              <p className="text-gray-400">No data available for {ticker} in the selected time range</p>
            ) : (
              <StockChart prices={prices} chartType={chartType} duration={duration} />
            )}
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="bg-card-bg p-4 rounded-lg">
              <h3 className="text-lg font-semibold mb-2">AI-Powered Analysis</h3>
              {analysis ? (
                <div>
                  <p className="text-gray-400">{analysis.summary}</p>
                  <p className="mt-2 text-gray-400">
                    <strong>Sentiment:</strong> {analysis.sentiment}
                  </p>
                  <p className="text-gray-400">
                    <strong>Confidence:</strong> {analysis.confidence.toFixed(2)}%
                  </p>
                  <p className="text-gray-400">
                    <strong>Recommendation:</strong> {analysis.recommendation}
                  </p>
                  <p className="text-gray-400">
                    <strong>Target Price:</strong> Low: ${analysis.targetPrice.low}, Mid: $
                    {analysis.targetPrice.mid}, High: ${analysis.targetPrice.high}
                  </p>
                </div>
              ) : (
                <p className="text-gray-400">Loading analysis...</p>
              )}
            </div>
            <div className="bg-card-bg p-4 rounded-lg">
              <h3 className="text-lg font-semibold mb-2">Recent News</h3>
              <NewsFeed news={news} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}