import email
import imaplib
import os
import re
import time
from email.header import decode_header

from django.core import mail
from selenium.webdriver.common.keys import Keys

from functional_tests.base import FunctionalTest

SUBJECT = "Your login link for Superlists"


class LoginTest(FunctionalTest):
    def wait_for_email(self, test_email, subject):
        if not self.staging_server:
            email_fake = mail.outbox[0]
            self.assertIn(test_email, email_fake.to)
            self.assertEqual(email_fake.subject, subject)
            return email_fake.body

        start = time.time()
        imap = imaplib.IMAP4_SSL("imap.gmail.com", 993)
        imap.login(test_email, os.environ["TEST_EMAIL_PASSWORD"])
        _, messages = imap.select("INBOX")
        messages = int(messages[0])

        while time.time() - start < 60:
            for i in range(messages, messages - 3, -1):
                # fetch the email message by ID
                _, msg = imap.fetch(str(i), "(RFC822)")
                for response in msg:
                    if isinstance(response, tuple):
                        # parse a bytes email into a message object
                        msg = email.message_from_bytes(response[1])
                        # decode the email subject
                        ext_subject, encoding = decode_header(msg["Subject"])[0]
                        if isinstance(ext_subject, bytes):
                            # if it's a bytes, decode to str
                            ext_subject = ext_subject.decode(encoding)
                        if subject in ext_subject:
                            # get the email body
                            body = msg.get_payload(decode=True).decode()
                            return body
            time.sleep(5)

        return None

        # email_id = None
        # start = time.time()
        # inbox = poplib.POP3_SSL("pop.gmail.com")
        # try:
        #     inbox.user(test_email)
        #     inbox.pass_(os.environ["TEST_EMAIL_PASSWORD"])
        #     while time.time() - start < 60:
        #         # get 10 newest messages
        #         count, _ = inbox.stat()
        #         for i in reversed(range(max(1, count - 10), count + 1)):
        #             print("getting msg", i)
        #             _, lines, __ = inbox.retr(i)
        #             lines = [line.decode("utf8") for line in lines]
        #             if f"Subject: {subject}" in lines:
        #                 email_id = i
        #                 body = "\n".join(lines)
        #                 return body

        #         time.sleep(5)
        # finally:
        #     if email_id:
        #         inbox.dele(email_id)
        #     inbox.quit()

    def test_can_get_email_link_to_log_in(self):
        if self.staging_server:
            test_email = "c.bazarbai@gmail.com"
        else:
            test_email = "edith@example.com"

        # Edith goes to the awesome superlists site and notices a "Log in" section in
        # the navbar for the first time
        self.browser.get(self.live_server_url)

        # She accidentally presses enter key, but then sees an error message
        self.browser.find_element_by_name("email").send_keys(Keys.ENTER)
        self.wait_for(
            lambda: self.assertIn(
                "Please enter a valid email address.",
                self.browser.find_element_by_css_selector(".alert-danger").text,
            )
        )

        # It's telling her to enter a valid email address, so she does
        self.browser.find_element_by_name("email").send_keys(test_email)
        self.browser.find_element_by_name("email").send_keys(Keys.ENTER)

        # A message appears telling her an email has been sent
        self.wait_for(
            lambda: self.assertIn(
                "Check your email",
                self.browser.find_element_by_css_selector(".alert-success").text,
            )
        )

        # She checks her email and finds a message
        body = self.wait_for_email(test_email, SUBJECT)

        # It has a url link in it
        self.assertIn("Use this link to log in", body)
        url_search = re.search(r"http://.+/.+$", body)
        if not url_search:
            self.fail(f"Could not find url in email body:\n{body}")
        url = url_search.group(0)
        self.assertIn(self.live_server_url, url)

        # she clicks it
        self.browser.get(url)

        # she is logged in!
        self.wait_to_be_logged_in(email=test_email)

        # Now she logs out
        self.browser.find_element_by_link_text("Log out").click()

        # She is logged out
        self.wait_to_be_logged_out(email=test_email)
