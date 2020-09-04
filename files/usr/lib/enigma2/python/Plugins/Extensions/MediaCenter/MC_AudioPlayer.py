from Components.MenuList import MenuList
from Components.GUIComponent import GUIComponent
from Components.MultiContent import MultiContentEntryText
from Screens.Screen import Screen
from Screens.ServiceInfo import ServiceInfoList, ServiceInfoListEntry
from Components.ActionMap import ActionMap, NumberActionMap, HelpableActionMap
from Components.Pixmap import Pixmap, MovingPixmap
from Components.Label import Label
from Screens.ChoiceBox import ChoiceBox
from Screens.InputBox import InputBox
from Tools.LoadPixmap import LoadPixmap
from ServiceReference import ServiceReference
from Components.Button import Button
from Components.Sources.StaticText import StaticText
from Components.Sources.List import List
from Screens.MessageBox import MessageBox
from Screens.HelpMenu import HelpableScreen
from Components.ServicePosition import ServicePositionGauge
from Components.ServiceEventTracker import ServiceEventTracker
from Components.Playlist import PlaylistIOInternal, PlaylistIOM3U, PlaylistIOPLS
from Components.ConfigList import ConfigList, ConfigListScreen
from Components.config import *
from Tools.Directories import resolveFilename, fileExists, pathExists, createDir, SCOPE_MEDIA, SCOPE_PLAYLIST, SCOPE_SKIN_IMAGE
from Screens.InfoBar import MoviePlayer
from Plugins.Plugin import PluginDescriptor
from MC_Filelist import FileList
import os
from random import randint
from os import path as os_path, remove as os_remove, listdir as os_listdir
from enigma import eListboxPythonStringContent, eListbox
from enigma import ePicLoad
from Components.AVSwitch import AVSwitch
from Components.Label import Label
import MP3Info
from os import environ
import gettext
from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE
lang = language.getLanguage()
environ['LANGUAGE'] = lang[:2]
gettext.bindtextdomain('enigma2', resolveFilename(SCOPE_LANGUAGE))
gettext.textdomain('enigma2')
gettext.bindtextdomain('MC_AudioPlayer', '%s%s' % (resolveFilename(SCOPE_PLUGINS), 'Extensions/MediaCenter/locale/'))

def _(txt):
    t = gettext.dgettext('MC_AudioPlayer', txt)
    if t == txt:
        t = gettext.gettext(txt)
    return t


config.plugins.mc_ap = ConfigSubsection()
config.plugins.mc_ap.showMvi = ConfigYesNo(default=True)
config.plugins.mc_ap.mvi_delay = ConfigInteger(default=10, limits=(5, 999))
config.plugins.mc_ap.showPreview = ConfigYesNo(default=False)
config.plugins.mc_ap.preview_delay = ConfigInteger(default=5, limits=(1, 30))
config.plugins.mc_ap.lastDir = ConfigText(default='mountpoint')
playlist = []

def getAspect():
    val = AVSwitch().getAspectRatioSetting()
    return val / 2


def PlaylistEntryComponent(serviceref, current):
    res = [serviceref]
    text = serviceref.getName()
    if text is '':
        text = os_path.split(serviceref.getPath().split('/')[-1])[1]
    try:
        text = text.decode('utf-8').encode('utf-8')
    except:
        try:
            text = text.decode('windows-1252').encode('utf-8')
        except:
            pass

    filename = serviceref.getPath()
    title = None
    year = None
    genre = None
    artist = None
    album = None
    duration = None
    try:
        id3r = MP3Info.MP3Info(open(filename, 'rb'))
        title = id3r.title
        artist = id3r.artist
        album = id3r.album
        year = id3r.year
        genre = id3r.genre
        duration = '%d:%02d' % (id3r.mpeg.length_minutes, id3r.mpeg.length_seconds)
    except:
        pass

    if title == None or title == '':
        title = text
    if artist == None:
        artist = ''
    if album == None:
        album = ''
    if year == None:
        year = ''
    else:
        year = ' - ' + year
    if genre == None:
        genre = ''
    if duration == None:
        duration = ''
    res.append(MultiContentEntryText(pos=(50, 5), size=(690, 50), font=0, text='' + title + ''))
    rutapng = '/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/images/'
    png = LoadPixmap(cached=True, path=rutapng + 'mc_music-fs8.png')
    res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND,
     11,
     9,
     32,
     32,
     png))
    res.append(MultiContentEntryText(pos=(58, 25), size=(690, 40), font=1, flags=RT_HALIGN_LEFT, text='' + str(artist) + ' [' + str(album) + str(year) + ']', color=8947848))
    res.append(MultiContentEntryText(pos=(785, 5), size=(120, 40), font=0, flags=RT_HALIGN_RIGHT, text='' + duration + ' '))
    res.append(MultiContentEntryText(pos=(785, 25), size=(120, 40), font=1, flags=RT_HALIGN_RIGHT, text='' + str(genre) + '', color=8947848))
    if current == serviceref.getPath():
        png = LoadPixmap(cached=True, path=rutapng + 'au_play.png')
        res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND,
         30,
         20,
         20,
         20,
         png))
    return res


