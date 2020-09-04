from Screens.ServiceInfo import ServiceInfoList, ServiceInfoListEntry
from Components.ActionMap import ActionMap, NumberActionMap, HelpableActionMap
from Components.Pixmap import Pixmap, MovingPixmap
from Components.Label import Label
from Components.Button import Button
from Components.Sources.List import List
from Components.Sources.StaticText import StaticText
from Screens.MessageBox import MessageBox
from Screens.HelpMenu import HelpableScreen
from Components.ConfigList import ConfigList
from Components.config import *
from Tools.Directories import resolveFilename, fileExists, pathExists, createDir, SCOPE_MEDIA
from Components.AVSwitch import AVSwitch
from Plugins.Plugin import PluginDescriptor
from MC_Filelist import FileList
import os
from os import path as os_path
config.plugins.mc_pp = ConfigSubsection()
config.plugins.mc_pp.slidetime = ConfigInteger(default=10, limits=(5, 60))
config.plugins.mc_pp.resize = ConfigSelection(default='0', choices=[('0', _('simple')), ('1', _('better'))])
config.plugins.mc_pp.cache = ConfigEnableDisable(default=True)
config.plugins.mc_pp.lastDir = ConfigText(default='mountpoint')
config.plugins.mc_pp.rotate = ConfigSelection(default='0', choices=[('0', _('none')), ('1', _('manual')), ('2', _('by Exif'))])
config.plugins.mc_pp.ThumbWidth = ConfigInteger(default=145, limits=(1, 999))
config.plugins.mc_pp.ThumbHeight = ConfigInteger(default=120, limits=(1, 999))
config.plugins.mc_pp.bgcolor = ConfigSelection(default='#00000000', choices=[('#00000000', _('black')),
 ('#009eb9ff', _('blue')),
 ('#00ff5a51', _('red')),
 ('#00ffe875', _('yellow')),
 ('#0038FF48', _('green'))])
config.plugins.mc_pp.textcolor = ConfigSelection(default='#0038FF48', choices=[('#00000000', _('black')),
 ('#009eb9ff', _('blue')),
 ('#00ff5a51', _('red')),
 ('#00ffe875', _('yellow')),
 ('#0038FF48', _('green'))])
config.plugins.mc_pp.framesize = ConfigSlider(default=30, increment=5, limits=(5, 99))
config.plugins.mc_pp.infoline = ConfigEnableDisable(default=True)
config.plugins.mc_pp.loop = ConfigEnableDisable(default=True)

def getAspect():
    val = AVSwitch().getAspectRatioSetting()
    return val / 2


def getScale():
    return AVSwitch().getFramebufferScale()


