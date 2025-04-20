from django.http import JsonResponse
from django.shortcuts import render

from django.views.generic import ListView, DetailView

from users.models import Wishlist
from .models import Product

from django.core.paginator import Paginator

class ProductListView(ListView):
    model = Product
    template_name = 'product_list.html'
    context_object_name = 'products'
    paginate_by = 8

    def get_queryset(self):
        queryset = Product.objects.all().filter(
            hidden=False, is_deleted=False, stock_quantity__gt=0
        ).order_by('created_at').prefetch_related('attributes')  # 预加载 attributes

        level3_id = self.kwargs.get('level3_id')
        level2_id = self.kwargs.get('level2_id')
        level1_id = self.kwargs.get('level1_id')

        if level3_id:
            queryset = queryset.filter(category_level3_id=level3_id)
        elif level2_id:
            queryset = queryset.filter(category_level2_id=level2_id)
        elif level1_id:
            queryset = queryset.filter(category_level1_id=level1_id)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category_level1_list'] = CategoryLevel1.objects.prefetch_related('subcategories__subcategories')
        return context



from django.shortcuts import redirect
from .models import Product

from django.shortcuts import redirect
from users.models import Review, OrderItem
from django.db.models import Avg


class ProductDetailView(DetailView):
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        product = self.get_object()

        # 收藏状态
        context['is_in_wishlist'] = False
        if user.is_authenticated:
            context['is_in_wishlist'] = Wishlist.objects.filter(user=user, product=product).exists()

        # 评价相关内容
        order_items = product.order_items.all()
        reviews = Review.objects.filter(order_item__in=order_items, parent_review=None).select_related('user', 'order_item', 'order_item__order')
        context['reviews'] = reviews

        avg_rating = reviews.aggregate(avg=Avg('rating'))['avg'] or 0
        context['avg_rating'] = round(avg_rating, 1)

        # 当前用户能评价的订单项
        if user.is_authenticated:
            context['can_review_items'] = order_items.filter(order__user=user).exclude(reviews__user=user)
        else:
            context['can_review_items'] = []

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
    paginate_by = 8

    def get_queryset(self):
        query = self.request.GET.get('q', '')  # 获取搜索关键词
        if query:
            # 使用 Q 查询来处理多个条件，忽略大小写进行模糊匹配
            return Product.objects.filter(
                Q(hidden=False, is_deleted=False, stock_quantity__gt=0) 
                & (Q(name__icontains=query) 
                | Q(description__icontains=query) 
                | Q(category_level1__name__icontains=query)
                | Q(category_level2__name__icontains=query)
                | Q(category_level3__name__icontains=query)
                | Q(attributes__key__icontains=query)
                | Q(attributes__value__icontains=query))
            )
        else:
            return Product.objects.filter(hidden=False, is_deleted=False, stock_quantity__gt=0)  # 如果没有输入搜索条件，则返回所有商品

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
        products = Product.objects.filter(hidden=False, is_deleted=False, stock_quantity__gt=0, category_level1=category)
    elif level == 2:
        category = get_object_or_404(CategoryLevel2, pk=category_id)
        products = Product.objects.filter(hidden=False, is_deleted=False, stock_quantity__gt=0, category_level2=category)
    elif level == 3:
        category = get_object_or_404(CategoryLevel3, pk=category_id)
        products = Product.objects.filter(hidden=False, is_deleted=False, stock_quantity__gt=0, category_level3=category)
    
    return render(request, 'products/category_detail.html', {'category': category, 'products': products})

from django.http import JsonResponse
from django.core.paginator import Paginator
from django.views.generic import ListView
from .models import Product, Pricing

from django.views.generic.list import ListView
from django.http import JsonResponse
from django.core.paginator import Paginator
from .models import Product  # 你根据实际路径替换
from django.db.models import Prefetch

from django.http import JsonResponse
from django.views.generic import ListView
from django.core.paginator import Paginator
from .models import Product

