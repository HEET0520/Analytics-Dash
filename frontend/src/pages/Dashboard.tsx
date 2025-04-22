import React, { useState, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';
import {
  TrendingUp,
  TrendingDown,
  Search,
  ArrowUpRight,
  ArrowDownRight,
  LineChart,
  CandlestickChart,
  BarChart4,
  RefreshCw,
} from 'lucide-react';
import StockChart from '../components/StockChart'; // Adjust path as needed
// import NewsCard from '../components/NewsFeed';
import AIAnalysis from '../components/AIAnalysis'; // Adjust path as needed

const FINNHUB_API_KEY = 'd03tdlpr01qm4vp3uh60d03tdlpr01qm4vp3uh6g'; // Replace with a valid key if needed

interface Stock {
  symbol: string;
  name: string;
  price: number;
  change: number;
  changePercent: number;
}

const Dashboard: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedStock, setSelectedStock] = useState<Stock | null>(null);
  const [stocks, setStocks] = useState<Stock[]>([]);
  const [timeRange, setTimeRange] = useState<'1D' | '1W' | '1M' | '3M' | '6M' | '1Y' | '5Y'>('1M'); // Default to 1M
  const [chartType, setChartType] = useState<'line' | 'bar' | 'candle'>('line');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchStocks = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(
        `https://finnhub.io/api/v1/stock/symbol?exchange=US&token=${FINNHUB_API_KEY}`
      );
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      const allSymbols = await response.json();
      const topSymbols = allSymbols.slice(0, 10);

      const stocksWithQuotes = await Promise.all(
        topSymbols.map(async (stock: any) => {
          const quoteRes = await fetch(
            `https://finnhub.io/api/v1/quote?symbol=${stock.symbol}&token=${FINNHUB_API_KEY}`
          );
          const quoteData = await quoteRes.json();
          return {
            symbol: stock.symbol,
            name: stock.description || stock.symbol,
            price: quoteData.c ?? 0,
            change: quoteData.d ?? 0,
            changePercent: quoteData.dp ?? 0,
          };
        })
      );

      setStocks(stocksWithQuotes);
      if (stocksWithQuotes.length && !selectedStock) {
        setSelectedStock(stocksWithQuotes[0]);
      }
    } catch (error) {
      console.error('Error fetching stocks:', error);
      setError('Failed to load watchlist. Please try again.');
    } finally {
      setIsLoading(false);
    }
  }, [selectedStock]);

  useEffect(() => {
    if (!stocks.length) {
      fetchStocks();
    }
  }, [fetchStocks, stocks.length]);

  useEffect(() => {
    if (!selectedStock) return;

    const fetchStockData = async () => {
      setIsLoading(true);
      try {
        const response = await fetch(
          `https://finnhub.io/api/v1/quote?symbol=${selectedStock.symbol}&token=${FINNHUB_API_KEY}`
        );
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const data = await response.json();
        setSelectedStock((prev) => ({
          ...prev!,
          price: data.c ?? 0,
          change: data.d ?? 0,
          changePercent: data.dp ?? 0,
        }));
      } catch (error) {
        console.error('Error updating selected stock:', error);
        setError(`Failed to update data for ${selectedStock.symbol}`);
      } finally {
        setIsLoading(false);
      }
    };

    fetchStockData();
  }, [selectedStock?.symbol]);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim() === '') return;

    const query = searchQuery.toUpperCase();
    setIsLoading(true);
    setError(null);
    try {
      const found = stocks.find((stock) => stock.symbol.toLowerCase() === query.toLowerCase());
      if (found) {
        setSelectedStock(found);
      } else {
        const response = await fetch(
          `https://finnhub.io/api/v1/quote?symbol=${query}&token=${FINNHUB_API_KEY}`
        );
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const data = await response.json();
        if (data.c) {
          const newStock: Stock = {
            symbol: query,
            name: query, // Could fetch full name from profile endpoint
            price: data.c,
            change: data.d,
            changePercent: data.dp,
          };
          setSelectedStock(newStock);
          setStocks((prev) => [...prev, newStock]);
        } else {
          setError('Invalid stock symbol');
        }
      }
      setSearchQuery('');
    } catch (error) {
      console.error('Error searching stock:', error);
      setError('Error searching stock. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleStockSelect = (stock: Stock) => {
    setSelectedStock(stock);
    setError(null);
  };

  return (
    <div className="pt-20">
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5 }}
        className="mb-6"
      >
        <h1 className="text-3xl font-bold mb-2">Market Dashboard</h1>
        <p className="text-gray-400">Real-time market analysis and AI-powered stock predictions</p>
      </motion.div>

      {error && (
        <div className="mb-4 p-3 bg-red-900/20 text-red-400 rounded-lg">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <div className="lg:col-span-1">
          <motion.div
            initial={{ x: -20, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ duration: 0.5 }}
            className="card mb-6"
          >
            <h2 className="text-xl font-semibold mb-4 flex items-center">
              <Search size={18} className="mr-2" />
              Stock Search
            </h2>

            <form onSubmit={handleSearch} className="mb-4">
              <div className="relative">
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search by symbol (e.g., AAPL)"
                  className="input-field w-full pr-10"
                  disabled={isLoading}
                />
                <button
                  type="submit"
                  className="absolute right-2 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-white"
                  disabled={isLoading}
                >
                  <Search size={18} />
                </button>
              </div>
            </form>

            <h3 className="text-lg font-medium mb-3 mt-6">Watchlist</h3>
            {isLoading && !stocks.length ? (
              <div className="text-gray-400">Loading watchlist...</div>
            ) : (
              <div className="space-y-3">
                {stocks.map((stock) => (
                  <motion.div
                    key={stock.symbol}
                    whileHover={{ x: 5 }}
                    onClick={() => handleStockSelect(stock)}
                    className={`p-3 rounded-lg cursor-pointer transition-all duration-200 flex justify-between items-center ${
                      selectedStock?.symbol === stock.symbol
                        ? 'bg-indigo-900/30 border border-indigo-800'
                        : 'hover:bg-gray-700/50'
                    }`}
                  >
                    <div>
                      <div className="font-medium">{stock.symbol}</div>
                      <div className="text-sm text-gray-400">{stock.name}</div>
                    </div>
                    <div className="text-right">
                      <div className="font-medium">${stock.price.toFixed(2)}</div>
                      <div
                        className={`text-sm flex items-center ${
                          stock.change >= 0 ? 'text-green-500' : 'text-red-500'
                        }`}
                      >
                        {stock.change >= 0 ? (
                          <ArrowUpRight size={14} className="mr-1" />
                        ) : (
                          <ArrowDownRight size={14} className="mr-1" />
                        )}
                        {stock.changePercent > 0 ? '+' : ''}
                        {stock.changePercent.toFixed(2)}%
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            )}
          </motion.div>
        </div>

        <div className="lg:col-span-3">
          <motion.div
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="card mb-6"
          >
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-6">
              <div>
                <div className="flex items-center">
                  <h2 className="text-2xl font-bold">{selectedStock?.symbol || 'Select a Stock'}</h2>
                  <span className="text-gray-400 ml-2">{selectedStock?.name}</span>
                </div>
                {selectedStock && (
                  <div className="flex items-center mt-1">
                    <span className="text-xl font-semibold">${selectedStock.price.toFixed(2)}</span>
                    <span
                      className={`ml-2 px-2 py-0.5 rounded text-sm flex items-center ${
                        selectedStock.change >= 0 ? 'bg-green-900/30 text-green-500' : 'bg-red-900/30 text-red-500'
                      }`}
                    >
                      {selectedStock.change >= 0 ? (
                        <TrendingUp size={14} className="mr-1" />
                      ) : (
                        <TrendingDown size={14} className="mr-1" />
                      )}
                      {selectedStock.change > 0 ? '+' : ''}
                      {selectedStock.change.toFixed(2)} ({selectedStock.changePercent.toFixed(2)}%)
                    </span>
                  </div>
                )}
              </div>

              <div className="flex mt-4 md:mt-0 space-x-2">
                <div className="flex items-center bg-gray-700 rounded-lg overflow-hidden">
                  <button
                    onClick={() => setChartType('line')}
                    className={`px-3 py-1.5 flex items-center ${
                      chartType === 'line' ? 'bg-indigo-600 text-white' : 'text-gray-300 hover:bg-gray-600'
                    }`}
                    disabled={isLoading}
                  >
                    <LineChart size={16} className="mr-1" /> Line
                  </button>
                  <button
                    onClick={() => setChartType('candle')}
                    className={`px-3 py-1.5 flex items-center ${
                      chartType === 'candle' ? 'bg-indigo-600 text-white' : 'text-gray-300 hover:bg-gray-600'
                    }`}
                    disabled={isLoading}
                  >
                    <CandlestickChart size={16} className="mr-1" /> Candle
                  </button>
                  <button
                    onClick={() => setChartType('bar')}
                    className={`px-3 py-1.5 flex items-center ${
                      chartType === 'bar' ? 'bg-indigo-600 text-white' : 'text-gray-300 hover:bg-gray-600'
                    }`}
                    disabled={isLoading}
                  >
                    <BarChart4 size={16} className="mr-1" /> Bar
                  </button>
                </div>

                <button
                  className="flex items-center bg-gray-700 hover:bg-gray-600 rounded-lg px-3 py-1.5 text-gray-300"
                  onClick={fetchStocks}
                  disabled={isLoading}
                >
                  <RefreshCw size={16} className={`mr-1 ${isLoading ? 'animate-spin' : ''}`} />
                  Refresh
                </button>
              </div>
            </div>

            <div className="h-[400px] w-full relative">
              {isLoading && (
                <div className="absolute inset-0 bg-gray-800/50 flex items-center justify-center z-10 rounded-lg">
                  <div className="flex items-center space-x-2">
                    <RefreshCw size={20} className="animate-spin text-indigo-500" />
                    <span>Loading chart data...</span>
                  </div>
                </div>
              )}
              {selectedStock && selectedStock.symbol && (
                <StockChart symbol={selectedStock.symbol} timeRange={timeRange} chartType={chartType} />
              )}
            </div>
          </motion.div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <motion.div
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ duration: 0.5, delay: 0.2 }}
            >
              {selectedStock && <AIAnalysis stock={selectedStock} />}
            </motion.div>

            <motion.div
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ duration: 0.5, delay: 0.3 }}
              className="card"
            >
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-semibold">Recent News</h2>
                <button className="text-sm text-indigo-400 hover:text-indigo-300 flex items-center">
                  <RefreshCw size={14} className="mr-1" /> Refresh
                </button>
              </div>
              <div className="space-y-4 max-h-[500px] overflow-y-auto pr-2">
                <div>Loading News...</div>
              </div>
            </motion.div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;