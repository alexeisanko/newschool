from datetime import date
from typing import Any

from django.contrib.auth.hashers import make_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.db.models import Count
from django.db.models import Max
from django.http import HttpRequest
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import FormView
from django.views.generic import TemplateView

from newschool.myclass.models import Lesson
from newschool.myclass.models import Record
from newschool.myclass.models import Teacher
from newschool.myclass.utils import update_info_from_myclass
from newschool.staff.models import CategoryLibraryStaff
from newschool.staff.models import LibraryStaff
from newschool.staff.models import TypeStaff
from newschool.users.forms import UserCreationForm
from newschool.users.models import User


class UserDetailView(LoginRequiredMixin, TemplateView):
    template_name = "users/profile_base.html"
    model = User

    def get(self, request, *args, **kwargs):
        return redirect("users:library")


user_detail_view = UserDetailView.as_view()


class LibraryStaffView(LoginRequiredMixin, TemplateView):
    template_name = "users/library.html"
    model = User

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        context["categories"] = CategoryLibraryStaff.objects.filter(
            type_staff=self.request.user.type_staff,
        )

        context["library_staff"] = LibraryStaff.objects.filter(
            type_staff=self.request.user.type_staff,
        )

        return context


library_staff_view = LibraryStaffView.as_view()


class UserLoginView(LoginView):
    template_name = "account/login.html"
    redirect_authenticated_user = True


user_login_view = UserLoginView.as_view()


class ManagerUserView(LoginRequiredMixin, FormView):
    model = User
    template_name = "users/manager_user.html"
    form_class = UserCreationForm
    success_url = reverse_lazy("users:manager_users")

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["users"] = User.objects.filter(is_superuser=False)
        context["type_staff"] = TypeStaff.objects.all()
        context["create_or_update_user"] = UserCreationForm
        return context

    def form_valid(self, form):
        user = form.save(commit=False)
        user.password = make_password(user.password)
        user.save()
        return super().form_valid(form)


manager_user_view = ManagerUserView.as_view()


class UserDeleteView(LoginRequiredMixin, TemplateView):
    model = User
    template_name = "users/manager_user.html"
    success_url = reverse_lazy("users:manager_users")

    def get(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        User.objects.filter(id=kwargs["id"]).delete()
        return redirect("users:manager_users")


user_delete_view = UserDeleteView.as_view()


class StatiscticView(LoginRequiredMixin, TemplateView):
    template_name = "users/statistic.html"
    model = User

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        update_info_from_myclass(date(2024, 18, 11))
        context = super().get_context_data(**kwargs)
        lessons = Lesson.objects.filter(status=1).order_by("-date", "teacher")
        records = Record.objects.values("lesson__id").annotate(Count("paid"))
        lessons_statistics = lessons.annotate(total=Count(id))
        context["statistics"] = records.all()
        context["library_staff"] = LibraryStaff.objects.filter(
            type_staff=self.request.user.type_staff,
        )

        return context


statistic_view = StatiscticView.as_view()


def update_statistic(request):
    update_info_from_myclass(date(2024, 18, 11))
    return redirect("users:statistic")
