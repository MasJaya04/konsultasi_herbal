from django.urls import path

from .views import DashboardExportView, DashboardHomeView

app_name = "dashboard"

urlpatterns = [
    path("", DashboardHomeView.as_view(), name="home"),
    path("export/", DashboardExportView.as_view(), name="export"),
]
