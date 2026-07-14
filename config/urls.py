from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include(("accounts.urls", "accounts"), namespace="accounts")),
    path("dashboard/", include(("consultations.dashboard_urls", "dashboard"), namespace="dashboard")),
    path("products/", include(("catalog.urls", "catalog"), namespace="catalog")),
    path("knowledge/", include(("knowledge.urls", "knowledge"), namespace="knowledge")),
    path("consultations/", include(("consultations.urls", "consultations"), namespace="consultations")),
]
