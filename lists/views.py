from django.contrib.auth import get_user_model
from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import redirect
from django.views.generic import DetailView  # RedirectView,; UpdateView,
from django.views.generic import CreateView, FormView

from lists.forms import ExistingListItemForm, ItemForm, NewListForm, ShareListForm
from lists.models import List

User = get_user_model()


class HomePageView(FormView):
    template_name = "home.html"
    form_class = ItemForm


# TODO: Use class inheritance to switch between forms?
class CreateOrExistingListView(DetailView, CreateView):
    model = List
    template_name = "list.html"
    form_class = ExistingListItemForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["share_list_form"] = ShareListForm(for_list=self.object)
        return context

    def get_form(self):
        self.object = self.get_object()
        if self.request.POST:
            return self.form_class(for_list=self.object, data=self.request.POST)
        return self.form_class(for_list=self.object)


class NewListView(CreateView):
    form_class = NewListForm
    template_name = "home.html"

    def form_valid(self, form: NewListForm):
        self.object = form.save(owner=self.request.user)
        return redirect(self.object)


class MyListsView(DetailView):
    model = User
    template_name = "my_lists.html"
    context_object_name = "owner"


# class ShareListView(UpdateView, RedirectView):
#     model = List
#     form_class = ShareListForm
#     template_name = "list.html"


def share_list(request: WSGIRequest, pk):
    list_: List = List.objects.get(pk=pk)

    if request.method == "POST":
        share_list_form = ShareListForm(
            for_list=list_, data=request.POST, for_request=request
        )
        if share_list_form.is_valid():
            share_list_form.save()

    return redirect(list_)
