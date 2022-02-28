import json

from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse

from lists.models import Item, List


def list(request: WSGIRequest, list_id):
    list_ = List.objects.get(pk=list_id)
    if request.method == "POST":
        Item.objects.create(list=list_, text=request.POST["text"])
        return HttpResponse(status=201)
    item_dicts = [{"id": item.id, "text": item.text} for item in list_.item_set.all()]
    return HttpResponse(json.dumps(item_dicts), content_type="application/json")
