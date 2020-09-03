from enigma import *
from enigma import eTimer, eConsoleAppContainer
from Components.config import *
from Screens.MessageBox import MessageBox
from Screens.Standby import *
from time import localtime, sleep, strftime
import Screens.Standby
from Screens import Standby
import os
from Screens.Console import Console
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE, fileExists
from Tools import Notifications
from Components.Language import language
from os import environ
import gettext
lang = language.getLanguage()
environ['LANGUAGE'] = lang[:2]
gettext.bindtextdomain('enigma2', resolveFilename(SCOPE_LANGUAGE))
gettext.textdomain('enigma2')
gettext.bindtextdomain('spzCAMD', '%s%s' % (resolveFilename(SCOPE_PLUGINS), 'Extensions/spazeMenu/spzPlugins/spzCAMD/locale/'))

def _(txt):
    t = gettext.dgettext('spzCAMD', txt)
    if t == txt:
        t = gettext.gettext(txt)
    return t


class timerScriptTasker:

    def __init__(self):
        self.restartTimer = eTimer()
        self.restartTimer.timeout.get().append(self.RestartTimerStart)
        self.checkCAMD = eTimer()
        self.checkCAMD.callback.append(self.checkstarted)
        self.minutes = 0
        self.timerActive = False
        self.oldService = None
        self.dormido = False

    def Initialize(self, session):
        self.session = session
        if config.plugins.spzCAMD.activar.value:
            from Plugins.Extensions.spazeMenu.DelayedFunction import DelayedFunction
            DelayedFunction(60000, self.RestartTimerStart, True)
        if config.plugins.spzCAMD.autorestart.value:
            self.checkCAMD.start(config.plugins.spzCAMD.restart_check.value * 1000, False)

    def RestartTimerStart(self, initializing = False, postponeDelay = 0):
        try:
            self.restartTimer.stop()
            self.timerActive = False
            lotime = localtime()
            wbegin = config.plugins.spzCAMD.restart_begin.value
            wend = config.plugins.spzCAMD.restart_end.value
            xtimem = lotime[3] * 60 + lotime[4]
            ytimem = wbegin[0] * 60 + wbegin[1]
            ztimem = wend[0] * 60 + wend[1]
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
                    self.minutes = 15
                    self.restartTimer.start(900000, False)
                    self.timerActive = True
        except Exception as e:
            print '[spzCAMD] RestartTimerStart exception:\n' + str(e)
            self.RestartTimerStart(True, 30)

    def lanzare(self):
        self.LaunchRestart(True)

    def InitRestart(self):
        if Screens.Standby.inStandby:
            self.dormido = True
            self.TimerTemp = eTimer()
            self.TimerTemp.callback.append(self.lanzare)
            self.TimerTemp.startLongTimer(7)
        else:
            self.dormido = False
            cam = config.plugins.spzCAMD.camd.value
            stri = _('Restart CAMD: ' + cam + '?\n Select no to postpone by 30 minutes.')
            self.session.openWithCallback(self.LaunchRestart, MessageBox, stri, MessageBox.TYPE_YESNO, timeout=30)

    def callback(self, retval):
        self.Initialize(self.session)

    def reinicioCB(self, retval):
        if retval:
            self.TimerTemp = eTimer()
            self.TimerTemp.callback.append(self.reinicioA)
            self.TimerTemp.startLongTimer(2)

    def ejecuta(self):
        if os.path.isfile('/etc/.CamdReStart.sh') is True:
            os.system('sh /etc/.CamdReStart.sh')
            cam = config.plugins.spzCAMD.camd.value
            self.session.openWithCallback(self.callback, MessageBox, _('Restart Camd: ' + cam + '...'), type=1, timeout=9)

    def LaunchRestart(self, confirmFlag = True):
        if confirmFlag:
            self.TimerTemp = eTimer()
            self.TimerTemp.callback.append(self.ejecuta)
            self.TimerTemp.startLongTimer(4)
        else:
            self.RestartTimerStart(True, 30)

    def ShowAutoRestartInfo(self):
        if config.plugins.spzCAMD.activar.value:
            self.RestartTimerStart(True)
        else:
            self.RestartTimerStop()
        if self.timerActive:
            mints = self.minutes % 60
            hours = self.minutes / 60
        if config.plugins.spzCAMD.autorestart.value and fileExists('/tmp/.spzCAMD'):
            self.checkCAMD.stop()
            self.checkCAMD.start(config.plugins.spzCAMD.restart_check.value * 1000, False)
        else:
            self.checkCAMD.stop()

    def checkstarted(self):
        if os.path.isfile('/etc/.BinCamd') and os.path.isfile('/etc/.CamdReStart.sh') and fileExists('/tmp/.spzCAMD'):
            caido = False
            ebin = open('/etc/.BinCamd', 'r').read().split()
            for e in ebin:
                check = os.popen('pidof ' + e).read()
                if check == '':
                    caido = True
                    open('/tmp/spzCAMD.log', 'a').write(strftime('%d/%m/%y %H:%M:%S') + ' ' + e + ' ' + _('not working') + '\n')

            if fileExists('/tmp/sbox.log'):
                log = os.popen("grep 'Broken pipe' /tmp/sbox.log").read()
                if len(log) > 0:
                    open('/tmp/spzCAMD.log', 'a').write(strftime('%d/%m/%y %H:%M:%S') + ' [Broken pipe] sbox ' + _('not working') + '??\n')
                    caido = True
            if caido:
                os.system('sh /etc/.CamdReStart.sh')
                try:
                    clist = open('/etc/.ActiveCamd', 'r')
                except:
                    pass

                lastcam = None
                if clist is not None:
                    for line in clist:
                        lastcam = line

                    clist.close()
                try:
                    open('/tmp/spzCAMD.log', 'a').write(strftime('%d/%m/%y %H:%M:%S') + ' ' + _('Start Camd:') + ' ' + str(lastcam) + '\n')
                except:
                    pass

                if config.plugins.spzCAMD.restart_viewmessage.value:
                    try:
                        from Plugins.Extensions.spazeMenu.spzPlugins.scrInformation.plugin import mostrarNotificacion
                        mostrarNotificacion(id='spzCAMD', texto=_('Start Camd:') + ' ' + str(lastcam), titulo=_('spzCAMD'), segundos=8, mostrarSegundos=True, cerrable=True)
                    except:
                        pass

    def RestartTimerStop(self):
        self.restartTimer.stop()
        self.timerActive = False
        self.minutes = 0


tsTasker = timerScriptTasker()
