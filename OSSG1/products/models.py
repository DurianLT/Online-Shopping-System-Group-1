from django.db import models
from users.models import CustomUser


# 存储商品分类信息
from django.db import models

# 一级分类表
class CategoryLevel1(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

# 二级分类表（外键关联一级分类）
class CategoryLevel2(models.Model):
    name = models.CharField(max_length=255, unique=True)
    parent = models.ForeignKey(CategoryLevel1, on_delete=models.CASCADE, related_name="subcategories")

    def __str__(self):
        return f"{self.parent.name} > {self.name}"

# 三级分类表（外键关联二级分类）
class CategoryLevel3(models.Model):
    name = models.CharField(max_length=255, unique=True)
    parent = models.ForeignKey(CategoryLevel2, on_delete=models.CASCADE, related_name="subcategories")

    def __str__(self):
        return f"{self.parent.parent.name} > {self.parent.name} > {self.name}"



from django.db import models


class Product(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="products")
    name = models.CharField(max_length=255)
    description = models.TextField()
    sku = models.CharField(max_length=50, unique=True)

    # 只允许产品关联到三级分类
    category_level1 = models.ForeignKey(CategoryLevel1, on_delete=models.CASCADE, null=True, blank=True,
                                        related_name="products_level1")
    category_level2 = models.ForeignKey(CategoryLevel2, on_delete=models.CASCADE, null=True, blank=True,
                                        related_name="products_level2")
    category_level3 = models.ForeignKey(CategoryLevel3, on_delete=models.CASCADE, null=True, blank=True,
                                        related_name="products_level3")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    hidden = models.BooleanField(default=False)
    is_physical = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class ProductAttribute(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="attributes")
    key = models.CharField(max_length=100, help_text="属性名称 (如: 品牌, 颜色, 型号)")
    value = models.CharField(max_length=255, help_text="属性值 (如: 百乐, 黑色, FX101)")

    class Meta:
        unique_together = ('product', 'key')  # 确保同一商品的属性名唯一

    def __str__(self):
        return f"{self.key}: {self.value}"


# 存储商品图片信息
import os
import uuid
from django.utils.deconstruct import deconstructible

@deconstructible
class PathAndRename:
    def __init__(self, sub_path):
        self.sub_path = sub_path

    def __call__(self, instance, filename):
        ext = filename.split('.')[-1]
        filename = f"{uuid.uuid4().hex}.{ext}"  # 使用隨機名稱
        return os.path.join(self.sub_path, filename)

path_and_rename_product_image = PathAndRename("product_images/")

# 存储商品图片信息
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to=path_and_rename_product_image, default='default_image.jpg')
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image of {self.product.name}"




# 存储商品定价信息
class Pricing(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name="pricing")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discount_start_date = models.DateTimeField(null=True, blank=True)
    discount_end_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Price of {self.product.name}: {self.price}"
