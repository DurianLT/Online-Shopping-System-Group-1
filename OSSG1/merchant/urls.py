from django.urls import path
from merchant.views import merchant_dashboard, product_list, add_product, order_list, order_detail, edit_product, \
    ship_order, delete_product

app_name = "merchant"

urlpatterns = [
    path("dashboard/", merchant_dashboard, name="dashboard"),
    path("products/", product_list, name="product_list"),
    path("products/<int:product_id>/edit/", edit_product, name="edit_product"),
    path("products/add/", add_product, name="add_product"),
    path("orders/", order_list, name="order_list"),
    path("orders/<int:order_id>/", order_detail, name="order_detail"),
    path("orders/<int:order_id>/ship/", ship_order, name="ship_order"),
    path("products/<int:product_id>/delete/", delete_product, name="delete_product"),
]
