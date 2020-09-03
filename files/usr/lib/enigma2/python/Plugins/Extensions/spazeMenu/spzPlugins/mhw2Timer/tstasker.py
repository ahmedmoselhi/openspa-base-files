from enigma import eTimer, eConsoleAppContainer, eServiceReference
from Screens.MessageBox import MessageBox
from Screens.Standby import TryQuitMainloop
from time import localtime, sleep, time
import Screens.Standby
from Screens import Standby
import os
from Screens.Console import Console
from mhwEPG import mhwEPG
from ServiceReference import ServiceReference
from Components.config import ConfigText, config, ConfigSubsection, ConfigYesNo
config.plugins.mwhepg = ConfigSubsection()
config.plugins.mwhepg.service = ConfigText(default='1:0:1:75c6:422:1:c00000:0:0:0')
config.plugins.mwhepg.hdmicec = ConfigYesNo(default=True)
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE, fileExists
from Tools import Notifications
from Components.Language import language
from os import environ
import gettext
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


class timerScriptTasker():

    def __init__(self):
        self.restartTimer = eTimer()
        self.restartTimer.timeout.get().append(self.RestartTimerStart)
        self.minutes = 0
        self.timerActive = False
        self.oldService = None
        self.dormido = False
        self.hdmicec = False

    def Initialize(self, session):
        self.session = session
        if config.plugins.mwhepg.activar.value:
            from Plugins.Extensions.spazeMenu.DelayedFunction import DelayedFunction
            DelayedFunction(60000, self.RestartTimerStart, True)

    def RestartTimerStart(self, initializing = False, postponeDelay = 0):
        try:
            self.restartTimer.stop()
            self.timerActive = False
            lotime = localtime()
            wbegin = config.plugins.mwhepg.script_begin.value
            wend = config.plugins.mwhepg.script_end.value
            xtimem = lotime[3] * 60 + lotime[4]
            ytimem = wbegin[0] * 60 + wbegin[1]
            ztimem = wend[0] * 60 + wend[1]
            os.system('echo "*************************">> /tmp/mhwEPGts.log; date >> /tmp/mhwEPGts.log; echo Start >> /tmp/mhwEPGts.log;echo "*************************">> /tmp/mhwEPGts.log;')
            if ytimem > ztimem:
                ztimem += 720
            if postponeDelay > 0:
                self.restartTimer.start(postponeDelay * 60000, False)
                self.timerActive = True
                mints = postponeDelay % 60
                hours = postponeDelay / 60
                return
            minsToGo = ytimem - xtimem
            if xtimem > ztimem:
                minsToGo += 1440
            if initializing or minsToGo > 0:
                if minsToGo < 0:
                    minsToGo += 1440
                elif minsToGo == 0:
                    minsToGo = 1
                self.restartTimer.start(minsToGo * 60000, False)
                self.timerActive = True
                self.minutes = minsToGo
                mints = self.minutes % 60
                hours = self.minutes / 60
            else:
                recordings = len(self.session.nav.getRecordings())
                next_rec_time = self.session.nav.RecordTimer.getNextRecordingTime()
                if not recordings and (next_rec_time - time() > 360 or next_rec_time < 0):
                    self.InitRestart()
                else:
                    os.system('echo "*************************">> /tmp/mhwEPGts.log; date >> /tmp/mhwEPGts.log; echo RECORDING. Wait 15 min >> /tmp/mhwEPGts.log;echo "*************************">> /tmp/mhwEPGts.log;')
                    self.minutes = 15
                    self.restartTimer.start(900000, False)
                    self.timerActive = True
        except Exception as e:
            print '[spTasker] RestartTimerStart exception:\n' + str(e)
            os.system('echo "*************************">> /tmp/mhwEPGts.log; date >> /tmp/mhwEPGts.log; echo ERROR [' + str(e) + '] >> /tmp/mhwEPGts.log;echo "*************************">> /tmp/mhwEPGts.log;')
            self.RestartTimerStart(True, 30)

    def lanzare(self):
        self.LaunchRestart(True)

    def InitRestart(self):
        if Screens.Standby.inStandby:
            if (os.path.exists('/dev/hdmi_cec') or os.path.exists('/dev/misc/hdmi_cec0')) and os.path.exists('/usr/lib/enigma2/python/Components/HdmiCec.pyo'):
                import Components.HdmiCec
                if config.hdmicec.enabled.value == True and config.plugins.mwhepg.hdmicec.value == True:
                    self.hdmicec = True
                    config.hdmicec.enabled.value = False
            self.dormido = True
            Screens.Standby.inStandby.Power()
            os.system('echo "*************************">> /tmp/mhwEPGts.log; date >> /tmp/mhwEPGts.log; echo instandby wake up >> /tmp/mhwEPGts.log;echo "*************************">> /tmp/mhwEPGts.log;')
            self.TimerTemp = eTimer()
            self.TimerTemp.callback.append(self.lanzare)
            self.TimerTemp.startLongTimer(7)
        else:
            self.dormido = False
            os.system('echo "*************************">> /tmp/mhwEPGts.log; date >> /tmp/mhwEPGts.log; echo wakedupAsk >> /tmp/mhwEPGts.log;echo "*************************">> /tmp/mhwEPGts.log;')
            stri = _('EPG download MediaHighway launching, Continue?\n Select no to postpone by 30 minutes.')
            self.session.openWithCallback(self.LaunchRestart, MessageBox, stri, MessageBox.TYPE_YESNO, timeout=30)

    def mirasireiniciar1(self):
        if self.oldService:
            self.session.nav.playService(self.oldService)
        self.TimerTemp = eTimer()
        self.TimerTemp.callback.append(self.mirasireiniciar2)
        self.TimerTemp.startLongTimer(6)

    def mirasireiniciar(self, ret):
        if ret:
            self.TimerTemp = eTimer()
            self.TimerTemp.callback.append(self.mirasireiniciar1)
            self.TimerTemp.startLongTimer(4)

    def mirasireiniciar2(self):
        if config.plugins.mwhepg.enigmarestart.value:
            self.session.openWithCallback(self.reinicioCB, MessageBox, _('Need restart GUI to apply changes\n Restart now?'), MessageBox.TYPE_YESNO, timeout=15)
        else:
            if self.dormido:
                self.dormido = True
                Notifications.AddNotification(Standby.Standby)
                if self.hdmicec:
                    config.hdmicec.enabled.value = True
            self.Initialize(self.session)

    def reinicioA(self):
        os.system('echo standbyEPG > /tmp/standbyEPG')
        os.system('echo "*************************">> /tmp/mhwEPGts.log; date >> /tmp/mhwEPGts.log; echo RESTARTGUI >> /tmp/mhwEPGts.log;echo "*************************">> /tmp/mhwEPGts.log;')
        self.session.open(TryQuitMainloop, 3)

    def nadacb(self, retval):
        if retval:
            a = 1

    def reinicioCB(self, retval):
        if retval:
            self.TimerTemp = eTimer()
            self.TimerTemp.callback.append(self.reinicioA)
            self.TimerTemp.startLongTimer(2)

    def ejecuta(self):
        self.lista = []
        if os.path.exists('/usr/lib/enigma2/python/Plugins/SystemPlugins/MovistarTV/EPGImport.pyo') and config.plugins.mwhepg.movistar.value:
            self.lista.append('Movistar')
        if os.path.exists('/usr/lib/enigma2/python/Plugins/Extensions/spzRemoteChannels/EPGImport.pyo') and config.plugins.mwhepg.remote.value:
            self.lista.append('Remote')
        if config.plugins.mwhepg.dplus.value:
            self.lista.append('Digital+')
        count = len(config.plugins.mwhepg.extras)
        if count != 0:
            i = 0
            while i < count:
                try:
                    if config.plugins.mwhepg.extras[i].enabled.value:
                        self.lista.append(str(i))
                except:
                    pass

                i += 1

        self.oldService = None
        try:
            self.oldService = self.session.nav.getCurrentlyPlayingServiceOrGroup()
        except Exception as e:
            self.oldService = None

        self.index = -1
        self.callbackfunction()

    def callbackfunction(self, ret = True):
        count = len(self.lista)
        self.index += 1
        if self.index < count:
            if self.lista[self.index] == 'Movistar':
                from Plugins.SystemPlugins.MovistarTV.EPGImport import EPGdownload
                self.session.openWithCallback(self.callbackfunction, EPGdownload)
            elif self.lista[self.index] == 'Remote':
                from Plugins.Extensions.spzRemoteChannels.EPGImport import EPGdownload
                self.session.openWithCallback(self.callbackfunction, EPGdownload)
            else:
                if self.lista[self.index] == 'Digital+':
                    service = '1:0:1:75c6:422:1:c00000:0:0:0'
                    try:
                        service = config.plugins.mwhepg.service.value
                    except:
                        pass

                    name = 'Digital+'
                    timer = config.plugins.mwhepg.standbyOnChannel.value
                else:
                    service = '1:0:1:75c6:422:1:c00000:0:0:0'
                    name = None
                    timer = 0
                    n = int(self.lista[self.index])
                    try:
                        service = config.plugins.mwhepg.extras[n].channel.value
                    except:
                        pass

                    try:
                        name = config.plugins.mwhepg.extras[n].name.value
                    except:
                        pass

                    try:
                        timer = config.plugins.mwhepg.extras[n].timeron.value
                    except:
                        pass

                try:
                    if len(ServiceReference(eServiceReference(service)).getServiceName()) == 0:
                        service = None
                except:
                    service = None

                if service and name and timer > 0:
                    self.session.nav.playService(eServiceReference(service))
                    com = '/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/mhw2Timer/mhwEPG'
                    os.system('echo "*************************">> /tmp/mhwEPGts.log; date >> /tmp/mhwEPGts.log; echo waiting for download >> /tmp/mhwEPGts.log;echo "*************************">> /tmp/mhwEPGts.log;')
                    self.session.openWithCallback(self.callbackfunction, mhwEPG, name, timer)
        else:
            self.mirasireiniciar(True)

    def LaunchRestart(self, confirmFlag = True):
        os.system('echo "*************************">> /tmp/mhwEPGts.log; date >> /tmp/mhwEPGts.log; echo AtemptLaunch >> /tmp/mhwEPGts.log;echo "*************************">> /tmp/mhwEPGts.log;')
        if confirmFlag:
            self.TimerTemp = eTimer()
            self.TimerTemp.callback.append(self.ejecuta)
            self.TimerTemp.startLongTimer(4)
        else:
            os.system('echo "*************************">> /tmp/mhwEPGts.log; date >> /tmp/mhwEPGts.log; echo 30minuteRetry >> /tmp/mhwEPGts.log;echo "*************************">> /tmp/mhwEPGts.log;')
            self.RestartTimerStart(True, 30)

    def ShowAutoRestartInfo(self):
        if config.plugins.mwhepg.activar.value:
            self.RestartTimerStart(True)
        else:
            self.RestartTimerStop()
        if self.timerActive:
            mints = self.minutes % 60
            hours = self.minutes / 60
            self.session.open(MessageBox, _('Next timer EPG download execution: ') + str(hours) + _(' hours ') + str(mints) + _(' minutes'), MessageBox.TYPE_INFO, 15)
        else:
            self.session.open(MessageBox, _('EPG download MediaHighway execution is currently not active.'), MessageBox.TYPE_INFO, 9)

    def verlog(self):
        if fileExists('/etc/mhw_Log.epg'):
            com = 'cat /etc/mhw_Log.epg'
            self.session.open(Console, _('Log file. EPG download MediaHighway'), ['%s' % com], closeOnSuccess=False)
        else:
            self.session.open(MessageBox, _('Log file. EPG download MediaHighway') + '\n' + _('not found') + ' (/etc/mhw_Log.epg)', MessageBox.TYPE_INFO, 12)

    def RestartTimerStop(self):
        self.restartTimer.stop()
        self.timerActive = False
        self.minutes = 0


tsTasker = timerScriptTasker()
