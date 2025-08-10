import CardWrapper from './CardWrapper';

function CurrencyCard({ data }) {
  if (!data || Object.keys(data).length === 0) {
    return (
      <CardWrapper title="Currency Rates">
        <p className="text-gray-500">No currency data</p>
      </CardWrapper>
    );
  }

  return (
    <CardWrapper title="Currency Rates">
      <ul className="space-y-2">
        {Object.entries(data).map(([currency, rate]) => (
          <li key={currency} className="flex justify-between border-b border-gray-100 pb-1">
            <span className="font-medium">{currency}</span>
            <span className="text-gray-700">{rate}</span>
          </li>
        ))}
      </ul>
    </CardWrapper>
  );
}

export default CurrencyCard;
