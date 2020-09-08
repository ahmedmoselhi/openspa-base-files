from Components.ActionMap import ActionMap, HelpableActionMap
from Components.MenuList import MenuList
from Components.Label import Label
from Components.PluginComponent import plugins
from Components.config import config, ConfigSubsection, ConfigYesNo, ConfigLocations, ConfigText, ConfigSelection, getConfigListEntry, ConfigInteger
from Components.ConfigList import ConfigListScreen
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.ChoiceBox import ChoiceBox
from Screens.Console import Console
from Screens.LocationBox import LocationBox
from Screens.HelpMenu import HelpableScreen, HelpMenu
from Components.Sources.List import List
from Plugins.Plugin import PluginDescriptor
from Screens.Standby import TryQuitMainloop
from QuickButtonList import QuickButtonList, QuickButtonListEntry
from QuickButtonXML import QuickButtonXML
from enigma import getDesktop, eTimer
from Plugins.Extensions.spazeMenu.sbar import openspaSB
from Components.Pixmap import Pixmap
from Tools.Directories import *
import xml.sax.xmlreader
import keymapparser
import os
import os.path
from __init__ import _
functionfile = '/usr/lib/enigma2/python/Plugins/Extensions/MultiQuickButton/mqbfunctions.xml'
config.plugins.QuickButton = ConfigSubsection()
config.plugins.QuickButton.enable = ConfigYesNo(default=True)
config.plugins.QuickButton.info = ConfigYesNo(default=True)
config.plugins.QuickButton.okexitstate = ConfigYesNo(default=False)
config.plugins.QuickButton.mainmenu = ConfigYesNo(default=False)
config.plugins.QuickButton.last_backupdir = ConfigText(default=resolveFilename(SCOPE_SYSETC))
config.plugins.QuickButton.backupdirs = ConfigLocations(default=[resolveFilename(SCOPE_SYSETC)])
config.plugins.QuickButton.channel1 = ConfigInteger(default=1, limits=(0, 9999))
config.plugins.QuickButton.channel2 = ConfigInteger(default=2, limits=(0, 9999))
config.plugins.QuickButton.channel3 = ConfigInteger(default=3, limits=(0, 9999))
config.plugins.QuickButton.channel4 = ConfigInteger(default=4, limits=(0, 9999))
config.plugins.QuickButton.channel5 = ConfigInteger(default=5, limits=(0, 9999))
config.plugins.QuickButton.macroI = ConfigText(default='')
config.plugins.QuickButton.macroII = ConfigText(default='')
config.plugins.QuickButton.macroIII = ConfigText(default='')
config.plugins.QuickButton.macroIV = ConfigText(default='')
config.plugins.QuickButton.macroV = ConfigText(default='')
MultiQuickButton_version = '3.0.01'
autostart = _('Autostart') + ': '
menuentry = ' '
info = _('Info') + ': '
info = _('Capture Key')
okexit = _('Key OK') + ': '
values = ('red',
 'red_long',
 'green',
 'green_long',
 'yellow',
 'yellow_long',
 'blue',
 'blue_long',
 'pvr',
 'pvr_long',
 'radio',
 'radio_long',
 'text',
 'text_long',
 'help_long',
 'info',
 'info_long',
 'end',
 'end_long',
 'home',
 'home_long',
 'cross_up',
 'cross_down',
 'cross_left',
 'cross_right',
 'previous',
 'next',
 'channelup',
 'channeldown',
 'audio',
 'ok',
 'exit',
 'play',
 'pause',
 'fastforward',
 'stop',
 'rewind',
 'tv',
 'stop_long',
 'key0',
 'pause_long',
 'back',
 'play_long',
 'forward',
 'record',
 'record_long')

