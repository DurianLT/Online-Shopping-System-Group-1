from django import forms
from products.models import Product, Pricing, ProductImage


from django import forms
from products.models import Product, CategoryLevel1, CategoryLevel2, CategoryLevel3

class ProductForm(forms.ModelForm):
    category_level1 = forms.ModelChoiceField(
        queryset=CategoryLevel1.objects.all(),
        empty_label="选择一级分类",
        required=True
    )
    category_level2 = forms.ModelChoiceField(
        queryset=CategoryLevel2.objects.none(),
        empty_label="选择二级分类",
        required=False
    )
    category_level3 = forms.ModelChoiceField(
        queryset=CategoryLevel3.objects.none(),
        empty_label="选择三级分类",
        required=False
    )

    class Meta:
        model = Product
        fields = ['name', 'description', 'sku', 'hidden', 'is_physical', 'category_level1', 'category_level2', 'category_level3']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if 'category_level1' in self.data:
            try:
                category_level1_id = int(self.data.get('category_level1'))
                self.fields['category_level2'].queryset = CategoryLevel2.objects.filter(parent_id=category_level1_id)
            except (ValueError, TypeError):
                pass

        if 'category_level2' in self.data:
            try:
                category_level2_id = int(self.data.get('category_level2'))
                self.fields['category_level3'].queryset = CategoryLevel3.objects.filter(parent_id=category_level2_id)
            except (ValueError, TypeError):
                pass



class PricingForm(forms.ModelForm):
    class Meta:
        model = Pricing
        fields = ["price", "discount", "discount_start_date", "discount_end_date"]


from django import forms

class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['image', 'is_primary']  # 包括图片字段和是否为主图
