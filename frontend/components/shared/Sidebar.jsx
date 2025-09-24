// frontend/components/shared/Sidebar.jsx
"use client";
import React from 'react';
import Link from 'next/link';

export default function Sidebar({ open, onClose }) {
  return (
    <>
      {/* Overlay */}
      <div
        className={`fixed inset-0 z-30 bg-black/40 transition-opacity md:hidden ${open ? 'opacity-100' : 'pointer-events-none opacity-0'}`}
        onClick={onClose}
      />

      <aside className={`fixed z-40 inset-y-0 left-0 w-72 bg-white dark:bg-secondary text-neutral-900 dark:text-white border-r border-black/10 dark:border-white/10 transform transition-transform md:translate-x-0 md:static md:inset-auto ${open ? 'translate-x-0' : '-translate-x-full'}`}>
        <div className="h-16 flex items-center px-4 border-b border-black/10 dark:border-white/10 font-semibold">Menu</div>
        <nav className="p-4 space-y-1 text-sm">
          <Link className="block rounded-md px-3 py-2 hover:bg-black/5 dark:hover:bg-white/10" href="/">Home</Link>
          <Link className="block rounded-md px-3 py-2 hover:bg-black/5 dark:hover:bg-white/10" href="/dashboard">Dashboard</Link>
          <Link className="block rounded-md px-3 py-2 hover:bg-black/5 dark:hover:bg-white/10" href="/document-analysis">Document Analysis</Link>
        </nav>
      </aside>
    </>
  );
}


