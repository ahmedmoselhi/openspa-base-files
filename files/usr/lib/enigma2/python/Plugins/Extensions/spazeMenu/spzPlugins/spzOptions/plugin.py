from Components.ActionMap import ActionMap
from Components.config import getConfigListEntry, ConfigEnableDisable, ConfigYesNo, ConfigText, ConfigClock, ConfigNumber, ConfigSelection, config, ConfigSubsection, ConfigSubList, ConfigSubDict, ConfigDirectory, ConfigBoolean, ConfigSelectionNumber
from Components.ConfigList import ConfigListScreen
from Components.Language import language
from Components.Button import Button
from Components.ScrollLabel import ScrollLabel
from os import environ
from Plugins.Plugin import PluginDescriptor
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from telnetlib import Telnet
from Tools.Directories import resolveFilename, SCOPE_LANGUAGE, SCOPE_PLUGINS, pathExists
import gettext
import os
from Plugins.Extensions.spazeMenu.plugin import esHD
lang = language.getLanguage()
environ['LANGUAGE'] = lang[:2]
gettext.bindtextdomain('enigma2', resolveFilename(SCOPE_LANGUAGE))
gettext.textdomain('enigma2')
gettext.bindtextdomain('spzOptions', '%s%s' % (resolveFilename(SCOPE_PLUGINS), 'Extensions/spazeMenu/spzPlugins/spzOptions/locale/'))

def _(txt):
    t = gettext.dgettext('spzOptions', txt)
    if t == txt:
        t = gettext.gettext(txt)
    return t


config.plugins.spzOptions = ConfigSubsection()
config.plugins.spzOptions.new_password = ConfigText(default='****', fixed_size=False)
config.plugins.spzOptions.bkchange = ConfigSelection(default='0', choices=[('0', _('Press [OK] for change'))])
config.plugins.spzOptions.spzExp = ConfigSelection(default='0', choices=[('0', _('Press [OK] for deactivate'))])
config.misc.spazeChannelSelection = ConfigYesNo(default=True)
config.misc.spazeinfobartp = ConfigYesNo(default=True)
config.misc.spazeupdates = ConfigYesNo(default=True)
config.misc.spazeinfobarecm = ConfigYesNo(default=True)
config.misc.spazeinfobarnum = ConfigYesNo(default=True)
config.misc.spazeinfobarinet = ConfigYesNo(default=True)
config.misc.spazeinfobarrec = ConfigYesNo(default=True)
config.misc.spazeinfobarmeteo = ConfigYesNo(default=True)
config.misc.spazeuseemc = ConfigYesNo(default=True)
config.misc.replacespzkeyboard = ConfigYesNo(default=True)
config.misc.spazeclearram = ConfigYesNo(default=True)
config.tvspaze.maxdaysEPG = ConfigSelectionNumber(min=1, max=7, stepwidth=1, default=1, wraparound=True)
try:
    config.plugins.mwhepg.standbyOnBoot = ConfigSelection(default='1', choices=[('0', _('No')), ('1', _('Only after mhw2 donwload')), ('2', _('Always'))])
    config.plugins.mwhepg.standbyOnBootTimeout = ConfigNumber(default=120)
except:
    config.plugins.mwhepg = ConfigSubsection()
    config.plugins.mwhepg.service = ConfigText(default='1:0:1:75c6:422:1:c00000:0:0:0')
    config.plugins.mwhepg.activar = ConfigYesNo(default=False)
    config.plugins.mwhepg.standbyOnBootTimeout = ConfigNumber(default=120)
    config.plugins.mwhepg.standbyOnChannel = ConfigNumber(default=100)
    config.plugins.mwhepg.enigmarestart = ConfigYesNo(default=False)
    config.plugins.mwhepg.script_begin = ConfigClock(default=7200)
    config.plugins.mwhepg.script_end = ConfigClock(default=18000)
    config.plugins.mwhepg.standbyOnBoot = ConfigSelection(default='1', choices=[('0', _('No')), ('1', _('Only after mhw2 donwload')), ('2', _('Always'))])

