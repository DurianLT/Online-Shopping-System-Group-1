from django.shortcuts import render
from django.http import JsonResponse
from django.views.generic.edit import FormView
from .models import UserInfo
from django import forms

# 创建一个简单的表单类
class LoginForm(forms.Form):
    username = forms.CharField(max_length=128, label='用户名')
    password = forms.CharField(widget=forms.PasswordInput(), max_length=128, label='密码')

class LoginView(FormView):
    template_name = 'testadmin/login.html'
    form_class = LoginForm

    def form_valid(self, form):
        # 获取表单数据
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        
        # 验证用户是否存在
        try:
            user = UserInfo.objects.get(username=username, password=password)
            response = {'message': '登录成功'}
            return JsonResponse(response)  # 返回 JSON 响应
        except UserInfo.DoesNotExist:
            response = {'message': '用户名或密码错误'}
            return JsonResponse(response, status=400)
