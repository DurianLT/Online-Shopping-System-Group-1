from django import forms
from products.models import Product, Pricing, ProductImage


from django import forms
from products.models import Product, CategoryLevel1, CategoryLevel2, CategoryLevel3


class ProductForm(forms.ModelForm):
    category_level1 = forms.ModelChoiceField(
        queryset=CategoryLevel1.objects.all(),
        empty_label="选择一级分类",
        required=False
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

    custom_category_level1 = forms.CharField(
        max_length=255, required=False, widget=forms.TextInput(attrs={'placeholder': '输入自定义一级分类'})
    )
    custom_category_level2 = forms.CharField(
        max_length=255, required=False, widget=forms.TextInput(attrs={'placeholder': '输入自定义二级分类'})
    )
    custom_category_level3 = forms.CharField(
        max_length=255, required=False, widget=forms.TextInput(attrs={'placeholder': '输入自定义三级分类'})
    )

    class Meta:
        model = Product
        fields = ['name', 'description', 'sku', 'hidden', 'is_physical',
                  'category_level1', 'category_level2', 'category_level3',
                  'custom_category_level1', 'custom_category_level2', 'custom_category_level3']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 预加载级联分类
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

    def clean(self):
        cleaned_data = super().clean()
        custom_category1 = cleaned_data.get("custom_category_level1")
        custom_category2 = cleaned_data.get("custom_category_level2")
        custom_category3 = cleaned_data.get("custom_category_level3")

        # 处理一级分类
        if custom_category1:
            category1, created = CategoryLevel1.objects.get_or_create(name=custom_category1)
            cleaned_data["category_level1"] = category1
            cleaned_data["category_level2"] = None
            cleaned_data["category_level3"] = None  # 一级分类自定义时，后续分类清空

        # 处理二级分类
        if custom_category2:
            if not cleaned_data.get("category_level1"):
                self.add_error("custom_category_level2", "必须先选择或创建一级分类")
            else:
                category2 = CategoryLevel2.objects.filter(name=custom_category2).first()
                if not category2:
                    category2 = CategoryLevel2.objects.create(
                        name=custom_category2,
                        parent=cleaned_data["category_level1"]
                    )
                cleaned_data["category_level2"] = category2
                cleaned_data["category_level3"] = None  # 二级分类自定义时，三级分类清空

        # 处理三级分类
        if custom_category3:
            if not cleaned_data.get("category_level2"):
                self.add_error("custom_category_level3", "必须先选择或创建二级分类")
            else:
                category3 = CategoryLevel3.objects.filter(name=custom_category3).first()
                if not category3:
                    category3 = CategoryLevel3.objects.create(
                        name=custom_category3,
                        parent=cleaned_data["category_level2"]
                    )
                cleaned_data["category_level3"] = category3

        return cleaned_data


class PricingForm(forms.ModelForm):
    class Meta:
        model = Pricing
        fields = ["price", "discount", "discount_start_date", "discount_end_date"]


from django import forms

class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['image', 'is_primary']  # 包括图片字段和是否为主图
