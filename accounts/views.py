from django.contrib import auth, messages
from django.core.handlers.wsgi import WSGIRequest
from django.core.mail import send_mail
from django.urls import reverse
from django.views.generic import RedirectView
from django.views.generic.edit import ModelFormMixin

from accounts.forms import LoginForm
from accounts.models import Token

TOKEN_SUCCESS = "Check your email, we've sent you a link you can use to log in."
TOKEN_FAILURE = "Please enter a valid email address."


class SendLoginEmailView(ModelFormMixin, RedirectView):
    model = Token
    form_class = LoginForm
    pattern_name = "home"
    url = "/"

    def post(self, request: WSGIRequest, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            self.object: Token = form.save()
            email = self.object.email
            url = request.build_absolute_uri(
                reverse("login") + "?token=" + str(self.object.uid)
            )
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

        return super().post(request, *args, **kwargs)


class LoginView(RedirectView):
    pattern_name = "home"

    def get_redirect_url(self, *args, **kwargs):
        user = auth.authenticate(uid=self.request.GET.get("token"))
        if user:
            auth.login(self.request, user)
        return super().get_redirect_url(*args, **kwargs)