class TitleScreen(Screen):

    def __init__(self, session, parent = None):
        Screen.__init__(self, session, parent)
        self.onLayoutFinish.append(self.setScreenTitle)

    def setScreenTitle(self):
        self.setTitle(_('openSPA Options'))


class SCRMain(ConfigListScreen, TitleScreen):
    if esHD():
        skin = '\n\t\t<screen position="center,center" size="1380,700" title="%s" >\n\t\t\t<widget name="config" position="0,5" size="1380,590" scrollbarMode="showOnDemand" itemHeight="42" />\n\t\t\t<widget name="key_red" position="0,610" size="210,60" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;18" transparent="1"/> \n\t\t\t<widget name="key_green" position="210,610" size="210,60" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;18" transparent="1"/> \t\n\t\t\t<ePixmap name="red" position="0,610" zPosition="2" size="210,60" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/hdred.png" transparent="1" alphatest="blend" />\n\t\t\t<ePixmap name="green" position="210,610" zPosition="2" size="210,60" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/hdgreen.png" transparent="1" alphatest="blend" />\t\n\t\t</screen>' % _('openSPA Options')
    else:
        skin = '\n\t\t<screen position="center,center" size="920,400" title="%s" >\n\t\t\t<widget name="config" position="0,0" size="920,340" scrollbarMode="showOnDemand" />\n\t\t\t<widget name="key_red" position="0,340" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;18" transparent="1"/> \n\t\t\t<widget name="key_green" position="140,340" size="140,40" valign="center" halign="center" zPosition="4"  foregroundColor="white" font="Regular;18" transparent="1"/> \t\n\t\t\t<ePixmap name="red" position="0,340" zPosition="2" size="140,40" pixmap="skin_default/buttons/red.png" transparent="1" alphatest="on" />\n\t\t\t<ePixmap name="green" position="140,340" zPosition="2" size="140,40" pixmap="skin_default/buttons/green.png" transparent="1" alphatest="on" />\t\n\t\t</screen>' % _('openSPA Options')

    def __init__(self, session, args = None):
        TitleScreen.__init__(self, session)
        self.session = session
        listacomandos = [getConfigListEntry(_('Go to standby on init') + ':', config.plugins.mwhepg.standbyOnBoot, None, None),
         getConfigListEntry(_('Time to go to standby (secs)'), config.plugins.mwhepg.standbyOnBootTimeout, None, None),
         getConfigListEntry(_('Set new password:'), config.plugins.spzOptions.new_password, self.changePassword, self.changePassword),
         getConfigListEntry(_('Use openSPA Channel Selection') + ':', config.misc.spazeChannelSelection, None, None),
         getConfigListEntry(_('Maximum days of epg in OpenSPA Channel Selection') + ':', config.tvspaze.maxdaysEPG, None, None),
         getConfigListEntry(_('Use VirtualKeyboard for input text (need restart)') + ':', config.misc.replacespzkeyboard, None, None)]
        if pathExists('/media/spzExtended/usr') and False:
            listacomandos.append(getConfigListEntry(_('Disable extended DOM (for install only):'), config.plugins.spzOptions.spzExp, self.spzExpSetup, self.spzExpSetup))
        listacomandos.append(getConfigListEntry(_('Show ecm information in infobar:'), config.misc.spazeinfobarecm, None, None))
        listacomandos.append(getConfigListEntry(_('Show Transponder information in infobar:'), config.misc.spazeinfobartp, None, None))
        listacomandos.append(getConfigListEntry(_('Show Number channel in infobar:'), config.misc.spazeinfobarnum, None, None))
        listacomandos.append(getConfigListEntry(_('Show Internet conection in infobar:'), config.misc.spazeinfobarinet, None, None))
        listacomandos.append(getConfigListEntry(_('Show meteo information in infobar:'), config.misc.spazeinfobarmeteo, None, None))
        listacomandos.append(getConfigListEntry(_('Check new updates and notify:'), config.misc.spazeupdates, None, None))
        listacomandos.append(getConfigListEntry(_('Clean cache memory on standby:'), config.misc.spazeclearram, None, None))
        if pathExists('/usr/lib/enigma2/python/Plugins/Extensions/EnhancedMovieCenter'):
            listacomandos.append(getConfigListEntry(_('Use EMC for show records:'), config.misc.spazeuseemc, None, None))
        ConfigListScreen.__init__(self, listacomandos)
        self['key_red'] = Button(_('Cancel'))
        self['key_green'] = Button(_('Save'))
        self.cambiado = False
        self.avalor = config.plugins.spzOptions.new_password.value
        self.achannel = config.misc.spazeChannelSelection.value
        self['actions'] = ActionMap(['ColorActions', 'OkCancelActions'], {'ok': self.key_ok,
         'cancel': self.cancel,
         'red': self.cancel,
         'green': self.save}, -2)

    def save(self):
        if not self.avalor == config.plugins.spzOptions.new_password.value:
            self.session.openWithCallback(self.saveok, MessageBox, _('For change password press [OK] in list entry!!!') + '\n' + _("You're sure to exit without change password?"), MessageBox.TYPE_YESNO)
            return
        self.saveok(True)

    def saveok(self, answ):
        if answ:
            cambiado = False
            for x in self['config'].list:
                if x[1].isChanged():
                    if x[2] is None:
                        cambiado = True
                        x[1].save()

            if not self.achannel == config.misc.spazeChannelSelection.value:
                try:
                    from Screens.InfoBar import InfoBar
                    if config.misc.spazeChannelSelection.value:
                        from Screens.newChannelSelection import newChannelSelection
                        if InfoBar and InfoBar.instance:
                            InfoBar.instance.servicelist = InfoBar.instance.session.instantiateDialog(newChannelSelection)
                    else:
                        from Screens.ChannelSelection import ChannelSelection
                        if InfoBar and InfoBar.instance:
                            InfoBar.instance.servicelist = InfoBar.instance.session.instantiateDialog(ChannelSelection)
                    self.close()
                except:
                    self.session.open(MessageBox, _('Channel Selection ERROR (288)!!!'), MessageBox.TYPE_ERROR)

            else:
                self.close()

    def reiniciagui(self):
        self.session.openWithCallback(self.cbcs, MessageBox, _('Restart GUI for apply changes?'))

    def cbcs(self, resp):
        from Screens.Standby import TryQuitMainloop
        if resp:
            self.session.open(TryQuitMainloop, 3)
        else:
            self.close()

    def cancel(self):
        cambiado = False
        for x in self['config'].list:
            if x[1].isChanged() and x[2] is None:
                cambiado = True

        if cambiado:
            self.session.openWithCallback(self.cancelOk, MessageBox, _('All changes will be lost!') + '\n' + _("You're sure to exit without saving?"), MessageBox.TYPE_YESNO)
            return
        self.cancelOk(True)

    def cancelOk(self, respuesta):
        if respuesta:
            for x in self['config'].list:
                x[1].cancel()

            self.close()

    def key_ok(self):
        try:
            self['config'].list[self['config'].getCurrentIndex()][3]()
        except:
            pass

    def spzExpSetup(self):
        mensa = _('The extra DOM will be deactivated.') + '\n' + _('All plugins/skins installed are not AVAILABLE.') + '\n' + _('Use this options ONLY for install new drivers!!!') + '\n' + _('The extra DOM will be activated again on restart') + '\n' + _('Are you sure to continue?')
        self.session.openWithCallback(self.spzExpCallBack, MessageBox, mensa, MessageBox.TYPE_YESNO)

    def spzExpCallBack(self, answer):
        if answer:
            self.session.open(screenSpzExp)

    def bkSetup(self):
        try:
            from Plugins.Extensions.spazeMenu.spzPlugins.BlackModernSetup.plugin import main
            main(self.session)
        except:
            pass

    def changePassword(self):
        old_pass = ''
        new_pass = config.plugins.spzOptions.new_password.value
        if '*' in new_pass:
            self.session.open(MessageBox, _('Type new password first!!!'), MessageBox.TYPE_INFO)
        elif len(new_pass) >= 3 and len(new_pass) < 9:
            os.system('passwd -d root')
            self.avalor = config.plugins.spzOptions.new_password.value
            self.session.open(PasswordChangerConsole, old_pass, new_pass)
        else:
            self.session.open(MessageBox, _('Incorrect new password!\nMinimum length: 3\nMaximum length: 8'), MessageBox.TYPE_ERROR)

    def exit(self):
        for x in self['config'].list:
            x[1].cancel()

        self.close()


