from . import _
from enigma import eTimer
from Components.config import config
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.ScrollLabel import ScrollLabel
from RSSList import RSSFeedList, RSSEntryList, RSSEntryListNot
from RSSPoller import savefilefeeds
from os import environ
import gettext
from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE, fileExists
from Components.Pixmap import Pixmap
from Plugins.Extensions.spazeMenu.sbar import openspaSB
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


def ayuda(self):
    self.session.open(RSSAyuda)


def archivoayuda():
    ruta = '/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/spzSimpleRSS/help/'
    lang = language.getLanguage()
    lenguaje = str(lang[:2])
    archivo = ruta + 'help_' + lenguaje + '.txt'
    if not fileExists(archivo):
        archivo = ruta + 'help_en.txt'
    return archivo


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


class RSSAyuda(Screen):
    """Shows a RSS Item"""
    skin = '\n\t\t<screen name="RSSAyuda" position="center,center" size="1100,590" title="%s">\n\t\t  <widget name="content" position="10,10" size="1080,580" font="Regular; 22" />\n\t\t<widget name="barrapix_arr" position="10,10" zPosition="19" size="1080,580" alphatest="blend" transparent="1" />\n\t\t<widget name="barrapix_abj" position="0,0" zPosition="19" size="20,20" alphatest="blend" transparent="1" />\t\t  \n\t\t</screen>' % _('Help')

    def __init__(self, session):
        self.session = session
        Screen.__init__(self, session)
        self['content'] = ScrollLabel()
        self['actions'] = ActionMap(['MenuActions',
         'OkCancelActions',
         'EPGSelectActions',
         'ColorActions',
         'DirectionActions'], {'cancel': self.close,
         'ok': self.close,
         'up': self.up,
         'down': self.down,
         'right': self.next,
         'left': self.previous})
        self['barrapix_arr'] = Pixmap()
        self['barrapix_abj'] = Pixmap()
        self.onLayoutFinish.append(self.setConditionalTitle)

    def setConditionalTitle(self):
        self.setTitle(_('Help') + ' spazeTeam RSS')
        erdato = ''
        try:
            booklist = open(archivoayuda(), 'r')
        except:
            pass

        if booklist is not None:
            contenido = booklist.read()
            self['content'].setText(contenido)
        openspaSB(objectoself=self, nombrelista='barrapix', barra='barrapix', altoitem=25, imagen=True)

    def up(self):
        self['content'].pageUp()

    def down(self):
        self['content'].pageDown()

    def next(self):
        self['content'].pageDown()

    def previous(self):
        self['content'].pageUp()


class RSSBaseView(Screen):
    """Base Screen for all Screens used in SimpleRSS"""

    def __init__(self, session, poller, parent = None):
        Screen.__init__(self, session, parent)
        self.rssPoller = poller
        self.pollDialog = None

    def errorPolling(self, errmsg = ''):
        self.session.open(MessageBox, _('Error while parsing Feed, this usually means there is something wrong with it.'), type=MessageBox.TYPE_ERROR, timeout=6)
        if self.pollDialog:
            self.pollDialog.close()
            self.pollDialog = None

    def singleUpdate(self, feedid, errback = None):
        if self.rssPoller is None:
            return
        if errback is None:
            errback = self.errorPolling
        self.rssPoller.singlePoll(feedid, callback=True, errorback=errback)
        self.pollDialog = self.session.open(MessageBox, _("Update is being done in Background.\nContents will automatically be updated when it's done."), type=MessageBox.TYPE_INFO, timeout=8)

    def selectEnclosure(self, enclosures):
        if enclosures is None:
            return
        from Components.Scanner import openList
        if not openList(self.session, enclosures):
            self.session.open(MessageBox, _('Found no Enclosure we can display.'), type=MessageBox.TYPE_INFO, timeout=5)


