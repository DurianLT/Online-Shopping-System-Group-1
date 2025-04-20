from django.contrib import messages 
from django.views.generic import ListView
from users.models import Cart
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from products.models import Product

class AddToCartView(LoginRequiredMixin, View):
    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        quantity = int(request.POST.get('quantity', 1))

        # 检查库存
        if quantity > product.stock:
            messages.warning(request, f"库存不足，仅剩 {product.stock} 件。")
            return redirect('cart_list')

        cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)

        if not created:
            if cart_item.quantity + quantity > product.stock:
                messages.warning(request, f"库存不足，无法添加更多。当前已加入 {cart_item.quantity} 件，最多还可添加 {product.stock - cart_item.quantity} 件。")
                return redirect('cart_list')
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity

        cart_item.save()
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
        
        # 用于存储库存不足商品的提醒信息
        out_of_stock_items = []

        # 检查购物车中的商品库存
        for item in cart_items:
            if item.product.stock <= 0:
                out_of_stock_items.append(item)
            elif item.product.stock < item.quantity:
                out_of_stock_items.append(item)

        # 将库存不足的商品传递给模板
        context['out_of_stock_items'] = out_of_stock_items
        
        # 计算总价和总数量
        total_price = 0
        total_quantity = 0
        for item in cart_items:
            price = item.product.pricing.discount if item.product.pricing.discount else item.product.pricing.price
            total_price += price * item.quantity
            total_quantity += item.quantity

        context['total_price'] = total_price
        context['total_quantity'] = total_quantity

        # 如果有商品库存不足，添加提醒消息
        if out_of_stock_items:
            context['out_of_stock_message'] = "以下商品库存不足或已售罄，请修改购物车。"

        return context


class ModifyCartView(LoginRequiredMixin, View):
    def post(self, request, product_id, action):
        cart_item = get_object_or_404(Cart, user=request.user, product_id=product_id)
        product = cart_item.product

        if action == 'remove':
            cart_item.delete()

        elif action == 'add':
            if cart_item.quantity + 1 > product.stock:
                messages.warning(request, f"库存不足，最多只能购买 {product.stock} 件。")
            else:
                cart_item.quantity += 1
                cart_item.save()

        elif action == 'subtract':
            cart_item.quantity -= 1
            if cart_item.quantity <= 0:
                cart_item.delete()
            else:
                cart_item.save()

        return redirect('cart_list')
