import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Clock, TrendingUp, TrendingDown, Minus } from 'lucide-react';

const NEWS_API_KEY = '43e6f0c16dad4e5695a19daa9a501dbf'; // Replace with your API key

interface NewsCardProps {
  title: string;
  source: string;
  time: string;
  sentiment: 'positive' | 'negative' | 'neutral';
}

const NewsCard: React.FC<NewsCardProps> = ({ title, source, time, sentiment }) => {
  const SentimentIcon = {
    positive: <TrendingUp size={14} />,
    negative: <TrendingDown size={14} />,
    neutral: <Minus size={14} />,
  }[sentiment];

  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      className="bg-gray-800/50 hover:bg-gray-700/50 p-4 rounded-lg border border-gray-700 transition-all"
    >
      <div className="flex justify-between items-start mb-2">
        <h3 className="font-medium line-clamp-2 text-sm">{title}</h3>
        <div
          className={`ml-2 p-1 rounded-full ${
            sentiment === 'positive'
              ? 'bg-green-900/30 text-green-500'
              : sentiment === 'negative'
              ? 'bg-red-900/30 text-red-500'
              : 'bg-gray-700/50 text-gray-400'
          }`}
        >
          {SentimentIcon}
        </div>
      </div>
      <div className="flex items-center text-xs text-gray-400">
        <span className="mr-3">{source}</span>
        <Clock size={12} className="mr-1" />
        <span>{new Date(time).toLocaleString()}</span>
      </div>
    </motion.div>
  );
};

const NewsFeed: React.FC = () => {
  const [newsData, setNewsData] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchNews = async () => {
      setIsLoading(true);
      try {
        const response = await fetch(`https://newsapi.org/v2/everything?q=stock&apiKey=${NEWS_API_KEY}`);
        const data = await response.json();
        setNewsData(data.articles || []);
      } catch (err) {
        console.error('Failed to fetch news:', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchNews();
  }, []);

  const getSentiment = (title: string): 'positive' | 'negative' | 'neutral' => {
    const lower = title.toLowerCase();
    if (lower.includes('growth') || lower.includes('gain') || lower.includes('positive')) return 'positive';
    if (lower.includes('fall') || lower.includes('drop') || lower.includes('decline')) return 'negative';
    return 'neutral';
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {isLoading ? (
        [...Array(6)].map((_, i) => (
          <div key={i} className="h-24 bg-gray-700/40 rounded-lg animate-pulse" />
        ))
      ) : (
        newsData.slice(0, 10).map((article, index) => (
          <NewsCard
            key={index}
            title={article.title}
            source={article.source.name}
            time={article.publishedAt}
            sentiment={getSentiment(article.title)}
          />
        ))
      )}
    </div>
  );
};

export default NewsFeed;
