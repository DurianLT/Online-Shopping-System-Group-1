from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.timezone import now

from products.models import Product
from users.models import Cart, Order, OrderItem, Address


def get_current_price(product):
    """
    获取商品当前有效价格，如果有折扣，返回折扣价，否则返回原价。
    """
    pricing = product.pricing
    if pricing.discount and pricing.discount_start_date and pricing.discount_end_date:
        if pricing.discount_start_date <= now() <= pricing.discount_end_date:
            return pricing.discount  # 折扣价
    return pricing.price  # 原价



@login_required
def order_from_cart(request):
    """ 处理订单提交，使用用户选择的地址 """
    if request.method == "POST":
        address_id = request.POST.get("address_id")
        if not address_id:
            messages.error(request, "请选择收货地址！")
            return redirect("orders:confirm_order")

        selected_address = get_object_or_404(Address, id=address_id, user=request.user)

        cart_items = Cart.objects.filter(user=request.user).select_related("product__pricing", "product__user")
        if not cart_items.exists():
            messages.warning(request, "购物车为空，请添加商品后再结账！")
            return redirect("cart")

        orders_by_seller = {}

        for item in cart_items:
            seller = item.product.user
            if seller not in orders_by_seller:
                orders_by_seller[seller] = []
            orders_by_seller[seller].append(item)

        for seller, items in orders_by_seller.items():
            total_amount = sum(
                (item.product.pricing.discount if item.product.pricing.discount else item.product.pricing.price) * item.quantity
                for item in items
            )
            order = Order.objects.create(user=request.user, seller=seller, total_amount=total_amount, address=selected_address, status="Paid")

            for item in items:
                OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity, price=item.product.pricing.price)

            Cart.objects.filter(user=request.user, product__user=seller).delete()

        messages.success(request, "订单创建成功！")
        return redirect("order_list")


from django.shortcuts import render

def order_list(request):
    status_filter = request.GET.get("status", "")
    orders = Order.objects.filter(user=request.user).order_by("-created_at")

    if status_filter:
        orders = orders.filter(status=status_filter)

    return render(request, "order/order_list.html", {
        "orders": orders,
        "status_filter": status_filter
    })

from django.shortcuts import render, get_object_or_404

def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    status_histories = order.status_histories.all()

    # 計算每個商品的小計，生成新的列表
    items_with_subtotal = []
    for item in order.items.all():
        item_dict = {
            "product": item.product,
            "price": item.price,
            "quantity": item.quantity,
            "subtotal": item.price * item.quantity,
        }
        items_with_subtotal.append(item_dict)

    return render(request, "order/order_detail.html", {
        "order": order,
        "items": items_with_subtotal,
        "status_histories": status_histories,
    })



@login_required
def confirm_order(request):
    """ 显示订单确认页面，支持购物车下单 & 直接购买 """
    product_id = request.GET.get("product_id")
    quantity = request.GET.get("quantity")

    cart_items = []

    if product_id and quantity:  # 直接购买单个商品
        product = get_object_or_404(Product, id=product_id)
        price = product.pricing.discount if product.pricing.discount else product.pricing.price
        subtotal = price * int(quantity)

        cart_items.append({
            "product": product,
            "quantity": int(quantity),
            "price": price,
            "subtotal": subtotal
        })

        total_price = subtotal

    else:  # 购物车结算
        cart_entries = Cart.objects.filter(user=request.user).select_related("product__pricing", "product__user")
        if not cart_entries.exists():
            return redirect("cart")

        total_price = 0
        for item in cart_entries:
            price = item.product.pricing.discount if item.product.pricing.discount else item.product.pricing.price
            subtotal = price * item.quantity
            total_price += subtotal

            cart_items.append({
                "product": item.product,
                "quantity": item.quantity,
                "price": price,
                "subtotal": subtotal
            })

    addresses = Address.objects.filter(user=request.user)

    return render(request, "order/confirm_order.html", {
        "cart_items": cart_items,
        "total_price": total_price,
        "addresses": addresses
    })


@login_required
def checkout_single_product(request, product_id):
    """ 处理单个商品结账 """
    product = get_object_or_404(Product, id=product_id)

    quantity = request.GET.get("quantity", 1)  # 获取数量，默认为 1
    try:
        quantity = int(quantity)
    except ValueError:
        messages.error(request, "无效的商品数量")
        return redirect("product_detail", product_id=product.id)

    # 计算价格
    price = product.pricing.discount if product.pricing.discount else product.pricing.price
    subtotal = price * quantity
    total_price = price * quantity

    # 获取用户的所有地址
    addresses = Address.objects.filter(user=request.user)

    return render(request, "order/checkout_single_product.html", {
        "product": product,
        "quantity": quantity,
        "price": price,
        "total_price": total_price,
        "addresses": addresses,
        "subtotal": subtotal
    })


@login_required
def order_single_product(request, product_id):
    """ 处理单个商品订单提交 """
    if request.method == "POST":
        product = get_object_or_404(Product, id=product_id)

        address_id = request.POST.get("address_id")
        if not address_id:
            messages.error(request, "请选择收货地址！")
            return redirect("orders:checkout_single_product", product_id=product.id)

        selected_address = get_object_or_404(Address, id=address_id, user=request.user)
        quantity = request.POST.get("quantity", 1)

        try:
            quantity = int(quantity)
        except ValueError:
            messages.error(request, "无效的商品数量")
            return redirect("orders:checkout_single_product", product_id=product.id)

        # 计算价格
        price = product.pricing.discount if product.pricing.discount else product.pricing.price
        total_amount = price * quantity

        # 创建订单
        order = Order.objects.create(user=request.user, seller=product.user, total_amount=total_amount, address=selected_address, status="Paid")
        OrderItem.objects.create(order=order, product=product, quantity=quantity, price=price)

        messages.success(request, "订单创建成功！")
        return redirect("order_list")

@login_required
def request_refund(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if order.status in ['Paid', 'Shipped']:
        order.status = 'Refunding'
        order.save()
        messages.success(request, "退款申请已提交，等待商家处理。")
    else:
        messages.error(request, "当前订单状态无法申请退款。")

    return redirect('order_detail', order_id=order.id)

def confirm_receipt(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user, status="Shipped")
    order.status = "Completed"
    order.save()
    messages.success(request, "订单已确认收货")
    return redirect("order_detail", order_id=order.id)