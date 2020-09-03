from . import _
from Components.config import config
from enigma import eTimer
from RSSFeed import BaseFeed, UniversalFeed
from twisted.web.client import getPage
from xml.etree.cElementTree import fromstring as cElementTree_fromstring
from Tools.Directories import fileExists
import time
from os import environ
import gettext
from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE, fileExists
from RSSFeed import formateafecha
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


NOTIFICATIONID = 'spzSimpleRSSUpdateNotification'

def pondebug(loque, crear = False):
    pass


def devStrTm(cadena, inicio, fin):
    try:
        if inicio not in cadena:
            return ''
        str = cadena.split(inicio)[1]
        if not fin == '':
            str = str.split(fin)[0]
        return str
    except:
        return ''


def savefilefeeds(lista):
    try:
        booklist = open('/etc/tuxbox/spzRSS.conf', 'w')
    except:
        pass

    if booklist is not None:
        for elemento in lista:
            nombre = elemento.title
            autou = elemento.autoupdate
            url = elemento.uri
            hayotro = False
            if len(nombre) > 0 and nombre != url:
                nombre = '[spzTITLE]=' + nombre
                hayotro = True
            else:
                nombre = ''
            cautou = ''
            if autou:
                cautou = '[spzAUTOUPDATE]=1'
                hayotro = True
            if hayotro:
                url = '[spzURL]=' + url
            booklist.write(nombre + cautou + url + '\n')

        booklist.close()


def getfilefeeds():
    list = []
    booklist = None
    if not fileExists('/etc/tuxbox/spzRSS.conf'):
        import os
        os.system('cp /usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/spzSimpleRSS/conf/spzRSS.conf /etc/tuxbox/spzRSS.conf')
    try:
        booklist = open('/etc/tuxbox/spzRSS.conf', 'r')
    except:
        pass

    if booklist is not None:
        for oneline in booklist:
            cadena = oneline.replace('\n', '')
            nombre = devStrTm(cadena, '[spzTITLE]=', '[')
            cautoup = devStrTm(cadena, '[spzAUTOUPDATE]=', '[')
            if cautoup == '1':
                autoup = True
            else:
                autoup = False
            laurl = devStrTm(cadena, '[spzURL]=', '')
            if laurl == '':
                laurl = devStrTm(cadena, 'http', '')
                if not laurl == '':
                    laurl = 'http' + laurl
            if not laurl == '':
                list.append((laurl, autoup, nombre))

        booklist.close()
    pondebug('lista:' + str(list))
    return list


