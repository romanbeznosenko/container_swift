import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const fetchSwiftCodes = async (params = {}) => {
  try {
    const { skip = 0, limit = 10, country, isHeadquarter, search } = params;

    const queryParams = new URLSearchParams();
    queryParams.append('skip', skip.toString());
    queryParams.append('limit', limit.toString());

    if (country) {
      queryParams.append('country', country);
    }

    if (isHeadquarter !== undefined) {
      queryParams.append('is_headquarter', isHeadquarter.toString());
    }

    const response = await apiClient.get(`/api/v1/swift-code/?${queryParams.toString()}`);

    let data = response.data;
    if (search) {
      const searchTerm = search.toLowerCase();
      data = data.filter(code =>
        code.swiftCode.toLowerCase().includes(searchTerm) ||
        code.address.toLowerCase().includes(searchTerm) ||
        code.countryName.toLowerCase().includes(searchTerm)
      );
    }

    return data;
  } catch (error) {
    console.error('Error fetching SWIFT codes:', error);
    throw error;
  }
};

export const fetchSwiftCodesCount = async (params = {}) => {
  try {
    const { country, isHeadquarter } = params;

    const queryParams = new URLSearchParams();

    if (country) {
      queryParams.append('country', country);
    }

    if (isHeadquarter !== undefined) {
      queryParams.append('is_headquarter', isHeadquarter.toString());
    }

    try {
      const response = await apiClient.get(`/api/v1/swift-code/count?${queryParams.toString()}`);
      return response.data;
    } catch (error) {
      console.log("Count endpoint not available, estimating count...");
      const response = await apiClient.get(`/api/v1/swift-code/?${queryParams.toString()}&limit=1000&skip=0`);

      const count = Array.isArray(response.data) ? response.data.length : 0;
      return { count: count < 1000 ? count : 1000 };
    }
  } catch (error) {
    console.error('Error fetching SWIFT codes count:', error);
    throw error;
  }
};

export const fetchSwiftCodeByCode = async (swiftCode) => {
  try {
    const response = await apiClient.get(`/api/v1/swift-code/${swiftCode}`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching SWIFT code ${swiftCode}:`, error);
    throw error;
  }
};

export const createSwiftCode = async (swiftCodeData) => {
  try {
    const response = await apiClient.post('/api/v1/swift-code/', swiftCodeData);
    return response.data;
  } catch (error) {
    console.error('Error creating SWIFT code:', error);
    throw error;
  }
};

export const deleteSwiftCode = async (swiftCode) => {
  try {
    await apiClient.delete(`/api/v1/swift-code/${swiftCode}`);
    return true;
  } catch (error) {
    console.error(`Error deleting SWIFT code ${swiftCode}:`, error);
    throw error;
  }
};