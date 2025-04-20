
from django.views.generic import ListView
from users.models import Cart
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from products.models import Product

class AddToCartView(LoginRequiredMixin, View):
    def post(self, request, product_id):
        # 获取商品对象
        product = get_object_or_404(Product, id=product_id)

        # 获取用户提交的数量（默认为1）
        quantity = int(request.POST.get('quantity', 1))

        # 获取购物车条目，如果没有则创建
        cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)

        if not created:
            # 如果商品已经在购物车中，更新数量
            cart_item.quantity += quantity
            cart_item.save()  # 保存更新的购物车条目
        else:
            # 如果是新商品，设置数量
            cart_item.quantity = quantity
            cart_item.save()  # 保存新的购物车条目

        # 重定向到购物车列表页面
        return redirect('cart_list')


class CartListView(LoginRequiredMixin, ListView):
    model = Cart
    template_name = 'shoppingtrolley/cart_list.html'
    context_object_name = 'cart_items'

    def get_queryset(self):
        # 获取当前登录用户的购物车条目
        return Cart.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_items = context['cart_items']

        # 计算总价
        total_price = 0
        total_quantity = 0

        for item in cart_items:
            # 使用折扣价，如果存在
            price = item.product.pricing.discount if item.product.pricing.discount else item.product.pricing.price
            total_price += price * item.quantity
            total_quantity += item.quantity

        context['total_price'] = total_price
        context['total_quantity'] = total_quantity
        return context


class ModifyCartView(LoginRequiredMixin, View):
    def post(self, request, product_id, action):
        # 获取购物车中的商品条目
        cart_item = get_object_or_404(Cart, user=request.user, product_id=product_id)

        if action == 'remove':
            cart_item.delete()  # 删除商品
        elif action == 'add':
            cart_item.quantity += 1  # 增加商品数量
            cart_item.save()  # 保存更新后的数量
        elif action == 'subtract':
            cart_item.quantity -= 1  # 减少商品数量
            if cart_item.quantity <= 0:
                cart_item.delete()  # 如果数量为0，删除该商品
            else:
                cart_item.save()  # 保存更新后的数量

        return redirect('cart_list')  # 重定向到购物车页面
