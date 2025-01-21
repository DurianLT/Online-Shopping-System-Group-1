import axiosInstance from './axios';  // 引入axios实例

// 获取用户列表
export const getUsers = () => axiosInstance.get('v1/UserInfo/');

// 提交用户数据
export const postUser = (username, password) => axiosInstance.post('v1/UserInfo/', {
  username,
  password,
});