class MultiQuickButton(Screen, HelpableScreen):
    textotitle = _('Remap Keys (v') + MultiQuickButton_version + ')'
    if esHD():
        skin = '\n\t\t<screen name="MultiQuickButtonOPENSPA" position="center,center" size="1500,870" title="openSPA %s">\n\t\t<widget name="list" position="7,0" size="1485,750" scrollbarMode="showOnDemand" />\n\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/menuHD.png" zPosition="2" position="22,813" size="52,37" alphatest="blend" />\n\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/okHD.png" zPosition="2" position="309,813" size="52,37" alphatest="blend" />\n\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/1HD.png" zPosition="2" position="739,810" size="52,37" alphatest="blend" />\n\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/2HD.png" zPosition="2" position="1071,810" size="52,37" alphatest="blend" />\n\t\t<widget name="key_menu" backgroundColor="#1f771f" zPosition="2" position="75,801" size="226,60" font="Regular; 18" halign="left" valign="center" transparent="1" />\n\t\t<widget name="key_1" backgroundColor="#1f771f" position="363,801" zPosition="2" size="378,60" font="Regular; 18" halign="left" valign="center" transparent="1" />\n\t\t<widget name="key_2" backgroundColor="#1f771f" position="792,801" zPosition="2" size="270,60" font="Regular; 18" halign="left" valign="center" transparent="1" />\n\t\t<widget name="key_3" backgroundColor="#1f771f" position="1123,801" zPosition="2" size="373,60" font="Regular; 18" halign="left" valign="center" transparent="1" />\n\t\t<widget name="key_help" backgroundColor="#00000000" zPosition="1" position="7,753" size="1485,45" font="Regular;17" foregroundColor="#00999999" halign="center" valign="center" transparent="1" />\n\t\t<eLabel backgroundColor="#00555555" zPosition="1" position="7,753" size="1485,1" />\n\t\t<eLabel backgroundColor="#00555555" zPosition="1" position="7,798" size="1485,1" />\n\t\t<widget name="barrapix_arr" position="0,0" zPosition="19" size="30,30" alphatest="blend" transparent="1" />\n\t\t<widget name="barrapix_abj" position="0,0" zPosition="19" size="30,30" alphatest="blend" transparent="1" />\t\t\n\t\t</screen>' % textotitle
    else:
        skin = '\n\t\t<screen name="MultiQuickButtonOPENSPA" position="center,center" size="1000,580" title="openSPA %s">\n\t\t<widget name="list" position="5,0" size="990,500" scrollbarMode="showOnDemand" />\n\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MultiQuickButton/pic/key_menu.png" zPosition="2" position="15,542" size="35,25" alphatest="on" />\n\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MultiQuickButton/pic/ok.png" zPosition="2" position="206,542" size="35,25" alphatest="on" />\n\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MultiQuickButton/pic/key_1.png" zPosition="2" position="493,540" size="35,25" alphatest="on" />\n\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MultiQuickButton/pic/key_2.png" zPosition="2" position="714,540" size="35,25" alphatest="on" />\n\t\t<widget name="key_menu" backgroundColor="#1f771f" zPosition="2" position="50,534" size="151,40" font="Regular; 18" halign="left" valign="center" transparent="1" />\n\t\t<widget name="key_1" backgroundColor="#1f771f" position="242,534" zPosition="2" size="252,40" font="Regular; 18" halign="left" valign="center" transparent="1" />\n\t\t<widget name="key_2" backgroundColor="#1f771f" position="528,534" zPosition="2" size="180,40" font="Regular; 18" halign="left" valign="center" transparent="1" />\n\t\t<widget name="key_3" backgroundColor="#1f771f" position="749,534" zPosition="2" size="249,40" font="Regular; 18" halign="left" valign="center" transparent="1" />\n\t\t<widget name="key_help" backgroundColor="#00000000" zPosition="1" position="5,502" size="990,30" font="Regular;17" foregroundColor="#00999999" halign="center" valign="center" transparent="1" />\n\t\t<eLabel backgroundColor="#00555555" zPosition="1" position="5,502" size="990,1" />\n\t\t<eLabel backgroundColor="#00555555" zPosition="1" position="5,532" size="990,1" />\n\t\t<widget name="barrapix_arr" position="0,0" zPosition="19" size="20,20" alphatest="blend" transparent="1" />\n\t\t<widget name="barrapix_abj" position="0,0" zPosition="19" size="20,20" alphatest="blend" transparent="1" />\t\t\n\t\t</screen>' % textotitle

    def __init__(self, session, args = None, mostrarayuda = False):
        Screen.__init__(self, session)
        HelpableScreen.__init__(self)
        self.session = session
        self.menu = args
        self.settigspath = ''
        self.mostrarayuda = mostrarayuda
        self.mostrarayuda2 = False
        self.list = []
        self['key_help'] = Label(_('Type key for search in list, or press (1) por advanced Capture Key'))
        self['key_menu'] = Label(_('Options'))
        self['key_1'] = Label(_('Information/Edit'))
        self['key_2'] = Label(info)
        self['key_3'] = Label(_('Graphic help'))
        self.iniciadoS = False
        self['barrapix_arr'] = Pixmap()
        self['barrapix_abj'] = Pixmap()
        self.createList()
        self['list'] = QuickButtonList(list=self.list, selection=0)
        self['actions'] = ActionMap(['OkCancelActions',
         'ColorActions',
         'NumberActions',
         'EPGSelectActions',
         'MenuActions',
         'DirectionActions'], {'ok': self.run,
         'cancel': self.close,
         'menu': self.opciones,
         '1': self.getTecla,
         'up': self.kup,
         'down': self.kdown,
         'right': self.kright,
         'left': self.kleft,
         '2': self.mayuda}, -3)
        self.kayuda = None
        self.textook = ''
        self.textoinfo = ''
        self.largo = None
        self.onShown.append(self.updateSettings)

    def mayuda(self):
        self.kayuda = None
        self.session.openWithCallback(self.cbhelp, HelpMenu, self.helpList)

    def cbhelp(self, resp = None, *args):
        if args:
            try:
                self.kayuda = str(args[1])
            except:
                pass

        if self.mostrarayuda2:
            self.mostrarayuda2 = False
            if self.kayuda:
                self.session.openWithCallback(self.cb1, MessageBox, text=_('Do you want to remap keys now?'), type=MessageBox.TYPE_YESNO, timeout=10, default=False)
            else:
                self.close()
        elif self.kayuda:
            self.cbcaptura(self.kayuda)

    def cb1(self, resp = None):
        if not resp:
            self.close()
        elif self.kayuda:
            self.cbcaptura(self.kayuda)

    def kup(self):
        self['list'].up()

    def kdown(self):
        self['list'].down()

    def kright(self):
        self['list'].pageDown()

    def kleft(self):
        self['list'].pageUp()

    def opciones(self):
        listares = []
        listares.append((info, 'getTecla'))
        listares.append((_('Channels'), 'setChannels'))
        listares.append((_('Macros'), 'configMacro'))
        listares.append((self.textoinfo, 'autostart'))
        listares.append((self.textook, 'toggleOkExit'))
        listares.append((_('Backup'), 'backup'))
        listares.append((_('Restore'), 'restoreMenu'))
        self.session.openWithCallback(self.cbopciones, ChoiceBox, _('Options'), listares)

    def cbopciones(self, answer):
        answer = answer and answer[1]
        if answer:
            if answer == 'infoKey':
                self.infoKey()
            elif answer == 'toggleOkExit':
                self.toggleOkExit()
            elif answer == 'getTecla':
                self.getTecla()
            elif answer == 'autostart':
                self.autostart()
            elif answer == 'setChannels':
                self.setChannels()
            elif answer == 'configMacro':
                self.configMacro()
            elif answer == 'backup':
                self.backup()
            elif answer == 'restoreMenu':
                self.restoreMenu()

    def getTecla(self):
        self.session.openWithCallback(self.cbcaptura, capturatecla)

    def cbcaptura(self, resp = None):
        if resp:
            if self.largo and resp in self.largo:
                self.largo = None
                return
            for ij in range(0, len(self.list)):
                if self['list'].list[ij][0][1] == resp:
                    if '_long' in resp:
                        self.largo = resp
                    else:
                        self.largo = None
                    self['list'].moveToIndex(ij)
                    return

            self.session.open(MessageBox, _('Key [%s] nonexistent.') % resp, type=MessageBox.TYPE_INFO, timeout=5)

    def infoKey(self, segs = 0):
        clave = self['list'].l.getCurrentSelection()[0][1]
        nombre = self['list'].l.getCurrentSelection()[0][0]
        accion = ''
        idx = self['list'].getSelectionIndex()
        try:
            accion = accion + str(self['list'].l.getCurrentSelection()[2][7])
        except:
            accion = 'NA'

        if segs == 0:
            mensaje = _('Key: ') + nombre + '\n'
        else:
            mensaje = _('Key pressed: ') + nombre + '\n'
        mensaje = mensaje + _('Code: ') + '[' + clave + ']\n'
        mensaje = mensaje + _('Action: ') + '' + accion.replace('[', '').replace(']', '')
        if segs == 0:
            dei = self.session.open(MessageBox, mensaje, type=MessageBox.TYPE_INFO)
        else:
            dei = self.session.open(MessageBox, mensaje, type=MessageBox.TYPE_INFO, timeout=segs)
        dei.setTitle(_('Key information'))

    def createList(self):
        self.a = None
        for button in values:
            if config.plugins.QuickButton.info.value:
                try:
                    functionbutton = ' ['
                    path = '/etc/MultiQuickButton/quickbutton_' + button + '.xml'
                    if not os.path.exists(path):
                        os.system("cp '/usr/lib/enigma2/python/Plugins/Extensions/MultiQuickButton/quickbutton_.xml' '" + path + "'")
                    menu = xml.dom.minidom.parse(path)
                    self.XML_db = QuickButtonXML(menu)
                    for a in self.XML_db.getMenu():
                        if a[1] == '1':
                            if functionbutton == ' [':
                                functionbutton = _(a[0])
                            else:
                                functionbutton = functionbutton + ' | ' + _(a[0])

                    if functionbutton == ' [':
                        space1 = ' **' + _('Not configured') + '** '
                        space2 = ' '
                        functionbutton = ' '
                    else:
                        space1 = ' ['
                        space2 = ']'
                    globals()['functionbutton_%s' % button] = ' ' + space1 + functionbutton + space2
                except Exception as a:
                    self.a = a

            else:
                globals()['functionbutton_%s' % button] = ' '

        self.list = []
        self.list.append(QuickButtonListEntry('', (_('red') + '', 'red'), 'red', functionbutton_red))
        self.list.append(QuickButtonListEntry('', (_('red') + _(' long') + '', 'red_long'), 'red', functionbutton_red_long))
        self.list.append(QuickButtonListEntry('', (_('green') + '', 'green'), 'green', functionbutton_green))
        self.list.append(QuickButtonListEntry('', (_('green') + _(' long') + '', 'green_long'), 'green', functionbutton_green_long))
        self.list.append(QuickButtonListEntry('', (_('yellow') + '', 'yellow'), 'yellow', functionbutton_yellow))
        self.list.append(QuickButtonListEntry('', (_('yellow') + _(' long') + '', 'yellow_long'), 'yellow', functionbutton_yellow_long))
        self.list.append(QuickButtonListEntry('', (_('blue') + '', 'blue'), 'blue', functionbutton_blue))
        self.list.append(QuickButtonListEntry('', (_('blue') + _(' long') + '', 'blue_long'), 'blue', functionbutton_blue_long))
        self.list.append(QuickButtonListEntry('', (_('TEXT') + '', 'text'), 'text', functionbutton_text))
        self.list.append(QuickButtonListEntry('', (_('TEXT') + _(' long') + '', 'text_long'), 'text', functionbutton_text_long))
        self.list.append(QuickButtonListEntry('', (_('HELP') + _(' long') + '', 'help_long'), 'help', functionbutton_help_long))
        self.list.append(QuickButtonListEntry('', (_('INFO/EPG') + '', 'info'), 'info', functionbutton_info))
        self.list.append(QuickButtonListEntry('', (_('INFO/EPG') + _(' long') + '', 'info_long'), 'info', functionbutton_info_long))
        self.list.append(QuickButtonListEntry('', (_('HOME') + '', 'home'), 'home', functionbutton_home))
        self.list.append(QuickButtonListEntry('', (_('HOME') + _(' long') + '', 'home_long'), 'home', functionbutton_home_long))
        self.list.append(QuickButtonListEntry('', (_('END') + '', 'end'), 'end', functionbutton_end))
        self.list.append(QuickButtonListEntry('', (_('END') + _(' long') + '', 'end_long'), 'end', functionbutton_end_long))
        self.list.append(QuickButtonListEntry('', (_('GUIDE/R-Button') + '', 'pvr'), 'guide', functionbutton_pvr))
        self.list.append(QuickButtonListEntry('', (_('GUIDE/R-Button') + _(' long') + '', 'pvr_long'), 'guide', functionbutton_pvr_long))
        self.list.append(QuickButtonListEntry('', (_('RADIO') + '', 'radio'), 'tecla', functionbutton_radio))
        self.list.append(QuickButtonListEntry('', (_('RADIO') + _(' long') + '', 'radio_long'), 'radio', functionbutton_radio_long))
        self.list.append(QuickButtonListEntry('', (_('TV') + '', 'tv'), 'tecla', functionbutton_tv))
        self.list.append(QuickButtonListEntry('', (_('Cross Up') + '', 'cross_up'), 'cross_up', functionbutton_cross_up))
        self.list.append(QuickButtonListEntry('', (_('Cross Down') + '', 'cross_down'), 'cross_down', functionbutton_cross_down))
        self.list.append(QuickButtonListEntry('', (_('Cross Left') + '', 'cross_left'), 'cross_left', functionbutton_cross_left))
        self.list.append(QuickButtonListEntry('', (_('Cross Right') + '', 'cross_right'), 'cross_right', functionbutton_cross_right))
        self.list.append(QuickButtonListEntry('', (_('Channel +') + '', 'channelup'), 'channelup', functionbutton_channelup))
        self.list.append(QuickButtonListEntry('', (_('Channel -') + '', 'channeldown'), 'channeldown', functionbutton_channeldown))
        self.list.append(QuickButtonListEntry('', (_('Forward >') + '', 'next'), 'next', functionbutton_next))
        self.list.append(QuickButtonListEntry('', (_('Backward <') + '', 'previous'), 'previous', functionbutton_previous))
        self.list.append(QuickButtonListEntry('', (_('Audio') + '', 'audio'), 'audio', functionbutton_audio))
        if config.plugins.QuickButton.okexitstate.value:
            self.list.append(QuickButtonListEntry('', ('OK', 'ok'), 'ok', functionbutton_ok))
        self.list.append(QuickButtonListEntry('', ('EXIT', 'exit'), 'exit', functionbutton_exit))
        self.list.append(QuickButtonListEntry('', (_('Play') + '', 'play'), 'play', functionbutton_play))
        self.list.append(QuickButtonListEntry('', (_('Play') + _(' long') + '', 'play_long'), 'play', functionbutton_play_long))
        self.list.append(QuickButtonListEntry('', (_('Pause') + '', 'pause'), 'pause', functionbutton_pause))
        self.list.append(QuickButtonListEntry('', (_('Pause') + _(' long') + '', 'pause_long'), 'pause', functionbutton_pause_long))
        self.list.append(QuickButtonListEntry('', ('Stop', 'stop'), 'stop', functionbutton_stop))
        self.list.append(QuickButtonListEntry('', ('Stop' + _(' long') + '', 'stop_long'), 'stop', functionbutton_stop_long))
        self.list.append(QuickButtonListEntry('', (_('Record') + '', 'record'), 'record', functionbutton_record))
        self.list.append(QuickButtonListEntry('', (_('Record') + _(' long') + '', 'record_long'), 'record', functionbutton_record_long))
        self.list.append(QuickButtonListEntry('', (_('Rewind <<') + '', 'rewind'), 'rewind', functionbutton_rewind))
        self.list.append(QuickButtonListEntry('', (_('FastForward >>') + '', 'fastforward'), 'fastforward', functionbutton_fastforward))
        self.list.append(QuickButtonListEntry('', (_('Back') + '', 'back'), 'back', functionbutton_back))
        self.list.append(QuickButtonListEntry('', (_('Fw') + '', 'forward'), 'forward', functionbutton_forward))
        self.list.append(QuickButtonListEntry('', (_('Key 0') + '', 'key0'), '0', functionbutton_key0))
        hacciones = {}
        hacciones2 = {}
        for iji in self.list:
            nombrekey = iji[0][1]
            valorkey = iji[2][7]
            if _('Not configured') not in valorkey:
                hacciones[nombrekey] = (self.nada, _(valorkey).replace('[', '').replace(']', ''))
            else:
                hacciones2[nombrekey] = self.nada

        self.helpList = []
        self['helpbuttonactions'] = myHelpableActionMap(self, 'QuickButtonActions', hacciones, -2)
        self['helpbuttonactions2'] = capMQBActionMap(['QuickButtonActions'], hacciones2, -2)

    def nada(self, key = None):
        if key == 'cross_up':
            self.kup()
        elif key == 'cross_down':
            self.kdown()
        elif key == 'cross_left':
            self.kleft()
        elif key == 'cross_right':
            self.kright()
        elif key:
            self.cbcaptura(key)

    def updateList(self):
        self.createList()
        self['list'].l.setList(self.list)

    def updateSettings(self):
        if not fileExists('/usr/bin/chkvs'):
            self.close()
        autostart_state = autostart
        menuentry_state = menuentry
        info_state = info
        okexit_state = okexit
        if config.plugins.QuickButton.enable.value:
            autostart_state += _('on')
        else:
            autostart_state += _('off')
        if config.plugins.QuickButton.mainmenu.value:
            menuentry_state += _('on')
        else:
            menuentry_state += _('off')
        if config.plugins.QuickButton.info.value:
            info_state += _('on')
        else:
            info_state += _('off')
        if config.plugins.QuickButton.okexitstate.value:
            okexit_state += _('on')
        else:
            okexit_state += _('off')
        self.textoinfo = autostart_state
        self.textook = okexit_state
        self.actualizaScrolls()
        self.iniciadoS = True
        if self.mostrarayuda:
            self.mostrarayuda = False
            self.mostrarayuda2 = True
            self.mayuda()

    def actualizaScrolls(self):
        openspaSB(objectoself=self, nombrelista='list', barra='barrapix', altoitem=25, imagen=True)

    def run(self):
        returnValue = self['list'].l.getCurrentSelection()[0][1]
        if returnValue is not None:
            if returnValue in values:
                path = '/etc/MultiQuickButton/quickbutton_' + returnValue + '.xml'
                if not os.path.exists(path):
                    os.system("cp '/usr/lib/enigma2/python/Plugins/Extensions/MultiQuickButton/quickbutton_.xml' '" + path + "'")
                nombre = self['list'].l.getCurrentSelection()[0][0]
                self.session.openWithCallback(self.updateAfterButtonChange, QuickButton, path, nombre, returnValue)

    def updateAfterButtonChange(self, res = None):
        self.updateList()

    def backup(self):
        self.session.openWithCallback(self.callBackup, BackupLocationBox, _('Please select the backup path...'), '', config.plugins.QuickButton.last_backupdir.value)

    def callBackup(self, path):
        if path is not None:
            if pathExists(path):
                config.plugins.QuickButton.last_backupdir.value = path
                config.plugins.QuickButton.last_backupdir.save()
                self.settigspath = path + 'MultiQuickButton_settings.tar.gz'
                if fileExists(self.settigspath):
                    self.session.openWithCallback(self.callOverwriteBackup, MessageBox, _('Overwrite existing Backup?.'), type=MessageBox.TYPE_YESNO)
                else:
                    com = 'tar czvf %s /etc/MultiQuickButton/' % self.settigspath
                    self.session.open(Console, _('Backup Settings...'), [com])
            else:
                self.session.open(MessageBox, _('Directory %s nonexistent.') % path, type=MessageBox.TYPE_ERROR, timeout=5)

    def callOverwriteBackup(self, res):
        if res:
            com = 'tar czvf %s /etc/MultiQuickButton/' % self.settigspath
            self.session.open(Console, _('Backup Settings...'), [com])

    def restoreMenu(self):
        listares = []
        listares.append((_('Personal backup restore'), 'personal'))
        listares.append((_('Restore Default settings'), 'default'))
        self.session.openWithCallback(self.cbrestore, ChoiceBox, _('Restore configuration'), listares)

    def cbrestore(self, answer):
        answer = answer and answer[1]
        if answer:
            if answer == 'personal':
                self.restore()
            elif answer == 'default':
                self.session.openWithCallback(self.cbdefault, MessageBox, _('Restore Default settings') + '\n' + _('Overwrite existing Settings?.'), type=MessageBox.TYPE_YESNO)

    def cbdefault(self, resp):
        if resp:
            os.system('tar -xzvf /usr/lib/enigma2/python/Plugins/Extensions/MultiQuickButton/ini/init_etc.rar.gz -C /')
            self.session.open(MessageBox, _('Default settings restored!'), type=MessageBox.TYPE_INFO, timeout=5)
            self.updateList()

    def restore(self):
        self.session.openWithCallback(self.callRestore, BackupLocationBox, _('Please select the restore path...'), '', config.plugins.QuickButton.last_backupdir.value)

    def callRestore(self, path):
        if path is not None:
            self.settigspath = path + 'MultiQuickButton_settings.tar.gz'
            if fileExists(self.settigspath):
                self.session.openWithCallback(self.callOverwriteSettings, MessageBox, _('Overwrite existing Settings?.'), type=MessageBox.TYPE_YESNO)
            else:
                self.session.open(MessageBox, _('File %s nonexistent.') % path, type=MessageBox.TYPE_ERROR, timeout=5)

    def callOverwriteSettings(self, res):
        if res:
            com = 'cd /; tar xzvf %s' % self.settigspath
            self.session.openWithCallback(self.cbrestore2, Console, _('Restore Settings...'), [com])

    def cbrestore2(self, resp = None):
        self.updateList()

    def autostart(self):
        if config.plugins.QuickButton.enable.value:
            config.plugins.QuickButton.enable.setValue(False)
            config.plugins.QuickButton.mainmenu.setValue(False)
            mens = _('Restarting Enigma2 to unset\nMulti QuickButton Autostart')
        else:
            config.plugins.QuickButton.enable.setValue(True)
            mens = _('Restarting Enigma2 to set\nMulti QuickButton Autostart')
        self.updateSettings()
        config.plugins.QuickButton.enable.save()
        self.session.openWithCallback(self.callRestart, MessageBox, mens, MessageBox.TYPE_YESNO, timeout=10)

    def setMainMenu(self):
        return
        if config.plugins.QuickButton.mainmenu.value:
            config.plugins.QuickButton.mainmenu.setValue(False)
        else:
            config.plugins.QuickButton.mainmenu.setValue(True)
        config.plugins.QuickButton.mainmenu.save()
        self.updateSettings()
        self.session.openWithCallback(self.callRestart, MessageBox, _('Restarting Enigma2 to load:\n') + _('Main menu') + _('Multi QuickButton settings'), MessageBox.TYPE_YESNO, timeout=10)

    def setInfo(self):
        return
        if config.plugins.QuickButton.info.value:
            config.plugins.QuickButton.info.setValue(False)
        else:
            config.plugins.QuickButton.info.setValue(True)
        config.plugins.QuickButton.info.save()
        self.updateList()
        self.updateSettings()

    def toggleOkExit(self):
        self.mqbkeymapfile = '/usr/lib/enigma2/python/Plugins/Extensions/MultiQuickButton/keymap.xml'
        self.mqbkeymap = open(self.mqbkeymapfile, 'r')
        self.text = self.mqbkeymap.read()
        self.mqbkeymap.close()
        self.keys = ['<key id="KEY_OK" mapto="ok" flags="m" />']
        if config.plugins.QuickButton.okexitstate.value:
            config.plugins.QuickButton.okexitstate.setValue(False)
            for self.key in self.keys:
                self.keyinactive = '<!-- ' + self.key + ' -->'
                if self.keyinactive not in self.text:
                    self.text = self.text.replace(self.key, self.keyinactive)

        else:
            config.plugins.QuickButton.okexitstate.setValue(True)
            for self.key in self.keys:
                self.keyinactive = '<!-- ' + self.key + ' -->'
                if self.keyinactive in self.text:
                    self.text = self.text.replace(self.keyinactive, self.key)

        self.mqbkeymap = open(self.mqbkeymapfile, 'w')
        self.mqbkeymap.write(self.text)
        self.mqbkeymap.close()
        keymapparser.removeKeymap(self.mqbkeymapfile)
        keymapparser.readKeymap(self.mqbkeymapfile)
        config.plugins.QuickButton.okexitstate.save()
        self.updateList()
        self.updateSettings()

    def setChannels(self):
        self.session.open(MultiQuickButtonChannelConfiguration)

    def configMacro(self):
        self.session.open(MultiQuickButtonMacro)

    def showAbout(self):
        self.session.open(MessageBox, "Multi Quickbutton idea is based on\nGP2's Quickbutton\nVersion: 2.8\nby Emanuel CLI-Team 2009\nwww.cablelinux.info\n ***special thanks*** to:\ngutemine & AliAbdul & Dr.Best ;-)\n\nChanges for VU+/Azbox/GoldenSpark by openSPA\nVersion %s" % MultiQuickButton_version, MessageBox.TYPE_INFO)

    def callRestart(self, restart):
        if restart == True:
            self.session.open(TryQuitMainloop, 3)


