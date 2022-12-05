from scrapy import Selector
import json
from user_data_profile import user_data
import country_converter as coco
from phonenumberfmt import format_phone_number
from data_model import UpworkUser


class UpworkParser:
    def __init__(self):
        self.base_url = "https://www.upwork.com"
        self.user_profile_data = user_data

    def parse_homepage(self, html_body: str, data_dict: dict):
        """
        Collect all data scraped from the homepage and save it to a json file.
        """
        try:
            print("Parsing homepage data and saving it to JSON file...")
            # Load the html body
            html_body = Selector(text=html_body)

            # Get valuable data
            name = html_body.css('a[class="profile-title"]::text').get().strip()
            available_connects = html_body.css('section[data-test="sidebar-available-connects"] > a::text').get().strip()
            hours_per_week = html_body.css('div[data-test="freelancer-sidebar-availability"] > div:nth-child(2) > span > span::text').get().strip()
            specialization = html_body.css('div.text-center > p::text').get().strip()
            categories = [x.strip() for x in html_body.css('section[data-test="sidebar-categories"] > div:nth-child(2) > *::text').getall()]
            profile_completeness = html_body.css('div.profile-completeness-nudges-tiles-alternative > div > div > small::text').get().strip()

            data_dict['name'] = name
            data_dict['available_connects'] = available_connects
            data_dict['hours_per_week'] = hours_per_week
            data_dict['specialization'] = specialization
            data_dict['categories'] = categories
            data_dict['profile_completeness'] = profile_completeness

            # Serialize it to json
            data_json = json.dumps(data_dict, indent=2)

            # Create the json file with the content
            with open("../level_1_task.json", "w") as outfile:
                outfile.write(data_json)

        except Exception as err:
            self.handle_error(err, "parse_homepage")

    def parse_profile_data(self, html_body: str, user_profile_data: dict):
        """
        Collect all data scraped from the profile page for the user profile.
        """
        try:
            print("Parsing profile page data...")
            # Load the HTML body
            html_body = Selector(text=html_body)

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
            user_profile_data["employer"] = employer
            user_profile_data["picture_url"] = picture_url
            user_profile_data["address"]["city"] = city
            user_profile_data["address"]["state"] = state
            user_profile_data["address"]["country"] = country_format
            user_profile_data["metadata"] = {
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
            self.handle_error(err, "parse_pofile_data")

    def parse_contact_info_data(self, html_body: str, user_profile_data: dict):
        """
        Collect all data scraped from the profile contact info page for the user profile.
        """
        try:
            print("Parsing contact info page data and validating final data...")
            # Load the html body of the page
            info_html = Selector(text=html_body)

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
            user_profile_data["first_name"] = first_name
            user_profile_data["last_name"] = last_name
            user_profile_data["full_name"] = f"{first_name} {last_name}"
            user_profile_data["email"] = e_mail
            user_profile_data["phone_number"] = phone_number_format
            user_profile_data["address"]["line1"] = street_address
            user_profile_data["address"]["line2"] = ap_number
            user_profile_data["address"]["postal_code"] = postal_code

            # Check if all fields have been completed
            self.check_empty_fields(user_profile_data)

            # Serialize the fields to a pydantic data model
            user = UpworkUser.parse_obj(user_profile_data)
            print(user_profile_data)
            print(user)

            return user_profile_data

        except Exception as err:
            self.handle_error(err, "parse_contact_info_data")

    def check_empty_fields(self, user: dict):
        """
        Method to check if the fields in the dict are empty.
        """
        for value in user.keys():
            if not user[value]:
                user[value] = "No available information."

    def handle_error(self, err, method_name: str):
        """
        Method to handle errors that may appear.
        """
        print(f"Fail to parse data in {method_name}. Got err: {err}")
