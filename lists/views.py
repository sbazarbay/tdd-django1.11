from django.contrib.auth import get_user_model
from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import redirect, render
from django.views.generic import CreateView, DetailView, FormView

from lists.forms import ExistingListItemForm, ItemForm, NewListForm
from lists.models import List

User = get_user_model()


class HomePageView(FormView):
    template_name = "home.html"
    form_class = ItemForm


class ViewAndAddToList(DetailView, CreateView):
    model = List
    template_name = "list.html"
    form_class = ExistingListItemForm

    def get_form(self):
        self.object = self.get_object()
        return self.form_class(for_list=self.object, data=self.request.POST)


class NewListView(CreateView):
    form_class = NewListForm
    template_name = "home.html"

    def form_valid(self, form: NewListForm):
        list_ = form.save(owner=self.request.user)
        return redirect(list_)


def new_list(request: WSGIRequest):
    form = NewListForm(data=request.POST)
    if form.is_valid():
        list_ = form.save(owner=request.user)
        return redirect(list_)
    return render(request, "home.html", {"form": form})


def my_lists(request, email):
    owner = User.objects.get(email=email)
    return render(request, "my_lists.html", {"owner": owner})


def share_list(request: WSGIRequest, list_id):
    user_email = request.POST.get("sharee")
    list_: List = List.objects.get(pk=list_id)
    if request.method == "POST" and user_email:
        user = User.objects.get(email=user_email)
        list_.shared_with.add(user)

    return redirect(list_)
