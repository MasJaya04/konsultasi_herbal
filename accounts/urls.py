from django.urls import path

from .views import AppLoginView, AppLogoutView, HomeRedirectView, UserCreateView, UserDeleteView, UserExportView, UserListView, UserUpdateView

app_name = "accounts"

urlpatterns = [
    path("", HomeRedirectView.as_view(), name="home"),
    path("login/", AppLoginView.as_view(), name="login"),
    path("logout/", AppLogoutView.as_view(), name="logout"),
    path("users/", UserListView.as_view(), name="user_list"),
    path("users/export/", UserExportView.as_view(), name="user_export"),
    path("users/create/", UserCreateView.as_view(), name="user_create"),
    path("users/<int:pk>/edit/", UserUpdateView.as_view(), name="user_update"),
    path("users/<int:pk>/delete/", UserDeleteView.as_view(), name="user_delete"),
]
