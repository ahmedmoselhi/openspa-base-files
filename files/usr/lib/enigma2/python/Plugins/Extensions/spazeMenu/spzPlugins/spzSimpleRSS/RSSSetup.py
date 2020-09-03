from . import _
from Screens.Screen import Screen
from Components.config import config, ConfigSubsection, ConfigEnableDisable, ConfigText, getConfigListEntry, ConfigSelection
from Components.ConfigList import ConfigListScreen
from Components.Button import Button
from RSSFeed import UniversalFeed
from Components.ActionMap import ActionMap
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


class RSSFeedEdit(ConfigListScreen, Screen):
    """Edit an RSS-Feed"""
    skin = '\n\t\t<screen name="RSSFeedEdit" position="center,center" size="1100,220" title="%s" >\n\t\t\t<widget name="config" position="10,20" size="1080,75" scrollbarMode="showOnDemand" />\n\t\t\t<ePixmap name="red"    position="0,175"   zPosition="4" size="140,40" pixmap="skin_default/buttons/red.png" transparent="1" alphatest="on" />\n\t\t\t<ePixmap name="green"  position="140,175" zPosition="4" size="140,40" pixmap="skin_default/buttons/green.png" transparent="1" alphatest="on" />\n\t\t\t<widget name="key_red" position="0,175" zPosition="5" size="140,40" valign="center" halign="center" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />\n\t\t\t<widget name="key_green" position="140,175" zPosition="5" size="140,40" valign="center" halign="center" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />\n\t\t\t<widget name="barrapix_arr" position="0,0" zPosition="19" size="20,20" alphatest="blend" transparent="1" />\n\t\t\t<widget name="barrapix_abj" position="0,0" zPosition="19" size="20,20" alphatest="blend" transparent="1" />\t\t\t\n\t\t</screen>' % _('spazeTeam RSS Reader Setup')

    def __init__(self, session, id, nombre = '', url = 'http://', autoup = False):
        Screen.__init__(self, session)
        self.list = [getConfigListEntry(_('Autoupdate'), ConfigEnableDisable(default=autoup)), getConfigListEntry(_('Feed URI'), ConfigText(default=url, fixed_size=False))]
        ConfigListScreen.__init__(self, self.list, session)
        self.onShow.append(self.iniscroll)
        self.iniciadoS = False
        self['barrapix_arr'] = Pixmap()
        self['barrapix_abj'] = Pixmap()
        self['key_red'] = Button(_('Cancel'))
        self['key_green'] = Button(_('OK'))
        self['setupActions'] = ActionMap(['SetupActions'], {'save': self.save,
         'cancel': self.keyCancel}, -1)
        self.id = id

    def iniscroll(self):
        if not self.iniciadoS:
            self.actualizaScrolls()
            self.iniciadoS = True

    def actualizaScrolls(self):
        openspaSB(objectoself=self, nombrelista='config', barra='barrapix', altoitem=25, imagen=True)

    def save(self):
        lista = [(self.id, self['config'].list[1][1].value, self['config'].list[0][1].value)]
        self.close(lista)