class RSSPoller:
    """Keeps all Feed and takes care of (automatic) updates"""

    def __init__(self, session, poll = True, nocargar = False):
        self.activo = False
        self.poll_timer = eTimer()
        self.poll_timer.callback.append(self.poll)
        self.ultima = ''
        if nocargar:
            self.poll_timer.startLongTimer(300)
        elif poll:
            self.poll_timer.start(0, 1)
        self.numfeeds = 0
        self.update_callbacks = []
        self.session = session
        self.reloading = False
        self.newItemFeed = BaseFeed('', _('New Items'), _('New Items since last Auto-Update'))
        losfeeds = getfilefeeds()
        self.numfeeds = len(losfeeds)
        pondebug('n feeds:' + str(losfeeds))
        if len(losfeeds) > 0:
            self.feeds = [ UniversalFeed(losfeeds[i][0], losfeeds[i][1], losfeeds[i][2]) for i in range(0, len(losfeeds)) ]
        else:
            self.feeds = [UniversalFeed('', False, '')]
        self.current_feed = 0

    def limpiapopup(self):
        from Tools.Notifications import AddNotificationWithID, RemovePopup
        try:
            RemovePopup(NOTIFICATIONID)
        except:
            pass

    def addCallback(self, callback):
        if callback not in self.update_callbacks:
            self.update_callbacks.append(callback)

    def removeCallback(self, callback):
        if callback in self.update_callbacks:
            self.update_callbacks.remove(callback)

    def doCallback(self, id = None):
        for callback in self.update_callbacks:
            try:
                callback(id)
            except:
                pass

    def error(self, error = ''):
        print '[spzRSS] failed to fetch feed:', error
        self.next_feed()

    def _gotPage(self, data, id = None, callback = False, errorback = None):
        try:
            self.gotPage(data, id)
            if callback:
                self.doCallback(id)
        except NotImplementedError as errmsg:
            if id is not None:
                from Screens.MessageBox import MessageBox
                self.session.open(MessageBox, _('Sorry, this type of feed is unsupported:\n%s') % str(errmsg), type=MessageBox.TYPE_INFO, timeout=5)
        except:
            import traceback, sys
            traceback.print_exc(file=sys.stdout)
            if errorback is not None:
                errorback()
                return
            self.next_feed()

    def gotPage(self, data, id = None):
        feed = cElementTree_fromstring(data)
        if id is not None:
            self.feeds[id].gotFeed(feed)
            print '[spzRSS] single feed parsed...'
            return
        new_items = self.feeds[self.current_feed].gotFeed(feed)
        print '[spzRSS] feed parsed...'
        if new_items is not None:
            self.newItemFeed.history.extend(new_items)
        self.newItemFeed.ultima = formateafecha(None, corta=True)
        self.next_feed()

    def singlePoll(self, id, callback = False, errorback = None):
        getPage(self.feeds[id].uri).addCallback(self._gotPage, id, callback, errorback).addErrback(errorback)

    def poll(self):
        if self.reloading:
            print '[spzRSS] timer triggered while reloading, rescheduling'
            self.poll_timer.start(10000, 1)
        elif len(self.feeds) <= self.current_feed:
            if len(self.newItemFeed.history):
                ok = None
                print '[spzRSS] got new items, calling back'
                self.doCallback()
                try:
                    self.newItemFeed.history.sort(key=lambda x: x[4])
                    self.newItemFeed.history.reverse()
                except:
                    pass

                del self.newItemFeed.history[config.plugins.spzsimpleRSS.maxentries.value * 4:]
                try:
                    hoy = time.localtime()
                    shoy = time.mktime(hoy)
                    shoy = shoy - 86400
                    for nele in range(0, len(self.newItemFeed.history)):
                        ele = self.newItemFeed.history[nele]
                        fechaele = time.mktime(ele[4])
                        if fechaele < shoy:
                            del self.newItemFeed.history[nele:]
                            break

                except:
                    pass

                if not self.activo:
                    if config.plugins.spzsimpleRSS.update_notification.value == 'preview':
                        from RSSScreens import RSSFeedViewNot
                        from Tools.Notifications import AddNotificationWithID, RemovePopup
                        RemovePopup(NOTIFICATIONID)
                        AddNotificationWithID(NOTIFICATIONID, RSSFeedViewNot, self.newItemFeed, newItems=True)
                    elif config.plugins.spzsimpleRSS.update_notification.value == 'tira':
                        from RSSScreens import RSSFeedViewTira
                        from Tools.Notifications import AddNotificationWithID, RemovePopup
                        RemovePopup(NOTIFICATIONID)
                        AddNotificationWithID(NOTIFICATIONID, RSSFeedViewTira, self.newItemFeed)
                    elif config.plugins.spzsimpleRSS.update_notification.value == 'notification':
                        from Tools.Notifications import AddPopup
                        from Screens.MessageBox import MessageBox
                        AddPopup(_('Received %d new news item(s).') % len(self.newItemFeed.history), MessageBox.TYPE_INFO, 5, NOTIFICATIONID)
            else:
                print '[spzRSS] no new items'
            self.current_feed = 0
            self.poll_timer.startLongTimer(config.plugins.spzsimpleRSS.interval.value * 60)
        else:
            clearHistory = self.current_feed == 0
            if config.plugins.spzsimpleRSS.update_notification.value != 'none':
                from Tools.Notifications import current_notifications, notifications
                for x in current_notifications:
                    if x[0] == NOTIFICATIONID:
                        print '[spzRSS] timer triggered while preview on screen, rescheduling'
                        self.poll_timer.start(10000, 1)
                        return

                if clearHistory:
                    for x in notifications:
                        if x[4] and x[4] == NOTIFICATIONID:
                            print '[spzRSS] wont wipe history because it was never read'
                            clearHistory = False
                            break

            if clearHistory:
                del self.newItemFeed.history[:]
            feed = self.feeds[self.current_feed]
            if feed.autoupdate:
                getPage(feed.uri).addCallback(self._gotPage).addErrback(self.error)
            else:
                print '[spzRSS] passing feed'
                self.next_feed()

    def next_feed(self):
        self.current_feed += 1
        self.poll_timer.start(1000, 1)

    def shutdown(self):
        self.poll_timer.callback.remove(self.poll)
        self.poll_timer = None

    def triggerReload(self):
        return
        self.reloading = True
        losfeeds = getfilefeeds()
        self.numfeeds = len(losfeeds)
        if len(losfeeds) > 0:
            self.feeds = [ UniversalFeed(losfeeds[i][0], losfeeds[i][1], losfeeds[i][2]) for i in range(0, len(losfeeds)) ]
        else:
            self.feeds = [UniversalFeed('', False, 'No Feeds Found')]
        self.reloading = False
