from django.contrib.auth.views import LogoutView
from django.urls import path

from .views import user_detail_view
from .views import user_login_view

app_name = "users"
urlpatterns = [
    path("profile/", view=user_detail_view, name="profile"),
    path("login/", view=user_login_view, name="login"),
    path("logout/", view=LogoutView.as_view(), name="logout"),
]
