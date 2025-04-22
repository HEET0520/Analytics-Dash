import React, { useEffect, useState } from 'react';
import {
  ResponsiveContainer,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  Line,
  Area,
  ComposedChart,
  BarChart,
  Bar,
} from 'recharts';
import { RefreshCw } from 'lucide-react';

const FINNHUB_API_KEY = 'd03tdlpr01qm4vp3uh60d03tdlpr01qm4vp3uh6g'; // Replace with a valid key if needed

interface ChartData {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

const fetchChartData = async (
  symbol: string,
  timeRange: '1D' | '1W' | '1M' | '3M' | '6M' | '1Y' | '5Y'
): Promise<ChartData[]> => {
  try {
    const resolutionMap = {
      '1D': '1',
      '1W': '60',
      '1M': 'D',
      '3M': 'D',
      '6M': 'W',
      '1Y': 'W',
      '5Y': 'M',
    };
    const resolution = resolutionMap[timeRange];
    const now = Math.floor(Date.now() / 1000);
    let from, to;

    switch (timeRange) {
      case '1D':
        const today = new Date();
        today.setHours(9, 30, 0, 0); // Start of trading day (US market)
        from = Math.floor(today.getTime() / 1000);
        to = now;
        break;
      case '1W':
        from = now - 7 * 86400;
        to = now;
        break;
      case '1M':
        from = now - 30 * 86400;
        to = now;
        break;
      case '3M':
        from = now - 90 * 86400;
        to = now;
        break;
      case '6M':
        from = now - 182 * 86400;
        to = now;
        break;
      case '1Y':
        from = now - 365 * 86400;
        to = now;
        break;
      case '5Y':
        from = now - 5 * 365 * 86400;
        to = now;
        break;
      default:
        from = now - 365 * 86400;
        to = now;
    }

    const url = `https://finnhub.io/api/v1/stock/candle?symbol=${symbol}&resolution=${resolution}&from=${from}&to=${to}&token=${FINNHUB_API_KEY}`;
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    const data = await response.json();

    if (data.s === 'ok') {
      return data.t.map((time: number, index: number) => ({
        date: new Date(time * 1000).toLocaleDateString(),
        open: data.o[index],
        high: data.h[index],
        low: data.l[index],
        close: data.c[index],
        volume: data.v[index],
      }));
    } else if (data.s === 'no_data') {
      console.warn(`No data available for ${symbol} in time range ${timeRange}`);
      return [];
    } else {
      console.error('Unexpected API response:', data);
      return [];
    }
  } catch (error) {
    console.error('Error fetching chart data:', error);
    return [];
  }
};

interface StockChartProps {
  symbol: string;
  timeRange: '1D' | '1W' | '1M' | '3M' | '6M' | '1Y' | '5Y';
  chartType: 'line' | 'bar' | 'candle';
}

const StockChart: React.FC<StockChartProps> = ({ symbol, timeRange, chartType }) => {
  const [data, setData] = useState<ChartData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      const chartData = await fetchChartData(symbol, timeRange);
      console.log('Fetched chart data:', chartData); // Debug log
      setData(chartData);
      setLoading(false);
      if (chartData.length === 0) {
        setError(`No data available for ${symbol} in the selected time range`);
      }
    };

    if (symbol) {
      fetchData();
    } else {
      setLoading(false);
      setError('No stock symbol provided');
    }
  }, [symbol, timeRange]);

  const formatXAxis = (tick: string) => {
    const date = new Date(tick);
    return timeRange === '1D'
      ? date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      : date.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
  };

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (!active || !payload?.length) return null;
    const entry = payload[0].payload;

    return (
      <div className="bg-gray-800 border border-gray-700 p-3 rounded shadow-lg">
        <p className="font-medium text-white">{label}</p>
        {chartType === 'candle' ? (
          <>
            <p className="text-gray-300">
              Open: <span className="text-white">${entry.open.toFixed(2)}</span>
            </p>
            <p className="text-gray-300">
              Close: <span className="text-white">${entry.close.toFixed(2)}</span>
            </p>
            <p className="text-gray-300">
              High: <span className="text-white">${entry.high.toFixed(2)}</span>
            </p>
            <p className="text-gray-300">
              Low: <span className="text-white">${entry.low.toFixed(2)}</span>
            </p>
          </>
        ) : (
          <p className="text-gray-300">
            Price: <span className="text-white">${entry.close.toFixed(2)}</span>
          </p>
        )}
        <p className="text-gray-300">
          Volume: <span className="text-white">{entry.volume.toLocaleString()}</span>
        </p>
      </div>
    );
  };

  const renderChart = () => {
    if (loading) {
      return (
        <div className="text-gray-400 text-center py-10 flex items-center justify-center">
          <RefreshCw size={20} className="animate-spin mr-2" />
          Loading chart data...
        </div>
      );
    }
    if (error) {
      return <div className="text-red-400 text-center py-10">{error}</div>;
    }
    if (!data.length) {
      return <div className="text-gray-400 text-center py-10">No data available for {symbol}</div>;
    }

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
                tickFormatter={(value) => `$${value.toFixed(2)}`}
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
                tickFormatter={(value) => `$${value.toFixed(2)}`}
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
                tickFormatter={(value) => `$${value.toFixed(2)}`}
              />
              <Tooltip content={<CustomTooltip />} />
              <Bar
                dataKey={(entry) => ({
                  open: entry.open,
                  close: entry.close,
                  high: entry.high,
                  low: entry.low,
                })}
                shape={(props: any) => {
                  const { x, y, width, payload, yAxis } = props;
                  const { open, close, high, low } = payload;
                  const isBullish = close >= open;
                  const fill = isBullish ? '#10b981' : '#ef4444';
                  const bodyHeight =
                    Math.abs(close - open) * (props.height / (yAxis.domain[1] - yAxis.domain[0]));
                  const wickTop = yAxis.scale(high);
                  const wickBottom = yAxis.scale(low);
                  const bodyY = isBullish ? yAxis.scale(close) : yAxis.scale(open);

                  return (
                    <g>
                      {/* Wick */}
                      <line
                        x1={x + width / 2}
                        x2={x + width / 2}
                        y1={wickTop}
                        y2={wickBottom}
                        stroke={fill}
                        strokeWidth={1}
                      />
                      {/* Body */}
                      <rect
                        x={x}
                        y={bodyY}
                        width={width}
                        height={bodyHeight || 1} // Ensure non-zero height
                        fill={fill}
                        stroke={fill}
                      />
                    </g>
                  );
                }}
                barSize={timeRange === '1D' ? 5 : timeRange === '1W' ? 15 : 20}
              />
            </ComposedChart>
          </ResponsiveContainer>
        );
      default:
        return <div className="text-red-400 text-center py-10">Invalid chart type</div>;
    }
  };

  return <div className="h-full w-full">{renderChart()}</div>;
};

export default StockChart;