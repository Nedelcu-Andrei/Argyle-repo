from upwork_scanner import UpworkScanner
from upwork_parser import UpworkParser


def run():
    parse = UpworkParser()
    cls = UpworkScanner(parse)
    cls.login()
    cls.scan_homepage()
    cls.scan_profile_page()
    return cls.scan_contact_info_page()


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
