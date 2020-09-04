from Components.Sources.StaticText import StaticText
from Components.config import *
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Plugins.Plugin import PluginDescriptor
import os
import time
from MC_AudioPlayer import MC_AudioPlayer
from MC_VideoPlayer import MC_VideoPlayer
from MC_PictureViewer import MC_PictureViewer
from MC_Settings import MC_Settings, MCS_Update
from Components.AVSwitch import AVSwitch
from Components.SystemInfo import SystemInfo
config.plugins.mc_scal = ConfigSubsection()
config.plugins.mc_scal.scalingmode = ConfigInteger(default=0, limits=(0, 100))
config.plugins.mc_globalsettings = ConfigSubsection()
config.plugins.mc_globalsettings.showinmainmenu = ConfigYesNo(default=False)
from os import environ
import gettext
from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE, fileExists
lang = language.getLanguage()
environ['LANGUAGE'] = lang[:2]
gettext.bindtextdomain('enigma2', resolveFilename(SCOPE_LANGUAGE))
gettext.textdomain('enigma2')
gettext.bindtextdomain('MediaCenterPlugin', '%s%s' % (resolveFilename(SCOPE_PLUGINS), 'Extensions/MediaCenter/locale/'))

def _(txt):
    t = gettext.dgettext('MediaCenterPlugin', txt)
    if t == txt:
        t = gettext.gettext(txt)
    return t


class DMC_MainMenu(Screen):

    def __init__(self, session):
        Screen.__init__(self, session)
        self.oldService = self.session.nav.getCurrentlyPlayingServiceOrGroup()
        self['actions'] = ActionMap(['OkCancelActions'], {'cancel': self.Exit,
         'ok': self.okbuttonClick}, -1)
        list = []
        list.append((_('My Videos'),
         'MC_VideoPlayer',
         'menu_video',
         '50'))
        list.append((_('My Music'),
         'MC_AudioPlayer',
         'menu_music',
         '50'))
        list.append((_('My Pictures'),
         'MC_PictureViewer',
         'menu_pictures',
         '50'))
        list.append((_('Settings'),
         'MC_Settings',
         'menu_settings',
         '50'))
        self['menu'] = List(list)
        self['title'] = StaticText(_('Media Center'))
        print 'Setting back TV scaling mode'
        try:
            SString = str(config.av.scalmodemc.value)
            open('/proc/scalingmode', 'w').write(str(SString))
            open('/proc/scalingmode', 'w').close()
            config.plugins.mc_scal.scalingmode.value = str(config.av.scalmodemc.value)
            config.plugins.mc_scal.save()
            configfile.save()
        except:
            pass

    def okbuttonClick(self):
        print 'okbuttonClick'
        selection = self['menu'].getCurrent()
        if selection is not None:
            if selection[1] == 'MC_VideoPlayer':
                self.session.open(MC_VideoPlayer)
            elif selection[1] == 'MC_PictureViewer':
                self.session.open(MC_PictureViewer)
            elif selection[1] == 'MC_AudioPlayer':
                self.session.open(MC_AudioPlayer)
            elif selection[1] == 'MC_Settings':
                self.session.open(MC_Settings)
            else:
                self.session.open(MessageBox, 'Error: Something is wrong, cannot find %s\n' % selection[1], MessageBox.TYPE_INFO)

    def Exit(self):
        try:
            SString = str(config.av.scalmode.value)
            open('/proc/scalingmode', 'w').write(str(SString))
            open('/proc/scalingmode', 'w').close()
        except:
            pass

        if fileExists('/tmp/.mcscaling'):
            os.remove('/tmp/.mcscaling')
        self.close()


actualsession = None

def Launch(confirmFlag = True):
    global actualsession
    if confirmFlag:
        for timer in actualsession.nav.RecordTimer.timer_list + actualsession.nav.RecordTimer.processed_timers:
            if timer.begin - time.time() < 360:
                actualsession.nav.RecordTimer.removeEntry(timer)

        actualsession.open(DMC_MainMenu)


def main(session, **kwargs):
    global actualsession
    session.open(MC_VideoPlayer)
    return
    recordings = len(session.nav.getRecordings())
    next_rec_time = session.nav.RecordTimer.getNextRecordingTime()
    if not recordings and (next_rec_time - time.time() > 360 or next_rec_time < 0):
        session.open(DMC_MainMenu)
    else:
        actualsession = session
        stri = _('A recording is in progress. If you continue recording stops.\n Want to continue?')
        session.openWithCallback(Launch, MessageBox, stri, MessageBox.TYPE_YESNO, timeout=30)


def menu(menuid, **kwargs):
    if menuid == 'mainmenu':
        return [(_('Media Center'),
          main,
          'dmc_mainmenu',
          44)]
    return []


def autostart(reason, **kwargs):
    pass


def Plugins(**kwargs):
    return [PluginDescriptor(where=[PluginDescriptor.WHERE_SESSIONSTART, PluginDescriptor.WHERE_AUTOSTART], fnc=autostart)]
