from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils.timezone import now

from products.models import Product
from users.models import Cart, Order, OrderItem, Address


def get_current_price(product):
    """ 获取商品当前有效价格 """
    pricing = product.pricing
    if pricing.discount and pricing.discount_start_date and pricing.discount_end_date:
        if pricing.discount_start_date <= now() <= pricing.discount_end_date:
            return pricing.discount
    return pricing.price


@login_required
def confirm_order(request):
    """ 显示订单确认页面，支持购物车下单 & 直接购买 """
    product_id = request.GET.get("product_id")
    quantity = request.GET.get("quantity")
    cart_items = []

    if product_id and quantity:  # 直接购买
        product = get_object_or_404(Product, id=product_id)
        price = get_current_price(product)
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
            price = get_current_price(item.product)
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
def order_from_cart(request):
    """ 使用购物车生成订单 """
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
            orders_by_seller.setdefault(seller, []).append(item)

        for seller, items in orders_by_seller.items():
            total_amount = sum(
                get_current_price(item.product) * item.quantity for item in items
            )

            # 创建订单，初始状态 Pending
            order = Order.objects.create(
                user=request.user,
                seller=seller,
                total_amount=total_amount,
                address=selected_address,
                status="Pending"
            )

            for item in items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=get_current_price(item.product)
                )

            # 改为已支付 ➜ 触发库存扣减逻辑
            order.status = "Paid"
            order.save()

            # 清空对应卖家的购物车项
            Cart.objects.filter(user=request.user, product__user=seller).delete()

        messages.success(request, "订单创建成功！")
        return redirect("order_list")


@login_required
def checkout_single_product(request, product_id):
    """ 显示单个商品结账页面 """
    product = get_object_or_404(Product, id=product_id)
    quantity = request.GET.get("quantity", 1)

    try:
        quantity = int(quantity)
    except ValueError:
        messages.error(request, "无效的商品数量")
        return redirect("product-detail", pk=product.id)

    price = get_current_price(product)
    subtotal = price * quantity
    total_price = subtotal

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
    """ 提交单个商品订单 """
    if request.method == "POST":
        product = get_object_or_404(Product, id=product_id)
        address_id = request.POST.get("address_id")
        quantity = request.POST.get("quantity", 1)

        if not address_id:
            messages.error(request, "请选择收货地址！")
            return redirect("orders:checkout_single_product", product_id=product.id)

        try:
            quantity = int(quantity)
        except ValueError:
            messages.error(request, "无效的商品数量")
            return redirect("orders:checkout_single_product", product_id=product.id)

        price = get_current_price(product)
        total_amount = price * quantity

        address = get_object_or_404(Address, id=address_id, user=request.user)

        # 创建订单，初始 Pending
        order = Order.objects.create(
            user=request.user,
            seller=product.user,
            total_amount=total_amount,
            address=address,
            status="Pending"
        )

        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            price=price
        )

        # 设置为 Paid ➜ 扣库存
        order.status = "Paid"
        order.save()

        messages.success(request, "订单创建成功！")
        return redirect("order_list")

from django.core.paginator import Paginator
from django.shortcuts import render

@login_required
def order_list(request):
    # 获取筛选参数
    status_filter = request.GET.get("status", "")
    page_number = request.GET.get('page', 1)
    
    # 基础查询
    orders = Order.objects.filter(user=request.user).select_related('seller').order_by("-created_at")
    
    # 状态筛选
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    # 分页处理 - 每页10条记录
    paginator = Paginator(orders, 10)
    page_obj = paginator.get_page(page_number)
    
    # 状态选项（用于前端显示当前筛选状态）
    status_choices = {
        '': '全部',
        'Pending': 'Pending',
        'Paid': 'Paid',
        'Shipped': 'Shipped',
        'Completed': 'Completed',
        'Cancelled': 'Cancelled',
    }
    
    return render(request, "order/order_list.html", {
        "orders": page_obj.object_list,
        "page_obj": page_obj,
        "status_filter": status_filter,
        "status_choices": status_choices,
        "is_paginated": page_obj.has_other_pages(),
    })


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    status_histories = order.status_histories.all()

    items_with_subtotal = []
    for item in order.items.all():
        items_with_subtotal.append({
            "product": item.product,
            "price": item.price,
            "quantity": item.quantity,
            "subtotal": item.price * item.quantity
        })

    return render(request, "order/order_detail.html", {
        "order": order,
        "items": items_with_subtotal,
        "status_histories": status_histories
    })


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


@login_required
def confirm_receipt(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user, status="Shipped")
    order.status = "Completed"
    order.save()
    messages.success(request, "订单已确认收货")
    return redirect("order_detail", order_id=order.id)
