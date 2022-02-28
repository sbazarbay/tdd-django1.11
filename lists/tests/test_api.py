import json

from django.test import TestCase

from lists.models import Item, List


class ListAPITest(TestCase):
    base_url = "/api/lists/{}/"

    def test_get_returns_json_200(self):
        list_: List = List.objects.create()
        response = self.client.get(self.base_url.format(list_.pk))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["content-type"], "application/json")

    def test_get_returns_items_for_correct_list(self):
        List.create_new("item 1")
        our_list: List = List.objects.create()
        item1: Item = Item.objects.create(list=our_list, text="item 1")
        item2: Item = Item.objects.create(list=our_list, text="item 2")
        response = self.client.get(self.base_url.format(our_list.pk))
        self.assertEqual(
            json.loads(response.content.decode("utf8")),
            [
                {"id": item1.pk, "text": item1.text},
                {"id": item2.pk, "text": item2.text},
            ],
        )

    def test_posting_a_new_item(self):
        list_: List = List.objects.create()
        response = self.client.post(
            self.base_url.format(list_.pk), {"text": "new item"}
        )
        self.assertEqual(response.status_code, 201)
        new_item: Item = list_.item_set.get()
        self.assertEqual(new_item.text, "new item")
