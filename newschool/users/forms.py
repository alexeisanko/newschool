from crispy_forms.helper import FormHelper
from django import forms
from django.contrib.auth.forms import AuthenticationForm

from newschool.users.models import User


class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Username", max_length=30)
    password = forms.CharField(label="Password", widget=forms.PasswordInput)

    def __init__(LoginForm, self, *args, **kwargs):
        super(self).__init__(*args, **kwargs)
        self.fields["username"].widget.attrs["placeholder"] = "Username"
        self.fields["password"].widget.attrs["placeholder"] = "Password"
        self.fields["username"].field_class = "form-control"
        self.fields["password"].field_class = "form-control"


class UserCreationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("username", "password", "type_staff")
        widgets = {"password": forms.PasswordInput()}

    def __init__(self, *args, **kwargs):
        super(UserCreationForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.method = "POST"
        self.helper.form_class = "form-inline"
        self.helper.label_class = "col-lg-2"


class DateForStatisticsForm(forms.Form):
    date = forms.DateField(label="Отчетная дата", widget=forms.DateInput(attrs={"type": "date"}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.method = "POST"
        self.helper.form_class = "form-inline"
        self.helper.label_class = "col-lg-2"
