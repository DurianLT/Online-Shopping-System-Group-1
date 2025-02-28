from django.shortcuts import render

# Create your views here.
from django.views.generic import ListView, DetailView

from users.models import Wishlist
from .models import Product

class ProductListView(ListView):
    model = Product
    template_name = 'products/product_list.html'  # 指定模板
    context_object_name = 'products'  # 上下文变量名

    # 重写get_queryset来过滤掉 hidden=True 的商品
    def get_queryset(self):
        return Product.objects.filter(hidden=False)


from django.shortcuts import redirect
from .models import Product

from django.shortcuts import redirect


class ProductDetailView(DetailView):
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # 检查用户是否登录
        if user.is_authenticated:
            product = self.get_object()
            # 检查当前用户是否已收藏该商品
            context['is_in_wishlist'] = Wishlist.objects.filter(user=user, product=product).exists()
        else:
            # 如果用户未登录，则无法收藏商品
            context['is_in_wishlist'] = False

        return context

    def post(self, request, *args, **kwargs):
        product = self.get_object()
        user = request.user

        # 检查用户是否登录
        if not user.is_authenticated:
            return redirect('login')  # 用户未登录，重定向到登录页面

        # 处理收藏功能
        if 'add_to_wishlist' in request.POST:
            if not Wishlist.objects.filter(user=user, product=product).exists():
                # 如果当前商品不在用户的收藏夹中，添加到收藏夹
                Wishlist.objects.create(user=user, product=product)
        elif 'remove_from_wishlist' in request.POST:
            # 如果商品已存在收藏夹中，移除
            Wishlist.objects.filter(user=user, product=product).delete()

        # 重定向到当前商品详情页
        return redirect('product-detail', pk=product.pk)


from django.views.generic import ListView, DeleteView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin


# 收藏夹视图，展示当前用户的收藏商品
class WishlistView(LoginRequiredMixin, ListView):
    model = Wishlist
    template_name = 'products/wishlist.html'
    context_object_name = 'wishlist_items'

    def get_queryset(self):
        # 获取当前登录用户的所有收藏商品
        return Wishlist.objects.filter(user=self.request.user)


# 移除收藏商品
class WishlistItemDeleteView(LoginRequiredMixin, DeleteView):
    model = Wishlist
    template_name = 'products/wishlist_confirm_delete.html'  # 提示用户确认删除
    context_object_name = 'wishlist_item'

    def get_success_url(self):
        # 删除成功后重定向到收藏夹页面
        return reverse_lazy('wishlist')


from django.views.generic import ListView
from django.db.models import Q
from .models import Product

class ProductSearchView(ListView):
    model = Product
    template_name = 'products/search_list.html'  # 你可以根据需求更新模板路径
    context_object_name = 'products'

    def get_queryset(self):
        query = self.request.GET.get('q', '')  # 获取搜索关键词
        if query:
            # 使用 Q 查询来处理多个条件，忽略大小写进行模糊匹配
            return Product.objects.filter(
                Q(name__icontains=query) | Q(description__icontains=query)
            )
        else:
            return Product.objects.all()  # 如果没有输入搜索条件，则返回所有商品
