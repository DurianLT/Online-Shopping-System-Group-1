from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.views.generic import ListView
from products.models import Product
from users.models import Cart

class AddToCartView(LoginRequiredMixin, View):
    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        cart, created = Cart.objects.get_or_create(user=request.user, product=product)
        if not created:
            cart.save()
        return redirect('cart_list')

class CartListView(LoginRequiredMixin, ListView):
    model = Cart
    template_name = 'shoppingtrolley/cart_list.html'
    context_object_name = 'cart_items'

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

class RemoveFromCartView(LoginRequiredMixin, View):
    def post(self, request, product_id):
        cart = get_object_or_404(Cart, user=request.user, product_id=product_id)
        cart.delete()
        return redirect('cart_list')