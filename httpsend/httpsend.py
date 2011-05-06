#-------------------------------------------------------------------------------
# Name:        httpsend
# Purpose:
#
# Author:      Sergey Pikhovkin
#
# Created:     26.08.2010
# Copyright:   (c) Sergey Pikhovkin 2010
# Licence:     New-style BSD
#-------------------------------------------------------------------------------

# -*- coding: UTF-8 -*-

__author__ = "Sergey Pikhovkin (s@pikhovkin.ru)"
__version__ = "0.3.0.0"
__copyright__ = "Copyright (c) 2010 Sergey Pikhovkin"
__license__ = "New-style BSD"

import urllib, urllib2, cookielib, urllib2handlers
from StringIO import StringIO
import gzip


class httpsend(object):
    HEADERS = [
        ('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 6.0; ru; rv:1.9.1.7) Gecko/20091221 Firefox/3.5.7'),
        ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'),
        ('Accept-Language', 'ru,en-us;q=0.7,en;q=0.3'),
        ('Accept-Encoding', 'gzip,deflate'),
        ('Accept-Charset', 'utf-8;q=0.7,*;q=0.7'),
        ('Keep-Alive', '300'),
        ('Connection', 'keep-alive')
    ]

    URL = ''

    def __init__(self):
        self.Status = 0
        self.HTTPProxy = None
        self.CookieHandler = urllib2.HTTPCookieProcessor(cookielib.CookieJar())
        self.RedirectHandler = urllib2handlers.SmartRedirectHandler()
        self.HTTPHandler = urllib2.HTTPHandler()
        self.HTTPSHandler = urllib2.HTTPSHandler()

        self.Opener = urllib2.build_opener(
            self.HTTPHandler,
            self.HTTPSHandler,
            self.CookieHandler,
            self.RedirectHandler)
        if self.HTTPProxy:
            self.ProxyHandler = urllib2.ProxyHandler(HTTPProxy)
            self.Opener.add_handler(self.ProxyHandler)

        urllib2.install_opener(self.Opener)

    def gunzip(self, stream):
        try:
            gz = gzip.GzipFile(fileobj=StringIO(stream))
        except:
            return ''
        return gz.read()

    def Request(self, url, params={}, header=[], on_success=None, on_failure=None):
        h = header if header else self.HEADERS
        self.Opener.addheaders = h
        try:
            if params: # POST
                params = urllib.urlencode(params)
                resource = self.Opener.open(url, params)
            else: # GET
                resource = self.Opener.open(url)

            self.Status = resource.status \
                if hasattr(resource, 'status') else resource.code

            self.URL = resource.url
            page = resource.read()
            info = resource.info()
            self.Cookies = self.CookieHandler.cookiejar
            s = info.get('Content-Encoding')
            if s and s.find('gzip') > -1:
                page = self.gunzip(page)

            if on_success:
                on_success(self.URL, page, info, status)
        except Exception, e:
            self.URL = url

            if on_failure:
                on_failure(url, e)
            page = ''
        return page

if __name__ == '__main__':
    h = httpsend()
    print h.Request('http://mail.ru')