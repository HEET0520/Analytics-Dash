// frontend/components/dashboard/StockChart.jsx
"use client";
import React, { useMemo } from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend,
  Filler,
  TimeSeriesScale,
} from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend, Filler, TimeSeriesScale);

export default function StockChart({ prices = [], ticker = 'TICKER' }) {
  const safeSeries = Array.isArray(prices) ? prices : [];
  const labels = safeSeries.map((p) => (typeof p === 'object' ? (p.date ?? p.time ?? p[0]) : ''));
  const values = safeSeries.map((p) => (typeof p === 'object' ? (p.close ?? p.price ?? p.value ?? p[1]) : p));

  const data = useMemo(() => ({
    labels,
    datasets: [
      {
        label: `${ticker} Close`,
        data: values,
        fill: true,
        borderColor: '#CA763A',
        backgroundColor: 'rgba(202,118,58,0.15)',
        tension: 0.3,
        pointRadius: 0,
      },
    ],
  }), [labels.join(','), values.join(','), ticker]);

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      x: { grid: { display: false } },
      y: { grid: { color: 'rgba(0,0,0,0.05)' }, ticks: { callback: (v) => `$${v}` } },
    },
    plugins: {
      legend: { display: false },
      tooltip: { mode: 'index', intersect: false },
    },
  };

  return (
    <div className="h-64 md:h-80 lg:h-96 card p-4">
      <div className="flex items-center justify-between mb-2">
        <h3 className="font-semibold">Price Chart</h3>
        <span className="text-xs text-neutral-500">Last {values.length} points</span>
      </div>
      <div className="h-full">
        <Line data={data} options={options} />
      </div>
    </div>
  );
}