class PlayList(MenuList):

    def __init__(self, enableWrapAround = False):
        MenuList.__init__(self, playlist, enableWrapAround, eListboxPythonMultiContent)
        self.l.setFont(0, gFont('Regular', 19))
        self.l.setFont(1, gFont('Regular', 18))
        self.l.setFont(2, gFont('Regular', 20))
        self.l.setItemHeight(50)
        MC_AudioPlayer.currPlaying = -1
        self.oldCurrPlaying = -1
        self.serviceHandler = eServiceCenter.getInstance()
        self.current = None
        self.playname = None

    def setName(self, name):
        self.playname = name

    def getName(self):
        return str(self.playname)

    def clear(self):
        del self.list[:]
        self.l.setList(self.list)
        MC_AudioPlayer.currPlaying = -1
        self.oldCurrPlaying = -1

    def refresh(self):
        lista = self.getServiceRefList()
        self.list = []
        for x in lista:
            self.addFile(x)

        self.updateList()

    def getSelection(self):
        return self.l.getCurrentSelection()[0]

    def addFile(self, serviceref):
        self.list.append(PlaylistEntryComponent(serviceref, self.current))

    def updateFile(self, index, newserviceref):
        if index < len(self.list):
            self.list[index] = PlaylistEntryComponent(newserviceref, STATE_NONE)

    def deleteFile(self, index):
        if MC_AudioPlayer.currPlaying >= index:
            MC_AudioPlayer.currPlaying -= 1
        del self.list[index]

    def setCurrentPlaying(self, index):
        self.oldCurrPlaying = MC_AudioPlayer.currPlaying
        MC_AudioPlayer.currPlaying = index
        if index > -1:
            self.current = self.getServiceRefList()[self.getCurrentIndex()].getPath()
            self.refresh()
            self.moveToIndex(index)
        else:
            self.current = None
            self.refresh()

    def updateState(self, state):
        if len(self.list) > self.oldCurrPlaying and self.oldCurrPlaying != -1:
            self.list[self.oldCurrPlaying] = PlaylistEntryComponent(self.list[self.oldCurrPlaying][0], STATE_NONE)
        if MC_AudioPlayer.currPlaying != -1 and MC_AudioPlayer.currPlaying < len(self.list):
            self.list[MC_AudioPlayer.currPlaying] = PlaylistEntryComponent(self.list[MC_AudioPlayer.currPlaying][0], state)
        self.updateList()

    def playFile(self):
        self.updateState(STATE_PLAY)

    def pauseFile(self):
        self.updateState(STATE_PAUSE)

    def stopFile(self):
        self.updateState(STATE_STOP)
        self.current = None
        self.refresh()

    def rewindFile(self):
        self.updateState(STATE_REWIND)

    def forwardFile(self):
        self.updateState(STATE_FORWARD)

    GUI_WIDGET = eListbox

    def updateList(self):
        self.l.setList(self.list)

    def getCurrentIndex(self):
        return MC_AudioPlayer.currPlaying

    def getCurrentEvent(self):
        l = self.l.getCurrentSelection()
        return l and self.serviceHandler.info(l[0]).getEvent(l[0])

    def getCurrent(self):
        l = self.l.getCurrentSelection()
        return l and l[0]

    def getServiceRefList(self):
        return [ x[0] for x in self.list ]

    def __len__(self):
        return len(self.list)


