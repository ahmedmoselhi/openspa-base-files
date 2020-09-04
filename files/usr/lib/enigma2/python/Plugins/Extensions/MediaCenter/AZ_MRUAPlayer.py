from Screens.MinuteInput import MinuteInput
from Screens.ServiceInfo import ServiceInfoList, ServiceInfoListEntry
from Screens.HelpMenu import HelpableScreen
from Screens.MessageBox import MessageBox
from Screens.ChoiceBox import ChoiceBox
from Screens.InfoBarGenerics import InfoBarSeek, InfoBarPVRState, InfoBarCueSheetSupport, InfoBarShowHide, InfoBarNotifications, InfoBarAudioSelection, InfoBarSubtitleSupport
from Components.ActionMap import ActionMap, NumberActionMap, HelpableActionMap
from Components.Pixmap import Pixmap, MovingPixmap
from Components.Label import Label
from Components.Sources.List import List
from Components.Sources.StaticText import StaticText
from Components.Button import Button
from Components.ServiceEventTracker import ServiceEventTracker
from Components.ConfigList import ConfigList, ConfigListScreen
from Components.config import *
from Components.Harddisk import harddiskmanager
from Tools.Directories import resolveFilename, fileExists, pathExists, createDir, SCOPE_MEDIA
from Components.Sources.StaticText import StaticText
from Components.MenuList import MenuList
from Components.ServiceEventTracker import ServiceEventTracker, InfoBarBase
from Plugins.Extensions.spazeMenu.spzPlugins.scrInformation.plugin import mostrarNotificacion
import os
from os import path as os_path, remove as os_remove, listdir as os_listdir, system
from MC_SeekInput import SeekInput
from MC_Menus import IniciaSelListMC, IniciaSelListEntryMC, Scalingmode_Menu, ScalingmodeEntryComponent, SubOptionsEntryComponent
from MC_Filelist import setResumePoint, getResumePoint
from Tools import Notifications
config.plugins.mc_mrua = ConfigSubsection()
config.plugins.mc_mrua.subenc = ConfigSelection(default='43', choices=[('42', _('Latin')), ('43', _('Utf-8'))])
config.plugins.mc_mrua.subpos = ConfigInteger(default=40, limits=(0, 100))
config.plugins.mc_mrua.subcolorname = ConfigText(default=_('White'))
config.plugins.mc_mrua.subcolorinside = ConfigText('FFFFFFFF', fixed_size=False)
config.plugins.mc_mrua.subcoloroutside = ConfigText('FF000000', fixed_size=False)
config.plugins.mc_mrua.subsize = ConfigInteger(default=50, limits=(30, 90))
config.plugins.mc_mrua.subdelay = ConfigInteger(default=0, limits=(-999999, 999999))
config.plugins.mc_mrua.screenres = ConfigInteger(default=0, limits=(-999999, 999999))
config.plugins.mc_mrua.subcolor = ConfigInteger(default=1, limits=(0, 9))
config.plugins.mc_mrua.repeat = ConfigYesNo(default=False)
config.plugins.mc_mrua.list1 = ConfigText(default=_('PlayList File') + '1')
config.plugins.mc_mrua.list2 = ConfigText(default=_('PlayList File') + '2')
config.plugins.mc_mrua.list3 = ConfigText(default=_('PlayList File') + '3')
config.plugins.mc_mrua.list4 = ConfigText(default=_('PlayList File') + '4')
config.plugins.mc_mrua.list5 = ConfigText(default=_('PlayList File') + '5')
config.plugins.mc_mrua.list6 = ConfigText(default=_('PlayList File') + '6')
config.plugins.mc_mrua.list7 = ConfigText(default=_('PlayList File') + '7')
config.plugins.mc_mrua.list8 = ConfigText(default=_('PlayList File') + '8')
config.plugins.mc_mrua.list9 = ConfigText(default=_('PlayList File') + '9')
from Plugins.Extensions.spazeMenu.spzPlugins.scrInformation.plugin import scrInformation
from timeSleepMRU import timesleep, timesleepBack
from time import localtime

def Humanizer(size, mostrarbytes = False):
    if size < 1024:
        humansize = str(size) + ' bytes'
    elif size < 1048576:
        humansize = '%.2f Kb' % (float(size) / 1024)
        if mostrarbytes:
            humansize = humansize + ' (' + str(size) + ' bytes)'
    elif size < 1073741824:
        humansize = '%.2f Mb' % (float(size) / 1048576)
        if mostrarbytes:
            humansize = humansize + ' (' + str(size) + ' bytes)'
    else:
        humansize = '%.2f Gb' % (float(size) / 1073741824)
        if mostrarbytes:
            humansize = humansize + ' (' + str(size) + ' bytes)'
    return humansize


from os import environ
import gettext
from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE
lang = language.getLanguage()
environ['LANGUAGE'] = lang[:2]
gettext.bindtextdomain('enigma2', resolveFilename(SCOPE_LANGUAGE))
gettext.textdomain('enigma2')
gettext.bindtextdomain('AZ_MRUAPlayer', '%s%s' % (resolveFilename(SCOPE_PLUGINS), 'Extensions/MediaCenter/locale/'))