class RSSEntryView(RSSBaseView):
    """Shows a RSS Item"""
    skin = '\n\t\t<screen name="RSSEntryView" position="center,center" size="1100,593" title="%s">\n\t\t  <eLabel position="0, 5" size="1100, 2" backgroundColor="grey" />\n\t\t  <widget name="info" position="0, 10" size="1100, 20" halign="right" font="Regular; 18" />\n\t\t  <widget name="content" position="0,30" size="1100,530" font="Regular; 22" />\n\t\t  <eLabel position="0,560" size="1100, 2" backgroundColor="grey" />\n\t\t  <ePixmap name="new ePixmap" position="16,564" size="35,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/spzSimpleRSS/res/izq-fs8.png" alphatest="blend" />\n\t\t  <widget name="texto_l" position="52,568" size="154,25" transparent="1" font="Regular; 16" zPosition="1" />\n\t\t  <ePixmap name="new ePixmap" position="216,564" size="35,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/spzSimpleRSS/res/dch-fs8.png" alphatest="blend" />\n\t\t  <widget name="texto_r" position="252,568" size="154,25" transparent="1" font="Regular; 16" zPosition="1" />\n\t\t<widget name="barrapix_arr" position="0,30" zPosition="19" size="1100,530" alphatest="blend" transparent="1" />\n\t\t<widget name="barrapix_abj" position="0,0" zPosition="19" size="20,20" alphatest="blend" transparent="1" />\t\t  \n\t\t</screen>' % _('spazeTeam RSS Reader')

    def __init__(self, session, data, feedTitle = '', cur_idx = None, entries = None, parent = None):
        RSSBaseView.__init__(self, session, None, parent)
        self.data = data
        self.feedTitle = feedTitle
        self.cur_idx = cur_idx
        self.entries = entries
        if cur_idx is not None and entries is not None:
            self['info'] = Label(_('Entry %s/%s') % (cur_idx + 1, entries))
        else:
            self['info'] = Label()
        self['texto_r'] = Label(_('Next entry'))
        self['texto_l'] = Label(_('Previous entry'))
        if data is not None:
            erdato = '\n\n'.join([data[0], data[2], ' '.join([str(len(data[3])), _('Enclosures')])])
            erdato = erdato + '\n\n------------------------------- ' + maqueaurl(data[1]) + ' -------------------------------'
            self['content'] = ScrollLabel(erdato)
        else:
            self['content'] = ScrollLabel()
        self['actions'] = ActionMap(['MenuActions',
         'OkCancelActions',
         'EPGSelectActions',
         'ColorActions',
         'DirectionActions',
         'InfobarChannelSelection'], {'cancel': self.close,
         'ok': self.selectEnclosure,
         'yellow': self.selectEnclosure,
         'up': self.up,
         'down': self.down,
         'zapDown': self.down,
         'zapUp': self.up,
         'right': self.next,
         'left': self.previous,
         'nextBouquet': self.nextFeed,
         'prevBouquet': self.previousFeed})
        self.onLayoutFinish.append(self.setConditionalTitle)
        self['barrapix_arr'] = Pixmap()
        self['barrapix_abj'] = Pixmap()

    def setConditionalTitle(self):
        openspaSB(objectoself=self, nombrelista='barrapix', barra='barrapix', altoitem=25, imagen=True)
        self.setTitle(': '.join([_('spazeTeam RSS Reader'), self.feedTitle]))

    def up(self):
        self['content'].pageUp()

    def down(self):
        self['content'].pageDown()

    def next(self):
        if self.parent is not None:
            self.data, self.cur_idx, self.entries = self.parent.nextEntry()
            self.setContent()

    def previous(self):
        if self.parent is not None:
            self.data, self.cur_idx, self.entries = self.parent.previousEntry()
            self.setContent()

    def nextFeed(self):
        if self.parent is not None:
            try:
                result = self.parent.next()
            except:
                return

            self.feedTitle = result[0]
            self.entries = len(result[1])
            if self.entries:
                self.cur_idx = 0
                self.data = result[1][0]
            else:
                self.cur_idx = None
                self.data = None
            self.setConditionalTitle()
            self.setContent()

    def previousFeed(self):
        if self.parent is not None:
            try:
                result = self.parent.previous()
            except:
                return

            self.feedTitle = result[0]
            self.entries = len(result[1])
            if self.entries:
                self.cur_idx = 0
                self.data = result[1][0]
            else:
                self.cur_idx = None
                self.data = None
            self.setConditionalTitle()
            self.setContent()

    def setContent(self):
        if self.cur_idx is not None and self.entries is not None:
            self['info'].setText(_('Entry %s/%s') % (self.cur_idx + 1, self.entries))
        else:
            self['info'].setText('')
        if self.data is not None:
            erdato = '\n\n'.join([self.data[0], self.data[2], ' '.join([str(len(self.data[3])), _('Enclosures')])])
            erdato = erdato + '\n\n------------------------------- ' + maqueaurl(self.data[1]) + ' -------------------------------'
            self['content'].setText(erdato)
        else:
            self['content'].setText(_('No such Item.'))

    def selectEnclosure(self):
        if self.data is not None:
            RSSBaseView.selectEnclosure(self, self.data[3])