class MC_AudioPlayer(Screen, HelpableScreen):

    def __init__(self, session, ruta_inicio = None):
        Screen.__init__(self, session)
        HelpableScreen.__init__(self)
        self.isVisible = True
        self.oldService = self.session.nav.getCurrentlyPlayingServiceOrGroup()
        self.session.nav.stopService()
        from Tools.HardwareInfo import HardwareInfo
        box = HardwareInfo().get_device_name()
        if not box.startswith('spark'):
            os.system('/usr/bin/showiframe /usr/share/enigma2/black.mvi &')
        self.coverArtFileName = ''
        self.playlist = PlayList()
        self['playlist'] = self.playlist
        self['key_red'] = Button(_('Home'))
        self['key_green'] = Button(_('Play All'))
        self['key_yellow'] = Button(_('Add to Playlist'))
        self['key_blue'] = Button(_('Playlist') + ' (%d)' % self.playlist.__len__())
        self['fileinfo'] = Label()
        self['currentfolder'] = Label()
        self['play'] = Pixmap()
        self['stop'] = Pixmap()
        self['curplayingtitle'] = Label()
        self.PlaySingle = 0
        MC_AudioPlayer.STATE = 'NONE'
        MC_AudioPlayer.playlistplay = 0
        MC_AudioPlayer.currPlaying = -1
        self.__event_tracker = ServiceEventTracker(screen=self, eventmap={iPlayableService.evEOF: self.doEOF,
         iPlayableService.evStopped: self.doEOF,
         iPlayableService.evUser + 11: self.__evDecodeError,
         iPlayableService.evUser + 12: self.__evPluginError})
        self['actions'] = HelpableActionMap(self, 'MC_AudioPlayerActions', {'ok': (self.KeyOK, 'Play selected file'),
         'cancel': (self.Exit, 'Exit Audio Player'),
         'left': (self.leftUp, 'List Top'),
         'right': (self.rightDown, 'List Bottom'),
         'up': (self.up, 'List up'),
         'down': (self.down, 'List down'),
         'menu': (self.showMenu, 'File / Folder Options'),
         'video': (self.visibility, 'Show / Hide Player'),
         'info': (self.showFileInfo, 'Show File Info'),
         'stop': (self.StopPlayback, 'Stop Playback'),
         'red': (self.Exit, 'Exit Music'),
         'green': (self.KeyPlayAll, 'Play All'),
         'yellow': (self.addFiletoPls, 'Add file to playlist'),
         'blue': (self.Playlists, 'Playlists'),
         'next': (self.KeyNext, 'Next song'),
         'previous': (self.KeyPrevious, 'Previous song'),
         'playpause': (self.PlayPause, 'Play / Pause'),
         'stop': (self.StopPlayback, 'Stop')}, -2)
        self.playlistparsers = {}
        self.addPlaylistParser(PlaylistIOM3U, 'm3u')
        self.addPlaylistParser(PlaylistIOPLS, 'pls')
        self.addPlaylistParser(PlaylistIOInternal, 'e2pls')
        self['title'] = Label()
        self['artist'] = Label()
        self['album'] = Label()
        self['year'] = Label()
        self['genre'] = Label()
        self['duration'] = Label()
        self['bitrate'] = Label()
        self['mode'] = Label()
        self['coverArt'] = Pixmap()
        self.picload = ePicLoad()
        self.picload.PictureData.get().append(self.paintPoster)
        self.Timer = eTimer()
        self.Timer.callback.append(self.showpic)
        self.pic = None
        self.oldpic = None
        MC_AudioPlayer.PLAYLISTNAME = None
        self.onLayoutFinish.append(self.deleteinfo)
        if not os.path.exists('/media/MediaServers'):
            os.system('mkdir -p /media/MediaServers')
        try:
            os.system('modprobe fuse')
            os.system('djmount -o allow_other -o iocharset=utf8 /media/MediaServers')
        except:
            pass

        import time
        time.sleep(3)
        if ruta_inicio == None:
            currDir = config.plugins.mc_ap.lastDir.value
        else:
            currDir = ruta_inicio
        if not pathExists(currDir):
            currDir = None
        self['currentfolder'].setText(str(currDir))
        self.filelist = FileList(currDir, showMountpoints=True, useServiceRef=False, showDirectories=True, showFiles=True, matchingPattern='(?i)^.*\\.(mp3|ogg|wav|wave|flac|m4a|m3u|pls|e2pls)', additionalExtensions='4098:m3u 4098:e2pls 4098:pls')
        self['filelist'] = self.filelist
        self['filelist'].onSelectionChanged.append(self.SelectionChanged)

    def SelectionChanged(self):
        if self['filelist'].canDescent():
            self['key_green'].hide()
            self['key_yellow'].hide()
        else:
            self['key_green'].show()
            self['key_yellow'].show()

    def up(self):
        self['filelist'].up()

    def down(self):
        self['filelist'].down()

    def leftUp(self):
        self['filelist'].pageUp()

    def rightDown(self):
        self['filelist'].pageDown()

    def KeyOK(self):
        if self['filelist'].canDescent():
            self.filelist.descent()
            self['currentfolder'].setText(str(self.filelist.getCurrentDirectory()))
        elif self.filelist.getServiceRef().type == 4098:
            ServiceRef = self.filelist.getServiceRef()
            extension = ServiceRef.getPath()[ServiceRef.getPath().rfind('.') + 1:]
            if self.playlistparsers.has_key(extension):
                self.playlist.clear()
                playlist = self.playlistparsers[extension]()
                list = playlist.open(ServiceRef.getPath())
                for x in list:
                    self.playlist.addFile(x.ref)

            self.playlist.updateList()
            MC_AudioPlayer.currPlaying = 0
            name = ServiceRef.getPath().split('/')[-1]
            name = name[:name.rfind('.')]
            MC_AudioPlayer.PLAYLISTNAME = name
            self.session.openWithCallback(self.updatedata, MC_AudioPlaylist, Auto=True)
        else:
            self.PlaySingle = 1
            self.PlayService()

    def updatedata(self, plist):
        self.playlist.clear()
        for x in plist:
            self.playlist.addFile(x)

        self['key_blue'].setText(_('Playlist') + ' (%d)' % self.playlist.__len__())

    def PlayPause(self):
        if MC_AudioPlayer.STATE == 'PLAY':
            service = self.session.nav.getCurrentService()
            pausable = service.pause()
            pausable.pause()
            MC_AudioPlayer.STATE = 'PAUSED'
        elif MC_AudioPlayer.STATE == 'PAUSED' or MC_AudioPlayer.STATE == 'SEEKBWD' or MC_AudioPlayer.STATE == 'SEEKFWD':
            service = self.session.nav.getCurrentService()
            pausable = service.pause()
            pausable.unpause()
            MC_AudioPlayer.STATE = 'PLAY'
        else:
            self.KeyOK()

    def seekFwd(self):
        if MC_AudioPlayer.STATE == 'PLAY' or MC_AudioPlayer.STATE == 'SEEKBWD':
            service = self.session.nav.getCurrentService()
            pausable = service.pause()
            pausable.setFastForward(4)
            MC_AudioPlayer.STATE = 'SEEKFWD'

    def seekBwd(self):
        if MC_AudioPlayer.STATE == 'PLAY' or MC_AudioPlayer.STATE == 'SEEKFWD':
            service = self.session.nav.getCurrentService()
            pausable = service.pause()
            pausable.setFastForward(-4)
            MC_AudioPlayer.STATE = 'SEEKBWD'

    def KeyNext(self):
        if MC_AudioPlayer.STATE != 'NONE':
            if MC_AudioPlayer.playlistplay == 1:
                next = self.playlist.getCurrentIndex() + 1
                if next < len(self.playlist):
                    MC_AudioPlayer.currPlaying = MC_AudioPlayer.currPlaying + 1
                else:
                    MC_AudioPlayer.currPlaying = 0
                self.PlayServicepls()
            else:
                print 'Play Next File ...'
                self.down()
                self.PlayService()

    def KeyPrevious(self):
        if MC_AudioPlayer.STATE != 'NONE':
            if MC_AudioPlayer.playlistplay == 1:
                next = self.playlist.getCurrentIndex() - 1
                if next != -1:
                    MC_AudioPlayer.currPlaying = MC_AudioPlayer.currPlaying - 1
                else:
                    MC_AudioPlayer.currPlaying = 0
                self.PlayServicepls()
            else:
                print 'Play previous File ...'
                self.up()
                self.PlayService()

    def KeyPlayAll(self):
        if not self['filelist'].canDescent():
            self.PlaySingle = 0
            self.PlayService()

    def KeyExit(self):
        self.filelist.gotoParent()

    def KeyYellow(self):
        print 'yellow'

    def visibility(self, force = 1):
        if self.isVisible == True:
            self.isVisible = False
            self.hide()
        else:
            self.isVisible = True
            self.show()

    def Playlists(self):
        self.StopPlayback()
        self.session.openWithCallback(self.updatedata, MC_AudioPlaylist)

    def deleteinfo(self):
        self['title'].setText('')
        self['artist'].setText('')
        self['album'].setText('')
        self['genre'].setText('')
        self['bitrate'].setText('')
        self['mode'].setText('')
        self.pic = '/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/images/no_poster_vp.jpg'
        self['filelist'].anadeSeleccion()
        self.showpic()

    def infoshow(self, filename):
        nombre = self['filelist'].getFilename()
        self['filelist'].anadeSeleccion(nombre)
        title = None
        year = None
        genre = None
        modo = None
        artist = None
        album = None
        cover = None
        tipo = None
        duration = None
        bitrate = None
        self.oldpic = self.pic
        try:
            id3r = MP3Info.MP3Info(open(filename, 'rb'))
            title = id3r.title
            artist = id3r.artist
            album = id3r.album
            year = id3r.year
            genre = id3r.genre
            duration = '%d:%02d' % (id3r.mpeg.length_minutes, id3r.mpeg.length_seconds)
            bitrate = '%iKbps' % id3r.mpeg.bitrate
            cover = id3r.cover
            tipo = id3r.picformat
            if tipo != 'jpg':
                cover = None
            modo = id3r.mpeg.mode
        except:
            pass

        if title == None or title == '':
            try:
                foldername = filename.rpartition('/')
                title = foldername[2].decode('windows-1252').encode('utf-8')
            except:
                title = ''

        if artist == None:
            artist = ''
        if album == None:
            album = ''
        if year == None:
            year = ''
        else:
            year = ' - ' + year
        if genre == None:
            genre = ''
        if modo == None:
            modo = ''
        if duration == None:
            duration = ''
        if bitrate == None:
            bitrate = ''
        self['title'].setText(str(title))
        self['artist'].setText(str(artist))
        self['album'].setText(str(album) + str(year))
        self['genre'].setText(str(genre))
        self['bitrate'].setText(str(bitrate))
        self['mode'].setText(str(modo))
        jfilename = None
        if cover != None:
            f = open('/tmp/.cover.' + str(tipo), 'wb')
            f.write(cover)
            f.close()
            jfilename = '/tmp/.cover.' + str(tipo)
        elif fileExists(str(self.filelist.getCurrentDirectory()) + str(album) + '.jpg'):
            jfilename = str(self.filelist.getCurrentDirectory()) + str(album) + '.jpg'
        elif fileExists(str(self.filelist.getCurrentDirectory()) + str(artist) + '.jpg'):
            jfilename = str(self.filelist.getCurrentDirectory()) + str(artist) + '.jpg'
        elif fileExists(str(self['filelist'].getFilename()) + '.jpg'):
            jfilename = str(self['filelist'].getFilename()) + '.jpg'
        if jfilename != None:
            self.pic = jfilename
            self.showpic()
        else:
            dirname = self['filelist'].getCurrentDirectory()
            try:
                jfilename = MP3Info.CoverFind(filename, dirname)
                if jfilename != None:
                    self.pic = jfilename
                    self.Timer.start(500, False)
                else:
                    self.pic = '/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/images/no_poster_vp.jpg'
                    self.showpic()
            except:
                pass

    def showpic(self):
        con = False
        if self.pic != self.oldpic:
            if not fileExists(self.pic):
                if fileExists('/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/images/NoAlbumCover.jpg'):
                    self.pic = '/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/images/NoAlbumCover.jpg'
                else:
                    self.pic = None
                con = True
            if self.pic != None:
                sc = AVSwitch().getFramebufferScale()
                try:
                    self.picload.setPara((self['coverArt'].instance.size().width(),
                     self['coverArt'].instance.size().height(),
                     sc[0],
                     sc[1],
                     0,
                     1,
                     '#00000000'))
                    self.picload.startDecode(self.pic)
                except:
                    pass

        if not con:
            self.Timer.stop()

    def paintPoster(self, picInfo = None):
        ptr = self.picload.getData()
        if ptr != None:
            self['coverArt'].instance.setPixmap(ptr.__deref__())
            self['coverArt'].show()

    def PlayService(self):
        playlistplay = 0
        newref = eServiceReference(4097, 0, self['filelist'].getFilename())
        self.session.nav.playService(newref)
        MC_AudioPlayer.STATE = 'PLAY'
        self.infoshow(self['filelist'].getFilename())

    def PlayServicepls(self):
        MC_AudioPlayer.playlistplay = 1
        x = self.playlist.getCurrentIndex()
        print 'x is %s' % x
        x = len(self.playlist)
        print 'x is %s' % x
        ref = self.playlist.getServiceRefList()[self.playlist.getCurrentIndex()]
        newref = eServiceReference(4097, 0, ref.getPath())
        self.session.nav.playService(newref)
        MC_AudioPlayer.STATE = 'PLAY'
        self.updateFileInfo()

    def StopPlayback(self):
        if self.isVisible == False:
            self.show()
            self.isVisible = True
        if self.session.nav.getCurrentService() is None:
            return
        self.session.nav.stopService()
        MC_AudioPlayer.STATE = 'NONE'
        self.oldpic = None
        self.deleteinfo()

    def showFileInfo(self):
        if self['filelist'].canDescent():
            return
        self.session.open(MC_AudioInfoView, self['filelist'].getCurrentDirectory() + self['filelist'].getFilename(), self['filelist'].getFilename(), self['filelist'].getServiceRef())

    def JumpToFolder(self, jumpto = None):
        if jumpto is None:
            return
        self['filelist'].changeDir(jumpto)
        self['currentfolder'].setText('%s' % jumpto)

    def updateFileInfo(self):
        currPlay = self.session.nav.getCurrentService()
        if currPlay is not None:
            sTitle = currPlay.info().getInfoString(iServiceInformation.sTagTitle)
            sArtist = currPlay.info().getInfoString(iServiceInformation.sTagArtist)
            sAlbum = currPlay.info().getInfoString(iServiceInformation.sTagAlbum)
            sGenre = currPlay.info().getInfoString(iServiceInformation.sTagGenre)
            sComment = currPlay.info().getInfoString(iServiceInformation.sTagComment)
            sYear = currPlay.info().getInfoString(iServiceInformation.sTagDate)
            if sTitle == '':
                sTitle = currPlay.info().getName().split('/')[-1]
            self['fileinfo'].setText('Title: ' + sTitle + '\nArtist: ' + sArtist + '\nAlbum: ' + sAlbum + '\nGenre: ' + sGenre + '\nComment: ' + sComment)
            self['curplayingtitle'].setText('Now Playing: ' + sArtist + ' - ' + sTitle)

    def addFiletoPls(self):
        if not self['filelist'].canDescent():
            if self.filelist.getServiceRef().type == 4098:
                ServiceRef = self.filelist.getServiceRef()
                extension = ServiceRef.getPath()[ServiceRef.getPath().rfind('.') + 1:]
                if self.playlistparsers.has_key(extension):
                    playlist = self.playlistparsers[extension]()
                    list = playlist.open(ServiceRef.getPath())
                    for x in list:
                        self.playlist.addFile(x.ref)

                    self.playlist.updateList()
            else:
                self.playlist.addFile(self.filelist.getServiceRef())
                self.playlist.updateList()
            self['key_blue'].setText(_('Playlist') + ' (%d)' % self.playlist.__len__())

    def addDirtoPls(self, directory, recursive = True):
        print 'copyDirectory', directory
        if directory == '/':
            print 'refusing to operate on /'
            return
        filelist = FileList(directory, useServiceRef=True, showMountpoints=False, isTop=True, matchingPattern='(?i)^.*\\.(mp3|ogg|wav|wave|flac|m4a)')
        for x in filelist.getFileList():
            y = x[0][0]
            if isinstance(y, eServiceReference):
                sref = y
            else:
                sref = None
            if x[0][1] == True:
                if recursive:
                    if x[0][0] != directory:
                        self.addDirtoPls(x[0][0])
            elif sref:
                self.playlist.addFile(x[0][0])

        self.playlist.updateList()
        self['key_blue'].setText(_('Playlist') + ' (%d)' % self.playlist.__len__())

    def deleteFile(self):
        self.service = self.filelist.getServiceRef()
        if self.service.type != 4098 and self.session.nav.getCurrentlyPlayingServiceReference() is not None:
            if self.service == self.session.nav.getCurrentlyPlayingServiceReference():
                self.StopPlayback()
        self.session.openWithCallback(self.deleteFileConfirmed, MessageBox, _('Do you really want to delete this file ?'))

    def deleteFileConfirmed(self, confirmed):
        if confirmed:
            delfile = self['filelist'].getFilename()
            os.remove(delfile)

    def deleteDir(self):
        self.session.openWithCallback(self.deleteDirConfirmed, MessageBox, _("Do you really want to delete this directory and it's content ?"))

    def deleteDirConfirmed(self, confirmed):
        if confirmed:
            import shutil
            deldir = self.filelist.getSelection()[0]
            shutil.rmtree(deldir)

    def addPlaylistParser(self, parser, extension):
        self.playlistparsers[extension] = parser

    def Exit(self):
        if self.isVisible == False:
            self.visibility()
            return
        try:
            config.plugins.mc_ap.lastDir.value = self.filelist.getCurrentDirectory()
        except:
            config.plugins.mc_ap.lastDir.value = 'mountpoint'

        config.plugins.mc_ap.save()
        configfile.save()
        del self.Timer
        self.session.nav.stopService()
        MC_AudioPlayer.STATE = 'NONE'
        self.session.nav.playService(self.oldService)
        try:
            os.system('fusermount -u /media/MediaServers')
            os.system('modprobe -r fuse')
            os.system('rm -r /media/MediaServers')
        except:
            pass

        self.close()

    def showMenu(self):
        menu = []
        if self.filelist.canDescent():
            x = self.filelist.getName()
            if x == '..':
                return
            menu.append((_('add directory to playlist '), 'copydir'))
            menu.append((_('delete directory'), 'deletedir'))
        else:
            menu.append((_('add file to playlist'), 'copyfile'))
            menu.append((_('add file to playlist and play'), 'copyandplay'))
            menu.append((_('add all files in directory to playlist'), 'copyfiles'))
            menu.append((_('delete file'), 'deletefile'))
        self.session.openWithCallback(self.menuCallback, ChoiceBox, title='', list=menu)

    def menuCallback(self, choice):
        if choice is None:
            return
        if choice[1] == 'copydir':
            self.addDirtoPls(self.filelist.getSelection()[0])
        elif choice[1] == 'deletedir':
            self.deleteDir()
        elif choice[1] == 'copyfile':
            self.addFiletoPls()
        elif choice[1] == 'copyandplay':
            self.addFiletoPls()
            self.StopPlayback()
            MC_AudioPlayer.currPlaying = self.playlist.__len__() - 1
            print 'curplay is %s' % MC_AudioPlayer.currPlaying
            self.session.openWithCallback(self.updatedata, MC_AudioPlaylist, Auto=True)
        elif choice[1] == 'copyfiles':
            self.addDirtoPls(os_path.dirname(self.filelist.getSelection()[0].getPath()) + '/', recursive=False)
        elif choice[1] == 'deletefile':
            self.deleteFile()

    def doEOF(self):
        print 'MediaCenter: EOF Event AUDIO...'
        if MC_AudioPlayer.playlistplay == 1:
            pass
        elif self.PlaySingle == 0:
            print 'Play Next File ...'
            self.down()
            if not self['filelist'].canDescent():
                self.PlayService()
            else:
                self.StopPlayback()
        else:
            print 'Stop Playback ...'
            self.StopPlayback()

    def __evDecodeError(self):
        currPlay = self.session.nav.getCurrentService()
        sVideoType = currPlay.info().getInfoString(iServiceInformation.sVideoType)
        print "[__evDecodeError] video-codec %s can't be decoded by hardware" % sVideoType
        self.session.open(MessageBox, _("This Box can't decode %s audio streams!") % sVideoType, type=MessageBox.TYPE_INFO, timeout=20)

    def __evPluginError(self):
        currPlay = self.session.nav.getCurrentService()
        message = currPlay.info().getInfoString(iServiceInformation.sUser + 12)
        print '[__evPluginError]', message
        self.session.open(MessageBox, message, type=MessageBox.TYPE_INFO, timeout=20)