class screenSpzExp(TitleScreen):
    skin = '\n\t\t<screen position="center,center" size="600,400" title="%s" flags="wfNoBorder" backgroundColor="#10000000" >\n\t\t\t<widget name="label" position="10,10" size="580,380" font="Regular;20" />\n\t\t</screen>' % _('spzExp')

    def __init__(self, session):
        TitleScreen.__init__(self, session)
        self.timeout = 2
        self['label'] = ScrollLabel('\n' + _('Deactivating extra DOM. Please Wait...'))
        self['actions'] = ActionMap(['WizardActions'], {'ok': self.exit,
         'back': self.exit}, -1)
        self.onLayoutFinish.append(self.run)

    def run(self):
        os.system('umount /media/spzExtended')
        os.system('umount -l /usr')
        self['label'].setText(_('Extra DOM deactivated.') + '\n' + _('Receiver has been locked to prevent failures.') + '\n' + _('After installing the drivers manually have to reboot Receiver!!!') + '\n' + _('When finished new driver install press [OK] or [EXIT] for reboot Receiver'))

    def exit(self):
        os.system('reboot')
        self.close()


class PasswordChangerConsole(TitleScreen):
    skin = '\n\t\t<screen position="center,center" size="720,400" title="%s" >\n\t\t\t<widget name="label" position="0,0" size="720,400" font="Regular;20" />\n\t\t</screen>' % _('Change Password')

    def __init__(self, session, old_pass, new_pass):
        TitleScreen.__init__(self, session)
        self.working = True
        self.old_pass = old_pass
        self.new_pass = new_pass
        self.log = ''
        self.timeout = 2
        self['label'] = ScrollLabel('')
        self['actions'] = ActionMap(['WizardActions'], {'ok': self.exit,
         'back': self.exit,
         'up': self['label'].pageUp,
         'down': self['label'].pageDown,
         'left': self['label'].pageUp,
         'right': self['label'].pageDown}, -1)
        self.onLayoutFinish.append(self.run)

    def exit(self):
        if not self.working:
            self.sendMessage('exit')
            self.close()

    def sendMessage(self, message):
        if self.t is not None:
            self.t.write(message + '\n')
            r = self.t.read_until('UNKNOWN', self.timeout)
            self.log += r
            return r
        else:
            return ''

    def run(self):
        logged_in = False
        try:
            self.t = Telnet('localhost')
            self.log = self.t.read_until('login:', self.timeout)
            if self.log.__contains__('login:'):
                r = self.sendMessage('root')
                if r.__contains__('~#'):
                    logged_in = True
                elif r.__contains__('Password:'):
                    r = self.sendMessage(self.old_pass)
                    if r.__contains__('~#'):
                        logged_in = True
        except:
            self.t = None

        if logged_in:
            self.changePassword()
        else:
            self.log += _('Could not log in!')
            self['label'].setText(self.log)
            self.working = False

    def changePassword(self):
        try:
            r = self.sendMessage('#### ' + _('Chanching password to') + '[' + self.new_pass + '] ####')
            r = self.sendMessage('passwd')
            if r.__contains__('New password:'):
                r = self.sendMessage(self.new_pass)
                if r.__contains__('Retype password:'):
                    r = self.sendMessage(self.new_pass)
                    r = self.sendMessage('#### ' + _('Press [EXIT] for close') + '] ####')
        except:
            self.log += _('Error while setting new password!')

        self['label'].setText(self.log)
        self.working = False


def mainOptions(session, **kwargs):
    session.open(SCRMain)
