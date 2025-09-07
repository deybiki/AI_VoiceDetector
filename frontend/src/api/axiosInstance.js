import axios from 'axios';

const BASE_URL = process.env.REACT_APP_EXPRESS_BACKEND_URI;

const axiosInstance = axios.create({
  baseURL: process.env.REACT_APP_EXPRESS_BACKEND_URI,
  headers: {
    'Content-Type': 'application/json',
  },
});

export default axiosInstance;