def _(txt):
    t = gettext.dgettext('AZ_MRUAPlayer', txt)
    if t == txt:
        t = gettext.gettext(txt)
    return t


class MRUASummary(Screen):
    skin = '\n\t<screen name="MRUASummary" position="0,0" size="90,64" id="3">\n\t\t<widget source="session.CurrentService" render="Label" position="0,0" size="120,25" font="Display;16" halign="center" valign="center">\n\t\t\t<convert type="ServicePosition">Position,ShowHours</convert>\n\t\t</widget>\n\t</screen>'

    def __init__(self, session, parent):
        Screen.__init__(self, session)


class MRUAPlayer(Screen, InfoBarBase, InfoBarNotifications, InfoBarSeek, InfoBarPVRState, InfoBarShowHide, HelpableScreen, InfoBarCueSheetSupport, InfoBarAudioSelection, InfoBarSubtitleSupport):
    ALLOW_SUSPEND = Screen.SUSPEND_PAUSES
    ENABLE_RESUME_SUPPORT = False

    def save_infobar_seek_config(self):
        self.saved_config_speeds_forward = config.seek.speeds_forward.value
        self.saved_config_speeds_backward = config.seek.speeds_backward.value
        self.saved_config_enter_forward = config.seek.enter_forward.value
        self.saved_config_enter_backward = config.seek.enter_backward.value
        self.saved_config_seek_on_pause = config.seek.on_pause.value
        self.saved_config_seek_speeds_slowmotion = config.seek.speeds_slowmotion.value
        self.saved_config_subenc = config.plugins.mc_mrua.subenc.value
        self.saved_config_subpos = config.plugins.mc_mrua.subpos.value
        self.saved_config_subcolorname = config.plugins.mc_mrua.subcolorname.value
        self.saved_config_subcolor = config.plugins.mc_mrua.subcolor.value
        self.saved_config_subsize = config.plugins.mc_mrua.subsize.value
        self.saved_config_subdelay = config.plugins.mc_mrua.subdelay.value

    def change_infobar_seek_config(self):
        config.seek.speeds_forward.value = [2,
         4,
         8,
         16,
         32,
         64]
        config.seek.speeds_backward.value = [2,
         4,
         8,
         16,
         32,
         64]
        config.seek.speeds_slowmotion.value = []
        config.seek.enter_forward.value = '2'
        config.seek.enter_backward.value = '2'
        config.seek.on_pause.value = 'play'

    def restore_infobar_seek_config(self):
        config.seek.speeds_forward.value = self.saved_config_speeds_forward
        config.seek.speeds_backward.value = self.saved_config_speeds_backward
        config.seek.speeds_slowmotion.value = self.saved_config_seek_speeds_slowmotion
        config.seek.enter_forward.value = self.saved_config_enter_forward
        config.seek.enter_backward.value = self.saved_config_enter_backward
        config.seek.on_pause.value = self.saved_config_seek_on_pause
        config.plugins.mc_mrua.subenc.value = self.saved_config_subenc
        config.plugins.mc_mrua.subpos.value = self.saved_config_subpos
        config.plugins.mc_mrua.subcolorname.value = self.saved_config_subcolorname
        config.plugins.mc_mrua.subcolor.value = self.saved_config_subcolor
        config.plugins.mc_mrua.subsize.value = self.saved_config_subsize
        config.plugins.mc_mrua.subdelay.value = self.saved_config_subdelay

    def __init__(self, session, ref = '', args = None, Listado = []):
        Screen.__init__(self, session)
        InfoBarBase.__init__(self)
        InfoBarNotifications.__init__(self)
        InfoBarCueSheetSupport.__init__(self, actionmap='MediaPlayerCueSheetActions')
        InfoBarShowHide.__init__(self)
        InfoBarAudioSelection.__init__(self)
        InfoBarSubtitleSupport.__init__(self)
        HelpableScreen.__init__(self)
        self.save_infobar_seek_config()
        self.change_infobar_seek_config()
        InfoBarSeek.__init__(self)
        InfoBarPVRState.__init__(self)
        self.skinName = ['MRUAPlayer', 'DVDPlayer']
        self.oldService = self.session.nav.getCurrentlyPlayingServiceOrGroup()
        self.session.nav.stopService()
        self['audioLabel'] = Label('n/a')
        self['subtitleLabel'] = Label('')
        self['angleLabel'] = Label('')
        self['chapterLabel'] = Label('')
        self['anglePix'] = Pixmap()
        self['anglePix'].hide()
        self.last_audioTuple = None
        self.last_subtitleTuple = None
        self.last_angleTuple = None
        self.totalChapters = 0
        self.currentChapter = 0
        self.totalTitles = 0
        self.currentTitle = 0
        self.listado = Listado
        self.contador = 0
        self.colors = [_('Black'),
         _('White'),
         _('Yellow'),
         _('Blue'),
         _('Red'),
         _('Green'),
         _('Orange'),
         _('Blue2'),
         _('Blue3'),
         _('Pink')]
        self.__event_tracker = ServiceEventTracker(screen=self, eventmap={iPlayableService.evEOF: self.__serviceStopped,
         iPlayableService.evStopped: self.__serviceStopped,
         iPlayableService.evStart: self.__serviceStarted,
         iPlayableService.evUser + 1: self.__statePlay,
         iPlayableService.evUser + 2: self.__statePause,
         iPlayableService.evUser + 3: self.__osdStringAvail,
         iPlayableService.evUser + 4: self.__osdAudioInfoAvail,
         iPlayableService.evUser + 5: self.__osdSubtitleInfoAvail})
        self['MRUAPlayerDirectionActions'] = ActionMap(['DirectionActions'], {'left': self.keyLeft,
         'right': self.keyRight,
         'leftRepeated': self.doNothing,
         'rightRepeated': self.doNothing,
         'upRepeated': self.doNothing,
         'downRepeated': self.doNothing,
         'leftUp': self.doNothing,
         'rightUp': self.doNothing,
         'upUp': self.doNothing,
         'downUp': self.doNothing})
        self['OkCancelActions'] = ActionMap(['OkCancelActions'], {'ok': self.keyOk,
         'cancel': self.keyCancel})
        self['DVDPlayerPlaybackActions'] = HelpableActionMap(self, 'MRUAPlayerActions', {'stop': (self.stop, _('Stop Playback')),
         'keyMenu': (self.menu, _('Show menu options')),
         'seekTotime': (self.seekTotime, _('switch to the next angle')),
         'seekFwdinput': (self.seekFwdInput, _('Seek forward with input box')),
         'seekBwdinput': (self.seekBwdInput, _('Seek backward with input box')),
         'subtitles': (self.subtitleSelection, _('Subtitle selection')),
         'playpause': (self.playpauseService, _('Pause / Resume')),
         'toggleInfo': (self.toggleShow, _('toggle time, chapter, audio, subtitle info')),
         'seekFwd': (self.keyRight, _('Seek forward')),
         'seekBwd': (self.keyLeft, _('Seek backward')),
         'AudioSelection': (self.audioSelection, _('Select audio track')),
         'scalingmode': (self.scalingmode, _('Select scaling mode'))}, -2)
        self['NumberActions'] = NumberActionMap(['NumberActions'], {'1': self.keyNumberGlobal,
         '2': self.keyNumberGlobal,
         '3': self.keyNumberGlobal,
         '4': self.keyNumberGlobal,
         '5': self.keyNumberGlobal,
         '6': self.keyNumberGlobal,
         '7': self.keyNumberGlobal,
         '8': self.keyNumberGlobal,
         '9': self.keyNumberGlobal,
         '0': self.keyNumberGlobal})
        self.onClose.append(self.__onClose)
        config.plugins.mc_mrua.screenres.value = str(config.av.videomode[config.av.videoport.value].value)[:-1]
        os.popen('killall rmfp_player')
        open('/proc/player', 'w').write('2')
        os.system('echo 0 > /tmp/zerortc')
        os.system('mount -o bind /tmp/zerortc /proc/stb/fp/rtc')
        self.ref = ref
        self.onFirstExecBegin.append(self.Start)
        self.service = None
        self.in_menu = False
        self.selected_subtitle = None
        self.repetir = False

    def reinicia(self):
        try:
            self.session.nav.stopService()
            self.service = None
            self.session.nav.playService(None)
            os.popen('killall rmfp_player')
            mostrarNotificacion(id='az_mruaplayer', texto=_('Repeating title...'), segundos=4)
            self.ENABLE_RESUME_SUPPORT = False
            self.repetir = True
            self.Start()
        except:
            self.exit()

    def __serviceStopped(self):
        ref = self.session.nav.getCurrentlyPlayingServiceOrGroup()
        if ref:
            setResumePoint(self.session, True)
        if len(self.listado) > 0:
            self.contador = self.contador + 1
            if self.contador >= len(self.listado):
                self.contador = 0
            else:
                self.session.nav.stopService()
                self.service = None
                self.session.nav.playService(None)
                os.popen('killall rmfp_player')
                if not fileExists(self.listado[self.contador]):
                    Notifications.AddPopup(text=_('Verify playlist. Press [MENU]') + '\n' + _('File not exists!') + ':\n' + self.listado[self.contador], type=MessageBox.TYPE_ERROR, timeout=8, id='azmruaplayer')
                    return
                else:
                    try:
                        mostrarNotificacion(id='az_mruaplayer', texto=_('PlayList') + ': ' + str(self.contador + 1) + ' ' + _('of') + ' ' + str(len(self.listado)), segundos=4)
                    except:
                        pass

                    self.ENABLE_RESUME_SUPPORT = False
                    self.Start()
                    return
        if config.plugins.mc_mrua.repeat.value:
            self.reinicia()
        else:
            self.exit()

    def __serviceStarted(self):
        service = self.session.nav.getCurrentService()
        seekable = service.seek()
        ref = self.session.nav.getCurrentlyPlayingServiceReference()
        perc, last, length = getResumePoint(ref)
        if last is None:
            return
        if seekable is None:
            return
        length = seekable.getLength() or (None, 0)
        print 'seekable.getLength() returns:', length
        if last > 900000 and (not length[1] or last < length[1] - 900000):
            self.resume_point = last
            l = last / 90000
            if 'ask' in config.usage.on_movie_start.value or not length[1]:
                Notifications.AddNotificationWithCallback(self.playLastCB, MessageBox, _('Do you want to resume this playback?') + '\n' + _('Resume position at %s') % ('%d:%02d:%02d' % (l / 3600, l % 3600 / 60, l % 60)), timeout=10, default='yes' in config.usage.on_movie_start.value)
            elif config.usage.on_movie_start.value == 'resume':
                Notifications.AddNotificationWithCallback(self.playLastCB, MessageBox, _('Resuming playback'), timeout=2, type=MessageBox.TYPE_INFO)
        self['SeekActions'].setEnabled(False)

    def __statePlay(self):
        print 'statePlay'

    def __statePause(self):
        print 'statePause'

    def __osdStringAvail(self):
        print 'StringAvail'

    def __osdAudioInfoAvail(self):
        info = self.getServiceInterface('info')
        audioTuple = info and info.getInfoObject(iServiceInformation.sUser + 6)
        print 'AudioInfoAvail ', repr(audioTuple)
        if audioTuple:
            audioString = '%d: %s' % (audioTuple[0], audioTuple[1])
            self['audioLabel'].setText(audioString)
            if audioTuple != self.last_audioTuple and not self.in_menu:
                self.doShow()
        self.last_audioTuple = audioTuple

    def __osdSubtitleInfoAvail(self):
        info = self.getServiceInterface('info')
        subtitleTuple = info and info.getInfoObject(iServiceInformation.sUser + 7)
        print 'SubtitleInfoAvail ', repr(subtitleTuple)
        if subtitleTuple:
            subtitleString = ''
            if subtitleTuple[0] is not 0:
                subtitleString = '%d: %s' % (subtitleTuple[0], subtitleTuple[1])
            self['subtitleLabel'].setText(subtitleString)
            if subtitleTuple != self.last_subtitleTuple and not self.in_menu:
                self.doShow()
        self.last_subtitleTuple = subtitleTuple

    def keyNumberGlobal(self, number):
        print 'You pressed number ' + str(number)

    def getServiceInterface(self, iface):
        service = self.service
        if service:
            attr = getattr(service, iface, None)
            if callable(attr):
                return attr()

    def doNothing(self):
        pass

    def sendKey(self, key):
        keys = self.getServiceInterface('keys')
        if keys:
            keys.keyPressed(key)
        return keys

    def audioSelection(self):
        playposition = 0
        try:
            seek = self.service and self.service.seek()
        except:
            pass

        if seek:
            playposition = seek.getPlayPosition()
        if playposition > 2000:
            from Screens.AudioSelection import AudioSelection
            self.session.open(AudioSelection, self)

    def subtitleSelection(self):
        playposition = 0
        try:
            seek = self.service and self.service.seek()
        except:
            pass

        if seek:
            playposition = seek.getPlayPosition()
        if playposition > 2000:
            subtitle = self.service and self.service.subtitle()
            subtitlelist = subtitle and subtitle.getSubtitleList()
            if self.selected_subtitle == None or self.selected_subtitle == (0, 0, 0, 0):
                if len(subtitlelist) == 0:
                    self.selected_subtitle = (0, 0, 0, 0)
                else:
                    self.selected_subtitle = (3, -1, 5, 0)
            from Screens.AudioSelection import SubtitleSelection
            self.session.open(SubtitleSelection, self)

    def getCurrentServiceSubtitle(self):
        service = self.session.nav.getCurrentService()
        return service and service.subtitle()

    def enableSubtitle(self, selectedSubtitle):
        subtitle = self.getCurrentServiceSubtitle()
        self.selected_subtitle = selectedSubtitle
        if subtitle and self.selected_subtitle:
            subtitle.enableSubtitles(self.subtitle_window.instance, self.selected_subtitle)
            self.subtitle_window.show()
        else:
            if subtitle:
                subtitle.disableSubtitles(self.subtitle_window.instance)
            self.subtitle_window.hide()

    def seekFwdInput(self):
        timesleep(instance=self)

    def seekBwdInput(self):
        timesleep(instance=self)

    def seekTotime(self):
        timesleep(instance=self)

    def seekProcess(self, pts):
        print 'test seek to time'
        if pts is not -1:
            if self.service:
                seekable = self.getSeek()
                if seekable:
                    seekable.seekTo(pts)

    def stop(self):
        self.confirmexit()

    def keyRight(self):
        timesleep(instance=self)

    def keyLeft(self):
        timesleepBack(instance=self)

    def keyOk(self):
        self.toggleShow()

    def keyCancel(self):
        self.confirmexit()

    def menu(self):
        self.session.openWithCallback(self.menuCallback, MRUAPlayer_Menu)

    def scalingmode(self):
        try:
            from Screens.VideoMode import VideoSetup
            self.session.open(VideoSetup)
        except:
            pass

    def menuCallback(self, value):
        if value == 0:
            self.seekTotime()
        if value == 1:
            self.session.openWithCallback(self.subOptionsCallback, MRUAPlayer_Suboptions2)
        elif value == 2:
            self.scalingmode()
        elif value == 3:
            self.subtitleSelection()
        elif value == 4:
            self.audioSelection()
        elif value == 5:
            self.movieInfo()
        elif value == 6:
            config.plugins.mc_mrua.repeat.value = not config.plugins.mc_mrua.repeat.value
            config.plugins.mc_mrua.repeat.save()
            if config.plugins.mc_mrua.repeat.value:
                textoinfo = _('Repeat mode ACTIVATED')
            else:
                textoinfo = _('Repeat mode DEACTIVATED')
            self.session.open(scrInformation, texto=textoinfo, segundos=2, mostrarSegundos=False)

    def movieInfo(self):
        from AZ_MRUAvideoinfo import VideoInfoMain
        VideoInfoMain(self.session, reference=self.ref)

    def subOptionsCallback(self, value):
        if value == 1:
            self.saved_config_subenc = config.plugins.mc_mrua.subenc.value
            self.saved_config_subpos = config.plugins.mc_mrua.subpos.value
            self.saved_config_subcolorname = config.plugins.mc_mrua.subcolorname.value
            self.saved_config_subcolor = config.plugins.mc_mrua.subcolor.value
            self.saved_config_subsize = config.plugins.mc_mrua.subsize.value
            self.saved_config_subdelay = config.plugins.mc_mrua.subdelay.value
            config.plugins.mc_mrua.save()
            configfile.save()

    def Start(self):
        print 'Mrua Starting Playback', self.ref
        if len(self.listado) > 0:
            self.ref = self.listado[self.contador]
            if not fileExists(self.ref):
                Notifications.AddPopup(text=_('Verify playlist. Press [MENU]') + '\n' + _('File not exists!') + ':\n' + self.listado[self.contador], type=MessageBox.TYPE_ERROR, timeout=8, id='azmruaplayer')
                return
        if self.ref is None:
            self.exit()
        else:
            newref = eServiceReference(4370, 0, self.ref)
            print 'play', newref.toString()
            name = str(self.ref)
            try:
                name = name.decode('utf-8').encode('utf-8')
            except:
                try:
                    name = name.decode('windows-1252').encode('utf-8')
                except:
                    pass

            try:
                self.cur_service = newref
            except:
                pass

            self['chapterLabel'].setText(name)
            self.session.nav.playService(newref)
            self.service = self.session.nav.getCurrentService()
            print 'self.service', self.service
            print 'cur_dlg', self.session.current_dialog

    def confirmexit(self):
        laref = _('Stop play and exit to list movie?')
        try:
            dei = self.session.openWithCallback(self.callbackexit, MessageBox, laref, MessageBox.TYPE_YESNO)
            dei.setTitle(_('Stop play'))
        except:
            self.exit()

    def callbackexit(self, respuesta):
        if respuesta:
            self.exit()

    def exit2(self):
        if self.service:
            self.session.nav.stopService()
            self.service = None
        self.close(True)

    def exit(self):
        if self.service:
            setResumePoint(self.session)
            self.session.nav.stopService()
            self.service = None
        self.repetir = False
        self.close(None)

    def __onClose(self):
        hdparm = os.popen('killall rmfp_player')
        open('/proc/player', 'w').write('1')
        self.restore_infobar_seek_config()

    def createSummary(self):
        return MRUASummary

    def playLastCB(self, answer):
        print 'playLastCB', answer, self.resume_point
        if self.service:
            if answer == True:
                seekable = self.getSeek()
                if seekable:
                    seekable.seekTo(self.resume_point)
        self.hideAfterResume()

    def showAfterCuesheetOperation(self):
        if not self.in_menu:
            self.show()

    def doEofInternal(self, playing):
        pass

    def calcRemainingTime(self):
        return 0

    def hotplugCB(self, dev, media_state):
        print '[hotplugCB]', dev, media_state
        if dev == harddiskmanager.getCD():
            if media_state == '1':
                self.scanHotplug()
            else:
                self.physicalDVD = False

    def scanHotplug(self):
        devicepath = harddiskmanager.getAutofsMountpoint(harddiskmanager.getCD())
        if pathExists(devicepath):
            from Components.Scanner import scanDevice
            res = scanDevice(devicepath)
            list = [ (r.description,
             r,
             res[r],
             self.session) for r in res ]
            if list:
                desc, scanner, files, session = list[0]
                for file in files:
                    print file
                    if file.mimetype == 'video/x-dvd':
                        print 'physical dvd found:', devicepath
                        self.physicalDVD = True
                        return

        self.physicalDVD = False


