from django.shortcuts import redirect
from functools import wraps

def merchant_required(view_func):
    """ 限制只有商家可以访问 """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_merchant:
            return redirect("product-list")  # 如果不是商家，重定向到首页
        return view_func(request, *args, **kwargs)
    return wrapper
