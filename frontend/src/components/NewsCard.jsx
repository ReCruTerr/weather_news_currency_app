import React from "react";

function NewsCard({ data }) {
  // Унифицируем данные в массив
  let newsArray = [];

  if (Array.isArray(data)) {
    newsArray = data;
  } else if (data && typeof data === "object" && Array.isArray(data.articles)) {
    newsArray = data.articles;
  } else if (data && typeof data === "object") {
    // Если это объект вида { 0: {...}, 1: {...} }
    newsArray = Object.values(data);
  }

  return (
    <div className="bg-white shadow-lg rounded-2xl p-6">
      <h2 className="text-xl font-semibold mb-4">Latest News</h2>
      {newsArray.length > 0 ? (
        <ul className="space-y-3">
          {newsArray.slice(0, 5).map((news, index) => (
            <li
              key={index}
              className="border-b border-gray-200 pb-2 last:border-0"
            >
              <a
                href={news.url || "#"}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:underline"
              >
                {news.title || "No title"}
              </a>
              {news.source && (
                <p className="text-sm text-gray-500">{news.source}</p>
              )}
            </li>
          ))}
        </ul>
      ) : (
        <p className="text-gray-500">No news data</p>
      )}
    </div>
  );
}

export default NewsCard;
