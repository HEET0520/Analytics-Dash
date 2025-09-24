// frontend/components/DocumentUploader.jsx
"use client";
import React, { useRef, useState } from 'react';
import { analyzeSyncDocument } from "../lib/api";

export default function DocumentUploader() {
  const inputRef = useRef(null);
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const onSelect = (e) => {
    setFile(e.target.files?.[0] || null);
    setResult(null);
    setError(null);
  };

  const onUpload = async () => {
    if (!file) return;
    if (file.size > 10 * 1024 * 1024) {
      setError('File must be under 10MB');
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const data = await analyzeSyncDocument(file);
      setResult(data);
    } catch (e) {
      setError(e?.message || 'Upload failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card p-4">
      <h3 className="font-semibold mb-3">Analyze Document</h3>
      <div className="flex flex-col sm:flex-row gap-3">
        <input ref={inputRef} type="file" accept=".pdf,image/*" onChange={onSelect} className="block w-full text-sm" />
        <button onClick={onUpload} disabled={!file || loading} className="btn-primary disabled:opacity-50">{loading ? 'Analyzing…' : 'Analyze'}</button>
      </div>
      {error && <div className="mt-3 text-sm text-red-600">{error}</div>}
      {result && (
        <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          <div className="space-y-2">
            <div className="text-xs uppercase tracking-wide text-neutral-500">Recommendation</div>
            <div className="font-medium">{result.recommendation}</div>
            <div className="text-xs text-neutral-500">Processing Time: {result.processing_time}s</div>
          </div>
          <div className="space-y-2 md:col-span-2">
            <div className="text-xs uppercase tracking-wide text-neutral-500">Analysis</div>
            <pre className="whitespace-pre-wrap bg-black/5 dark:bg-white/10 p-3 rounded-lg">
{JSON.stringify(result.analysis_results, null, 2)}
            </pre>
          </div>
          {result.financial_metrics_table && (
            <div className="md:col-span-2">
              <div className="text-xs uppercase tracking-wide text-neutral-500 mb-2">Financial Metrics</div>
              <div className="overflow-x-auto">
                <table className="min-w-full text-sm">
                  <thead>
                    <tr className="text-left">
                      {Object.keys(result.financial_metrics_table[0] || {}).map((k) => (
                        <th key={k} className="px-3 py-2 border-b border-black/10 dark:border-white/10">{k}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {result.financial_metrics_table.map((row, idx) => (
                      <tr key={idx} className="odd:bg-black/5 dark:odd:bg-white/5">
                        {Object.values(row).map((v, i) => (
                          <td key={i} className="px-3 py-2 border-b border-black/10 dark:border-white/10">{String(v)}</td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}


