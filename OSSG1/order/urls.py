from django.urls import path

from order.views import order_from_cart, order_list, order_detail, confirm_order, checkout_single_product, \
    order_single_product

urlpatterns = [
    path('order_from_cart/', order_from_cart, name="order_from_cart"),
    path('order_list/', order_list, name="order_list"),  # ✅ 确保有 order_list 路由
    path('order_detail/<int:order_id>/', order_detail, name="order_detail"),
    path('confirm_order/', confirm_order, name="confirm_order"),
    path('checkout_single_product/<int:product_id>/', checkout_single_product, name="checkout_single_product"),  # 进入订单确认
    path('order_single_product/<int:product_id>/', order_single_product, name="order_single_product"),  # 提交订单
]