from Components.MultiContent import MultiContentEntryText
from enigma import eListboxPythonMultiContent, eServiceCenter, gFont
from Tools.LoadPixmap import LoadPixmap

class IniciaSelListMC(MenuList):

    def __init__(self, list, enableWrapAround = False):
        MenuList.__init__(self, list, enableWrapAround, eListboxPythonMultiContent)
        self.l.setItemHeight(30)
        self.l.setFont(0, gFont('Regular', 19))
        self.l.setFont(1, gFont('Regular', 17))


def IniciaSelListEntryMC(texto, imagen = 'na'):
    res = [texto]
    res.append(MultiContentEntryText(pos=(42, 4), size=(1000, 30), font=0, text=texto))
    carpetaimg = '/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/images/'
    png = '' + carpetaimg + 'MC_vo' + imagen + '-fs8.png'
    if not fileExists(png):
        png = carpetaimg + 'MC_vona-fs8.png'
    if fileExists(png):
        fpng = LoadPixmap(png)
        res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND,
         2,
         2,
         35,
         25,
         fpng))
    return res


class MRUAPlayer_Menu(Screen):
    skin = '\n\t<screen name="MRUAPlayer_Menu" position="30,55" size="350,240" title="%s" >\n\t<widget name="pathlabel" transparent="1" zPosition="2" position="0,220" size="380,20" font="Regular;16" />\n\t<widget name="list" zPosition="5" transparent="1" position="10,10" size="330,200" scrollbarMode="showOnDemand" />\n\t</screen>' % _('VideoPlayer - Menu')

    def __init__(self, session):
        Screen.__init__(self, session)
        self['list'] = IniciaSelListMC([])
        self.list = []
        self.list.append(_('Go to position'))
        self.list.append(_('Subtitle Options'))
        self.list.append(_('Scaling mode'))
        self.list.append(_('Subtitle Selection'))
        self.list.append(_('Audio Selection'))
        self.list.append(_('Movie Information'))
        valorrepeat = config.plugins.mc_mrua.repeat.value
        if valorrepeat:
            txtr = _('Repeat') + '(' + _('Yes') + ')'
        else:
            txtr = _('Repeat') + '(' + _('No') + ')'
        self.list.append(txtr)
        self['pathlabel'] = Label(_('Select option'))
        self['actions'] = ActionMap(['OkCancelActions', 'ColorActions'], {'yellow': self.setaudio,
         'red': self.setsubtitle,
         'cancel': self.Exit,
         'ok': self.okbuttonClick}, -1)
        self.onLayoutFinish.append(self.buildList)

    def buildList(self):
        list = []
        for i in range(0, len(self.list)):
            texto = '' + self.list[i]
            list.append(IniciaSelListEntryMC(texto, str(i)))

        self['list'].setList(list)

    def setaudio(self):
        self.close(2)

    def setsubtitle(self):
        self.close(3)

    def okbuttonClick(self):
        selection = self['list'].getSelectionIndex()
        self.close(selection)

    def Exit(self):
        self.close(None)


