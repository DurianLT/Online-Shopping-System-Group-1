from django.http import JsonResponse
from django.shortcuts import render

from django.views.generic import ListView, DetailView

from users.models import Wishlist
from .models import Product

from django.core.paginator import Paginator

class ProductListView(ListView):
    model = Product
    template_name = 'product_list.html'  # 显示产品的模板
    context_object_name = 'products'
    paginate_by = 8  # 每页8个商品

    def get_queryset(self):
        queryset = Product.objects.all().filter(hidden=False).order_by('created_at')

        # 基于三级分类筛选
        level3_id = self.kwargs.get('level3_id')
        if level3_id:
            queryset = queryset.filter(category_level3_id=level3_id)

        # 如果没有选择三级分类，允许选择一级或二级分类
        level2_id = self.kwargs.get('level2_id')
        if level2_id:
            queryset = queryset.filter(category_level2_id=level2_id)

        level1_id = self.kwargs.get('level1_id')
        if level1_id:
            queryset = queryset.filter(category_level1_id=level1_id)

        return queryset




from django.shortcuts import redirect
from .models import Product

from django.shortcuts import redirect


class ProductDetailView(DetailView):
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # 检查用户是否登录
        if user.is_authenticated:
            product = self.get_object()
            # 检查当前用户是否已收藏该商品
            context['is_in_wishlist'] = Wishlist.objects.filter(user=user, product=product).exists()
        else:
            # 如果用户未登录，则无法收藏商品
            context['is_in_wishlist'] = False

        return context

    def post(self, request, *args, **kwargs):
        product = self.get_object()
        user = request.user

        # 检查用户是否登录
        if not user.is_authenticated:
            return redirect('login')  # 用户未登录，重定向到登录页面

        # 处理收藏功能
        if 'add_to_wishlist' in request.POST:
            if not Wishlist.objects.filter(user=user, product=product).exists():
                # 如果当前商品不在用户的收藏夹中，添加到收藏夹
                Wishlist.objects.create(user=user, product=product)
        elif 'remove_from_wishlist' in request.POST:
            # 如果商品已存在收藏夹中，移除
            Wishlist.objects.filter(user=user, product=product).delete()

        # 重定向到当前商品详情页
        return redirect('product-detail', pk=product.pk)


from django.views.generic import ListView, DeleteView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin


# 收藏夹视图，展示当前用户的收藏商品
class WishlistView(LoginRequiredMixin, ListView):
    model = Wishlist
    template_name = 'products/wishlist.html'
    context_object_name = 'wishlist_items'

    def get_queryset(self):
        # 获取当前登录用户的所有收藏商品
        return Wishlist.objects.filter(user=self.request.user)


# 移除收藏商品
class WishlistItemDeleteView(LoginRequiredMixin, DeleteView):
    model = Wishlist
    template_name = 'products/wishlist_confirm_delete.html'  # 提示用户确认删除
    context_object_name = 'wishlist_item'

    def get_success_url(self):
        # 删除成功后重定向到收藏夹页面
        return reverse_lazy('wishlist')


from django.views.generic import ListView
from django.db.models import Q
from .models import Product

class ProductSearchView(ListView):
    model = Product
    template_name = 'products/search_list.html'  # 你可以根据需求更新模板路径
    context_object_name = 'products'

    def get_queryset(self):
        query = self.request.GET.get('q', '')  # 获取搜索关键词
        if query:
            # 使用 Q 查询来处理多个条件，忽略大小写进行模糊匹配
            return Product.objects.filter(
                Q(name__icontains=query) | Q(description__icontains=query)
            )
        else:
            return Product.objects.all()  # 如果没有输入搜索条件，则返回所有商品

from .models import CategoryLevel1, CategoryLevel2, CategoryLevel3

class CategoryLevel1ListView(ListView):
    model = CategoryLevel1
    template_name = 'products/category_list.html'
    context_object_name = 'categories'

class CategoryLevel2ListView(ListView):
    model = CategoryLevel2
    template_name = 'products/category_list.html'
    context_object_name = 'categories'

    def get_queryset(self):
        parent_id = self.kwargs['level1_id']
        return CategoryLevel2.objects.filter(parent_id=parent_id)

class CategoryLevel3ListView(ListView):
    model = CategoryLevel3
    template_name = 'products/category_list.html'
    context_object_name = 'categories'

    def get_queryset(self):
        parent_id = self.kwargs['level2_id']
        return CategoryLevel3.objects.filter(parent_id=parent_id)
    
from django.shortcuts import render, get_object_or_404
from .models import CategoryLevel1, CategoryLevel2, CategoryLevel3, Product

def category_detail(request, category_id, level=1):
    if level == 1:
        category = get_object_or_404(CategoryLevel1, pk=category_id)
        products = Product.objects.filter(category_level1=category)
    elif level == 2:
        category = get_object_or_404(CategoryLevel2, pk=category_id)
        products = Product.objects.filter(category_level2=category)
    elif level == 3:
        category = get_object_or_404(CategoryLevel3, pk=category_id)
        products = Product.objects.filter(category_level3=category)
    
    return render(request, 'products/category_detail.html', {'category': category, 'products': products})

from django.http import JsonResponse
from django.core.paginator import Paginator
from django.views.generic import ListView
from .models import Product, Pricing

class ProductListApiView(ListView):
    model = Product
    context_object_name = 'products'

    def get(self, request, *args, **kwargs):
        page_number = request.GET.get('page', 1)
        # 添加排序条件，按创建时间排序
        products = Product.objects.all().filter(hidden=False).order_by('created_at')  # 或者按其他字段排序

        paginator = Paginator(products, 8)  # 每页 8 个商品
        page_obj = paginator.get_page(page_number)

        products_data = []
        for product in page_obj:
            # 获取商品的定价信息
            try:
                pricing = product.pricing  # 尝试获取关联的定价信息
                price = pricing.price
                discount = pricing.discount
                discount_start_date = pricing.discount_start_date
                discount_end_date = pricing.discount_end_date
            except Pricing.DoesNotExist:
                price = 'N/A'
                discount = 'N/A'
                discount_start_date = None
                discount_end_date = None

            products_data.append({
                'id': product.id,
                'name': product.name,
                'image_url': product.images.first().image.url if product.images.first() else '',  # 图片链接
                'description': product.description,
                'price': price,  # 处理定价缺失
                'discount': discount,  # 处理折扣缺失
                'discount_start_date': discount_start_date,  # 折扣开始日期
                'discount_end_date': discount_end_date,  # 折扣结束日期
            })

        return JsonResponse({'products': products_data})