class BackupLocationBox(LocationBox):

    def __init__(self, session, text, filename, dir, minFree = None):
        inhibitDirs = ['/bin',
         '/boot',
         '/dev',
         '/lib',
         '/proc',
         '/sbin',
         '/sys',
         '/usr',
         '/var']
        LocationBox.__init__(self, session, text=text, filename=filename, currDir=dir, bookmarks=config.plugins.QuickButton.backupdirs, autoAdd=True, editDir=True, inhibitDirs=inhibitDirs, minFree=minFree)
        self.skinName = 'LocationBox'


class QuickButton(Screen):
    if esHD():
        skin = '\n\t\t<screen name="openSPAQuickButton" position="center,center" size="1200,870" title="QuickButton">\n\t\t<widget name="info1" backgroundColor="#000000" zPosition="1" position="15,0" size="1183,45" font="Regular;20" halign="left" valign="center" transparent="1" />\n\t\t<widget name="info2" backgroundColor="#000000" zPosition="1" position="15,52" size="1183,45" font="Regular;20" halign="left" valign="center" transparent="1" />\n\t\t<widget name="info3" backgroundColor="#000000" zPosition="1" position="15,112" size="1183,45" font="Regular;20" halign="left" valign="center" transparent="1" />\n\t\t<widget name="list" position="15,175" size="1170,562" scrollbarMode="showOnDemand" />\n\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/redHD.png" zPosition="2" position="22,775" size="37,37" alphatest="blend" />\n\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/greenHD.png" zPosition="2" position="307,775" size="37,37" alphatest="blend" />\n\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/yellowHD.png" zPosition="2" position="592,775" size="37,37" alphatest="blend" />\n\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/blueHD.png" zPosition="2" position="877,775" size="37,37" alphatest="blend" />\n\t\t<widget name="key_red" backgroundColor="#000000" zPosition="2" position="75,765" size="270,60" font="Regular;20" halign="left" valign="center" transparent="1" />\n\t\t<widget name="key_green" backgroundColor="#000000" position="360,765" zPosition="2" size="270,60" font="Regular;20" halign="left" valign="center" transparent="1" />\n\t\t<widget name="key_yellow" backgroundColor="#000000" position="645,765" zPosition="2" size="270,60" font="Regular;20" halign="left" valign="center" transparent="1" />\n\t\t<widget name="key_blue" backgroundColor="#000000" position="930,765" zPosition="2" size="270,60" font="Regular;20" halign="left" valign="center" transparent="1" />\n\t\t<eLabel name="linea1" position="0,163" size="1200,1" backgroundColor="#10777777" />\n\t\t<eLabel name="linea2" position="0,747" size="1200,1" backgroundColor="#10777777" />\n\t\t<widget name="key_help" backgroundColor="#000000" zPosition="2" position="0,825" size="1200,45" font="Regular;17" halign="center" valign="center" transparent="1" foregroundColor="#00999999" />\n\t\t<widget name="barrapix_arr" position="0,0" zPosition="19" size="30,30" alphatest="blend" transparent="1" />\n\t\t<widget name="barrapix_abj" position="0,0" zPosition="19" size="30,30" alphatest="blend" transparent="1" />\t\n\t\t</screen>'
    else:
        skin = '\n\t\t<screen name="openSPAQuickButton" position="center,center" size="800,580" title="QuickButton">\n\t\t<widget name="info1" backgroundColor="#000000" zPosition="1" position="10,0" size="789,30" font="Regular;20" halign="left" valign="center" transparent="1" />\n\t\t<widget name="info2" backgroundColor="#000000" zPosition="1" position="10,35" size="789,30" font="Regular;20" halign="left" valign="center" transparent="1" />\n\t\t<widget name="info3" backgroundColor="#000000" zPosition="1" position="10,75" size="789,30" font="Regular;20" halign="left" valign="center" transparent="1" />\n\t\t<widget name="list" position="10,117" size="780,375" scrollbarMode="showOnDemand" />\n\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MultiQuickButton/pic/button_red.png" zPosition="2" position="15,517" size="25,25" alphatest="on" />\n\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MultiQuickButton/pic/button_green.png" zPosition="2" position="205,517" size="25,25" alphatest="on" />\n\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MultiQuickButton/pic/button_yellow.png" zPosition="2" position="395,517" size="25,25" alphatest="on" />\n\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MultiQuickButton/pic/button_blue.png" zPosition="2" position="585,517" size="25,25" alphatest="on" />\n\t\t<widget name="key_red" backgroundColor="#000000" zPosition="2" position="50,510" size="180,40" font="Regular;20" halign="left" valign="center" transparent="1" />\n\t\t<widget name="key_green" backgroundColor="#000000" position="240,510" zPosition="2" size="180,40" font="Regular;20" halign="left" valign="center" transparent="1" />\n\t\t<widget name="key_yellow" backgroundColor="#000000" position="430,510" zPosition="2" size="180,40" font="Regular;20" halign="left" valign="center" transparent="1" />\n\t\t<widget name="key_blue" backgroundColor="#000000" position="620,510" zPosition="2" size="180,40" font="Regular;20" halign="left" valign="center" transparent="1" />\n\t\t<eLabel name="linea1" position="0,109" size="800,1" backgroundColor="#10777777" />\n\t\t<eLabel name="linea2" position="0,498" size="800,1" backgroundColor="#10777777" />\n\t\t<widget name="key_help" backgroundColor="#000000" zPosition="2" position="0,550" size="800,30" font="Regular;17" halign="center" valign="center" transparent="1" foregroundColor="#00999999" />\n\t\t<widget name="barrapix_arr" position="0,0" zPosition="19" size="20,20" alphatest="blend" transparent="1" />\n\t\t<widget name="barrapix_abj" position="0,0" zPosition="19" size="20,20" alphatest="blend" transparent="1" />\t\n\t\t</screen>'

    def __init__(self, session, path = None, title = '', clave = ''):
        Screen.__init__(self, session)
        self.session = session
        self.path = path
        self.newtitle = _('Information/Setup key:') + ' ' + _(title)
        self.changed = False
        self.e = None
        list = []
        try:
            menu = xml.dom.minidom.parse(self.path)
            self.XML_db = QuickButtonXML(menu)
            for e in self.XML_db.getMenu():
                if e[1] == '1':
                    list.append(QuickButtonListEntry('green', (_(e[0]), e[0], '1')))
                else:
                    list.append(QuickButtonListEntry('red', (_(e[0]), e[0], '')))

        except Exception as e:
            self.e = e
            list = []

        self['list'] = QuickButtonList(list=list, selection=0)
        self['info1'] = Label(_('Key: ') + _(title))
        self['info2'] = Label(_('Code: ') + '[' + clave + ']')
        self['info3'] = Label(_('Action: '))
        self['key_help'] = Label(_(' '))
        self['key_red'] = Label(_('Cancel'))
        self['key_green'] = Label(_('Save'))
        self['key_yellow'] = Label(_('delete'))
        self['key_blue'] = Label(_('Add'))
        self.iniciadoS = False
        self['barrapix_arr'] = Pixmap()
        self['barrapix_abj'] = Pixmap()
        self.udpacciones()
        self['actions'] = ActionMap(['OkCancelActions', 'ColorActions', 'DirectionActions'], {'ok': self.run,
         'cancel': self.cancel,
         'red': self.close,
         'green': self.save,
         'yellow': self.delete,
         'blue': self.add,
         'up': self.up,
         'down': self.down,
         'left': self.keyLeft,
         'right': self.keyRight}, -1)
        self.onExecBegin.append(self.error)
        self.onShown.append(self.updateTitle)

    def error(self):
        if self.e:
            self.session.open(MessageBox, 'XML ' + _('Error') + ': %s' % self.e, MessageBox.TYPE_ERROR)
            self.close(None)

    def udpacciones(self):
        chelp = 'Press [OK] for deactivate/activate functions.[BLUE] for add action to key.[YELLOW] for remove.'
        if len(self['list'].list) == 1:
            self['info3'].setText(_('Action: '))
        elif len(self['list'].list) > 1:
            self['info3'].setText(_('Actions: '))
        else:
            chelp = 'Press [BLUE] for add actions to this key'
            self['info3'].setText(_('Action: ') + _('Not configured'))
        self['key_help'].setText(_(chelp))
        if self.iniciadoS:
            self.actualizaScrolls()

    def updateTitle(self):
        self.setTitle(self.newtitle)
        if not self.iniciadoS:
            self.actualizaScrolls()
            self.iniciadoS = True

    def actualizaScrolls(self):
        openspaSB(objectoself=self, nombrelista='list', barra='barrapix', altoitem=25, imagen=True)

    def run(self):
        returnValue = self['list'].l.getCurrentSelection()[0][2]
        if returnValue is not None:
            if returnValue is '1':
                self.session.openWithCallback(self.runcb, MessageBox, _('Do yo want deactivate this function?'), MessageBox.TYPE_YESNO)
            else:
                self.session.openWithCallback(self.runcb, MessageBox, _('Do yo want activate this function?'), MessageBox.TYPE_YESNO)

    def runcb(self, resp):
        if resp:
            returnValue = self['list'].l.getCurrentSelection()[0][2]
            name = self['list'].l.getCurrentSelection()[0][1]
            self.changed = True
            if returnValue is not None:
                idx = 0
                if returnValue is '1':
                    list = []
                    self.XML_db.setSelection(name, '')
                    for e in self.XML_db.getMenu():
                        if e[1] == '1':
                            list.append(QuickButtonListEntry('green', (_(e[0]), e[0], '1')))
                            idx += 1
                        else:
                            list.append(QuickButtonListEntry('red', (_(e[0]), e[0], '')))

                else:
                    list = []
                    self.XML_db.setSelection(name, '1')
                    for e in self.XML_db.getMenu():
                        if e[1] == '1':
                            list.append(QuickButtonListEntry('green', (_(e[0]), e[0], '1')))
                            idx += 1
                        else:
                            list.append(QuickButtonListEntry('red', (_(e[0]), e[0], '')))

                self['list'].setList(list)

    def save(self):
        self.XML_db.saveMenu(self.path)
        self.changed = False
        self.cancel()

    def keyLeft(self):
        if len(self['list'].list) > 0:
            while 1:
                self['list'].instance.moveSelection(self['list'].instance.pageUp)
                if self['list'].l.getCurrentSelection()[0][1] != '--' or self['list'].l.getCurrentSelectionIndex() == 0:
                    break

    def keyRight(self):
        if len(self['list'].list) > 0:
            while 1:
                self['list'].instance.moveSelection(self['list'].instance.pageDown)
                if self['list'].l.getCurrentSelection()[0][1] != '--' or self['list'].l.getCurrentSelectionIndex() == len(self['list'].list) - 1:
                    break

    def up(self):
        if len(self['list'].list) > 0:
            while 1:
                self['list'].instance.moveSelection(self['list'].instance.moveUp)
                if self['list'].l.getCurrentSelection()[0][1] != '--' or self['list'].l.getCurrentSelectionIndex() == 0:
                    break

    def down(self):
        if len(self['list'].list) > 0:
            while 1:
                self['list'].instance.moveSelection(self['list'].instance.moveDown)
                if self['list'].l.getCurrentSelection()[0][1] != '--' or self['list'].l.getCurrentSelectionIndex() == len(self['list'].list) - 1:
                    break

    def getPluginsList(self):
        unic = []
        twins = ['']
        pluginlist = plugins.getPlugins([PluginDescriptor.WHERE_PLUGINMENU, PluginDescriptor.WHERE_EXTENSIONSMENU, PluginDescriptor.WHERE_EVENTINFO])
        pluginlist.sort(key=lambda p: p.name)
        for plugin in pluginlist:
            if plugin.name in twins:
                pass
            else:
                unic.append((_(plugin.name),
                 plugin.name,
                 'plugins',
                 ''))
                twins.append(plugin.name)

        return unic

    def getFunctionList(self):
        unic = []
        mqbfunctionfile = functionfile
        self.mqbfunctions = xml.dom.minidom.parse(mqbfunctionfile)
        for mqbfunction in self.mqbfunctions.getElementsByTagName('mqbfunction'):
            functionname = str(mqbfunction.getElementsByTagName('name')[0].childNodes[0].data)
            if functionname[0][0] == '-':
                linea = '------------------'
                nombrefun = linea + ' ' + _(functionname.replace('-', '')) + ' ' + linea + linea + linea + linea
            else:
                nombrefun = _(functionname)
            unic.append((nombrefun, functionname, 'functions'))

        return unic

    def add(self):
        self.changed = True
        self.session.openWithCallback(self.setNewEntryType, ChoiceBox, _('MQB Functions and Plugins'), self.getNewEntryType())

    def setNewEntryType(self, selection):
        if selection:
            if selection[1] == 'functions':
                self.addfunction()
            elif selection[1] == 'plugins':
                self.addplugin()
            else:
                self.session.open(MessageBox, _('No valid selection'), type=MessageBox.TYPE_ERROR, timeout=5)

    def getNewEntryType(self):
        entrytype = []
        entrytype.append((_('Add Functions to MQB Key'), 'functions'))
        entrytype.append((_('Add Plugins to MQB Key'), 'plugins'))
        return entrytype

    def addfunction(self):
        self.changed = True
        nkeys = ['',
         '1',
         '2',
         '3',
         '4',
         '5',
         '6',
         '7',
         '8',
         '',
         'blue',
         'yellow',
         '',
         'red']
        try:
            self.session.openWithCallback(self.QuickPluginSelected, ChoiceBox, keys=nkeys, title=_('Functions'), list=self.getFunctionList())
        except Exception as e:
            self.session.open(MessageBox, _('No valid function file found'), type=MessageBox.TYPE_ERROR, timeout=5)

    def addplugin(self):
        self.changed = True
        self.session.openWithCallback(self.QuickPluginSelected, ChoiceBox, _('Plugins'), self.getPluginsList())

    def QuickPluginSelected(self, choice):
        if choice:
            if choice[0][0] == '-':
                return
            for entry in self['list'].list:
                if entry[0][0] == choice[0]:
                    self.session.open(MessageBox, _('Entry %s already exists.') % entry[0][0], type=MessageBox.TYPE_ERROR, timeout=5)
                    return

            if choice[2] == 'plugins':
                self.XML_db.addPluginEntry(choice[1])
            elif choice[2] == 'functions':
                self.XML_db.addFunctionEntry(choice[1])
            else:
                return
            list = []
            for newEntry in self.XML_db.getMenu():
                if newEntry[1] == '1':
                    list.append(QuickButtonListEntry('green', (_(newEntry[0]), _(newEntry[0]), '1')))
                else:
                    list.append(QuickButtonListEntry('red', (_(newEntry[0]), _(newEntry[0]), '')))

            self['list'].setList(list)
            self.udpacciones()
            if len(self['list'].list) > 0:
                while 1:
                    self['list'].instance.moveSelection(self['list'].instance.moveDown)
                    if self['list'].l.getCurrentSelection()[0][1] != '--' or self['list'].l.getCurrentSelectionIndex() == len(self['list'].list) - 1:
                        break

    def delete(self):
        self.changed = True
        name = self['list'].l.getCurrentSelection()[0][1]
        if name and name != '--':
            self.XML_db.rmEntry(name)
            list = []
            for e in self.XML_db.getMenu():
                if e[1] == '1':
                    list.append(QuickButtonListEntry('green', (_(e[0]), e[0], '1')))
                else:
                    list.append(QuickButtonListEntry('red', (_(e[0]), e[0], '')))

            lastValue = '--'
            tmplist = []
            for i in list:
                if i[0][1] == '--' and lastValue == '--':
                    lastValue = ''
                else:
                    tmplist.append(i)
                    lastValue = i[0][1]

            list = tmplist
            self['list'].setList(list)
            self.udpacciones()

    def cancel(self):
        if self.changed is True:
            self.session.openWithCallback(self.callForSaveValue, MessageBox, _('Save Settings'), MessageBox.TYPE_YESNO)
        else:
            self.close(None)

    def callForSaveValue(self, result):
        if result is True:
            self.save()
            self.close(None)
        else:
            self.close(None)


