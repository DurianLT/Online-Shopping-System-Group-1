from django.contrib import admin
from .models import Category, Product, ProductImage, Pricing
from users.models import CustomUser


# 自定义显示字段
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1  # 默认显示一行空白记录


class PricingInline(admin.StackedInline):
    model = Pricing
    extra = 1  # 默认显示一行空白记录


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'user', 'created_at', 'updated_at')  # 显示的字段
    search_fields = ('name', 'sku', 'description')  # 可搜索的字段
    list_filter = ('category', 'created_at', 'updated_at')  # 过滤器
    inlines = [ProductImageInline, PricingInline]  # 嵌套显示图片和定价


class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'image_preview', 'is_primary', 'created_at')

    # 如果你想在 admin 中显示图片预览
    def image_preview(self, obj):
        return f'<img src="{obj.image.url}" width="50" />'

    image_preview.allow_tags = True  # 允许返回 HTML 标签


admin.site.register(ProductImage, ProductImageAdmin)


class PricingAdmin(admin.ModelAdmin):
    list_display = (
    'product', 'price', 'discount', 'discount_start_date', 'discount_end_date', 'created_at', 'updated_at')  # 显示的字段
    list_filter = ('product', 'discount')  # 过滤器


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')  # 显示的字段
    search_fields = ('name',)  # 可搜索的字段


# 注册模型到 Django Admin
admin.site.register(Category, CategoryAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Pricing, PricingAdmin)
