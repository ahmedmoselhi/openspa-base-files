from Components.Task import Task, Job, job_manager
from enigma import *
from Components.Label import Label
from Components.MenuList import MenuList
from Components.PluginComponent import plugins
from Screens.ChannelSelection import ChannelSelectionBase, ChannelSelectionEPG, SelectionEventInfo, ChannelSelection
from Components.MultiContent import MultiContentEntryText
from enigma import eListboxPythonMultiContent, eServiceCenter, gFont, RT_HALIGN_RIGHT, RT_HALIGN_LEFT, RT_HALIGN_CENTER, eServiceReference
from enigma import eTimer
from enigma import eSize, ePoint
from ServiceReference import ServiceReference
from Components.Sources.ServiceEvent import ServiceEvent
from Components.Pixmap import Pixmap, MovingPixmap
from Tools.LoadPixmap import LoadPixmap
from Components.EpgList import EPGList, EPG_TYPE_SINGLE, EPG_TYPE_SIMILAR, EPG_TYPE_MULTI
from Screens.ChoiceBox import ChoiceBox
from RecordTimer import RecordTimerEntry, parseEvent, AFTEREVENT
from Components.UsageConfig import preferredTimerPath
from Screens.TimerEntry import TimerEntry
from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Components.ConfigList import ConfigListScreen
from Screens.MessageBox import MessageBox
from twisted.internet import reactor
from Components.ActionMap import ActionMap
from Components.Button import Button
from GlobalActions import globalActionMap
from Screens.EventView import EventViewSimple
from Components.config import getConfigListEntry, ConfigEnableDisable, ConfigYesNo, ConfigText, ConfigClock, ConfigNumber, ConfigSelection, config, ConfigSubsection, ConfigSubList, ConfigSubDict, ConfigDirectory
from Tools import Notifications
import os
from time import localtime, asctime, time, gmtime, strftime
from Tools.Directories import fileExists, resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE, SCOPE_SKIN, SCOPE_CURRENT_SKIN, SCOPE_SKIN_IMAGE
from Components.Language import language
from os import environ
import os
from Components.MultiContent import MultiContentEntryText
from enigma import eListboxPythonMultiContent, gFont
from enigma import eEPGCache
config.misc.spazeChannelSelection = ConfigYesNo(default=True)
from Components.ActionMap import HelpableActionMap
from Screens.newChannelSelection import newChannelSelection

def nchannelSelection__init__(self):
    self.servicelist = self.session.instantiateDialog(newChannelSelection)
    if config.misc.initialchannelselection.value:
        self.onShown.append(self.firstRun)
    self['ChannelSelectActions'] = HelpableActionMap(self, 'InfobarChannelSelection', {'keyUp': (self.keyUpCheck, self.getKeyUpHelptext),
     'keyDown': (self.keyDownCheck, self.getKeyDownHelptext),
     'keyLeft': (self.keyLeftCheck, self.getKeyLeftHelptext),
     'keyRight': (self.keyRightCheck, self.getKeyRightHelptext),
     'historyBack': (self.historyBack, _('previous channel in history')),
     'historyNext': (self.historyNext, _('next channel in history')),
     'keyChannelUp': (self.keyChannelUpCheck, self.getKeyChannelUpHelptext),
     'keyChannelDown': (self.keyChannelDownCheck, self.getKeyChannelDownHelptext)})


def autostart(reason, **kwargs):
    global session
    global gSession
    if config.misc.spazeChannelSelection.value:
        from Screens.InfoBarGenerics import InfoBarChannelSelection
        try:
            InfoBarChannelSelection.__init__ = nchannelSelection__init__
        except:
            pass

    return
    if reason == 0 and kwargs.has_key('session'):
        gSession = kwargs['session']
        session = kwargs['session']
        chequeaLista()
        gSession = kwargs['session']


def pondebug(loque):
    os.system('date >>/tmp/errnc.log')
    os.system("echo '" + loque + "' >>/tmp/errnc.log")
    os.system("echo '------------------------------------------' >>/tmp/errnc.log")


class chequeaLista:
    TimerLista = eTimer()

    def __init__(self):
        try:
            if 'newChannelSelection' in str(InfoBar.instance.servicelist):
                return
        except:
            pass

        if config.misc.spazeChannelSelection.value:
            self.TimerLista.callback.append(self.CheckCambiar)
            self.TimerLista.startLongTimer(10)

    def CheckCambiar(self):
        try:
            from Screens.InfoBar import InfoBar
            if 'newChannelSelection' in str(InfoBar.instance.servicelist):
                return
            if InfoBar and InfoBar.instance and not InfoBar.instance.servicelist == None:
                InfoBar.instance.servicelist = InfoBar.instance.session.instantiateDialog(newChannelSelection)
            else:
                self.TimerLista.startLongTimer(6)
        except Exception as e:
            self.TimerLista.startLongTimer(5)


class CheckCambiarScreen(Screen):
    skin = ' <screen position="29,29" size="196,87" title="%s" flags="wfNoBorder" backgroundColor="#ff000000" >\n\t\t\t<widget name="texto" position="0,0" size="345,30" valign="center" halign="center" font="Regular;19" transparent="1" backgroundColor="#000000" />\n\t\t\t<ePixmap name="new ePixmap" position="0,0" size="196,87" zPosition="0" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/newChannelSelection/spzTeam/logospzfs8.png" alphatest="blend" />\n\t\t</screen>' % _('spazeTeam ChannelSelection')

    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session
        self['texto'] = Label(_(' '))
        self['actions'] = ActionMap(['DirectionActions',
         'ShortcutActions',
         'WizardActions',
         'EPGSelectActions'], {'ok': self.nada,
         'red': self.exit}, -1)
        self.TimerChequea = eTimer()
        self.TimerChequea.callback.append(self.actualiza)
        self.onLayoutFinish.append(self.actualiza)

    def actualiza(self):
        try:
            from Screens.InfoBar import InfoBar
            if InfoBar and InfoBar.instance:
                InfoBar.instance.servicelist = InfoBar.instance.session.instantiateDialog(newChannelSelection)
            self.close()
        except:
            self.TimerChequea.TimerChequea(10)
            self['texto'].setText('Err 1')

    def nada(self):
        pass

    def exit(self):
        self.close()


def main(session, **kwargs):
    pass


def Plugins(**kwargs):
    return [PluginDescriptor(name=_('New Channel Selection'), description=_('New Channel Selection'), where=[PluginDescriptor.WHERE_SESSIONSTART, PluginDescriptor.WHERE_AUTOSTART], fnc=autostart), PluginDescriptor(name=_('New Channel Selection'), description=_('New Channel Selection'), where=PluginDescriptor.WHERE_PLUGINMENU, fnc=main)]
