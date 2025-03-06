from .models import CategoryLevel1

def categories_context(request):
    categories = CategoryLevel1.objects.prefetch_related("subcategories__subcategories")
    return {"categories": categories}
