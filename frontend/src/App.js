import React from 'react';
import DocumentUploader from './components/DocumentUploader';
import StockAnalyzer from './components/StockAnalyzer';
import './App.css';

function App() {
  return (
    <div className="App">
      <h1>Agentic Document Processor</h1>
      <DocumentUploader />
      <StockAnalyzer />
    </div>
  );
}

export default App;