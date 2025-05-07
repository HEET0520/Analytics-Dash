import { NewsItem } from '../lib/types';

interface NewsFeedProps {
  news: NewsItem[];
}

export function NewsFeed({ news }: NewsFeedProps) {
  return (
    <div>
      {news.length > 0 ? (
        <ul>
          {news.map((item, index) => (
            <li key={index} className="mb-4">
              <a href={item.url} target="_blank" rel="noopener noreferrer" className="text-primary-blue">
                {item.title}
              </a>
              <p className="text-gray-400 text-sm">{item.source} • {item.published_at}</p>
              <p className="text-gray-400">{item.description}</p>
            </li>
          ))}
        </ul>
      ) : (
        <p>Loading news...</p>
      )}
    </div>
  );
}