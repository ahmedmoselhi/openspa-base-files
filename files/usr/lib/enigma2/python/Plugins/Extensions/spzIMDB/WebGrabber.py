import os
import urllib2
import socket
from sys import version_info
import sys, traceback
from HtmlEncoding import decode_htmlentities
import xml.dom.minidom as minidom
import Utf8
import re
cacheDir = '/tmp/cachehttp'
downloadDir = '/tmp/cachehttp'
RETRIES = 3
import urllib
import urlparse

def url_fix(s):
    scheme, netloc, path, qs, anchor = urlparse.urlsplit(s)
    path = urllib.quote(path, '/%')
    qs = urllib.quote_plus(qs, ':&=')
    return urlparse.urlunsplit((scheme,
     netloc,
     path,
     qs,
     anchor))


def folderSize(folder):
    folder_size = 0
    for path, dirs, files in os.walk(folder):
        for file in files:
            filename = os.path.join(path, file)
            folder_size += os.path.getsize(filename)

    return folder_size / 1048576.0


def freeSpace(folder):
    s = os.statvfs(folder)
    return s.f_bavail * s.f_frsize / 1048576.0


def checkCache(url):
    if not os.path.isdir(cacheDir):
        os.mkdir(cacheDir)
    if not os.path.isdir(downloadDir):
        os.mkdir(downloadDir)
    cacheFile = re.sub('\\W', '', url).strip()
    rtv = None
    if os.path.isfile(Utf8.utf8ToLatin(cacheDir + '/' + cacheFile + '.cache')):
        f = Utf8.Utf8(cacheDir + '/' + cacheFile + '.cache', 'r')
        rtv = f.read()
        f.close()
    return rtv


def addCache(url, text):
    if folderSize(cacheDir) > 4.0 or freeSpace(cacheDir) < 2.0:
        for f in os.listdir(cacheDir):
            file = os.path.join(cacheDir, f)
            os.remove(file)

    cacheFile = re.sub('\\W', '', url).strip()
    if text is not None and len(text) > 0:
        f = Utf8.Utf8(cacheDir + '/' + cacheFile + '.cache', 'w')
        f.write(text)
        f.close


def getXml(url):
    rawXml = getText(url)
    decodedXml = None
    try:
        if rawXml is not None:
            try:
                decodedXml = minidom.parseString(rawXml)
            except Exception as ex:
                decodedXml = minidom.parseString(rawXml.encode('utf-8'))

    except Exception as ex:
        print 'URL', Utf8.utf8ToLatin(url)
        print 'WebGrabber.getXml: ', ex

    return decodedXml


def getHtml(url):
    rawHtml = getText(url)
    decodedHtml = None
    try:
        if rawHtml is not None:
            decodedHtml = decode_htmlentities(rawHtml)
    except Exception as ex:
        print 'URL', Utf8.utf8ToLatin(url)
        print 'WebGrabber.getHtml: ', ex

    return decodedHtml


def getText(url):
    utfPage = checkCache(url)
    if utfPage is None:
        for i in range(RETRIES):
            page = None
            kwargs = {}
            if version_info[1] >= 6:
                kwargs['timeout'] = 10
            else:
                socket.setdefaulttimeout(10)
            try:
                opener = urllib2.build_opener()
                opener.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux x86_64; en-GB; rv:1.8.1.6) Gecko/20070723 Iceweasel/2.0.0.6 (Debian-2.0.0.6-0etch1)')]
                page = opener.open(url_fix(Utf8.utf8ToLatin(url)))
            except Exception as ex:
                print 'URL', Utf8.utf8ToLatin(url)
                print 'urllib2::urlopen: ', ex
                continue

            if page is not None:
                rawPage = page.read()
                utfPage = Utf8.stringToUtf8(rawPage)
                addCache(url, utfPage)
                break

    return utfPage


def getJson(url):
    rawHtml = getTextj(url)
    return rawHtml
    decodedHtml = None
    try:
        if rawHtml is not None:
            decodedHtml = decode_htmlentities(rawHtml)
    except Exception as ex:
        print 'URL', Utf8.utf8ToLatin(url)
        print 'WebGrabber.getHtml: ', ex

    return decodedHtml


def getTextj(url):
    utfPage = checkCache(url)
    if utfPage is None:
        for i in range(RETRIES):
            page = None
            kwargs = {}
            if version_info[1] >= 6:
                kwargs['timeout'] = 10
            else:
                socket.setdefaulttimeout(10)
            try:
                opener = urllib2.build_opener()
                opener.addheaders = [('Content-Type', 'application/json; charset=utf-8'), ('Accept', 'application/json'), ('User-Agent', 'Mozilla/5.0 (X11; U; Linux x86_64; en-GB; rv:1.8.1.6) Gecko/20070723 Iceweasel/2.0.0.6 (Debian-2.0.0.6-0etch1)')]
                page = opener.open(url_fix(Utf8.utf8ToLatin(url)))
            except Exception as ex:
                print 'URL ERROR:[' + Utf8.utf8ToLatin(url) + ']'
                print 'urllib2::urlopen: ', ex
                continue

            if page is not None:
                rawPage = page.read()
                utfPage = str(rawPage)
                addCache(url, utfPage)
                break

    else:
        utfPage = utfPage + '}'
    return utfPage


def getFile(url, name, retry = 3):
    localFilename = downloadDir + '/' + name
    url = url.strip()
    if os.path.isfile(Utf8.utf8ToLatin(localFilename)) is False:
        for i in range(retry):
            try:
                page = urllib2.urlopen(url_fix(Utf8.utf8ToLatin(url)), timeout=5)
                f = open(Utf8.utf8ToLatin(localFilename), 'wb')
                f.write(page.read())
                f.close()
                break
            except Exception as ex:
                print 'File download failed: ', ex
                print 'Name: ', Utf8.utf8ToLatin(name)
                print 'Url: ', Utf8.utf8ToLatin(url)
                print type(ex)
                print '-' * 60
                traceback.print_exc(file=sys.stdout)
                print '-' * 60
