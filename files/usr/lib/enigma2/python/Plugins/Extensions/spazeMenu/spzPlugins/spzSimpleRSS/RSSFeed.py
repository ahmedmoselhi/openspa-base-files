from sets import Set
from TagStrip import strip, strip_readable
from Components.Scanner import ScanFile
from Components.config import config
import time
from os import environ, system
import gettext
from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE, fileExists
lang = language.getLanguage()
environ['LANGUAGE'] = lang[:2]
lenguaje = str(lang[:2])
gettext.bindtextdomain('enigma2', resolveFilename(SCOPE_LANGUAGE))
gettext.textdomain('enigma2')
gettext.bindtextdomain('spzSimpleRSS', '%s%s' % (resolveFilename(SCOPE_PLUGINS), 'Extensions/spazeMenu/spzPlugins/spzSimpleRSS/locale/'))

def pondebug(texto):
    return
    if texto == 'inicio':
        system('date > /tmp/rssdebug.log')
    system('date >> /tmp/rssdebug.log')
    system("echo '" + texto + "' >> /tmp/rssdebug.log")
    system("echo '-----------------------------------------' >> /tmp/rssdebug.log")


def _(txt):
    t = gettext.dgettext('spzSimpleRSS', txt)
    if t == txt:
        t = gettext.gettext(txt)
    return t


NS_RDF = '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}'
NS_RSS_09 = '{http://my.netscape.com/rdf/simple/0.9/}'
NS_RSS_10 = '{http://purl.org/rss/1.0/}'

def formateafecha(lafecha = None, sepa = '-', corta = False, hora = True):
    if not lafecha == None:
        t2 = lafecha
    else:
        t2 = time.localtime()
    t3 = time.localtime()
    cdia = str(time.strftime('%d', t2))
    cmes = str(time.strftime('%B', t2))
    cano = str(time.strftime('%Y', t2))
    xhoy = str(time.strftime('%d', t3)) + str(time.strftime('%B', t3)) + str(time.strftime('%Y', t3))
    diayer = str(int(time.strftime('%d', t3)) - 1)
    if len(diayer) == 1:
        diayer = '0' + diayer
    xay = str(diayer + str(time.strftime('%B', t3)) + str(time.strftime('%Y', t3)))
    if cdia + cmes + cano == xhoy:
        csemana = _('Today') + ' ' + _(str(time.strftime('%A', t2)))
    elif cdia + cmes + cano == xay:
        csemana = _('Yesterday') + ' ' + _(str(time.strftime('%A', t2)))
    else:
        csemana = _(str(time.strftime('%A', t2)))
    chora = ''
    if hora:
        chora = ' ' + str(time.strftime('%H:%M', t2))
    if corta:
        cmes = _(cmes)
        cmes = cmes[0:3]
        csemana = _(csemana)
        csemana = csemana[0:3]
        return cdia + sepa + cmes + chora
    else:
        return _(csemana) + ', ' + cdia + sepa + _(cmes) + sepa + cano + chora


def nunmes(cmes):
    cmes = str(cmes).lower()
    meses = {'jan': 1,
     'feb': 2,
     'mar': 3,
     'apr': 4,
     'may': 5,
     'jun': 6,
     'jul': 7,
     'aug': 8,
     'sep': 9,
     'oct': 10,
     'nov': 11,
     'dec': 12}
    if cmes in meses:
        ret = meses[cmes]
        cret = str(ret)
        if len(cret) == 1:
            cret = '0' + cret
    else:
        return '01'
    return cret


def cogefecha(eltiempo, formatohora = False):
    ret = eltiempo
    temptiempo = 'NA'
    try:
        if ',' in eltiempo:
            arrtiempo = eltiempo.split(' ')
            dia = arrtiempo[1]
            mes = arrtiempo[2]
            ano = arrtiempo[3]
            hora = arrtiempo[4]
            temptiempo = dia + ' ' + nunmes(mes) + ' ' + ano + ' ' + hora
            c = time.strptime(temptiempo, '%d %m %Y %H:%M:%S')
            pondebug('[cogefecha]' + str(formatohora) + ' c:' + str(c))
            if formatohora:
                return c
            ret = formateafecha(c)
    except:
        pondebug('[cogefecha]error ' + str(formatohora))

    pondebug('[cogefecha]' + str(formatohora) + ' ret:' + str(ret) + ' ---- tiempo:' + temptiempo)
    if formatohora:
        return None
    else:
        return ret


