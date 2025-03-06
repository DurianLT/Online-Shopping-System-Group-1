from django.shortcuts import redirect
from functools import wraps

from users.models import Order


def merchant_required(view_func):
    """ 限制只有商家可以访问 """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_merchant:
            return redirect("product-list")  # 如果不是商家，重定向到首页
        return view_func(request, *args, **kwargs)
    return wrapper


from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from merchant.decorators import merchant_required
from products.models import Product, ProductImage


@login_required
@merchant_required
def merchant_dashboard(request):
    """ 商家管理首页 """
    products = Product.objects.filter(user=request.user)
    orders = Order.objects.filter(seller=request.user)

    total_sales = sum(order.total_amount for order in orders if order.status == "Shipped")
    pending_orders = orders.filter(status="Paid").count()

    return render(request, "merchant/dashboard.html", {
        "products": products,
        "orders": orders,
        "total_sales": total_sales,
        "pending_orders": pending_orders,
    })


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from merchant.decorators import merchant_required
from products.models import Product, Pricing
from merchant.forms import ProductForm, PricingForm

@login_required
@merchant_required
def product_list(request):
    """ 商家商品列表 """
    products = Product.objects.filter(user=request.user)
    return render(request, "merchant/product_list.html", {"products": products})



from django.shortcuts import render, redirect
from django.forms import modelformset_factory
from .forms import ProductForm, ProductImageForm
from django.contrib import messages


@login_required
@merchant_required
def add_product(request):
    """ 商家添加新商品 """
    if request.method == "POST":
        product_form = ProductForm(request.POST)
        pricing_form = PricingForm(request.POST)

        if product_form.is_valid() and pricing_form.is_valid():
            # 保存商品信息
            product = product_form.save(commit=False)
            product.user = request.user  # 设置商家为当前用户
            product.save()

            # 保存定价信息
            pricing = pricing_form.save(commit=False)
            pricing.product = product
            pricing.save()

            # 处理图片上传
            images = request.FILES.getlist('images')  # 获取上传的多个文件
            is_primary_set = False  # 用来标记是否已经设置了主图

            for index, image in enumerate(images):
                product_image = ProductImage(product=product, image=image)
                if not is_primary_set:  # 如果还没有设置主图，将第一张图片设为主图
                    product_image.is_primary = True
                    is_primary_set = True
                else:
                    product_image.is_primary = False  # 后续图片不设为主图
                product_image.save()

            messages.success(request, "商品添加成功！")
            return redirect("merchant:product_list")

    else:
        product_form = ProductForm()
        pricing_form = PricingForm()

    return render(request, "merchant/add_product.html", {
        "product_form": product_form,
        "pricing_form": pricing_form
    })



from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from merchant.decorators import merchant_required

@login_required
@merchant_required
def order_list(request):
    """ 商家查看订单列表 """
    status_filter = request.GET.get("status", "")
    orders = Order.objects.filter(seller=request.user).order_by("-created_at")

    if status_filter:
        orders = orders.filter(status=status_filter)

    return render(request, "merchant/order_list.html", {
        "orders": orders,
        "status_filter": status_filter
    })


@login_required
@merchant_required
def order_detail(request, order_id):
    """ 商家查看订单详情 """
    order = get_object_or_404(Order, id=order_id, seller=request.user)
    return render(request, "merchant/order_detail.html", {"order": order})


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from merchant.decorators import merchant_required
from products.models import Product, Pricing
from merchant.forms import ProductForm, PricingForm


@login_required
@merchant_required
def edit_product(request, product_id):
    """ 商家编辑商品 """
    product = get_object_or_404(Product, id=product_id, user=request.user)  # 确保商家只能编辑自己的商品
    pricing = get_object_or_404(Pricing, product=product)

    if request.method == "POST":
        product_form = ProductForm(request.POST, instance=product)
        pricing_form = PricingForm(request.POST, instance=pricing)

        # 处理删除图片
        if 'delete_image' in request.POST:
            image_id = request.POST['delete_image']
            product_image = get_object_or_404(ProductImage, id=image_id, product=product)
            product_image.delete()
            messages.success(request, "图片已删除！")
            return redirect("merchant:product_list")

        if product_form.is_valid() and pricing_form.is_valid():
            # 保存商品信息
            product_form.save()
            pricing_form.save()

            # 处理主图替换
            primary_image_id = request.POST.get('primary_image')
            if primary_image_id:
                # 如果选择了主图，确保选择的是已有图片
                if primary_image_id.startswith('new-'):
                    # 新上传的图片设置为主图
                    product.images.exclude(is_primary=True).update(is_primary=False)
                    new_image = ProductImage.objects.last()  # 获取最近上传的图片
                    new_image.is_primary = True
                    new_image.save()
                else:
                    primary_image = get_object_or_404(ProductImage, id=primary_image_id, product=product)
                    # 更新主图
                    product.images.exclude(id=primary_image.id).update(is_primary=False)
                    primary_image.is_primary = True
                    primary_image.save()

            # 处理上传的图片
            images = request.FILES.getlist('images')  # 获取上传的多张图片
            for image in images:
                product_image = ProductImage(product=product, image=image)
                product_image.save()

            messages.success(request, "商品信息已更新！")
            return redirect("merchant:product_list")

    else:
        product_form = ProductForm(instance=product)
        pricing_form = PricingForm(instance=pricing)

    return render(request, "merchant/edit_product.html", {
        "product_form": product_form,
        "pricing_form": pricing_form,
        "product": product,
    })



@login_required
@merchant_required
def ship_order(request, order_id):
    """ 商家将订单状态更新为 '已发货' """
    order = get_object_or_404(Order, id=order_id, seller=request.user)

    if order.status != "Paid":
        messages.error(request, "只能发货已支付的订单")
        return redirect("merchant:order_detail", order_id=order.id)

    order.status = "Shipped"
    order.save()

    messages.success(request, f"订单 #{order.id} 已标记为 '已发货'")
    return redirect("merchant:order_detail", order_id=order.id)


@login_required
@merchant_required
def delete_product(request, product_id):
    """ 商家删除商品 """
    product = get_object_or_404(Product, id=product_id, user=request.user)  # 确保商家只能删除自己的商品

    if request.method == "POST":
        product.delete()
        messages.success(request, "商品已成功删除")
        return redirect("merchant:product_list")

    return render(request, "merchant/delete_product.html", {"product": product})


