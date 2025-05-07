import { useMemo } from 'react';
import { Line, Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { PriceData } from '../lib/types';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend
);

interface StockChartProps {
  prices: PriceData[];
  chartType: 'line' | 'candlestick' | 'bar';
  duration: string;
}

export function StockChart({ prices, chartType, duration }: StockChartProps) {
  const filteredPrices = useMemo(() => {
    const now = new Date();
    let startDate: Date;

    switch (duration) {
      case '1y':
        startDate = new Date(now.getFullYear() - 1, now.getMonth(), now.getDate());
        break;
      case '6m':
        startDate = new Date(now.getFullYear(), now.getMonth() - 6, now.getDate());
        break;
      case '1m':
        startDate = new Date(now.getFullYear(), now.getMonth() - 1, now.getDate());
        break;
      case '1w':
        startDate = new Date(now.getFullYear(), now.getMonth(), now.getDate() - 7);
        break;
      case '1d':
        startDate = new Date(now.getFullYear(), now.getMonth(), now.getDate() - 1);
        break;
      default:
        startDate = new Date(now.getFullYear() - 1, now.getMonth(), now.getDate());
    }

    return prices.filter((price) => new Date(price.date) >= startDate);
  }, [prices, duration]);

  const labels = filteredPrices.map((price) => price.date);

  const data = {
    labels,
    datasets: [
      chartType === 'line' || chartType === 'candlestick'
        ? {
            label: 'Close Price',
            data: filteredPrices.map((price) => price.close),
            borderColor: '#6366f1',
            backgroundColor: 'rgba(99, 102, 241, 0.2)',
            fill: true,
          }
        : {
            label: 'Close Price',
            data: filteredPrices.map((price) => price.close),
            backgroundColor: '#6366f1',
          },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: {
        display: false,
      },
      title: {
        display: false,
      },
    },
    scales: {
      x: {
        ticks: {
          color: '#a0a5bd',
        },
        grid: {
          color: '#2d3348',
        },
      },
      y: {
        ticks: {
          color: '#a0a5bd',
        },
        grid: {
          color: '#2d3348',
        },
      },
    },
  };

  return (
    <div className="h-96">
      {(chartType === 'line' || chartType === 'candlestick') && <Line data={data} options={options} />}
      {chartType === 'bar' && <Bar data={data} options={options} />}
      {chartType === 'candlestick' && (
        <p className="text-gray-400 text-sm mt-2">
          Note: Candlestick chart rendering is currently simplified as a line chart. For full candlestick functionality, consider using a library like TradingView's lightweight-charts.
        </p>
      )}
    </div>
  );
}