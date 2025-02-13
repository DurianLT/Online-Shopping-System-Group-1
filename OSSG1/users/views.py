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

from django.contrib.auth import get_user_model
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views import View

User = get_user_model()

class PasswordResetByUsernameView(View):
    def get(self, request):
        return render(request, 'users/password_reset_by_username.html')  # 返回一个简单的表单页面

    def post(self, request):
        username = request.POST.get('username')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')

        if not username or not new_password1 or not new_password2:
            messages.error(request, "所有字段都是必填的！")
            return render(request, 'users/password_reset_by_username.html')

        if new_password1 != new_password2:
            messages.error(request, "新密码和确认密码不一致！")
            return render(request, 'users/password_reset_by_username.html')

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, "该用户名不存在！")
            return render(request, 'users/password_reset_by_username.html')

        # 设置新密码并保存
        user.set_password(new_password1)
        user.save()

        messages.success(request, "密码已成功重置！")
        return redirect('login')  # 重定向到登录页面


from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.urls import reverse  # 导入reverse函数，用于获取URL
from django.views.generic import UpdateView

User = get_user_model()

class UserProfileUpdateView(UpdateView):
    model = User
    template_name = 'users/edit_profile.html'  # 编辑个人信息页面模板
    fields = ['username', 'email']  # 只允许编辑用户名和邮箱
    context_object_name = 'user'

    # 获取当前登录用户的数据进行编辑
    def get_object(self):
        return self.request.user  # 获取当前登录的用户

    # 更新成功后重定向至用户中心
    def get_success_url(self):
        messages.success(self.request, "个人信息更新成功！")
        return reverse('product-list')  # 返回URL字符串，重定向到用户中心页面

    # 重写form_valid方法，确保表单数据处理正确
    def form_valid(self, form):
        # 检查并确保用户名和邮箱字段的处理是正确的
        username = form.cleaned_data.get('username')
        email = form.cleaned_data.get('email')

        # 如果你不需要URL编码，可以省略下面的编码处理
        form.instance.username = username
        form.instance.email = email

        return super().form_valid(form)
