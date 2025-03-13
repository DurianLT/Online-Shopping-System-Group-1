from django.urls import path
from .views import AddToCartView, CartListView, ModifyCartView

urlpatterns = [
    path('', CartListView.as_view(), name='cart_list'),
    path('add/<int:product_id>/', AddToCartView.as_view(), name='add_to_cart'),
    path('modify/<int:product_id>/<str:action>/', ModifyCartView.as_view(), name='modify_cart'),
]