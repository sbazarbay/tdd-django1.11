import json

from django.test import TestCase

from lists.forms import DUPLICATE_ITEM_ERROR, EMPTY_ITEM_ERROR
from lists.models import Item, List


class ListAPITest(TestCase):
    base_url = "/api/lists/{}/"

    def post_empty_input(self):
        list_: List = List.objects.create()
        return self.client.post(self.base_url.format(list_.pk), data={"text": ""})

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

    def test_for_invalid_input_nothing_saved_to_db(self):
        self.post_empty_input()
        self.assertEqual(Item.objects.count(), 0)

    def test_for_invalid_input_returns_error_code(self):
        response = self.post_empty_input()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            json.loads(response.content.decode("utf8")), {"error": EMPTY_ITEM_ERROR}
        )

    def test_duplicate_items_error(self):
        list_: List = List.objects.create()
        self.client.post(self.base_url.format(list_.pk), data={"text": "thing"})
        response = self.client.post(
            self.base_url.format(list_.pk), data={"text": "thing"}
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            json.loads(response.content.decode("utf8")), {"error": DUPLICATE_ITEM_ERROR}
        )
