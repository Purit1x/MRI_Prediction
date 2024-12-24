//定制请求的实例

//导入axios  npm install axios
import axios from 'axios';
import { toast } from '@/utils/util';

const BASE_URL = 'http://121.40.197.3:10010';

const instance = axios.create({
    baseURL: BASE_URL,
    headers: {
        'Content-Type': 'application/json'
    }
});

// 添加请求拦截器
instance.interceptors.request.use(
    config => {
        // 从 localStorage 获取 jwt token
        const token = localStorage.getItem('jwt');
        if (token) {
            // 直接设置 token,不添加 Bearer 前缀
            config.headers.Authorization = token;
            console.log('Request headers:', config.headers); // 调试用
        }
        return config;
    },
    error => {
        return Promise.reject(error);
    }
);

// 添加响应拦截器
instance.interceptors.response.use(
    response => {
        return response.data;
    },
    error => {
        const msg = error.response?.data?.msg || "请求失败";
        toast(msg, 'error');
        return Promise.reject(error);
    }
);

export default instance;