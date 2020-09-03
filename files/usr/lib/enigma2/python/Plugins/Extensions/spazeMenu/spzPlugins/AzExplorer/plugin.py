from enigma import eTimer
from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Screens.InfoBar import InfoBar
from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap
from Components.MenuList import MenuList
from Components.Label import Label
from Components.Button import Button
from Components.Pixmap import Pixmap
from Tools.Directories import fileExists, pathExists, resolveFilename, SCOPE_LANGUAGE, SCOPE_PLUGINS
from Components.Language import language
from explorer import salirEspera, azExplorerII
from Components.config import config
from Plugins.Extensions.spazeMenu.plugin import esHD
from os import environ
import os
import gettext
import stat
lang = language.getLanguage()
environ['LANGUAGE'] = lang[:2]
gettext.bindtextdomain('enigma2', resolveFilename(SCOPE_LANGUAGE))
gettext.textdomain('enigma2')
gettext.bindtextdomain('AzExplorer', '%s%s' % (resolveFilename(SCOPE_PLUGINS), 'Extensions/spazeMenu/spzPlugins/AzExplorer/locale/'))

def _(txt):
    t = gettext.dgettext('AzExplorer', txt)
    if t == txt:
        t = gettext.gettext(txt)
    return t


def Plugins(**kwargs):
    list = [PluginDescriptor(name=_('Explorer'), description=_('Explore files in your Azbox.'), where=[PluginDescriptor.WHERE_PLUGINMENU], icon='azexplorer.png', fnc=main)]
    list.append(PluginDescriptor(name=_('Explorer'), where=PluginDescriptor.WHERE_EXTENSIONSMENU, fnc=main))
    if config.plugins.azExplorer.showinmenu.value:
        list.append(PluginDescriptor(name=_('Explorer'), description=_('Explore files in your Azbox.'), where=PluginDescriptor.WHERE_MENU, fnc=start_from_mainmenu))
    return list


def main(session, rutainicial = None, **kwargs):
    session.open(esperaExplorer, rutainicial)


def start_from_mainmenu(menuid, **kwargs):
    if menuid == 'mainmenu':
        return [(_('Explorer'),
          main,
          'explorer',
          46)]
    return []


def autostart(reason, **kwargs):
    global explSession
    if reason == 0:
        if kwargs.has_key('session'):
            explSession = kwargs['session']


class esperaExplorer(Screen):
    if esHD():
        skin = '\n\t\t<screen position="center,center" size="585,139" title="%s" >\n\t\t\t<ePixmap name="new ePixmap" position="0,0" size="130,139" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/AzExplorer/res/iconofs8.png" alphatest="blend" />\n\t\t\t<widget name="texto" position="165,0" size="240,139" valign="center" halign="left" font="Regular;20" itemHeight="42" />\n\t\t</screen>' % _('az-Explorer')
    skin = '\n\t\t<screen position="center,center" size="390,93" title="%s" >\n\t\t\t<ePixmap name="new ePixmap" position="0,0" size="87,93" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/AzExplorer/res/iconofs8.png" alphatest="blend" />\n\t\t\t<widget name="texto" position="110,0" size="160,93" valign="center" halign="left" font="Regular;20" />\n \t\t</screen>' % _('az-Explorer')

    def __init__(self, session, rutainicial = None):
        self.session = session
        Screen.__init__(self, session)
        self['texto'] = Label(_('Starting') + '...')
        self.rutainicial = rutainicial
        self.puntos = '...'
        self.TimerTemp = eTimer()
        self.TimerTemp.callback.append(self.mirar)
        self.iniciado = False
        self['actions'] = ActionMap(['DirectionActions',
         'ShortcutActions',
         'WizardActions',
         'EPGSelectActions'], {'ok': self.nada,
         'green': self.nada,
         'red': self.nada,
         'back': self.nada,
         'info': self.nada,
         'left': self.nada,
         'right': self.nada,
         'up': self.nada,
         'down': self.nada}, -1)
        self.onShow.append(self.mirar)

    def abrir(self):
        self.session.open(azExplorerII, self.rutainicial)

    def mirar(self):
        self.TimerTemp.stop()
        if not self.iniciado:
            self.TimerTemp2 = eTimer()
            self.TimerTemp2.callback.append(self.abrir)
            self.TimerTemp2.start(300, True)
            self.iniciado = True
            self['texto'].setText(_('Starting') + self.puntos)
        if salirEspera():
            self.TimerTemp.callback.append(self.exit)
            self.TimerTemp.startLongTimer(1)
        else:
            self['texto'].setText(_('Starting') + self.puntos)
            self.TimerTemp.startLongTimer(1)

    def exit(self):
        self['texto'].setText(_('Closing') + self.puntos)
        self.TimerTemp.stop()
        self.close()

    def nada(self):
        pass