class MRUAPlayer_Suboptions2(Screen):
    skin = '\n\t<screen name="MRUAPlayer_Suboptions2" position="30,55" size="600,250" title="%s" >\n\t<widget name="list" zPosition="2" transparent="1" position="10,10" size="600,250" scrollbarMode="showOnDemand" />\n\t<widget name="sizeval" position="300,10" zPosition="3" size="250,40" font="Regular;20" valign="top" halign="left" transparent="1" />\n\t<widget name="posval" position="300,40" zPosition="3" size="250,40" font="Regular;20" valign="top" halign="left" transparent="1" />\n\t<widget name="colorval" position="300,70" zPosition="3" size="250,40" font="Regular;20" valign="top" halign="left" transparent="1" />\n\t<widget name="encval" position="300,100" zPosition="3" size="250,40" font="Regular;20" valign="top" halign="left" transparent="1" />\n\t<widget name="delayval" position="300,130" zPosition="3" size="250,40" font="Regular;20" valign="top" halign="left" transparent="1" />\n\t<widget name="note" position="0,170" zPosition="3" size="600,30" font="Regular;18" valign="top" halign="center" transparent="1" />\n\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/skins/default/images/icons/key-red.png" position="400,210" zPosition="2" size="150,30" transparent="1" alphatest="on" />\n\t<widget name="key_red" position="400,210" zPosition="3" size="150,30" font="Regular;16" valign="center" halign="center" transparent="1" />\n\t</screen>' % _('VideoPlayer - Menu')

    def __init__(self, session):
        Screen.__init__(self, session)
        self.save = False
        self['sizeval'] = Label()
        self['posval'] = Label()
        self['colorval'] = Label()
        self['encval'] = Label()
        self['delayval'] = Label()
        self['note'] = Label()
        self['key_red'] = Button('Save as Defaults')
        self['list'] = IniciaSelListMC([])
        self.list = []
        self.list.append(_('Subtitle Size'))
        self.list.append(_('Subtitle Position'))
        self.list.append(_('Subtitle Color'))
        self.list.append(_('Subtitle Encoding'))
        self.list.append(_('Subtitle Delay (in seconds)'))
        self.colorindex = -1
        self.colorcount = -1
        self.colors = [_('Black'),
         _('White'),
         _('Yellow'),
         _('Blue'),
         _('Red'),
         _('Green'),
         _('Orange'),
         _('Blue2'),
         _('Blue3'),
         _('Pink')]
        self['actions'] = ActionMap(['MC_AudioPlayerActions'], {'cancel': self.Exit,
         'ok': self.okbuttonClick,
         'right': self.right,
         'left': self.left,
         'blue': self.setcolor,
         'red': self.Dosave}, -1)
        self.onLayoutFinish.append(self.buildList)

    def getServiceInterface(self, iface):
        service = self.session.nav.getCurrentService()
        if service:
            attr = getattr(service, iface, None)
            if callable(attr):
                return attr()

    def getInfo(self):
        info = self.getServiceInterface('info')
        infoTuple = info and info.getInfoObject(iServiceInformation.sUser + 9)
        print 'Getting Subtitle Info ', repr(infoTuple)
        if infoTuple:
            self.size = infoTuple[0]
            self.pos = infoTuple[1]
            self.color = infoTuple[2]
            self.enc = infoTuple[3]
            self.delay = infoTuple[4]
            self.enctype = infoTuple[5]
        else:
            self.size = 0
            self.pos = 0
            self.color = 0
            self.enc = 0
            self.delay = 0
            self.enctype = 0
        if self.size == 1:
            self['sizeval'].setText('%02d' % config.plugins.mc_mrua.subsize.value)
        else:
            self['sizeval'].setText('Fixed')
        if self.pos == 1:
            self['posval'].setText('%02d' % config.plugins.mc_mrua.subpos.value)
        else:
            self['posval'].setText('Fixed')
        if self.color == 1:
            self['colorval'].setText('%s' % config.plugins.mc_mrua.subcolorname.value)
            self.colorindex = self.colors.index(config.plugins.mc_mrua.subcolorname.value)
            config.plugins.mc_mrua.subcolor.value = self.colorindex
        else:
            self['colorval'].setText('Fixed')
        if self.enc == 1:
            if self.enctype == 1:
                self['encval'].setText('Latin-1')
                config.plugins.mc_mrua.subenc.value = '42'
            elif self.enctype == 2:
                self['encval'].setText('UTF-8')
                config.plugins.mc_mrua.subenc.value = '43'
            elif self.enctype == 0:
                if config.plugins.mc_mrua.subenc.value == 42:
                    self['encval'].setText('Latin-1')
                else:
                    self['encval'].setText('UTF-8')
        else:
            self['encval'].setText('Fixed')
        if self.delay == 1:
            self['delayval'].setText('%.1f' % config.plugins.mc_mrua.subdelay.value)
        else:
            self['delayval'].setText('Fixed')

    def buildList(self):
        list = []
        for i in range(0, len(self.list)):
            text = '' + self.list[i]
            list.append(SubOptionsEntryComponent(text))

        self['list'].setList(list)
        self.getInfo()
        self['note'].setText('Please use left/right keys to change settings')

    def right(self):
        selection = self['list'].getSelectionIndex()
        keys = self.getServiceInterface('keys')
        if selection == 0 and self.size == 1:
            val = config.plugins.mc_mrua.subsize.value + 5
            if val <= 90:
                config.plugins.mc_mrua.subsize.setValue(val)
                self['sizeval'].setText('%02d' % config.plugins.mc_mrua.subsize.value)
            keys.keyPressed(iServiceKeys.keyUser)
        if selection == 1 and self.pos == 1:
            val = config.plugins.mc_mrua.subpos.value + 5
            if val <= 100:
                config.plugins.mc_mrua.subpos.setValue(val)
                self['posval'].setText('%02d' % config.plugins.mc_mrua.subpos.value)
            keys.keyPressed(iServiceKeys.keyUser + 1)
        if selection == 2 and self.color == 1:
            if self.colorindex < len(self.colors) - 1:
                self.colorindex = self.colorindex + 1
            else:
                self.colorindex = 0
            config.plugins.mc_mrua.subcolor.value = self.colorindex
            config.plugins.mc_mrua.subcolorname.value = self.colors[self.colorindex]
            self['colorval'].setText('%s' % config.plugins.mc_mrua.subcolorname.value)
            keys.keyPressed(iServiceKeys.keyUser + 5)
        if selection == 3 and self.enc == 1:
            config.plugins.mc_mrua.subenc.handleKey(KEY_RIGHT)
            print config.plugins.mc_mrua.subenc.value
            if config.plugins.mc_mrua.subenc.value == '42':
                self['encval'].setText('Latin-1')
            else:
                self['encval'].setText('UTF-8')
            keys.keyPressed(iServiceKeys.keyUser + 3)
        if selection == 4 and self.delay == 1:
            val = config.plugins.mc_mrua.subdelay.value + 0.1
            if val <= 10:
                config.plugins.mc_mrua.subdelay.setValue(val)
                self['delayval'].setText('%.1f' % config.plugins.mc_mrua.subdelay.value)
            keys.keyPressed(iServiceKeys.keyUser + 4)

    def left(self):
        selection = self['list'].getSelectionIndex()
        keys = self.getServiceInterface('keys')
        if selection == 0 and self.size == 1:
            val = config.plugins.mc_mrua.subsize.value - 5
            if val >= 30:
                config.plugins.mc_mrua.subsize.setValue(val)
                self['sizeval'].setText('%02d' % config.plugins.mc_mrua.subsize.value)
            keys.keyPressed(iServiceKeys.keyUser)
        if selection == 1 and self.pos == 1:
            val = config.plugins.mc_mrua.subpos.value - 5
            if val >= 0:
                config.plugins.mc_mrua.subpos.setValue(val)
                self['posval'].setText('%02d' % config.plugins.mc_mrua.subpos.value)
            keys.keyPressed(iServiceKeys.keyUser + 1)
        if selection == 2 and self.color == 1:
            if self.colorindex > 0:
                self.colorindex = self.colorindex - 1
            else:
                self.colorindex = len(self.colors) - 1
            config.plugins.mc_mrua.subcolor.value = self.colorindex
            config.plugins.mc_mrua.subcolorname.value = self.colors[self.colorindex]
            self['colorval'].setText('%s' % config.plugins.mc_mrua.subcolorname.value)
            keys.keyPressed(iServiceKeys.keyUser + 5)
        if selection == 3 and self.enc == 1:
            config.plugins.mc_mrua.subenc.handleKey(KEY_LEFT)
            print config.plugins.mc_mrua.subenc.value
            if config.plugins.mc_mrua.subenc.value == '42':
                self['encval'].setText('Latin-1')
            else:
                self['encval'].setText('UTF-8')
            keys.keyPressed(iServiceKeys.keyUser + 3)
        if selection == 4 and self.delay == 1:
            val = config.plugins.mc_mrua.subdelay.value - 0.1
            if val >= -10:
                config.plugins.mc_mrua.subdelay.setValue(val)
                self['delayval'].setText('%.1f' % config.plugins.mc_mrua.subdelay.value)
            keys.keyPressed(iServiceKeys.keyUser + 4)

    def Dosave(self):
        print 'Saving settings as default'
        self['note'].setText('Please use left/right keys to change settings...SAVED')
        self.save = True

    def setcolor(self):
        keys = self.getServiceInterface('keys')
        keys.keyPressed(iServiceKeys.keyUser + 5)

    def okbuttonClick(self):
        self.Exit()

    def Exit(self):
        if self.save == True:
            val = 1
        else:
            val = 0
        self.close(val)