class MultiQuickButtonChannelConfiguration(Screen, ConfigListScreen):
    if esHD():
        skin = '\n\t\t<screen position="center,center" size="825,450" title="MultiQuickButton Channel Selection" >\n\t\t<widget name="config" position="0,0" size="825,390" scrollbarMode="showOnDemand" itemHeight="42" />\n\t\t<widget name="buttonred" position="15,390" size="150,60" backgroundColor="red" valign="center" halign="center" zPosition="2" foregroundColor="white" font="Regular;18"/>\n\t\t<widget name="buttongreen" position="180,390" size="150,60" backgroundColor="green" valign="center" halign="center" zPosition="2" foregroundColor="white" font="Regular;18"/>\n\t\t</screen>'
    else:
        skin = '\n\t\t<screen position="center,center" size="550,300" title="MultiQuickButton Channel Selection" >\n\t\t<widget name="config" position="0,0" size="550,260" scrollbarMode="showOnDemand" />\n\t\t<widget name="buttonred" position="10,260" size="100,40" backgroundColor="red" valign="center" halign="center" zPosition="2" foregroundColor="white" font="Regular;18"/>\n\t\t<widget name="buttongreen" position="120,260" size="100,40" backgroundColor="green" valign="center" halign="center" zPosition="2" foregroundColor="white" font="Regular;18"/>\n\t\t</screen>'

    def __init__(self, session, args = 0):
        self.session = session
        Screen.__init__(self, session)
        self.createConfigList()
        self.onShown.append(self.setWindowTitle)
        ConfigListScreen.__init__(self, self.list, session=self.session, on_change=self.changedEntry)
        self['buttonred'] = Label(_('Cancel'))
        self['buttongreen'] = Label(_('OK'))
        self['setupActions'] = ActionMap(['SetupActions', 'ColorActions'], {'green': self.save,
         'red': self.cancel,
         'save': self.save,
         'cancel': self.cancel,
         'ok': self.save}, -2)

    def createConfigList(self):
        self.list = []
        self.list.append(getConfigListEntry(_('Channel') + ' 1', config.plugins.QuickButton.channel1))
        self.list.append(getConfigListEntry(_('Channel') + ' 2', config.plugins.QuickButton.channel2))
        self.list.append(getConfigListEntry(_('Channel') + ' 3', config.plugins.QuickButton.channel3))
        self.list.append(getConfigListEntry(_('Channel') + ' 4', config.plugins.QuickButton.channel4))
        self.list.append(getConfigListEntry(_('Channel') + ' 5', config.plugins.QuickButton.channel5))

    def changedEntry(self):
        self.createConfigList()
        self['config'].setList(self.list)

    def setWindowTitle(self):
        self.setTitle(_('Channel Selection'))

    def save(self):
        for x in self['config'].list:
            x[1].save()

        self.changedEntry()
        self.close(True, self.session)

    def cancel(self):
        if self['config'].isChanged():
            self.session.openWithCallback(self.cancelConfirm, MessageBox, _('Quite without saving changes ?'), MessageBox.TYPE_YESNO, default=False)
        else:
            for x in self['config'].list:
                x[1].cancel()

            self.close(False, self.session)

    def cancelConfirm(self, result):
        if result is None or result is False:
            pass
        else:
            for x in self['config'].list:
                x[1].cancel()

            self.close(False, self.session)


