import httpretty
import sure
from dummyauth.spider import EndpointDiscoverySpider
from unittest import TestCase


class EndpointDiscoverySpiderTestCase(TestCase):

    @httpretty.httprettified
    def test_spider_can_use_headers_for_auth_endpoint(self):
        # Set up the authorization endpoint as an HTTP header.
        request_headers = ', '.join([
            '<http://login.example.com/auth>; rel="authorization_endpoint"',
            '<http://login.example.com/token>; rel="token_endpoint"'
        ])
        httpretty.register_uri(httpretty.HEAD, 'http://johndoe.example.com',
                               adding_headers={'Link': request_headers})

        spider = EndpointDiscoverySpider('http://johndoe.example.com')
        auth_endpoint = spider.authorization_endpoint
        token_endpoint = spider.token_endpoint

        auth_endpoint.should.equal('http://login.example.com/auth')
        token_endpoint.should.equal('http://login.example.com/token')

    @httpretty.httprettified
    def test_spider_solves_non_absolute_links_in_headers(self):
        # Set up the authorization endpoint as an HTTP header.
        request_headers = ', '.join([
            '</auth>; rel="authorization_endpoint"',
            '<extra/token>; rel="token_endpoint"'
        ])
        httpretty.register_uri(httpretty.HEAD, 'http://example.com/johndoe/',
                               adding_headers={'Link': request_headers})

        spider = EndpointDiscoverySpider('http://example.com/johndoe/')
        auth_endpoint = spider.authorization_endpoint
        token_endpoint = spider.token_endpoint

        auth_endpoint.should.equal('http://example.com/auth')
        token_endpoint.should.equal('http://example.com/johndoe/extra/token')

    @httpretty.httprettified
    def test_spider_fetches_html_if_no_headers_have_links(self):
        httpretty.register_uri(httpretty.HEAD, 'http://johndoe.example.com')
        httpretty.register_uri(httpretty.GET, 'http://johndoe.example.com',
                               body="""<!DOCTYPE html>
        <html>
            <head>
                <title>John Doe Website</title>
                <link rel="canonical" href="http://johndoe.example.com">
                <link rel="authorization_endpoint" href="http://auth.example.com/">
                <link rel="token_endpoint" href="http://token.example.com/">
            </head>
        </html>
        """)

        spider = EndpointDiscoverySpider('http://johndoe.example.com')
        auth_endpoint = spider.authorization_endpoint
        token_endpoint = spider.token_endpoint

        auth_endpoint.should.equal('http://auth.example.com/')
        token_endpoint.should.equal('http://token.example.com/')

    @httpretty.httprettified
    def test_spider_solves_non_absolute_links_in_html(self):
        httpretty.register_uri(httpretty.HEAD, 'http://example.com/johndoe/')
        httpretty.register_uri(httpretty.GET, 'http://example.com/johndoe/',
                               body="""<!DOCTYPE html>
        <html>
            <head>
                <title>John Doe Website</title>
                <link rel="canonical" href="http://example.com/johndoe/">
                <link rel="authorization_endpoint" href="/auth">
                <link rel="token_endpoint" href="extra/token">
            </head>
        </html>
        """)

        spider = EndpointDiscoverySpider('http://example.com/johndoe/')
        auth_endpoint = spider.authorization_endpoint
        token_endpoint = spider.token_endpoint

        auth_endpoint.should.equal('http://example.com/auth')
        token_endpoint.should.equal('http://example.com/johndoe/extra/token')

    @httpretty.httprettified
    def test_spider_fetches_html_if_a_header_is_missing(self):
        link = '<http://auth.example.com/>; rel="authorization_endpoint"'
        httpretty.register_uri(httpretty.HEAD, 'http://johndoe.example.com',
                               adding_headers={'Link': link})
        httpretty.register_uri(httpretty.GET, 'http://johndoe.example.com',
                               body="""<!DOCTYPE html>
        <html>
            <head>
                <title>John Doe Website</title>
                <link rel="canonical" href="http://johndoe.example.com">
                <link rel="token_endpoint" href="http://token.example.com/">
            </head>
        </html>
        """)

        spider = EndpointDiscoverySpider('http://johndoe.example.com')
        auth_endpoint = spider.authorization_endpoint
        token_endpoint = spider.token_endpoint

        auth_endpoint.should.equal('http://auth.example.com/')
        token_endpoint.should.equal('http://token.example.com/')

    @httpretty.httprettified
    def test_spider_prioritizes_headers_over_html_tags(self):
        link = '<http://auth.example.com/>; rel="authorization_endpoint"'
        httpretty.register_uri(httpretty.HEAD, 'http://johndoe.example.com',
                               adding_headers={'Link': link})
        httpretty.register_uri(httpretty.GET, 'http://johndoe.example.com',
                               body="""<!DOCTYPE html>
        <html>
            <head>
                <title>John Doe Website</title>
                <link rel="canonical" href="http://johndoe.example.com">
                <link rel="authorization_endpoint" href="/auth">
                <link rel="token_endpoint" href="http://token.example.com/">
            </head>
        </html>
        """)

        spider = EndpointDiscoverySpider('http://johndoe.example.com')
        auth_endpoint = spider.authorization_endpoint
        auth_endpoint.should.equal('http://auth.example.com/')

    @httpretty.httprettified
    def test_spider_follows_temporally_redirects(self):
        old_headers = {'Location': 'http://new.example.com'}
        httpretty.register_uri(httpretty.HEAD, 'http://old.example.com',
                               status=302, adding_headers=old_headers)
        link_tags = ', '.join([
            '<http://login.example.com/auth>; rel="authorization_endpoint"',
            '<http://login.example.com/token>; rel="token_endpoint"'
        ])
        httpretty.register_uri(httpretty.HEAD, 'http://new.example.com',
                               adding_headers={'Link': link_tags})

        spider = EndpointDiscoverySpider('http://old.example.com')
        spider.canonical_url.should.equal('http://old.example.com')
        spider.target_url.should.equal('http://new.example.com')

    @httpretty.httprettified
    def test_spider_follows_permanent_redirects(self):
        old_headers = {'Location': 'http://new.example.com'}
        httpretty.register_uri(httpretty.HEAD, 'http://old.example.com',
                               status=301, adding_headers=old_headers)
        link_tags = ', '.join([
            '<http://login.example.com/auth>; rel="authorization_endpoint"',
            '<http://login.example.com/token>; rel="token_endpoint"'
        ])
        httpretty.register_uri(httpretty.HEAD, 'http://new.example.com',
                               adding_headers={'Link': link_tags})

        spider = EndpointDiscoverySpider('http://old.example.com')
        spider.canonical_url.should.equal('http://new.example.com')
        spider.target_url.should.equal('http://new.example.com')
