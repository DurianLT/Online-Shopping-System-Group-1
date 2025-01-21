<template>
    <div class="hello">
      <h1>{{ msg }}</h1>
      <ul>
        <li v-for="(user, index) in filteredUsers" :key="index" style="display: block;">
          {{ index }}--{{ user.username }}--{{ user.password }}
        </li>
      </ul>
      <form @submit.prevent="userSubmit">
        用户名：<input type="text" placeholder="user name" v-model="inputUser.username"><br>
        密码：<input type="text" placeholder="user password" v-model="inputUser.password"><br>
        <button type="submit">提交</button>
      </form>
    </div>
  </template>
  
  <script>
  import { getUsers, postUser } from '../api';  // 导入 api.js 中的接口方法
  
  export default {
    name: 'HelloUser',
    data() {
      return {
        msg: 'Welcome to Your Vue.js App',
        users: [],
        inputUser: {
          username: '',
          password: '',
        }
      };
    },
    methods: {
      async loadUsers() {
        try {
          const response = await getUsers();  // 调用 getUsers 方法
          this.users = response.data;
        } catch (error) {
          console.error('Error loading users:', error);
        }
      },
      async userSubmit() {
        try {
          const response = await postUser(this.inputUser.username, this.inputUser.password);  // 调用 postUser 方法
          console.log('User submitted:', response);
          this.loadUsers();  // 提交后重新加载用户列表
        } catch (error) {
          console.error('Error submitting user:', error);
        }
      }
    },
    created() {
      this.loadUsers();  // 组件加载时获取用户数据
    }
  };
  </script>
  