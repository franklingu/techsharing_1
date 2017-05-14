#!/usr/bin/env python
"""Get a list of news links on businesswire
"""
import time
import random
import urllib

import requests
from lxml import etree
from lxml.cssselect import CSSSelector


def get_news_home_links(retry=3, sleep=30):
    url = 'http://www.businesswire.com/portal/site/home/news/'
    headers = {
        'Referer': 'http://www.businesswire.com/portal/site/home/',
        'User-Agent': (
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
            ' (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'
        )
    }
    root_url = 'http://www.businesswire.com/'
    selector = CSSSelector('#headlines > ul > li > div > a')
    html_parser = etree.HTMLParser()
    for retry_num in range(retry):
        try:
            res = requests.get(url, headers=headers)
            if res.status_code != 200:
                raise ValueError(
                    'Response is not OK: {}'.format(res.status_code)
                )
            parsed = etree.fromstring(res.content, html_parser)
            for link_elem in selector(parsed):
                yield urllib.parse.urljoin(root_url, link_elem.get('href'))
            break
        except Exception:
            if retry_num >= retry - 1:
                raise
            time.sleep(sleep + sleep * random.random())


if __name__ == '__main__':
    for link in get_news_home_links():
        print(link)
