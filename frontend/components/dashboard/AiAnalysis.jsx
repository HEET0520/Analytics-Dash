// frontend/components/dashboard/AiAnalysis.jsx
"use client";
import React from 'react';

export default function AiAnalysis({ analysis }) {
  if (!analysis) {
    return (
      <div className="card p-4">
        <div className="animate-pulse h-5 w-40 bg-black/10 dark:bg-white/10 rounded mb-3" />
        <div className="animate-pulse h-4 w-full bg-black/10 dark:bg-white/10 rounded mb-2" />
        <div className="animate-pulse h-4 w-5/6 bg-black/10 dark:bg-white/10 rounded" />
      </div>
    );
  }

  const { summary, sentiment, confidence, keyFactors, targetPrice, recommendation, dataAvailability } = analysis;
  const confidencePercent = typeof confidence === 'number' ? (confidence > 1 ? Math.round(confidence) : Math.round(confidence * 100)) : 0;

  return (
    <div className="card p-4 space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold">AI Analysis</h3>
        {sentiment && (
          <span className={`text-xs px-2 py-1 rounded bg-black/5 dark:bg-white/10`}>{sentiment} • {confidencePercent}%</span>
        )}
      </div>
      {summary && <p className="text-sm leading-6">{summary}</p>}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm">
        {Array.isArray(keyFactors) && (
          <div>
            <div className="text-xs uppercase tracking-wide text-neutral-500 mb-1">Key Factors</div>
            <ul className="list-disc list-inside space-y-1">
              {keyFactors.map((k, idx) => (
                <li key={idx}>{k}</li>
              ))}
            </ul>
          </div>
        )}
        <div className="space-y-2">
          {targetPrice && typeof targetPrice === 'object' && (
            <div className="space-y-1">
              <div className="text-xs uppercase tracking-wide text-neutral-500">Target Price</div>
              <div className="grid grid-cols-3 gap-2 text-xs">
                <div className="rounded bg-black/5 dark:bg-white/10 px-2 py-1">Low: ${Number(targetPrice.low ?? 0).toLocaleString()}</div>
                <div className="rounded bg-black/5 dark:bg-white/10 px-2 py-1">Mid: ${Number(targetPrice.mid ?? 0).toLocaleString()}</div>
                <div className="rounded bg-black/5 dark:bg-white/10 px-2 py-1">High: ${Number(targetPrice.high ?? 0).toLocaleString()}</div>
              </div>
            </div>
          )}
          {recommendation && (
            <div className="flex items-center justify-between"><span className="text-neutral-500">Recommendation</span><span className="font-medium">{recommendation}</span></div>
          )}
          {dataAvailability && (
            <div className="text-xs text-neutral-500">Data: {String(dataAvailability)}</div>
          )}
        </div>
      </div>
    </div>
  );
}