class MC_AudioPlaylist(Screen):

    def __init__(self, session, Auto = False):
        Screen.__init__(self, session)
        self['PositionGauge'] = ServicePositionGauge(self.session.nav)
        self.mode = _('Normal')
        self['key_red'] = Button(_('Back'))
        self['key_green'] = Button(self.mode)
        self['key_yellow'] = Button(_('delete track'))
        self['key_blue'] = Button(_('File Browser'))
        self['fileinfo'] = Label()
        self['coverArt'] = MediaPixmap()
        self['playlistname'] = Label()
        self['track'] = Label()
        self.curfavfolder = -1
        self['play'] = Pixmap()
        self['stop'] = Pixmap()
        self['curplayingtitle'] = Label()
        self.updateFileInfo()
        self.PlaySingle = 0
        self.playlist = PlayList()
        self['playlist'] = self.playlist
        self.playname = str(self.playlist.getName())
        self.playlistIOInternal = PlaylistIOInternal()
        self.playlistparsers = {}
        self.addPlaylistParser(PlaylistIOM3U, 'm3u')
        self.addPlaylistParser(PlaylistIOPLS, 'pls')
        self.addPlaylistParser(PlaylistIOInternal, 'e2pls')
        self.__event_tracker = ServiceEventTracker(screen=self, eventmap={iPlayableService.evEOF: self.eof,
         iPlayableService.evStopped: self.StopPlayback})
        self['actions'] = HelpableActionMap(self, 'MC_AudioPlayerActions', {'ok': (self.KeyOK, 'Play from selected file'),
         'cancel': (self.Exit, 'Exit Audio Player'),
         'left': (self.leftUp, 'List Top'),
         'right': (self.rightDown, 'List Bottom'),
         'up': (self.up, 'List up'),
         'down': (self.down, 'List down'),
         'menu': (self.showMenu, 'File / Folder Options'),
         'video': (self.visibility, 'Show / Hide Player'),
         'info': (self.showFileInfo, 'Show File Info'),
         'stop': (self.StopPlayback, 'Stop Playback'),
         'red': (self.Exit, 'Close Playlist'),
         'green': (self.changemode, 'Change mode'),
         'yellow': (self.deleteEntry, 'Delete Entry'),
         'blue': (self.Exit, 'Close Playlist'),
         'next': (self.KeyNext, 'Next song'),
         'previous': (self.KeyPrevious, 'Previous song'),
         'playpause': (self.PlayPause, 'Play / Pause'),
         'stop': (self.StopPlayback, 'Stop')}, -2)
        self['title'] = Label()
        self['artist'] = Label()
        self['album'] = Label()
        self['year'] = Label()
        self['genre'] = Label()
        self['duration'] = Label()
        self['bitrate'] = Label()
        self['mode'] = Label()
        self['coverArt'] = Pixmap()
        self.picload = ePicLoad()
        self.picload.PictureData.get().append(self.paintPoster)
        self.Timer = eTimer()
        self.Timer.callback.append(self.showpic)
        self.pic = None
        self.oldpic = None
        self['playlistname'] = Label(_('Playlist') + ': %s' % MC_AudioPlayer.PLAYLISTNAME)
        self['track'] = Label(_('Track') + ': %d / %d' % (self.playlist.getCurrentIndex() + 1, self.playlist.__len__()))
        if Auto:
            self.onLayoutFinish.append(self.KeyOK)
        else:
            self.onLayoutFinish.append(self.deleteinfo)
        self.oidos = []

    def changemode(self):
        if self.mode == _('Normal'):
            self.mode = _('Continuous')
        elif self.mode == _('Continuous'):
            self.mode = _('Random')
        else:
            self.mode = _('Normal')
        self['key_green'].setText(self.mode)

    def up(self):
        self['playlist'].up()

    def down(self):
        self['playlist'].down()

    def leftUp(self):
        self['playlist'].pageUp()

    def rightDown(self):
        self['playlist'].pageDown()

    def KeyOK(self):
        if len(self.playlist.getServiceRefList()):
            if MC_AudioPlayer.currPlaying != -1:
                x = MC_AudioPlayer.currPlaying
            else:
                x = self.playlist.getSelectionIndex()
            print 'x is %s' % x
            self.playlist.setCurrentPlaying(self.playlist.getSelectionIndex())
            if self.mode == _('Random'):
                self.oidos.append(self.playlist.getSelectionIndex())
            x = self.playlist.getCurrentIndex()
            print 'x is %s' % x
            x = len(self.playlist)
            print 'x is %s' % x
            self.PlayService()

    def PlayPause(self):
        if MC_AudioPlayer.STATE != 'NONE':
            if MC_AudioPlayer.STATE == 'PLAY':
                service = self.session.nav.getCurrentService()
                pausable = service.pause()
                pausable.pause()
                MC_AudioPlayer.STATE = 'PAUSED'
            elif MC_AudioPlayer.STATE == 'PAUSED':
                service = self.session.nav.getCurrentService()
                pausable = service.pause()
                pausable.unpause()
                MC_AudioPlayer.STATE = 'PLAY'
            else:
                self.KeyOK()

    def KeyNext(self):
        if MC_AudioPlayer.STATE != 'NONE':
            if MC_AudioPlayer.playlistplay == 1:
                if self.mode == _('Random'):
                    if self.playlist.__len__() == len(self.oidos):
                        self.oidos = []
                    next = None
                    while next == None or next in self.oidos:
                        next = randint(0, self.playlist.__len__() - 1)

                    self.oidos.append(next)
                    self.playlist.setCurrentPlaying(next)
                    self.PlayService()
                else:
                    next = self['playlist'].getCurrentIndex() + 1
                    if next < len(self.playlist):
                        self.playlist.setCurrentPlaying(next)
                        self.PlayService()
                    elif self.mode == _('Continuous'):
                        self.playlist.setCurrentPlaying(0)
                        self.PlayService()
                    else:
                        self.StopPlayback()
            else:
                self.session.open(MessageBox, _('You have to close playlist before you can go to the next song while playing from file browser.'), MessageBox.TYPE_ERROR)

    def KeyPrevious(self):
        if MC_AudioPlayer.playlistplay == 1:
            next = self.playlist.getCurrentIndex() - 1
            if next != -1:
                self.playlist.setCurrentPlaying(next)
            else:
                self.playlist.setCurrentPlaying(0)
            self.PlayService()
        else:
            self.session.open(MessageBox, _('You have to close playlist before you can go to the previous song while playing from file browser.'), MessageBox.TYPE_ERROR)

    def deleteinfo(self):
        self['title'].setText('')
        self['artist'].setText('')
        self['album'].setText('')
        self['genre'].setText('')
        self['bitrate'].setText('')
        self['mode'].setText('')
        self.pic = '/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/images/no_poster_vp.jpg'
        self.playlist.setCurrentPlaying(-1)
        self['playlistname'].setText(_('Playlist') + ': %s' % MC_AudioPlayer.PLAYLISTNAME)
        self['track'].setText(_('Track') + ': %d / %d' % (self.playlist.getCurrentIndex() + 1, self.playlist.__len__()))
        self.showpic()
        self['key_red'].show()
        self['key_blue'].show()
        self['key_yellow'].show()

    def infoshow(self, filename):
        nombre = self['playlist'].getSelection()
        title = None
        year = None
        genre = None
        modo = None
        artist = None
        album = None
        cover = None
        tipo = None
        duration = None
        bitrate = None
        self.oldpic = self.pic
        try:
            id3r = MP3Info.MP3Info(open(filename, 'rb'))
            title = id3r.title
            artist = id3r.artist
            album = id3r.album
            year = id3r.year
            genre = id3r.genre
            duration = '%d:%02d' % (id3r.mpeg.length_minutes, id3r.mpeg.length_seconds)
            bitrate = '%iKbps' % id3r.mpeg.bitrate
            cover = id3r.cover
            tipo = id3r.picformat
            if tipo != 'jpg':
                cover = None
            modo = id3r.mpeg.mode
        except:
            pass

        if title == None or title == '':
            try:
                foldername = filename.rpartition('/')
                title = foldername[2].decode('windows-1252').encode('utf-8')
            except:
                title = ''

        if artist == None:
            artist = ''
        if album == None:
            album = ''
        if year == None:
            year = ''
        else:
            year = ' - ' + year
        if genre == None:
            genre = ''
        if modo == None:
            modo = ''
        if duration == None:
            duration = ''
        if bitrate == None:
            bitrate = ''
        self['title'].setText(str(title))
        self['artist'].setText(str(artist))
        self['album'].setText(str(album) + str(year))
        self['genre'].setText(str(genre))
        self['bitrate'].setText(str(bitrate))
        self['mode'].setText(str(modo))
        jfilename = None
        directory = os_path.split(str(filename).split('/')[-1])[0]
        if cover != None:
            f = open('/tmp/.cover.' + str(tipo), 'wb')
            f.write(cover)
            f.close()
            jfilename = '/tmp/.cover.' + str(tipo)
        elif fileExists(str(directory) + str(album) + '.jpg'):
            jfilename = str(directory) + str(album) + '.jpg'
        elif fileExists(str(directory) + str(artist) + '.jpg'):
            jfilename = str(directory) + str(artist) + '.jpg'
        elif fileExists(str(filename) + '.jpg'):
            jfilename = str(filename) + '.jpg'
        if jfilename != None:
            self.pic = jfilename
            self.showpic()
        else:
            try:
                jfilename = MP3Info.CoverFind(filename, directory)
                if jfilename != None:
                    self.pic = jfilename
                    self.Timer.start(500, False)
                else:
                    self.pic = '/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/images/no_poster_vp.jpg'
                    self.showpic()
            except:
                pass

        self['playlistname'].setText(_('Playlist') + ': %s' % MC_AudioPlayer.PLAYLISTNAME)
        self['track'].setText(_('Track') + ': %d / %d' % (self.playlist.getCurrentIndex() + 1, self.playlist.__len__()))
        self['key_red'].hide()
        self['key_blue'].hide()
        self['key_yellow'].hide()

    def showpic(self):
        con = False
        if self.pic != self.oldpic:
            if not fileExists(self.pic):
                if fileExists('/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/images/NoAlbumCover.jpg'):
                    self.pic = '/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/images/NoAlbumCover.jpg'
                else:
                    self.pic = None
                con = True
            if self.pic != None:
                sc = AVSwitch().getFramebufferScale()
                try:
                    self.picload.setPara((self['coverArt'].instance.size().width(),
                     self['coverArt'].instance.size().height(),
                     sc[0],
                     sc[1],
                     0,
                     1,
                     '#00000000'))
                    self.picload.startDecode(self.pic)
                except:
                    pass

        if not con:
            self.Timer.stop()

    def paintPoster(self, picInfo = None):
        ptr = self.picload.getData()
        if ptr != None:
            self['coverArt'].instance.setPixmap(ptr.__deref__())
            self['coverArt'].show()

    def PlayService(self):
        MC_AudioPlayer.playlistplay = 1
        ref = self.playlist.getServiceRefList()[self.playlist.getCurrentIndex()]
        newref = eServiceReference(4097, 0, ref.getPath())
        self.session.nav.playService(newref)
        MC_AudioPlayer.STATE = 'PLAY'
        self.infoshow(ref.getPath())

    def StopPlayback(self):
        if self.session.nav.getCurrentService() is None:
            return
        self.session.nav.stopService()
        MC_AudioPlayer.STATE = 'NONE'
        self.deleteinfo()

    def visibility(self, force = 1):
        if self.isVisible == True:
            self.isVisible = False
            self.hide()
        else:
            self.isVisible = True
            self.show()

    def showFileInfo(self):
        if self['filelist'].canDescent():
            return
        self.session.open(MC_AudioInfoView, self['filelist'].getCurrentDirectory() + self['filelist'].getFilename(), self['filelist'].getFilename(), self['filelist'].getServiceRef())

    def Settings(self):
        self.session.open(AudioPlayerSettings)

    def Exit(self):
        if MC_AudioPlayer.STATE != 'PLAY':
            self.close(self.playlist.getServiceRefList())

    def eof(self):
        self.KeyNext()

    def updateFileInfo(self):
        print 'DOING EOF FOR 2'
        currPlay = self.session.nav.getCurrentService()
        if currPlay is not None:
            sTitle = currPlay.info().getInfoString(iServiceInformation.sTagTitle)
            sArtist = currPlay.info().getInfoString(iServiceInformation.sTagArtist)
            sAlbum = currPlay.info().getInfoString(iServiceInformation.sTagAlbum)
            sGenre = currPlay.info().getInfoString(iServiceInformation.sTagGenre)
            sComment = currPlay.info().getInfoString(iServiceInformation.sTagComment)
            sYear = currPlay.info().getInfoString(iServiceInformation.sTagDate)
            if sTitle == '':
                sTitle = currPlay.info().getName().split('/')[-1]
            self['fileinfo'].setText('Title: ' + sTitle + '\nArtist: ' + sArtist + '\nAlbum: ' + sAlbum + '\nGenre: ' + sGenre + '\nComment: ' + sComment)
            self['curplayingtitle'].setText('Now Playing: ' + sArtist + ' - ' + sTitle)

    def save_playlist(self):
        self.session.openWithCallback(self.save_pls, InputBox, title=_('Please enter filename (empty = use current date)'), windowTitle=_('Save Playlist'))

    def save_pls(self, name):
        if name is not None:
            name = name.strip()
            if name == '':
                name = strftime('%y%m%d_%H%M%S')
            MC_AudioPlayer.PLAYLISTNAME = name
            name += '.e2pls'
            self.playlistIOInternal.clear()
            for x in self.playlist.list:
                self.playlistIOInternal.addService(ServiceReference(x[0]))

            self.playlistIOInternal.save(resolveFilename(SCOPE_PLAYLIST) + name)
            self.deleteinfo()

    def load_playlist(self):
        listpath = []
        playlistdir = resolveFilename(SCOPE_PLAYLIST)
        try:
            for i in os_listdir(playlistdir):
                listpath.append((i, playlistdir + i))

        except IOError as e:
            print 'Error while scanning subdirs ', e

        self.session.openWithCallback(self.load_pls, ChoiceBox, title=_('Please select a playlist...'), list=listpath)

    def load_pls(self, path):
        if path is not None:
            self.playlist.clear()
            extension = path[0].rsplit('.', 1)[-1]
            name = path[0].split('/')[-1]
            name = name[:name.rfind('.')]
            MC_AudioPlayer.PLAYLISTNAME = name
            if self.playlistparsers.has_key(extension):
                playlist = self.playlistparsers[extension]()
                list = playlist.open(path[1])
                for x in list:
                    self.playlist.addFile(x.ref)

            self.playlist.updateList()
            self.deleteinfo()

    def delete_saved_playlist(self):
        listpath = []
        playlistdir = resolveFilename(SCOPE_PLAYLIST)
        try:
            for i in os_listdir(playlistdir):
                listpath.append((i, playlistdir + i))

        except IOError as e:
            print 'Error while scanning subdirs ', e

        self.session.openWithCallback(self.delete_saved_pls, ChoiceBox, title=_('Please select a playlist to delete...'), list=listpath)

    def delete_saved_pls(self, path):
        if path is not None:
            self.delname = path[1]
            self.session.openWithCallback(self.delete_saved_pls_conf, MessageBox, _('Do you really want to delete %s?') % path[1])

    def delete_saved_pls_conf(self, confirmed):
        if confirmed:
            try:
                os_remove(self.delname)
            except OSError as e:
                print 'delete failed:', e
                self.session.open(MessageBox, _('Delete failed!'), MessageBox.TYPE_ERROR)

    def addPlaylistParser(self, parser, extension):
        self.playlistparsers[extension] = parser

    def showMenu(self):
        if MC_AudioPlayer.STATE != 'PLAY':
            menu = []
            menu.append((_('delete from playlist'), 'deleteentry'))
            menu.append((_('clear playlist'), 'clear'))
            menu.append((_('load playlist'), 'loadplaylist'))
            menu.append((_('save playlist'), 'saveplaylist'))
            menu.append((_('delete saved playlist'), 'deleteplaylist'))
            self.session.openWithCallback(self.menuCallback, ChoiceBox, title='', list=menu)

    def deleteEntry(self):
        if MC_AudioPlayer.STATE != 'PLAY':
            self.playlist.deleteFile(self.playlist.getSelectionIndex())
            self.playlist.updateList()
            self.deleteinfo()

    def menuCallback(self, choice):
        if choice is None:
            return
        if choice[1] == 'deleteentry':
            self.deleteEntry()
        elif choice[1] == 'clear':
            self.playlist.clear()
            self.deleteinfo()
        elif choice[1] == 'loadplaylist':
            self.load_playlist()
        elif choice[1] == 'saveplaylist':
            self.save_playlist()
        elif choice[1] == 'deleteplaylist':
            self.delete_saved_playlist()


