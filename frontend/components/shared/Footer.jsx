// frontend/components/shared/Footer.jsx
import React from 'react';

export default function Footer() {
  return (
    <footer className="w-full border-t border-black/10 dark:border-white/10 bg-white dark:bg-secondary/70 backdrop-blur supports-[backdrop-filter]:bg-white/60 dark:supports-[backdrop-filter]:bg-secondary/60 mt-auto">
      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <div className="md:flex md:items-center md:justify-between">
          <div className="text-center text-sm md:text-left text-neutral-500 dark:text-neutral-400">
            © {new Date().getFullYear()} Analytics Dash. All rights reserved.
          </div>
          <div className="mt-4 md:mt-0 flex items-center justify-center space-x-4">
            <a href="#" className="text-neutral-500 dark:text-neutral-400 hover:text-primary dark:hover:text-white transition">Privacy Policy</a>
            <a href="#" className="text-neutral-500 dark:text-neutral-400 hover:text-primary dark:hover:text-white transition">Terms of Service</a>
          </div>
        </div>
      </div>
    </footer>
  );
}