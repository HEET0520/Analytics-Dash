import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  TrendingUp, TrendingDown, Clock, Search, AlertTriangle, 
  ChevronDown, RefreshCw, DollarSign, BarChart4, CandlestickChart,
  ArrowUpRight, ArrowDownRight, LineChart, PieChart
} from 'lucide-react';
import StockChart from '../components/StockChart';
import NewsCard from '../components/NewsCard';
import AIAnalysis from '../components/AIAnalysis';

// Mock data - will be replaced with API calls
const mockStocks = [
  { symbol: 'AAPL', name: 'Apple Inc.', price: 187.32, change: 1.25, changePercent: 0.67 },
  { symbol: 'MSFT', name: 'Microsoft Corp.', price: 415.56, change: 3.78, changePercent: 0.92 },
  { symbol: 'GOOGL', name: 'Alphabet Inc.', price: 175.98, change: -0.87, changePercent: -0.49 },
  { symbol: 'AMZN', name: 'Amazon.com Inc.', price: 178.12, change: 2.34, changePercent: 1.33 },
  { symbol: 'TSLA', name: 'Tesla Inc.', price: 177.67, change: -5.23, changePercent: -2.86 },
];

const Dashboard: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedStock, setSelectedStock] = useState(mockStocks[0]);
  const [timeRange, setTimeRange] = useState('1D');
  const [chartType, setChartType] = useState('line');
  const [isLoading, setIsLoading] = useState(false);

  // Simulate API call when stock or time range changes
  useEffect(() => {
    const fetchStockData = async () => {
      setIsLoading(true);
      // Simulate API call delay
      setTimeout(() => {
        setIsLoading(false);
      }, 1000);
    };

    fetchStockData();
  }, [selectedStock, timeRange]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    // Here you would call the Alpha Vantage API to search for stocks
    console.log('Searching for:', searchQuery);
    // For demo, just select the first stock
    if (searchQuery.trim() !== '') {
      setSelectedStock(mockStocks[0]);
    }
  };

  const handleStockSelect = (stock: typeof mockStocks[0]) => {
    setSelectedStock(stock);
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
        <p className="text-gray-400">
          Real-time market analysis and AI-powered stock predictions
        </p>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Left Sidebar - Watchlist & Search */}
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
                  placeholder="Search by symbol or name..."
                  className="input-field w-full pr-10"
                />
                <button
                  type="submit"
                  className="absolute right-2 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-white"
                >
                  <Search size={18} />
                </button>
              </div>
            </form>

            <h3 className="text-lg font-medium mb-3 mt-6">Watchlist</h3>
            <div className="space-y-3">
              {mockStocks.map((stock) => (
                <motion.div
                  key={stock.symbol}
                  whileHover={{ x: 5 }}
                  onClick={() => handleStockSelect(stock)}
                  className={`p-3 rounded-lg cursor-pointer transition-all duration-200 flex justify-between items-center ${
                    selectedStock.symbol === stock.symbol
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
          </motion.div>
        </div>

        {/* Main Content - Stock Chart & Details */}
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
                  <h2 className="text-2xl font-bold">{selectedStock.symbol}</h2>
                  <span className="text-gray-400 ml-2">{selectedStock.name}</span>
                </div>
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
                    {selectedStock.change.toFixed(2)} ({selectedStock.changePercent > 0 ? '+' : ''}
                    {selectedStock.changePercent.toFixed(2)}%)
                  </span>
                </div>
              </div>

              <div className="flex mt-4 md:mt-0 space-x-2">
                <div className="flex items-center bg-gray-700 rounded-lg overflow-hidden">
                  <button
                    onClick={() => setChartType('line')}
                    className={`px-3 py-1.5 flex items-center ${
                      chartType === 'line' ? 'bg-indigo-600 text-white' : 'text-gray-300 hover:bg-gray-600'
                    }`}
                  >
                    <LineChart size={16} className="mr-1" />
                    Line
                  </button>
                  <button
                    onClick={() => setChartType('candle')}
                    className={`px-3 py-1.5 flex items-center ${
                      chartType === 'candle' ? 'bg-indigo-600 text-white' : 'text-gray-300 hover:bg-gray-600'
                    }`}
                  >
                    <CandlestickChart size={16} className="mr-1" />
                    Candle
                  </button>
                  <button
                    onClick={() => setChartType('bar')}
                    className={`px-3 py-1.5 flex items-center ${
                      chartType === 'bar' ? 'bg-indigo-600 text-white' : 'text-gray-300 hover:bg-gray-600'
                    }`}
                  >
                    <BarChart4 size={16} className="mr-1" />
                    Bar
                  </button>
                </div>

                <div className="relative">
                  <button
                    className="flex items-center bg-gray-700 hover:bg-gray-600 rounded-lg px-3 py-1.5 text-gray-300"
                    onClick={() => {
                      // Refresh data logic here
                      setIsLoading(true);
                      setTimeout(() => setIsLoading(false), 1000);
                    }}
                  >
                    <RefreshCw size={16} className={`mr-1 ${isLoading ? 'animate-spin' : ''}`} />
                    Refresh
                  </button>
                </div>
              </div>
            </div>

            <div className="flex flex-wrap gap-2 mb-4">
              {['1D', '1W', '1M', '3M', '6M', '1Y', '5Y', 'MAX'].map((range) => (
                <button
                  key={range}
                  onClick={() => setTimeRange(range)}
                  className={`px-3 py-1 rounded-lg text-sm ${
                    timeRange === range
                      ? 'bg-indigo-600 text-white'
                      : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  }`}
                >
                  {range}
                </button>
              ))}
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
              <StockChart symbol={selectedStock.symbol} timeRange={timeRange} chartType={chartType} />
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
              <div className="bg-gray-700/50 p-3 rounded-lg">
                <div className="text-gray-400 text-sm">Open</div>
                <div className="font-semibold">${(selectedStock.price - 1.5).toFixed(2)}</div>
              </div>
              <div className="bg-gray-700/50 p-3 rounded-lg">
                <div className="text-gray-400 text-sm">High</div>
                <div className="font-semibold">${(selectedStock.price + 2.3).toFixed(2)}</div>
              </div>
              <div className="bg-gray-700/50 p-3 rounded-lg">
                <div className="text-gray-400 text-sm">Low</div>
                <div className="font-semibold">${(selectedStock.price - 3.1).toFixed(2)}</div>
              </div>
              <div className="bg-gray-700/50 p-3 rounded-lg">
                <div className="text-gray-400 text-sm">Volume</div>
                <div className="font-semibold">32.5M</div>
              </div>
            </div>
          </motion.div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* AI Analysis */}
            <motion.div
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ duration: 0.5, delay: 0.2 }}
            >
              <AIAnalysis stock={selectedStock} />
            </motion.div>

            {/* News Feed */}
            <motion.div
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ duration: 0.5, delay: 0.3 }}
              className="card"
            >
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-semibold">Recent News</h2>
                <button className="text-sm text-indigo-400 hover:text-indigo-300 flex items-center">
                  <RefreshCw size={14} className="mr-1" />
                  Refresh
                </button>
              </div>

              <div className="space-y-4 max-h-[500px] overflow-y-auto pr-2">
                <NewsCard
                  title="Apple announces new AI features for iPhone"
                  source="TechCrunch"
                  time="2 hours ago"
                  sentiment="positive"
                />
                <NewsCard
                  title="Microsoft reports strong cloud growth in Q2 earnings"
                  source="CNBC"
                  time="5 hours ago"
                  sentiment="positive"
                />
                <NewsCard
                  title="Tesla faces production challenges amid supply chain issues"
                  source="Reuters"
                  time="Yesterday"
                  sentiment="negative"
                />
                <NewsCard
                  title="Amazon expands same-day delivery to more cities"
                  source="Bloomberg"
                  time="Yesterday"
                  sentiment="neutral"
                />
                <NewsCard
                  title="Google unveils new AI model for financial analysis"
                  source="Wall Street Journal"
                  time="2 days ago"
                  sentiment="positive"
                />
              </div>
            </motion.div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;