class RSSFeedViewTira(Screen):
    skin = '\n\t\t<screen name="RSSFeedViewTira" position="0,635" size="1281,94" title="spazeTeam RSS" flags="wfNoBorder" backgroundColor="#50000000">\t\t  \n\t\t\t<widget name="content" position="112,3" size="990,48" valign="center" font="Regular; 20" transparent="1" backgroundColor="#000000" foregroundColor="#00ffffff" shadowColor="#000000" shadowOffset="-2,-2"/>\n\t\t\t<widget name="rinfo" position="1135,12" size="136,27" font="Regular; 18" transparent="1" noWrap="1" zPosition="4" backgroundColor="#000000" foregroundColor="#006cbcf0" shadowColor="#000000" shadowOffset="-2,-2"/>\n\t\t\t<eLabel position="103,5" size="2,40" backgroundColor="#20555555" zPosition="2" />\n\t\t\t<eLabel position="1125,5" size="2,40" backgroundColor="#20555555" zPosition="2" />\n\t\t\t<ePixmap name="new ePixmap" position="38,5" size="48,37" zPosition="2" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/spzSimpleRSS/res/rss37-fs8.png" alphatest="blend" />\t\t\n\t\t</screen>'

    def __init__(self, session, feed):
        Screen.__init__(self, session)
        self.feed = feed
        self['content'] = Label()
        self['rinfo'] = Label('RSS')
        self.iniciado = False
        self['actions'] = ActionMap(['DirectionActions', 'MenuActions', 'OkCancelActions'], {'left': self.klef,
         'right': self.krig,
         'up': self.krig,
         'menu': self.cerrar,
         'down': self.klef,
         'ok': self.showCurrentEntry,
         'cancel': self.cerrar}, -2)
        self.timerRoll = eTimer()
        self.timerClose = eTimer()
        self.timerRoll.callback.append(self.timerfeeds)
        self.timerClose.callback.append(self.cerrar)
        self.tamano = 0
        self.afeed = 0
        self.onLayoutFinish.append(self.verfeeds)

    def showCurrentEntry(self):
        try:
            current_entry = self.feed.history[self.afeed]
        except:
            self.cerrar()
            return

        if current_entry is None:
            self.cerrar()
        self.timerClose.stop()
        self.timerRoll.stop()
        self.session.openWithCallback(self.updateInfo, RSSEntryView, current_entry, cur_idx=self.afeed, entries=len(self.feed.history), feedTitle=self.feed.title, parent=self)

    def updateInfo(self, resp = None):
        self.verfeeds()

    def krig(self):
        self.timerRoll.stop()
        self.timerClose.stop()
        self.afeed = self.afeed + 1
        if self.afeed >= len(self.feed.history):
            self.afeed = 0
        self.verfeeds()

    def klef(self):
        self.timerRoll.stop()
        self.timerClose.stop()
        self.afeed = self.afeed - 1
        if self.afeed < 0:
            self.afeed = len(self.feed.history) - 1
        self.verfeeds()

    def nextEntry(self):
        self.afeed = self.afeed + 1
        if self.afeed >= len(self.feed.history):
            self.afeed = 0
        try:
            current_entry = self.feed.history[self.afeed]
            return (current_entry, self.afeed, len(self.feed.history))
        except:
            self.cerrar()

    def previousEntry(self):
        self.afeed = self.afeed - 1
        if self.afeed < 0:
            self.afeed = len(self.feed.history) - 1
        try:
            current_entry = self.feed.history[self.afeed]
            return (current_entry, self.afeed, len(self.feed.history))
        except:
            self.cerrar()

    def timerfeeds(self):
        self.afeed = self.afeed + 1
        if self.afeed >= len(self.feed.history):
            self.timerClose.startLongTimer(6)
        else:
            self.verfeeds()

    def verfeeds(self):
        contenido = ''
        self['rinfo'].setText(' ' + str(self.afeed + 1) + '/' + str(len(self.feed.history)) + '')
        if self.afeed < len(self.feed.history):
            try:
                erfeed = self.feed.history[self.afeed]
            except:
                self.cerrar()
                return

            laurl = maqueaurl(erfeed[1])
            contenido = contenido + erfeed[0] + ' / ' + laurl
            self.timerRoll.startLongTimer(8)
        else:
            try:
                erfeed = self.feed.history[self.afeed]
            except:
                self.cerrar()
                return

            laurl = maqueaurl(erfeed[1])
            contenido = contenido + erfeed[0] + ' / ' + laurl
        self['content'].setText(contenido)

    def cerrar(self):
        self.timerClose.stop()
        self.timerRoll.stop()
        self.close()


