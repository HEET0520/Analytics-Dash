// frontend/components/dashboard/NewsFeed.jsx
"use client";
import React from 'react';

export default function NewsFeed({ items = [] }) {
  return (
    <div className="rounded-2xl p-[1px] bg-gradient-to-r from-brandStart/30 via-brandMid/20 to-brandEnd/30">
      <div className="card p-4 h-64 overflow-y-auto motion-safe:animate-in border-transparent">
        <h3 className="font-semibold mb-3">Latest News</h3>
        {items.length === 0 ? (
          <div className="text-sm text-neutral-500">No recent news available.</div>
        ) : (
          <ul className="space-y-3">
            {items.map((n, idx) => (
              <li key={idx} className="text-sm motion-safe:animate-in transition-transform duration-200 hover:translate-x-0.5" style={{ animationDelay: `${idx * 40}ms` }}>
                <a className="font-medium hover:underline" href={n.url || '#'} target="_blank" rel="noreferrer">
                  {n.title || n.headline || 'News Item'}
                </a>
                <div className="mt-1 flex items-center gap-2 text-xs text-neutral-500">
                  <span className="inline-flex items-center rounded-full bg-black/5 dark:bg-white/10 px-2 py-0.5">
                    {(n.source?.name || n.source) ?? 'Source'}
                  </span>
                  {n.published_at || n.date ? (
                    <span className="inline-flex items-center rounded-full bg-black/5 dark:bg-white/10 px-2 py-0.5">
                      {n.published_at || n.date}
                    </span>
                  ) : null}
                </div>
                {(n.description || n.summary) && (
                  <p className="text-xs mt-2 text-neutral-700 dark:text-neutral-300 leading-5">
                    {n.description || n.summary}
                  </p>
                )}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}