class ProductListApiView(ListView):
    model = Product
    context_object_name = 'products'

    def get(self, request, *args, **kwargs):
        page_number = request.GET.get('page', 1)
        products_per_page = 8

        # 获取所有符合条件的商品
        products = Product.objects.filter(
            hidden=False, is_deleted=False, stock_quantity__gt=0
        ).order_by('created_at').prefetch_related(
            'attributes', 'images', 'pricing'
        ).select_related(
            'category_level1', 'category_level2', 'category_level3'
        )

        # 根据分类筛选
        level3_id = self.kwargs.get('level3_id')
        level2_id = self.kwargs.get('level2_id')
        level1_id = self.kwargs.get('level1_id')

        if level3_id:
            products = products.filter(category_level3_id=level3_id)
        elif level2_id:
            products = products.filter(category_level2_id=level2_id)
        elif level1_id:
            products = products.filter(category_level1_id=level1_id)

        paginator = Paginator(products, products_per_page)
        page_obj = paginator.get_page(page_number)

        products_data = []
        for product in page_obj:
            attributes = [{
                'key': attr.key,
                'value': attr.value
            } for attr in product.attributes.all()]

            pricing = getattr(product, 'pricing', None)
            price = pricing.price if pricing else 'N/A'
            discount = pricing.discount if pricing else None

            # 分类信息（需要为 JS 模板准备）
            category_level1 = {
                'id': product.category_level1.id,
                'name': product.category_level1.name
            } if product.category_level1 else None

            category_level2 = {
                'id': product.category_level2.id,
                'name': product.category_level2.name
            } if product.category_level2 else None

            category_level3 = {
                'id': product.category_level3.id,
                'name': product.category_level3.name
            } if product.category_level3 else None

            products_data.append({
                'id': product.id,
                'name': product.name,
                'image_url': product.images.first().image.url if product.images.exists() else '',
                'description': product.description,
                'attributes': attributes,
                'price': price,
                'discount': discount,
                'category_level1': category_level1,
                'category_level2': category_level2,
                'category_level3': category_level3,
            })

        return JsonResponse({
            'total_products': paginator.count,
            'products': products_data
        })




# views.py
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.shortcuts import get_object_or_404
from users.models import Review, OrderItem
from .forms import ReviewForm

class ReviewCreateView(CreateView):
    model = Review
    form_class = ReviewForm
    template_name = 'reviews/review_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.order_item = get_object_or_404(OrderItem, pk=self.kwargs['pk'], order__user=request.user)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.order_item = self.order_item
        form.instance.author_type = "buyer"
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('product-detail', kwargs={'pk': self.order_item.product.pk})

class ReviewUpdateView(UpdateView):
    model = Review
    form_class = ReviewForm
    template_name = 'reviews/review_form.html'

    def get_queryset(self):
        return Review.objects.filter(user=self.request.user)

    def get_success_url(self):
        return reverse('product-detail', kwargs={'pk': self.object.order_item.product.pk})

class ReviewDeleteView(DeleteView):
    model = Review
    template_name = 'reviews/review_confirm_delete.html'

    def get_queryset(self):
        return Review.objects.filter(user=self.request.user)

    def get_success_url(self):
        return reverse('product-detail', kwargs={'pk': self.object.order_item.product.pk})

from django.views import View
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Product

class ProductSearchApiView(View):
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '')
        page_number = request.GET.get('page', 1)
        products_per_page = 8

        # 基础过滤
        products = Product.objects.filter(hidden=False, is_deleted=False, stock_quantity__gt=0)

        # 搜索过滤
        if query:
            products = products.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(category_level1__name__icontains=query) |
                Q(category_level2__name__icontains=query) |
                Q(category_level3__name__icontains=query) |
                Q(attributes__key__icontains=query) |
                Q(attributes__value__icontains=query)
            )

        # 去重（因为 attributes 多对多可能导致重复）
        products = products.distinct()

        # 优化查询
        products = products.order_by('created_at').prefetch_related(
            'attributes', 'images', 'pricing'
        ).select_related(
            'category_level1', 'category_level2', 'category_level3'
        )

        paginator = Paginator(products, products_per_page)
        page_obj = paginator.get_page(page_number)

        products_data = []
        for product in page_obj:
            attributes = [{'key': attr.key, 'value': attr.value} for attr in product.attributes.all()]
            pricing = getattr(product, 'pricing', None)
            price = pricing.price if pricing else 'N/A'
            discount = pricing.discount if pricing else None

            category_level1 = {'id': product.category_level1.id, 'name': product.category_level1.name} if product.category_level1 else None
            category_level2 = {'id': product.category_level2.id, 'name': product.category_level2.name} if product.category_level2 else None
            category_level3 = {'id': product.category_level3.id, 'name': product.category_level3.name} if product.category_level3 else None

            products_data.append({
                'id': product.id,
                'name': product.name,
                'image_url': product.images.first().image.url if product.images.exists() else '',
                'description': product.description,
                'attributes': attributes,
                'price': price,
                'discount': discount,
                'category_level1': category_level1,
                'category_level2': category_level2,
                'category_level3': category_level3,
            })

        return JsonResponse({
            'total_products': paginator.count,
            'products': products_data
        })
