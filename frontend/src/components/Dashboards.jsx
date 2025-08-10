import { useState, useEffect, useCallback } from 'react';
import { fetchDashboard } from '../services/api';
import WeatherCard from './WeatherCard';
import NewsCard from './NewsCard';
import CurrencyCard from './CurrencyCard';

function Dashboard() {
  const [data, setData] = useState(null);
  const [cityInput, setCityInput] = useState("Moscow");
  const [city, setCity] = useState("Moscow");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await fetchDashboard(city);
      setData(result);
      console.log("Full dashboard data:", result);
      console.log("News raw data:", result.news);

    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [city]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleCityChange = (e) => {
    setCityInput(e.target.value);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (cityInput.trim()) {
      setCity(cityInput.trim());
    }
  };

  return (
    <div className="container mx-auto px-4 py-6 bg-gray-50 min-h-screen">
      <h1 className="text-4xl font-extrabold text-gray-900 mb-8 text-center tracking-tight">
        🌍 City Dashboard
      </h1>

      {/* Форма поиска */}
      <form 
        onSubmit={handleSubmit} 
        className="mb-8 flex flex-col sm:flex-row gap-3 justify-center items-center"
      >
        <input
          type="text"
          value={cityInput}
          onChange={handleCityChange}
          className="border border-gray-300 p-3 rounded-xl w-full sm:w-72 shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 transition"
          placeholder="Enter city name"
        />
        <button
          type="submit"
          className="bg-blue-600  hover:cursor-pointer text-white px-6 py-3 rounded-xl hover:bg-blue-700 active:scale-95 transition font-semibold shadow-sm"
        >
          Update
        </button>
      </form>

      {/* Состояния загрузки / ошибки */}
      {loading && (
        <p className="text-blue-500 text-lg text-center animate-pulse">
          Loading...
        </p>
      )}
      {error && (
        <p className="text-red-500 text-lg text-center">
          ❌ Error: {error}
        </p>
      )}

      {/* Карточки данных */}
      {data && !error && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="col-span-1">
            <WeatherCard data={data.weather} />
          </div>
          <div className="col-span-1 lg:col-span-2">
            <NewsCard data={data.news.news} />
          </div>
          <div className="col-span-1">
            <CurrencyCard data={data.currency} />
          </div>
        </div>
      )}
    </div>
  );
}

export default Dashboard;
