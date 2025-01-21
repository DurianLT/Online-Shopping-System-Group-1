import axios from 'axios';
// 创建 Axios 实例
const axiosInstance = axios.create({
    baseURL: 'http://127.0.0.1:8000/api/', // Django 后端 API 的根路径
    timeout: 5000, // 请求超时设置
    headers: {
        'Content-Type': 'application/json',
    },
});
// 导出 Axios 实例
export default axiosInstance;
