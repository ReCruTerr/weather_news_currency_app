import CardWrapper from './CardWrapper';

function WeatherCard({ data }) {
  if (!data) {
    return (
      <CardWrapper title="Weather">
        <p className="text-gray-500">No weather data</p>
      </CardWrapper>
    );
  }

  return (
    <CardWrapper title={`Weather in ${data.city}`}>
      <div className="flex flex-col items-center space-y-3">
        <span className="text-5xl">{data.icon || '🌤️'}</span>
        <p className="text-3xl font-bold">{data.temperature}°C</p>
        <p className="text-gray-600">{data.description}</p>
      </div>
    </CardWrapper>
  );
}

export default WeatherCard;
