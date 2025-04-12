import React, { useState } from 'react';
import axios from 'axios';

function DocumentUploader() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [query, setQuery] = useState('');
  const [queryResult, setQueryResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleFileChange = (e) => setFile(e.target.files[0]);

  const handleSubmit = async () => {
    if (!file) return;
    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);
    try {
      const response = await axios.post('http://localhost:8000/process_document', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setResult(response.data);
    } catch (error) {
      console.error('Error processing document:', error);
    }
    setLoading(false);
  };

  const handleQuery = async () => {
    if (!query) return;
    try {
      const response = await axios.get(`http://localhost:8000/query?query=${encodeURIComponent(query)}`);
      setQueryResult(response.data.results);
    } catch (error) {
      console.error('Error querying document:', error);
    }
  };

  return (
    <div>
      <input type="file" onChange={handleFileChange} />
      <button onClick={handleSubmit} disabled={loading}>
        {loading ? 'Processing...' : 'Process Document'}
      </button>

      {result && (
        <div>
          <h2>Extracted Text</h2>
          <p>{result.extracted_text}</p>
          <h2>Insights</h2>
          <p>{result.insights}</p>
          <h2>Market Context</h2>
          <p>{result.market_context}</p>
          <h2>RAG Results</h2>
          <ul>
            {result.rag_results.map((item, idx) => (
              <li key={idx}>{item}</li>
            ))}
          </ul>
        </div>
      )}

      <h2>Query Document</h2>
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Ask a question..."
      />
      <button onClick={handleQuery}>Query</button>

      {queryResult && (
        <div>
          <h3>Query Results</h3>
          <ul>
            {queryResult.map((item, idx) => (
              <li key={idx}>{item}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default DocumentUploader;