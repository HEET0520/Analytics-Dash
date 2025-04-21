import React, { useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import { useDropzone } from 'react-dropzone';
import { FileText, Upload, AlertTriangle, CheckCircle, X, FileType, RefreshCw } from 'lucide-react';
import axios from 'axios';

// API URLs
const API_BASE_URL = 'http://127.0.0.1:8000';

interface AnalysisResult {
  summary: string;
  analysisResults: string;
  financialMetrics: string;
  keyInsights: string[];
  sentiment: 'positive' | 'negative' | 'neutral';
  recommendations: string[];
}

interface AnalysisStatus {
  task_id: string;
  status: string;
}

const DocumentAnalysis: React.FC = () => {
  const [files, setFiles] = useState<File[]>([]);
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [taskId, setTaskId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [usesMockData, setUsesMockData] = useState(false);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    setFiles(acceptedFiles);
    setAnalysisResult(null);
    setError(null);
    setUsesMockData(false);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt'],
      'image/png': ['.png'],
      'image/jpeg': ['.jpg', '.jpeg'],
    },
    maxFiles: 1,
  });

  const generateMockAnalysisResult = (fileName: string): AnalysisResult => {
    // Create realistic mock data based on the file name
    const fileType = fileName.split('.').pop()?.toLowerCase();
    const isEarningsReport = fileName.toLowerCase().includes('earnings') || 
                             fileName.toLowerCase().includes('report') ||
                             fileName.toLowerCase().includes('financial');
    
    return {
      summary: isEarningsReport 
        ? "This quarterly report indicates strong financial performance with revenue growth of 15% year-over-year. The company has expanded its market share in key regions and introduced new product lines that are performing above expectations. Cash flow remains positive, and debt levels have been reduced by 8% compared to the previous quarter."
        : `Analysis of ${fileName} shows mixed financial indicators with moderate growth potential. The document contains key metrics that suggest cautious optimism for upcoming quarters.`,
      analysisResults: "### Financial Strengths\nStrong revenue growth of 15% year-over-year. Expanding market share in key regions. New product lines performing above expectations.\n\n### Operational Performance\nEfficiency ratio improved to 68% from 72% last year. Operating margin at 23%, up 2.5 percentage points.\n\n### Growth Metrics\nProjected annual growth of 12-15% for next fiscal year. R&D investment increased by 22%.",
      financialMetrics: "- Revenue: $245.8M (+15% YoY)\n- Operating Margin: 23% (up from 20.5%)\n- EBITDA: $78.2M (+18% YoY)\n- Cash on Hand: $112.4M\n- Debt-to-Equity: 0.82 (improved from 0.95)",
      keyInsights: [
        "Revenue growth of 15% year-over-year",
        "Market share expansion in North America and Europe",
        "New product line contributing 12% to overall revenue",
        "Debt reduction of 8% from previous quarter",
        "Operating margin improved by 2.5 percentage points"
      ],
      sentiment: isEarningsReport ? "positive" : "neutral",
      recommendations: [
        "Consider increasing position based on strong fundamentals",
        "Monitor new product line performance in next quarter",
        "Watch for potential acquisition targets mentioned in report",
        "Be aware of mentioned supply chain challenges in Asian markets"
      ]
    };
  };

  const checkAnalysisStatus = async (taskId: string) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/task/${taskId}`);
      
      if (response.data.status === 'completed') {
        // Parse the full analysis results and financial metrics
        const analysisResults = response.data.analysis_results || "";
        const financialMetrics = response.data.financial_metrics || "";
        
        // Extract key insights from the financial metrics
        const keyInsights = financialMetrics
          .split('\n')
          .filter((line: string) => line.trim().startsWith('-'))
          .map((line: string) => line.trim());
        
        // Determine sentiment based on keywords in the analysis
        const sentiment = 
          analysisResults.toLowerCase().includes("growth") || 
          analysisResults.toLowerCase().includes("increase") || 
          analysisResults.toLowerCase().includes("improved") 
            ? "positive" 
            : analysisResults.toLowerCase().includes("decline") || 
              analysisResults.toLowerCase().includes("decrease") || 
              analysisResults.toLowerCase().includes("risk")
              ? "negative"
              : "neutral";
        
        // Extract recommendations or generate some based on the analysis
        const recommendationSection = analysisResults.includes("challenges") 
          ? analysisResults.split("challenges")[1] 
          : "";
        
        const recommendations = recommendationSection
          ? recommendationSection
              .split('\n')
              .filter((line: string) => line.trim().length > 10)
              .slice(0, 4)
          : ["Review the complete analysis for detailed recommendations"];
        
        const resultData: AnalysisResult = {
          summary: "Analysis complete. " + analysisResults.split('\n')[0],
          analysisResults: analysisResults,
          financialMetrics: financialMetrics,
          keyInsights: keyInsights.length > 0 ? keyInsights : ["No specific insights extracted"],
          sentiment: sentiment,
          recommendations: recommendations
        };
        
        setAnalysisResult(resultData);
        setAnalyzing(false);
      } else if (response.data.status === 'failed') {
        setError('Analysis failed. Please try again with a different document.');
        setAnalyzing(false);
      } else {
        // Still processing, check again after a delay
        setTimeout(() => checkAnalysisStatus(taskId), 2000);
      }
    } catch (error) {
      console.error('Error checking analysis status:', error);
      setError('Failed to retrieve analysis results. Please try again.');
      setAnalyzing(false);
    }
  };

  const handleAnalyze = async () => {
    if (files.length === 0) return;
    
    setAnalyzing(true);
    setError(null);
    
    try {
      const formData = new FormData();
      formData.append('file', files[0]);
      
      try {
        // First try to call the actual API
        const response = await axios.post(`${API_BASE_URL}/analyze/`, formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        });
        
        const { task_id } = response.data as AnalysisStatus;
        setTaskId(task_id);
        
        // Start polling for results
        checkAnalysisStatus(task_id);
      } catch (apiError) {
        console.warn('API connection failed, using mock data instead:', apiError);
        
        // Simulate API delay
        setTimeout(() => {
          setUsesMockData(true);
          setAnalysisResult(generateMockAnalysisResult(files[0].name));
          setAnalyzing(false);
        }, 3000);
      }
    } catch (error) {
      console.error('Error submitting document for analysis:', error);
      setError('Failed to submit document for analysis. Please try again.');
      setAnalyzing(false);
    }
  };

  const removeFile = () => {
    setFiles([]);
    setAnalysisResult(null);
    setTaskId(null);
    setError(null);
    setUsesMockData(false);
  };

  return (
    <div className="pt-20">
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5 }}
        className="mb-6"
      >
        <h1 className="text-3xl font-bold mb-2">Financial Document Analysis</h1>
        <p className="text-gray-400">
          Upload financial documents for AI-powered analysis and extraction of key insights
        </p>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <motion.div
          initial={{ x: -20, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ duration: 0.5 }}
          className="card"
        >
          <h2 className="text-xl font-semibold mb-4 flex items-center">
            <Upload size={18} className="mr-2" />
            Upload Document
          </h2>

          {files.length === 0 ? (
            <div
              {...getRootProps()}
              className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-all duration-200 ${
                isDragActive
                  ? 'border-indigo-500 bg-indigo-900/20'
                  : 'border-gray-600 hover:border-indigo-400 hover:bg-gray-800/50'
              }`}
            >
              <input {...getInputProps()} />
              <FileText className="h-12 w-12 mx-auto mb-4 text-indigo-400" />
              <p className="text-lg font-medium mb-2">
                {isDragActive ? 'Drop the file here' : 'Drag & drop a financial document here'}
              </p>
              <p className="text-gray-400 text-sm mb-4">
                Supported formats: PDF, DOC, DOCX, TXT, JPG, PNG
              </p>
              <button className="btn-primary">Browse Files</button>
            </div>
          ) : (
            <div className="border-2 border-gray-700 rounded-lg p-6">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center">
                  <FileType className="h-10 w-10 text-indigo-400 mr-3" />
                  <div>
                    <p className="font-medium">{files[0].name}</p>
                    <p className="text-sm text-gray-400">
                      {(files[0].size / 1024 / 1024).toFixed(2)} MB
                    </p>
                  </div>
                </div>
                <button
                  onClick={removeFile}
                  className="text-gray-400 hover:text-white p-1 rounded-full hover:bg-gray-700"
                >
                  <X size={18} />
                </button>
              </div>

              <button
                onClick={handleAnalyze}
                disabled={analyzing}
                className={`w-full py-3 rounded-lg font-medium flex items-center justify-center ${
                  analyzing
                    ? 'bg-indigo-900/50 text-indigo-300 cursor-not-allowed'
                    : 'bg-indigo-600 hover:bg-indigo-700 text-white'
                }`}
              >
                {analyzing ? (
                  <>
                    <RefreshCw size={18} className="mr-2 animate-spin" />
                    Analyzing Document...
                  </>
                ) : (
                  <>
                    <FileText size={18} className="mr-2" />
                    Analyze Document
                  </>
                )}
              </button>
            </div>
          )}

          <div className="mt-6">
            <h3 className="text-lg font-medium mb-3">How It Works</h3>
            <ol className="space-y-3 text-gray-300">
              <li className="flex items-start">
                <span className="bg-indigo-900/50 text-indigo-400 rounded-full w-6 h-6 flex items-center justify-center mr-2 flex-shrink-0">
                  1
                </span>
                <span>Upload any financial document (earnings reports, SEC filings, financial statements)</span>
              </li>
              <li className="flex items-start">
                <span className="bg-indigo-900/50 text-indigo-400 rounded-full w-6 h-6 flex items-center justify-center mr-2 flex-shrink-0">
                  2
                </span>
                <span>Our AI model analyzes the document content, extracting key financial data and insights</span>
              </li>
              <li className="flex items-start">
                <span className="bg-indigo-900/50 text-indigo-400 rounded-full w-6 h-6 flex items-center justify-center mr-2 flex-shrink-0">
                  3
                </span>
                <span>Receive a comprehensive analysis with key insights and investment recommendations</span>
              </li>
            </ol>
          </div>
        </motion.div>

        <motion.div
          initial={{ x: 20, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="card overflow-auto max-h-screen"
        >
          <h2 className="text-xl font-semibold mb-4 flex items-center sticky top-0 bg-gray-900 py-2 z-10">
            <FileText size={18} className="mr-2" />
            Analysis Results
          </h2>

          {analyzing ? (
            <div className="flex flex-col items-center justify-center py-12">
              <RefreshCw size={40} className="text-indigo-500 animate-spin mb-4" />
              <h3 className="text-xl font-medium mb-2">Analyzing Document</h3>
              <p className="text-gray-400 text-center max-w-md">
                Our AI is processing your document, extracting key financial data and generating insights...
              </p>
              {taskId && (
                <p className="text-xs text-gray-500 mt-4">Task ID: {taskId}</p>
              )}
            </div>
          ) : error ? (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <AlertTriangle size={40} className="text-red-500 mb-4" />
              <h3 className="text-xl font-medium mb-2">Analysis Error</h3>
              <p className="text-gray-400 max-w-md">{error}</p>
            </div>
          ) : analysisResult ? (
            <div className="space-y-6">
              {usesMockData && (
                <div className="bg-indigo-900/30 border border-indigo-800 p-3 rounded-lg mb-6">
                  <p className="text-sm text-indigo-300">
                    <AlertTriangle size={16} className="inline-block mr-2 text-indigo-400" />
                    Demo mode: Displaying sample analysis as API connection is unavailable
                  </p>
                </div>
              )}
              
              {/* Summary Section */}
              <div>
                <h3 className="text-lg font-medium mb-2">Document Summary</h3>
                <p className="text-gray-300 bg-gray-800/50 p-4 rounded-lg">{analysisResult.summary}</p>
              </div>
              
              {/* Complete Analysis Results Section */}
              <div>
                <h3 className="text-lg font-medium mb-2">Complete Analysis</h3>
                <div className="bg-gray-800/50 p-4 rounded-lg">
                  {analysisResult.analysisResults.split('\n\n').map((section, idx) => (
                    <div key={idx} className="mb-4">
                      {section.split('\n').map((line, lineIdx) => (
                        <p key={`line-${idx}-${lineIdx}`} className={`text-gray-300 ${line.startsWith('###') ? 'text-lg font-medium text-indigo-300 mt-2' : ''}`}>
                          {line.startsWith('###') ? line.replace('###', '') : line}
                        </p>
                      ))}
                    </div>
                  ))}
                </div>
              </div>
              
              {/* Financial Metrics Section */}
              <div>
                <h3 className="text-lg font-medium mb-2">Financial Metrics</h3>
                <div className="bg-gray-800/50 p-4 rounded-lg">
                  {analysisResult.financialMetrics.split('\n').map((metric, idx) => (
                    <p key={idx} className="text-gray-300 mb-1">{metric}</p>
                  ))}
                </div>
              </div>
              
              {/* Key Insights Section */}
              <div>
                <h3 className="text-lg font-medium mb-2">Key Insights</h3>
                <ul className="space-y-2">
                  {analysisResult.keyInsights.map((insight, index) => (
                    <li key={index} className="flex items-start">
                      <CheckCircle size={18} className="text-green-500 mr-2 flex-shrink-0 mt-0.5" />
                      <span className="text-gray-300">{insight}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Sentiment Analysis Section */}
              <div>
                <h3 className="text-lg font-medium mb-2">Sentiment Analysis</h3>
                <div
                  className={`flex items-center p-3 rounded-lg ${
                    analysisResult.sentiment === 'positive'
                      ? 'bg-green-900/20 text-green-500'
                      : analysisResult.sentiment === 'negative'
                      ? 'bg-red-900/20 text-red-500'
                      : 'bg-gray-700/50 text-gray-300'
                  }`}
                >
                  {analysisResult.sentiment === 'positive' ? (
                    <CheckCircle size={18} className="mr-2" />
                  ) : analysisResult.sentiment === 'negative' ? (
                    <AlertTriangle size={18} className="mr-2" />
                  ) : (
                    <div className="w-4 h-4 rounded-full bg-gray-400 mr-2"></div>
                  )}
                  <span className="capitalize">{analysisResult.sentiment} Outlook</span>
                </div>
              </div>

              {/* Recommendations Section */}
              <div>
                <h3 className="text-lg font-medium mb-2">Recommendations</h3>
                <ul className="space-y-2">
                  {analysisResult.recommendations.map((recommendation, index) => (
                    <li key={index} className="bg-gray-800/50 p-3 rounded-lg text-gray-300">
                      {recommendation}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <FileText size={40} className="text-gray-500 mb-4" />
              <h3 className="text-xl font-medium mb-2">No Document Analyzed Yet</h3>
              <p className="text-gray-400 max-w-md">
                Upload a financial document and click "Analyze Document" to see AI-powered insights here.
              </p>
            </div>
          )}
        </motion.div>
      </div>
    </div>
  );
};

export default DocumentAnalysis;