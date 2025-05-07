import Link from 'next/link';
import { HomeIcon, ChartBarIcon, DocumentTextIcon } from '@heroicons/react/24/outline';

export function Navbar() {
  return (
    <nav className="bg-card-bg p-4 flex justify-between items-center">
      <div className="flex items-center gap-2">
        <ChartBarIcon className="h-6 w-6 text-primary-blue" />
        <Link href="/" className="text-xl font-bold text-primary-blue">
          FinanceAI
        </Link>
      </div>
      <div className="flex gap-4">
        <Link href="/" className="flex items-center gap-2 text-gray-400 hover:text-white">
          <HomeIcon className="h-5 w-5" />
          Home
        </Link>
        <Link href="/dashboard" className="flex items-center gap-2 text-gray-400 hover:text-white">
          <ChartBarIcon className="h-5 w-5" />
          Dashboard
        </Link>
        <Link href="/document-analysis" className="flex items-center gap-2 text-gray-400 hover:text-white">
          <DocumentTextIcon className="h-5 w-5" />
          Document Analysis
        </Link>
      </div>
    </nav>
  );
}