class MediaPixmap(Pixmap):

    def __init__(self):
        Pixmap.__init__(self)
        self.coverArtFileName = ''
        self.picload = ePicLoad()
        self.picload.PictureData.get().append(self.paintCoverArtPixmapCB)
        self.coverFileNames = ['folder.png', 'folder.jpg']

    def applySkin(self, desktop, screen):
        from Tools.LoadPixmap import LoadPixmap
        noCoverFile = None
        if self.skinAttributes is not None:
            for attrib, value in self.skinAttributes:
                if attrib == 'pixmap':
                    noCoverFile = value
                    break

        if noCoverFile is None:
            noCoverFile = resolveFilename(SCOPE_SKIN_IMAGE, 'skin_default/no_coverArt.png')
        self.noCoverPixmap = LoadPixmap(noCoverFile)
        return Pixmap.applySkin(self, desktop, screen)

    def onShow(self):
        Pixmap.onShow(self)
        sc = AVSwitch().getFramebufferScale()
        self.picload.setPara((self.instance.size().width(),
         self.instance.size().height(),
         sc[0],
         sc[1],
         False,
         1,
         '#00000000'))

    def paintCoverArtPixmapCB(self, picInfo = None):
        ptr = self.picload.getData()
        if ptr != None:
            self.instance.setPixmap(ptr.__deref__())

    def updateCoverArt(self, path):
        while not path.endswith('/'):
            path = path[:-1]

        new_coverArtFileName = None
        for filename in self.coverFileNames:
            if fileExists(path + filename):
                new_coverArtFileName = path + filename

        if self.coverArtFileName != new_coverArtFileName:
            self.coverArtFileName = new_coverArtFileName
            if new_coverArtFileName:
                self.picload.startDecode(self.coverArtFileName)
            else:
                self.showDefaultCover()

    def showDefaultCover(self):
        self.instance.setPixmap(self.noCoverPixmap)

    def embeddedCoverArt(self):
        print '[embeddedCoverArt] found'
        self.coverArtFileName = '/tmp/.id3coverart'
        self.picload.startDecode(self.coverArtFileName)


