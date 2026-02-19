import axios from 'axios'

const myBaseUrl = 'http://127.0.0.1:8000/'; // Base URL of the backend server
const AxiosInstance = axios.create({ // Create Axios instance with default settings
    baseURL: myBaseUrl,
    timeout: 5000,
    headers: {"Content-Type":"application/json", accept: "application/json"}
});

// Add token to request headers if user is logged in
AxiosInstance.interceptors.request.use((config) => {
  const token = localStorage.getItem("accessToken");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export default AxiosInstance