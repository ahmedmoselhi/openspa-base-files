from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Components.ConfigList import ConfigListScreen
from Screens.MessageBox import MessageBox
from Screens.Console import Console
from Screens import Standby
from Components.ActionMap import ActionMap
from Components.Button import Button
from Components.config import getConfigListEntry, ConfigEnableDisable, ConfigYesNo, ConfigText, ConfigClock, ConfigNumber, ConfigSelection, ConfigInteger, config, ConfigSubsection, ConfigSubList, ConfigSubDict, ConfigDirectory, KEY_LEFT, KEY_RIGHT, ConfigSelectionNumber, NoSave
from ServiceReference import ServiceReference
from Screens.ChannelSelection import SimpleChannelSelection
from Tools import Notifications
import os
from time import localtime, time
from enigma import quitMainloop, eTimer
from tstasker import tsTasker
from seletequiv import IniciaSel
from Tools.Directories import fileExists, resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE
from Components.Language import language
from Components.Label import Label
from os import environ
import os
import gettext
from Plugins.Extensions.spazeMenu.plugin import esHD
lang = language.getLanguage()
environ['LANGUAGE'] = lang[:2]
gettext.bindtextdomain('enigma2', resolveFilename(SCOPE_LANGUAGE))
gettext.textdomain('enigma2')
gettext.bindtextdomain('mhw2Timer', '%s%s' % (resolveFilename(SCOPE_PLUGINS), 'Extensions/spazeMenu/spzPlugins/mhw2Timer/locale/'))

def _(txt):
    t = gettext.dgettext('mhw2Timer', txt)
    if t == txt:
        t = gettext.gettext(txt)
    return t


session = None
timerscriptstarttime = 30
timerscriptsleeptime = 10
gSession = None
config.plugins.mwhepg = ConfigSubsection()
config.plugins.mwhepg.activar = ConfigYesNo(default=False)
config.plugins.mwhepg.standbyOnBoot = ConfigSelection(default='1', choices=[('0', _('No')), ('1', _('Only after donwload')), ('2', _('Always'))])
config.plugins.mwhepg.standbyOnBootTimeout = ConfigNumber(default=120)
config.plugins.mwhepg.standbyOnChannel = ConfigNumber(default=300)
config.plugins.mwhepg.enigmarestart = ConfigYesNo(default=False)
config.plugins.mwhepg.script_begin = ConfigClock(default=60 * 60 * 2)
config.plugins.mwhepg.script_end = ConfigClock(default=60 * 60 * 5)
config.plugins.mwhepg.service = ConfigText(default='1:0:1:75c6:422:1:c00000:0:0:0')
config.plugins.mwhepg.hdmicec = ConfigYesNo(default=True)
config.plugins.mwhepg.movistar = ConfigYesNo(default=True)
config.plugins.mwhepg.remote = ConfigYesNo(default=True)
config.plugins.mwhepg.dplus = ConfigYesNo(default=True)
config.plugins.mwhepg.extrascount = ConfigInteger(0)
config.plugins.mwhepg.extras = ConfigSubList()
count = config.plugins.mwhepg.extrascount.value
if count != 0:
    i = 0
    while i < count:
        try:
            config.plugins.mwhepg.extras.append(ConfigSubsection())
            config.plugins.mwhepg.extras[i].enabled = ConfigYesNo(default=True)
            config.plugins.mwhepg.extras[i].name = ConfigText(default='')
            config.plugins.mwhepg.extras[i].channel = ConfigText(default='')
            config.plugins.mwhepg.extras[i].timeron = ConfigNumber(default=120)
        except:
            pass

        i += 1

timer = eTimer()

def mostrarNotificacion():
    NOTIFICATIONID = 'mwh2epg'
    from Tools.Notifications import AddNotificationWithID, RemovePopup
    try:
        RemovePopup(NOTIFICATIONID)
    except:
        pass

    AddNotificationWithID(NOTIFICATIONID, DotimerscriptScreen)


def autostart(reason, **kwargs):
    global session
    global gSession
    if reason == 0 and kwargs.has_key('session'):
        gSession = kwargs['session']
        session = kwargs['session']
        Dotimerscript()
        gSession = kwargs['session']
        tsTasker.Initialize(gSession)


