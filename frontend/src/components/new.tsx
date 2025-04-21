import React, { useEffect, useState } from 'react';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
  Area,
  ComposedChart,
} from 'recharts';

interface StockChartProps {
  symbol: string;
  timeRange: string;
  chartType: string;
}

// Mock data generator - will be replaced with Alpha Vantage API
const generateMockData = (timeRange: string) => {
  const data = [];
  const now = new Date();
  let startDate: Date;
  let interval: number;
  let format: string;
  let dataPoints: number;

  switch (timeRange) {
    case '1D':
      startDate = new Date(now);
      startDate.setHours(9, 30, 0, 0);
      interval = 5; // 5 minutes
      format = 'HH:mm';
      dataPoints = 78; // 6.5 hours / 5 minutes
      break;
    case '1W':
      startDate = new Date(now);
      startDate.setDate(now.getDate() - 7);
      interval = 1; // 1 day
      format = 'MM/dd';
      dataPoints = 7;
      break;
    case '1M':
      startDate = new Date(now);
      startDate.setMonth(now.getMonth() - 1);
      interval = 1; // 1 day
      format = 'MM/dd';
      dataPoints = 30;
      break;
    case '3M':
      startDate = new Date(now);
      startDate.setMonth(now.getMonth() - 3);
      interval = 3; // 3 days
      format = 'MM/dd';
      dataPoints = 30;
      break;
    case '6M':
      startDate = new Date(now);
      startDate.setMonth(now.getMonth() - 6);
      interval = 7; // 1 week
      format = 'MM/dd';
      dataPoints = 26;
      break;
    case '1Y':
      startDate = new Date(now);
      startDate.setFullYear(now.getFullYear() - 1);
      interval = 14; // 2 weeks
      format = 'MM/dd';
      dataPoints = 26;
      break;
    case '5Y':
      startDate = new Date(now);
      startDate.setFullYear(now.getFullYear() - 5);
      interval = 60; // 2 months
      format = 'MM/yyyy';
      dataPoints = 30;
      break;
    default: // MAX
      startDate = new Date(now);
      startDate.setFullYear(now.getFullYear() - 10);
      interval = 120; // 4 months
      format = 'MM/yyyy';
      dataPoints = 30;
      break;
  }

  let baseValue = 150 + Math.random() * 50;
  let volatility = 0.02;

  for (let i = 0; i < dataPoints; i++) {
    const date = new Date(startDate);
    if (timeRange === '1D') {
      date.setMinutes(date.getMinutes() + interval * i);
      if (date.getHours() >= 16) break; // Market closes at 4 PM
    } else {
      date.setDate(date.getDate() + interval * i);
    }

    // Generate random price movement with some trend
    const change = (Math.random() - 0.5) * volatility * baseValue;
    if (i > 0) {
      baseValue = data[i - 1].close + change;
    }

    const open = baseValue;
    const close = baseValue + (Math.random() - 0.5) * volatility * baseValue;
    const high = Math.max(open, close) + Math.random() * volatility * baseValue;
    const low = Math.min(open, close) - Math.random() * volatility * baseValue;
    const volume = Math.floor(100000 + Math.random() * 900000);

    data.push({
      date: date.toLocaleDateString(),
      time: timeRange === '1D' ? date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : '',
      open: parseFloat(open.toFixed(2)),
      close: parseFloat(close.toFixed(2)),
      high: parseFloat(high.toFixed(2)),
      low: parseFloat(low.toFixed(2)),
      volume,
    });
  }

  return data;
};

