from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from merchant.decorators import merchant_required
from django.utils.decorators import method_decorator
from products.models import Product, Pricing, ProductImage, CategoryLevel1, CategoryLevel2, CategoryLevel3, \
    ProductAttribute
from users.models import Order
from merchant.forms import ProductForm, PricingForm
from django.db.models import Q


class MerchantRequiredMixin(LoginRequiredMixin):
    """ 只允许商家访问 """

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_merchant:
            return redirect("product-list")  # 如果不是商家，重定向到首页
        return super().dispatch(request, *args, **kwargs)


from django.views.generic import ListView
from django.utils.timezone import now, timedelta
from django.db.models import Sum, Count, Avg
from users.models import Review, OrderItem
from django.db.models import F
from django.db.models.functions import TruncDate
from django.utils.timezone import now, localtime
from collections import defaultdict


class MerchantDashboardView(MerchantRequiredMixin, ListView):
    """ 商家管理首页 """
    template_name = "merchant/dashboard.html"
    context_object_name = "products"

    def get_queryset(self):
        return Product.objects.filter(user=self.request.user, is_deleted=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # 所有订单
        orders = Order.objects.filter(seller=user)
        context["orders"] = orders

        # 累计销售额（已完成）
        context["total_sales"] = orders.filter(status="Completed").aggregate(
            total=Sum("total_amount")
        )["total"] or 0

        # 待处理订单（已付款未发货）
        context["pending_orders"] = orders.filter(status="Paid").count()

        # 销售趋势（近30天）
        today = localtime(now()).date()
        start_date = today - timedelta(days=29)
        date_range = [start_date + timedelta(days=i) for i in range(30)]
        sales_labels = [d.strftime("%m-%d") for d in date_range]

        # 初始化每日销售额字典
        sales_dict = defaultdict(float)
        # 过滤已完成订单
        orders = Order.objects.filter(seller=user, status="Completed")
        filtered_orders = [
            order for order in orders
            if localtime(order.created_at).date() >= start_date
        ]
        # 手动汇总每日销售额
        for order in filtered_orders:
            order_date = localtime(order.created_at).date()
            if start_date <= order_date <= today:
                sales_dict[order_date] += float(order.total_amount)

        # 构建销售数据列表
        sales_data = [sales_dict.get(date, 0.0) for date in date_range]

        context["sales_labels"] = sales_labels
        context["sales_data"] = sales_data

        # 热门商品（销量前5）
        top_products = (
            Product.objects.filter(user=user)
            .annotate(
                sales_count=Sum("order_items__quantity"),
                total_sales=Sum(F("order_items__quantity") * F("order_items__price"))
            )
            .order_by("-sales_count")[:5]
        )
        context["top_products"] = top_products

        # 最近订单（最新5条）
        context["recent_orders"] = orders.order_by("-created_at")[:5]

        return context



class ProductListView(MerchantRequiredMixin, ListView):
    """ 商家商品列表 """
    template_name = "merchant/product_list.html"
    context_object_name = "products"

    def get_queryset(self):
        """ 获取筛选后的产品列表 """
        query = self.request.GET.get("q", "").strip()
        products = Product.objects.filter(user=self.request.user, is_deleted=False)

        if query:
            products = products.filter(
                Q(name__icontains=query) | Q(id__icontains=query)
            )

        return products

    def get_context_data(self, **kwargs):
        """ 传递查询参数到模板 """
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET.get("q", "")
        return context


class AddProductView(MerchantRequiredMixin, CreateView):
    """ 商家添加新商品 """
    model = Product
    form_class = ProductForm
    template_name = "merchant/add_product.html"
    success_url = reverse_lazy("merchant:product_list")

    def form_valid(self, form):
        form.instance.user = self.request.user  # 设置商家为当前用户
        response = super().form_valid(form)

        custom_category1 = self.request.POST.get("custom_category_level1")
        print(custom_category1)
        custom_category2 = self.request.POST.get("custom_category_level2")
        print(custom_category2)
        custom_category3 = self.request.POST.get("custom_category_level3")
        print(custom_category3)



        # 处理定价表单
        pricing_form = PricingForm(self.request.POST)
        if pricing_form.is_valid():
            pricing = pricing_form.save(commit=False)
            pricing.product = self.object
            pricing.save()

            # 处理图片上传
            images = self.request.FILES.getlist("images")
            is_primary_set = False
            for image in images:
                product_image = ProductImage(product=self.object, image=image)
                if not is_primary_set:
                    product_image.is_primary = True
                    is_primary_set = True
                product_image.save()

            # 获取并保存标签
            tags = self.request.POST.get("tags", "").split(",")  # 获取标签并分割
            for tag in tags:
                if tag:  # 过滤空标签
                    key, value = tag.split(":")  # 假设每个标签是以 'key: value' 格式
                    ProductAttribute.objects.create(
                        product=self.object,
                        key=key.strip(),
                        value=value.strip()
                    )

            messages.success(self.request, "The product has been added successfully!")
            return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["product_form"] = context.get("form", ProductForm())  # 确保 `product_form` 存在
        context["pricing_form"] = PricingForm()
        context["categories_level1"] = CategoryLevel1.objects.all()
        return context


class GetSubcategoriesView(View):
    """ 处理 AJAX 级联请求 """

    def get(self, request, *args, **kwargs):
        parent_id = request.GET.get("parent_id")
        level = request.GET.get("level")
        subcategories = []

        if level == "2":
            subcategories = list(CategoryLevel2.objects.filter(parent_id=parent_id).values("id", "name"))
        elif level == "3":
            subcategories = list(CategoryLevel3.objects.filter(parent_id=parent_id).values("id", "name"))

        return JsonResponse(subcategories, safe=False)



from django.http import JsonResponse
from django.views import View

class GetRecommendedTagsView(View):
    def get(self, request, *args, **kwargs):
        category_name = request.GET.get("category_name")
        try:
            category = CategoryLevel1.objects.get(name=category_name)
            tags = list(category.recommended_tags.values_list('tag_name', flat=True))
        except CategoryLevel1.DoesNotExist:
            tags = []
        return JsonResponse(tags, safe=False)



from django.views.generic import ListView
from django.db.models import Count
from django.utils.functional import cached_property
class OrderListView(MerchantRequiredMixin, ListView):
    """商家查看订单列表视图"""
    template_name = "merchant/order_list.html"
    context_object_name = "orders"
    paginate_by = 10  # 默认分页
    ordering = "-created_at"

    STATUS_CHOICES = {
        'Paid': 'Paid',
        'Shipped': 'Shipped',
        'Completed': 'Completed',
        'Cancelled': 'Cancelled',
    }

    @cached_property
    def status_filter(self):
        """获取状态筛选参数"""
        return self.request.GET.get("status", "").strip()

    def get_queryset(self):
        """查询当前商家的订单列表"""
        queryset = Order.objects.filter(seller=self.request.user)

        # 状态过滤
        if self.status_filter in self.STATUS_CHOICES.values():
            queryset = queryset.filter(status=self.status_filter)

        # 优化查询，避免 N+1
        queryset = queryset.select_related("user").prefetch_related("items")

        return queryset.order_by(self.ordering)

    def get_context_data(self, **kwargs):
        """添加额外上下文数据"""
        context = super().get_context_data(**kwargs)
        context["status_filter"] = self.status_filter

        # 统计每种状态的订单数量
        status_counts = Order.objects.filter(seller=self.request.user).values(
            "status"
        ).annotate(count=Count("id"))
        context["status_counts"] = {item["status"]: item["count"] for item in status_counts}

        return context

    def get_paginate_by(self, queryset):
        """允许通过 GET 参数动态控制分页数量"""
        try:
            return int(self.request.GET.get("paginate_by", self.paginate_by))
        except ValueError:
            return self.paginate_by



class OrderDetailView(MerchantRequiredMixin, DetailView):
    """ 商家查看订单详情 """
    model = Order
    template_name = "merchant/order_detail.html"

    def get_object(self, queryset=None):
        return get_object_or_404(Order, id=self.kwargs["order_id"], seller=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 传递订单状态变更历史到模板
        context["status_histories"] = self.object.status_histories.all().order_by("-changed_at")

        # 计算商品列表中的小计
        items_with_subtotal = []
        for item in self.object.items.all():
            item_dict = {
                "product": item.product,
                "price": item.price,
                "quantity": item.quantity,
                "subtotal": item.price * item.quantity,
            }
            items_with_subtotal.append(item_dict)

        # 将计算好的商品列表添加到上下文中
        context["items"] = items_with_subtotal
        return context


from django.http import JsonResponse


class EditProductView(MerchantRequiredMixin, UpdateView):
    """ 商家编辑商品 """
    model = Product
    form_class = ProductForm
    template_name = "merchant/edit_product.html"
    success_url = reverse_lazy("merchant:product_list")

    def get_object(self, queryset=None):
        return get_object_or_404(Product, id=self.kwargs["product_id"], user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        context["product"] = product
        context["product_form"] = ProductForm(instance=product)
        context["pricing_form"] = PricingForm(instance=product.pricing)
        context["categories_level1"] = CategoryLevel1.objects.all()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        pricing_form = PricingForm(request.POST, instance=self.object.pricing)

        # 图片删除请求
        delete_image_id = request.POST.get("delete_image")
        if delete_image_id:
            try:
                image = ProductImage.objects.get(id=delete_image_id, product=self.object, is_primary=False)
                image.delete()
                return JsonResponse({"status": "success", "message": "图片已删除"})
            except ProductImage.DoesNotExist:
                return JsonResponse({"status": "error", "message": "图片不存在"}, status=404)

        if form.is_valid() and pricing_form.is_valid():
            product = form.save()
            pricing_form.save()

            # 主图替换
            new_primary = request.FILES.get("replace_primary_image")
            if new_primary:
                primary = product.images.filter(is_primary=True).first()
                if primary:
                    primary.image = new_primary
                    primary.save()

            # 新图片
            for image in request.FILES.getlist("images"):
                ProductImage.objects.create(product=product, image=image)

            # 删除标签
            delete_tags = request.POST.get("delete_tags", "")
            for tag_id in delete_tags.split(","):
                if tag_id.strip():
                    ProductAttribute.objects.filter(id=tag_id.strip(), product=product).delete()

            # 添加新标签
            tags_str = request.POST.get("tags", "")
            for tag in tags_str.split(","):
                if ":" in tag:
                    key, value = tag.split(":", 1)
                    ProductAttribute.objects.create(product=product, key=key.strip(), value=value.strip())

            messages.success(request, "The product information has been updated!")
            return redirect(self.success_url)


        else:
            # ✅ 打印表单错误
            print("ProductForm Errors:", form.errors)
            print("PricingForm Errors:", pricing_form.errors)

        context = self.get_context_data()
        context["product_form"] = form
        context["pricing_form"] = pricing_form
        return self.render_to_response(context)




class ShipOrderView(MerchantRequiredMixin, View):
    """ 商家将订单状态更新为 '已发货' """

    def post(self, request, *args, **kwargs):
        order = get_object_or_404(Order, id=self.kwargs["order_id"], seller=request.user)

        if order.status != "Paid":
            messages.error(request, "Only orders that have already been paid for can be shipped.")
        else:
            order.status = "Shipped"
            order.save()
            messages.success(request, f"Order #{order.id} Marked as 'shipped'")

        return redirect("merchant:order_detail", order_id=order.id)


from django.views import View
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages

class DeleteProductView(MerchantRequiredMixin, View):
    """ 商家软删除商品 """
    def post(self, request, *args, **kwargs):
        product = get_object_or_404(Product, id=kwargs["product_id"], user=request.user)
        product.soft_delete()
        messages.success(request, "The item was successfully deleted (soft deleted)")
        return redirect("merchant:product_list")

    def get(self, request, *args, **kwargs):
        """可选：用于渲染确认删除页面"""
        product = get_object_or_404(Product, id=kwargs["product_id"], user=request.user)
        return render(request, "merchant/delete_product.html", {"product": product})



from django.contrib.auth.decorators import login_required

@login_required
def approve_refund(request, order_id):
    """ 商家同意退款，订单状态改为 'Refunded' """
    order = get_object_or_404(Order, id=order_id, seller=request.user)

    if order.status == 'Refunding':
        order.status = 'Refunded'
        order.save()
        messages.success(request, "The refund has been approved and the order has been refunded.")
    else:
        messages.error(request, "Refund operations cannot be performed on the current order status.")

    return redirect('merchant:order_detail', order_id=order.id)

@login_required
def reject_refund(request, order_id):
    """ 商家拒绝退款，订单状态回到 'Shipped' """
    order = get_object_or_404(Order, id=order_id, seller=request.user)

    if order.status == 'Refunding':
        order.status = 'Shipped'
        order.save()
        messages.info(request, "The refund request is denied and the order is restored to the shipped state.")
    else:
        messages.error(request, "Refunds cannot be denied in the current order status.")

    return redirect('merchant:order_detail', order_id=order.id)


from django.shortcuts import render, redirect, get_object_or_404


def mark_out_of_stock(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # 设置库存数量为 0
    product.stock_quantity = 0
    product.save()

    # 重定向到商品管理页面
    return redirect('merchant:product_list')  # 请根据实际的 URL 名称更新