class MRUAPlayer_SubOptions(Screen):
    skin = '\n\t\t<screen position="80,80" size="600,220" title="Subtitle Options" >\n\t\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/skins/default/images/icons/key-yellow.png" position="360,30" zPosition="2" size="150,30" transparent="1" alphatest="on" />\n\t\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/skins/default/images/icons/key-blue.png" position="360,90" zPosition="2" size="150,30" transparent="1" alphatest="on" />\n\t\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/skins/default/images/icons/key-red.png" position="360,150" zPosition="2" size="150,30" transparent="1" alphatest="on" />\n\t\t\t<widget name="key_yellow" position="360,30" zPosition="3" size="150,30" font="Regular;20" valign="center" halign="center" transparent="1" />\n\t\t\t<widget name="key_blue" position="360,90" zPosition="3" size="150,30" font="Regular;20" valign="center" halign="center" transparent="1" />\n\t\t\t<widget name="key_red" position="360,150" zPosition="3" size="150,30" font="Regular;20" valign="center" halign="center" transparent="1" />\n\t\t\t<widget name="navigation" position="40,30" zPosition="3" size="200,200" font="Regular;20" valign="top" halign="left" transparent="1" />\n\t\t</screen>'

    def __init__(self, session):
        self.skin = MRUAPlayer_SubOptions.skin
        Screen.__init__(self, session)
        self['DVDPlayerPlaybackActions'] = HelpableActionMap(self, 'MC_AudioPlayerActions', {'ok': (self.close, 'Play selected file'),
         'cancel': (self.close, 'Exit Video Player'),
         'left': (self.left, 'Move left'),
         'right': (self.right, 'Move right'),
         'up': (self.up, 'Move up'),
         'down': (self.down, 'Move down'),
         'nextBouquet': (self.increase, 'Increase Size'),
         'prevBouquet': (self.decrease, 'Decrease Size'),
         'red': (self.reset, 'Reset to defaults'),
         'yellow': (self.encoding, 'Change Subtitle Encoding'),
         'blue': (self.color, 'Change Subtitle Color')}, -2)
        self['key_red'] = Button('Reset')
        self['key_yellow'] = Button('Encoding')
        self['key_blue'] = Button(_('Color'))
        self['navigation'] = Button(_('Use the navigation buttons on the remote to move the subtitles around'))
        self.service = self.session.nav.getCurrentService()

    def getServiceInterface(self, iface):
        service = self.service
        if service:
            attr = getattr(service, iface, None)
            if callable(attr):
                return attr()
            return

    def up(self):
        keys = self.getServiceInterface('keys')
        keys.keyPressed(iServiceKeys.keyUp)

    def down(self):
        keys = self.getServiceInterface('keys')
        keys.keyPressed(iServiceKeys.keyDown)

    def left(self):
        keys = self.getServiceInterface('keys')
        keys.keyPressed(iServiceKeys.keyLeft)

    def right(self):
        keys = self.getServiceInterface('keys')
        keys.keyPressed(iServiceKeys.keyRight)

    def increase(self):
        keys = self.getServiceInterface('keys')
        keys.keyPressed(iServiceKeys.keyUser)

    def decrease(self):
        keys = self.getServiceInterface('keys')
        keys.keyPressed(iServiceKeys.keyUser + 1)

    def reset(self):
        keys = self.getServiceInterface('keys')
        keys.keyPressed(iServiceKeys.keyUser + 4)

    def encoding(self):
        keys = self.getServiceInterface('keys')
        keys.keyPressed(iServiceKeys.keyUser + 2)

    def color(self):
        keys = self.getServiceInterface('keys')
        keys.keyPressed(iServiceKeys.keyUser + 3)
