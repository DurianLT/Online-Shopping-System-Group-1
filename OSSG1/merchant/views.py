from django.shortcuts import get_object_or_404, redirect
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


class MerchantDashboardView(MerchantRequiredMixin, ListView):
    """ 商家管理首页 """
    template_name = "merchant/dashboard.html"
    context_object_name = "products"

    def get_queryset(self):
        return Product.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        orders = Order.objects.filter(seller=self.request.user)
        context["orders"] = orders
        context["total_sales"] = sum(order.total_amount for order in orders if order.status == "Shipped")
        context["pending_orders"] = orders.filter(status="Paid").count()
        return context


class ProductListView(MerchantRequiredMixin, ListView):
    """ 商家商品列表 """
    template_name = "merchant/product_list.html"
    context_object_name = "products"

    def get_queryset(self):
        """ 获取筛选后的产品列表 """
        query = self.request.GET.get("q", "").strip()
        products = Product.objects.filter(user=self.request.user)

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

            messages.success(self.request, "商品添加成功！")
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



# views.py
from django.http import JsonResponse

RECOMMENDED_TAGS = {
    "休闲": ["品牌", "材质", "型号", "颜色", "适用年龄", "适用性别"],
    "体育": ["品牌", "型号", "运动种类", "颜色", "适用年龄", "适用性别"],
    "医药品": ["品牌", "型号", "适用年龄", "适用性别"],
    "文具": ["品牌", "型号", "颜色"],
    "玩具": ["品牌", "适用年龄", "适用性别", "材质", "型号", "颜色"],
    "生活用品": ["品牌", "材质", "型号", "颜色", "适用年龄", "适用性别", "适用人数"],
    "电子产品": ["品牌", "型号", "内存", "CPU", "储存", "颜色"],
    "食品": ["品牌", "味道", "地区"]
}


class GetRecommendedTagsView(View):
    def get(self, request, *args, **kwargs):
        category_name = request.GET.get("category_name")
        tags = RECOMMENDED_TAGS.get(category_name, [])
        return JsonResponse(tags, safe=False)





class OrderListView(MerchantRequiredMixin, ListView):
    """ 商家查看订单列表 """
    template_name = "merchant/order_list.html"
    context_object_name = "orders"

    def get_queryset(self):
        """ 获取当前商家所有订单，并按购买日期降序排列 """
        status_filter = self.request.GET.get("status", "").strip()
        orders = Order.objects.filter(seller=self.request.user).order_by("-created_at")

        if status_filter:
            orders = orders.filter(status=status_filter)

        return orders

    def get_context_data(self, **kwargs):
        """ 传递筛选状态到模板 """
        context = super().get_context_data(**kwargs)
        context["status_filter"] = self.request.GET.get("status", "")
        return context


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
        context["product_form"] = ProductForm(instance=self.get_object())  # 使用 get_object()
        context["pricing_form"] = PricingForm(instance=self.get_object().pricing)
        return context

    def post(self, request, *args, **kwargs):
        # 確保 self.object 正確初始化
        self.object = self.get_object()

        # 處理刪除圖片請求
        delete_image_id = request.POST.get("delete_image")
        if delete_image_id:
            try:
                image_instance = ProductImage.objects.get(
                    id=delete_image_id,
                    product=self.object,
                    is_primary=False
                )
                image_instance.delete()
                return JsonResponse({"status": "success", "message": "圖片刪除成功"})
            except ProductImage.DoesNotExist:
                return JsonResponse({"status": "error", "message": "圖片不存在或無權限刪除"}, status=404)

        # 替換主圖
        primary_image = request.FILES.get("replace_primary_image")
        if primary_image:
            primary_image_instance = self.object.images.filter(is_primary=True).first()
            if primary_image_instance:
                primary_image_instance.image = primary_image
                primary_image_instance.save()

        # 添加非主圖
        images = request.FILES.getlist("images")
        for image in images:
            ProductImage.objects.create(product=self.object, image=image)

        messages.success(request, "商品信息已更新！")
        return super().post(request, *args, **kwargs)





class ShipOrderView(MerchantRequiredMixin, View):
    """ 商家将订单状态更新为 '已发货' """

    def post(self, request, *args, **kwargs):
        order = get_object_or_404(Order, id=self.kwargs["order_id"], seller=request.user)

        if order.status != "Paid":
            messages.error(request, "只能发货已支付的订单")
        else:
            order.status = "Shipped"
            order.save()
            messages.success(request, f"订单 #{order.id} 已标记为 '已发货'")

        return redirect("merchant:order_detail", order_id=order.id)


class DeleteProductView(MerchantRequiredMixin, DeleteView):
    """ 商家删除商品 """
    model = Product
    template_name = "merchant/delete_product.html"
    success_url = reverse_lazy("merchant:product_list")

    def get_object(self, queryset=None):
        return get_object_or_404(Product, id=self.kwargs["product_id"], user=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(request, "商品已成功删除")
        return super().delete(request, *args, **kwargs)

from django.contrib.auth.decorators import login_required

@login_required
def approve_refund(request, order_id):
    """ 商家同意退款，订单状态改为 'Refunded' """
    order = get_object_or_404(Order, id=order_id, seller=request.user)

    if order.status == 'Refunding':
        order.status = 'Refunded'
        order.save()
        messages.success(request, "退款已批准，订单已退款。")
    else:
        messages.error(request, "当前订单状态无法执行退款操作。")

    return redirect('merchant:order_detail', order_id=order.id)

@login_required
def reject_refund(request, order_id):
    """ 商家拒绝退款，订单状态回到 'Shipped' """
    order = get_object_or_404(Order, id=order_id, seller=request.user)

    if order.status == 'Refunding':
        order.status = 'Shipped'
        order.save()
        messages.info(request, "退款请求被拒绝，订单恢复到已发货状态。")
    else:
        messages.error(request, "当前订单状态无法拒绝退款。")

    return redirect('merchant:order_detail', order_id=order.id)