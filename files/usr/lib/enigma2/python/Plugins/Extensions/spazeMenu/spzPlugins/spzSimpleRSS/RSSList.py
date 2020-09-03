from Components.MenuList import MenuList
from Components.MultiContent import MultiContentEntryText
from Tools.LoadPixmap import LoadPixmap
from enigma import eListboxPythonMultiContent, gFont, RT_HALIGN_LEFT, RT_HALIGN_RIGHT, RT_WRAP, RT_VALIGN_CENTER
from os import environ
import gettext
from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE, fileExists
lang = language.getLanguage()
environ['LANGUAGE'] = lang[:2]
lenguaje = str(lang[:2])
gettext.bindtextdomain('enigma2', resolveFilename(SCOPE_LANGUAGE))
gettext.textdomain('enigma2')
gettext.bindtextdomain('spzSimpleRSS', '%s%s' % (resolveFilename(SCOPE_PLUGINS), 'Extensions/spazeMenu/spzPlugins/spzSimpleRSS/locale/'))

def _(txt):
    t = gettext.dgettext('spzSimpleRSS', txt)
    if t == txt:
        t = gettext.gettext(txt)
    return t


def maqueaurl(urlini):
    lacual = urlini
    try:
        lacual = lacual.replace('http://', '')
        lacual = lacual.replace('https://', '')
        lacual = lacual.replace('www.', '')
        if '/' in lacual:
            lacual = lacual.split('/')[0]
        if '?' in lacual:
            lacual = lacual.split('?')[0]
        return lacual
    except:
        return urlini


class RSSBaseList(MenuList):
    """Base List Component for RSSFeeds."""

    def __init__(self, entries, itemheight):
        MenuList.__init__(self, entries, False, content=eListboxPythonMultiContent)
        self.l.setFont(0, gFont('Regular', 22))
        self.l.setFont(1, gFont('Regular', 18))
        self.l.setFont(2, gFont('Regular', 17))
        self.l.setFont(3, gFont('Regular', 20))
        self.l.setItemHeight(itemheight)

    def connectSelChanged(self, fnc):
        if fnc not in self.onSelectionChanged:
            self.onSelectionChanged.append(fnc)

    def disconnectSelChanged(self, fnc):
        if fnc in self.onSelectionChanged:
            self.onSelectionChanged.remove(fnc)

    def moveToEntry(self, identifier):
        pass

    def invalidate(self):
        self.l.invalidate()


