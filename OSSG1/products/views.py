from django.shortcuts import render

# Create your views here.
from django.views.generic import ListView, DetailView
from .models import Product

class ProductListView(ListView):
    model = Product
    template_name = 'product_list.html'  # 指定模板
    context_object_name = 'products'  # 上下文变量名

class ProductDetailView(DetailView):
    model = Product
    template_name = 'product_detail.html'  # 指定模板
    context_object_name = 'product'  # 上下文变量名