class MC_PictureViewer(Screen, HelpableScreen):

    def __init__(self, session, ruta_inicio = None):
        Screen.__init__(self, session)
        HelpableScreen.__init__(self)
        self.oldService = self.session.nav.getCurrentlyPlayingServiceOrGroup()
        self.session.nav.stopService()
        os.system('/usr/bin/showiframe /usr/share/enigma2/black.mvi &')
        self['key_red'] = Button('Home')
        self['key_green'] = Button('Slide Show')
        self['key_yellow'] = Button('Thumb View')
        self['key_blue'] = Button(_('Settings'))
        self['currentfolder'] = Label('')
        self['currentfavname'] = Label('')
        self.curfavfolder = -1
        self['actions'] = HelpableActionMap(self, 'MC_PictureViewerActions', {'ok': (self.KeyOk, 'Show Picture'),
         'cancel': (self.Exit, 'Exit Picture Viewer'),
         'left': (self.leftUp, 'List Top'),
         'right': (self.rightDown, 'List Bottom'),
         'up': (self.up, 'List up'),
         'down': (self.down, 'List down'),
         'menu': (self.KeyMenu, 'File / Folder Options'),
         'info': (self.StartExif, 'Show File Info'),
         'nextBouquet': (self.NextFavFolder, 'Next Favorite Folder'),
         'prevBouquet': (self.PrevFavFolder, 'Previous Favorite Folder'),
         'red': (self.Exit, 'Exit Pictures'),
         'green': (self.startslideshow, 'Start Slideshow'),
         'yellow': (self.StartThumb, 'Thumb View'),
         'blue': (self.Settings, 'Settings')}, -2)
        self.aspect = getAspect()
        if ruta_inicio == None:
            currDir = config.plugins.mc_pp.lastDir.value
        else:
            currDir = ruta_inicio
        if not pathExists(currDir):
            currDir = None
        if not os.path.exists('/media/MediaServers'):
            os.system('mkdir -p /media/MediaServers')
        try:
            os.system('modprobe fuse')
            os.system('djmount -o allow_other -o iocharset=utf8 /media/MediaServers')
        except:
            pass

        import time
        time.sleep(3)
        self['currentfolder'].setText(str(currDir))
        self.filelist = FileList(currDir, showMountpoints=True, matchingPattern='(?i)^.*\\.(jpeg|jpg|jpe|png|bmp)')
        self['filelist'] = self.filelist
        self['thumbnail'] = Pixmap()
        self.ThumbTimer = eTimer()
        self.ThumbTimer.callback.append(self.showThumb)
        self.ThumbTimer.start(500, True)
        self.picload = ePicLoad()

    def startslideshow(self):
        self.session.openWithCallback(self.returnVal, MC_PicView, self.filelist.getFileList(), self.filelist.getSelectionIndex(), self.filelist.getCurrentDirectory(), True)

    def up(self):
        self['filelist'].up()
        self.ThumbTimer.start(500, True)

    def down(self):
        self['filelist'].down()
        self.ThumbTimer.start(500, True)

    def leftUp(self):
        self['filelist'].pageUp()
        self.ThumbTimer.start(500, True)

    def rightDown(self):
        self['filelist'].pageDown()
        self.ThumbTimer.start(500, True)

    def NextFavFolder(self):
        if self.curfavfolder + 1 < config.plugins.mc_favorites.foldercount.value:
            self.curfavfolder += 1
            self.favname = config.plugins.mc_favorites.folders[self.curfavfolder].name.value
            self.folder = config.plugins.mc_favorites.folders[self.curfavfolder].basedir.value
            self['currentfolder'].setText('%s' % self.folder)
            self['currentfavname'].setText('%s' % self.favname)
            if os.path.exists(self.folder) == True:
                self['filelist'].changeDir(self.folder)
        else:
            return

    def PrevFavFolder(self):
        if self.curfavfolder <= 0:
            return
        self.curfavfolder -= 1
        self.favname = config.plugins.mc_favorites.folders[self.curfavfolder].name.value
        self.folder = config.plugins.mc_favorites.folders[self.curfavfolder].basedir.value
        self['currentfolder'].setText('%s' % self.folder)
        self['currentfavname'].setText('%s' % self.favname)
        if os.path.exists(self.folder) == True:
            self['filelist'].changeDir(self.folder)

    def showPic(self, picInfo = ''):
        ptr = self.picload.getData()
        if ptr != None:
            self['thumbnail'].instance.setPixmap(ptr.__deref__())
            self['thumbnail'].show()

    def showThumb(self):
        return
        if not self.filelist.canDescent():
            if self.picload.getThumbnail(self.filelist.getCurrentDirectory() + self.filelist.getFilename()) == 1:
                ptr = self.picload.getData()
            else:
                ptr = None
            if ptr != None:
                self['thumbnail'].instance.setPixmap(ptr.__deref__())
                self['thumbnail'].show()
        else:
            self['thumbnail'].hide()

    def KeyOk(self):
        if self.filelist.canDescent():
            self.filelist.descent()
        else:
            self.session.openWithCallback(self.returnVal, MC_PicView, self.filelist.getFileList(), self.filelist.getSelectionIndex(), self.filelist.getCurrentDirectory(), False)

    def KeyMenu(self):
        self.ThumbTimer.stop()
        if self['filelist'].canDescent():
            if self.filelist.getCurrent()[0][1]:
                self.currentDirectory = self.filelist.getCurrent()[0][0]
                if self.currentDirectory is not None:
                    foldername = self.currentDirectory.split('/')
                    foldername = foldername[-2]
                    self.session.open(MC_FolderOptions, self.currentDirectory, foldername)

    def StartThumb(self):
        self.session.openWithCallback(self.returnVal, MC_PicThumbViewer, self.filelist.getFileList(), self.filelist.getSelectionIndex(), self.filelist.getCurrentDirectory())

    def JumpToFolder(self, jumpto = None):
        if jumpto is None:
            return
        self['filelist'].changeDir(jumpto)
        self['currentfolder'].setText('%s' % jumpto)

    def FavoriteFolders(self):
        self.session.openWithCallback(self.JumpToFolder, MC_FavoriteFolders)

    def returnVal(self, val = 0):
        if val > 0:
            for x in self.filelist.getFileList():
                if x[0][1] == True:
                    val += 1

            self.filelist.moveToIndex(val)

    def StartExif(self):
        if not self.filelist.canDescent():
            self.session.open(MessageBox, 'Oh no, bugged in this version :(', MessageBox.TYPE_ERROR)

    def Settings(self):
        self.session.open(MC_PicSetup)

    def Exit(self):
        try:
            config.plugins.mc_pp.lastDir.value = self.filelist.getCurrentDirectory()
        except:
            config.plugins.mc_pp.lastDir.value = 'mountpoint'

        config.plugins.mc_pp.save()
        configfile.save()
        self.session.nav.playService(self.oldService)
        try:
            os.system('fusermount -u /media/MediaServers')
            os.system('modprobe -r fuse')
            os.system('rm -r /media/MediaServers')
        except:
            pass

        self.close()


