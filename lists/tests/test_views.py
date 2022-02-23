import unittest
from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.utils.datastructures import MultiValueDict
from django.utils.html import escape

from lists.forms import (DUPLICATE_ITEM_ERROR, EMPTY_ITEM_ERROR, SHARE_LIST_FAIL,
                         SHARE_LIST_SUCCESS, ExistingListItemForm, ItemForm)
from lists.models import Item, List
from lists.views import NewListView

User = get_user_model()


class HomePageTest(TestCase):
    def test_home_page_returns_correct_html(self):
        response = self.client.get("/")
        self.assertTemplateUsed(response, "home.html")

    def test_home_page_uses_item_form(self):
        response = self.client.get("/")
        self.assertIsInstance(response.context["form"], ItemForm)


class ListViewTest(TestCase):
    def test_uses_list_template(self):
        list_ = List.objects.create()
        response = self.client.get(f"/lists/{list_.id}/")
        self.assertTemplateUsed(response, "list.html")

    def test_passes_correct_list_to_template(self):
        # other_list = List.objects.create()
        correct_list = List.objects.create()
        response = self.client.get(f"/lists/{correct_list.id}/")
        self.assertEqual(response.context["list"], correct_list)

    def test_displays_only_items_for_that_list(self):
        correct_list = List.objects.create()
        Item.objects.create(text="itemey 1", list=correct_list)
        Item.objects.create(text="itemey 2", list=correct_list)
        other_list = List.objects.create()
        Item.objects.create(text="other list item 1", list=other_list)
        Item.objects.create(text="other list item 2", list=other_list)

        response = self.client.get(f"/lists/{correct_list.id}/")

        self.assertContains(response, "itemey 1")
        self.assertContains(response, "itemey 2")
        self.assertNotContains(response, "other list item 1")
        self.assertNotContains(response, "other list item 2")

    def test_can_save_a_post_request_to_an_existing_list(self):
        List.objects.create()
        correct_list = List.objects.create()

        self.client.post(
            f"/lists/{correct_list.id}/",
            data={"text": "A new item for an existing list"},
        )
        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, "A new item for an existing list")
        self.assertEqual(new_item.list, correct_list)

    def test_post_redirects_to_list_view(self):
        List.objects.create()
        correct_list = List.objects.create()

        response = self.client.post(
            f"/lists/{correct_list.id}/",
            data={"text": "A new item for an existing list"},
        )
        self.assertRedirects(response, f"/lists/{correct_list.id}/")

    def post_invalid_input(self):
        list_ = List.objects.create()
        return self.client.post(f"/lists/{list_.id}/", data={"text": ""})

    def test_for_invalid_input_nothing_saved_to_db(self):
        self.post_invalid_input()
        self.assertEqual(Item.objects.count(), 0)

    def test_for_invalid_input_renders_list_template(self):
        response = self.post_invalid_input()
        self.assertEqual(response.status_code, 200)

    def test_for_invalid_input_passes_form_to_template(self):
        response = self.post_invalid_input()
        self.assertIsInstance(response.context["form"], ExistingListItemForm)

    def test_for_invalid_input_shows_error_on_page(self):
        response = self.post_invalid_input()
        self.assertContains(response, escape(EMPTY_ITEM_ERROR))

    def test_displays_item_form(self):
        list_ = List.objects.create()
        response = self.client.get(f"/lists/{list_.id}/")
        self.assertIsInstance(response.context["form"], ExistingListItemForm)
        self.assertContains(response, 'name="text"')

    def test_duplicate_item_validation_errors_end_up_on_lists_page(self):
        list1 = List.objects.create()
        Item.objects.create(list=list1, text="textey")
        response = self.client.post(f"/lists/{list1.id}/", data={"text": "textey"})

        expected_error = escape(DUPLICATE_ITEM_ERROR)
        self.assertContains(response, expected_error)
        self.assertTemplateUsed(response, "list.html")
        self.assertEqual(Item.objects.all().count(), 1)

    def test_display_no_error_messages_on_get_request(self):
        list_: List = List.objects.create()
        response = self.client.get(f"/lists/{list_.pk}/")
        self.assertNotContains(response, escape(EMPTY_ITEM_ERROR))


class NewListViewIntegratedTest(TestCase):
    def test_can_save_a_post_request(self):
        self.client.post("/lists/new", data={"text": "A new list item"})

        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, "A new list item")

    def test_for_invalid_input_doesnt_save_but_shows_errors(self):
        response = self.client.post("/lists/new", data={"text": ""})
        self.assertEqual(List.objects.count(), 0)
        self.assertContains(response, escape(EMPTY_ITEM_ERROR))

    def test_list_owner_is_saved_if_user_is_authenticated(self):
        user = User.objects.create(email="a@b.com")
        self.client.force_login(user)
        self.client.post("/lists/new", data={"text": "new item"})
        list_: List = List.objects.first()
        self.assertEqual(list_.owner, user)


