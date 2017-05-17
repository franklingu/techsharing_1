#!/usr/bin/env python
"""Get a list of news on businesswire
"""
import threading
import multiprocessing
import queue
import time
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
import asyncio

import requests
import gevent


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
                task_queue.task_done()
            except queue.Empty:
                return


class ProcessDownloader(NewsDownloader):
    """docstring for ProcessDownloader"""
    def __init__(self, *arg, **kwargs):
        super(ProcessDownloader, self).__init__()
        self.num_processes = 4
        if 'num_processes' in kwargs:
            self.num_processes = kwargs['num_processes']

    def download_news(self, links):
        task_queue = multiprocessing.JoinableQueue()
        result_queue = multiprocessing.Queue()
        for link in links:
            task_queue.put(link)
        for idx in range(self.num_threads):
            worker = multiprocessing.Process(
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
                task_queue.task_done()
            except queue.Empty:
                return


class ConcurrentDownloader(NewsDownloader):
    """docstring for ConcurrentDownloader"""
    def __init__(self, *arg, **kwargs):
        super(ConcurrentDownloader, self).__init__()
        self.num_workers = 4
        if 'num_workers' in kwargs:
            self.num_workers = kwargs['num_workers']

    def download_news(self, links):
        with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
            fs_map = {
                link: executor.submit(
                    self._send_news_request, link)
                for link in links
            }
            as_completed(fs_map.values())
            return {link: ft.result() for link, ft in fs_map.items()}


class GeventDownloader(NewsDownloader):
    """docstring for GeventDownloader"""
    def __init__(self, *arg, **kwargs):
        super(GeventDownloader, self).__init__()
        self.num_workers = 4
        if 'num_workers' in kwargs:
            self.num_workers = kwargs['num_workers']
        gevent.monkey.patch_all(thread=False, select=False)

    def download_news(self, links):
        raise NotImplemented
        worker_pool = gevent.pool.Pool(self.num_workers)
        jobs = [self._download_worker(worker_pool, link) for link in links]
        gevent.joinall(jobs)

    def _download_worker(self, pool, link):
        return pool.spawn(self._send_news_request, link=link)


class AsyncIODownloader(NewsDownloader):
    """docstring for AsyncIODownloader"""
    def __init__(self, *arg, **kwargs):
        super(AsyncIODownloader, self).__init__()

    async def download_news(self, links):
        self._ret = {}
        loop = asyncio.get_event_loop()
        ret_map = {}
        for link in links:
            future = loop.run_in_executor(None, self._send_news_request, link)
            ret_map[link] = future
        for ft in ret_map.values():
            await ft
        for link, ft in ret_map.items():
            self._ret[link] = ft.result()

    def retrive_result(self):
        return self._ret


if __name__ == '__main__':
    links = [
        'http://www.google.com',
        'http://stackoverflow.com/questions/22190403/how-could-i-use-requests-in-asyncio',
        'https://docs.python.org/3/library/concurrent.futures.html',
        'http://docs.bonobo-project.org/en/0.2/tutorial/tut01.html',
        'http://basic.10jqka.com.cn/000738/company.html',
        'https://github.com/codelucas/newspaper/blob/master/newspaper/article.py',
        'https://github.com/codelucas/newspaper/blob/master/newspaper/article.py',
        'https://github.com/codelucas/newspaper',
    ]
    start = time.time()
    loop = asyncio.get_event_loop()
    async_worker = AsyncIODownloader()
    loop.run_until_complete(async_worker.download_news(links))
    end = time.time()
    print('Asyncio:', end - start, len(async_worker.retrive_result()))
    start = time.time()
    sq_worker = SequentialDownloader()
    ret = sq_worker.download_news(links)
    end = time.time()
    print('Sequential:', end - start, len(ret))
    start = time.time()
    thread_worker = ThreadDownloader()
    ret = thread_worker.download_news(links)
    end = time.time()
    print('Thread:', end - start, len(ret))
    start = time.time()
    cc_worker = ConcurrentDownloader()
    ret = cc_worker.download_news(links)
    end = time.time()
    print('Concurrent:', end - start, len(ret))
