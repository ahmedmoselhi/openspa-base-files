from time import localtime, time, mktime
from enigma import eTimer
from Components.config import ConfigYesNo, ConfigClock, config, ConfigSubsection
from os import environ
import gettext
from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE
lang = language.getLanguage()
environ['LANGUAGE'] = lang[:2]
lenguaje = str(lang[:2])
gettext.bindtextdomain('enigma2', resolveFilename(SCOPE_LANGUAGE))
gettext.textdomain('enigma2')
gettext.bindtextdomain('autodeepsleep', '%s%s' % (resolveFilename(SCOPE_PLUGINS), 'Extensions/autodeepsleep/locale/'))

def _(txt):
    t = gettext.dgettext('autodeepsleep', txt)
    if t == txt:
        t = gettext.gettext(txt)
    return t


ultimoled = None
TimerTempReposo = None
TimerReposo = None
TiempoWakeUp = -1
session = None
config.plugins.autodeepsleep = ConfigSubsection()
config.plugins.autodeepsleep.enable = ConfigYesNo(default=True)
horatest = 2
config.plugins.autodeepsleep.sleep = ConfigClock(default=(horatest * 60 + 0) * 60)
config.plugins.autodeepsleep.wakeup = ConfigClock(default=(horatest * 60 + 0) * 60 + 28800)

def debugtxt(loque, loque2 = None, inicio = False):
    return
    import os
    if inicio:
        os.system("echo ''>/etc/debugdeep.log")
    os.system("echo '******************************'>>/etc/debugdeep.log")
    os.system('date>>/etc/debugdeep.log')
    os.system("echo '" + str(loque) + "'>>/etc/debugdeep.log")
    if loque2 != None:
        os.system("echo '" + str(loque2) + "'>>/etc/debugdeep.log")
    os.system("echo '******************************'>>/etc/debugdeep.log")


def clkToTime(clock):
    return (clock.value[0] * 60 + int(clock.value[1])) * 60


def getTime():
    ltime = localtime()
    return (int(ltime.tm_hour) * 60 + int(ltime.tm_min)) * 60


tiemporeposo = -1

def ini_timer(session = None):
    global tiemporeposo
    global TiempoWakeUp
    global TimerReposo
    global TimerTempReposo
    if config.plugins.autodeepsleep.enable.value:
        if TimerReposo == None:
            TimerTempReposo = eTimer()
            TimerReposo = eTimer()
            TimerTempReposo.callback.append(ini_timer)
            TimerReposo.callback.append(lanza_reposo)
            debugtxt('ini_timer initialized')
        debugtxt('ini_timer check')
        TiempoWakeUp = setNextWakeup()
        try:
            TimerReposo.stop()
            TimerTempReposo.stop()
        except:
            pass

        lotime = localtime()
        wbegin = config.plugins.autodeepsleep.sleep.value
        wend = config.plugins.autodeepsleep.sleep.value
        xtimem = lotime[3] * 60 + lotime[4]
        ytimem = wbegin[0] * 60 + wbegin[1]
        ztimem = wend[0] * 60 + wend[1] + 180
        if ytimem > ztimem:
            ztimem += 720
        minsToGo = ytimem - xtimem
        if xtimem > ztimem:
            minsToGo += 1440
        if minsToGo > 0:
            if minsToGo < 0:
                minsToGo += 1440
            elif minsToGo == 0:
                minsToGo = 1
            debugtxt('ini_timer ' + str(minsToGo) + 'min.', minsToGo * 60000)
            TimerReposo.start(minsToGo * 60000, True)
            tiemporeposo = minsToGo * 60000
            minutes = minsToGo
            mints = minutes % 60
            hours = minutes / 60
            debugtxt('sleep en ' + str(hours) + 'horas ', '' + str(mints) + 'minutos ')
        else:
            recordings = len(session.nav.getRecordings())
            next_rec_time = session.nav.RecordTimer.getNextRecordingTime()
            if not recordings and (next_rec_time - time() > 360 or next_rec_time < 0):
                lanza_reposo()
            else:
                debugtxt('grabacion pendiente o en curso esperamos 15min')
                TimerReposo.start(900000, True)
    else:
        debugtxt('ini_timer AutoDeepStandby disabled')
        try:
            TimerTempReposo.stop()
            TimerReposo.stop()
        except:
            pass

        try:
            TimerTempReposo = None
            TimerReposo = None
        except:
            pass


