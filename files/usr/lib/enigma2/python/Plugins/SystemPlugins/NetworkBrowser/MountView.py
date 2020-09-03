from __init__ import _
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.Sources.StaticText import StaticText
from Components.ActionMap import ActionMap
from Components.Network import iNetwork
from Components.Sources.List import List
from Tools.LoadPixmap import LoadPixmap
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_SKIN_IMAGE, SCOPE_ACTIVE_SKIN, fileExists
from AutoMount import iAutoMount, AutoMount
from MountEdit import AutoMountEdit

class AutoMountView(Screen):
    skin = '\n\t\t<screen name="AutoMountView" position="90,140" size="560,350" title="MountView">\n\t\t\t<ePixmap pixmap="skin_default/buttons/red.png" position="0,0" size="140,40" alphatest="on" />\n\t\t\t<ePixmap pixmap="skin_default/buttons/yellow.png" position="280,0" size="140,40" alphatest="on" />\n\t\t\t<widget source="key_red" render="Label" position="0,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />\n\t\t\t<widget source="key_yellow" render="Label" position="280,0" zPosition="1" size="140,40" font="Regular;20" halign="center" valign="center" backgroundColor="#a08500" transparent="1" />\n\t\t\t<widget source="legend1" render="Label" position="0,50" zPosition="1" size="130,40" font="Regular;18" halign="center" valign="center" backgroundColor="#25062748" transparent="1" />\n\t\t\t<widget source="legend2" render="Label" position="130,50" zPosition="1" size="310,40" font="Regular;18" halign="center" valign="center" backgroundColor="#25062748" transparent="1" />\n\t\t\t<widget source="legend3" render="Label" position="410,50" zPosition="1" size="100,40" font="Regular;18" halign="center" valign="center" backgroundColor="#25062748" transparent="1" />\n\t\t\t<ePixmap pixmap="skin_default/div-h.png" position="0,90" zPosition="2" size="560,2" />\n\t\t\t<widget source="config" render="Listbox" position="5,100" size="555,200" scrollbarMode="showOnDemand">\n\t\t\t\t<convert type="TemplatedMultiContent">\n\t\t\t\t\t{"template": [\n\t\t\t\t\t\t\tMultiContentEntryPixmapAlphaTest(pos = (15, 1), size = (48, 48), png = 0), # index 0 is the isMounted pixmap\n\t\t\t\t\t\t\tMultiContentEntryText(pos = (100, 3), size = (200, 25), font=0, flags = RT_HALIGN_LEFT, text = 1), # index 1 is the sharename\n\t\t\t\t\t\t\tMultiContentEntryText(pos = (290, 5), size = (150, 17), font=1, flags = RT_HALIGN_LEFT, text = 2), # index 2 is the IPdescription\n\t\t\t\t\t\t\tMultiContentEntryText(pos = (100, 29), size = (350, 17), font=1, flags = RT_HALIGN_LEFT, text = 3), # index 3 is the DIRdescription\n\t\t\t\t\t\t\tMultiContentEntryPixmapAlphaTest(pos = (450, 9), size = (48, 48), png = 4), # index 4 is the activepng pixmap\n\t\t\t\t\t\t\tMultiContentEntryPixmapAlphaTest(pos = (480, 1), size = (48, 48), png = 5), # index 4 is the mounttype pixmap\n\t\t\t\t\t\t],\n\t\t\t\t\t"fonts": [gFont("Regular", 20),gFont("Regular", 14)],\n\t\t\t\t\t"itemHeight": 50\n\t\t\t\t\t}\n\t\t\t\t</convert>\n\t\t\t</widget>\n\t\t\t<ePixmap pixmap="skin_default/div-h.png" position="0,310" zPosition="1" size="560,2" />\n\t\t\t<widget source="introduction" render="Label" position="110,320" size="300,20" zPosition="10" font="Regular;21" halign="center" valign="center" backgroundColor="#25062748" transparent="1" />\n\t\t</screen>'

    def __init__(self, session, plugin_path):
        self.skin_path = plugin_path
        self.session = session
        Screen.__init__(self, session)
        self.mounts = None
        self.applyConfigRef = None
        self['shortcuts'] = ActionMap(['ShortcutActions', 'WizardActions'], {'ok': self.keyOK,
         'back': self.exit,
         'cancel': self.exit,
         'red': self.exit,
         'yellow': self.delete})
        self['legend1'] = StaticText(_('Mounted/\nUnmounted'))
        self['legend2'] = StaticText(_('Mount informations'))
        self['legend3'] = StaticText(_('Active/\nInactive'))
        self['introduction'] = StaticText(_('Press OK to edit the settings.'))
        self['key_red'] = StaticText(_('Close'))
        self['key_yellow'] = StaticText(_('Delete mount'))
        self.list = []
        self['config'] = List(self.list)
        self.showMountsList()

    def showMountsList(self):
        self.list = []
        self.mounts = iAutoMount.getMountsList()
        for sharename in self.mounts.keys():
            mountentry = iAutoMount.automounts[sharename]
            self.list.append(self.buildMountViewItem(mountentry))

        self['config'].setList(self.list)

    def buildMountViewItem(self, entry):
        if entry['isMounted'] is True:
            if fileExists(resolveFilename(SCOPE_ACTIVE_SKIN, 'networkbrowser/ok.png')):
                isMountedpng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_ACTIVE_SKIN, 'networkbrowser/ok.png'))
            else:
                isMountedpng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, 'SystemPlugins/NetworkBrowser/icons/ok.png'))
        if entry['isMounted'] is False:
            if fileExists(resolveFilename(SCOPE_ACTIVE_SKIN, 'networkbrowser/cancel.png')):
                isMountedpng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_ACTIVE_SKIN, 'networkbrowser/cancel.png'))
            else:
                isMountedpng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, 'SystemPlugins/NetworkBrowser/icons/cancel.png'))
        sharename = entry['sharename']
        IPdescription = _('IP:') + ' ' + str(entry['ip'])
        DIRdescription = _('Dir:') + ' ' + str(entry['sharedir'])
        if entry['active'] == 'True' or entry['active'] == True:
            if fileExists(resolveFilename(SCOPE_ACTIVE_SKIN, 'icons/lock_on.png')):
                activepng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_ACTIVE_SKIN, 'icons/lock_on.png'))
            else:
                activepng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_SKIN_IMAGE, 'skin_default/icons/lock_on.png'))
        if entry['active'] == 'False' or entry['active'] == False:
            if fileExists(resolveFilename(SCOPE_ACTIVE_SKIN, 'icons/lock_error.png')):
                activepng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_ACTIVE_SKIN, 'icons/lock_error.png'))
            else:
                activepng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_SKIN_IMAGE, 'skin_default/icons/lock_error.png'))
        if entry['mounttype'] == 'nfs':
            if fileExists(resolveFilename(SCOPE_ACTIVE_SKIN, 'networkbrowser/i-nfs.png')):
                mounttypepng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_ACTIVE_SKIN, 'networkbrowser/i-nfs.png'))
            else:
                mounttypepng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, 'SystemPlugins/NetworkBrowser/icons/i-nfs.png'))
        if entry['mounttype'] == 'cifs':
            if fileExists(resolveFilename(SCOPE_ACTIVE_SKIN, 'networkbrowser/i-smb.png')):
                mounttypepng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_ACTIVE_SKIN, 'networkbrowser/i-smb.png'))
            else:
                mounttypepng = LoadPixmap(cached=True, path=resolveFilename(SCOPE_PLUGINS, 'SystemPlugins/NetworkBrowser/icons/i-smb.png'))
        return (isMountedpng,
         sharename,
         IPdescription,
         DIRdescription,
         activepng,
         mounttypepng)

    def exit(self):
        self.close()

    def keyOK(self, returnValue = None):
        cur = self['config'].getCurrent()
        if cur:
            returnValue = cur[1]
            self.session.openWithCallback(self.MountEditClosed, AutoMountEdit, self.skin_path, iAutoMount.automounts[returnValue])

    def MountEditClosed(self, returnValue = None):
        if returnValue == None:
            self.showMountsList()

    def delete(self, returnValue = None):
        cur = self['config'].getCurrent()
        if cur:
            returnValue = cur[1]
            self.applyConfigRef = self.session.openWithCallback(self.applyConfigfinishedCB, MessageBox, _('Please wait while removing your network mount...'), type=MessageBox.TYPE_INFO, enable_input=False)
            iAutoMount.removeMount(returnValue, self.removeDataAvail)

    def removeDataAvail(self, data):
        if data is True:
            iAutoMount.writeMountsConfig()
            iAutoMount.getAutoMountPoints(self.deleteDataAvail)

    def deleteDataAvail(self, data):
        if data is True:
            if self.applyConfigRef.execing:
                self.applyConfigRef.close(True)

    def applyConfigfinishedCB(self, data):
        if data is True:
            self.session.openWithCallback(self.ConfigfinishedCB, MessageBox, _('Your network mount has been removed.'), type=MessageBox.TYPE_INFO, timeout=10)

    def ConfigfinishedCB(self, data):
        if data is not None:
            if data is True:
                self.showMountsList()
