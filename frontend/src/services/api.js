const API_BASE_URL = '/api';

export const fetchDashboard = async (city) => {
  const response = await fetch(`${API_BASE_URL}/v1/city/${city}/dashboard`);
  if (!response.ok) throw new Error('Network response was not ok');
  return response.json();
};