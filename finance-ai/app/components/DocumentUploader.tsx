import { useState } from 'react';
import { analyzeDocument } from '../lib/api';

interface DocumentUploaderProps {
  setAnalysisResults: (results: string) => void;
  setFinancialMetrics: (metrics: string) => void;
}

export function DocumentUploader({ setAnalysisResults, setFinancialMetrics }: DocumentUploaderProps) {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState<boolean>(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFile(e.target.files[0]);
    }
  };

  const handleAnalyze = async () => {
    if (!file) return;
    setLoading(true);
    try {
      const response = await analyzeDocument(file);
      setAnalysisResults(response.analysis_results);
      setFinancialMetrics(response.financial_metrics);
    } catch (err) {
      setAnalysisResults('Error analyzing document');
      setFinancialMetrics('');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="border-dashed border-2 border-gray-500 p-6 rounded-lg text-center">
        <input
          type="file"
          onChange={handleFileChange}
          className="hidden"
          id="file-upload"
          accept=".pdf,.png,.jpg,.jpeg"
        />
        <label htmlFor="file-upload" className="cursor-pointer">
          <p className="text-gray-400 mb-2">
            {file ? file.name : 'Drag & drop a financial document here'}
          </p>
          <p className="text-gray-400 text-sm mb-4">
            Supported formats: PDF, DOC, DOCX, TXT, JPG, PNG
          </p>
          <button className="bg-primary-blue text-white px-4 py-2 rounded-lg">Browse Files</button>
        </label>
      </div>
      <button
        onClick={handleAnalyze}
        disabled={!file || loading}
        className="mt-4 bg-primary-blue text-white px-4 py-2 rounded-lg disabled:opacity-50"
      >
        {loading ? 'Analyzing...' : 'Analyze Document'}
      </button>
    </div>
  );
}