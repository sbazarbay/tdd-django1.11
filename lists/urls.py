from django.conf.urls import url

from lists import views

urlpatterns = [
    url(r"^new$", views.NewListView.as_view(), name="new_list"),
    url(r"^(?P<pk>\d+)/$", views.CreateOrExistingListView.as_view(), name="view_list"),
    url(r"^users/(?P<pk>.+)/$", views.MyListsView.as_view(), name="my_lists"),
    url(r"^(?P<pk>\d+)/share$", views.share_list, name="share_list"),
]
