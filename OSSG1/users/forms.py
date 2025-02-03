from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()  # 获取当前使用的用户模型

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, max_length=255)  # 强制要求输入 email

    class Meta:
        model = User  # 使用自定义的用户模型
        fields = ('username', 'email', 'password1', 'password2')  # 仅包含 username、email 和密码