def Plugins(**kwargs):
    return [PluginDescriptor(name=_('EPG download MediaHighway'), description=_('Download EPG from MediaHighway'), where=[PluginDescriptor.WHERE_SESSIONSTART, PluginDescriptor.WHERE_AUTOSTART], fnc=autostart), PluginDescriptor(name=_('EPG download MediaHighway'), description=_('Download EPG from MediaHighway'), where=PluginDescriptor.WHERE_PLUGINMENU, fnc=main)]


def main(session, **kwargs):
    try:
        session.open(timerscript)
    except:
        print '[EPG download MediaHighway] Pluginexecution failed'


class timerscript(ConfigListScreen, Screen):
    if esHD():
        skin = '\n\t\t<screen position="100,100" size="1170,600" title="%s" >\n\t\t\t<widget name="config" position="0,5" size="1170,630" scrollbarMode="showOnDemand" itemHeight="42" />\n\t\t\t<widget name="key_red" position="0,510" size="210,60" valign="center" halign="center" zPosition="4" foregroundColor="white" font="Regular;18" transparent="1" backgroundColor="black" borderColor="black" borderWidth="1" noWrap="1"/> \n\t\t\t<widget name="key_green" position="210,510" size="210,60" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;18" transparent="1" backgroundColor="black" borderColor="black" borderWidth="1" noWrap="1"/> \n\t\t\t<widget name="key_yellow" position="405,510" size="240,60" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;18" transparent="1" backgroundColor="black" borderColor="black" borderWidth="1" noWrap="1"/> \n\t\t\t<widget name="key_blue" position="615,510" size="240,60" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;18" transparent="1" backgroundColor="black" borderColor="black" borderWidth="1" noWrap="1"/> \n\t\t\t<ePixmap name="red"    position="0,510"   zPosition="2" size="210,60" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/hdred.png" transparent="1" alphatest="blend" />\n\t\t\t<ePixmap name="green"  position="210,510" zPosition="2" size="210,60" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/hdgreen.png" transparent="1" alphatest="blend" />\n\t\t\t<ePixmap name="yellow"  position="420,510" zPosition="2" size="210,60" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/hdyellow.png" transparent="1" alphatest="blend" />\n\t\t\t<ePixmap name="blue"  position="630,510" zPosition="2" size="210,60" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/hdblue.png" transparent="1" alphatest="blend" />\n\t\t\t<ePixmap name="info"  position="870,517" zPosition="2" size="52,37" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/okHD.png" transparent="1" alphatest="blend" />\n\t\t\t<widget name="key_info" position="900,510" size="240,60" valign="left" halign="center" zPosition="4"  foregroundColor="white" font="Regular;18" transparent="1" backgroundColor="black" borderColor="black" borderWidth="1" noWrap="1"/> \n\t\t</screen>' % _('EPG download MediaHighway')
    else:
        skin = '\n\t\t\t<screen position="100,100" size="780,400" title="%s" >\n\t\t\t<widget name="config" position="0,0" size="780,420" scrollbarMode="showOnDemand" />\n\t\t\t\n\t\t\t<widget name="key_red" position="0,340" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;18" transparent="1" backgroundColor="black" borderColor="black" borderWidth="1" noWrap="1"/> \n\t\t\t<widget name="key_green" position="140,340" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;18" transparent="1" backgroundColor="black" borderColor="black" borderWidth="1" noWrap="1"/> \n\t\t\t<widget name="key_yellow" position="270,340" size="160,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;18" transparent="1" backgroundColor="black" borderColor="black" borderWidth="1" noWrap="1"/> \n\t\t\t<widget name="key_blue" position="410,340" size="160,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;18" transparent="1" backgroundColor="black" borderColor="black" borderWidth="1" noWrap="1"/> \n\t\t\t<ePixmap name="red"    position="0,340"   zPosition="2" size="140,40" pixmap="skin_default/buttons/red.png" transparent="1" alphatest="on" />\n\t\t\t<ePixmap name="green"  position="140,340" zPosition="2" size="140,40" pixmap="skin_default/buttons/green.png" transparent="1" alphatest="on" />\n\t\t\t<ePixmap name="yellow"  position="280,340" zPosition="2" size="140,40" pixmap="skin_default/buttons/yellow.png" transparent="1" alphatest="on" />\n\t\t\t<ePixmap name="blue"  position="420,340" zPosition="2" size="140,40" pixmap="skin_default/buttons/blue.png" transparent="1" alphatest="on" />\n\t\t\t<ePixmap name="info"  position="580,345" zPosition="2" size="35,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/mhw2Timer/bok.png" transparent="1" alphatest="on" />\n\t\t\t<widget name="key_info" position="600,340" size="160,40" valign="left" halign="center" zPosition="4"  foregroundColor="white" font="Regular;18" transparent="1" backgroundColor="black" borderColor="black" borderWidth="1" noWrap="1"/> \n\t\t</screen>' % _('EPG download MediaHighway')

    def __init__(self, session, args = 0):
        self.session = session
        Screen.__init__(self, session)
        self.service = '1:0:1:75c6:422:1:c00000:0:0:0'
        try:
            self.service = config.plugins.mwhepg.service.value
        except:
            pass

        self.setTitle(_('EPG download') + ' | openSPA')
        self.entry_service = None
        self.list = []
        ConfigListScreen.__init__(self, self.list)
        self['key_red'] = Button(_('Remove'))
        self['key_green'] = Button(_('Save'))
        self['key_info'] = Button(_('Edit'))
        self['key_yellow'] = Button(_('Add'))
        self['key_blue'] = Button(_('Download now'))
        self['setupActions'] = ActionMap(['OkCancelActions',
         'DirectionAction',
         'ColorActions',
         'EPGSelectActions'], {'ok': self.keyOK,
         'left': self.keyLeft,
         'right': self.keyRight,
         'red': self.delete,
         'green': self.save,
         'blue': self.force,
         'yellow': self.append,
         'cancel': self.cancel}, -2)
        self['config'].onSelectionChanged.append(self.SelectionChanged)
        self.createconfig()

    def SelectionChanged(self):
        try:
            if self.list[self['config'].getCurrentIndex()][2].startswith('Extra') or self.list[self['config'].getCurrentIndex()][2] == 'Digital+':
                self['key_info'].setText(_('Edit'))
            else:
                self['key_info'].setText('')
        except:
            self['key_info'].setText('')

        try:
            if self.list[self['config'].getCurrentIndex()][2].startswith('Extra'):
                self['key_red'].setText(_('Remove'))
            else:
                self['key_red'].setText('')
        except:
            self['key_red'].setText('')

    def createconfig(self):
        self.list = []
        self.list.append(getConfigListEntry(_('Number of days to download'), config.epg.maxdays, None, None))
        if (os.path.exists('/dev/hdmi_cec') or os.path.exists('/dev/misc/hdmi_cec0')) and os.path.exists('/usr/lib/enigma2/python/Components/HdmiCec.pyo'):
            self.list.append(getConfigListEntry(_('Disable HDMIcec when epg download from standby'), config.plugins.mwhepg.hdmicec, self.autoRestartInfo, self.autoRestartInfo))
        self.list.append(getConfigListEntry(_('Enable Epg MediaHighway autodownload'), config.plugins.mwhepg.activar, self.autoRestartInfo, self.autoRestartInfo))
        self.list.append(getConfigListEntry(_('Auto Execution time start'), config.plugins.mwhepg.script_begin, self.autoRestartInfo, self.autoRestartInfo))
        self.list.append(getConfigListEntry(_('Auto execution time end'), config.plugins.mwhepg.script_end, self.autoRestartInfo, self.autoRestartInfo))
        self.list.append(getConfigListEntry(_('Restart GUI after execution'), config.plugins.mwhepg.enigmarestart, None, None))
        self.list.append(getConfigListEntry(_('Go to standby on init'), config.plugins.mwhepg.standbyOnBoot, None, None))
        self.list.append(getConfigListEntry(_('Time to go to standby (secs)'), config.plugins.mwhepg.standbyOnBootTimeout, None, None))
        if os.path.exists('/usr/lib/enigma2/python/Plugins/SystemPlugins/MovistarTV/EPGImport.pyo'):
            self.list.append(getConfigListEntry(_('Download EPG from MovistarTV'), config.plugins.mwhepg.movistar, 'MovistarTV', None))
        if os.path.exists('/usr/lib/enigma2/python/Plugins/Extensions/spzRemoteChannels/EPGImport.pyo'):
            self.list.append(getConfigListEntry(_('Download EPG from Remote Channels'), config.plugins.mwhepg.remote, 'Remote', None))
        self.list.append(getConfigListEntry(_('Download EPG from Digital+'), config.plugins.mwhepg.dplus, 'Digital+', None))
        count = len(config.plugins.mwhepg.extras)
        if count != 0:
            i = 0
            while i < count:
                try:
                    self.list.append(getConfigListEntry(_('Download EPG from') + ' ' + config.plugins.mwhepg.extras[i].name.value, config.plugins.mwhepg.extras[i].enabled, 'Extra' + str(i), None))
                    i += 1
                except:
                    pass

        self['config'].list = self.list

    def delete(self):
        try:
            i = int(self.list[self['config'].getCurrentIndex()][2][5:])
        except:
            i = -1

        try:
            if self.list[self['config'].getCurrentIndex()][2].startswith('Extra'):
                self.session.openWithCallback(self.deleteConfirm, MessageBox, _('Really delete this Entry?'))
        except:
            pass

    def deleteConfirm(self, result):
        if not result:
            return
        try:
            i = int(self.list[self['config'].getCurrentIndex()][2][5:])
        except:
            i = -1

        if i > -1:
            config.plugins.mwhepg.extras.remove(config.plugins.mwhepg.extras[i])
            self.createconfig()

    def append(self):
        self.session.openWithCallback(self.endappend, editentry, name=None, channel=None, timer=None)

    def keyRight(self):
        self['config'].handleKey(KEY_RIGHT)

    def keyLeft(self):
        self['config'].handleKey(KEY_LEFT)

    def edite(self):
        self.session.open(IniciaSel)

    def force(self):
        tsTasker.ejecuta()

    def ViewLog(self):
        tsTasker.verlog()

    def dirSelected(self, res):
        if res is not None:
            if res[-1:] == '/':
                res = res[:-1]
            self.list[self['config'].getCurrentIndex()][1].value = res + '/'

    def openLocationBox(self):
        try:
            path = self.list[self['config'].getCurrentIndex()][1].value + '/'
            from Screens.LocationBox import LocationBox
            self.session.openWithCallback(self.dirSelected, LocationBox, text=_('Choose directory'), filename='', currDir=path, minFree=100)
        except:
            pass

    def autoRestartInfo(self, dummy = None):
        tsTasker.ShowAutoRestartInfo()

    def keyOK(self):
        if str(self.list[self['config'].getCurrentIndex()][2]) == 'Digital+':
            self.session.openWithCallback(self.endedit, editentry, name=str(self.list[self['config'].getCurrentIndex()][2]), channel=self.service, timer=config.plugins.mwhepg.standbyOnChannel.value)
        elif 'Extra' in str(self.list[self['config'].getCurrentIndex()][2]):
            try:
                i = int(self.list[self['config'].getCurrentIndex()][2][5:])
            except:
                i = -1

            if i > -1:
                self.session.openWithCallback(self.endedit, editentry, name=config.plugins.mwhepg.extras[i].name.value, channel=config.plugins.mwhepg.extras[i].channel.value, timer=config.plugins.mwhepg.extras[i].timeron.value)

    def endappend(self, name, channel, timer):
        if name != None and channel != None and channel != '':
            i = len(config.plugins.mwhepg.extras)
            config.plugins.mwhepg.extras.append(ConfigSubsection())
            config.plugins.mwhepg.extras[i].enabled = ConfigYesNo(default=True)
            config.plugins.mwhepg.extras[i].name = ConfigText(default='')
            config.plugins.mwhepg.extras[i].channel = ConfigText(default='')
            config.plugins.mwhepg.extras[i].timeron = ConfigNumber(default=120)
            config.plugins.mwhepg.extras[i].enabled.value = True
            config.plugins.mwhepg.extras[i].name.value = name
            config.plugins.mwhepg.extras[i].channel.value = channel
            config.plugins.mwhepg.extras[i].timeron.value = timer
        self.createconfig()

    def endedit(self, name, channel, timer):
        if name != None and channel != None and channel != '':
            if str(self.list[self['config'].getCurrentIndex()][2]) == 'Digital+':
                config.plugins.mwhepg.service.value = channel
                config.plugins.mwhepg.standbyOnChannel.value = timer
            else:
                try:
                    i = int(self.list[self['config'].getCurrentIndex()][2][5:])
                except:
                    i = -1

                if i > -1:
                    config.plugins.mwhepg.extras[i].enabled.value = True
                    config.plugins.mwhepg.extras[i].name.value = name
                    config.plugins.mwhepg.extras[i].channel.value = channel
                    config.plugins.mwhepg.extras[i].timeron.value = timer
        self.createconfig()

    def save(self):
        cambiado = False
        for x in self['config'].list:
            if x[1] != self.entry_service:
                if x[1].isChanged():
                    x[1].save()
                    if x[2] is not None:
                        cambiado = True

        if config.plugins.mwhepg.service.isChanged():
            config.plugins.mwhepg.service.save()
        count = len(config.plugins.mwhepg.extras)
        if count != 0:
            i = 0
            while i < count:
                try:
                    if config.plugins.mwhepg.extras[i].enabled.isChanged():
                        config.plugins.mwhepg.extras[i].enabled.save()
                    config.plugins.mwhepg.extras[i].name.save()
                    config.plugins.mwhepg.extras[i].channel.save()
                    config.plugins.mwhepg.extras[i].timeron.save()
                    i += 1
                except:
                    pass

        config.plugins.mwhepg.extras.save()
        config.plugins.mwhepg.extrascount.value = len(config.plugins.mwhepg.extras)
        config.plugins.mwhepg.extrascount.save()
        config.plugins.mwhepg.service.save()
        config.plugins.mwhepg.standbyOnChannel.save()
        if cambiado:
            self.autoRestartInfo()
        self.close()

    def cancel(self):
        for x in self['config'].list:
            if x[1] != self.entry_service:
                x[1].cancel()

        self.close(False, self.session)