T_INDEX = 0
T_FRAME_POS = 1
T_PAGE = 2
T_NAME = 3
T_FULL = 4

class MC_PicThumbViewer(Screen, HelpableScreen):

    def __init__(self, session, piclist, lastindex, path):
        self['key_red'] = Button('')
        self['key_green'] = Button('Slide Show')
        self['key_yellow'] = Button('File View')
        self['key_blue'] = Button(_('Settings'))
        self.textcolor = config.plugins.mc_pp.textcolor.value
        self.color = config.plugins.mc_pp.bgcolor.value
        textsize = 20
        self.spaceX = 20
        self.spaceY = 25
        self.picX = config.plugins.mc_pp.ThumbWidth.value
        self.picY = config.plugins.mc_pp.ThumbHeight.value
        size_w = getDesktop(0).size().width()
        size_h = getDesktop(0).size().height()
        if size_w == 1280:
            self.spaceTop = 150
            self.spaceLeft = 175
            self.spaceRight = 175
            self.spaceBottom = 150
            self.ButtonPosY = 630
        else:
            self.spaceTop = 120
            self.spaceLeft = 25
            self.ButtonPosY = 72
        self.thumbsX = (size_w - self.spaceLeft - self.spaceRight) / (self.spaceX + self.picX)
        self.spaceLeftExtra = (size_w - self.spaceLeft - self.spaceRight - self.thumbsX * (self.spaceX + self.picX)) / 2
        self.thumbsY = (size_h - self.spaceTop - self.spaceBottom) / (self.spaceY + self.picY)
        self.spaceTopExtra = (size_h - self.spaceTop - self.spaceBottom - self.thumbsY * (self.spaceY + self.picY)) / 2
        self.thumbsC = self.thumbsX * self.thumbsY
        self.positionlist = []
        skincontent = ''
        posX = -1
        for x in range(self.thumbsC):
            posY = x / self.thumbsX
            posX += 1
            if posX >= self.thumbsX:
                posX = 0
            absX = self.spaceLeft + self.spaceLeftExtra + posX * (self.spaceX + self.picX)
            absY = self.spaceTop + self.spaceTopExtra + self.spaceY + posY * (self.spaceY + self.picY)
            self.positionlist.append((absX, absY))
            skincontent += '<widget name="label' + str(x) + '" position="' + str(absX + 5) + ',' + str(absY + self.picY - textsize) + '" size="' + str(self.picX - 10) + ',' + str(textsize) + '" font="Regular;14" zPosition="2" transparent="1" noWrap="1" foregroundColor="' + self.textcolor + '" />'
            skincontent += '<widget name="thumb' + str(x) + '" position="' + str(absX + 5) + ',' + str(absY + 5) + '" size="' + str(self.picX - 10) + ',' + str(self.picY - textsize * 2) + '" zPosition="2" transparent="1" alphatest="on" />'

        self.skindir = config.plugins.mc_globalsettings.currentskin.path.value.split('/')[0]
        self.skin = '<screen position="0,0" size="' + str(size_w) + ',' + str(size_h) + '" flags="wfNoBorder" > \t\t\t<ePixmap name="mb_bg" position="0,0" zPosition="1" size="' + str(size_w) + ',' + str(size_h) + '" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/skins/' + str(self.skindir) + '/images/picturebg.jpg" /> \t\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/skins/' + str(self.skindir) + '/images/icons/key-red.png" position="136,' + str(self.ButtonPosY) + '" zPosition="2" size="140,40" transparent="1" alphatest="on" /> \t\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/skins/' + str(self.skindir) + '/images/icons/key-green.png" position="422,' + str(self.ButtonPosY) + '" zPosition="2" size="140,40" transparent="1" alphatest="on" /> \t\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/skins/' + str(self.skindir) + '/images/icons/key-yellow.png" position="708,' + str(self.ButtonPosY) + '" zPosition="2" size="140,40" transparent="1" alphatest="on" /> \t\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/skins/' + str(self.skindir) + '/images/icons/key-blue.png" position="994,' + str(self.ButtonPosY) + '" zPosition="2" size="140,40" transparent="1" alphatest="on" /> \t\t\t<widget name="key_red" position="136,' + str(self.ButtonPosY) + '" zPosition="3" size="140,40" font="Regular;20" valign="center" halign="center" backgroundColor="#9f1313" transparent="1" /> \t\t\t<widget name="key_green" position="422,' + str(self.ButtonPosY) + '" zPosition="3" size="140,40" font="Regular;20" valign="center" halign="center" backgroundColor="#1f771f" transparent="1" /> \t\t\t<widget name="key_yellow" position="708,' + str(self.ButtonPosY) + '" zPosition="3" size="140,40" font="Regular;20" valign="center" halign="center" backgroundColor="#a08500" transparent="1" /> \t\t\t<widget name="key_blue" position="994,' + str(self.ButtonPosY) + '" zPosition="3" size="140,40" font="Regular;20" valign="center" halign="center" backgroundColor="#18188b" transparent="1" /> \t\t\t<eLabel position="0,0" zPosition="0" size="' + str(size_w) + ',' + str(size_h) + '" backgroundColor="' + self.color + '" /> \t\t\t<widget name="frame" position="35,30" size="' + str(self.picX + 1) + ',' + str(self.picY + 10) + '" pixmap="pic_frame.png" zPosition="3" alphatest="on" />' + skincontent + '</screen>'
        Screen.__init__(self, session)
        self['actions'] = HelpableActionMap(self, 'MC_PictureViewerActions', {'ok': (self.KeyOk, 'Show Picture'),
         'cancel': (self.Exit, 'Exit Picture Viewer'),
         'left': (self.key_left, 'List Top'),
         'right': (self.key_right, 'List Bottom'),
         'up': (self.key_up, 'List up'),
         'down': (self.key_down, 'List down'),
         'info': (self.StartExif, 'Show File Info'),
         'green': (self.startslideshow, 'Start Slideshow'),
         'yellow': (self.close, 'File View'),
         'blue': (self.Settings, 'Settings')}, -2)
        self['frame'] = MovingPixmap()
        for x in range(self.thumbsC):
            self['label' + str(x)] = Label()
            self['thumb' + str(x)] = Pixmap()

        self.Thumbnaillist = []
        self.filelist = []
        self.currPage = -1
        self.dirlistcount = 0
        self.path = path
        index = 0
        framePos = 0
        Page = 0
        for x in piclist:
            if x[0][1] == False:
                self.filelist.append((index,
                 framePos,
                 Page,
                 x[0][0],
                 path + x[0][0]))
                index += 1
                framePos += 1
                if framePos > self.thumbsC - 1:
                    framePos = 0
                    Page += 1
            else:
                self.dirlistcount += 1

        self.maxentry = len(self.filelist) - 1
        self.index = lastindex - self.dirlistcount
        if self.index < 0:
            self.index = 0
        self.picload = ePicLoad()
        self.picload.PictureData.get().append(self.showPic)
        self.onLayoutFinish.append(self.setPicloadConf)
        self.ThumbTimer = eTimer()
        self.ThumbTimer.callback.append(self.showPic)

    def setPicloadConf(self):
        sc = getScale()
        self.picload.setPara([self['thumb0'].instance.size().width(),
         self['thumb0'].instance.size().height(),
         sc[0],
         sc[1],
         config.plugins.mc_pp.cache.value,
         int(config.plugins.mc_pp.resize.value),
         self.color])
        self.paintFrame()

    def paintFrame(self):
        if self.maxentry < self.index or self.index < 0:
            return
        pos = self.positionlist[self.filelist[self.index][T_FRAME_POS]]
        self['frame'].moveTo(pos[0], pos[1], 1)
        self['frame'].startMoving()
        if self.currPage != self.filelist[self.index][T_PAGE]:
            self.currPage = self.filelist[self.index][T_PAGE]
            self.newPage()

    def newPage(self):
        self.Thumbnaillist = []
        for x in range(self.thumbsC):
            self['label' + str(x)].setText('')
            self['thumb' + str(x)].hide()

        for x in self.filelist:
            if x[T_PAGE] == self.currPage:
                self['label' + str(x[T_FRAME_POS])].setText('(' + str(x[T_INDEX] + 1) + ') ' + x[T_NAME])
                self.Thumbnaillist.append([0, x[T_FRAME_POS], x[T_FULL]])

        self.showPic()

    def showPic(self, picInfo = ''):
        for x in range(len(self.Thumbnaillist)):
            if self.Thumbnaillist[x][0] == 0:
                if self.picload.getThumbnail(self.Thumbnaillist[x][2]) == 1:
                    self.ThumbTimer.start(500, True)
                else:
                    self.Thumbnaillist[x][0] = 1
                break
            elif self.Thumbnaillist[x][0] == 1:
                self.Thumbnaillist[x][0] = 2
                ptr = self.picload.getData()
                if ptr != None:
                    self['thumb' + str(self.Thumbnaillist[x][1])].instance.setPixmap(ptr.__deref__())
                    self['thumb' + str(self.Thumbnaillist[x][1])].show()

    def key_left(self):
        self.index -= 1
        if self.index < 0:
            self.index = self.maxentry
        self.paintFrame()

    def key_right(self):
        self.index += 1
        if self.index > self.maxentry:
            self.index = 0
        self.paintFrame()

    def key_up(self):
        self.index -= self.thumbsX
        if self.index < 0:
            self.index = self.maxentry
        self.paintFrame()

    def key_down(self):
        self.index += self.thumbsX
        if self.index > self.maxentry:
            self.index = 0
        self.paintFrame()

    def StartExif(self):
        if self.maxentry < 0:
            return
        self.session.open(Pic_Exif, self.picload.getInfo(self.filelist[self.index][T_FULL]))

    def KeyOk(self):
        if self.maxentry < 0:
            return
        self.old_index = self.index
        self.session.openWithCallback(self.callbackView, MC_PicView, self.filelist, self.index, self.path, False)

    def startslideshow(self):
        if self.maxentry < 0:
            return
        self.session.openWithCallback(self.callbackView, MC_PicView, self.filelist, self.index, self.path, True)

    def Settings(self):
        self.session.open(MC_PicSetup)

    def callbackView(self, val = 0):
        self.index = val
        if self.old_index != self.index:
            self.paintFrame()

    def Exit(self):
        del self.picload
        self.close(self.index + self.dirlistcount)