class RSSFeedList(RSSBaseList):

    def __init__(self, entries):
        RSSBaseList.__init__(self, entries, 70)
        self.l.setBuildFunc(self.buildListboxEntry)

    def moveToEntry(self, feed):
        if feed is None:
            return
        idx = 0
        for x in self.list:
            if feed.uri == x[0].uri:
                self.instance.moveSelectionTo(idx)
                break
            idx += 1

    def buildListboxEntry(self, feed):
        res = [None]
        width = self.l.getItemSize().width()
        if feed.title == feed.description:
            res.append(MultiContentEntryText(pos=(70, 20), size=(width, 75), font=0, flags=RT_HALIGN_LEFT, text=feed.title))
            res.append(MultiContentEntryText(pos=(80, 50), size=(width, 20), font=1, flags=RT_HALIGN_LEFT, text=''))
        else:
            res.append(MultiContentEntryText(pos=(70, 10), size=(width, 75), font=0, flags=RT_HALIGN_LEFT, text=feed.title))
            if feed.title == _('New Items'):
                descri = feed.description
                if not feed.ultima == '':
                    descri = descri + ' (' + feed.ultima + ')'
                res.append(MultiContentEntryText(pos=(80, 40), size=(width, 20), font=1, flags=RT_HALIGN_LEFT, text=descri))
            else:
                res.append(MultiContentEntryText(pos=(80, 40), size=(width, 20), font=1, flags=RT_HALIGN_LEFT, text=feed.description))
        try:
            if feed.title == _('New Items'):
                xtexto = '' + str(len(feed.history)) + ' ' + _('Entries') + ''
            elif len(feed.history) == 0 and feed.autoupdate:
                xtexto = '' + _('AutoDownload') + ''
            elif len(feed.history) == 0 and not feed.autoupdate:
                xtexto = '' + _('ManualDownload') + ''
            else:
                xtexto = '' + str(len(feed.history)) + ' ' + _('Entries') + ''
                if feed.autoupdate:
                    xtexto = xtexto + '-' + _('Auto') + ''
            xtexto = '(' + xtexto + ')'
            res.append(MultiContentEntryText(pos=(650, 45), size=(200, 20), font=1, flags=RT_HALIGN_RIGHT, text=xtexto))
        except:
            pass

        if len(feed.history) <= 0 or feed.history == None:
            laimagen = '/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/spzSimpleRSS/res/ng64-fs8.png'
        elif feed.title == _('New Items'):
            laimagen = '/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/spzSimpleRSS/res/nr64-fs8.png'
        elif len(feed.history) > 0:
            laimagen = '/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/spzSimpleRSS/res/nn64-fs8.png'
        else:
            laimagen = '/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/spzSimpleRSS/res/ng64-fs8.png'
        png = LoadPixmap(laimagen)
        res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND,
         0,
         1,
         96,
         96,
         png))
        return res

    def getCurrent(self):
        return self.l.getCurrentSelection()[0]


class RSSEntryList(RSSBaseList):

    def __init__(self, entries, sinuevos = False):
        RSSBaseList.__init__(self, entries, 50)
        self.nuevos = sinuevos
        self.l.setBuildFunc(self.buildListboxEntry)

    def moveToEntry(self, entry):
        if entry is None:
            return
        idx = 0
        for x in self.list:
            if entry[0] == x[0]:
                self.instance.moveSelectionTo(idx)
                break
            idx += 1

    def buildListboxEntry(self, title, link, summary, enclosures, fecha):
        res = [None]
        width = self.l.getItemSize().width()
        sizo = width
        tam = 0
        if self.nuevos:
            tam = 3
            sizo = 840
        res.append(MultiContentEntryText(pos=(52, 0), size=(sizo, 50), font=tam, flags=RT_HALIGN_LEFT | RT_WRAP | RT_VALIGN_CENTER, text=title))
        if self.nuevos:
            erlink = maqueaurl(link)
            if len(erlink) > 28:
                erlink = erlink[:25] + '...'
            titulo = '| ' + erlink
            res.append(MultiContentEntryText(pos=(835, 0), size=(285, 50), font=2, flags=RT_HALIGN_RIGHT | RT_VALIGN_CENTER, text=titulo))
        laimagen = '/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/spzSimpleRSS/res/rss48-fs8.png'
        png = LoadPixmap(laimagen)
        res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND,
         0,
         1,
         48,
         48,
         png))
        return res


class RSSEntryListNot(RSSBaseList):

    def __init__(self, entries):
        RSSBaseList.__init__(self, entries, 50)
        self.l.setBuildFunc(self.buildListboxEntry)

    def moveToEntry(self, entry):
        if entry is None:
            return
        idx = 0
        for x in self.list:
            if entry[0] == x[0]:
                self.instance.moveSelectionTo(idx)
                break
            idx += 1

    def buildListboxEntry(self, title, link, summary, enclosures, fecha):
        res = [None]
        width = self.l.getItemSize().width()
        res.append(MultiContentEntryText(pos=(52, 0), size=(width, 50), font=1, flags=RT_HALIGN_LEFT | RT_WRAP | RT_VALIGN_CENTER, text=title))
        laimagen = '/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/spzSimpleRSS/res/rss48-fs8.png'
        png = LoadPixmap(laimagen)
        res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND,
         0,
         1,
         48,
         48,
         png))
        return res
