from unittest import TestCase
from dummyauth.forms import CanonicalFilter

class CanonicalFilterTestCase(TestCase):

    def test_filter_leaves_valid_urls_intact(self):
        valid_urls = [
            'https://example.com/',
            'https://example.com/profile',
            'https://example.com/profile?lang=ES',
        ]
        canonical_filter = CanonicalFilter()
        for valid_url in valid_urls:
            filtered_url = canonical_filter(valid_url)
            self.assertEqual(valid_url, filtered_url)

    def test_filter_adds_missing_path_component(self):
        invalid_url = 'http://example.com'
        filter = CanonicalFilter()
        self.assertEqual('http://example.com/', filter(invalid_url))

    def test_filter_converts_hostname_to_lowercase(self):
        invalid_url = 'https://Example.com/JohnDoe'
        filter = CanonicalFilter()
        self.assertEqual('https://example.com/JohnDoe', filter(invalid_url))

    def test_filter_prepends_a_scheme_if_a_scheme_is_missing(self):
        invalid_url = 'example.com/'
        filter = CanonicalFilter()
        self.assertEqual('http://example.com/', filter(invalid_url))

    def test_filter_can_create_an_url_from_a_hostname(self):
        hostname = 'example.com'
        filter = CanonicalFilter()
        self.assertEqual('http://example.com/', filter(hostname))

    def test_filter_keeps_invalid_stuff_intact(self):
        """
        The purpose of the filter is to get a canonical URL. Even if the
        profile URL is invalid, we have a validator for stuff like that.
        Do not remove stuff like usernames or passwords here.
        """
        url = 'https://user:pass@example.com:8443/#me'
        filter = CanonicalFilter()
        self.assertEqual('https://user:pass@example.com:8443/#me', filter(url))