class RSSSetup(ConfigListScreen, Screen):
    """Setup for SimpleRSS, quick-edit for Feed-URIs and settings present."""
    skin = '\n\t\t<screen name="RSSSetup" position="center,center" size="1100,600" title="%s" >\n\t\t\t<widget name="config"  position="10,10" size="1080,550" scrollbarMode="showOnDemand" />\n\t\t\t<ePixmap name="red"    position="0,560"   zPosition="4" size="140,40" pixmap="skin_default/buttons/red.png" transparent="1" alphatest="on" />\n\t\t\t<ePixmap name="green"  position="140,560" zPosition="4" size="140,40" pixmap="skin_default/buttons/green.png" transparent="1" alphatest="on" />\n\t\t\t<ePixmap name="yellow" position="280,560" zPosition="4" size="140,40" pixmap="skin_default/buttons/yellow.png" transparent="1" alphatest="on" />\n\t\t\t<ePixmap name="blue"   position="420,560" zPosition="4" size="140,40" pixmap="skin_default/buttons/blue.png" transparent="1" alphatest="on" />\n\t\t\t<widget name="key_red"    position="0,560" zPosition="5" size="140,40" valign="center" halign="center" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />\n\t\t\t<widget name="key_green"  position="140,560" zPosition="5" size="140,40" valign="center" halign="center" font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />\n\t\t\t<widget name="key_yellow" position="280,560" zPosition="5" size="140,40" valign="center" halign="center"  font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />\n\t\t\t<widget name="key_blue"   position="420,560" zPosition="5" size="140,40" valign="center" halign="center"  font="Regular;21" transparent="1" foregroundColor="white" shadowColor="black" shadowOffset="-1,-1" />\n\t\t<widget name="barrapix_arr" position="0,0" zPosition="19" size="20,20" alphatest="blend" transparent="1" />\n\t\t<widget name="barrapix_abj" position="0,0" zPosition="19" size="20,20" alphatest="blend" transparent="1" />\t\t\t\n\t\t</screen>' % _('spazeTeam RSS Reader Setup')

    def __init__(self, session, rssPoller = None):
        Screen.__init__(self, session)
        self.onClose.append(self.abort)
        self.rssPoller = rssPoller
        self.list = []
        config.plugins.spzsimpleRSS.autostart.addNotifier(self.autostartChanged, initial_call=False)
        self.list.append(getConfigListEntry(_('Start automatically with Enigma2'), config.plugins.spzsimpleRSS.autostart))
        self.keep_running = getConfigListEntry(_('Keep running in background'), config.plugins.spzsimpleRSS.keep_running)
        if not config.plugins.spzsimpleRSS.autostart.value:
            self.list.append(self.keep_running)
        self.list.append(getConfigListEntry(_('Show new Messages as'), config.plugins.spzsimpleRSS.update_notification))
        self.list.append(getConfigListEntry(_('Update Interval (min)'), config.plugins.spzsimpleRSS.interval))
        self.list.append(getConfigListEntry(_('Max entries for RSS channel'), config.plugins.spzsimpleRSS.maxentries))
        self.list.append(getConfigListEntry(' ', ConfigSelection(choices=[(' ', '---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------')], default=' ')))
        self.anadelista()
        ConfigListScreen.__init__(self, self.list, session)
        self['key_red'] = Button(_('Cancel'))
        self['key_green'] = Button(_('OK'))
        self['key_yellow'] = Button(_('New'))
        self['key_blue'] = Button(_('Delete'))
        self['setupActions'] = ActionMap(['SetupActions', 'ColorActions', 'EPGSelectActions'], {'blue': self.delete,
         'yellow': self.new,
         'save': self.keySave,
         'cancel': self.keyCancel,
         'info': self.fayuda,
         'ok': self.ok}, -1)
        self.onShow.append(self.iniscroll)
        self.iniciadoS = False
        self['barrapix_arr'] = Pixmap()
        self['barrapix_abj'] = Pixmap()

    def iniscroll(self):
        if not self.iniciadoS:
            self.actualizaScrolls()
            self.iniciadoS = True

    def actualizaScrolls(self):
        openspaSB(objectoself=self, nombrelista='config', barra='barrapix', altoitem=25, imagen=True)

    def fayuda(self):
        from RSSScreen import ayuda
        ayuda(self)

    def anadelista(self):
        list2 = []
        for ele in self.list:
            if ele[0] != _('Feed'):
                list2.append(ele)

        self.list = []
        for ele in list2:
            self.list.append(ele)

        conta = 0
        for feed in self.rssPoller.feeds:
            if feed.title == feed.uri:
                erfeed = ' url=' + feed.uri
            else:
                erfeed = feed.title + ' url=' + feed.uri
            if len(erfeed) > 100:
                erfeed = erfeed[:97] + '...'
            self.list.append(getConfigListEntry(_('Feed'), ConfigSelection(choices=[(str(conta), erfeed)], default=str(conta))))
            conta = conta + 1

        self.actualizaScrolls()

    def autostartChanged(self, instance):
        if instance.value:
            self.list.remove(self.keep_running)
        else:
            self.list.insert(1, self.keep_running)
        self['config'].setList(self.list)
        self.actualizaScrolls()

    def delete(self):
        from Screens.MessageBox import MessageBox
        idx = self['config'].instance.getCurrentIndex()
        if self['config'].list[idx][0] == _('Feed'):
            self.session.openWithCallback(self.deleteConfirm, MessageBox, _('Really delete this entry?\nIt cannot be recovered!'))

    def deleteConfirm(self, result):
        if result:
            idx = self['config'].instance.getCurrentIndex()
            id = int(self['config'].list[idx][1].value)
            self.rssPoller.feeds.remove(self.rssPoller.feeds[id])
            self.anadelista()
            self['config'].setList(self.list)
            self.actualizaScrolls()
            savefilefeeds(self.rssPoller.feeds)

    def ok(self):
        idx = self['config'].instance.getCurrentIndex()
        try:
            id = int(self['config'].list[idx][1].value)
            nombre = self.rssPoller.feeds[id].title
            url = self.rssPoller.feeds[id].uri
            auto = self.rssPoller.feeds[id].autoupdate
            self.session.openWithCallback(self.refresh, RSSFeedEdit, id, nombre, url, auto)
        except:
            pass

    def refresh(self, resplista = None):
        if not resplista == None:
            try:
                id = resplista[0][0]
                url = resplista[0][1]
                auto = resplista[0][2]
                self.rssPoller.feeds[id].uri = url
                self.rssPoller.feeds[id].autoupdate = auto
                self.anadelista()
                self['config'].setList(self.list)
                savefilefeeds(self.rssPoller.feeds)
                self.actualizaScrolls()
            except:
                pass

    def new(self):
        self.session.openWithCallback(self.conditionalNew, RSSFeedEdit, -1)

    def conditionalNew(self, resplista = None):
        if not resplista == None:
            try:
                id = resplista[0][0]
                url = resplista[0][1]
                auto = resplista[0][2]
                self.rssPoller.feeds.append(UniversalFeed(url, auto, ''))
                self.anadelista()
                self['config'].setList(self.list)
                self.actualizaScrolls()
                savefilefeeds(self.rssPoller.feeds)
            except:
                pass

    def keySave(self):
        if self.rssPoller is not None:
            self.rssPoller.triggerReload()
        ConfigListScreen.keySave(self)

    def abort(self):
        print '[spzRSS] Closing Setup Dialog'
        config.plugins.spzsimpleRSS.autostart.notifiers.remove(self.autostartChanged)


def addFeed(address, auto = False, rssf = None):
    if rssf:
        rssf.feeds.append(UniversalFeed(address, auto, ''))
        savefilefeeds(rssf.feeds)