class MC_PicView(Screen):

    def __init__(self, session, filelist, index, path, startslide):
        skin = '\n\t\t\t<screen name="MC_PicView" position="0,0" size="0,0" title="" >\n\t\t\t'
        Screen.__init__(self, session)
        self['actions'] = ActionMap(['MC_AudioPlayerActions'], {'cancel': self.Exit,
         'playpause': self.PlayPause,
         'next': self.nextPic,
         'previous': self.prevPic,
         'left': self.prevPic,
         'right': self.nextPic,
         'showEventInfo': self.StartExif}, -1)
        self['point'] = Pixmap()
        self['pic'] = Pixmap()
        self['play_icon'] = Pixmap()
        self['file'] = Label(_('please wait, loading picture...'))
        self.service = None
        self.old_index = 0
        self.filelist = []
        self.lastindex = index
        self.currPic = []
        self.shownow = True
        self.dirlistcount = 0
        for x in filelist:
            if len(filelist[0]) == 3:
                if x[0][1] == False:
                    self.filelist.append(path + x[0][0])
                else:
                    self.dirlistcount += 1
            else:
                self.filelist.append(x[T_FULL])

        self.maxentry = len(self.filelist) - 1
        self.index = index - self.dirlistcount
        if self.index < 0:
            self.index = 0
        self.slideTimer = eTimer()
        self.slideTimer.callback.append(self.slidePic)
        if self.maxentry >= 0:
            self.onLayoutFinish.append(self.start_decode)
        if startslide == True:
            self.slideTimer.start(config.plugins.mc_pp.slidetime.value * 1000)

    def ShowPicture(self):
        if self.shownow:
            self.shownow = False
            self.currPic = []
            self.next()
            self.lastindex = self.index
            self.start_decode()

    def start_decode(self):
        newref = eServiceReference(4370, 0, self.filelist[self.index])
        if self.service:
            self.session.nav.stopService()
            self.service = None
        self.session.nav.playService(newref)
        self.service = self.session.nav.getCurrentService()

    def next(self):
        self.index += 1
        if self.index > self.maxentry:
            self.index = 0

    def prev(self):
        self.index -= 1
        if self.index < 0:
            self.index = self.maxentry

    def slidePic(self):
        print 'slide to next Picture index=' + str(self.lastindex)
        if config.plugins.mc_pp.loop.value == False and self.lastindex == self.maxentry:
            self.exit()
        self.shownow = True
        self.ShowPicture()

    def PlayPause(self):
        if self.slideTimer.isActive():
            self.slideTimer.stop()
        else:
            self.slideTimer.start(config.plugins.mc_pp.slidetime.value * 1000)
            self.nextPic()

    def prevPic(self):
        self.currPic = []
        self.index = self.lastindex
        self.prev()
        self.start_decode()
        self.shownow = True

    def nextPic(self):
        self.shownow = True
        self.ShowPicture()

    def StartExif(self):
        if self.maxentry < 0:
            return
        self.session.open(Pic_Exif, self.picload.getInfo(self.filelist[self.lastindex]))

    def Exit(self):
        if self.service:
            self.session.nav.stopService()
            self.service = None
        self.close(self.lastindex + self.dirlistcount)


