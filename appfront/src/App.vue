<template>
  <div id="app">
    <h1>{{ message }}</h1>
  </div>
</template>

<script>
import axiosInstance from './axios-config';

export default {
  name: 'App',
  data() {
    return {
      message: '',
    };
  },
  created() {
    // 在组件创建时请求后端数据
    axiosInstance.get('hello/')
      .then(response => {
        this.message = response.data.message;  // 设置返回的消息
      })
      .catch(error => {
        console.error('Error fetching data:', error);
      });
  },
};
</script>
