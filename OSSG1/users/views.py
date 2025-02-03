from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy

class CustomLoginView(LoginView):
    template_name = 'login.html'  # 指定自定义模板
    redirect_authenticated_user = True  # 如果用户已经登录，则自动跳转

    def get_success_url(self):
        return reverse_lazy('product-list')  # 登录成功后跳转到主页


from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import CustomUserCreationForm

class RegisterView(CreateView):
    form_class = CustomUserCreationForm  # 使用自定义的注册表单
    template_name = 'register.html'  # 指定注册页面模板
    success_url = reverse_lazy('login')  # 注册成功后跳转到登录页
