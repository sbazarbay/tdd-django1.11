from django.forms import ValidationError
from django.shortcuts import redirect, render

from lists.models import Item, List


def home_page(request):
    return render(request, "home.html")


def view_list(request, list_id):
    list_ = List.objects.get(id=list_id)

    return render(request, "list.html", {"list": list_})


def new_list(request):
    list_ = List.objects.create()
    item_text = request.POST["item_text"]
    item = Item(text=item_text, list=list_)
    try:
        item.full_clean()
        item.save()
    except ValidationError:
        list_.delete()
        error = "You can't have an empty list item"
        return render(request, "home.html", {"error": error})
    return redirect(f"/lists/{list_.id}/")


def add_item(request, list_id):
    list_ = List.objects.get(id=list_id)
    item_text = request.POST["item_text"]
    Item.objects.create(text=item_text, list=list_)
    return redirect(f"/lists/{list_.id}/")
