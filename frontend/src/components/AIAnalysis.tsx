import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, AlertTriangle, RefreshCw, Brain, Lightbulb, Target } from 'lucide-react';

interface AIAnalysisProps {
  stock: {
    symbol: string;
    name: string;
    price: number;
    change: number;
    changePercent: number;
  };
}

const AIAnalysis: React.FC<AIAnalysisProps> = ({ stock }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [analysis, setAnalysis] = useState<{
    summary: string;
    sentiment: 'bullish' | 'bearish' | 'neutral';
    confidence: number;
    keyFactors: string[];
    targetPrice: {
      low: number;
      mid: number;
      high: number;
    };
    recommendation: 'buy' | 'sell' | 'hold';
  } | null>(null);

  const validateTicker = async (ticker: string) => {
    try {
      const response = await fetch(`http://localhost:8000/validate-ticker/${ticker}`);
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      const data = await response.json();
      return data.valid;
    } catch {
      return false;
    }
  };

  const fetchAnalysis = async () => {
    setLoading(true);
    setError(null);
    try {
      if (!(await validateTicker(stock.symbol))) {
        throw new Error(
          `Ticker ${stock.symbol} is not supported by the data provider. Please try major tickers like TSLA, MSFT, or AAPL.`
        );
      }
      const response = await fetch(`http://localhost:8000/analyze/${stock.symbol}`);
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setAnalysis(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalysis();
  }, [stock.symbol]);

  const refreshAnalysis = () => {
    fetchAnalysis();
  };

  return (
    <div className="card h-full">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold flex items-center">
          <Brain className="mr-2 text-indigo-400" size={20} />
          AI-Powered Analysis
        </h2>
        <button
          onClick={refreshAnalysis}
          className="text-sm text-indigo-400 hover:text-indigo-300 flex items-center"
          disabled={loading}
        >
          <RefreshCw size={14} className={`mr-1 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      {loading ? (
        <div className="flex flex-col items-center justify-center py-8">
          <RefreshCw size={30} className="text-indigo-500 animate-spin mb-4" />
          <p className="text-gray-300">Analyzing market data...</p>
        </div>
      ) : error ? (
        <div className="flex flex-col items-center justify-center py-8">
          <AlertTriangle size={30} className="text-yellow-500 mb-4" />
          <p className="text-gray-300 text-center">{error}</p>
        </div>
      ) : analysis ? (
        <div className="space-y-4">
          <p className="text-gray-300">{analysis.summary}</p>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
            <div className="bg-gray-800/50 p-3 rounded-lg">
              <div className="text-gray-400 text-sm mb-1">Sentiment</div>
              <div
                className={`font-semibold flex items-center ${
                  analysis.sentiment === 'bullish'
                    ? 'text-green-500'
                    : analysis.sentiment === 'bearish'
                    ? 'text-red-500'
                    : 'text-gray-300'
                }`}
              >
                {analysis.sentiment === 'bullish' ? (
                  <TrendingUp size={16} className="mr-1" />
                ) : analysis.sentiment === 'bearish' ? (
                  <TrendingDown size={16} className="mr-1" />
                ) : (
                  <AlertTriangle size={16} className="mr-1" />
                )}
                {analysis.sentiment.charAt(0).toUpperCase() + analysis.sentiment.slice(1)}
              </div>
            </div>

            <div className="bg-gray-800/50 p-3 rounded-lg">
              <div className="text-gray-400 text-sm mb-1">Confidence</div>
              <div className="font-semibold flex items-center">
                <div className="w-full bg-gray-700 rounded-full h-2 mr-2">
                  <div
                    className={`h-2 rounded-full ${
                      analysis.confidence > 70
                        ? 'bg-green-500'
                        : analysis.confidence > 40
                        ? 'bg-yellow-500'
                        : 'bg-red-500'
                    }`}
                    style={{ width: `${analysis.confidence}%` }}
                  ></div>
                </div>
                {analysis.confidence.toFixed(0)}%
              </div>
            </div>

            <div className="bg-gray-800/50 p-3 rounded-lg">
              <div className="text-gray-400 text-sm mb-1">Recommendation</div>
              <div
                className={`font-semibold uppercase ${
                  analysis.recommendation === 'buy'
                    ? 'text-green-500'
                    : analysis.recommendation === 'sell'
                    ? 'text-red-500'
                    : 'text-yellow-500'
                }`}
              >
                {analysis.recommendation}
              </div>
            </div>
          </div>

          <div>
            <h3 className="text-lg font-medium mb-2 flex items-center">
              <Lightbulb size={18} className="mr-2 text-yellow-500" />
              Key Factors
            </h3>
            <ul className="space-y-1">
              {analysis.keyFactors.map((factor, index) => (
                <li key={index} className="flex items-start text-gray-300">
                  <span className="text-indigo-400 mr-2">•</span>
                  {factor}
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h3 className="text-lg font-medium mb-2 flex items-center">
              <Target size={18} className="mr-2 text-indigo-400" />
              Price Targets (12 months)
            </h3>
            <div className="bg-gray-800/50 p-3 rounded-lg">
              <div className="flex justify-between items-center">
                <div className="text-center">
                  <div className="text-sm text-gray-400">Low</div>
                  <div className="font-semibold text-red-500">${analysis.targetPrice.low.toFixed(2)}</div>
                  <div className="text-xs text-gray-500">
                    {((analysis.targetPrice.low / stock.price - 1) * 100).toFixed(1)}%
                  </div>
                </div>
                <div className="text-center">
                  <div className="text-sm text-gray-400">Target</div>
                  <div className="font-semibold text-indigo-400">${analysis.targetPrice.mid.toFixed(2)}</div>
                  <div className="text-xs text-gray-500">
                    {((analysis.targetPrice.mid / stock.price - 1) * 100).toFixed(1)}%
                  </div>
                </div>
                <div className="text-center">
                  <div className="text-sm text-gray-400">High</div>
                  <div className="font-semibold text-green-500">${analysis.targetPrice.high.toFixed(2)}</div>
                  <div className="text-xs text-gray-500">
                    {((analysis.targetPrice.high / stock.price - 1) * 100).toFixed(1)}%
                  </div>
                </div>
              </div>
              <div className="mt-2 relative h-2 bg-gray-700 rounded-full">
                <div
                  className="absolute h-2 bg-red-500 rounded-full"
                  style={{ left: '0%', width: '33%' }}
                ></div>
                <div
                  className="absolute h-2 bg-indigo-500 rounded-full"
                  style={{ left: '33%', width: '33%' }}
                ></div>
                <div
                  className="absolute h-2 bg-green-500 rounded-full"
                  style={{ left: '66%', width: '34%' }}
                ></div>
                <div
                  className="absolute w-2 h-4 bg-white rounded-full top-1/2 transform -translate-y-1/2"
                  style={{
                    left: `${((stock.price - analysis.targetPrice.low) / (analysis.targetPrice.high - analysis.targetPrice.low)) * 100}%`,
                  }}
                ></div>
              </div>
              <div className="flex justify-between mt-1">
                <div className="text-xs text-gray-500">${analysis.targetPrice.low.toFixed(2)}</div>
                <div className="text-xs text-gray-500">${analysis.targetPrice.high.toFixed(2)}</div>
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="flex flex-col items-center justify-center py-8">
          <AlertTriangle size={30} className="text-yellow-500 mb-4" />
          <p className="text-gray-300">Unable to load analysis. Please try again.</p>
        </div>
      )}
    </div>
  );
};

export default AIAnalysis;