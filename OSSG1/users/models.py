from django.contrib.auth.models import AbstractUser
from django.db import models


# 用户信息模型，继承了django的基础用户模型新增了以下字段
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True, max_length=255)
    is_merchant = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # 设置 email 作为唯一标识符
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.username


# 用户搜索历史
class SearchHistory(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="search_histories")
    query = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} searched {self.query}"


# 用户浏览历史
class BrowsingHistory(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="browsing_histories")
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name="browsing_histories")
    ip_address = models.GenericIPAddressField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} viewed {self.product.name}"


# 地址信息
from django.db import models

class Address(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="addresses")
    address = models.TextField()
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # 如果设置为默认地址，则取消用户其他默认地址
        if self.is_default:
            # 取消用户之前的默认地址
            Address.objects.filter(user=self.user, is_default=True).update(is_default=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.address}"


from django.db import models
from products.models import Product


class Order(models.Model):
    STATUS_CHOICES = [
        ('Pending', '待支付'),
        ('Paid', '已支付'),
        ('Shipped', '已发货'),
        ('Completed', '已完成'),
        ('Cancelled', '已取消'),
        ('Refunding', '退款中'),  # 新增退款中状态
        ('Refunded', '已退款'),  # 新增已退款状态
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="orders")  # 购买者
    seller = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="seller_orders")  # 商家（从 product.user 取）
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    address = models.ForeignKey('Address', on_delete=models.SET_NULL, null=True, blank=True, related_name="orders")

    def save(self, *args, **kwargs):
        # 如果订单状态变更，记录状态变化
        if self.pk and Order.objects.filter(pk=self.pk).exists():
            old_status = Order.objects.get(pk=self.pk).status
            if old_status != self.status:
                OrderStatusHistory.objects.create(order=self, status=self.status)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order {self.id} - {self.status} - {self.seller.username}"


from django.db import models

class OrderStatusHistory(models.Model):
    STATUS_CHOICES = [
        ('Pending', '待支付'),
        ('Paid', '已支付'),
        ('Shipped', '已发货'),
        ('Completed', '已完成'),
        ('Cancelled', '已取消'),
        ('Refunding', '退款中'),  # 新增退款中状态
        ('Refunded', '已退款'),  # 新增已退款状态
    ]

    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name="status_histories")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    changed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.order.id} - {self.status} at {self.changed_at}"



class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="order_items")
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)  # 记录下单时的价格

    def __str__(self):
        return f"{self.product.name} x {self.quantity} - Order {self.order.id}"




# api token，不知道用不用的上
class ApiToken(models.Model):
    developer_name = models.CharField(max_length=255)
    token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def __str__(self):
        return f"{self.developer_name} API Token"


from django.db import models
from products.models import Product  # 假设你的商品模型在这个位置

class Cart(models.Model):
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name="cart_items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="cart_items")
    quantity = models.PositiveIntegerField(default=1)  # 添加数量字段，默认为1
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.name} (Quantity: {self.quantity}) in Cart"



# 用户对商品评价

class Review(models.Model):
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE, related_name="reviews", null=True, blank=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="reviews", null=True, blank=True)
    parent_review = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name="replies")  # 回复的评价
    author_type = models.CharField(max_length=10, choices=[("buyer", "Buyer"), ("seller", "Seller")], default="buyer")
    rating = models.IntegerField()  # 评分 1-5
    comment = models.TextField()  # 评价内容
    created_at = models.DateTimeField(auto_now_add=True)  # 评价创建时间
    updated_at = models.DateTimeField(auto_now=True)  # 评价更新时间

    def __str__(self):
        return f"Review by {self.user.username} on Order Item {self.order_item.id} - {self.rating} Stars"



# 收藏
class Wishlist(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="wishlist")
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name="wishlist")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.name} in Wishlist"
