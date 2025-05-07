import Link from 'next/link';

export default function Home() {
  return (
    <div className="text-center">
      <h1 className="text-4xl font-bold mb-4">AI-Powered Stock Analysis & Prediction</h1>
      <p className="text-gray-400 mb-6">
        Make smarter investment decisions with our advanced AI algorithms that analyze market trends,
        financial documents, and news in real-time.
      </p>
      <div className="flex justify-center gap-4">
        <Link href="/dashboard">
          <button className="bg-primary-blue text-white px-6 py-2 rounded-lg">Explore Dashboard</button>
        </Link>
        <Link href="/document-analysis">
          <button className="bg-gray-600 text-white px-6 py-2 rounded-lg">Analyze Documents</button>
        </Link>
      </div>
      <div className="mt-10 bg-gradient-to-r from-purple-500 to-indigo-600 p-6 rounded-lg">
        <h2 className="text-2xl font-semibold">Powered by Advanced AI</h2>
        <p className="text-gray-200">Analyzing millions of data points to deliver precise predictions</p>
      </div>
      <div className="mt-10">
        <h2 className="text-3xl font-bold mb-6">Powerful Features</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-card-bg p-4 rounded-lg">
            <h3 className="text-xl font-semibold">Real-Time Stock Analysis</h3>
            <p className="text-gray-400">Get instant insights on stock performance with AI-powered analysis trends.</p>
          </div>
          <div className="bg-card-bg p-4 rounded-lg">
            <h3 className="text-xl font-semibold">Predictive Analytics</h3>
            <p className="text-gray-400">Advanced algorithms predict future stock movements with probabilistic consistency.</p>
          </div>
          <div className="bg-card-bg p-4 rounded-lg">
            <h3 className="text-xl font-semibold">Document Analysis</h3>
            <p className="text-gray-400">Upload financial documents for AI-powered analysis and extraction of key insights.</p>
          </div>
        </div>
      </div>
    </div>
  );
}