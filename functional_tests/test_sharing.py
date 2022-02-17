from unittest import skip
from selenium import webdriver

from functional_tests.base import FunctionalTest
from functional_tests.pages.list_page import ListPage
from functional_tests.pages.my_lists_page import MyListsPage


def quit_if_possible(browser: webdriver.Firefox):
    try:
        browser.quit()
    except Exception:
        pass


class SharingTest(FunctionalTest):
    @skip
    def test_can_share_a_list_with_another_user(self):
        # Edith is a logged-in user
        self.create_pre_authenticated_session("edith@example.com")
        edith_browser = self.browser

        # Her friend Oniciferous is also hanging out on the lists site
        oni_browser = webdriver.Firefox()
        self.addCleanup(lambda: quit_if_possible(oni_browser))
        self.browser = oni_browser

        self.create_pre_authenticated_session("oniciferous@example.com")

        # Edith goes to the home page and starts a list
        self.browser = edith_browser
        self.browser.get(self.live_server_url)
        list_page = ListPage(self).add_list_item("Get help")

        # She notices a "Share this list" option
        share_box = list_page.get_share_box()
        self.assertEqual(
            share_box.get_attribute("placeholder"), "your-friend@example.com"
        )

        # She shares her list.
        # The page updates to say that it's shared with Oniciferous:
        list_page.share_list_with("oniciferous@example.com")

        # Oniciferous now goes to the lists page with his browser
        self.browser = oni_browser
        my_lists_page = MyListsPage(self).go_to_my_lists_page()

        # He sees Edith's list in there!
        my_lists_page.go_to_list_page("Get help")

        # On the list page, Oniciferous can see say that it's Edith's list
        self.wait_for(
            lambda: self.assertEqual(list_page.get_list_owner(), "edith@example.com")
        )

        # He adds an item to the list
        list_page.add_list_item("Hi Edith!")

        # When Edith refreshes the page, she sees Oniciferous's addition
        self.browser = edith_browser
        self.browser.refresh()
        list_page.wait_for_row_in_list_table("Hi Edith!", 2)
