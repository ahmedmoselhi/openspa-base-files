from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.ChoiceBox import ChoiceBox
from Screens.HelpMenu import HelpableScreen
from Screens.InfoBarGenerics import InfoBarSeek, InfoBarPVRState, InfoBarCueSheetSupport, InfoBarShowHide, InfoBarNotifications, InfoBarAudioSelection, InfoBarSubtitleSupport
from Components.ActionMap import ActionMap, NumberActionMap, HelpableActionMap
from Components.Label import Label
from Components.Sources.StaticText import StaticText
from Components.Pixmap import Pixmap
from Components.FileList import FileList
from Components.MenuList import MenuList
from Components.ServiceEventTracker import ServiceEventTracker, InfoBarBase
from Components.config import config
from Tools.Directories import pathExists, fileExists
from Components.Harddisk import harddiskmanager
from MC_Menus import IniciaSelListMC, IniciaSelListEntryMC
import serviceazdvd

class DVDSummary(Screen):
    skin = '\n\t\t<screen name="DVDSummary" position="0,0" size="50,64" id="3">\n\t\t\t\t<widget source="session.CurrentService" render="Label" position="0,0" size="90,25" font="Display;16" halign="center" valign="center">\n\t\t\t\t\t\t<convert type="ServicePosition">Position,ShowHours</convert>\n\t\t\t\t</widget>\n\t\t</screen>'

    def __init__(self, session, parent):
        Screen.__init__(self, session)


class DVDOverlay(Screen):

    def __init__(self, session, args = None):
        desktop_size = getDesktop(0).size()
        DVDOverlay.skin = '<screen name="DVDOverlay" position="0,0" size="%d,%d" flags="wfNoBorder" zPosition="-1" backgroundColor="transparent" />' % (desktop_size.width(), desktop_size.height())
        Screen.__init__(self, session)


class ChapterZap(Screen):
    skin = '\n\t<screen name="ChapterZap" position="235,255" size="250,60" title="Chapter" >\n\t\t<widget name="chapter" position="35,15" size="110,25" font="Regular;23" />\n\t\t<widget name="number" position="145,15" size="80,25" halign="right" font="Regular;23" />\n\t</screen>'

    def quit(self):
        self.Timer.stop()
        self.close(0)

    def keyOK(self):
        self.Timer.stop()
        self.close(int(self['number'].getText()))

    def keyNumberGlobal(self, number):
        self.Timer.start(3000, True)
        self.field = self.field + str(number)
        self['number'].setText(self.field)
        if len(self.field) >= 4:
            self.keyOK()

    def __init__(self, session, number):
        Screen.__init__(self, session)
        self.field = str(number)
        self['chapter'] = Label(_('Chapter:'))
        self['number'] = Label(self.field)
        self['actions'] = NumberActionMap(['SetupActions'], {'cancel': self.quit,
         'ok': self.keyOK,
         '1': self.keyNumberGlobal,
         '2': self.keyNumberGlobal,
         '3': self.keyNumberGlobal,
         '4': self.keyNumberGlobal,
         '5': self.keyNumberGlobal,
         '6': self.keyNumberGlobal,
         '7': self.keyNumberGlobal,
         '8': self.keyNumberGlobal,
         '9': self.keyNumberGlobal,
         '0': self.keyNumberGlobal})
        self.Timer = eTimer()
        self.Timer.callback.append(self.keyOK)
        self.Timer.start(3000, True)