class MultiQuickButtonMacro(Screen):
    if esHD():
        skin = '\n\t\t<screen position="center,center" size="960,600" title="Macro configuration" >\n\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MultiQuickButton/pic/button_red.png" zPosition="2" position="15,525" size="37,37" alphatest="on" />\n\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MultiQuickButton/pic/button_green.png" zPosition="2" position="240,525" size="37,37" alphatest="on" />\n\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MultiQuickButton/pic/button_yellow.png" zPosition="2" position="495,525" size="37,37" alphatest="on" />\n\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MultiQuickButton/pic/button_blue.png" zPosition="2" position="735,525" size="37,37" alphatest="on" />\n\t\t<widget name="buttonred" backgroundColor="#1f771f" position="52,514" zPosition="2" size="375,60" font="Regular;20" halign="left" valign="center" transparent="1" />\n\t\t<widget name="buttongreen" backgroundColor="#1f771f" position="277,514" zPosition="2" size="375,60" font="Regular;20" halign="left" valign="center" transparent="1" />\n\t\t<widget name="buttonyellow" backgroundColor="#1f771f" position="532,514" zPosition="2"  size="225,60" font="Regular;20" halign="left" valign="center" transparent="1" />\n\t\t<widget name="buttonblue" backgroundColor="#1f771f" position="772,514" zPosition="2"  size="225,60" font="Regular;20" halign="left" valign="center" transparent="1" />\n\t\t<widget source="menu" render="Listbox" position="0,0" size="960,507" scrollbarMode="showOnDemand" >\n\t\t\t<convert type="TemplatedMultiContent" transparent="0">\n\t\t\t\t{"template": [\n\t\t\t\t\t\tMultiContentEntryText(pos = (52, 2), size = (620,26), font=0, flags = RT_HALIGN_LEFT|RT_VALIGN_CENTER, text = 0),\n\t\t\t\t\t],\n\t\t\t\t"fonts": [gFont("Regular", 22)],\n\t\t\t\t"itemHeight": 26\n\t\t\t\t}\n\t\t\t</convert>\n\t\t</widget>\n\t\t<widget name="barrapix_arr" position="0,0" zPosition="19" size="960,507" alphatest="blend" transparent="1" />\n\t\t<widget name="barrapix_abj" position="0,0" zPosition="19" size="30,30" alphatest="blend" transparent="1" />\t\n\t\t</screen>'
    else:
        skin = '\n\t\t<screen position="center,center" size="640,400" title="Macro configuration" >\n\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MultiQuickButton/pic/button_red.png" zPosition="2" position="10,350" size="25,25" alphatest="on" />\n\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MultiQuickButton/pic/button_green.png" zPosition="2" position="160,350" size="25,25" alphatest="on" />\n\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MultiQuickButton/pic/button_yellow.png" zPosition="2" position="330,350" size="25,25" alphatest="on" />\n\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MultiQuickButton/pic/button_blue.png" zPosition="2" position="490,350" size="25,25" alphatest="on" />\n\t\t<widget name="buttonred" backgroundColor="#1f771f" position="35,343" zPosition="2" size="250,40" font="Regular;20" halign="left" valign="center" transparent="1" />\n\t\t<widget name="buttongreen" backgroundColor="#1f771f" position="185,343" zPosition="2" size="250,40" font="Regular;20" halign="left" valign="center" transparent="1" />\n\t\t<widget name="buttonyellow" backgroundColor="#1f771f" position="355,343" zPosition="2"  size="150,40" font="Regular;20" halign="left" valign="center" transparent="1" />\n\t\t<widget name="buttonblue" backgroundColor="#1f771f" position="515,343" zPosition="2"  size="150,40" font="Regular;20" halign="left" valign="center" transparent="1" />\n\t\t<widget source="menu" render="Listbox" position="0,0" size="640,338" scrollbarMode="showOnDemand" >\n\t\t\t<convert type="TemplatedMultiContent" transparent="0">\n\t\t\t\t{"template": [\n\t\t\t\t\t\tMultiContentEntryText(pos = (52, 2), size = (620,26), font=0, flags = RT_HALIGN_LEFT|RT_VALIGN_CENTER, text = 0),\n\t\t\t\t\t],\n\t\t\t\t"fonts": [gFont("Regular", 22)],\n\t\t\t\t"itemHeight": 26\n\t\t\t\t}\n\t\t\t</convert>\n\t\t</widget>\n\t\t<widget name="barrapix_arr" position="0,0" zPosition="19" size="640,338" alphatest="blend" transparent="1" />\n\t\t<widget name="barrapix_abj" position="0,0" zPosition="19" size="20,20" alphatest="blend" transparent="1" />\t\n\t\t</screen>'

    def __init__(self, session, args = 0):
        self.session = session
        Screen.__init__(self, session)
        self.title = _('Macro configuration')
        try:
            self['title'] = StaticText(self.title)
        except:
            pass

        self.list = []
        self['menu'] = List(self.list)
        self['barrapix_arr'] = Pixmap()
        self['barrapix_abj'] = Pixmap()
        self['buttonred'] = Label(_('Exit'))
        self['buttongreen'] = Label(_('OK'))
        self['buttonyellow'] = Label()
        self['buttonblue'] = Label()
        self['setupActions'] = ActionMap(['SetupActions', 'ColorActions'], {'green': self.save,
         'red': self.cancel,
         'blue': self.addButton,
         'yellow': self.removeButton,
         'save': self.save,
         'cancel': self.cancel,
         'ok': self.keyOk}, -2)
        self.selectmacro = True
        self.configmacro = False
        self.addkey = False
        self.buttondic = {'011': '0',
         '002': '1',
         '003': '2',
         '004': '3',
         '005': '4',
         '006': '5',
         '007': '6',
         '008': '7',
         '009': '8',
         '010': '9',
         '059': _('F1'),
         '060': _('F2'),
         '061': _('F3'),
         '104': _('Page Up'),
         '109': _('Page Down'),
         '116': _('Power'),
         '136': _('Find'),
         '142': _('Sleep'),
         '217': _('Search'),
         '139': _('Menu'),
         '402': _('Channel +'),
         '403': _('Channel -'),
         '358': _('Info'),
         '352': _('OK'),
         '105': _('Cross Left'),
         '106': _('Cross Right'),
         '103': _('Cross Up'),
         '108': _('Cross Down'),
         '174': _('EXIT'),
         '398': _('red'),
         '401': _('blue'),
         '399': _('green'),
         '400': _('yellow'),
         '207': _('Play'),
         '119': _('Pause'),
         '128': _('Stop'),
         '167': _('Record'),
         '208': _('FastForward >>'),
         '168': _('Rewind <<'),
         '107': _('END'),
         '102': _('HOME'),
         '392': _('Audio'),
         '370': _('Subtitle'),
         '168': _('Rewind <<'),
         '388': _('TEXT'),
         '365': _('EPG'),
         '377': _('TV'),
         '385': _('RADIO'),
         '138': _('HELP'),
         '115': _('Volume +'),
         '114': _('Volume -'),
         '113': _('Mute'),
         '393': _('Favourites'),
         '393': _('Video Format'),
         '394': _('Directory'),
         '407': _('Forward >'),
         '412': _('Backward <'),
         '512': _('TVSat'),
         '517': _('RECALL'),
         '518': _('Playmode'),
         '519': _('USB'),
         '520': _('Portal')}
        self.onLayoutFinish.append(self.createMenu)

    def createMenu(self):
        self.textstring = _('Configure macro')
        self.list = []
        self.list.append((self.textstring + ' I', 'macroI'))
        self.list.append((self.textstring + ' II', 'macroII'))
        self.list.append((self.textstring + ' III', 'macroIII'))
        self.list.append((self.textstring + ' IV', 'macroIV'))
        self.list.append((self.textstring + ' V', 'macroV'))
        self['menu'].setList(self.list)
        openspaSB(objectoself=self, nombrelista='barrapix', barra='barrapix', altoitem=25, imagen=True)

    def keyOk(self):
        cur = self['menu'].getCurrent()
        if cur:
            self['buttonred'].setText(_('Cancel'))
            self['buttongreen'].setText(_('Save'))
            self['buttonyellow'].setText(_('Delete'))
            self['buttonblue'].setText(_('Add'))
            if self.configmacro == False and self.selectmacro == True:
                self.selectmacro = False
                self.configmacro = True
                if cur[1] == 'macroI':
                    keys = config.plugins.QuickButton.macroI.value
                elif cur[1] == 'macroII':
                    keys = config.plugins.QuickButton.macroII.value
                elif cur[1] == 'macroIII':
                    keys = config.plugins.QuickButton.macroIII.value
                elif cur[1] == 'macroIV':
                    keys = config.plugins.QuickButton.macroIV.value
                elif cur[1] == 'macroV':
                    keys = config.plugins.QuickButton.macroV.value
                self.current_macro = cur[1]
                self.macrolist = []
                for key in keys.split(','):
                    if key in self.buttondic:
                        self.macrolist.append((_('Button : ') + _(self.buttondic[key]), key))

                self['menu'].setList(self.macrolist)
            elif self.configmacro == True and self.selectmacro == False and self.addkey == True:
                self.addkey = False
                self.macrolist.append(cur)
                self['menu'].setList(self.macrolist)

    def addButton(self):
        if self.configmacro == True and self.selectmacro == False:
            self['buttonred'].setText(_('Cancel'))
            self['buttongreen'].setText(_('Ok'))
            self['buttonyellow'].setText('')
            self['buttonblue'].setText('')
            self.addkey = True
            self.buttonlist = []
            for key in sorted(self.buttondic.iterkeys()):
                self.buttonlist.append((_('Button : ') + self.buttondic[key], key))

            self['menu'].setList(self.buttonlist)

    def removeButton(self):
        if self.configmacro == True and self.selectmacro == False:
            cur = self['menu'].getCurrent()
            if cur:
                self.macrolist.remove(cur)
            self['menu'].updateList(self.macrolist)

    def save(self):
        if self.configmacro == True and self.selectmacro == False and self.addkey == False:
            self.selectmacro = True
            self.configmacro = False
            self.addkey = False
            self.new_config_value = ''
            for entry in self.macrolist:
                self.new_config_value = self.new_config_value + ',' + entry[1]

            self.new_config_value = self.new_config_value.strip(',')
            if self.current_macro == 'macroI':
                config.plugins.QuickButton.macroI.value = self.new_config_value
                config.plugins.QuickButton.macroI.save()
            elif self.current_macro == 'macroII':
                config.plugins.QuickButton.macroII.value = self.new_config_value
                config.plugins.QuickButton.macroII.save()
            elif self.current_macro == 'macroIII':
                config.plugins.QuickButton.macroIII.value = self.new_config_value
                config.plugins.QuickButton.macroIII.save()
            elif self.current_macro == 'macroIV':
                config.plugins.QuickButton.macroIV.value = self.new_config_value
                config.plugins.QuickButton.macroIV.save()
            elif self.current_macro == 'macroV':
                config.plugins.QuickButton.macroV.value = self.new_config_value
                config.plugins.QuickButton.macroV.save()
            self['buttonred'].setText(_('Exit'))
            self['buttongreen'].setText(_('Ok'))
            self['buttonyellow'].setText('')
            self['buttonblue'].setText('')
            self['menu'].setList(self.list)
        elif self.selectmacro == True:
            self.keyOk()
        else:
            self.close(True, self.session)

    def cancel(self):
        if self.selectmacro == True:
            self.close(False, self.session)
        elif self.configmacro == True and self.selectmacro == False and self.addkey == False:
            self.selectmacro = True
            self.configmacro = False
            self['buttonred'].setText(_('Exit'))
            self['buttongreen'].setText(_('Ok'))
            self['buttonyellow'].setText('')
            self['buttonblue'].setText('')
            self['menu'].setList(self.list)
        elif self.configmacro == True and self.selectmacro == False and self.addkey == True:
            self.addkey = False
            self['buttonred'].setText(_('Cancel'))
            self['buttongreen'].setText(_('Save'))
            self['buttonyellow'].setText(_('Delete'))
            self['buttonblue'].setText(_('Add'))
            self['menu'].setList(self.macrolist)


