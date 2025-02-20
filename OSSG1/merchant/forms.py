from django import forms
from products.models import Product, Pricing

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ["name", "description", "sku", "category"]

class PricingForm(forms.ModelForm):
    class Meta:
        model = Pricing
        fields = ["price", "discount", "discount_start_date", "discount_end_date"]
