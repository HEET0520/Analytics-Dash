import React from 'react';

export const Card = ({ children }: { children: React.ReactNode }) => {
  return (
    <div className="bg-white shadow-sm border border-gray-200 rounded-2xl">
      {children}
    </div>
  );
};

export const CardHeader = ({ children }: { children: React.ReactNode }) => {
  return (
    <div className="px-6 py-4 border-b border-gray-100 font-semibold text-lg">
      {children}
    </div>
  );
};

export const CardContent = ({ children }: { children: React.ReactNode }) => {
  return <div className="p-6">{children}</div>;
};