class editentry(ConfigListScreen, Screen):
    if esHD():
        skin = '\n\t\t<screen position="100,100" size="1170,600" title="%s" >\n\t\t\t<widget name="config" position="0,5" size="1170,630" scrollbarMode="showOnDemand" itemHeight="42" />\n\t\t\t\n\t\t\t<widget name="key_red" position="0,510" size="210,60" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;18" transparent="1" backgroundColor="black" borderColor="black" borderWidth="1" noWrap="1"/> \n\t\t\t<widget name="key_green" position="210,510" size="210,60" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;18" transparent="1" backgroundColor="black" borderColor="black" borderWidth="1" noWrap="1"/> \n\t\t\t<widget name="key_yellow" position="405,510" size="240,60" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;18" transparent="1" backgroundColor="black" borderColor="black" borderWidth="1" noWrap="1"/> \n\t\t\t<widget name="key_blue" position="615,510" size="240,60" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;18" transparent="1" backgroundColor="black" borderColor="black" borderWidth="1" noWrap="1"/> \n\t\t\t<ePixmap name="red"    position="0,510"   zPosition="2" size="210,60" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/hdred.png" transparent="1" alphatest="blend" />\n\t\t\t<ePixmap name="green"  position="210,510" zPosition="2" size="210,60" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/hdgreen.png" transparent="1" alphatest="blend" />\n\t\t\t<ePixmap name="yellow"  position="420,510" zPosition="2" size="210,60" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/hdyellow.png" transparent="1" alphatest="blend" />\n\t\t\t<ePixmap name="blue"  position="630,510" zPosition="2" size="210,60" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/hdblue.png" transparent="1" alphatest="blend" />\n\t\t\t<ePixmap name="info"  position="870,517" zPosition="2" size="52,37" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/infoHD.png" transparent="1" alphatest="blend" />\n\t\t\t<widget name="key_info" position="900,510" size="240,60" valign="left" halign="center" zPosition="4"  foregroundColor="white" font="Regular;18" transparent="1" backgroundColor="black" borderColor="black" borderWidth="1" noWrap="1"/> \n\t\t</screen>' % _('EPG download MediaHighway')
    else:
        skin = '\n\t\t\t<screen position="100,100" size="780,400" title="%s" >\n\t\t\t<widget name="config" position="0,0" size="780,420" scrollbarMode="showOnDemand" />\n\t\t\t\n\t\t\t<widget name="key_red" position="0,340" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;18" transparent="1" backgroundColor="black" borderColor="black" borderWidth="1" noWrap="1"/> \n\t\t\t<widget name="key_green" position="140,340" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;18" transparent="1" backgroundColor="black" borderColor="black" borderWidth="1" noWrap="1"/> \n\t\t\t<widget name="key_yellow" position="270,340" size="160,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;18" transparent="1" backgroundColor="black" borderColor="black" borderWidth="1" noWrap="1"/> \n\t\t\t<widget name="key_blue" position="410,340" size="160,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;18" transparent="1" backgroundColor="black" borderColor="black" borderWidth="1" noWrap="1"/> \n\t\t\t<ePixmap name="red"    position="0,340"   zPosition="2" size="140,40" pixmap="skin_default/buttons/red.png" transparent="1" alphatest="on" />\n\t\t\t<ePixmap name="green"  position="140,340" zPosition="2" size="140,40" pixmap="skin_default/buttons/green.png" transparent="1" alphatest="on" />\n\t\t\t<ePixmap name="yellow"  position="280,340" zPosition="2" size="140,40" pixmap="skin_default/buttons/yellow.png" transparent="1" alphatest="on" />\n\t\t\t<ePixmap name="blue"  position="420,340" zPosition="2" size="140,40" pixmap="skin_default/buttons/blue.png" transparent="1" alphatest="on" />\n\t\t\t<ePixmap name="info"  position="580,345" zPosition="2" size="35,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/mhw2Timer/info.png" transparent="1" alphatest="on" />\n\t\t\t<widget name="key_info" position="600,340" size="160,40" valign="left" halign="center" zPosition="4"  foregroundColor="white" font="Regular;18" transparent="1" backgroundColor="black" borderColor="black" borderWidth="1" noWrap="1"/> \n\t\t</screen>' % _('EPG download MediaHighway')

    def __init__(self, session, name = None, channel = None, timer = None):
        self.session = session
        Screen.__init__(self, session)
        self.servicename = None
        try:
            self.servicename = str(ServiceReference(channel).getServiceName())
        except:
            pass

        self.entry_service_ref = ServiceReference(channel)
        self.entry_service = ConfigSelection([self.servicename])
        self.name = name or 'New'
        self.timer = timer or 120
        self.channel = channel
        if self.name:
            self.setTitle(_('Config EPG:') + ' ' + self.name + ' | openSPA')
        else:
            self.setTitle(_('Config EPG: New | openSPA'))
        self['key_red'] = Button(_('Cancel'))
        self['key_green'] = Button(_('Save'))
        if self.name == 'Digital+':
            self['key_info'] = Button(_('View last Log'))
            self['key_yellow'] = Button(_('Edit equiv'))
        else:
            self['key_info'] = Button('')
            self['key_yellow'] = Button('')
        self['key_blue'] = Button('')
        self['setupActions'] = ActionMap(['SetupActions',
         'ColorActions',
         'EPGSelectActions',
         'InfobarActions'], {'left': self.keyLeft,
         'right': self.keyRight,
         'red': self.cancel,
         'green': self.save,
         'yellow': self.edite,
         'info': self.ViewLog,
         'cancel': self.cancel}, -2)
        self.list = []
        ConfigListScreen.__init__(self, self.list, session=session)
        self.createconfig()

    def createconfig(self):
        self.list = []
        if self.name != 'Digital+':
            self.cname = NoSave(ConfigText(fixed_size=False))
            if self.name == None:
                self.cname.value = ''
            else:
                self.cname.value = self.name
            self.list.append(getConfigListEntry(_('Name:'), self.cname, None, None))
        self.channelEntry = getConfigListEntry(_('Channel for EPG Download'), self.entry_service)
        self.list.append(self.channelEntry)
        self.ctimer = NoSave(ConfigNumber(default=120))
        self.ctimer.value = self.timer
        self.list.append(getConfigListEntry(_('Time to wait in the channel for EPG download (secs)'), self.ctimer, None, None))
        self['config'].list = self.list

    def keyRight(self):
        self['config'].handleKey(KEY_RIGHT)
        self.keysel()

    def keyLeft(self):
        self['config'].handleKey(KEY_LEFT)
        self.keysel()

    def keysel(self):
        cur = self['config'].getCurrent()
        if cur == self.channelEntry:
            self.session.openWithCallback(self.finishedChannelSelection, SimpleChannelSelection, _('Select channel to Change for Download EPG'))

    def edite(self):
        if self.name == 'Digital+':
            self.session.open(IniciaSel)

    def ViewLog(self):
        if self.name == 'Digital+':
            tsTasker.verlog()

    def save(self):
        if self.name == 'Digital+':
            name = 'Digital+'
        else:
            name = self.cname.value
        self.close(name, self.channel, self.ctimer.value)

    def cancel(self):
        self.close(None, None, None)

    def finishedChannelSelection(self, *args):
        if args:
            self.entry_service_ref = ServiceReference(args[0])
            self.entry_service.setCurrentText(self.entry_service_ref.getServiceName())
            self.channel = args[0].toString()