class AudioPlayerSettings(Screen):
    skin = '\n\t\t<screen position="160,220" size="400,120" title="Audioplayer Settings" >\n\t\t\t<widget name="configlist" position="10,10" size="380,100" />\n\t\t</screen>'

    def __init__(self, session):
        self.skin = AudioPlayerSettings.skin
        Screen.__init__(self, session)
        self['actions'] = NumberActionMap(['SetupActions'], {'ok': self.close,
         'cancel': self.close,
         'left': self.keyLeft,
         'right': self.keyRight,
         '0': self.keyNumber,
         '1': self.keyNumber,
         '2': self.keyNumber,
         '3': self.keyNumber,
         '4': self.keyNumber,
         '5': self.keyNumber,
         '6': self.keyNumber,
         '7': self.keyNumber,
         '8': self.keyNumber,
         '9': self.keyNumber}, -1)
        self.list = []
        self['configlist'] = ConfigList(self.list)
        self.list.append(getConfigListEntry(_('Screensaver Enable'), config.plugins.mc_ap.showMvi))
        self.list.append(getConfigListEntry(_('Screensaver Interval'), config.plugins.mc_ap.mvi_delay))

    def keyLeft(self):
        self['configlist'].handleKey(KEY_LEFT)

    def keyRight(self):
        self['configlist'].handleKey(KEY_RIGHT)

    def keyNumber(self, number):
        self['configlist'].handleKey(KEY_0 + number)


