from django import forms

from accounts.models import Token


class LoginForm(forms.models.ModelForm):
    class Meta:
        model = Token
        fields = ("email",)