@patch("lists.views.NewListView.form_class")
class NewListViewUnitTest(unittest.TestCase):
    def setUp(self) -> None:
        path = reverse("new_list")
        data = {"text": "new list item"}
        self.request = RequestFactory().post(path=path, data=data)
        self.request.user = Mock()

    def new_list(self, request):
        return NewListView.as_view()(request)

    def test_passes_post_data_to_newlistform(self, mock_form_class):
        self.new_list(self.request)
        mock_form_class.assert_called_once_with(
            initial={},
            prefix=None,
            data=self.request.POST,
            files=MultiValueDict(),
            instance=None,
        )

    def test_saves_form_with_owner_if_form_valid(self, mock_form_class):
        mock_form = mock_form_class.return_value
        mock_form.is_valid.return_value = True
        self.new_list(self.request)
        mock_form.save.assert_called_once_with(owner=self.request.user)

    @patch("lists.views.redirect")
    def test_redirects_to_form_returned_object_if_form_valid(
        self, mock_redirect, mock_form_class
    ):
        mock_form = mock_form_class.return_value
        mock_form.is_valid.return_value = True
        response = self.new_list(self.request)
        self.assertEqual(response, mock_redirect.return_value)
        mock_redirect.assert_called_once_with(mock_form.save.return_value)

    @patch("lists.views.NewListView.response_class")
    def test_renders_home_template_with_form_if_form_invalid(
        self, mock_response_class, mock_form_class
    ):
        mock_form = mock_form_class.return_value
        mock_form.is_valid.return_value = False

        response = self.new_list(self.request)

        mock_response_class.assert_called_once()
        self.assertEqual(response, mock_response_class.return_value)

        _, kwargs = mock_response_class.call_args

        self.assertEqual(kwargs["template"], ["home.html"])
        self.assertEqual(kwargs["context"]["form"], mock_form)

    def test_does_not_save_if_form_invalid(self, mock_form_class):
        mock_form = mock_form_class.return_value
        mock_form.is_valid.return_value = False
        self.new_list(self.request)
        self.assertFalse(mock_form.save.called)


class MyListsTest(TestCase):
    def test_my_lists_url_renders_my_lists_template(self):
        User.objects.create(email="a@b.com")
        response = self.client.get("/lists/users/a@b.com/")
        self.assertTemplateUsed(response, "my_lists.html")

    def test_passes_correct_owner_to_template(self):
        User.objects.create(email="wrong@owner.com")
        correct_user = User.objects.create(email="a@b.com")
        response = self.client.get("/lists/users/a@b.com/")
        self.assertEqual(response.context["owner"], correct_user)


class ShareListTest(TestCase):
    def test_post_redirects_to_lists_page(self):
        List.objects.create()
        list_: List = List.objects.create()
        response = self.client.post(f"/lists/{list_.pk}/share")
        self.assertRedirects(response, f"/lists/{list_.pk}/")

    # TODO: def test_unauthenticated_cant_share_list(self):

    def test_user_added_to_shared_with(self):
        user = User.objects.create(email="bob@example.com")
        list_: List = List.objects.create()
        self.client.post(f"/lists/{list_.pk}/share", data={"shared_with": user.email})
        self.assertIn(user, list_.shared_with.all())

    def test_form_submission_redirects_back_to_list(self):
        user = User.objects.create(email="bob@example.com")
        list_: List = List.objects.create()
        response = self.client.post(
            f"/lists/{list_.pk}/share", data={"shared_with": user.email}
        )
        self.assertRedirects(response, f"/lists/{list_.pk}/")

    def test_success_message_is_sent(self):
        user = User.objects.create(email="bob@example.com")
        list_: List = List.objects.create()
        response = self.client.post(
            f"/lists/{list_.pk}/share", data={"shared_with": user.email}, follow=True
        )
        message = list(response.context["messages"])[0]
        self.assertEqual(
            message.message,
            SHARE_LIST_SUCCESS,
        )
        self.assertEqual(message.tags, "success")

    def test_error_message_is_sent_on_invalid_email(self):
        list_: List = List.objects.create()
        response = self.client.post(
            f"/lists/{list_.pk}/share", data={"shared_with": "asdf"}, follow=True
        )
        message = list(response.context["messages"])[0]
        self.assertEqual(
            message.message,
            SHARE_LIST_FAIL,
        )
        self.assertEqual(message.tags, "error")

    def test_error_message_is_sent_on_empty_email(self):
        list_: List = List.objects.create()
        response = self.client.post(
            f"/lists/{list_.pk}/share", data={"shared_with": ""}, follow=True
        )
        message = list(response.context["messages"])[0]
        self.assertEqual(
            message.message,
            SHARE_LIST_FAIL,
        )
        self.assertEqual(message.tags, "error")
