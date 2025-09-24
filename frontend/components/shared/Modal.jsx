// frontend/components/shared/Modal.jsx
"use client";
import React from 'react';

export default function Modal({ open, onClose, title, children, footer }) {
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/50" onClick={onClose} />
      <div className="relative w-full max-w-lg rounded-xl border border-black/10 dark:border-white/10 bg-white dark:bg-secondary text-neutral-900 dark:text-white shadow-xl">
        <div className="px-4 py-3 border-b border-black/10 dark:border-white/10 font-semibold">{title}</div>
        <div className="p-4">{children}</div>
        {footer ? <div className="px-4 py-3 border-t border-black/10 dark:border-white/10">{footer}</div> : null}
      </div>
    </div>
  );
}


