from products.views import ProductListView, ProductDetailView, WishlistView, WishlistItemDeleteView, ProductSearchView, ProductListApiView
from django.urls import path
from . import views

urlpatterns = [
     # 商品分类详情页（根据分类层级显示对应的产品）
    path('category/<int:category_id>/', views.category_detail, name='category_detail'),  # 默认是一级分类
    path('category/<int:category_id>/level2/', views.category_detail, {'level': 2}, name='category_level2_detail'),
    path('category/<int:category_id>/level3/', views.category_detail, {'level': 3}, name='category_level3_detail'),

    path('', ProductListView.as_view(), name='product-list'),
    path('product/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('wishlist/', WishlistView.as_view(), name='wishlist'),
    path('wishlist/<int:pk>/remove/', WishlistItemDeleteView.as_view(), name='remove_from_wishlist'),
    path('search/', ProductSearchView.as_view(), name='product_search'),

    path('api/products/', ProductListApiView.as_view(), name='product-list-api'),  # 这个API端点用于返回JSON数据

]