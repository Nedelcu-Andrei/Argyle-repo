import json
from playwright.sync_api import sync_playwright
from scrapy import Selector
from config import configure
import os
from data_model import UpworkUser
import country_converter as coco
from user_data_profile import user_data
from phonenumberfmt import format_phone_number


def check_empty_fields(user):
    """
    Method to check if the fields in the dict are empty.
    """
    for value in user.keys():
        if not user[value]:
            user[value] = "No available information."


class UpworkScraper:
    def __init__(self):
        configure()
        self.user = os.getenv("UPWORK_USERNAME")
        self.passw = os.getenv("PASSWORD")
        self.secret = os.getenv("SECRET")
        self.login_portal = "https://www.upwork.com/ab/account-security/login"
        self.base_url = "https://www.upwork.com"
        self.page = None
        self.browser = None
        self.user_data = user_data
        self.pw = sync_playwright().start()

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

    def scrape_homepage(self):
        """
        Scrape the homepage of the website for valuable data.
        """
        try:
            self.page.once("load", lambda: print("Scraping the homepage.."))
            # Close the pop-up page
            self.check_popup(self.page.inner_html('body'))

            # Check the data has been loaded into the page and scrape important elements
            self.page.wait_for_selector('a[class="profile-title"]')

        except Exception as err:
            self.handle_error(err, "scrape_homepage")

    def collect_homepage_data(self):
        """
        Collect all data scraped from the homepage and save it to a json file.
        """
        try:
            # Load the html body
            html_body = Selector(text=self.page.inner_html('body'))

            # Get valuable data
            name = html_body.css('a[class="profile-title"]::text').get().strip()
            available_connects = html_body.css('section[data-test="sidebar-available-connects"] > a::text').get().strip()
            hours_per_week = html_body.css('div[data-test="freelancer-sidebar-availability"] > div:nth-child(2) > span > span::text').get().strip()
            specialization = html_body.css('div.text-center > p::text').get().strip()
            categories = [x.strip() for x in html_body.css('section[data-test="sidebar-categories"] > div:nth-child(2) > *::text').getall()]
            profile_completeness = html_body.css('div.profile-completeness-nudges-tiles-alternative > div > div > small::text').get().strip()

            # Build the dict object
            data_dict = {
                "name": name,
                "specialization": specialization,
                "available_connects": available_connects,
                "hours_per_week": hours_per_week,
                "categories": categories,
                "profile_completeness": profile_completeness
            }

            # Serialize it to json
            data_json = json.dumps(data_dict, indent=2)

            # Create the json file with the content
            with open("../level_1_task.json", "w") as outfile:
                outfile.write(data_json)

        except Exception as err:
            self.handle_error(err, "collect_homepage_data")

    def scrape_profile_page(self):
        """
        Scrape the profile page for the user profile data.
        """
        try:
            self.page.once("load", lambda: print("Scraping profile page..."))
            # Close the pop-up page if it appears
            self.check_popup(self.page.inner_html('body'))

            # Check if the elements have been loaded properly then go to the profile page
            self.page.wait_for_selector('a.profile-title')
            self.page.click('a.profile-title')

            # Check if the next page has been loaded
            self.page.wait_for_selector('section.up-card-section > div > ul > li > div > div > h4[role="presentation"]')

        except Exception as err:
            self.handle_error(err, "scrape_profile_page")

    def collect_profile_data(self):
        """
        Collect all data scraped from the profile page for the user profile.
        """
        try:
            # Load the HTML body
            html_body = Selector(text=self.page.inner_html('body'))

            # Get data related to address
            city = html_body.css('span[itemprop="locality"]::text').get().strip()
            state = html_body.css('span[itemprop="state-name"]::text').get().strip()
            country = html_body.css('span[itemprop="country-name"]::text').get().strip()
            country_format = coco.convert(names=country, to='ISO2')  # Format the country name

            # Other data related to the profile object
            picture_url = html_body.css('div.up-presence-container > img.up-avatar::attr(src)').get().strip()
            job_employer = html_body.css('section.up-card-section > div > ul > li > div > div > h4[role="presentation"]::text').get().split("|")
            employer = job_employer[-1].strip() if len(job_employer) > 1 else ""

            # Get rest of data available on the page and save it to metadata in the profile object
            # Freelance work related data
            specialization = html_body.css('section.up-card-section > div > div > div > h2::text').get().strip()
            hourly_rate = html_body.css('h3[role="presentation"] > span::text').get().strip()
            hours_per_week = html_body.css('section.up-card-section > div.mt-30 > div:nth-child(2) > span::text').get().strip()

            # Languages and military status data
            languages = html_body.css('ul.list-unstyled > li > div > strong::text').get().strip()
            proficiency = html_body.css('ul.list-unstyled > li > div > span::text').get().strip()
            language = f"{languages} {proficiency}"
            military_status = html_body.css('section.up-card-section > div.mt-30 > div > div > span > strong::text').get().strip()

            # Education related data
            university = html_body.css('ul.list-unstyled > li > div > h5[role="presentation"]::text').get().strip()
            degree = html_body.css('ul.list-unstyled > li > div > div::text').get().strip()
            university_years = html_body.css('ul.list-unstyled > li > div > div.text-muted::text').get().strip()

            # Set data in the user data profile
            self.user_data["employer"] = employer
            self.user_data["picture_url"] = picture_url
            self.user_data["address"]["city"] = city
            self.user_data["address"]["state"] = state
            self.user_data["address"]["country"] = country_format
            self.user_data["metadata"] = {
                "specialization": specialization,
                "hourly_rate": hourly_rate,
                "hours_per_week": hours_per_week,
                "language": language,
                "military_status": military_status,
                "education": {
                    "university": university,
                    "degree": degree,
                    "university_years": university_years
                }}

        except Exception as err:
            self.handle_error(err, "collect_profile_data")

    def scrape_contact_info_page(self):
        """
        Scrape contact info page for the user profile data.
        """
        try:
            self.page.once("load", lambda: print("Scraping contact info page..."))
            # Check for the popup window and close it if it appears
            self.check_popup(self.page.inner_html('body'))

            # Get the contact info url from the page and go to it
            contact_info_url = self.page.get_attribute("ul[data-cy='dropdown-menu'] > li:nth-child(4) > ul > li > a", "href")
            self.page.goto(f"{self.base_url}{contact_info_url}")

            # Check if the secret is needed, if not, wait for the page to load up
            try:
                self.page.wait_for_selector('input[id="deviceAuth_answer"]')
                self.page.fill('input[id="deviceAuth_answer"]', self.secret)
                self.page.click('button[id="control_save"]')
                self.page.wait_for_selector('div[data-test="userId"]')
            except Exception:
                self.page.wait_for_selector('div[data-test="userId"]')

        except Exception as err:
            self.handle_error(err, "scrape_contact_info_page")

    def collect_contact_info_data(self):
        """
        Collect all data scraped from the contact info page for the user profile.
        """
        try:
            # Load the html body of the page
            info_html = Selector(text=self.page.inner_html('body'))

            # Get name related data
            full_name = info_html.css('div[data-test="userName"]::text').get().strip().replace("\n", "").split(" ")
            first_name = full_name[0] if len(full_name) > 0 else ""
            last_name = full_name[-1] if len(full_name) > 1 else ""

            # Get address related data
            street_address = info_html.css('span[data-test="addressStreet"]::text').get().strip()
            ap_number = info_html.css('span[data-test="addressStreet2"]::text').get().strip()
            postal_code = info_html.css('span[data-test="addressZip"]::text').get().strip()

            # Get email and phone data
            phone_number = info_html.css('div[data-test="phone"]::text').get()
            phone_number_format = format_phone_number(phone_number, implied_phone_region='US')  # Format the phone data
            e_mail = info_html.css('div[data-test="userEmail"]::text').get().strip()

            # Set it in the user data profile
            self.user_data["first_name"] = first_name
            self.user_data["last_name"] = last_name
            self.user_data["full_name"] = f"{first_name} {last_name}"
            self.user_data["email"] = e_mail
            self.user_data["phone_number"] = phone_number_format
            self.user_data["address"]["line1"] = street_address
            self.user_data["address"]["line2"] = ap_number
            self.user_data["address"]["postal_code"] = postal_code

            # Check if all fields have been completed
            check_empty_fields(self.user_data)

            # Serialize the fields to a pydantic data model
            user = UpworkUser.parse_obj(self.user_data)
            print(self.user_data)
            print(user)

            return self.user_data

        except Exception as err:
            self.handle_error(err, "collect_contact_info_data")
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
            print(f"Failed to scrape in method {method_name}. Got err: {err}. Closing the page")
            self.page.close()