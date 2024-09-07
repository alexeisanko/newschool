from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.views.generic import TemplateView

from newschool.staff.models import CategoryLibraryStaff
from newschool.staff.models import LibraryStaff
from newschool.users.models import User


class UserDetailView(LoginRequiredMixin, TemplateView):
    template_name = "users/profile.html"
    model = User

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        context["categories_library_staff"] = CategoryLibraryStaff.objects.filter(
            type_staff=self.request.user.type_staff,
        )

        context["library_staff"] = LibraryStaff.objects.filter(
            type_staff=self.request.user.type_staff,
        )

        return context


user_detail_view = UserDetailView.as_view()


class UserLoginView(LoginView):
    template_name = "account/login.html"
    redirect_authenticated_user = True


user_login_view = UserLoginView.as_view()
