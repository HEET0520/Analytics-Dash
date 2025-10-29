// frontend/components/shared/Navbar.jsx
"use client";
import React from 'react';
import Link from 'next/link';

export default function Navbar({ theme, onToggleTheme }) {
  const [open, setOpen] = React.useState(false);
  return (
    <header className="sticky top-0 z-30 w-full border-b border-black/10 dark:border-white/10 bg-white/80 dark:bg-secondary/70 backdrop-blur supports-[backdrop-filter]:bg-white/60 dark:supports-[backdrop-filter]:bg-secondary/60">
      <div className="mx-auto max-w-7xl px-4 py-3">
        <div className="flex items-center justify-between">
          <div className="font-bold text-lg text-secondary dark:text-white">Analytics Dash</div>
          <div className="flex items-center gap-2 md:hidden">
            <button onClick={() => setOpen((v) => !v)} aria-label="Toggle menu" className="inline-flex h-10 w-10 items-center justify-center rounded-md border border-black/10 dark:border-white/10">☰</button>
            <button onClick={onToggleTheme} className="px-3 py-2 rounded-md bg-primary text-white text-sm hover:opacity-90">
              {theme === 'dark' ? 'Light' : 'Dark'} Mode
            </button>
          </div>
          <nav className="hidden md:flex items-center gap-6 text-sm">
            <Link href="/" className="hover:opacity-80">Home</Link>
            <Link href="/dashboard" className="hover:opacity-80">Dashboard</Link>
            <Link href="/document-analysis" className="hover:opacity-80">Document Analysis</Link>
            <button onClick={onToggleTheme} className="px-3 py-2 rounded-md bg-primary text-white text-sm hover:opacity-90">
              {theme === 'dark' ? 'Light' : 'Dark'} Mode
            </button>
          </nav>
        </div>
        {open && (
          <div className="mt-3 md:hidden grid gap-2 text-sm">
            <Link href="/" className="rounded-md px-3 py-2 hover:bg-black/5 dark:hover:bg-white/10">Home</Link>
            <Link href="/dashboard" className="rounded-md px-3 py-2 hover:bg-black/5 dark:hover:bg-white/10">Dashboard</Link>
            <Link href="/document-analysis" className="rounded-md px-3 py-2 hover:bg-black/5 dark:hover:bg-white/10">Document Analysis</Link>
          </div>
        )}
      </div>
    </header>
  );
}


