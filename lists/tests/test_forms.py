import unittest
from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from lists.forms import (
    DUPLICATE_ITEM_ERROR,
    EMPTY_ITEM_ERROR,
    ExistingListItemForm,
    ItemForm,
    NewListForm,
    ShareListForm,
)
from lists.models import Item, List

User = get_user_model()


class ItemFormTest(TestCase):
    def test_form_renders_item_text_input(self):
        form = ItemForm()
        self.assertIn('placeholder="Enter a to-do item"', form.as_p())
        self.assertIn('class="form-control input-lg"', form.as_p())

    def test_form_validation_for_blank_items(self):
        form = ItemForm(data={"text": ""})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["text"], [EMPTY_ITEM_ERROR])


class ExistingListItemFormTest(TestCase):
    def test_form_renders_item_text_input(self):
        list_ = List.objects.create()
        form = ExistingListItemForm(for_list=list_)
        self.assertIn('placeholder="Enter a to-do item"', form.as_p())

    def test_form_validation_for_blank_items(self):
        list_ = List.objects.create()
        form = ExistingListItemForm(for_list=list_, data={"text": ""})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["text"], [EMPTY_ITEM_ERROR])

    def test_form_validation_for_duplicate_items(self):
        list_ = List.objects.create()
        Item.objects.create(list=list_, text="no twins!")
        form = ExistingListItemForm(for_list=list_, data={"text": "no twins!"})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["text"], [DUPLICATE_ITEM_ERROR])

    def test_form_save(self):
        list_ = List.objects.create()
        form = ExistingListItemForm(for_list=list_, data={"text": "hi"})
        new_item = form.save()
        self.assertEqual(new_item, Item.objects.all()[0])


class NewListFormTest(unittest.TestCase):
    @patch("lists.forms.List.create_new")
    def test_save_creates_new_list_from_post_data_if_user_not_authenticated(
        self, mockList_create_new
    ):
        user = Mock(is_authenticated=False)
        form = NewListForm(data={"text": "new item text"})
        form.is_valid()
        form.save(owner=user)
        mockList_create_new.assert_called_once_with(first_item_text="new item text")

    @patch("lists.forms.List.create_new")
    def test_save_creates_new_list_with_owner_if_user_authenticated(
        self, mock_List_create_new
    ):
        user = Mock(is_authenticated=True)
        form = NewListForm(data={"text": "new item text"})
        form.is_valid()
        form.save(owner=user)
        mock_List_create_new.assert_called_once_with(
            first_item_text="new item text", owner=user
        )

    @patch("lists.forms.List.create_new")
    def test_save_returns_new_list_object(self, mock_List_create_new):
        user = Mock(is_authenticated=True)
        form = NewListForm(data={"text": "new item text"})
        form.is_valid()
        response = form.save(owner=user)
        self.assertEqual(response, mock_List_create_new.return_value)


class ShareListFormTest(unittest.TestCase):
    def test_form_renders_item_text_input(self):
        list_ = List.objects.create()
        form = ShareListForm(for_list=list_)
        self.assertIn('placeholder="your-friend@example.com"', form.as_p())

    def test_form_save(self):
        list_ = List.objects.create()
        user = User.objects.create(pk="bob@example.com")
        form = ShareListForm(for_list=list_, data={"shared_with": user.pk})
        form.is_valid()
        shared_list = form.save()
        self.assertIn(shared_list, user.shared_lists.all())

    def test_form_applies_to_target_list(self):
        List.objects.create()
        list_ = List.objects.create()
        form = ShareListForm(for_list=list_)

        self.assertEqual(form.instance, list_)

    def test_doesnt_exist_form_doesnt_save(self):
        list_: List = List.objects.create()
        form = ShareListForm(for_list=list_, data={"shared_with": "asdf3@asdf.com"})
        self.assertTrue(form.is_valid())
        shared_list = form.save()
        self.assertEqual(shared_list.shared_with.count(), 0)
