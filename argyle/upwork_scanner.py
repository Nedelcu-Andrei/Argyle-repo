from playwright.sync_api import sync_playwright
from scrapy import Selector
from config import configure
import os
from upwork_parser import UpworkParser
from user_data_profile import user_data, data_dict


class UpworkScanner:
    def __init__(self, parser: UpworkParser):
        configure()
        self.user = os.getenv("UPWORK_USERNAME")
        self.passw = os.getenv("PASSWORD")
        self.secret = os.getenv("SECRET")
        self.login_portal = "https://www.upwork.com/ab/account-security/login"
        self.base_url = "https://www.upwork.com"
        self.page = None
        self.browser = None
        self.pw = sync_playwright().start()
        self.parser = parser

    def login(self):
        """
        Logins into the website using the username, password and occasionally the secret question.
        """
        try:
            # Create the browser, instantiate the page for it and go to url
            self.browser = self.pw.chromium.launch(headless=False, slow_mo=100)

            self.page = self.browser.new_page()
            self.page.goto(self.login_portal)
            self.page.once("load", lambda: print("Page loaded!"))

            # Wait for the username field, populate it and continue
            self.page.wait_for_selector('#login_username', timeout=10000)
            self.page.fill('#login_username', self.user)
            self.page.click('#login_password_continue')

            # Wait for password field, populate it and continue
            self.page.wait_for_selector('#login_password', timeout=10000)
            self.page.fill('#login_password', self.passw)
            self.page.click('#login_control_continue')

            # If it asks for secret, populate it, else continue without it
            try:
                self.page.wait_for_selector('#login_answer', timeout=10000)
                self.page.fill('#login_answer', self.secret)
                self.page.click('#login_control_continue')
            except Exception:
                print("Continuing without secret.")

            print("Login has been done succesfully!")

        except Exception as err:
            self.handle_error(err, "login")

    def scan_homepage(self):
        """
        Scan the homepage of the website for valuable data.
        """
        try:
            self.page.once("load", lambda: print("Scanning the homepage.."))
            # Close the pop-up page
            self.check_popup(self.page.inner_html('body'))

            # Check the data has been loaded into the page and scrape important elements
            self.page.wait_for_selector('a[class="profile-title"]')

            # Parse the data
            self.parser.parse_homepage(self.page.inner_html('body'), data_dict)

        except Exception as err:
            self.handle_error(err, "scan_homepage")

    def scan_profile_page(self):
        """
        Scan the profile page for the user profile data.
        """
        try:
            self.page.once("load", lambda: print("Scanning profile page..."))
            # Close the pop-up page if it appears
            self.check_popup(self.page.inner_html('body'))

            # Check if the elements have been loaded properly then go to the profile page
            self.page.wait_for_selector('a.profile-title')
            self.page.click('a.profile-title')

            # Check if the next page has been loaded
            self.page.wait_for_selector(
                'section.up-card-section > div > ul > li > div > div > h4[role="presentation"]')

            # Prase the data
            self.parser.parse_profile_data(self.page.inner_html('body'),
                                           user_data)

        except Exception as err:
            self.handle_error(err, "scan_profile_page")

    def scan_contact_info_page(self):
        """
        Scan contact info page for the user profile data.
        """
        try:
            self.page.once("load",
                           lambda: print("Scanning contact info page..."))
            # Check for the popup window and close it if it appears
            self.check_popup(self.page.inner_html('body'))

            # Get the contact info url from the page and go to it
            contact_info_url = self.page.get_attribute(
                "ul[data-cy='dropdown-menu'] > li:nth-child(4) > ul > li > a",
                "href")
            self.page.goto(f"{self.base_url}{contact_info_url}")

            # Check if the secret is needed, if not, wait for the page to load up
            try:
                self.page.wait_for_selector('input[id="deviceAuth_answer"]')
                self.page.fill('input[id="deviceAuth_answer"]', self.secret)
                self.page.click('button[id="control_save"]')
                self.page.wait_for_selector('div[data-test="userId"]')
            except Exception:
                self.page.wait_for_selector('div[data-test="userId"]')

            # Parse and return the data, else stop and retry
            contact_info_result = self.parser.parse_contact_info_data(
                self.page.inner_html('body'), user_data)

            if contact_info_result is None:
                self.pw.stop()
            else:
                return contact_info_result

        except Exception as err:
            self.handle_error(err, "scan_contact_info_page")
            self.pw.stop()

    def check_popup(self, page):
        """
        Method to check if the pop-up page appears. If it appears, it closes it.
        """
        check_popup = Selector(text=page)
        if check_popup.css('button[data-cy="close-button"] > div > svg'):
            self.page.click('button[data-cy="close-button"] > div > svg')

    def handle_error(self, err, method_name: str):
        """
        Method to handle errors that may appear.
        """
        if self.page.is_closed():
            print(f"Page already closed in {method_name} due to a prior error.")
        else:
            print(
                f"Failed to scan in method {method_name}. Got err: {err}. Closing the page")
            self.page.close()
