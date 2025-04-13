from django.views.generic import TemplateView, View
from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages

from products.models import Product
from users.models import Review


@method_decorator(user_passes_test(lambda u: u.is_staff), name='dispatch')
class AdminDashboardView(TemplateView):
    template_name = "adminpanel/home.html"

    def get(self, request, *args, **kwargs):
        product_id = request.GET.get("product_id")
        if product_id:
            reviews = Review.objects.filter(order_item__product_id=product_id).order_by("-created_at")
        else:
            reviews = Review.objects.select_related('order_item', 'user').order_by("-created_at")[:20]

        products = Product.objects.filter(is_deleted=False)
        return render(request, self.template_name, {
            "reviews": reviews,
            "products": products,
            "product_filter": product_id,
        })


class DeleteReviewView(View):
    @method_decorator(user_passes_test(lambda u: u.is_staff))
    def post(self, request, pk):
        review = get_object_or_404(Review, pk=pk)
        review.delete()
        messages.success(request, "评论已删除")
        return redirect("adminpanel:dashboard")


class SoftDeleteProductView(View):
    @method_decorator(user_passes_test(lambda u: u.is_staff))
    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        product.soft_delete()
        messages.success(request, f"已软删除商品：{product.name}")
        return redirect("adminpanel:dashboard")
