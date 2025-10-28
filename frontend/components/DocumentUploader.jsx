// frontend/components/DocumentUploader.jsx
"use client";
import React, { useRef, useState } from 'react';
import { analyzeSyncDocument } from "../lib/api";
import AnalysisFormatter from './AnalysisFormatter';

export default function DocumentUploader() {
  const inputRef = useRef(null);
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [analysisProgress, setAnalysisProgress] = useState(0);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const onSelect = (e) => {
    setFile(e.target.files?.[0] || null);
    setResult(null);
    setError(null);
    setProgress(0);
    setAnalysisProgress(0);
  };

  const onUpload = async () => {
    if (!file) return;
    if (file.size > 10 * 1024 * 1024) {
      setError('File must be under 10MB');
      return;
    }
    setLoading(true);
    setError(null);
    setProgress(0);
    setAnalysisProgress(0);
    
    // Estimate pages based on file size (rough approximation)
    const estimatedPages = Math.max(1, Math.round(file.size / (50 * 1024))); // ~50KB per page
    const estimatedTimeMinutes = Math.max(1, Math.round(estimatedPages * 1.5)); // ~1.5 min per page
    
    try {
      // Start analysis progress simulation
      const progressInterval = setInterval(() => {
        setAnalysisProgress(prev => {
          if (prev >= 90) return prev; // Stop at 90% until completion
          return prev + Math.random() * 2; // Gradual increase
        });
      }, 2000);
      
      const data = await analyzeSyncDocument(file, (progressEvent) => {
        const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        setProgress(percentCompleted);
      });
      
      clearInterval(progressInterval);
      setAnalysisProgress(100);
      setResult(data);
    } catch (e) {
      if (e?.message?.includes('timeout')) {
        setError(`Analysis timed out after ${estimatedTimeMinutes} minutes. Large documents (${estimatedPages} pages) may take longer. Please try with a smaller file.`);
      } else {
        setError(e?.message || 'Upload failed');
      }
    } finally {
      setLoading(false);
      setProgress(0);
      setAnalysisProgress(0);
    }
  };

  return (
    <div className="card p-4">
      <h3 className="font-semibold mb-3">Analyze Document</h3>
      <div className="flex flex-col sm:flex-row gap-3">
        <input ref={inputRef} type="file" accept=".pdf,image/*" onChange={onSelect} className="input" />
        <button onClick={onUpload} disabled={!file || loading} className="btn-primary disabled:opacity-50">
          {loading ? (
            <span className="inline-flex items-center gap-2">
              <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none"/>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
              </svg>
              Analyzing...
            </span>
          ) : (
            <span className="inline-flex items-center gap-2">
              <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              Analyze
            </span>
          )}
        </button>
      </div>
      {loading && (
        <div className="mt-3 space-y-3">
          <div className="flex items-center justify-between text-sm text-neutral-600">
            <span>Uploading document...</span>
            <span>{progress}%</span>
          </div>
          <div className="w-full bg-neutral-200 dark:bg-neutral-700 rounded-full h-2">
            <div 
              className="bg-gradient-to-r from-brandStart via-brandMid to-brandEnd h-2 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
          
          {progress === 100 && (
            <>
              <div className="flex items-center justify-between text-sm text-neutral-600">
                <span>Analyzing document...</span>
                <span>{Math.round(analysisProgress)}%</span>
              </div>
              <div className="w-full bg-neutral-200 dark:bg-neutral-700 rounded-full h-2">
                <div 
                  className="bg-gradient-to-r from-brandStart via-brandMid to-brandEnd h-2 rounded-full transition-all duration-500"
                  style={{ width: `${analysisProgress}%` }}
                />
              </div>
              <div className="text-xs text-neutral-500 text-center">
                Large documents may take several minutes to analyze
              </div>
            </>
          )}
        </div>
      )}
      {error && <div className="mt-3 text-sm text-red-600">{error}</div>}
      {result && (
        <div className="mt-6 space-y-6">
          {/* Recommendation Card */}
          <div className="bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-800 dark:to-slate-900 rounded-xl p-6 border border-slate-200 dark:border-slate-700">
            <div className="flex items-center gap-3 mb-4">
              <div className="p-2 bg-emerald-100 dark:bg-emerald-900/30 rounded-lg">
                <svg className="h-5 w-5 text-emerald-600 dark:text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100">Investment Recommendation</h3>
            </div>
            <div className="space-y-3">
              <div className="p-4 bg-white dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700">
                <div className="text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">Recommendation</div>
                <div className="text-lg font-semibold text-slate-900 dark:text-slate-100">{result.recommendation}</div>
              </div>
              <div className="flex items-center justify-between text-sm text-slate-500 dark:text-slate-400">
                <span className="flex items-center gap-2">
                  <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  Processing Time
                </span>
                <span className="font-medium">{result.processing_time}s</span>
              </div>
            </div>
          </div>

          {/* Analysis Card */}
          <div className="bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-xl p-6 border border-blue-200 dark:border-blue-800">
            <div className="flex items-center gap-3 mb-4">
              <div className="p-2 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
                <svg className="h-5 w-5 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100">Financial Analysis</h3>
            </div>
            <div className="bg-white dark:bg-slate-800 rounded-lg p-4 border border-blue-200 dark:border-blue-800">
              <div className="prose prose-sm max-w-none dark:prose-invert">
                <div className="whitespace-pre-wrap text-slate-700 dark:text-slate-300 leading-relaxed">
                  {typeof result.analysis_results === 'string' ? result.analysis_results : JSON.stringify(result.analysis_results, null, 2)}
                </div>
              </div>
            </div>
          </div>

          {/* Financial Metrics Table */}
          {result.financial_metrics_table && Array.isArray(result.financial_metrics_table) && result.financial_metrics_table.length > 0 && (
            <div className="bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 rounded-xl p-6 border border-purple-200 dark:border-purple-800">
              <div className="flex items-center gap-3 mb-4">
                <div className="p-2 bg-purple-100 dark:bg-purple-900/30 rounded-lg">
                  <svg className="h-5 w-5 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                  </svg>
                </div>
                <h3 className="text-lg font-semibold text-slate-900 dark:text-slate-100">Financial Metrics</h3>
              </div>
              <div className="bg-white dark:bg-slate-800 rounded-lg border border-purple-200 dark:border-purple-800 overflow-hidden">
                <div className="overflow-x-auto">
                  <table className="min-w-full">
                    <thead className="bg-slate-50 dark:bg-slate-700">
                      <tr>
                        {Object.keys(result.financial_metrics_table[0]).map((k) => (
                          <th key={k} className="px-4 py-3 text-left text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wider border-b border-slate-200 dark:border-slate-600">
                            {k}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-200 dark:divide-slate-600">
                      {result.financial_metrics_table.map((row, idx) => (
                        <tr key={idx} className="hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors">
                          {Object.values(row).map((v, i) => (
                            <td key={i} className="px-4 py-3 text-sm text-slate-900 dark:text-slate-100">
                              {String(v)}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}


