from django.urls import path

from .views import (
    ProductCategoryCreateView,
    ProductCategoryDeleteView,
    ProductCategoryListView,
    ProductCategoryUpdateView,
    ProductCreateView,
    ProductDeleteView,
    ProductExportView,
    ProductListView,
    ProductUpdateView,
)

app_name = "catalog"

urlpatterns = [
    path("categories/", ProductCategoryListView.as_view(), name="category_list"),
    path("categories/create/", ProductCategoryCreateView.as_view(), name="category_create"),
    path("categories/<int:pk>/edit/", ProductCategoryUpdateView.as_view(), name="category_update"),
    path("categories/<int:pk>/delete/", ProductCategoryDeleteView.as_view(), name="category_delete"),
    path("", ProductListView.as_view(), name="product_list"),
    path("export/", ProductExportView.as_view(), name="product_export"),
    path("create/", ProductCreateView.as_view(), name="product_create"),
    path("<int:pk>/edit/", ProductUpdateView.as_view(), name="product_update"),
    path("<int:pk>/delete/", ProductDeleteView.as_view(), name="product_delete"),
]