class RSSFeedView(RSSBaseView):
    """Shows a RSS-Feed"""
    skin = '\n\t\t<screen position="center,center" size="1150,600" title="%s">\n\t\t  <eLabel position="0, 0" size="1150, 2" backgroundColor="grey" />\n\t\t  <widget name="info" position="0, 0" size="1150, 20" halign="right" font="Regular; 18" />\n\t\t  <widget name="content" position="0, 25" size="1150, 450" scrollbarMode="showOnDemand" />\n\t\t  <widget name="summary" position="10,480" size="1130, 90" font="Regular;19" />\n\t\t  <eLabel position="0, 477" size="1150, 2" backgroundColor="grey" />\n\t\t <ePixmap name="new ePixmap" position="16,575" size="35,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/spzSimpleRSS/res/green.png" alphatest="blend" />\n\t\t  <widget name="texto_g" position="52,578" size="365,26" transparent="1" font="Regular; 16" zPosition="1" noWrap="1" />\n\t\t  <ePixmap name="new ePixmap" position="411,575" size="35,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/spzSimpleRSS/res/menu.png" alphatest="blend" />\n\t\t  <widget name="texto_m" position="447,578" size="250,25" transparent="1" font="Regular; 16" zPosition="1" />\n\t\t<widget name="barrapix_arr" position="0,0" zPosition="19" size="20,20" alphatest="blend" transparent="1" />\n\t\t<widget name="barrapix_abj" position="0,0" zPosition="19" size="20,20" alphatest="blend" transparent="1" />\n\t\t</screen>' % _('spazeTeam RSS Reader')

    def __init__(self, session, feed = None, newItems = False, parent = None, rssPoller = None, id = None):
        RSSBaseView.__init__(self, session, rssPoller, parent)
        self.feed = feed
        self.newItems = newItems
        self.id = id
        if self.feed.title == _('New Items'):
            nuevos = True
        else:
            nuevos = False
        if newItems:
            self['content'] = RSSEntryListNot(self.feed.history)
        else:
            self['content'] = RSSEntryList(self.feed.history, nuevos)
        self['summary'] = Label()
        self['info'] = Label()
        self['texto_g'] = Label(_('Update selected entry'))
        self['texto_m'] = Label(_('Options...'))
        if not newItems:
            self['actions'] = ActionMap(['OkCancelActions',
             'EPGSelectActions',
             'MenuActions',
             'ColorActions'], {'ok': self.showCurrentEntry,
             'cancel': self.close,
             'nextBouquet': self.next,
             'prevBouquet': self.previous,
             'menu': self.menu,
             'green': self.actualiza,
             'yellow': self.selectEnclosure})
            self.onLayoutFinish.append(self.__show)
            self.onClose.append(self.__close)
            self.timer = None
        else:
            self['actions'] = ActionMap(['DirectionActions',
             'MenuActions',
             'OkCancelActions',
             'EPGSelectActions'], {'ok': self.mostrar,
             'cancel': self.close,
             'left': self.klef,
             'right': self.krig,
             'up': self.kup,
             'info': self.fayuda,
             'down': self.kdow}, -2)
            self.timer = eTimer()
            self.timer.callback.append(self.timerTick)
            self.onExecBegin.append(self.startTimer)
            self.timer2 = eTimer()
            self.timer2.callback.append(self.iniciaf)
        self['content'].connectSelChanged(self.updateInfo)
        self.onLayoutFinish.extend([self.updateInfo, self.setConditionalTitle])
        self.onShow.append(self.iniscroll)
        self.iniciadoS = False
        self['barrapix_arr'] = Pixmap()
        self['barrapix_abj'] = Pixmap()

    def iniscroll(self):
        if not self.iniciadoS:
            self.actualizaScrolls()
            self.iniciadoS = True

    def actualizaScrolls(self):
        openspaSB(objectoself=self, nombrelista='content', barra='barrapix', altoitem=50, imagen=True)

    def fayuda(self):
        ayuda(self)

    def krig(self):
        self.timer.stop()
        self['content'].pageDown()

    def klef(self):
        self.timer.stop()
        self['content'].pageUp()

    def kup(self):
        self.timer.stop()
        self['content'].up()

    def kdow(self):
        self.timer.stop()
        self['content'].down()

    def mostrar(self):
        self.timer.stop()
        self.showCurrentEntry()

    def iniciaf(self):
        from Screens.InfoBar import InfoBar
        if InfoBar and InfoBar.instance:
            from plugin import main2
            main(self.session)

    def startTimer(self):
        self.timer.startLongTimer(15)

    def timerTick(self):
        self.timer.callback.remove(self.timerTick)
        self.close()

    def __show(self):
        self.rssPoller.addCallback(self.pollCallback)

    def __close(self):
        if self.timer is not None:
            self.timer.callback.remove(self.timerTick)
            self.timer = None
        self.rssPoller.removeCallback(self.pollCallback)

    def pollCallback(self, id = None):
        print '[spzRSS] SimpleRSSFeed called back'
        if id is None or id + 1 == self.id:
            current_entry = self['content'].getCurrent()
            self['content'].moveToEntry(current_entry)
            self['content'].invalidate()
            self.setConditionalTitle()
            self.updateInfo()

    def setConditionalTitle(self):
        self.setTitle(': '.join([_('spazeTeam RSS Reader'), self.feed.title]))

    def updateInfo(self):
        current_entry = self['content'].getCurrent()
        if current_entry:
            self['summary'].setText(current_entry[2])
            cur_idx = self['content'].getSelectedIndex()
            self['info'].setText(_('Entry %s/%s') % (cur_idx + 1, len(self.feed.history)))
        else:
            self['summary'].setText(_('Feed is empty.'))
            self['info'].setText('')

    def menu(self):
        from Screens.ChoiceBox import ChoiceBox
        possible_actions = [(_('Update Feed'), 'update'), (_('Help'), 'help'), (_('Close'), 'close')]
        self.session.openWithCallback(self.cbmenu, ChoiceBox, _('What to do?'), possible_actions)

    def cbmenu(self, result):
        if result:
            if result[1] == 'update':
                if self.id > 0:
                    self.singleUpdate(self.id - 1)
            elif result[1] == 'help':
                ayuda(self)

    def actualiza(self):
        if self.id > 0:
            self.singleUpdate(self.id - 1)

    def nextEntry(self):
        self['content'].down()
        return (self['content'].getCurrent(), self['content'].getSelectedIndex(), len(self.feed.history))

    def previousEntry(self):
        self['content'].up()
        return (self['content'].getCurrent(), self['content'].getSelectedIndex(), len(self.feed.history))

    def next(self):
        if self.parent is not None:
            self.feed, self.id = self.parent.nextFeed()
            self['content'].setList(self.feed.history)
            self['content'].moveToIndex(0)
            self.updateInfo()
            self.setConditionalTitle()
            return (self.feed.title, self.feed.history, self.id)
        return (self.feed.title, self.feed.history, self.id)

    def previous(self):
        if self.parent is not None:
            self.feed, self.id = self.parent.previousFeed()
            self['content'].setList(self.feed.history)
            self['content'].moveToIndex(0)
            self.updateInfo()
            self.setConditionalTitle()
            return (self.feed.title, self.feed.history, self.id)
        return (self.feed.title, self.feed.history, self.id)

    def checkEmpty(self):
        if self.id > 0 and not len(self.feed.history):
            self.singleUpdate(self.id - 1)

    def showCurrentEntry(self):
        current_entry = self['content'].getCurrent()
        if current_entry is None:
            return
        self.session.openWithCallback(self.updateInfo, RSSEntryView, current_entry, cur_idx=self['content'].getSelectedIndex(), entries=len(self.feed.history), feedTitle=self.feed.title, parent=self)

    def selectEnclosure(self):
        current_entry = self['content'].getCurrent()
        if current_entry is None:
            return
        RSSBaseView.selectEnclosure(self, current_entry[3])