class Pic_Exif(Screen):
    skin = '<screen position="80,120" size="560,360" title="Info" >\n\t\t\t\t<widget source="menu" render="Listbox" position="0,0" size="560,360" scrollbarMode="showOnDemand" selectionDisabled="1" >\n\t\t\t\t<convert type="TemplatedMultiContent">\n\t\t\t\t\t{"template": [  MultiContentEntryText(pos = (5, 5), size = (250, 30), flags = RT_HALIGN_LEFT, text = 0), MultiContentEntryText(pos = (260, 5), size = (290, 30), flags = RT_HALIGN_LEFT, text = 1)], "fonts": [gFont("Regular", 20)], "itemHeight": 30 }\n\t\t\t\t</convert>\n\t\t\t\t</widget>\n\t\t\t</screen>'

    def __init__(self, session, exiflist):
        Screen.__init__(self, session)
        self['actions'] = ActionMap(['OkCancelActions'], {'cancel': self.close}, -1)
        exifdesc = [_('filename') + ':',
         'EXIF-Version:',
         'Make:',
         'Camera:',
         'Date/Time:',
         'Width / Height:',
         'Flash used:',
         'Orientation:',
         'User Comments:',
         'Metering Mode:',
         'Exposure Program:',
         'Light Source:',
         'CompressedBitsPerPixel:',
         'ISO Speed Rating:',
         'X-Resolution:',
         'Y-Resolution:',
         'Resolution Unit:',
         'Brightness:',
         'Exposure Time:',
         'Exposure Bias:',
         'Distance:',
         'CCD-Width:',
         'ApertureFNumber:']
        list = []
        for x in range(len(exiflist)):
            if x > 0:
                list.append((exifdesc[x], exiflist[x]))
            else:
                name = exiflist[x].split('/')[-1]
                list.append((exifdesc[x], name))

        self['menu'] = List(list)