class capturatecla(Screen):
    skin = '\n\t\t<screen position="center,center" size="650,380" title="Capture Key" >\n\t\t<ePixmap name="tecla" position="10,0" size="48,62" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MultiQuickButton/img/teclafs8.png" zPosition="0" alphatest="blend" />\n\t\t<widget name="key_press" position="62,25" size="588,50" halign="left" font="Regular; 20" foregroundColor="#00999999" backgroundColor="#00000000" transparent="1"/>\n\t\t<widget name="key_info" position="10,110" size="630,230" font="Regular; 18" valign="top" halign="left" transparent="1" backgroundColor="#00000000"/>\n\t\t<widget name="key_tecla" position="0,350" size="650,30" font="Regular; 21" halign="center" backgroundColor="#00ffffff" foregroundColor="#00000000" zPosition="2" />\n\t\t</screen>'

    def __init__(self, session, args = 0):
        self.session = session
        Screen.__init__(self, session)
        self.onShown.append(self.setWindowTitle)
        self['key_tecla'] = Label('')
        self['key_tecla'].hide()
        self['key_press'] = Label(_('Press any key to capture remote control code and return to list.'))
        self['key_info'] = Label(_('* To capture long keys press long key (3 secs.)\n* You may have keys that are not configured.\n* Your remote control does not support long press.\n* You may have keys that are blocked by the system and the mapping does not work.') + '\n' + _('* On key press and return to list press info for more info about this key'))
        self.TimerTemp = eTimer()
        self.TimerTemp.callback.append(self.exit)
        self.TimerTemp.startLongTimer(30)
        self.key = None
        self['actions'] = capMQBActionMap(['QuickButtonActions'], {'red': self.quickSelectGlobal_,
         'red_long': self.quickSelectGlobal_,
         'green': self.quickSelectGlobal_,
         'green_long': self.quickSelectGlobal_,
         'yellow': self.quickSelectGlobal_,
         'yellow_long': self.quickSelectGlobal_,
         'blue': self.quickSelectGlobal_,
         'blue_long': self.quickSelectGlobal_,
         'pvr': self.quickSelectGlobal_,
         'pvr_long': self.quickSelectGlobal_,
         'radio': self.quickSelectGlobal_,
         'radio_long': self.quickSelectGlobal_,
         'tv': self.quickSelectGlobal_,
         'text': self.quickSelectGlobal_,
         'text_long': self.quickSelectGlobal_,
         'help_long': self.quickSelectGlobal_,
         'info': self.quickSelectGlobal_,
         'info_long': self.quickSelectGlobal_,
         'end': self.quickSelectGlobal_,
         'end_long': self.quickSelectGlobal_,
         'home': self.quickSelectGlobal_,
         'home_long': self.quickSelectGlobal_,
         'cross_up': self.quickSelectGlobal_,
         'cross_down': self.quickSelectGlobal_,
         'cross_left': self.quickSelectGlobal_,
         'cross_right': self.quickSelectGlobal_,
         'channeldown': self.quickSelectGlobal_,
         'channelup': self.quickSelectGlobal_,
         'next': self.quickSelectGlobal_,
         'previous': self.quickSelectGlobal_,
         'audio': self.quickSelectGlobal_,
         'ok': self.quickSelectGlobal_,
         'exit': self.quickSelectGlobal_,
         'play': self.quickSelectGlobal_,
         'stop': self.quickSelectGlobal_,
         'pause': self.quickSelectGlobal_,
         'fastforward': self.quickSelectGlobal_,
         'rewind': self.quickSelectGlobal_,
         'f1': self.quickSelectGlobal_,
         'f2': self.quickSelectGlobal_,
         'f3': self.quickSelectGlobal_,
         'key0': self.quickSelectGlobal_,
         'stop_long': self.quickSelectGlobal_,
         'pause_long': self.quickSelectGlobal_,
         'back': self.quickSelectGlobal_,
         'play_long': self.quickSelectGlobal_,
         'forward': self.quickSelectGlobal_,
         'record': self.quickSelectGlobal_,
         'record_long': self.quickSelectGlobal_}, -1)

    def exit(self):
        self.TimerTemp.stop()
        self.close(self.key)

    def quickSelectGlobal_(self, key):
        self.TimerTemp.stop()
        self.key = key
        self['key_tecla'].setText(_('Key Pressed: [') + key + ']')
        self['key_tecla'].show()
        self.TimerTemp.start(700, True)

    def setWindowTitle(self):
        self.setTitle(_('Capture Key'))