def lanza_reposo():
    global TiempoWakeUp
    TiempoWakeUp = setNextWakeup()
    debugtxt('lanza_reposo activado ' + str(TiempoWakeUp), config.plugins.autodeepsleep.sleep.value)
    from Screens.Standby import inTryQuitMainloop
    if not inTryQuitMainloop:
        debugtxt('lanzar_reposo')
        TimerTempReposo.stop()
        lanzar_reposo()
    else:
        debugtxt('lanza_reposo cancelado ya en intryquitmailloop')


def lanzar_reposo():
    global TiempoWakeUp
    TiempoWakeUp = setNextWakeup()
    cret = auto_reposo_profundo()
    if cret:
        TimerReposo.start(60000, True)
        debugtxt('lanzar_reposo verificar 600000')
    else:
        TimerReposo.start(900000, True)
        debugtxt('lanzar_reposo mirar mas tarde 15 min')


def auto_reposo_profundo():
    debugtxt('auto reposo profundo')
    from Screens.InfoBar import InfoBar
    lasesion = None
    if InfoBar and InfoBar.instance:
        try:
            lasesion = InfoBar.instance.session
        except:
            pass

    if lasesion == None:
        return False
    recordings = lasesion.nav.getRecordings()
    next_rec_time = -1
    if not recordings:
        next_rec_time = lasesion.nav.RecordTimer.getNextRecordingTime()
    if recordings or next_rec_time > 0 and next_rec_time - time() < 360:
        return False
    from Screens.Standby import TryQuitMainloop, inStandby
    debugtxt('auto reposo profundo 2')
    if inStandby:
        debugtxt('auto reposo profundo activado')
        from enigma import quitMainloop
        try:
            debugtxt('REPOSO PROFUNDO OK')
            quitMainloop(1)
        except:
            debugtxt('ERROR AL IR A REPOSO PROFUNDO')
            return false

        return True
        if config.plugins.autodeepsleep.enable.value:
            debugtxt('Autostart AutoDeepStandby enabled')
            ini_timer(lasession)
        else:
            debugtxt('Autostart AutoDeepStandby disabled')
    else:
        debugtxt('auto reposo profundo : No en standby')
        return False


def devcadtiempo():
    temptiepo = tiemporeposo / 60000
    mints = temptiepo % 60
    hours = temptiepo / 60
    cad = _('Time left for next auto sleep:') + str(hours) + ' ' + _('hours') + ' ' + str(mints) + ' ' + _('minutes')
    temptiepo = TiempoWakeUp / 60000
    mints = temptiepo % 60
    hours = temptiepo / 60
    cad = cad + '\n' + _('Time left for next auto wake up:') + str(hours) + ' ' + _('hours') + ' ' + str(mints) + ' ' + _('minutes')
    return cad


def setNextWakeup():
    debugtxt('setNextWakeup', TiempoWakeUp)
    if not config.plugins.autodeepsleep.enable.value or config.plugins.autodeepsleep.wakeup.value[0] == config.plugins.autodeepsleep.sleep.value[0] and config.plugins.autodeepsleep.wakeup.value[1] == config.plugins.autodeepsleep.sleep.value[1]:
        debugtxt('Next wake up deactivated, no sleep', TiempoWakeUp)
        return -1
    now = localtime()
    begin = mktime((now.tm_year,
     now.tm_mon,
     now.tm_mday,
     config.plugins.autodeepsleep.wakeup.value[0],
     config.plugins.autodeepsleep.wakeup.value[1],
     0,
     now.tm_wday,
     now.tm_yday,
     now.tm_isdst))
    debugtxt('setNextWakeup', begin)
    if begin > time():
        return begin
    debugtxt('setNextWakeup add 1 day ', begin + 86400)
    return begin + 86400


def autostart(reason, **kwargs):
    global session
    debugtxt('autostart')
    if reason == 0 and kwargs.has_key('session'):
        session = kwargs['session']
        if config.plugins.autodeepsleep.enable.value:
            debugtxt('Autostart AutoDeepStandby enabled')
            ini_timer(session)
        else:
            debugtxt('Autostart AutoDeepStandby disabled')


def info_timer(ses = None):
    lacad = devcadtiempo()
    debugtxt(lacad)


def getNextWakeup():
    try:
        debugtxt('getNextWakeup TiempoWakeUp', TiempoWakeUp)
    except:
        pass

    if session is None:
        return TiempoWakeUp
    nextTimer = session.nav.RecordTimer.getNextRecordingTime()
    if nextTimer < 1 or nextTimer > TiempoWakeUp:
        return TiempoWakeUp
    try:
        debugtxt('getNextWakeup nextimer ', nextTimer - 1)
    except:
        pass

    return nextTimer - 1