def formatea(loque):
    ret = loque
    if ret == None:
        return ret
    ret = ret.replace('&aacute;', '\xc3\xa1')
    ret = ret.replace('&eacute;', '\xc3\xa9')
    ret = ret.replace('&iacute;', '\xc3\xad')
    ret = ret.replace('&oacute;', '\xc3\xb3')
    ret = ret.replace('&uacute;', '\xc3\xba')
    ret = ret.replace('&Aacute;', '\xc3\x81')
    ret = ret.replace('&Eacute;', '\xc3\x89')
    ret = ret.replace('&Iacute;', '\xc3\x8d')
    ret = ret.replace('&Oacute;', '\xc3\x93')
    ret = ret.replace('&Uacute;', '\xc3\x9a')
    ret = ret.replace('&uuml;', '\xc3\xbc')
    ret = ret.replace('&Uuml;', '\xc3\x9c')
    ret = ret.replace('&ntilde;', '\xc3\xb1')
    ret = ret.replace('&Ntilde;', '\xc3\x91')
    ret = ret.replace('&#191;', '\xc2\xbf')
    ret = ret.replace('&#161', '\xc2\xa1')
    ret = ret.replace('&amp;', '&')
    ret = ret.replace('&quot;', '"')
    return ret


class ElementWrapper:

    def __init__(self, element, ns = ''):
        self._element = element
        self._ns = ns

    def __getattr__(self, tag):
        if tag.startswith('__'):
            raise AttributeError(tag)
        return self._element.findtext(self._ns + tag)


class RSSEntryWrapper(ElementWrapper):

    def __getattr__(self, tag):
        if tag == 'enclosures':
            myl = []
            for elem in self._element.findall(self._ns + 'enclosure'):
                length = elem.get('length')
                if length:
                    length = int(length) / 1048576
                myl.append({'href': elem.get('url'),
                 'type': elem.get('type'),
                 'length': length})

            return myl
        if tag == 'id':
            possibleId = self._element.findtext(self._ns + 'guid')
            if not possibleId:
                possibleId = ''.join([self.title, self.link])
            return possibleId
        if tag == 'updated':
            tag = 'lastBuildDate'
        elif tag == 'summary':
            tag = 'description'
        elif tag == 'date':
            tag = 'pubDate'
        return ElementWrapper.__getattr__(self, tag)


class PEAEntryWrapper(ElementWrapper):

    def __getattr__(self, tag):
        if tag == 'link':
            for elem in self._element.findall(self._ns + tag):
                if not elem.get('rel') == 'enclosure':
                    return elem.get('href')

            return ''
        if tag == 'enclosures':
            myl = []
            for elem in self._element.findall(self._ns + 'link'):
                if elem.get('rel') == 'enclosure':
                    length = elem.get('length')
                    if length:
                        length = int(length) / 1048576
                    myl.append({'href': elem.get('href'),
                     'type': elem.get('type'),
                     'length': length})

            return myl
        return ElementWrapper.__getattr__(self, tag)


class RSSWrapper(ElementWrapper):

    def __init__(self, channel, items, ns = ''):
        self._items = items
        ElementWrapper.__init__(self, channel, ns)

    def __iter__(self):
        return iter([ self[i] for i in range(len(self)) ])

    def __len__(self):
        return len(self._items)

    def __getitem__(self, index):
        return RSSEntryWrapper(self._items[index], self._ns)


class RSS1Wrapper(RSSWrapper):

    def __init__(self, feed, ns):
        RSSWrapper.__init__(self, feed.find(ns + 'channel'), feed.findall(ns + 'item'), ns)


class RSS2Wrapper(RSSWrapper):

    def __init__(self, feed, ns):
        channel = feed.find('channel')
        RSSWrapper.__init__(self, channel, channel.findall('item'))


