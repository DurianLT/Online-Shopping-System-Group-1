from django.urls import path
from .views import hello_world

urlpatterns = [
    path('hello/', hello_world),  # 配置 API 路径
]
