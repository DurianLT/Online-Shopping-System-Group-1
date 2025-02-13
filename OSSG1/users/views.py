from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy

class CustomLoginView(LoginView):
    template_name = 'users/login.html'  # 指定自定义模板
    redirect_authenticated_user = True  # 如果用户已经登录，则自动跳转

    def get_success_url(self):
        return reverse_lazy('product-list')  # 登录成功后跳转到主页


from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import CustomUserCreationForm

class RegisterView(CreateView):
    form_class = CustomUserCreationForm  # 使用自定义的注册表单
    template_name = 'users/register.html'  # 指定注册页面模板
    success_url = reverse_lazy('login')  # 注册成功后跳转到登录页

from django.views.generic import DetailView
from django.shortcuts import get_object_or_404
from .models import CustomUser

class UserProfileView(DetailView):
    model = CustomUser
    template_name = 'users/user_profile.html'  # 指定用户详情页面模板
    context_object_name = 'user'  # 上下文中用户对象的名称

    # 获取当前登录的用户
    def get_object(self):
        return get_object_or_404(CustomUser, id=self.request.user.id)
