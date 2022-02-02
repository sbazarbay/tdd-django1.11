from django.conf.urls import include, url
# from django.contrib import admin
from lists import views as list_views
from lists import urls as list_urls

urlpatterns = [
    # url(r'^admin/', admin.site.urls),
    url(r'^$', list_views.home_page, name="home"),
    url(r'^lists/', include(list_urls)),
]
