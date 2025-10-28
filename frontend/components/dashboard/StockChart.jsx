// frontend/components/dashboard/StockChart.jsx
"use client";
import React, { useEffect, useMemo, useRef, useState } from 'react';
import { Chart } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Tooltip,
  Legend,
  Filler,
  TimeSeriesScale,
} from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, BarElement, Tooltip, Legend, Filler, TimeSeriesScale);

export default function StockChart({ prices = [], ticker = 'TICKER', chartType = 'line' }) {
  const safeSeries = Array.isArray(prices) ? prices : [];
  const labels = safeSeries.map((p) => (typeof p === 'object' ? (p.date ?? p.time ?? p[0]) : ''));
  const values = safeSeries.map((p) => (typeof p === 'object' ? (p.close ?? p.price ?? p.value ?? p[1]) : p));

  const firstVal = typeof values[0] === 'number' ? values[0] : null;
  const lastVal = typeof values[values.length - 1] === 'number' ? values[values.length - 1] : null;
  const bullish = firstVal != null && lastVal != null ? lastVal >= firstVal : true;
  const stroke = bullish ? '#22c55e' : '#ef4444';
  const fill = bullish ? 'rgba(34,197,94,0.15)' : 'rgba(239,68,68,0.15)';

  const data = useMemo(() => {
    if (chartType === 'bar') {
      return {
        labels,
        datasets: [
          {
            label: `${ticker} Close`,
            data: values,
            type: 'bar',
            backgroundColor: fill,
            borderColor: stroke,
          },
        ],
      };
    }
    return {
      labels,
      datasets: [
        {
          label: `${ticker} Close`,
          data: values,
          type: 'line',
          fill: true,
          borderColor: stroke,
          backgroundColor: fill,
          tension: 0.3,
          pointRadius: 0,
        },
      ],
    };
  }, [labels.join(','), values.join(','), ticker, chartType, stroke, fill]);

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
    <div className="rounded-2xl p-[1px] bg-gradient-to-r from-brandStart/30 via-brandMid/20 to-brandEnd/30">
      <div className="h-64 md:h-80 lg:h-96 card p-4 border-transparent motion-safe:animate-in">
        <div className="flex items-center justify-between mb-3">
          <h3 className="font-semibold">Price Chart</h3>
          <span className="text-xs text-neutral-500">Last {values.length} points</span>
        </div>
        <div className="h-[calc(100%-1rem)] overflow-hidden rounded-lg">
          <Chart data={data} options={options} type={chartType} />
        </div>
      </div>
    </div>
  );
}


