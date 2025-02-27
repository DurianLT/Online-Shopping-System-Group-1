from django.db import models
from users.models import CustomUser


# 存储商品分类信息
class Category(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


from django.db import models

class Product(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="products")
    name = models.CharField(max_length=255)
    description = models.TextField()
    sku = models.CharField(max_length=50, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    hidden = models.BooleanField(default=False)  # 新增隐藏状态，默认为不隐藏
    is_physical = models.BooleanField(default=True)  # 新增是否为实体商品，默认为实体商品

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
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to='product_images/', default='default_image.jpg')  # 手动定义一个默认图片路径
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
