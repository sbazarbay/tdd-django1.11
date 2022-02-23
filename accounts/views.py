from django.contrib import auth, messages
from django.core.handlers.wsgi import WSGIRequest
from django.core.mail import send_mail
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import RedirectView

from accounts.forms import LoginForm
from accounts.models import Token

TOKEN_SUCCESS = "Check your email, we've sent you a link you can use to log in."
TOKEN_FAILURE = "Please enter a valid email address."


def send_login_email(request: WSGIRequest):
    form = LoginForm(data=request.POST)
    if form.is_valid():
        token: Token = form.save()
        email = token.email
        url = request.build_absolute_uri(reverse("login") + "?token=" + str(token.uid))
        message_body = f"Use this link to log in:\n\n{url}"
        send_mail(
            "Your login link for Superlists",
            message_body,
            "noreply@superlists",
            [email],
        )
        messages.success(request, TOKEN_SUCCESS)
    else:
        messages.error(request, TOKEN_FAILURE)

    return redirect("/")


class LoginView(RedirectView):
    pattern_name = "home"
    pass

    def get_redirect_url(self, *args, **kwargs):
        user = auth.authenticate(uid=self.request.GET.get("token"))
        if user:
            auth.login(self.request, user)
        return super().get_redirect_url(*args, **kwargs)