class AZDVDPlayer(Screen, InfoBarBase, InfoBarNotifications, InfoBarSeek, InfoBarPVRState, InfoBarShowHide, HelpableScreen, InfoBarCueSheetSupport, InfoBarAudioSelection, InfoBarSubtitleSupport):
    ALLOW_SUSPEND = Screen.SUSPEND_PAUSES
    ENABLE_RESUME_SUPPORT = False

    def save_infobar_seek_config(self):
        self.saved_config_speeds_forward = config.seek.speeds_forward.value
        self.saved_config_speeds_backward = config.seek.speeds_backward.value
        self.saved_config_enter_forward = config.seek.enter_forward.value
        self.saved_config_enter_backward = config.seek.enter_backward.value
        self.saved_config_seek_on_pause = config.seek.on_pause.value
        self.saved_config_seek_speeds_slowmotion = config.seek.speeds_slowmotion.value

    def change_infobar_seek_config(self):
        config.seek.speeds_forward.value = [2,
         4,
         8,
         16,
         32,
         64]
        config.seek.speeds_backward.value = [8,
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

    def __init__(self, session, dvd_device = None, dvd_filelist = [], args = None):
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
        self.dvdScreen = self.session.instantiateDialog(DVDOverlay)
        self.skinName = ['AZDVDPlayer', 'DVDPlayer']
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
        AZDVDPlayer.STATE = 'NONE'
        self.__event_tracker = ServiceEventTracker(screen=self, eventmap={iPlayableService.evStopped: self.__serviceStopped,
         iPlayableService.evStart: self.__serviceStarted,
         iPlayableService.evUser + 3: self.__osdFFwdInfoAvail,
         iPlayableService.evUser + 4: self.__osdFBwdInfoAvail,
         iPlayableService.evUser + 6: self.__osdAudioInfoAvail,
         iPlayableService.evUser + 7: self.__osdSubtitleInfoAvail,
         iPlayableService.evUser + 8: self.__chapterUpdated,
         iPlayableService.evUser + 9: self.__titleUpdated,
         iPlayableService.evUser + 11: self.__menuOpened,
         iPlayableService.evUser + 12: self.__menuClosed,
         iPlayableService.evUser + 13: self.__osdAngleInfoAvail})
        self['DVDPlayerDirectionActions'] = ActionMap(['DirectionActions'], {'left': self.keyLeft,
         'right': self.keyRight,
         'up': self.keyUp,
         'down': self.keyDown,
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
        self['DVDPlayerPlaybackActions'] = HelpableActionMap(self, 'AZDVDPlayerActions', {'stop': (self.stop, _('exit DVD player')),
         'toggleInfo': (self.toggleInfo, _('toggle time, chapter, audio, subtitle info')),
         'dvdMenu': (self.menu, _('show DVD main menu')),
         'nextChapter': (self.nextChapter, _('forward to the next chapter')),
         'prevChapter': (self.prevChapter, _('rewind to the previous chapter')),
         'nextTitle': (self.nextTitle, _('jump forward to the next title')),
         'prevTitle': (self.prevTitle, _('jump back to the previous title')),
         'nextAudioTrack': (self.nextAudioTrack, _('switch to the next audio track')),
         'SubtitleSelection': (self.subtitleSelection, _('switch to the next subtitle language')),
         'nextSubtitleTrack': (self.nextSubtitleTrack, _('switch to the next subtitle language')),
         'nextAngle': (self.nextAngle, _('switch to the next angle')),
         'seekBeginning': self.seekBeginning,
         'pause': (self.playpauseService, _('Pause / Resume')),
         'seekFwd': (self.seekFwd, _('Seek forward')),
         'seekBwd': (self.seekBack, _('Seek backward')),
         'AudioSelection': (self.audioSelection, _('Select audio track'))}, -2)
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
        popen('killall dvd_player')
        open('/proc/player', 'w').write('2')
        self.onClose.append(self.__onClose)
        from Plugins.SystemPlugins.Hotplug.plugin import hotplugNotifier
        hotplugNotifier.append(self.hotplugCB)
        self.autoplay = dvd_device or dvd_filelist
        if dvd_device:
            self.physicalDVD = True
        else:
            self.scanHotplug()
        self.dvd_filelist = dvd_filelist
        self.onFirstExecBegin.append(self.opened)
        self.service = None
        self.in_menu = False

    def __serviceStopped(self):
        self.exit()

    def __serviceStarted(self):
        self['SeekActions'].setEnabled(False)

    def serviceStarted(self):
        self.dvdScreen.show()

    def __menuOpened(self):
        self.hide()
        self.in_menu = True
        self['NumberActions'].setEnabled(False)

    def __menuClosed(self):
        self.show()
        self.in_menu = False
        self['NumberActions'].setEnabled(True)

    def __osdFFwdInfoAvail(self):
        self.setChapterLabel()
        print 'FFwdInfoAvail'

    def __osdFBwdInfoAvail(self):
        self.setChapterLabel()
        print 'FBwdInfoAvail'

    def __osdAudioInfoAvail(self):
        info = self.getServiceInterface('info')
        audioTuple = info and info.getInfoObject(iServiceInformation.sUser + 6)
        print 'AudioInfoAvail ', repr(audioTuple)
        if audioTuple:
            audioString = '%d: %s (%s)' % (audioTuple[0], audioTuple[1], audioTuple[2])
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

    def __osdAngleInfoAvail(self):
        info = self.getServiceInterface('info')
        angleTuple = info and info.getInfoObject(iServiceInformation.sUser + 8)
        print 'AngleInfoAvail ', repr(angleTuple)
        if angleTuple:
            angleString = ''
            if angleTuple[1] > 1:
                angleString = '%d / %d' % (angleTuple[0], angleTuple[1])
                self['anglePix'].show()
            else:
                self['anglePix'].hide()
            self['angleLabel'].setText(angleString)
            if angleTuple != self.last_angleTuple and not self.in_menu:
                self.doShow()
        self.last_angleTuple = angleTuple

    def __chapterUpdated(self):
        info = self.getServiceInterface('info')
        if info:
            self.currentChapter = info.getInfo(iServiceInformation.sCurrentChapter)
            self.totalChapters = info.getInfo(iServiceInformation.sTotalChapters)
            self.setChapterLabel()
            print '__chapterUpdated: %d/%d' % (self.currentChapter, self.totalChapters)

    def __titleUpdated(self):
        info = self.getServiceInterface('info')
        if info:
            self.currentTitle = info.getInfo(iServiceInformation.sCurrentTitle)
            self.totalTitles = info.getInfo(iServiceInformation.sTotalTitles)
            self.setChapterLabel()
            print '__titleUpdated: %d/%d' % (self.currentTitle, self.totalTitles)
            if not self.in_menu:
                self.doShow()

    def __onClose(self):
        self.restore_infobar_seek_config()
        self.session.nav.playService(self.oldService)
        hdparm = popen('killall dvd_player')
        open('/proc/player', 'w').write('1')
        from Plugins.SystemPlugins.Hotplug.plugin import hotplugNotifier
        hotplugNotifier.remove(self.hotplugCB)

    def opened(self):
        if self.autoplay and self.dvd_filelist:
            self.FileBrowserClosed(self.dvd_filelist[0])
        elif self.autoplay and self.physicalDVD:
            self.playPhysicalCB(True)

    def playPhysicalCB(self, answer):
        if answer == True:
            self.FileBrowserClosed(harddiskmanager.getAutofsMountpoint(harddiskmanager.getCD()))
        else:
            self.session.openWithCallback(self.FileBrowserClosed, FileBrowser)

    def FileBrowserClosed(self, val):
        curref = self.session.nav.getCurrentlyPlayingServiceReference()
        print 'FileBrowserClosed', val
        if val is None:
            self.exit()
        else:
            newref = eServiceReference(4371, 0, val)
            print 'play', newref.toString()
            if curref is None or curref != newref:
                if newref.toString().endswith('/VIDEO_TS') or newref.toString().endswith('/'):
                    names = newref.toString().rsplit('/', 3)
                    if names[2].startswith('Disk ') or names[2].startswith('DVD '):
                        name = str(names[1]) + ' - ' + str(names[2])
                    else:
                        name = names[2]
                    print 'setting name to: ', str(name)
                    newref.setName(str(name))
                AZDVDPlayer.STATE = 'PLAY'
                self.session.nav.playService(newref)
                self.service = self.session.nav.getCurrentService()
                print 'self.service', self.service
                print 'cur_dlg', self.session.current_dialog

    def createSummary(self):
        return DVDSummary

    def doNothing(self):
        pass

    def getServiceInterface(self, iface):
        service = self.service
        if service:
            attr = getattr(service, iface, None)
            if callable(attr):
                return attr()

    def doEofInternal(self, playing):
        if self.in_menu:
            self.hide()

    def setChapterLabel(self):
        chapterLCD = 'Menu'
        chapterOSD = 'DVD Menu'
        if self.currentTitle > 0:
            chapterLCD = '%s %d' % (_('Chap.'), self.currentChapter)
            chapterOSD = 'DVD %s %d/%d' % (_('Chapter'), self.currentChapter, self.totalChapters)
            chapterOSD += ' (%s %d/%d)' % (_('Title'), self.currentTitle, self.totalTitles)
        self['chapterLabel'].setText(chapterOSD)

    def stop(self):
        self.exit()

    def exit(self):
        if self.service:
            self.session.nav.stopService()
            self.service = None
        self.close()

    def toggleInfo(self):
        if not self.in_menu:
            self.toggleShow()
            print 'toggleInfo'

    def seekBeginning(self):
        if self.service:
            seekable = self.getSeek()
            if seekable:
                seekable.seekTo(0)

    def keyNumberGlobal(self, number):
        print 'You pressed number ' + str(number)
        self.session.openWithCallback(self.numberEntered, ChapterZap, number)

    def numberEntered(self, retval):
        if retval > 0:
            self.zapToNumber(retval)

    def zapToNumber(self, number):
        if self.service:
            seekable = self.getSeek()
            if seekable:
                print 'seek to chapter %d' % number
                seekable.seekChapter(number)

    def menu(self):
        self.session.openWithCallback(self.menuCallback, AZDVDPlayer_Menu)

    def menuCallback(self, value):
        if value == 0:
            self.enterTitleMenu()
        elif value == 1:
            self.enterRootMenu()
        elif value == 2:
            self.enterDVDAudioMenu()
        elif value == 3:
            self.session.openWithCallback(self.numberEntered, ChapterZap, 0)
        elif value == 4:
            self.subtitleSelection()
        elif value == 5:
            self.audioSelection()

    def sendKey(self, key):
        keys = self.getServiceInterface('keys')
        if keys:
            keys.keyPressed(key)
        return keys

    def nextAudioTrack(self):
        self.sendKey(iServiceKeys.keyUser)

    def subtitleSelection(self):
        from Screens.AudioSelection import SubtitleSelection
        self.session.open(SubtitleSelection, self)

    def nextSubtitleTrack(self):
        self.sendKey(iServiceKeys.keyUser + 1)

    def enterDVDAudioMenu(self):
        self.sendKey(iServiceKeys.keyUser + 2)

    def nextChapter(self):
        self.sendKey(iServiceKeys.keyUser + 3)

    def prevChapter(self):
        self.sendKey(iServiceKeys.keyUser + 4)

    def nextTitle(self):
        self.sendKey(iServiceKeys.keyUser + 5)

    def prevTitle(self):
        self.sendKey(iServiceKeys.keyUser + 6)

    def enterRootMenu(self):
        self.sendKey(iServiceKeys.keyUser + 7)

    def enterTitleMenu(self):
        self.sendKey(iServiceKeys.keyUser + 8)

    def nextAngle(self):
        self.sendKey(iServiceKeys.keyUser + 9)

    def keyRight(self):
        self.sendKey(iServiceKeys.keyRight)

    def keyLeft(self):
        self.sendKey(iServiceKeys.keyLeft)

    def keyUp(self):
        self.sendKey(iServiceKeys.keyUp)

    def keyDown(self):
        self.sendKey(iServiceKeys.keyDown)

    def keyOk(self):
        if self.sendKey(iServiceKeys.keyOk) and not self.in_menu:
            self.toggleInfo()

    def keyCancel(self):
        self.exit()

    def playLastCB(self, answer):
        print 'playLastCB', answer, self.resume_point
        if self.service:
            if answer == True:
                seekable = self.getSeek()
                if seekable:
                    seekable.seekTo(self.resume_point)
            pause = self.service.pause()
            pause.unpause()
        self.hideAfterResume()

    def showAfterCuesheetOperation(self):
        if not self.in_menu:
            self.show()

    def doEof(self):
        self.setSeekState(self.SEEK_STATE_PLAY)

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


class AZDVDPlayer_Menu(Screen):
    skin = '\n\t\t<screen name="AZDVDPlayer_Menu" position="30,55" size="350,240" title="%s" >\n\t\t<widget name="pathlabel" transparent="1" zPosition="2" position="0,170" size="380,20" font="Regular;16" />\n\t\t<widget name="list" zPosition="5" transparent="1" position="10,10" size="330,200" scrollbarMode="showOnDemand" />\n\t\t</screen>' % _('DVDPlayer - Menu')

    def __init__(self, session):
        Screen.__init__(self, session)
        self['list'] = IniciaSelListMC([])
        self.list = []
        self.list.append(_('Go to Title Menu'))
        self.list.append(_('Go to Root Menu'))
        self.list.append(_('Go to Audio Menu'))
        self.list.append(_('Go to Chapter'))
        self.list.append(_('Subtitle Selection'))
        self.list.append(_('Audio Selection'))
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
