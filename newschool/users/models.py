from django.contrib.auth.models import AbstractUser
from django.db.models import CharField
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Default custom user model for NewSchool.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """

    # First and last name do not cover name patterns around the globe

    first_name = None  # type: ignore[assignment]
    last_name = None  # type: ignore[assignment]
    type_account = CharField(
        _("Type staff"),
        choices=[("admin", "Admin"), ("teacher", "Teacher"), ("student", "Student")],
        max_length=10,
        default="student",
    )

    def get_absolute_url(self) -> str:
        """Get URL for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"username": self.username})