class MC_AudioInfoView(Screen):
    skin = '\n\t\t<screen position="80,130" size="560,320" title="View Audio Info" >\n\t\t\t<widget name="infolist" position="5,5" size="550,310" selectionDisabled="1" />\n\t\t</screen>'

    def __init__(self, session, fullname, name, ref):
        self.skin = MC_AudioInfoView.skin
        Screen.__init__(self, session)
        self['actions'] = ActionMap(['OkCancelActions'], {'cancel': self.close,
         'ok': self.close}, -1)
        tlist = []
        self['infolist'] = ServiceInfoList(tlist)
        currPlay = self.session.nav.getCurrentService()
        if currPlay is not None:
            stitle = currPlay.info().getInfoString(iServiceInformation.sTagTitle)
            if stitle == '':
                stitle = currPlay.info().getName().split('/')[-1]
            tlist.append(ServiceInfoListEntry('Title: ', stitle))
            tlist.append(ServiceInfoListEntry('Artist: ', currPlay.info().getInfoString(iServiceInformation.sTagArtist)))
            tlist.append(ServiceInfoListEntry('Album: ', currPlay.info().getInfoString(iServiceInformation.sTagAlbum)))
            tlist.append(ServiceInfoListEntry('Genre: ', currPlay.info().getInfoString(iServiceInformation.sTagGenre)))
            tlist.append(ServiceInfoListEntry('Year: ', currPlay.info().getInfoString(iServiceInformation.sTagDate)))
            tlist.append(ServiceInfoListEntry('Comment: ', currPlay.info().getInfoString(iServiceInformation.sTagComment)))
