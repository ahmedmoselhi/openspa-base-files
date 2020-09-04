from Screens.Standby import TryQuitMainloop
from Screens.ServiceInfo import ServiceInfoList, ServiceInfoListEntry
from Components.ActionMap import ActionMap, NumberActionMap
from Components.Pixmap import Pixmap, MovingPixmap
from Components.Label import Label
from Screens.MessageBox import MessageBox
from Components.Sources.List import List
from Components.Sources.StaticText import StaticText
from Components.MenuList import MenuList
from Components.ConfigList import ConfigList, ConfigListScreen
from Components.Console import Console
from Components.ScrollLabel import ScrollLabel
from Components.config import *
from Components.Button import Button
from Tools.Directories import resolveFilename, fileExists, pathExists, createDir, SCOPE_MEDIA
from Components.FileList import FileList
from Components.AVSwitch import AVSwitch
from Plugins.Plugin import PluginDescriptor
try:
    from twisted.web.client import getPage
except Exception as e:
    print 'Media Center: Import twisted.web.client failed'

from os import path, walk
from enigma import eServiceReference
import os
config.plugins.mc_globalsettings = ConfigSubsection()
config.plugins.mc_globalsettings.showinmainmenu = ConfigYesNo(default=False)

class MC_Settings(Screen):

    def __init__(self, session):
        Screen.__init__(self, session)
        self['actions'] = NumberActionMap(['SetupActions', 'OkCancelActions'], {'ok': self.okbuttonClick,
         'cancel': self.save,
         'home': self.close,
         'red': self.save,
         'green': self.save,
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
        self.conflist = []
        self['configlist'] = ConfigList(self.conflist)
        self.conflist.append(getConfigListEntry(_('Show MC in Main-Menu'), config.plugins.mc_globalsettings.showinmainmenu))

    def okbuttonClick(self):
        selection = self['configlist'].getCurrent()
        if selection is not None:
            if selection[1] == 'MCS_SkinSelector':
                self.session.open(MCS_SkinSelector)
            elif selection[1] == 'MCS_Update':
                self.session.open(MCS_Update)
            else:
                print 'config option selected'

    def keyLeft(self):
        self.processConfigKey(KEY_LEFT)

    def keyRight(self):
        self.processConfigKey(KEY_RIGHT)

    def keyNumber(self, number):
        self.processConfigKey(KEY_0 + number)

    def processConfigKey(self, key):
        selection = self['configlist'].getCurrent()
        if selection[1] != 'MCS_SkinSelector' and selection[1] != 'MCS_Update':
            self['configlist'].handleKey(key)

    def save(self):
        config.plugins.mc_globalsettings.save()
        configfile.save()
        self.close()


class MCS_SkinSelector(Screen):
    skin = '\n\t\t<screen position="75,138" size="600,320" title="Choose your Skin" >\n\t\t\t<widget name="SkinList" position="10,10" size="275,300" scrollbarMode="showOnDemand" />\n\t\t\t<widget name="Preview" position="305,45" size="280,210" alphatest="on"/>\n\t\t</screen>\n\t\t'
    skinlist = []
    root = '/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/skins/'

    def __init__(self, session, args = None):
        self.skin = MCS_SkinSelector.skin
        Screen.__init__(self, session)
        self.skinlist = []
        self.previewPath = ''
        path.walk(self.root, self.find, '')
        self.skinlist.sort()
        self['SkinList'] = MenuList(self.skinlist)
        self['Preview'] = Pixmap()
        self['actions'] = NumberActionMap(['WizardActions', 'InputActions', 'EPGSelectActions'], {'ok': self.ok,
         'back': self.close,
         'up': self.up,
         'down': self.down,
         'left': self.left,
         'right': self.right}, -1)
        self.onLayoutFinish.append(self.layoutFinished)

    def layoutFinished(self):
        tmp = config.plugins.mc_globalsettings.currentskin.path.value.find('/skin.xml')
        if tmp != -1:
            tmp = config.plugins.mc_globalsettings.currentskin.path.value[:tmp]
            idx = 0
            for skin in self.skinlist:
                if skin == tmp:
                    break
                idx += 1

            if idx < len(self.skinlist):
                self['SkinList'].moveToIndex(idx)
        self.loadPreview()

    def up(self):
        self['SkinList'].up()
        self.loadPreview()

    def down(self):
        self['SkinList'].down()
        self.loadPreview()

    def left(self):
        self['SkinList'].pageUp()
        self.loadPreview()

    def right(self):
        self['SkinList'].pageDown()
        self.loadPreview()

    def find(self, arg, dirname, names):
        for x in names:
            if x == 'skin.xml':
                if dirname != self.root:
                    foldername = dirname.split('/')
                    subdir = foldername[-1]
                    self.skinlist.append(subdir)
                else:
                    subdir = 'Default Skin'
                    self.skinlist.append(subdir)

    def ok(self):
        if self['SkinList'].getCurrent() == 'Default Skin':
            skinfile = 'default/skin.xml'
        else:
            skinfile = self['SkinList'].getCurrent() + '/skin.xml'
        print 'Skinselector: Selected Skin: ' + self.root + skinfile
        config.plugins.mc_globalsettings.currentskin.path.value = skinfile
        config.plugins.mc_globalsettings.currentskin.path.save()
        restartbox = self.session.openWithCallback(self.restartGUI, MessageBox, _('GUI needs a restart to apply a new skin\nDo you want to Restart the GUI now?'), MessageBox.TYPE_YESNO)
        restartbox.setTitle(_('Restart GUI now?'))

    def loadPreview(self):
        if self['SkinList'].getCurrent() == 'Default Skin':
            pngpath = self.root + '/preview.png'
        else:
            pngpath = self.root + self['SkinList'].getCurrent() + '/preview.png'
        if not path.exists(pngpath):
            pngpath = '/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/skins/noprev.png'
        if self.previewPath != pngpath:
            self.previewPath = pngpath
        self['Preview'].instance.setPixmapFromFile(self.previewPath)

    def restartGUI(self, answer):
        if answer is True:
            self.session.open(TryQuitMainloop, 3)


class MCS_Update(Screen):
    skin = '\n\t\t<screen position="110,110" size="500,380" title="Media Center - Software Update" >\n\t\t\t<widget name="text" position="10,10" size="480,360" font="Regular;20" />\n\t\t</screen>'

    def __init__(self, session):
        self.skin = MCS_Update.skin
        Screen.__init__(self, session)
        self.working = False
        self.Console = Console()
        self['text'] = ScrollLabel('Checking for updates ...')
        self['actions'] = NumberActionMap(['WizardActions', 'InputActions', 'EPGSelectActions'], {'ok': self.close,
         'back': self.close}, -1)
        self.url = 'http://www.homeys-bunker.de/dm800/projects/MediaCenter/'
        self.onFirstExecBegin.append(self.CheckForMCUpdate)

    def CheckForMCUpdate(self):
        try:
            getPage(self.url + 'currentversion.txt').addCallback(self.GotMCUpdateInfo).addErrback(self.error)
            self['text'].setText(_('Checking for updates ...'))
        except Exception as e:
            self['text'].setText(_('Error: Twisted-Web not installed'))

    def GotMCUpdateInfo(self, html):
        tmp_infolines = html.splitlines()
        remoteversion = tmp_infolines[0]
        if config.plugins.mc_globalsettings.currentplatform.value == 'mipsel':
            self.installfilename = tmp_infolines[1]
        elif config.plugins.mc_globalsettings.currentplatform.value == 'powerpc':
            self.installfilename = tmp_infolines[2]
        else:
            self.installfilename = ''
            return
        if config.plugins.mc_globalsettings.currentversion.value < remoteversion:
            self['text'].setText('A new version of MediaCenter is available :-)\n\nInstall: %s' % self.installfilename)
            self.initupdate()
        else:
            self['text'].setText('Your MediaCenter is up to date! No update required ...')

    def initupdate(self):
        self.working = True
        if self.installfilename != '':
            cmd = 'ipkg install -force-overwrite ' + str(self.url) + str(self.installfilename)
            self['text'].setText('Updating MediaCenter ...\n\n\nStay tuned :-)')
            self.Console.ePopen(cmd, self.startupdate)

    def startupdate(self, result, retval, extra_args):
        if retval == 0:
            self.working = True
            self['text'].setText(result)
            self.session.open(MessageBox, 'Your MediaCenter was hopefully updated now ...\n\nYou have to restart Enigma now!', MessageBox.TYPE_INFO)
        else:
            self.working = False
