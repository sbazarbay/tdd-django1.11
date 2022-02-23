from django.contrib import messages
from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from django.views.generic import CreateView, DetailView, FormView, RedirectView
from django.views.generic.edit import ModelFormMixin

from lists.forms import ExistingListItemForm, ItemForm, NewListForm, ShareListForm
from lists.models import List

SHARE_LIST_SUCCESS = "The list has been successfully shared."
SHARE_LIST_FAIL = "Given email is invalid or doesn't exist in Superlists."

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


class ShareListView(ModelFormMixin, RedirectView):
    model = List
    form_class = ShareListForm
    pattern_name = "view_list"

    def get_form(self) -> ShareListForm:
        return self.form_class(for_list=self.get_object(), data=self.request.POST)

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            messages.success(
                self.request,
                SHARE_LIST_SUCCESS,
            )
            return self.form_valid(form)

        messages.error(
            self.request,
            SHARE_LIST_FAIL,
        )
        return super().post(request, *args, **kwargs)
