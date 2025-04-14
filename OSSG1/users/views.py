from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from .forms import CustomAuthenticationForm
from django.views.generic import CreateView
from .forms import CustomUserCreationForm
from django.views.generic import DetailView
from django.shortcuts import get_object_or_404
from .models import CustomUser
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from django.urls import reverse  # 导入reverse函数，用于获取URL
from django.views.generic import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView
from .models import Address
from django.views.generic import DeleteView
from django.contrib.auth import login

# 登录
class CustomLoginView(LoginView):
    template_name = 'users/login.html'  # 指定自定义模板
    redirect_authenticated_user = True  # 如果用户已经登录，则自动跳转

    form_class = CustomAuthenticationForm  # 使用自定义的表单

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request  # 传递 request 到表单
        return kwargs

    def get_success_url(self):
        return reverse_lazy('product-list')  # 登录成功后跳转到主页

    def form_invalid(self, form):
        # 在表单验证失败时返回错误
        return self.render_to_response(self.get_context_data(form=form))

# 注册
class RegisterView(CreateView):
    form_class = CustomUserCreationForm  # 使用自定义的注册表单
    template_name = 'users/register.html'  # 指定注册页面模板
    success_url = reverse_lazy('product-list')  # 注册成功后跳转到主页

    def form_valid(self, form):
        """
        当表单验证成功后执行：
        1. 保存用户信息
        2. 若填写了送货地址，则保存
        3. 自动登录
        4. 跳转到主页，并显示欢迎消息
        """
        user = form.save()  # 保存新用户
        login(self.request, user)  # 自动登录用户
        messages.success(self.request, f"欢迎 {user.username}，您的账号已成功注册！")
        return redirect(self.success_url)  # 跳转到主页或其他页面

    def form_invalid(self, form):
        """
        如果表单无效：
        1. 记录错误信息
        2. 渲染注册页面并返回错误信息
        """
        messages.error(self.request, "注册失败，请检查输入信息并重试。")
        return self.render_to_response(self.get_context_data(form=form))
# 用户中心
from django.views.generic import DetailView
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from users.models import Order

User = get_user_model()

class UserProfileView(DetailView):
    model = User
    template_name = 'users/user_profile.html'
    context_object_name = 'user'

    def get_object(self):
        return get_object_or_404(User, id=self.request.user.id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self.request.user

        # 统计当前用户各订单状态数量
        order_status_counts = {
            'Pending': Order.objects.filter(user=user, status='Pending').count(),
            'Paid': Order.objects.filter(user=user, status='Paid').count(),
            'Shipped': Order.objects.filter(user=user, status='Shipped').count(),
            'Completed': Order.objects.filter(user=user, status='Completed').count(),
            'Cancelled': Order.objects.filter(user=user, status='Cancelled').count(),
            'Refunding': Order.objects.filter(user=user, status='Refunding').count(),
            'Refunded': Order.objects.filter(user=user, status='Refunded').count(),
        }

        # 获取默认地址
        default_address = user.addresses.filter(is_default=True).first()

        context['order_status_counts'] = order_status_counts
        context['default_address'] = default_address

        return context


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

class AddressListView(LoginRequiredMixin, ListView):
    model = Address
    template_name = 'users/address_list.html'
    context_object_name = 'addresses'

    def get_queryset(self):
        # 只显示当前登录用户的地址
        return Address.objects.filter(user=self.request.user)

class AddressCreateView(LoginRequiredMixin, CreateView):
    model = Address
    template_name = 'users/address_form.html'
    fields = ['address', 'is_default']
    success_url = reverse_lazy('address_list')

    def form_valid(self, form):
        # 默认将地址设置为当前用户
        form.instance.user = self.request.user
        return super().form_valid(form)

class AddressUpdateView(LoginRequiredMixin, UpdateView):
    model = Address
    template_name = 'users/address_form.html'
    fields = ['address', 'is_default']
    success_url = reverse_lazy('address_list')

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

class AddressDeleteView(LoginRequiredMixin, DeleteView):
    model = Address
    template_name = 'users/address_confirm_delete.html'
    success_url = reverse_lazy('address_list')

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)
