from django.contrib.auth.models import AbstractUser
from django.db.models import PROTECT
from django.db.models import ForeignKey
from django.urls import reverse


class User(AbstractUser):
    """
    Default custom user model for NewSchool.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """

    type_staff = ForeignKey(
        "staff.TypeStaff",
        on_delete=PROTECT,
        null=True,
        blank=True,
    )

    REQUIRED_FIELDS = []

    def get_absolute_url(self) -> str:
        """Get URL for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"username": self.username})
