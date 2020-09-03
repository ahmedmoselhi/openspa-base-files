from enigma import *
from enigma import eTimer
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.ActionMap import ActionMap
from Components.ProgressBar import ProgressBar
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Plugins.Plugin import PluginDescriptor
import os
import sys
import time
from os import environ
import gettext
from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE
lang = language.getLanguage()
environ['LANGUAGE'] = lang[:2]
gettext.bindtextdomain('enigma2', resolveFilename(SCOPE_LANGUAGE))
gettext.textdomain('enigma2')
gettext.bindtextdomain('mhwEPG', '%s%s' % (resolveFilename(SCOPE_PLUGINS), 'Extensions/spazeMenu/spzPlugins/mhw2Timer/locale/'))
from Components.config import ConfigNumber, config, ConfigSubsection
config.plugins.mwhepg = ConfigSubsection()
config.plugins.mwhepg.standbyOnChannel = ConfigNumber(default=100)

def _(txt):
    t = gettext.dgettext('mhwEPG', txt)
    if t == txt:
        t = gettext.gettext(txt)
    return t


class mhwWrapper:
    EVENT_CHANNEL = 0
    EVENT_PROG = 1
    EVENT_SUMMARY = 2
    EVENT_EPGDAT = 3
    EVENT_CLOSE = 4
    EVENT_QUIT = 5
    EVENT_PROGRESS = 6

    def __init__(self):
        self.cmd = eConsoleAppContainer()
        self.cache = None
        self.callbackList = []


from Plugins.Extensions.spazeMenu.plugin import esHD

class mhwEPG(Screen):
    if esHD():
        skin = '\n\t\t<screen name="mhwEPG" position="40,40" size="615,195" title="mhwEPG" flags="wfNoBorder" backgroundColor="#ff000000">\n\t\t<ePixmap name="background" position="0,0" size="615,195" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/mhw2Timer/backgroundHD.png" zPosition="-1" alphatest="off" />\n\t\t<widget name="action" halign="left" valign="center" position="13,9" size="433,30" font="Regular;17" foregroundColor="#dfdfdf" transparent="1" backgroundColor="#000000" borderColor="black" borderWidth="1" noWrap="1"/>\n\t\t<widget name="progress" position="30,97" size="540,12" borderWidth="0" backgroundColor="#1143495b" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/mhw2Timer/progreso.png" zPosition="2" alphatest="blend" />\n\t\t<eLabel name="fondoprogreso" position="30,97" size="540,12" backgroundColor="#102a3b58" />\n\t\t<widget name="espera" valign="center" halign="center" position="30,63" size="540,30" font="Regular;15" foregroundColor="#dfdfdf" transparent="1" backgroundColor="#000000" borderColor="black" borderWidth="1" noWrap="1"/>\n\t\t<widget name="status" halign="center" valign="center" position="30,120" size="540,30" font="Regular;16" foregroundColor="#ffffff" transparent="1" backgroundColor="#000000" borderColor="black" borderWidth="1" noWrap="1"/>\n\t\t</screen>'
    else:
        skin = '\n\t\t<screen name="mhwEPG" position="40,40" size="410,130" title="mhwEPG" flags="wfNoBorder" backgroundColor="#ff000000">\n\t\t<ePixmap name="background" position="0,0" size="410,130" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/mhw2Timer/background.png" zPosition="-1" alphatest="off" />\n\t\t<widget name="action" halign="left" valign="center" position="9,6" size="289,20" font="Regular;17" foregroundColor="#dfdfdf" transparent="1" backgroundColor="#000000" borderColor="black" borderWidth="1" noWrap="1"/>\n\t\t<widget name="progress" position="20,65" size="360,8" borderWidth="0" backgroundColor="#1143495b" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/mhw2Timer/progreso.png" zPosition="2" alphatest="blend" />\n\t\t<eLabel name="fondoprogreso" position="20,65" size="360,8" backgroundColor="#102a3b58" />\n\t\t<widget name="espera" valign="center" halign="center" position="20,42" size="360,20" font="Regular;15" foregroundColor="#dfdfdf" transparent="1" backgroundColor="#000000" borderColor="black" borderWidth="1" noWrap="1"/>\n\t\t<widget name="status" halign="center" valign="center" position="20,80" size="360,20" font="Regular;16" foregroundColor="#ffffff" transparent="1" backgroundColor="#000000" borderColor="black" borderWidth="1" noWrap="1"/>\n\t\t</screen>'

    def __init__(self, session, name, timer):
        self.session = session
        Screen.__init__(self, session)
        self.iprogress = 0
        self.sec = 0
        self.tsec = timer
        self.TimerTemp = None
        self.sw = False
        self['action'] = Label(_('EPG Download:') + ' ' + name)
        self.setTitle(_('EPG Download:') + ' ' + name)
        self['status'] = Label(_('Wait...'))
        self['channels'] = Label('')
        self['titles'] = Label('')
        self['summaries'] = Label('')
        self['espera'] = Label('')
        self['progress'] = ProgressBar()
        self['actions'] = ActionMap(['OkCancelActions'], {'cancel': self.salir}, -1)
        self.oldService = None
        self.ss = self.tsec / 100
        self.onFirstExecBegin.append(self.firstExec)
        self.onShow.append(self.download)

    def salir(self):
        stri = _('The download is in progress. Exit now?')
        self.session.openWithCallback(self.salirok, MessageBox, stri, MessageBox.TYPE_YESNO, timeout=30)

    def salirok(self, answer):
        if answer:
            self.close(True)

    def firstExec(self):
        pass

    def download(self):
        self.actualizaprogreso()

    def actualizaprogreso(self):
        self['progress'].setValue(self.iprogress)
        self.sec = self.sec + 1
        self.iprogress = self.sec * 100 // self.tsec
        self.sw = not self.sw
        if self.iprogress >= 100:
            self['espera'].setText('100 %')
            self.setTitle('MediaHighway2 - ' + _('Download') + ' [100%]')
        else:
            self['espera'].setText(str(self.iprogress) + ' %')
            self.setTitle('MediaHighway2 - ' + _('Download') + ' [' + str(self.iprogress) + ' %]')
        if self.iprogress > 101:
            self.iprogress = 100
            self.close(True)
        else:
            self.TimerTemp = eTimer()
            self.TimerTemp.callback.append(self.actualizaprogreso)
            self.TimerTemp.startLongTimer(1)
