from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from functional_tests.base import FunctionalTest
from functional_tests.pages.list_page import ListPage


class SharingValidationTest(FunctionalTest):
    def test_invalid_form_input(self):
        # Edith is a long-time user of superlists
        self.create_pre_authenticated_session("edith@example.com")
        edith_browser = self.browser
        edith_browser.quit()

        # A new (anonymous) user just created a list
        self.browser = webdriver.Firefox()
        self.browser.get(self.live_server_url)
        list_page = ListPage(self).add_list_item("Interesting...")

        # Now he sees "share" form and accedentally presses enter, only to be reminded
        # by a helpful HTML5 validator that the form cannot be blank
        share_box = list_page.get_share_box()
        share_box.send_keys(Keys.ENTER)
        self.wait_for(
            lambda: self.browser.find_element_by_css_selector("#id_shared_with:invalid")
        )

        # He tries to randomly put some letters, but again, sees HTML5 validator
        share_box.send_keys("ABABAB")
        self.wait_for(
            lambda: self.browser.find_element_by_css_selector("#id_shared_with:invalid")
        )

        # He doesn't know anyone, but wants to try and share the list with a random user
        share_box.send_keys("ABABAB@example.com")
        share_box.send_keys(Keys.ENTER)

        # He gets redirected back to the same page, and sees a helpful error message
        self.wait_for(
            lambda: self.assertEqual(
                self.browser.find_element_by_css_selector(".alert-danger").text,
                "Given email is invalid or doesn't exist in Superlists.",
            )
        )

        # He remembered that his friend Edith uses Superlists, and tries to input her
        # email
        list_page.share_list_with("edith@example.com")

        # He sees a message that it was successful!
        self.wait_for(
            lambda: self.assertEqual(
                self.browser.find_element_by_css_selector(".alert-success").text,
                "The list has been successfully shared.",
            )
        )
