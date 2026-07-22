import axios from 'axios';

const axiosInstance = axios.create({
    baseURL: 'http://127.0.0.1:8000/api/',
});
axiosInstance.interceptors.request.use((config) => {
    const accessToken = localStorage.getItem('access_token');
    if (accessToken) {
        config.headers.Authorization = `Bearer ${accessToken}`;
    }
    return config;
});
// response interceptor - jab response 401 (expired token) aaye , tab chlta hai
axiosInstance.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;
    
    if (error.response?.status === 401 && !originalRequest._retry) {
        originalRequest._retry = True;

        try {
            const refreshToken = localStorage.getItem('refresh_token');
        const res = await axios.post('http://127.0.0.1:8000/api/token/refresh/', {
        refresh: refreshToken,
        });
        
        localStorage.setItem('access_token', res.data.access);

        // original request ko naye token ke saath dobara bhejo

        originalRequest.headers.Authorization = `Bearer ${res.data.access}`;
        return axiosInstance(originalRequest);
        }catch(refreshError) {
        // refresher bhi fail hua - matlb refresh token bhi expire ho chuka
        localStorage.removeItem('access_token');
        localStorage.removeItem('refreshError');
        window.location.href = '/login';
        return Promise.reject(refreshError);
        }
    }

    return Promise.reject(Error);
}
);

export default axiosInstance;

