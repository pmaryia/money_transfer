from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path, reverse_lazy


urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="registration/login.html",
            redirect_authenticated_user=True,
            next_page=reverse_lazy("transfer"),
        ),
        name="login",
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(next_page=reverse_lazy("login")),
        name="logout",
    ),
    path("transfer/", include("accounts.urls")),
]