class RSSFeedViewNot(RSSFeedView, RSSBaseView):
    skin = '\n<screen position="50,50" size="700, 425" title="%s">\n  <eLabel position="0, 0" size="700, 2" backgroundColor="grey" />\n  <widget name="info" position="0, 0" size="700, 20" halign="right" font="Regular; 18" />\n  <widget name="content" position="0, 25" size="700, 300" scrollbarMode="showOnDemand" />\n  <widget name="summary" position="10, 330" size="680, 98" font="Regular;19" />\n  <eLabel position="0, 325" size="700, 1" backgroundColor="grey" />\n  <widget name="texto_g" position="52,617" size="365,26" transparent="1" font="Regular; 16" zPosition="1" noWrap="1" />\n  <widget name="texto_m" position="447,618" size="250,25" transparent="1" font="Regular; 16" zPosition="1" />\n\t\t<widget name="barrapix_arr" position="0,0" zPosition="19" size="20,20" alphatest="blend" transparent="1" />\n\t\t<widget name="barrapix_abj" position="0,0" zPosition="19" size="20,20" alphatest="blend" transparent="1" />  \n</screen>' % _('spazeTeam RSS Reader New Items')

    def __init__(self, session, feed = None, newItems = False, parent = None, rssPoller = None, id = None):
        RSSFeedView.__init__(self, session, feed, newItems, parent, rssPoller, id)