class Dotimerscript():
    print '[EPG download MediaHighway] Starting up Version '
    trysleep = config.plugins.mwhepg.standbyOnBoot.value == '2' or config.plugins.mwhepg.standbyOnBoot.value == '1' and fileExists('/tmp/standbyEPG')
    TimerStandby = eTimer()

    def __init__(self):
        global timerscriptsleeptime
        if self.trysleep:
            self.TimerStandby.callback.append(self.CheckStandby)
            self.TimerStandby.startLongTimer(timerscriptsleeptime)
            print '[EPG download MediaHighway] Set up standby timer'

    def CheckStandby(self):
        global timerscriptstarttime
        try:
            if config.plugins.mwhepg.standbyOnBoot.value == '2' or config.plugins.mwhepg.standbyOnBoot.value == '1' and fileExists('/tmp/standbyEPG'):
                if not Standby.inStandby:
                    mostrarNotificacion()
            os.system('rm /tmp/standbyEPG')
            if config.plugins.mwhepg.activar.value:
                os.system('echo "*************************">> /tmp/mhwEPGts.log; date >> /tmp/mhwEPGts.log; echo enigmaStart >> /tmp/mhwEPGts.log;echo "*************************">> /tmp/mhwEPGts.log;')
        except:
            print '[EPG download MediaHighway] Failed Showing Standby Screen, retring... '
            if self.trysleep:
                self.TimerStandby.startLongTimer(timerscriptstarttime)


