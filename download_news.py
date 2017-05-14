#!/usr/bin/env python
"""Get a list of news on businesswire
"""
import threading
import urllib

import requests
from lxml import etree
from lxml.cssselect import CSSSelector


class SequentialDownloader(object):
    """docstring for SequentialDownloader"""
    def __init__(self, arg):
        super(SequentialDownloader, self).__init__()
        self.arg = arg


class ThreadDownloader(object):
    """docstring for ThreadDownloader"""
    def __init__(self, arg):
        super(ThreadDownloader, self).__init__()
        self.arg = arg


class ProcessDownloader(object):
    """docstring for ProcessDownloader"""
    def __init__(self, arg):
        super(ProcessDownloader, self).__init__()
        self.arg = arg



class ConcurrentDownloader(object):
    """docstring for ConcurrentDownloader"""
    def __init__(self, arg):
        super(ConcurrentDownloader, self).__init__()
        self.arg = arg


class HybridDownloader(object):
    """docstring for HybridDownloader"""
    def __init__(self, arg):
        super(HybridDownloader, self).__init__()
        self.arg = arg


class GeventDownloader(object):
    """docstring for GeventDownloader"""
    def __init__(self, arg):
        super(GeventDownloader, self).__init__()
        self.arg = arg


class AsyncIODownloader(object):
    """docstring for AsyncIODownloader"""
    def __init__(self, arg):
        super(AsyncIODownloader, self).__init__()
        self.arg = arg