const StockChart: React.FC<StockChartProps> = ({ symbol, timeRange, chartType }) => {
  const [data, setData] = useState<any[]>([]);

  useEffect(() => {
    // This would be replaced with an actual API call to Alpha Vantage
    const mockData = generateMockData(timeRange);
    setData(mockData);
  }, [symbol, timeRange]);

  const formatXAxis = (tickItem: string) => {
    if (timeRange === '1D') {
      return tickItem; // Already formatted as time
    }
    
    // For other time ranges, format as date
    const date = new Date(tickItem);
    if (timeRange === '5Y' || timeRange === 'MAX') {
      return date.toLocaleDateString(undefined, { month: 'short', year: '2-digit' });
    }
    return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
  };

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-gray-800 border border-gray-700 p-3 rounded shadow-lg">
          <p className="font-medium text-white">{timeRange === '1D' ? `${label}` : new Date(label).toLocaleDateString()}</p>
          {chartType === 'candle' ? (
            <>
              <p className="text-gray-300">Open: <span className="text-white">${payload[0].payload.open.toFixed(2)}</span></p>
              <p className="text-gray-300">Close: <span className="text-white">${payload[0].payload.close.toFixed(2)}</span></p>
              <p className="text-gray-300">High: <span className="text-white">${payload[0].payload.high.toFixed(2)}</span></p>
              <p className="text-gray-300">Low: <span className="text-white">${payload[0].payload.low.toFixed(2)}</span></p>
            </>
          ) : (
            <p className="text-gray-300">Price: <span className="text-white">${payload[0].value.toFixed(2)}</span></p>
          )}
          <p className="text-gray-300">Volume: <span className="text-white">{payload[0].payload.volume.toLocaleString()}</span></p>
        </div>
      );
    }
    return null;
  };

  const renderChart = () => {
    switch (chartType) {
      case 'line':
        return (
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={data}>
              <defs>
                <linearGradient id="colorClose" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis
                dataKey="date"
                tickFormatter={formatXAxis}
                stroke="#9ca3af"
                tick={{ fill: '#9ca3af' }}
                axisLine={{ stroke: '#4b5563' }}
              />
              <YAxis
                domain={['auto', 'auto']}
                stroke="#9ca3af"
                tick={{ fill: '#9ca3af' }}
                axisLine={{ stroke: '#4b5563' }}
                tickFormatter={(value) => `$${value}`}
              />
              <Tooltip content={<CustomTooltip />} />
              <Area
                type="monotone"
                dataKey="close"
                stroke="#6366f1"
                strokeWidth={2}
                fillOpacity={1}
                fill="url(#colorClose)"
                activeDot={{ r: 6, fill: '#6366f1', stroke: '#fff' }}
              />
              <Line
                type="monotone"
                dataKey="close"
                stroke="#6366f1"
                strokeWidth={2}
                dot={false}
                activeDot={{ r: 6, fill: '#6366f1', stroke: '#fff' }}
              />
            </ComposedChart>
          </ResponsiveContainer>
        );
      case 'bar':
        return (
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis
                dataKey="date"
                tickFormatter={formatXAxis}
                stroke="#9ca3af"
                tick={{ fill: '#9ca3af' }}
                axisLine={{ stroke: '#4b5563' }}
              />
              <YAxis
                domain={['auto', 'auto']}
                stroke="#9ca3af"
                tick={{ fill: '#9ca3af' }}
                axisLine={{ stroke: '#4b5563' }}
                tickFormatter={(value) => `$${value}`}
              />
              <Tooltip content={<CustomTooltip />} />
              <Bar
                dataKey="close"
                fill="#6366f1"
                radius={[4, 4, 0, 0]}
                barSize={timeRange === '1D' ? 5 : timeRange === '1W' ? 15 : 20}
              />
            </BarChart>
          </ResponsiveContainer>
        );
      case 'candle':
        return (
          <ResponsiveContainer width="100%" height="100%">
            <ComposedChart data={data}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis
                dataKey="date"
                tickFormatter={formatXAxis}
                stroke="#9ca3af"
                tick={{ fill: '#9ca3af' }}
                axisLine={{ stroke: '#4b5563' }}
              />
              <YAxis
                domain={['auto', 'auto']}
                stroke="#9ca3af"
                tick={{ fill: '#9ca3af' }}
                axisLine={{ stroke: '#4b5563' }}
                tickFormatter={(value) => `$${value}`}
              />
              <Tooltip content={<CustomTooltip />} />
              {data.map((entry, index) => (
                <React.Fragment key={index}>
                  {/* High-Low line */}
                  <Line
                    dataKey="high"
                    stroke={entry.close >= entry.open ? '#10b981' : '#ef4444'}
                    dot={false}
                    activeDot={false}
                    isAnimationActive={false}
                  />
                  <Line
                    dataKey="low"
                    stroke={entry.close >= entry.open ? '#10b981' : '#ef4444'}
                    dot={false}
                    activeDot={false}
                    isAnimationActive={false}
                  />
                  {/* Candle body */}
                  <Bar
                    dataKey={entry.close >= entry.open ? 'close' : 'open'}
                    fill={entry.close >= entry.open ? '#10b981' : '#ef4444'}
                    stroke={entry.close >= entry.open ? '#10b981' : '#ef4444'}
                    barSize={timeRange === '1D' ? 5 : timeRange === '1W' ? 15 : 20}
                  />
                </React.Fragment>
              ))}
            </ComposedChart>
          </ResponsiveContainer>
        );
      default:
        return null;
    }
  };

  return (
    <div className="h-full w-full">
      {renderChart()}
    </div>
  );
};

export default StockChart;