class capMQBActionMap(ActionMap):

    def action(self, contexts, action):
        quickSelection = ('red', 'red_long', 'green', 'green_long', 'yellow', 'yellow_long', 'blue', 'blue_long', 'pvr', 'pvr_long', 'radio', 'radio_long', 'text', 'text_long', 'help_long', 'info', 'info_long', 'end', 'end_long', 'home', 'home_long', 'cross_up', 'cross_down', 'cross_left', 'cross_right', 'previous', 'next', 'channelup', 'channeldown', 'f1', 'f2', 'f3', 'audio', 'exit', 'ok', 'play', 'pause', 'rewind', 'fastforward', 'stop', 'tv', 'stop_long', 'key0', 'pause_long', 'back', 'play_long', 'forward', 'record', 'record_long')
        if action in quickSelection and self.actions.has_key(action):
            res = self.actions[action](action)
            if res is not None:
                return res
            return 1
        else:
            return ActionMap.action(self, contexts, action)


class myHelpableActionMap(capMQBActionMap):

    def __init__(self, parent, context, actions = {}, prio = 0):
        alist = []
        adict = {}
        for action, funchelp in actions.iteritems():
            if isinstance(funchelp, tuple):
                alist.append((action, funchelp[1]))
                adict[action] = funchelp[0]
            else:
                adict[action] = funchelp

        capMQBActionMap.__init__(self, [context], adict, prio)
        parent.helpList.append((self, context, alist))
