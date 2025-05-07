'use client';

import { useState } from 'react';
import { DocumentUploader } from './../components/DocumentUploader';

export default function DocumentAnalysis() {
  const [analysisResults, setAnalysisResults] = useState<string>('');
  const [financialMetrics, setFinancialMetrics] = useState<string>('');

  return (
    <div>
      <h1 className="text-3xl font-bold mb-4">Financial Document Analysis</h1>
      <p className="text-gray-400 mb-6">
        Upload financial documents for AI-powered analysis and extraction of key insights
      </p>

      <div className="flex gap-6">
        <div className="w-1/2 bg-card-bg p-4 rounded-lg">
          <DocumentUploader
            setAnalysisResults={setAnalysisResults}
            setFinancialMetrics={setFinancialMetrics}
          />
          <div className="mt-6">
            <h3 className="text-lg font-semibold">How It Works</h3>
            <ul className="text-gray-400 list-decimal list-inside">
              <li>Upload any financial document (earnings reports, SEC filings, financial statements)</li>
              <li>Our AI model analyzes the document content, extracting key financial data and insights</li>
              <li>Receive a comprehensive analysis with key insights and investment recommendations</li>
            </ul>
          </div>
        </div>
        <div className="w-1/2 bg-card-bg p-4 rounded-lg">
          <h2 className="text-xl font-semibold mb-4">Analysis Results</h2>
          {analysisResults ? (
            <div>
              <p>{analysisResults}</p>
              <h3 className="text-lg font-semibold mt-4">Financial Metrics</h3>
              <p>{financialMetrics}</p>
            </div>
          ) : (
            <p className="text-gray-400">
              No Document Analyzed Yet. Upload a financial document and click "Analyze Document" to see detailed insights here.
            </p>
          )}
        </div>
      </div>
    </div>
  );
}