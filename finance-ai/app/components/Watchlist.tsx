'use client';

import { useState, useEffect } from 'react';
import { fetchAllData } from '../lib/api';
import { WatchlistItem } from '../lib/types';

interface WatchlistProps {
  onSelectTicker: (ticker: string) => void;
}

export function Watchlist({ onSelectTicker }: WatchlistProps) {
  const [watchlist, setWatchlist] = useState<WatchlistItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    const loadWatchlist = async () => {
      try {
        setLoading(true);
        // Predefined list of tickers for the watchlist
        const tickers = ['BRDCY', 'SCDA', 'GRMZF', 'ANL', 'CIMPRB', 'TE', 'RBIL', 'ESGE', 'IMPUY'];
        const watchlistData: WatchlistItem[] = [];

        for (const ticker of tickers) {
          try {
            const data = await fetchAllData(ticker);
            if (data.errors && data.errors.length > 0) {
              console.warn(`Failed to fetch data for ${ticker}: ${data.errors.join(', ')}`);
              continue;
            }

            const latestPrice =
              data.historical_prices.length > 0
                ? data.historical_prices[data.historical_prices.length - 1].close
                : 0.0;
            const change =
              data.historical_prices.length > 1
                ? ((latestPrice - data.historical_prices[data.historical_prices.length - 2].close) /
                    data.historical_prices[data.historical_prices.length - 2].close) *
                  100
                : 0.0;

            watchlistData.push({
              ticker,
              name: data.basic_financials?.name || ticker,
              price: latestPrice,
              change: parseFloat(change.toFixed(2)),
            });
          } catch (err) {
            console.warn(`Error fetching data for ${ticker}: ${err}`);
          }
        }

        setWatchlist(watchlistData);
      } catch (err) {
        setError('Failed to load watchlist');
      } finally {
        setLoading(false);
      }
    };

    loadWatchlist();
  }, []);

  if (loading) {
    return <p className="text-gray-400">Loading watchlist...</p>;
  }

  if (error) {
    return <p className="text-red-500">{error}</p>;
  }

  return (
    <div className="bg-card-bg p-4 rounded-lg">
      <h3 className="text-lg font-semibold mb-2">Watchlist</h3>
      {watchlist.length > 0 ? (
        <ul>
          {watchlist.map((stock) => (
            <li
              key={stock.ticker}
              className="flex justify-between items-center py-2 cursor-pointer hover:bg-gray-600 rounded-lg px-2"
              onClick={() => onSelectTicker(stock.ticker)}
            >
              <div>
                <p className="font-semibold">{stock.ticker}</p>
                <p className="text-gray-400 text-sm">{stock.name}</p>
              </div>
              <div className="text-right">
                <p>${stock.price.toFixed(2)}</p>
                <p className={stock.change >= 0 ? 'text-green-500' : 'text-red-500'}>
                  {stock.change >= 0 ? '+' : ''}{stock.change}%
                </p>
              </div>
            </li>
          ))}
        </ul>
      ) : (
        <p className="text-gray-400">No stocks in watchlist</p>
      )}
    </div>
  );
}