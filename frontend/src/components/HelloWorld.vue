<template>
  <div class="hello">
      <h1>{{ msg }}</h1>
      <ul>
          <li v-for="(user,index) in users" :key="index" style="display: block;">
              {{ index }}--{{ user.username }}--{{ user.password }}
          </li>
      </ul>
      <form action="">
          用户名：<input type="text" placeholder="user name" v-model="inputUser.username"><br>

          密码：<input type="text" placeholder="user password" v-model="inputUser.password"><br>
          <button type="submit" @click="userSubmit()">提交</button>
      </form>
  </div>
</template>

<script>
import { getUsers,postUser } from '../api/api.js';
export default {
  name:'hellouser',
  data () {
      return {
          msg:'Welcome to Your Vue.js App',
          users:[
              {username:'test1',password:'test1'},
              {username:'test2',password:'test2'}
          ],
          inputUser:{
              "username":"",
              "password":"",
          }
      }
  },
  methods:{
      loadUsers(){},
      userSubmit(){}
  },
  created: function(){
      this.loadUsers()
  }
}
</script>
