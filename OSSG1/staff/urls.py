
from django.urls import path
from . import views

app_name = "adminpanel"

urlpatterns = [
    path('', views.AdminDashboardView.as_view(), name='dashboard'),
    path('delete_review/<int:pk>/', views.DeleteReviewView.as_view(), name='delete_review'),
    path('soft_delete_product/<int:pk>/', views.SoftDeleteProductView.as_view(), name='soft_delete_product'),
    path("tags/", views.manage_tags, name="manage_tags"),
    path('tags/add/<int:category_id>/', views.add_tag, name='add_tag'),
    path('tags/delete/<int:tag_id>/', views.delete_tag, name='delete_tag'),
]

