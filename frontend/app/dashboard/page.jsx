'use client';
import { useEffect, useState } from 'react';
import dynamic from 'next/dynamic';
import { getPrices, getAnalyze, getMarketContext, getSnapshots } from '../../lib/api';
import AiAnalysis from '../../components/dashboard/AiAnalysis';
import NewsFeed from '../../components/dashboard/NewsFeed';

const StockChart = dynamic(() => import('../../components/dashboard/StockChart'), {
  ssr: false,
  loading: () => (
    <div className="h-64 md:h-80 lg:h-96 card p-4 flex flex-col justify-end">
      <div className="flex items-center justify-between mb-2">
        <div className="h-5 w-28 rounded bg-black/10 dark:bg-white/10" />
        <div className="h-4 w-32 rounded bg-black/10 dark:bg-white/10" />
      </div>
      <div className="h-40 w-full rounded-lg bg-black/5 dark:bg-white/10" />
    </div>
  ),
});

const DEFAULT_TICKERS = [
  'AAPL','MSFT','GOOGL','AMZN','TSLA','NVDA','META','NFLX','RELIANCE.NS','TCS.NS'
];

export default function DashboardPage() {
  const [ticker, setTicker] = useState('AAPL');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [prices, setPrices] = useState([]);
  const [analysis, setAnalysis] = useState(null);
  const [news, setNews] = useState([]);
  const [recent, setRecent] = useState([]);
  const [chartType, setChartType] = useState('line'); // 'line' | 'bar'

  const load = async (t) => {
    setLoading(true);
    setError(null);
    try {
      const [priceRes, analysisRes, newsRes] = await Promise.all([
        getPrices(t).catch(() => null),
        getAnalyze(t).catch(() => null),
        getMarketContext(t).catch(() => null),
      ]);

      // Prices normalization
      const series = Array.isArray(priceRes?.prices)
        ? priceRes.prices
        : Array.isArray(priceRes)
          ? priceRes
          : [];
      setPrices(series);

      // Analysis
      setAnalysis(analysisRes || null);

      // News normalization
      const items = Array.isArray(newsRes?.news) ? newsRes.news : Array.isArray(newsRes) ? newsRes : [];
      const mapped = items.map((n) => ({
        title: n.title,
        source: n.source,
        date: n.published_at,
        summary: n.description,
        url: n.url,
      }));
      setNews(mapped);
    } catch (e) {
      setError(e?.message || 'Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(ticker); }, []);
  useEffect(() => {
    (async () => {
      try {
        const res = await getSnapshots(DEFAULT_TICKERS);
        setRecent(res?.snapshots || []);
      } catch {}
    })();
    const id = setInterval(async () => {
      try {
        const res = await getSnapshots(DEFAULT_TICKERS);
        setRecent(res?.snapshots || []);
      } catch {}
    }, 60_000);
    return () => clearInterval(id);
  }, []);

  const onSubmit = (e) => {
    e.preventDefault();
    if (!ticker) return;
    load(ticker);
  };

  return (
    <div className="mx-auto max-w-7xl space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1 space-y-4">
          <form onSubmit={onSubmit} className="flex gap-3 animate-in">
            <input
              value={ticker}
              onChange={(e) => setTicker(e.target.value.toUpperCase())}
              placeholder="Enter ticker (e.g., AAPL)"
              className="input"
            />
            <button type="submit" className="btn-primary whitespace-nowrap">{loading ? 'Loading…' : 'Load'}</button>
          </form>
          <div className="rounded-2xl p-[1px] bg-gradient-to-r from-brandStart/30 via-brandMid/20 to-brandEnd/30">
            <div className="card p-4 motion-safe:animate-in border-transparent">
              <div className="font-semibold mb-2">Recent Stocks</div>
            <ul className="divide-y divide-black/10 dark:divide-white/10">
              {recent.map((r) => (
                <li key={r.ticker} className="flex items-center justify-between py-2 text-sm">
                  <button className="text-left hover:underline" onClick={() => { setTicker(r.ticker); load(r.ticker); }}>{r.ticker}</button>
                  <span className="tabular-nums">
                    {r.price != null ? `$${r.price}` : '—'}{' '}
                    {typeof r.change_percent === 'number' && (
                      <span className={r.change_percent >= 0 ? 'text-green-500' : 'text-red-500'}>
                        ({r.change_percent >= 0 ? '+' : ''}{r.change_percent}%)
                      </span>
                    )}
                  </span>
                </li>
              ))}
            </ul>
            </div>
          </div>
        </div>
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <div className="text-sm text-neutral-500">Chart Type</div>
            <div className="inline-flex rounded-xl border border-black/10 dark:border-white/10 overflow-hidden">
              {['line','bar'].map((t) => (
                <button
                  key={t}
                  type="button"
                  onClick={() => setChartType(t)}
                  className={`px-3 py-1.5 text-sm capitalize ${chartType === t ? 'bg-gradient-to-r from-brandStart via-brandMid to-brandEnd text-white' : 'bg-transparent hover:bg-black/5 dark:hover:bg-white/5'}`}
                >
                  {t}
                </button>
              ))}
            </div>
          </div>
          <StockChart prices={prices} ticker={ticker} chartType={chartType} />
          <AiAnalysis analysis={analysis} />
        </div>
      </div>
      <NewsFeed items={news} />
    </div>
  );
}


