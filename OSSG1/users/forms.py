from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password

CustomUser = get_user_model()  # 获取自定义用户模型

class CustomUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label="密码", widget=forms.PasswordInput)
    password2 = forms.CharField(label="确认密码", widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ['username', 'email']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError("该邮箱已被注册，请使用其他邮箱。")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if CustomUser.objects.filter(username=username).exists():
            raise ValidationError("该用户名已被注册，请使用其他用户名。")
        return username

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 != password2:
            raise ValidationError("密码和确认密码不一致，请重新输入。")
        if password1 and password1 == self.cleaned_data.get('username'):
            raise ValidationError("密码不能与用户名相似，请重新设置密码。")
        return password2

    def save(self, commit=True):
        # 获取 cleaned_data 中的密码字段
        user = super().save(commit=False)
        user.password = make_password(self.cleaned_data["password1"])  # 加密密码并保存
        if commit:
            user.save()  # 保存到数据库
        return user



from django import forms
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from users.models import CustomUser  # 引入自定义用户模型


class CustomAuthenticationForm(forms.Form):
    username = forms.CharField(label="用户名或邮箱", max_length=255)
    password = forms.CharField(label="密码", widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)  # 获取 request 参数
        super().__init__(*args, **kwargs)  # 调用父类的初始化方法

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if not username or not password:
            raise ValidationError("用户名或邮箱和密码不能为空")

        # 尝试通过邮箱（email）查找用户
        user = None
        if '@' in username:  # 如果输入的是邮箱
            try:
                user = CustomUser.objects.get(email=username)
                print(1)
            except CustomUser.DoesNotExist:
                try:
                    print(2)
                    user = CustomUser.objects.get(username=username)
                except CustomUser.DoesNotExist:
                    print(3)
                    raise ValidationError("用户不存在")

        else:
            try:
                print(4)
                user = CustomUser.objects.get(username=username)
            except CustomUser.DoesNotExist:
                print(5)
                raise ValidationError("用户不存在")

        # 如果通过邮箱找到了用户，尝试验证密码
        if user and not user.check_password(password):
            raise ValidationError("密码不正确")

        if user is None:
            raise ValidationError("用户名或邮箱和密码不匹配")

        self.user = user
        return self.cleaned_data

    def get_user(self):
        """
        返回已经认证的用户对象
        """
        return self.user