class MC_PicSetup(Screen):

    def __init__(self, session):
        self.skin = '<screen position="120,180" size="480,310" title="Settings" >\n\t\t\t\t\t<widget name="liste" position="5,5" size="470,300" scrollbarMode="showOnDemand" />\n\t\t\t\t</screen>'
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
        self['liste'] = ConfigList(self.list)
        self.list.append(getConfigListEntry(_('Slideshow Interval (sec.)'), config.plugins.mc_pp.slidetime))
        self.list.append(getConfigListEntry(_('Scaling Mode'), config.plugins.mc_pp.resize))
        self.list.append(getConfigListEntry(_('Cache Thumbnails'), config.plugins.mc_pp.cache))
        self.list.append(getConfigListEntry(_('Thumbnail Width'), config.plugins.mc_pp.ThumbWidth))
        self.list.append(getConfigListEntry(_('Thumbnail Height'), config.plugins.mc_pp.ThumbHeight))
        self.list.append(getConfigListEntry(_('show Infoline'), config.plugins.mc_pp.infoline))
        self.list.append(getConfigListEntry(_('Frame size in full view'), config.plugins.mc_pp.framesize))
        self.list.append(getConfigListEntry(_('slide picture in loop'), config.plugins.mc_pp.loop))
        self.list.append(getConfigListEntry(_('backgroundcolor'), config.plugins.mc_pp.bgcolor))
        self.list.append(getConfigListEntry(_('textcolor'), config.plugins.mc_pp.textcolor))

    def keyLeft(self):
        self['liste'].handleKey(KEY_LEFT)

    def keyRight(self):
        self['liste'].handleKey(KEY_RIGHT)

    def keyNumber(self, number):
        self['liste'].handleKey(KEY_0 + number)


