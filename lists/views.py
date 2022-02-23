from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from django.views.generic import CreateView, DetailView, FormView, RedirectView

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


class ShareListView(RedirectView):
    pattern_name = "view_list"

    def get_redirect_url(self, *args, **kwargs):
        pk = self.request.resolver_match.kwargs["pk"]
        list_ = List.objects.get(pk=pk)
        if self.request.method == "POST":
            share_list_form = ShareListForm(
                for_list=list_, data=self.request.POST, for_request=self.request
            )
            if share_list_form.is_valid():
                share_list_form.save()

        return super().get_redirect_url(*args, **kwargs)
