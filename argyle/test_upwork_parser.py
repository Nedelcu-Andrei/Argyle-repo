import unittest
import pytest
from upwork_parser import UpworkParser
from test_constants import map_html_body
from scrapy import Selector
from user_data_profile import user_data, data_dict


class UpworkParserTests(unittest.TestCase):
    @pytest.fixture(autouse=True)
    def create_test_context(self):
        self.parser = UpworkParser()
        self.parse_homepage_body = map_html_body['parse_homepage']
        self.parse_profile_data_body = map_html_body['parse_profile_data']
        self.parse_contact_info_data_body = map_html_body['parse_contact_info_data']
        self.invalid_data_list = [1, 2, 3]
        self.invalid_tuple_list = (1, 2, 3)
        self.invalid_error = ValueError
        self.data_dict = data_dict
        self.user_profile_data = user_data

    def test_invalid_parse_homepage(self):
        assert self.parser.parse_homepage(self.invalid_data_list, self.data_dict) is None

    def test_valid_parse_homepage(self):
        self.parser.parse_homepage(self.parse_homepage_body, self.data_dict)
        assert self.data_dict['name'] == 'Bobby B.'
        assert self.data_dict['profile_completeness'] == '30%'
        assert len(self.data_dict['categories']) == 2

    def test_invalid_parse_profile_data(self):
        assert self.parser.parse_profile_data(self.invalid_tuple_list, self.user_profile_data) is None

    def test_valid_parse_profile_page(self):
        self.parser.parse_profile_data(self.parse_profile_data_body, self.user_profile_data)
        assert self.user_profile_data['employer'] == 'All Party No Work Company'
        assert self.user_profile_data["address"]["city"] == 'Miami'
        assert len(self.user_profile_data['metadata']) == 6

    def test_invalid_parse_contact_info_data(self):
        assert self.parser.parse_contact_info_data(self.invalid_error, self.user_profile_data) is None

    def test_valid_parse_contact_info_data(self):
        self.parser.parse_contact_info_data(self.parse_contact_info_data_body, self.user_profile_data)
        assert self.user_profile_data['last_name'] == 'Backupy'
        assert self.user_profile_data["address"]["postal_code"] == '123456'
        assert self.user_profile_data["phone_number"].startswith("+1")

    def test_invalid_type_empty_fields(self):
        with pytest.raises(AttributeError):
            self.parser.check_empty_fields(self.invalid_data_list)

    def test_valid_type_empty_fields(self):
        mock_data = {
            "data": ""
        }
        self.parser.check_empty_fields(mock_data)
        assert mock_data['data'] == "No available information."
