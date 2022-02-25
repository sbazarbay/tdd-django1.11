from django.conf.urls import url
from django.contrib.auth.views import logout  # using deprecated method

from accounts import views

urlpatterns = [
    url(
        r"^send_login_email$",
        views.SendLoginEmailView.as_view(),
        name="send_login_email",
    ),
    url(r"^login$", views.LoginView.as_view(), name="login"),
    url(r"^logout$", logout, {"next_page": "/"}, name="logout"),
]
