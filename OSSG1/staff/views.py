from django.views.generic import TemplateView, View
from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages

from products.models import Product, CategoryLevel1, RecommendedTag
from staff.form import AddTagForm
from users.models import Review


@method_decorator(user_passes_test(lambda u: u.is_staff), name='dispatch')
class AdminDashboardView(TemplateView):
    template_name = "staff/home.html"

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
        messages.success(request, "The comment was deleted")
        return redirect("adminpanel:dashboard")


class SoftDeleteProductView(View):
    @method_decorator(user_passes_test(lambda u: u.is_staff))
    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        product.soft_delete()
        messages.success(request, f"Soft-deleted listings:{product.name}")
        return redirect("adminpanel:dashboard")


# staff/views.py
from django.shortcuts import render, redirect, get_object_or_404



def manage_tags(request):
    categories = CategoryLevel1.objects.all()
    return render(request, 'staff/manage_tags.html', {'categories': categories})

def add_tag(request, category_id):
    category = get_object_or_404(CategoryLevel1, id=category_id)
    if request.method == 'POST':
        tag_name = request.POST.get('tag_name')
        if tag_name:
            RecommendedTag.objects.create(category=category, tag_name=tag_name)
    return redirect('adminpanel:manage_tags')

def delete_tag(request, tag_id):
    tag = get_object_or_404(RecommendedTag, id=tag_id)
    tag.delete()
    return redirect('adminpanel:manage_tags')