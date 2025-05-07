export function Sidebar() {
    return (
      <aside className="w-64 bg-card-bg p-4">
        <div className="mb-6">
          <h3 className="text-lg font-semibold">FinanceAI</h3>
          <p className="text-gray-400">AI-powered market analysis and stock prediction with probabilistic consistency.</p>
        </div>
        <div className="mb-6">
          <h4 className="font-semibold">Features</h4>
          <ul className="text-gray-400">
            <li>Stock Analysis</li>
            <li>Market Predictions</li>
            <li>Document Analysis</li>
            <li>Financial News</li>
          </ul>
        </div>
        <div className="mb-6">
          <h4 className="font-semibold">Resources</h4>
          <ul className="text-gray-400">
            <li>Documentation</li>
            <li>API Reference</li>
            <li>Blog</li>
            <li>Support</li>
          </ul>
        </div>
        <div>
          <h4 className="font-semibold">Legal</h4>
          <ul className="text-gray-400">
            <li>Terms of Service</li>
            <li>Privacy Policy</li>
            <li>Cookie Policy</li>
            <li>Disclaimer</li>
          </ul>
        </div>
      </aside>
    );
  }