class RSSOverview(RSSBaseView):
    """Shows an Overview over all RSS-Feeds known to rssPoller"""
    skin = '\n\t\t<screen name="RSSOverview" position="center,center" size="900, 600" title="%s">\n\t\t\t<eLabel position="0, 0" size="900, 2" backgroundColor="grey" />\n\t\t\t<widget name="info" position="0, 0" size="900, 20" halign="right" font="Regular; 18" />\n\t\t\t<eLabel position="0, 95" size="850, 1" backgroundColor="grey" />\n\t\t\t<eLabel position="0, 165" size="850, 1" backgroundColor="grey" />\n\t\t\t<eLabel position="0, 235" size="850, 1" backgroundColor="grey" />\n\t\t\t<eLabel position="0, 305" size="850, 1" backgroundColor="grey" />\n\t\t\t<eLabel position="0, 375" size="850, 1" backgroundColor="grey" />\n\t\t\t<eLabel position="0, 445" size="850, 1" backgroundColor="grey" />\n\t\t\t\n\t\t\t<widget name="content" position="0, 25" size="900,490" scrollbarMode="showOnDemand" />\n\t\t\t<widget name="summary" position="0,520" size="900, 50" font="Regular;19" />\n\t\t\t<eLabel position="0,515" size="900, 2" backgroundColor="grey" />\n\t\t  <ePixmap name="new ePixmap" position="16,575" size="35,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/spzSimpleRSS/res/green.png" alphatest="blend" />\n\t\t  <widget name="texto_g" position="52,578" size="365,26" transparent="1" font="Regular; 16" zPosition="1" noWrap="1" />\n\t\t  <ePixmap name="new ePixmap" position="411,575" size="35,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/spzSimpleRSS/res/menu.png" alphatest="blend" />\n\t\t  <widget name="texto_m" position="447,578" size="245,25" transparent="1" font="Regular; 16" zPosition="1" />\n\t\t<widget name="barrapix_arr" position="0,0" zPosition="19" size="20,20" alphatest="blend" transparent="1" />\n\t\t<widget name="barrapix_abj" position="0,0" zPosition="19" size="20,20" alphatest="blend" transparent="1" />\n\t\t  </screen>' % _('spazeTeam RSS Reader')

    def __init__(self, session, poller):
        RSSBaseView.__init__(self, session, poller)
        self['actions'] = ActionMap(['OkCancelActions',
         'MenuActions',
         'ColorActions',
         'EPGSelectActions'], {'ok': self.showCurrentEntry,
         'cancel': self.cerrar,
         'menu': self.menu,
         'yellow': self.selectEnclosure,
         'info': self.fayuda,
         'green': self.actualiza})
        self.fillFeeds()
        self['content'] = RSSFeedList(self.feeds)
        self['summary'] = Label(_('Move to RSS channels. If autodownload is enabled, feeds download automatically, if manual press [OK] for download.'))
        self['info'] = Label(_('Feed %s/%s') % (1, len(self.feeds)))
        self['texto_g'] = Label(_('Update selected entry'))
        self['texto_m'] = Label(_('Options...'))
        self['content'].connectSelChanged(self.updateInfo)
        self.onLayoutFinish.append(self.__show)
        self.onClose.append(self.__close)
        self.onShow.append(self.iniscroll)
        self.iniciadoS = False
        self['barrapix_arr'] = Pixmap()
        self['barrapix_abj'] = Pixmap()

    def iniscroll(self):
        if not self.iniciadoS:
            self.actualizaScrolls()
            self.iniciadoS = True

    def actualizaScrolls(self):
        openspaSB(objectoself=self, nombrelista='content', barra='barrapix', altoitem=70, imagen=True)

    def fayuda(self):
        ayuda(self)

    def actualiza(self):
        cur_idx = self['content'].getSelectedIndex()
        if cur_idx > 0:
            self.singleUpdate(cur_idx - 1)

    def __show(self):
        self.rssPoller.addCallback(self.pollCallback)

    def __close(self):
        self.rssPoller.removeCallback(self.pollCallback)

    def cerrar(self):
        savefilefeeds(self.rssPoller.feeds)
        if not config.plugins.spzsimpleRSS.autostart.value and not config.plugins.spzsimpleRSS.keep_running.value:
            self.session.openWithCallback(self.cerrarcb, MessageBox, _('Do you want keep runngin in background for new items notification?'), default=False)
        else:
            self.close(False)

    def cerrarcb(self, respuesta):
        if respuesta:
            self.close(False)
        else:
            self.close(True)

    def fillFeeds(self):
        self.feeds = [(self.rssPoller.newItemFeed,)]
        self.feeds.extend([ (feed,) for feed in self.rssPoller.feeds ])

    def pollCallback(self, id = None):
        print '[spzRSS] SimpleRSS called back'
        self.updateInfo()
        self['content'].invalidate()

    def updateInfo(self):
        current_entry = self['content'].getCurrent()
        textoinfo = ' '.join([str(len(current_entry.history)), _('Entries')])
        cur_idx = self['content'].getSelectedIndex()
        if cur_idx == 0:
            textoinfo = textoinfo + ' :: ' + _('Show the new items since last update')
        elif self.rssPoller.feeds[cur_idx - 1].autoupdate:
            siauto = _('AutoDownload enabled')
            if len(current_entry.history) == 0:
                textoinfo = textoinfo + ' :: ' + siauto + ' :: ' + _('Wait for download feeds...')
            else:
                textoinfo = textoinfo + ' :: ' + _('Press [GREEN] for update feeds...')
        else:
            siauto = _('AutoDownload is disabled')
            if len(current_entry.history) == 0:
                textoinfo = textoinfo + ' :: ' + siauto + ' :: ' + _('Press [OK] or [GREEN] for download feeds...')
            else:
                textoinfo = textoinfo + ' :: ' + _('Press [GREEN] for update feeds...')
        self['summary'].setText(textoinfo)
        self['info'].setText(_('Feed %s/%s') % (self['content'].getSelectedIndex() + 1, len(self.feeds)))

    def menu(self):
        from Screens.ChoiceBox import ChoiceBox
        cur_idx = self['content'].getSelectedIndex()
        if cur_idx > 0:
            possible_actions = [(_('Update Feed'), 'update'),
             (_('Setup'), 'setup'),
             (_('Help'), 'help'),
             (_('Close'), 'close')]
        else:
            possible_actions = [(_('Setup'), 'setup'), (_('Help'), 'help'), (_('Close'), 'close')]
        self.session.openWithCallback(self.menuChoice, ChoiceBox, _('What to do?'), possible_actions)

    def menuChoice(self, result):
        if result:
            if result[1] == 'update':
                cur_idx = self['content'].getSelectedIndex()
                if cur_idx > 0:
                    self.singleUpdate(cur_idx - 1)
            elif result[1] == 'setup':
                from RSSSetup import RSSSetup
                self.session.openWithCallback(self.refresh, RSSSetup, rssPoller=self.rssPoller)
            elif result[1] == 'close':
                self.close()
            elif result[1] == 'help':
                ayuda(self)

    def refresh(self, resp = None):
        current_entry = self['content'].getCurrent()
        self.fillFeeds()
        self['content'].setList(self.feeds)
        self['content'].moveToEntry(current_entry)
        self.updateInfo()

    def nextFeed(self):
        self['content'].up()
        return (self['content'].getCurrent(), self['content'].getSelectedIndex())

    def previousFeed(self):
        self['content'].down()
        return (self['content'].getCurrent(), self['content'].getSelectedIndex())

    def showCurrentEntry(self):
        current_entry = self['content'].getCurrent()
        cur_idx = self['content'].getSelectedIndex()
        if len(current_entry.history) > 0 or cur_idx == 0:
            self.session.openWithCallback(self.updateInfo, RSSFeedView, feed=current_entry, parent=self, rssPoller=self.rssPoller, id=cur_idx)
        elif cur_idx > 0:
            self.singleUpdate(cur_idx - 1)

    def selectEnclosure(self):
        enclosures = []
        for entry in self['content'].getCurrent().history:
            enclosures.extend(entry[3])

        RSSBaseView.selectEnclosure(self, enclosures)
