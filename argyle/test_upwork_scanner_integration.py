import unittest
import pytest
import os
from config import configure

configure()
user = os.getenv("UPWORK_USERNAME")
passw = os.getenv("PASSWORD")
secret = os.getenv("SECRET")
base_url = "https://www.upwork.com"


class UpworkScannerTests(unittest.TestCase):
    @pytest.fixture(autouse=True)
    def create_browser_context(self, page):
        page.goto('https://www.upwork.com/ab/account-security/login')
        page.fill('#login_username', user)
        page.click('#login_password_continue')
        page.fill('#login_password', passw)
        page.click('#login_control_continue')
        self.page = page

    def test_login(self):
        assert self.page.inner_text(
            '#fwh-sidebar-profile > div > h3 > a') == 'Bobby B.'
        assert self.page.inner_text(
            '#fwh-sidebar-profile > div > p') == 'Master Blockain IPO Executive management with Phd'

    def test_scan_profile_page(self):
        self.page.click('button[data-cy="close-button"] > div > svg')
        self.page.click('a.profile-title')
        assert self.page.inner_text(
            'h3[role="presentation"] > span').strip() == '$500.00/hr'
        assert self.page.inner_text(
            'span[itemprop="country-name"]').strip() == 'United States'
        assert self.page.get_attribute(
            "ul[data-cy='dropdown-menu'] > li:nth-child(4) > ul > li > a",
            "href") == "/freelancers/settings/contactInfo"

    def test_required_secret_auth(self):
        self.page.click('button[data-cy="close-button"] > div > svg')
        self.page.click('a.profile-title')
        self.page.click(
            '#main > div > div > div > div > div > div:nth-child(3) > div.up-card.py-0.my-0.d-none.d-lg-block > section.up-card-section.py-30 > div > div.col.col-auto.min-width-380.text-right > div > a.up-btn.up-btn-primary.m-0')
        self.page.wait_for_selector('#control_save')
        assert self.page.locator('#control_save').is_visible()

    def test_scan_contact_info_data(self):
        self.page.click('button[data-cy="close-button"] > div > svg')
        self.page.click('a.profile-title')
        self.page.click(
            '#main > div > div > div > div > div > div:nth-child(3) > div.up-card.py-0.my-0.d-none.d-lg-block > section.up-card-section.py-30 > div > div.col.col-auto.min-width-380.text-right > div > a.up-btn.up-btn-primary.m-0')
        self.page.wait_for_selector('#control_save')
        self.page.fill('input[id="deviceAuth_answer"]', secret)
        self.page.click('button[id="control_save"]')
        self.page.click(
            '#main > div > div > div.col-md-3.d-none.d-md-block > nav > div.user-settings-nav-container > div:nth-child(2) > ul > li.up-settings-list-item.up-settings-list-item-contact > a')
        assert self.page.inner_text(
            '#main > div > div > div.col-md-9 > main > div:nth-child(2) > header > h2').strip() == 'Account'