class PEAWrapper(RSSWrapper):

    def __init__(self, feed, ns):
        ns = feed.tag[:feed.tag.index('}') + 1]
        RSSWrapper.__init__(self, feed, feed.findall(ns + 'entry'), ns)

    def __getitem__(self, index):
        return PEAEntryWrapper(self._items[index], self._ns)

    def __getattr__(self, tag):
        if tag == 'description':
            tag = 'subtitle'
        return ElementWrapper.__getattr__(self, tag)


class BaseFeed:
    """Base-class for all Feeds. Initializes needed Elements."""
    try:
        MAX_HISTORY_ELEMENTS = config.plugins.spzsimpleRSS.maxentries.value
    except:
        MAX_HISTORY_ELEMENTS = 25

    def __init__(self, uri, title = '', description = ''):
        self.uri = uri
        self.title = title or uri.encode('UTF-8')
        self.description = description
        self.ultima = ''
        self.fecha = None
        self.history = []

    def __str__(self):
        return '<%s, "%s", "%s", %d items>' % (self.__class__,
         self.title,
         self.description,
         len(self.history))


class UniversalFeed(BaseFeed):
    """Feed which can handle rdf, rss and atom feeds utilizing abstraction wrappers."""

    def __init__(self, uri, autoupdate, nombre = ''):
        BaseFeed.__init__(self, uri, nombre)
        self.autoupdate = autoupdate
        self.last_update = None
        self.last_ids = set()
        self.wrapper = None
        self.ns = ''

    def gotWrapper(self, wrapper):
        updated = wrapper.updated
        if updated and self.last_update == updated:
            return []
        idx = 0
        for item in wrapper:
            enclosures = []
            link = ''
            title = formatea(strip(item.title))
            pondebug(str(title) + '::' + str(item.date))
            if not title:
                continue
            id = item.id
            if not id or id in self.last_ids:
                continue
            link = item.link
            fecha = ''
            try:
                fecha = cogefecha(str(item.date)) + '\n'
            except:
                pondebug('err fecha')

            fechahora = cogefecha(str(item.date), True)
            if fechahora == None:
                try:
                    fechahora = time.strptime('01 01 2000 00:00:00', '%d %m %Y %H:%M:%S')
                except:
                    pass

            for enclosure in item.enclosures:
                enclosures.append(ScanFile(enclosure['href'], mimetype=enclosure['type'], size=enclosure['length'], autodetect=False))

            summary = fecha + strip_readable(item.summary)
            summary = formatea(summary)
            self.history.insert(idx, (title.encode('UTF-8'),
             link.encode('UTF-8'),
             summary.encode('UTF-8'),
             enclosures,
             fechahora))
            self.last_ids.add(id)
            idx += 1

        try:
            self.MAX_HISTORY_ELEMENTS = config.plugins.spzsimpleRSS.maxentries.value
        except:
            self.MAX_HISTORY_ELEMENTS = 26

        del self.history[self.MAX_HISTORY_ELEMENTS:]
        return self.history[:idx]

    def gotFeed(self, feed):
        if self.wrapper is not None:
            wrapper = self.wrapper(feed, self.ns)
        else:
            if feed.tag == 'rss':
                self.wrapper = RSS2Wrapper
            elif feed.tag.startswith(NS_RDF):
                self.ns = NS_RDF
                self.wrapper = RSS1Wrapper
            elif feed.tag.startswith(NS_RSS_09):
                self.ns = NS_RSS_09
                self.wrapper = RSS1Wrapper
            elif feed.tag.startswith(NS_RSS_10):
                self.ns = NS_RSS_10
                self.wrapper = RSS1Wrapper
            elif feed.tag.endswith('feed'):
                self.wrapper = PEAWrapper
            else:
                raise NotImplementedError, 'Unsupported Feed: %s' % feed.tag
            wrapper = self.wrapper(feed, self.ns)
            self.title = strip(wrapper.title).encode('UTF-8')
            self.description = strip_readable(wrapper.description or '').encode('UTF-8')
        return self.gotWrapper(wrapper)
