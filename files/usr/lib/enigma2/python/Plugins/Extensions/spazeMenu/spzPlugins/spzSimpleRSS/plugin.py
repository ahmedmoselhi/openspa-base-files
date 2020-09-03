from Components.config import config, ConfigSubsection, ConfigSubList, ConfigEnableDisable, ConfigNumber, ConfigText, ConfigSelection, ConfigInteger
from RSSPoller import pondebug
from os import environ
import gettext
from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE, fileExists
from enigma import eTimer
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


config.plugins.spzsimpleRSS = ConfigSubsection()
config.plugins.spzsimpleRSS.update_notification = ConfigSelection(choices=[('tira', _('Scrolling text')),
 ('notification', _('Notification')),
 ('preview', _('Preview')),
 ('none', _('none'))], default='tira')
config.plugins.spzsimpleRSS.interval = ConfigNumber(default=30)
config.plugins.spzsimpleRSS.autostart = ConfigEnableDisable(default=False)
config.plugins.spzsimpleRSS.keep_running = ConfigEnableDisable(default=False)
config.plugins.spzsimpleRSS.maxentries = ConfigInteger(default=25, limits=(10, 100))
rssPoller = None

def main3():
    from Screens.InfoBar import InfoBar
    if InfoBar and InfoBar.instance:
        main(InfoBar.instance.session)


def main2(session):
    timer2 = eTimer()
    timer2.callback.append(main3)
    timer2.startLongTimer(4)


def main(session, **kwargs):
    global rssPoller
    if rssPoller is None:
        from RSSPoller import RSSPoller
        rssPoller = RSSPoller(session)
    else:
        rssPoller.poll_timer.stop()
        rssPoller.poll_timer.start(0, 1)
    rssPoller.activo = True
    rssPoller.limpiapopup()
    from RSSScreens import RSSOverview
    session.openWithCallback(closed, RSSOverview, rssPoller)


def closed(sicerrar = False):
    global rssPoller
    rssPoller.limpiapopup()
    rssPoller.activo = False
    if not config.plugins.spzsimpleRSS.autostart.value and not config.plugins.spzsimpleRSS.keep_running.value:
        if sicerrar:
            rssPoller.shutdown()
            rssPoller = None


def autostart(reason, **kwargs):
    global rssPoller
    pondebug('autostart', True)
    if config.plugins.spzsimpleRSS.autostart.value and kwargs.has_key('session') and reason == 0:
        from RSSPoller import RSSPoller
        rssPoller = RSSPoller(kwargs['session'], nocargar=True)
    elif reason == 1:
        if rssPoller is not None:
            rssPoller.shutdown()
            rssPoller = None


def filescan_open(item, session, **kwargs):
    from RSSSetup import addFeed
    for each in item:
        addFeed(each, False, rssPoller)

    from Screens.MessageBox import MessageBox
    session.open(MessageBox, _('%d Feed(s) were added to configuration.') % len(item), type=MessageBox.TYPE_INFO, timeout=5)


def filescan(**kwargs):
    from Components.Scanner import Scanner, ScanPath

    class RemoteScanner(Scanner):

        def checkFile(self, file):
            return file.path.startswith(('http://', 'https://'))

    return [RemoteScanner(mimetypes=['application/rss+xml', 'application/atom+xml'], paths_to_scan=[ScanPath(path='', with_subdirs=False)], name=_('RSS-Reader'), description='Subscribe Newsfeed...', openfnc=filescan_open)]


def Plugins(**kwargs):
    from Plugins.Plugin import PluginDescriptor
    return [PluginDescriptor(name='spazeTeam ' + _('RSS Reader'), description=_('A simple to use RSS reader'), icon='rss.png', where=PluginDescriptor.WHERE_PLUGINMENU, fnc=main), PluginDescriptor(where=[PluginDescriptor.WHERE_SESSIONSTART, PluginDescriptor.WHERE_AUTOSTART], fnc=autostart), PluginDescriptor(name=_('View RSS') + ' spazeTeam', description=_("Let's you view current RSS entries"), where=PluginDescriptor.WHERE_EXTENSIONSMENU, fnc=main)]
