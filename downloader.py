#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import sys
import threading
import Queue
from optparse import OptionParser, OptionError, OptionConflictError
from optparse import OptionValueError, BadOptionError, AmbiguousOptionError
import time

from httpsend.httpsend import httpsend


class Loader(threading.Thread):
    """
    Download URL and save to file
    """

    def __init__(self, url_queue, thread_name):
        threading.Thread.__init__(self, name=thread_name)

        self._HTTP = httpsend()
        self._URLQueue = url_queue

    def run(self):
        while True:
            try:
                url = self._URLQueue.get()
                page = self._HTTP.Request(url)
                t = time.time()
                strf = (self.getName(), t)
                f = open('%s_%s.html' % strf, 'w')
                f.write(page)
            finally:
                f.close()
                self._URLQueue.task_done()


class Download(object):
    """
    Download URL list
    """

    def __init__(self, urls, number_threads):
        self._urls = urls
        self._number_threads = number_threads

    def Run(self):
        url_queue = Queue.Queue()

        for url in self._urls:
            url_queue.put(url)

        for i in xrange(self._number_threads):
            loader = Loader(url_queue, 't%d' % i)
            loader.setDaemon(True)
            loader.start()

        url_queue.join()


def GetCommands():
    parser = OptionParser()
    try:
        parser.add_option('-n', '--number',
            type='int',
            action='store',
            dest='number',
            help='set number of threads (by default: 10)',
            default='10')
        parser.add_option('-f', '--filename',
            type='string',
            action='store',
            dest='filename',
            help='set filename (e.g.: urls.txt)')
    except AmbiguousOptionError, e:
        print e
    except (OptionConflictError, OptionValueError, BadOptionError), e:
        print e
    except OptionError, e:
        print e

    options, args = parser.parse_args(args=None)
    try:
        number = max(1, abs(options.number))
        filename = options.filename if options.filename else args[0]
        return (number, filename)
    except (AttributeError, UnboundLocalError), e:
        print e

def main():
    number, filename = GetCommands()
    urls = [url[:-1] for url in open(filename, 'r').readlines()]
    download = Download(urls, number)
    download.Run()

if __name__ == '__main__':
    main()