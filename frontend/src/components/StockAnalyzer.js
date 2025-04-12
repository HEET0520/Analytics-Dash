import React, { useState } from 'react';
import axios from 'axios';

function StockAnalyzer() {
  const [ticker, setTicker] = useState('');
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleFileChange = (e) => setFile(e.target.files[0]);
  const handleTickerChange = (e) => setTicker(e.target.value);

  const handleSubmit = async () => {
    if (!ticker) return;
    setLoading(true);
    const formData = new FormData();
    formData.append('ticker', ticker);
    if (file) formData.append('file', file);

    try {
      const response = await axios.post('http://localhost:8000/analyze_stock', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setResult(response.data);
    } catch (error) {
      console.error('Error analyzing stock:', error);
    }
    setLoading(false);
  };

  return (
    <div>
      <h2>Stock Analysis</h2>
      <input
        type="text"
        value={ticker}
        onChange={handleTickerChange}
        placeholder="Enter stock ticker (e.g., AAPL)"
      />
      <input type="file" onChange={handleFileChange} />
      <button onClick={handleSubmit} disabled={loading}>
        {loading ? 'Analyzing...' : 'Analyze Stock'}
      </button>

      {result && (
        <div>
          <h3>Stock: {result.ticker}</h3>
          <p><strong>Analysis:</strong> {result.analysis}</p>
          <p><strong>Recent Prices:</strong> {result.stock_prices.join(', ')}</p>
          <p><strong>Confidence:</strong> {(result.confidence * 100).toFixed(2)}%</p>
        </div>
      )}
    </div>
  );
}

export default StockAnalyzer;