class MC_FolderOptions(Screen):
    skin = '\n\t\t<screen position="160,200" size="400,200" title="Media Center - Folder Options" >\n\t\t\t<widget source="pathlabel" transparent="1" render="Label" zPosition="2" position="0,180" size="380,20" font="Regular;16" />\n\t\t\t<widget source="menu" render="Listbox" zPosition="5" transparent="1" position="10,10" size="380,160" scrollbarMode="showOnDemand" >\n\t\t\t\t<convert type="StringList" />\n\t\t\t</widget>\n\t\t</screen>'

    def __init__(self, session, directory, dirname):
        self.skin = MC_FolderOptions.skin
        Screen.__init__(self, session)
        self.dirname = dirname
        self.directory = directory
        self.list = []
        self.list.append(('Delete File \\ Folder', 'delete', 'menu_delete', '50'))
        self['menu'] = List(self.list)
        self['pathlabel'] = StaticText('Folder: ' + self.directory)
        self['actions'] = ActionMap(['OkCancelActions'], {'cancel': self.Exit,
         'ok': self.okbuttonClick}, -1)

    def okbuttonClick(self):
        print 'okbuttonClick'
        selection = self['menu'].getCurrent()
        if selection is not None:
            if selection[1] == 'delete':
                self.removedir()
            else:
                self.close()
        else:
            self.close()

    def removedir(self):
        self.session.openWithCallback(self.deleteConfirm, MessageBox, _('Are you sure to delete this file \\ folder?'))

    def deleteConfirm(self, result):
        if result:
            try:
                os.rmdir(self.directory)
            except os.error:
                self.session.open(MessageBox, 'Error: Cannot remove file \\ folder\n', MessageBox.TYPE_INFO)

            self.close()

    def Exit(self):
        self.close()
