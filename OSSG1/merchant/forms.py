from django import forms
from products.models import Product, Pricing, ProductImage


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'sku', 'category', 'hidden', 'is_physical']

class PricingForm(forms.ModelForm):
    class Meta:
        model = Pricing
        fields = ["price", "discount", "discount_start_date", "discount_end_date"]


from django import forms

class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['image', 'is_primary']  # 包括图片字段和是否为主图
