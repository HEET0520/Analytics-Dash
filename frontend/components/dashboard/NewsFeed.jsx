// frontend/components/dashboard/NewsFeed.jsx
"use client";
import React from 'react';

export default function NewsFeed({ items = [] }) {
  return (
    <div className="card p-4 h-64 overflow-y-auto">
      <h3 className="font-semibold mb-3">Latest News</h3>
      {items.length === 0 ? (
        <div className="text-sm text-neutral-500">No recent news available.</div>
      ) : (
        <ul className="space-y-3">
          {items.map((n, idx) => (
            <li key={idx} className="text-sm">
              <a className="font-medium hover:underline" href={n.url || '#'} target="_blank" rel="noreferrer">
                {n.title || n.headline || 'News Item'}
              </a>
              <div className="text-xs text-neutral-500">{(n.source?.name || n.source) ?? 'Source'} • {n.published_at || n.date || ''}</div>
              {(n.description || n.summary) && <p className="text-xs mt-1 text-neutral-700 dark:text-neutral-300">{n.description || n.summary}</p>}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}


