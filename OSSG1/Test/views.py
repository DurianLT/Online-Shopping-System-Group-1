from django.shortcuts import render

from rest_framework.viewsets import ModelViewSet
from Test.models import UserInfo
from Test.serializer import UserInfoSerializer
from Test.filter import UserInfoFilter
from django_filters.rest_framework import DjangoFilterBackend


class UserInfoViewSet(ModelViewSet):
    queryset = UserInfo.objects.all()
    serializer_class = UserInfoSerializer

    filter_class = UserInfoFilter
    filter_fields = ['username']
    search_fields = ('username',)
