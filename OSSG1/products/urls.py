from products.views import ProductListView, ProductDetailView, WishlistView, WishlistItemDeleteView, ProductSearchView
from django.urls import path

urlpatterns = [
    path('', ProductListView.as_view(), name='product-list'),
    path('product/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('wishlist/', WishlistView.as_view(), name='wishlist'),
    path('wishlist/<int:pk>/remove/', WishlistItemDeleteView.as_view(), name='remove_from_wishlist'),
    path('search/', ProductSearchView.as_view(), name='product_search'),

]