from django.contrib.auth.views import LogoutView
from django.urls import path

from .views import library_staff_view
from .views import manager_user_view
from .views import statistic_view
from .views import update_statistic
from .views import user_delete_view
from .views import user_detail_view
from .views import user_login_view

app_name = "users"
urlpatterns = [
    path("profile/", view=user_detail_view, name="profile"),
    path("library/", view=library_staff_view, name="library"),
    path("manager_users/", view=manager_user_view, name="manager_users"),
    path("user_delete/<int:id>/", view=user_delete_view, name="user_delete"),
    path("login/", view=user_login_view, name="login"),
    path("logout/", view=LogoutView.as_view(), name="logout"),
    path("statistic/", view=statistic_view, name="statistic"),
    path("update_statistic/", view=update_statistic, name="statistic"),
]
