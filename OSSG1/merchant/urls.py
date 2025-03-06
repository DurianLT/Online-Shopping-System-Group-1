from django.urls import path
from merchant.views import (
    MerchantDashboardView, ProductListView, AddProductView, GetSubcategoriesView,
    EditProductView, DeleteProductView, OrderListView, OrderDetailView, ShipOrderView
)

app_name = "merchant"

urlpatterns = [
    path("dashboard/", MerchantDashboardView.as_view(), name="dashboard"),
    path("products/", ProductListView.as_view(), name="product_list"),
    path("products/add/", AddProductView.as_view(), name="add_product"),
    path("products/<int:product_id>/edit/", EditProductView.as_view(), name="edit_product"),
    path("products/<int:product_id>/delete/", DeleteProductView.as_view(), name="delete_product"),
    path("orders/", OrderListView.as_view(), name="order_list"),
    path("orders/<int:order_id>/", OrderDetailView.as_view(), name="order_detail"),
    path("orders/<int:order_id>/ship/", ShipOrderView.as_view(), name="ship_order"),
    path("get_subcategories/", GetSubcategoriesView.as_view(), name="get_subcategories"),
]