class DotimerscriptScreen(Screen):
    if esHD():
        skin = ' <screen position="1320,105" size="517,45" title="%s" >\n\t\t\t<widget name="texto" position="0,0" size="517,45" valign="center" halign="center" font="Regular;20" itemHeight="40" />\n\t\t</screen>' % _('AutoShutdown')
    else:
        skin = ' <screen position="880,70" size="345,30" title="%s" >\n\t\t\t<widget name="texto" position="0,0" size="345,30" valign="center" halign="center" font="Regular;20" />\n\t\t</screen>' % _('AutoShutdown')

    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session
        self['texto'] = Label(_('AutoShutdown'))
        self.timeout = config.plugins.mwhepg.standbyOnBootTimeout.value
        self.contador = config.plugins.mwhepg.standbyOnBootTimeout.value
        print '[EPG download MediaHighway] Showing AutoStandby Screen '
        self['actions'] = ActionMap(['DirectionActions',
         'ShortcutActions',
         'WizardActions',
         'EPGSelectActions'], {'ok': self.exit,
         'green': self.exit,
         'red': self.exit,
         'blue': self.exit,
         'yellow': self.exit,
         'home': self.exit,
         'back': self.exit,
         'info': self.exit,
         'left': self.exit,
         'right': self.exit,
         'up': self.exit,
         'down': self.exit,
         'menu': self.exit}, -1)
        self.TimerChequea = eTimer()
        self.TimerChequea.callback.append(self.actualiza)
        self.onLayoutFinish.append(self.actualiza)

    def actualiza(self):
        self.contador = self.contador - 1
        self.TimerChequea.stop()
        if Standby.inStandby:
            self.setTitle(_('Canceled autopower off') + '(' + str(self.contador) + ')')
            self.close()
        elif self.contador <= -99:
            self.close()
        elif self.contador == 0:
            self.setTitle(_('Go Standby') + '')
            self.TimerChequea.startLongTimer(1)
        elif self.contador < 0:
            self.setTitle(_('Go Standby') + '...')
            self.DotimerscriptStandby()
        else:
            self.setTitle(_('Power off in') + ' ' + str(self.contador) + ' ' + _('sec'))
            self.TimerChequea.startLongTimer(1)

    def DotimerscriptStandby(self):
        if True:
            Notifications.AddNotification(Standby.Standby)
            self.close()

    def exit(self):
        self.TimerChequea.stop()
        self.contador = -100
        self.setTitle(_('Canceled autopower off'))
        self.TimerChequea.start(400, True)

    def DotimerscriptSleep(self, retval):
        if retval:
            if Standby.inTryQuitMainloop == False:
                self.session.open(Standby.TryQuitMainloop, 1)
        else:
            self.dontsleep = True
