from upwork_scanner import *


def run():
    cls = UpworkScraper()
    cls.login()
    cls.scrape_homepage()
    cls.collect_homepage_data()
    cls.scrape_profile_page()
    cls.collect_profile_data()
    cls.scrape_contact_info_page()
    return cls.collect_contact_info_data()


def main():
    max_retries = 2
    tries = 1
    x = run()
    while tries <= max_retries and x is None:
        print(f"Scanning Failed. Re-trying.... Attempt // {tries}")
        tries += 1
        run()


if __name__ == "__main__":
    main()
