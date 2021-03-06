from functional_tests.base import FunctionalTest


class MyListsPage(object):
    def __init__(self, test):
        self.test: FunctionalTest = test

    def go_to_my_lists_page(self):
        self.test.browser.get(self.test.live_server_url)
        self.test.browser.find_element_by_link_text("My lists").click()
        self.test.wait_for(
            lambda: self.test.assertEqual(
                self.test.browser.find_element_by_tag_name("h1").text, "My Lists"
            )
        )
        return self

    def go_to_list_page(self, list_name):
        self.test.browser.find_element_by_link_text(list_name).click()
