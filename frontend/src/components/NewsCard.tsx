import React from 'react';
import { motion } from 'framer-motion';
import { Clock, TrendingUp, TrendingDown, Minus } from 'lucide-react';

interface NewsCardProps {
  title: string;
  source: string;
  time: string;
  sentiment: 'positive' | 'negative' | 'neutral';
}

const NewsCard: React.FC<NewsCardProps> = ({ title, source, time, sentiment }) => {
  return (
    <motion.div
      whileHover={{ x: 5 }}
      className="bg-gray-800/50 hover:bg-gray-700/50 p-4 rounded-lg border border-gray-700 cursor-pointer transition-all duration-200"
    >
      <div className="flex justify-between items-start mb-2">
        <h3 className="font-medium">{title}</h3>
        <div
          className={`ml-2 p-1 rounded-full flex-shrink-0 ${
            sentiment === 'positive'
              ? 'bg-green-900/30 text-green-500'
              : sentiment === 'negative'
              ? 'bg-red-900/30 text-red-500'
              : 'bg-gray-700/50 text-gray-400'
          }`}
        >
          {sentiment === 'positive' ? (
            <TrendingUp size={14} />
          ) : sentiment === 'negative' ? (
            <TrendingDown size={14} />
          ) : (
            <Minus size={14} />
          )}
        </div>
      </div>
      <div className="flex items-center text-sm text-gray-400">
        <span className="mr-3">{source}</span>
        <Clock size={12} className="mr-1" />
        <span>{time}</span>
      </div>
    </motion.div>
  );
};

export default NewsCard;