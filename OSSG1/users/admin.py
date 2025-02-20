from django.contrib import admin
from .models import CustomUser, SearchHistory, BrowsingHistory, Address, Order, ApiToken, Cart, Review, Wishlist
from products.models import Product


# 用户模型的管理
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_merchant', 'created_at', 'updated_at')  # 显示字段
    search_fields = ('username', 'email')  # 可搜索字段
    list_filter = ('is_merchant', 'created_at', 'updated_at')  # 过滤器


# 用户搜索历史的管理
class SearchHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'query', 'created_at')
    list_filter = ('user', 'created_at')
    search_fields = ('query',)


# 用户浏览历史的管理
class BrowsingHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'ip_address', 'created_at')
    list_filter = ('user', 'product', 'created_at')
    search_fields = ('ip_address',)


# 用户地址信息的管理
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'address', 'is_default', 'created_at', 'updated_at')
    list_filter = ('user', 'is_default', 'created_at', 'updated_at')
    search_fields = ('address',)


# 订单信息的管理
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'sku', 'total_amount', 'status', 'created_at', 'updated_at')
    list_filter = ('user', 'status', 'created_at', 'updated_at')
    search_fields = ('sku', 'status')


# API Token的管理
class ApiTokenAdmin(admin.ModelAdmin):
    list_display = ('developer_name', 'token', 'created_at', 'expires_at')
    list_filter = ('created_at', 'expires_at')
    search_fields = ('developer_name', 'token')


# 购物车项的管理
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'created_at', 'updated_at')
    list_filter = ('user', 'created_at', 'updated_at')
    search_fields = ('user__username', 'product__name')


# 用户对商品评价的管理
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('order', 'rating', 'created_at', 'updated_at')
    list_filter = ('order', 'rating', 'created_at', 'updated_at')
    search_fields = ('order__sku',)


# 用户收藏商品的管理
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'created_at')
    list_filter = ('user', 'created_at')
    search_fields = ('user__username', 'product__name')


# 注册所有模型到 Django Admin
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(SearchHistory, SearchHistoryAdmin)
admin.site.register(BrowsingHistory, BrowsingHistoryAdmin)
admin.site.register(Address, AddressAdmin)
# admin.site.register(Order, OrderAdmin)
admin.site.register(ApiToken, ApiTokenAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Wishlist, WishlistAdmin)
