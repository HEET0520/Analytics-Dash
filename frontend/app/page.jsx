'use client';
import Link from 'next/link';

export default function Home() {
  return (
    <div className="mx-auto max-w-7xl">
      <section className="pt-10 md:pt-16 text-center">
        <h1 className="text-4xl md:text-6xl font-extrabold tracking-tight text-secondary dark:text-white">
          AI Financial Analysis Platform
        </h1>
        <p className="mt-4 text-lg md:text-2xl text-neutral-700 dark:text-neutral-300 max-w-3xl mx-auto">
          Actionable insights, real-time prices, and document intelligence in one dashboard.
        </p>
        <div className="mt-8 flex items-center justify-center gap-3">
          <Link href="/dashboard" className="btn-primary">Open Dashboard</Link>
          <Link href="/document-analysis" className="btn-secondary">Analyze Document</Link>
        </div>
      </section>

      <section className="mt-14 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {[
          { title: 'AI Analysis', desc: 'Summaries, sentiment, and recommendations for any ticker.' },
          { title: 'Market Context', desc: 'Latest news and signals to inform your decisions.' },
          { title: 'Document IQ', desc: 'Upload filings, reports, and get structured metrics.' },
        ].map((f) => (
          <div key={f.title} className="card p-6">
            <div className="text-xl font-semibold mb-2">{f.title}</div>
            <p className="text-sm text-neutral-700 dark:text-neutral-300">{f.desc}</p>
          </div>
        ))}
      </section>
    </div>
  );
}
