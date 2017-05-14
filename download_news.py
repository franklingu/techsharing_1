#!/usr/bin/env python
"""Get a list of news on businesswire
"""
import threading
import multiprocessing
import queue
import time
import random

import requests
import gevent
from lxml import etree
from lxml.cssselect import CSSSelector


class NewsDownloader(object):
    """docstring for NewsDownloader"""
    def __init__(self, *args, **kwargs):
        super(NewsDownloader, self).__init__()
        self.headers = {
            'Referer': 'http://www.businesswire.com/portal/site/home/news/',
            'User-Agent': (
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
                ' (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36'
            )
        }
        self.retry = 3
        self.sleep = 30
        if 'retry' in kwargs:
            self.retry = kwargs['retry']
        if 'sleep' in kwargs:
            self.sleep = kwargs['sleep']

    def download_news(self, links):
        raise NotImplemented

    def _send_news_request(self, link):
        for retry_num in range(self.retry):
            try:
                res = requests.get(link, headers=self.headers)
                if res.status_code != 200:
                    raise ValueError(
                        'Response is not OK: {}'.format(res.status_code)
                    )
                return res.content
            except Exception:
                if retry_num >= self.retry - 1:
                    raise
                time.sleep(self.sleep + self.sleep * random.random())


class SequentialDownloader(NewsDownloader):
    """docstring for SequentialDownloader"""
    def __init__(self, *arg, **kwargs):
        super(SequentialDownloader, self).__init__()

    def download_news(self, links):
        result = {}
        for link in links:
            result[link] = self._send_news_request(link)
        return result


class ThreadDownloader(NewsDownloader):
    """docstring for ThreadDownloader"""
    def __init__(self, *arg, **kwargs):
        super(ThreadDownloader, self).__init__()
        self.num_threads = 4
        if 'num_threads' in kwargs:
            self.num_threads = kwargs['num_threads']

    def download_news(self, links):
        task_queue = queue.Queue()
        result_queue = queue.Queue()
        for link in links:
            task_queue.put(link)
        for idx in range(self.num_threads):
            worker = threading.Thread(
                target=self._download_worker, args=(task_queue, result_queue)
            )
            worker.start()
        task_queue.join()
        result = {}
        while True:
            try:
                link, res_content = result_queue.get(timeout=0.1)
                result[link] = res_content
            except queue.Empty:
                return result

    def _download_worker(self, task_queue, result_queue):
        while True:
            try:
                link = task_queue.get(timeout=0.1)
                res_content = self._send_news_request(link)
                result_queue.put((link, res_content))
                task_queue.done()
            except queue.Empty:
                return


class ProcessDownloader(NewsDownloader):
    """docstring for ProcessDownloader"""
    def __init__(self, *arg, **kwargs):
        super(ProcessDownloader, self).__init__()
        self.arg = arg


class ConcurrentDownloader(NewsDownloader):
    """docstring for ConcurrentDownloader"""
    def __init__(self, *arg, **kwargs):
        super(ConcurrentDownloader, self).__init__()
        self.arg = arg


class HybridDownloader(NewsDownloader):
    """docstring for HybridDownloader"""
    def __init__(self, *arg, **kwargs):
        super(HybridDownloader, self).__init__()
        self.arg = arg


class GeventDownloader(NewsDownloader):
    """docstring for GeventDownloader"""
    def __init__(self, *arg, **kwargs):
        super(GeventDownloader, self).__init__()
        self.arg = arg


class AsyncIODownloader(NewsDownloader):
    """docstring for AsyncIODownloader"""
    def __init__(self, *arg, **kwargs):
        super(AsyncIODownloader, self).__init__()
        self.arg = arg
