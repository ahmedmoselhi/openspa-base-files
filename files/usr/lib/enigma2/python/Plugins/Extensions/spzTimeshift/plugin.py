from Components.Label import Label
from enigma import eServiceCenter, eServiceReference
from enigma import eTimer, iPlayableService
from ServiceReference import ServiceReference
from Components.Pixmap import Pixmap
from Plugins.Extensions.spazeMenu.plugin import limpiamemoria
from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.EventView import EventViewSimple
from Screens import Standby
from Screens.InfoBarGenerics import delResumePoint
from Screens.InfoBar import MoviePlayer
from Components.SystemInfo import SystemInfo
from Components.ActionMap import ActionMap
import NavigationInstance
from RecordTimer import AFTEREVENT
from Components.config import config, ConfigClock
from Tools.FuzzyDate import FuzzyTime
from Tools import Notifications
from time import localtime, time, mktime
import os
from Screens.TimeDateInput import TimeDateInput
from os import environ
import gettext
from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE, fileExists
from Plugins.Extensions.spazeMenu.spzPlugins.scrInformation.plugin import mostrarNotificacion, scrInformation
lang = language.getLanguage()
environ['LANGUAGE'] = lang[:2]
lenguaje = str(lang[:2])
gettext.bindtextdomain('enigma2', resolveFilename(SCOPE_LANGUAGE))
gettext.textdomain('enigma2')
gettext.bindtextdomain('spzTimeshift', '%s%s' % (resolveFilename(SCOPE_PLUGINS), 'Extensions/spzTimeshift/locale/'))
fin = 0

def _(txt):
    t = gettext.dgettext('spzTimeshift', txt)
    if t == txt:
        t = gettext.gettext(txt)
    return t


tmrecord = None
currservice = None

class spzTimeshiftPIPp(Screen):

    def __init__(self, session, parent, nocapturar = True):
        skin = ''
        skin += '<screen name="spzTimeshiftPIPp" position="0,0" size="1280,720" title="VirtualPIP" flags="wfNoBorder" backgroundColor="#ff000000">'
        skin += '\t  <widget name="img_blue" position="1023,674" size="27,19" alphatest="blend" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spzTimeshift/img/yellow-fs8.png" zPosition="23" />'
        skin += '\t  <widget name="tex_blue" position="1053,672" size="215,18" transparent="1" font="Regular; 16" backgroundColor="black" foregroundColor="#ababab" noWrap="1" zPosition="23" />'
        skin += '\t  <widget name="fondo" position="0,644" size="1280,76" backgroundColor="#40000000" zPosition="22" />'
        skin += '<eLabel name="infopause" position="38,645" size="29,22" transparent="1" font="Regular;19" backgroundColor="black" foregroundColor="white" shadowColor="#000000" shadowOffset="-2,-2" zPosition="23" text="||" />'
        skin += '<widget source="session.CurrentService" render="Label" position="67,645" size="415,24" transparent="1" font="Regular;21" backgroundColor="#000000" foregroundColor="#006cbcf0" shadowColor="#000000" shadowOffset="-2,-2" zPosition="23">'
        skin += '  <convert type="ServiceName">Name</convert>'
        skin += '</widget>'
        skin += '<widget source="session.Event_Now" render="Label" position="67,670" size="99,22" transparent="1" font="Regular;18" backgroundColor="#000000" foregroundColor="#ababab" halign="left" shadowColor="#000000" shadowOffset="-2,-2" zPosition="23">'
        skin += '  <convert type="EventTime">Remaining</convert>'
        skin += '  <convert type="RemainingToText">InMinutes</convert>'
        skin += '</widget>'
        skin += '<widget source="session.Event_Now" render="Label" position="152,670" size="380,22" transparent="1" font="Regular;18" backgroundColor="#000000" foregroundColor="#ffffff" halign="left" shadowColor="#000000" shadowOffset="-2,-2" zPosition="23" noWrap="1">'
        skin += ' <convert type="EventName">Name</convert>'
        skin += '</widget>'
        skin += '<widget source="session.RecordState" position="1139,651" render="Label" size="111,23" valign="center" halign="left" zPosition="23" backgroundColor="black" foregroundColor="#00ff4040" font="Regular; 18" transparent="1">'
        skin += '<convert type="infoRecBm">Restan</convert>'
        skin += '</widget>'
        skin += '<eLabel name="irec" position="1024,651" size="111,23" valign="center" halign="right" zPosition="23" backgroundColor="black" foregroundColor="#00ff4040" font="Regular; 18" transparent="1" text="[REC] +" />'
        skin += '\t</screen>'
        self.skin = skin
        Screen.__init__(self, session)
        self.parent = parent
        self.trabajando = False
        self.skinName = 'spzTimeshiftPIPp'
        self['tex_blue'] = Label(_('Continue play'))
        self['fondo'] = Label(' ')
        self['img_blue'] = Pixmap()
        self['actions'] = ActionMap(['OkCancelActions',
         'ColorActions',
         'DirectionActions',
         'WizardActions',
         'EPGSelectActions',
         'InfobarActions',
         'InfobarSeekActions',
         'InfobarEPGActions'], {'yellow': self.Exit,
         'playpauseService': self.Exit,
         'pauseService': self.Exit,
         'showMovies': self.Exit,
         'cancel': self.Exit,
         'showGraphEPG': self.Exit,
         'info': self.muestrabarra}, -1)

    def cierra(self):
        self.close(1)

    def Exit(self):
        self.parent.reanudar(False)
        self.close(1)

    def muestrabarra(self):
        self.parent.openEventView()


def tmshowPiP(self):
    try:
        slist = self.servicelist
        if self.session.pipshown:
            if slist and slist.dopipzap:
                slist.togglePipzap()
            del self.session.pip
            self.session.pipshown = False
        else:
            from Screens.PictureInPicture import PictureInPicture
            self.session.pip = self.session.instantiateDialog(PictureInPicture)
            self.session.pip.show()
            self.session.pipshown = True
            self.session.pip.playService(slist.getCurrentSelection())
    except:
        pass


class spzTimeshift_summary(Screen):
    skin = '\n\t<screen position="0,0" size="132,64">\n\t\t<widget source="global.CurrentTime" render="Label" position="62,46" size="64,18" font="Regular;16" halign="right" >\n\t\t\t<convert type="ClockToText">WithSeconds</convert>\n\t\t</widget>\n\t\t<widget source="session.RecordState" render="FixedLabel" text=" " position="62,46" size="64,18" zPosition="1" >\n\t\t\t<convert type="ConfigEntryTest">config.usage.blinking_display_clock_during_recording,True,CheckSourceBoolean</convert>\n\t\t\t<convert type="ConditionalShowHide">Blink</convert>\n\t\t</widget>\n\t\t<widget source="session.CurrentService" render="Label" position="6,4" size="120,42" font="Regular;18" >\n\t\t\t<convert type="ServiceName">Name</convert>\n\t\t</widget>\n\t\t<widget source="session.CurrentService" render="Progress" position="6,46" size="56,18" borderWidth="1" >\n\t\t\t<convert type="ServicePosition">Position</convert>\n\t\t</widget>\n\t</screen>'


from Screens.InfoBarGenerics import InfoBarMoviePlayerSummarySupport, InfoBarMoviePlayerSummary

class InfoBarMoviePlayerSummarySupport():

    def __init__(self):
        pass

    def createSummary(self):
        return spzTimeshift_summary


class tmInfoBarMoviePlayerSummarySupport():

    def __init__(self):
        pass

    def createSummary(self):
        return spzTimeshift_summary


class spzTimeshift(MoviePlayer):

    def __init__(self, session, parar = True):
        global currservice
        self.session = session
        self.resume_point = None
        service = None
        self.ckTimer = eTimer()
        self.endirecto = False
        self.ckTimer.callback.append(self.aumentarTiempo)
        self.mastiempo = True
        self.posicion = None
        self.contador = 0
        if currservice:
            self.lastservice = currservice
        self.fin = 0
        self.tempTimer = eTimer()
        self.tempTimer.callback.append(self.retarda)
        self.maxpos = 0
        self.parar = parar
        self.pausado = not parar
        self.listarec = []
        self.grabacion = None
        self.contador_ini = 0
        Screen.__init__(self, session)
        MoviePlayer.__init__(self, session, service)
        self.skinName = ['spzTimeshift', 'MoviePlayer', 'spzTimeshift_summary']
        self['actions'] = ActionMap(['InfobarActions'], {'showMovies': self.nada,
         'showRadio': self.nada,
         'showTv': self.nada}, -3)
        self['actions'] = ActionMap(['MoviePlayerActions',
         'MenuActions',
         'GlobalActions',
         'StandbyActions',
         'ColorActions',
         'InfobarActions',
         'DirectionActions',
         'EPGSelectActions',
         'InfobarEPGActions',
         'OkCancelActions',
         'NumberActions'], {'leavePlayer': self.leavePlayer,
         'cancel': self.leavePlayer,
         'exit': self.leavePlayer,
         'power_down': self.apagar,
         'power_up': self.apagar,
         'menu': self.leavePlayer,
         'info': self.openEventView,
         'showEventInfo': self.openEventView,
         'mainMenu': self.leavePlayer,
         'showMovies': self.nada,
         'keyTV': self.nada,
         'showTv': self.nada,
         'showRadio': self.nada,
         'down': self.nada,
         'up': self.nada,
         'showGraphEPG': self.showMovies,
         'ok': self.keyok,
         '8': self.menupip,
         '0': self.creamarca,
         '1': self.k_1,
         '3': self.k_3,
         '4': self.k_4,
         '6': self.k_6,
         '7': self.k_7,
         '9': self.k_9}, -3)
        self['SeekActions'] = ActionMap(['InfobarSeekActions'], {'playpauseService': self.TMplaypauseService,
         'pauseService': self.TMpauseService,
         'unPauseService': self.TMunPauseService,
         'seekFwd': self.TMseekFwd,
         'seekFwdManual': self.TMseekFwdManual,
         'seekBack': self.TMseekBack,
         'seekBackManual': self.TMseekBackManual}, prio=-1)
        if parar:
            eliminaDialogos(self.session)
        self.iniciado = False
        self.onShown.append(self.mostrar)
        self.trabajando = False
        self.Console = None
        self.temppos = -1
        self.temppos2 = -4
        self.dei = None
        self.dialogo = None
        self.initiempo = mktime(localtime())
        limpiamemoria(3, 'timeshift_init')

    def createSummary(self):
        return spzTimeshift_summary

    def creamarca(self):
        try:
            self.toggleMark()
        except:
            pass

    def k_1(self):
        ertiempo = -config.seek.selfdefined_13.value
        self.doSeekRelative(ertiempo * 90000)

    def k_3(self):
        ertiempo = config.seek.selfdefined_13.value
        self.doSeekRelative(ertiempo * 90000)

    def k_4(self):
        ertiempo = -config.seek.selfdefined_46.value
        self.doSeekRelative(ertiempo * 90000)

    def k_6(self):
        ertiempo = config.seek.selfdefined_46.value
        self.doSeekRelative(ertiempo * 90000)

    def k_7(self):
        ertiempo = -config.seek.selfdefined_79.value
        self.doSeekRelative(ertiempo * 90000)

    def k_9(self):
        ertiempo = config.seek.selfdefined_79.value
        self.doSeekRelative(ertiempo * 90000)

    def menupip(self, nnum = 0, nmenu = False):
        if SystemInfo.get('NumVideoDecoders', 1) > 1:
            if not fileExists('/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/spzPiPMenu/plugin.pyo'):
                from Screens.InfoBar import InfoBar
                InfoBar.instance.showPiP()
                return
            try:
                from Plugins.Extensions.spazeMenu.spzPlugins.spzPiPMenu.plugin import pipmenu
                pipmenu(self.session, nomenu=nmenu, limitar=True, refPip=self.lastservice)
            except:
                pass

    def keyok(self):
        self.toggleShow()

    def showPiP(self):
        slist = None
        try:
            slist = self.servicelist
        except:
            pass

        try:
            slist = self.servicelist
        except:
            pass

        if self.session.pipshown:
            try:
                if slist and slist.dopipzap:
                    slist.togglePipzap()
            except:
                pass

            del self.session.pip
            self.session.pipshown = False
        else:
            from Screens.PictureInPicture import PictureInPicture
            self.session.pip = self.session.instantiateDialog(PictureInPicture)
            self.session.pip.show()
            self.session.pipshown = True
            self.session.pip.playService(self.lastservice)

    def swapPiP(self):
        pass

    def openEventView(self):
        epglist = []
        self.epglist = epglist
        service = self.session.nav.getCurrentService()
        ref = self.session.nav.getCurrentlyPlayingServiceOrGroup()
        info = service.info()
        ptr = info.getEvent(0)
        if ptr:
            epglist.append(ptr)
        ptr = info.getEvent(1)
        if ptr:
            epglist.append(ptr)
        if epglist:
            self.session.open(EventViewSimple, epglist[0], ServiceReference(ref))

    def esok(self, timer):
        try:
            if timer.Filename == self.grabacion.Filename:
                return True
            return False
        except:
            return False

    def cbmostrar(self, respuesta = 0):
        self.temppos = -9
        if respuesta == 3:
            self.session.openWithCallback(self.cbmostrar, spzTimeshiftPIPp, self, True)

    def muestradirecto(self):
        self.dei = None
        self.session.openWithCallback(self.cbmostrar, spzTimeshiftPIPp, self)

    def showMovies(self):
        if not self.endirecto:
            self.activapip()

    def nada(self):
        pass

    def apagar(self):
        self.ckTimer.stop()
        for timer in NavigationInstance.instance.RecordTimer.timer_list:
            if timer.state == timer.StateRunning and self.esok(timer):
                nfaltan = (timer.end - time()) / 60
                timer.autoincrease = False
                if nfaltan <= 30:
                    timer.end = timer.end + 3600
                self.session.nav.RecordTimer.timeChanged(timer)
                break

        self.ckTimer.stop()
        self.forzarpausa()
        self.salir()
        Notifications.AddNotification(Standby.Standby)

    def iniciatm(self):
        global tmrecord
        self.listarec = []
        ernombre = ''
        if tmrecord == None:
            for timer in NavigationInstance.instance.RecordTimer.timer_list:
                if timer.state == timer.StateRunning and not timer.disabled:
                    try:
                        if timer.Filename:
                            pass
                        self.listarec.append(timer)
                        tmrecord = timer
                        ernombre = '' + timer.name
                    except:
                        pass

            if len(self.listarec) > 1:
                self.seleGrab()
                return
        if tmrecord == None:
            self.iniciado = False
            if self.contador_ini <= 3:
                eliminaDialogos(self.session)
                mostrarNotificacion(id='timeshift', texto=_('Waiting for record start') + '...', titulo=_('TimeShift'), segundos=6, mostrarSegundos=False, cerrable=False)
                self.contador_ini = self.contador_ini + 1
            return
        self.iniciaplay()
        if not ernombre == '':
            self.doTimerHide()
            mostrarNotificacion(id='timeshift', texto=ernombre, titulo=_('TimeShift'), segundos=3, mostrarSegundos=True, cerrable=True)

    def cbseleGrab(self, answer):
        global tmrecord
        answer = answer and answer[1]
        notificado = None
        if not answer:
            sel = 0
        else:
            sel = int(answer)
        tmrecord = self.listarec[sel]
        self.iniciaplay()

    def seleGrab(self):
        list = []
        nkeys = []
        conta = 0
        for elerec in self.listarec:
            nombre = elerec.name
            if len(nombre) > 20:
                nombre = nombre[:17] + '...'
            nombre = nombre + ' (' + str(FuzzyTime(elerec.begin)[1])
            nombre = nombre + ' - ' + str(FuzzyTime(elerec.end)[1])
            nombre = nombre + ') ' + elerec.service_ref.getServiceName()
            list.append((nombre + ' ', str(conta)))
            nkeys.append(str(conta + 1))
            if conta < 9:
                conta = conta + 1

        from Screens.ChoiceBox import ChoiceBox
        self.session.openWithCallback(self.cbseleGrab, ChoiceBox, keys=nkeys, title='TimeShift - ' + _('Select Record to play'), list=list)

    def iniciaplay(self):
        global fin
        self.iniciatiempo()
        self.grabacion = tmrecord
        filename = str(self.grabacion.Filename) + '.ts'
        if fin > 0:
            self.fin = fin + 1800
        elif fin == 0:
            self.fin = self.grabacion.end + 1800
        else:
            self.fin = 0
        service = eServiceReference('1:0:0:0:0:0:0:0:0:0:' + filename)
        self.service = service
        self.servicecopy = service
        try:
            self.cur_service = service
        except:
            pass

        self.session.nav.playService(self.service)
        self.listarec = []
        self.doShow()
        if self.parar:
            self.temppos = -15
            self.pauseService()
            self.pausado = True

    def mostrar(self):
        self.hideTimer.stop()
        if not self.iniciado:
            self.iniciado = True
            self.iniciatm()
        else:
            self.doShow()

    def TMplaypauseService(self):
        self.temppos = -5
        self.playpauseService()

    def TMpauseService(self):
        if self.endirecto:
            return
        self.pauseService()

    def TMunPauseService(self):
        if self.endirecto:
            return
        self.temppos = -6
        self.unPauseService()

    def TMseekFwd(self):
        self.maxpos = 0
        if self.endirecto:
            return
        self.seekFwd()

    def TMseekFwdManual(self):
        self.maxpos = 0
        if self.endirecto:
            return
        self.seekFwdManual()

    def TMseekBack(self):
        self.maxpos = 0
        if self.endirecto:
            return
        self.seekBack()

    def TMseekBackManual(self):
        self.maxpos = 0
        if self.endirecto:
            return
        self.seekBackManual()

    def doSeek(self, pts, reiniciar = True):
        self.maxpos = 0
        self.ckTimer.stop()
        seekable = self.getSeek()
        if seekable is None:
            return
        if reiniciar:
            self.iniciatiempo(5000)
        seekable.seekTo(pts)

    def doSeekRelative(self, pts, reiniciar = True):
        self.maxpos = 0
        self.ckTimer.stop()
        seekable = self.getSeek()
        if seekable is None:
            return
        if reiniciar:
            self.iniciatiempo(5000)
        prevstate = self.seekstate
        if self.seekstate == self.SEEK_STATE_EOF:
            if prevstate == self.SEEK_STATE_PAUSE:
                self.setSeekState(self.SEEK_STATE_PAUSE)
            else:
                self.setSeekState(self.SEEK_STATE_PLAY)
        seekable.seekRelative(pts < 0 and -1 or 1, abs(pts))
        if abs(pts) > 100 and config.usage.show_infobar_on_skip.value:
            self.showAfterSeek()

    def playpauseService(self):
        if self.endirecto:
            self.reanudar()
        else:
            self.temppos = -12
            self.iniciatiempo(6000)
            if self.seekstate != self.SEEK_STATE_PLAY:
                self.unPauseService()
                if self.cueGetCurrentPosition() == self.temppos2:
                    pass
                self.temppos2 = -2
            else:
                self.temppos2 = self.cueGetCurrentPosition()
                self.pauseService()

    def iniciatiempo(self, valor = 30000):
        self.ckTimer.stop()
        self.ckTimer.start(valor, True)

    def fueraConfirmed(self, respuesta):
        if respuesta:
            self.forzarpausa()
            self.ckTimer.stop()
            try:
                self.stopRecordConfirmation(True)
            except:
                pass

            self.salir()
        else:
            self.initiempo = mktime(localtime())

    def aumentarTiempo(self, respuesta = None):
        self.ckTimer.stop()
        if self.initiempo + 21600 < mktime(localtime()):
            self.session.openWithCallback(self.fueraConfirmed, MessageBox, text=_('It takes more than 6 hours using the timeshift\nWant to stop timeshift?\nThe timeshift function will stop. Choose not to continue.'), type=MessageBox.TYPE_YESNO, timeout=30)
            self.iniciatiempo(50000)
            return
        self.contador = self.contador + 1
        self.maxpos = 0
        if self.mastiempo:
            for timer in NavigationInstance.instance.RecordTimer.timer_list:
                if timer.state == timer.StateRunning and self.esok(timer):
                    nfaltan = (timer.end - time()) / 60
                    if nfaltan <= 2:
                        timer.autoincrease = False
                        timer.end = timer.end + 900
                        self.session.nav.RecordTimer.timeChanged(timer)
                    break

        if not self.endirecto:
            if self.seekstate == self.SEEK_STATE_PLAY:
                if not self.dialogo == None:
                    self.temppos = -15
                else:
                    if self.cueGetCurrentPosition() == self.temppos and self.temppos > 3:
                        self.temppos = -3
                        self.iniciatiempo(8000)
                        return
                    self.temppos = self.cueGetCurrentPosition()
        if self.dialogo == None:
            self.ckTimer.start(1100, True)
        else:
            self.temppos = -16
            self.ckTimer.start(6100, True)
        if 'spzTimeshift' in str(self.session.current_dialog):
            self.dialogo = None
        else:
            self.dialogo = str(self.session.current_dialog)

    def setEndtime(self, entry):
        elfin = entry.end
        if self.fin > 0 and self.fin >= entry.begin:
            elfin = self.fin
        endtime = ConfigClock(default=elfin)
        dlg = self.session.openWithCallback(self.TimeDateInputClosed, TimeDateInput, endtime)
        dlg.setTitle(_('Please change recording endtime'))

    def TimeDateInputClosed(self, ret):
        if len(ret) > 1:
            if ret[0]:
                localendtime = localtime(ret[1])
                for timer in NavigationInstance.instance.RecordTimer.timer_list:
                    if timer.state == timer.StateRunning and self.esok(timer):
                        if timer.end != ret[1]:
                            if timer.begin >= ret[1]:
                                from Screens.MessageBox import MessageBox
                                self.session.open(MessageBox, _('End date/time is less than begin date/time!!!') + '\n' + _('End time NOT changed'), MessageBox.TYPE_ERROR, timeout=8)
                                return
                            timer.autoincrease = False
                            self.mastiempo = False
                            timer.end = ret[1]
                            self.session.nav.RecordTimer.timeChanged(timer)
                            mostrarNotificacion(id='timeshift', texto=_('End timer changed!'), segundos=1, mostrarSegundos=False)
                        break
                        return

        self.aumentarTiempo()

    def doEofInternal(self, playing):
        self.iniciatiempo(12000)
        try:
            ref = self.session.nav.getCurrentlyPlayingServiceReference()
            if ref:
                delResumePoint(ref)
        except:
            pass

        if len(self.session.nav.getRecordings()) > 0:
            for timer in NavigationInstance.instance.RecordTimer.timer_list:
                if timer.state == timer.StateRunning and self.esok(timer):
                    self.posicion = self.cueGetCurrentPosition()
                    seekable = self.getSeek()
                    if seekable is not None:
                        self.posicion = seekable.getLength()[1] - 1350000
                    if self.maxpos >= self.posicion - 90000:
                        self.maxpos = self.posicion
                        self.tempTimer.start(1000, True)
                        return
                    mensaje = _('Join live tv')
                    mostrarNotificacion(id='timeshift', texto=mensaje, segundos=2, mostrarSegundos=False, cerrable=True)
                    self.iniciatiempo(12000)
                    self.tempTimer.start(1000, True)
                    self.maxpos = self.posicion
                    return

        self.leavePlayer()

    def retarda(self):
        self.iniciatiempo(12000)
        self.service = self.servicecopy
        self.ENABLE_RESUME_SUPPORT = False
        self.session.nav.playService(self.service, forceRestart=True)
        self.temppos = -8
        self.iniciatiempo(8000)
        self.forzarpausa()
        self.setSeekState(self.SEEK_STATE_PLAY)
        try:
            self.doSeek(self.posicion)
        except:
            pass

        self.posicion = 0

    def handleLeave(self, how):
        self.is_closing = True
        nfaltan = None
        if len(self.session.nav.getRecordings()) > 0:
            nquedan = 0
            faltan = 0
            for timer in NavigationInstance.instance.RecordTimer.timer_list:
                if timer.state == timer.StateRunning and self.esok(timer):
                    nfaltan = (timer.end - time()) / 60
                    if nfaltan >= 1:
                        faltan = str(int(nfaltan)) + ' ' + _('mins')
                    else:
                        faltan = str(int(nfaltan * 60)) + ' ' + _('secs')
                    nquedan = int((timer.end - timer.begin) / 60)
                    break

            quedan = str(faltan)
        if nfaltan:
            nkeys = ['yellow',
             'green',
             '',
             '',
             'red',
             '0',
             '1',
             '',
             '2',
             '3',
             '4',
             '5']
            list = [(_('Exit and stop record and delete movie'), 'quitanddeleteconfirmed'),
             (_('Exit and continue recording') + ' (+' + quedan + ')', 'quit'),
             (_('Exit and stop record'), 'quitandstop'),
             ('--', 'nada'),
             (_('Audio selection'), 'audio'),
             (_('Scaling Mode'), 'scale'),
             (_('Information') + '...', 'info'),
             ('--', 'nada'),
             (_('Record manager'), 'record'),
             (_('Set end of record'), 'changeendtime'),
             (_('Restart playing from begin'), 'restart')]
        else:
            nkeys = ['yellow',
             'green',
             '',
             'red',
             '0',
             '1',
             '',
             '2',
             '4']
            list = [(_('Exit and delete movie'), 'quitanddeleteconfirmed'),
             (_('Exit'), 'quit'),
             ('--', 'nada'),
             (_('Audio selection'), 'audio'),
             (_('Scaling Mode'), 'scale'),
             (_('Information') + '...', 'info'),
             ('--', 'nada'),
             (_('Record manager'), 'record'),
             (_('Restart playing from begin'), 'restart')]
        if self.endirecto == False:
            list.append((_('Go to end of record') + ' ', 'end'))
            nkeys.append('6')
            list.append((_('View live TV') + ' ', 'live'))
            nkeys.append('7')
        try:
            if SystemInfo.get('NumVideoDecoders', 1) > 1:
                if self.session.pipshown:
                    list.append((_('Show Menu PiP') + ' ', 'pip'))
                else:
                    list.append((_('PiP (Picture in Picture)') + ' ', 'pip'))
                nkeys.append('8')
        except:
            pass

        list.append(('--', 'nada'))
        nkeys.append('')
        list.append((_('Delete') + '/' + _('Toggle a cut mark at the current position') + ' ', 'mark'))
        nkeys.append('0')
        from Screens.ChoiceBox import ChoiceBox
        self.session.openWithCallback(self.leavePlayerConfirmed, ChoiceBox, keys=nkeys, title='TimeShift - ' + _('What do you do?'), list=list)

    def leavePlayerConfirmed(self, answer):
        answer = answer and answer[1]
        notificado = None
        if answer in ('quitanddelete', 'quitanddeleteconfirmed'):
            if self.endirecto:
                self.reanudar()
            if len(self.session.nav.getRecordings()) > 0:
                self.ckTimer.stop()
                try:
                    self.stopRecordConfirmation(True)
                except:
                    pass

            try:
                ref = self.session.nav.getCurrentlyPlayingServiceReference()
                from enigma import eServiceCenter
                serviceHandler = eServiceCenter.getInstance()
                info = serviceHandler.info(ref)
                name = info and info.getName(ref) or _('this recording')
                self.forzarpausa()
                if answer == 'quitanddelete':
                    self.session.openWithCallback(self.deleteConfirmed, MessageBox, _('Do you really want to delete %s?') % name)
                    return
                if answer == 'quitanddeleteconfirmed':
                    offline = serviceHandler.offlineOperations(ref)
                    self.ckTimer.stop()
                    if offline.deleteFromDisk(0):
                        self.session.openWithCallback(self.salir, MessageBox, _('You cannot delete this!'), MessageBox.TYPE_ERROR)
                        return
                    else:
                        self.salir()
                        mostrarNotificacion(id='timeshift', texto=_('Movie Deleted!'), segundos=2, mostrarSegundos=False)
                        notificado = 1
                        return
            except:
                self.salir()

        if answer in ('quit', 'quitanddeleteconfirmed'):
            self.ckTimer.stop()
            try:
                self.forzarpausa()
                self.ENABLE_RESUME_SUPPORT = True
                for timer in NavigationInstance.instance.RecordTimer.timer_list:
                    if timer.state == timer.StateRunning and self.esok(timer):
                        timer.autoincrease = False
                        self.session.nav.RecordTimer.timeChanged(timer)
                        self.salir()
                        if notificado == 1:
                            pass
                        else:
                            mostrarNotificacion(id='timeshift', texto=_('Recording!') + ' ' + timer.name, segundos=4)
                        return
                        break

            except:
                pass

            self.salir()
        elif answer == 'quitandstop':
            try:
                self.ENABLE_RESUME_SUPPORT = True
                self.forzarpausa()
                self.ckTimer.stop()
                self.stopRecordConfirmation(True)
            except:
                pass

            self.salir()
        elif answer == 'pip':
            self.menupip(nmenu=True)
        elif answer == 'restart':
            if self.endirecto == True:
                self.ENABLE_RESUME_SUPPORT = False
                self.session.nav.playService(self.service)
                self.endirecto = False
                self.posicion = None
            self.posicion = 0
            self.temppos = -8
            self.iniciatiempo(8000)
            self.forzarpausa()
            self.doSeek(0)
            self.setSeekState(self.SEEK_STATE_PLAY)
        elif answer == 'changeendtime':
            try:
                self.ckTimer.stop()
                for timer in NavigationInstance.instance.RecordTimer.timer_list:
                    if timer.state == timer.StateRunning and self.esok(timer):
                        self.setEndtime(timer)
                        break

            except:
                pass

        elif answer == 'live':
            self.activapip()
        elif answer == 'continue':
            if self.endirecto == True:
                self.reanudar()
            else:
                try:
                    xpos = self.cueGetCurrentPosition()
                    self.doSeek(xpos)
                except:
                    pass

        elif answer == 'audio':
            self.set_audio()
        elif answer == 'mark':
            self.creamarca()
        elif answer == 'end':
            try:
                seekable = self.getSeek()
                if seekable is not None:
                    self.posicion = seekable.getLength()[1] - 1440000
                    self.doSeek(self.posicion)
            except:
                pass

        elif answer == 'scale':
            self.set_scaling()
        elif answer == 'record':
            self.record_manager()
        elif answer == 'info':
            from Plugins.Extensions.spazeMenu.spzPlugins.InfoAz.plugin import iniciainfo
            iniciainfo(self.session)

    def salir(self):
        global currservice
        global gsession
        global tmrecord
        try:
            if not self.cur_service:
                self.cur_service = eServiceReference('1:0:0:0:0:0:0:0:0:0:na')
        except:
            pass

        currservice = None
        gsession = None
        tmrecord = None
        try:
            if self.session.pipshown:
                del self.session.pip
                self.session.pipshown = False
        except:
            pass

        self.close()

    def forzarpausa(self):
        if self.seekstate != self.SEEK_STATE_PLAY:
            pass
        else:
            self.temppos = -10
            self.pauseService()

    def activapip(self):
        self.endirecto = True
        self.forzarpausa()
        self.posicion = self.cueGetCurrentPosition()
        self.iradirecto()
        self.muestradirecto()

    def iradirecto(self):
        self.maxpos = 0
        self.session.nav.playService(self.lastservice)

    def reanudar(self, pausar = False):
        self.iniciatiempo(10000)
        self.ENABLE_RESUME_SUPPORT = False
        self.temppos = -4
        self.session.nav.playService(self.service)
        if self.posicion:
            self.doSeek(self.posicion - 3)
            if pausar:
                self.forzarpausa()
        self.posicion = None
        self.endirecto = False

    def stopRecordConfirmation(self, confirmed):
        if not confirmed:
            return
        filename = ''
        for timer in NavigationInstance.instance.RecordTimer.timer_list:
            if timer.state == timer.StateRunning and self.esok(timer):
                filename = str(timer.Filename)
                break

        if filename == '':
            return
        if filename[0] == '/':
            filename = os.path.split(filename)[1]
        if filename.endswith('.ts'):
            filename = filename[:-3]
        for timer in NavigationInstance.instance.RecordTimer.timer_list:
            if timer.isRunning() and not timer.justplay and timer.Filename.find(filename) >= 0 and self.esok(timer):
                if timer.repeated:
                    return False
                timer.afterEvent = AFTEREVENT.NONE
                NavigationInstance.instance.RecordTimer.removeEntry(timer)

    def set_audio(self):
        from Screens.InfoBar import InfoBar
        if InfoBar and InfoBar.instance:
            InfoBar.audioSelection(InfoBar.instance)

    def set_scaling(self):
        if fileExists('/usr/lib/enigma2/python/Plugins/Extensions/ScalingModes/plugin.pyo'):
            try:
                from Plugins.Extensions.ScalingModes.plugin import main
                main(self.session)
                return
            except:
                pass

        try:
            from Screens.VideoMode import VideoSetup
            self.session.open(VideoSetup)
            return
        except:
            pass

        try:
            from Plugins.SystemPlugins.Videomode.plugin import videoSetupMain
            videoSetupMain(self.session)
            return
        except:
            pass

    def record_manager(self):
        try:
            from Screens.TimerEdit import TimerEditList
            self.session.open(TimerEditList)
        except:
            pass


gsession = None
rTimer = None
intentos = 0

def main(session, servicelist, **kwargs):
    global currservice
    global gsession
    global tmrecord
    if not fileExists('/usr/bin/chkvs'):
        Notifications.AddPopup(text=_('Not spazeTeam image found!\nMore info in www.azboxhd.es'), type=MessageBox.TYPE_ERROR, timeout=10, id='spzTimeshift')
        return
    gsession = session
    currservice = None
    recordings = len(session.nav.getRecordings())
    if recordings > 0:
        from Screens.InfoBar import InfoBar
        nombre = 'NA'
        dobletuner = False
        contaok = 0
        if SystemInfo.get('NumVideoDecoders', 1) > 1:
            for timer in NavigationInstance.instance.RecordTimer.timer_list:
                if timer.state == timer.StateRunning and not timer.disabled:
                    timerok = True
                    try:
                        if timer.Filename:
                            pass
                        else:
                            timerok = False
                    except:
                        timerok = False

                    if timerok:
                        contaok = contaok + 1
                    if timerok and str(timer.service_ref.getServiceName()) != str(ServiceReference(session.nav.getCurrentlyPlayingServiceOrGroup()).getServiceName()):
                        nombre = timer.name
                        if len(nombre) > 40:
                            nombre = nombre[:37] + '...'
                        nombre = nombre + '\n' + str(FuzzyTime(timer.begin)[1])
                        try:
                            nombre = nombre + ' - ' + str(FuzzyTime(timer.end)[1])
                        except:
                            pass

                        nombre = nombre + ' '
                        try:
                            duracion = str((timer.end - timer.begin) / 60) + ' ' + _('minutes')
                            nombre = nombre + ' \xe2\x80\xa2  ' + duracion
                        except:
                            pass

                        try:
                            nfaltan = (timer.end - time()) / 60
                            if nfaltan >= 1:
                                faltan = str(int(nfaltan)) + ' ' + _('minutes')
                            else:
                                faltan = str(int(nfaltan * 60)) + ' ' + _('seconds')
                            nombre = nombre + ' (+' + faltan + ')'
                        except:
                            pass

                        nombre = nombre + '\n' + _('Channel') + ': ' + timer.service_ref.getServiceName()
                        dobletuner = True

            if contaok > 1:
                eliminaDialogos(InfoBar.instance.session)
                try:
                    InfoBar.instance.session.openWithCallback(respuesta_sel, seleccionaGrabacion)
                except:
                    pass

                return
        if recordings > 1 or not dobletuner:
            tmrecord = None
            gsession.open(spzTimeshift, parar=False)
            return
        eliminaDialogos(InfoBar.instance.session)
        ermensaje = _('Record are running') + ':#$#' + nombre + '#$#' + _('As you want to use the timeshift function?')
        try:
            InfoBar.instance.session.openWithCallback(respuesta_dobletuner, Preguntar_timeshift, textos=ermensaje)
        except:
            pass

        return
    inicia_grabacion()


def respuesta_dobletuner(respuesta = None):
    global tmrecord
    if respuesta == None:
        return
    if respuesta == 1:
        tmrecord = None
        gsession.open(spzTimeshift, parar=False)
    elif respuesta == 0:
        inicia_grabacion()


def respuesta_sel(respuesta = None):
    if respuesta == None:
        return
    gsession.open(spzTimeshift, parar=False)


from Screens.InfoBar import InfoBar

def inicia_grabacion():
    global intentos
    global currservice
    global rTimer
    global tmrecord
    ernombre = ''
    intentos = 0
    if InfoBar and InfoBar.instance:
        tmrecord = None
        currservice = gsession.nav.getCurrentlyPlayingServiceOrGroup()
        InfoBar.instance.startInstantRecording(InfoBar.instance)
        eliminaDialogos(gsession)
        rTimer = eTimer()
        rTimer.callback.append(inicia)
        eliminaDialogos(gsession)
        mostrarNotificacion(id='timeshift', texto=_('Initiating timeshift. Wait') + '...', titulo=_('TimeShift'), segundos=7, mostrarSegundos=False, cerrable=False)
        rTimer.start(8200, True)


def inicia(parar = True):
    global intentos
    global rTimer
    global tmrecord
    if intentos == 0:
        pass
    tmrecord = None
    for timer in NavigationInstance.instance.RecordTimer.timer_list:
        if timer.state == timer.StateRunning and not timer.disabled:
            try:
                if timer.Filename:
                    pass
                if str(timer.service_ref.getServiceName()) == str(ServiceReference(currservice).getServiceName()):
                    timer.autoincrease = False
                    timer.end = int(time() + 9000.0)
                    InfoBar.instance.session.nav.RecordTimer.timeChanged(timer)
                    ernombre = '\n' + timer.name
                    tmrecord = timer
                    break
            except Exception as e:
                pass

    eliminaDialogos(gsession)
    eliminaDialogos(InfoBar.instance.session)
    if not tmrecord == None:
        try:
            gsession.open(spzTimeshift, parar)
            rTimer = None
            return
        except Exception as e:
            pass

    intentos = intentos + 1
    if intentos < 5:
        rTimer.start(1600, True)


def eliminaDialogos(lasession):
    from Tools.Notifications import AddNotificationWithID, RemovePopup
    try:
        RemovePopup('StartRecord')
    except:
        pass

    try:
        RemovePopup('timeshift')
    except:
        pass

    try:
        if 'MessageBox' in str(lasession.current_dialog):
            lasession.current_dialog.cancel()
    except:
        pass

    try:
        if 'scrInformation' in str(lasession.current_dialog) or 'MessageBox' in str(lasession.current_dialog):
            lasession.current_dialog.TimerChequea.stop()
            lasession.current_dialog.close()
    except:
        pass

    try:
        if 'scrInformation' in str(lasession.current_dialog):
            lasession.current_dialog.close()
    except:
        pass


def tmexit(respuesta = None):
    pass


from enigma import RT_HALIGN_LEFT, gFont
from Components.MultiContent import MultiContentEntryText
from Components.Sources.List import List

class Preguntar_timeshift(Screen):
    skin = '<screen name="Preguntar_timeshift" position="center,center" size="600,300" title="%s" zPosition="10" flags="wfBorder" backgroundColor="background">\n\t\t<ePixmap name="logo" position="0,2" size="48,48" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spzTimeshift/img/icog-fs8.png" zPosition="0" alphatest="blend" />\n\t\t<widget name="texto1" position="49,10" size="541,30" transparent="1" font="Regular; 22" foregroundColor="foreground" noWrap="1" valign="center" />\n\t\t<ePixmap name="icor" position="48,48" size="29,23" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spzTimeshift/img/rec-fs8.png" zPosition="5" alphatest="blend" />\t\n\t\t<widget name="textor" position="81,46" size="515,97" transparent="1" font="Regular; 20" foregroundColor="foreground" valign="top" />\n\t\t<eLabel name="linea" position="10,148" size="580,1" foregroundColor="foreground" zPosition="1" transparent="0" backgroundColor="foreground" />\n\t\t<ePixmap name="icoques" position="0,161" size="48,48" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spzTimeshift/img/msg-fs8.png" zPosition="5" alphatest="blend" />\n\t\t<widget name="textop" position="53,155" size="537,62" transparent="1" font="Regular; 22" foregroundColor="foreground" valign="center" />\n\t\t<eLabel name="linea2" position="10,225" size="580,1" foregroundColor="foreground" zPosition="1" transparent="0" backgroundColor="foreground" />\n\t\t<ePixmap name="icotim" position="14,240" size="25,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spzTimeshift/img/icot-fs8.png" zPosition="5" alphatest="blend" />\n\t\t<ePixmap name="icorec" position="14,265" size="25,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spzTimeshift/img/icor-fs8.png" zPosition="5" alphatest="blend" />\n\t\t<widget source="lista" render="Listbox" position="10,240" zPosition="1" size="580,50" transparent="1">\n\t\t\t  <convert type="TemplatedMultiContent">\n\t\t\t{"template": [\n\t\t\t\t\tMultiContentEntryText(pos = (34, -1), size = (580, 25), font=0, flags = RT_HALIGN_LEFT, text = 0), # index 0 is the name\n\t\t\t\t],\n\t\t\t"fonts": [gFont("Regular", 21),gFont("Regular", 18)],\n\t\t\t"itemHeight": 25\n\t\t\t}\n\t\t\t</convert>\n\t\t</widget>\n\t</screen> ' % _('Advanced TimeShift')

    def __init__(self, session, textos, tiempo = 30):
        Screen.__init__(self, session)
        self.session = session
        self['actions'] = ActionMap(['ShortcutActions', 'WizardActions', 'MediaPlayerActions'], {'ok': self.keyOK,
         'back': self.keyCancel,
         'up': self.keyUp,
         'down': self.keyDown,
         'left': self.keyUp,
         'right': self.keyDown}, -1)
        listatextos = textos.split('#$#')
        self['texto1'] = Label(listatextos[0])
        self['textor'] = Label(listatextos[1])
        self['textop'] = Label(listatextos[2])
        self.listopt = []
        canal = ''
        try:
            canal = ' - ' + ServiceReference(self.session.nav.getCurrentlyPlayingServiceOrGroup()).getServiceName() + ''
        except:
            pass

        self.listopt.append((_('Start timeshift with current channel') + ' ' + canal + '',))
        self.listopt.append((_('Use timeshift with this active record'),))
        self['lista'] = List(self.listopt)
        self.TimerAuto = eTimer()
        self.TimerAuto.callback.append(self.actualiza)
        if tiempo == 0:
            self.tiempo = -2
        else:
            self.tiempo = tiempo
        self.onLayoutFinish.append(self.actualiza)

    def actualiza(self):
        titulo = _('Advanced TimeShift')
        if self.tiempo == -1:
            self.keyOK()
        elif self.tiempo >= 0:
            mensajesec = '(' + str(self.tiempo) + ')'
            self.setTitle(mensajesec + ' ' + titulo)
            self.TimerAuto.startLongTimer(1)
            self.tiempo = self.tiempo - 1
        else:
            self.setTitle(titulo)

    def Exit(self, valor = None):
        self.TimerAuto.stop()
        self.close(valor)

    def keyCancel(self):
        self.Exit()

    def keyOK(self):
        indice = self['lista'].getIndex()
        self.Exit(indice)

    def keyUp(self):
        self.tiempo = -2
        indice = self['lista'].getIndex()
        if indice == 0:
            self['lista'].setIndex(self['lista'].count() - 1)
        else:
            self['lista'].selectPrevious()

    def keyDown(self):
        self.tiempo = -2
        indice = self['lista'].getIndex()
        if indice == self['lista'].count() - 1:
            self['lista'].setIndex(0)
        else:
            self['lista'].selectNext()


class seleccionaGrabacion(Screen):
    skin = '<screen name="seleccionaGrabacion" position="center,center" size="800,300" title="%s" zPosition="10" flags="wfBorder" backgroundColor="background" transparent="0">\n\t\t\t<ePixmap name="logo" position="0,2" size="48,48" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spzTimeshift/img/icog-fs8.png" zPosition="0" alphatest="blend" />\n\t\t\t<widget name="texto1" position="49,10" size="743,64" transparent="1" font="Regular; 21" foregroundColor="foreground" valign="top" />\n\t\t\t<ePixmap name="icor" position="9,104" size="30,21" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spzTimeshift/img/rec-fs8.png" zPosition="5" alphatest="blend" />\t\n\t\t\t<eLabel name="linea" position="10,88" size="780,1" foregroundColor="foreground" zPosition="1" transparent="0" backgroundColor="foreground" font="Regular; 22" />\n\t\t\t<widget name="textop" position="44,100" size="760,28" transparent="1" font="Regular; 22" foregroundColor="foreground" valign="center" noWrap="1" />\n\t\t\t<widget source="lista" render="Listbox" position="10,144" zPosition="1" size="780,150" transparent="1">\n\t\t\t\t  <convert type="TemplatedMultiContent">\n\t\t\t\t{"template": [\n\t\t\t\t\t\tMultiContentEntryText(pos = (4, 0), size = (780, 25), font=0, flags = RT_HALIGN_LEFT, text = 0), # index 0 is the name\n\t\t\t\t\t],\n\t\t\t\t"fonts": [gFont("Regular", 20),gFont("Regular", 18)],\n\t\t\t\t"itemHeight": 25\n\t\t\t\t}\n\t\t\t\t</convert>\n\t\t\t</widget>\n\t\t</screen>' % _('Advanced TimeShift')

    def __init__(self, session, tiempo = 60):
        Screen.__init__(self, session)
        self.session = session
        self['actions'] = ActionMap(['ShortcutActions', 'WizardActions', 'MediaPlayerActions'], {'ok': self.keyOK,
         'back': self.keyCancel,
         'up': self.keyUp,
         'down': self.keyDown,
         'left': self.keyUp,
         'right': self.keyDown}, -1)
        self['texto1'] = Label(_('Several recordings are in progress, and you must select one to use the timeshift.'))
        self['textop'] = Label(_('Select Record to play') + ':')
        self.listopt = []
        self.listarec = []
        conta = 0
        self.indice = 0
        for timer in NavigationInstance.instance.RecordTimer.timer_list:
            if timer.state == timer.StateRunning and not timer.disabled:
                timerok = True
                try:
                    if timer.Filename:
                        pass
                    else:
                        timerok = False
                except:
                    timerok = False

                if timerok:
                    if str(timer.service_ref.getServiceName()) == str(ServiceReference(session.nav.getCurrentlyPlayingServiceOrGroup()).getServiceName()):
                        self.indice = conta
                    nombre = '  \xe2\x80\xa2 ' + timer.service_ref.getServiceName()
                    if len(nombre) > 20:
                        nombre = nombre[:18] + '...'
                    nombre = nombre + ' \xe2\x80\xa2 ' + str(FuzzyTime(timer.begin)[1])
                    try:
                        nombre = nombre + ' - ' + str(FuzzyTime(timer.end)[1])
                    except:
                        pass

                    nombre = nombre + ''
                    try:
                        nfaltan = (timer.end - time()) / 60
                        if nfaltan >= 1:
                            faltan = str(int(nfaltan)) + ' ' + _('min.')
                        else:
                            faltan = str(int(nfaltan * 60)) + ' ' + _('sec.')
                        nombre = nombre + ' (+' + faltan + ')'
                    except:
                        pass

                    nombre = nombre + '  ' + timer.name
                    self.listarec.append(timer)
                    self.listopt.append((nombre,))
                    conta = conta + 1

        self['lista'] = List(self.listopt)
        self.TimerAuto = eTimer()
        self.TimerAuto.callback.append(self.actualiza)
        if tiempo == 0:
            self.tiempo = -2
        else:
            self.tiempo = tiempo
        self.onLayoutFinish.append(self.actualiza)

    def actualiza(self):
        if self.indice > 0:
            self['lista'].setIndex(self.indice)
            self.indice = 0
        titulo = _('Advanced TimeShift')
        if self.tiempo == -1:
            self.keyOK()
        elif self.tiempo >= 0:
            mensajesec = '(' + str(self.tiempo) + ')'
            self.setTitle(mensajesec + ' ' + titulo)
            self.TimerAuto.startLongTimer(1)
            self.tiempo = self.tiempo - 1
        else:
            self.setTitle(titulo)

    def Exit(self, valor = None):
        self.TimerAuto.stop()
        self.close(valor)

    def keyCancel(self):
        self.Exit()

    def keyOK(self):
        global tmrecord
        if self['lista'].count() <= 0:
            self.keyCancel()
        indice = self['lista'].getIndex()
        tmrecord = self.listarec[indice]
        self.Exit(indice)

    def keyUp(self):
        if self['lista'].count() <= 0:
            return
        self.tiempo = -2
        indice = self['lista'].getIndex()
        if indice == 0:
            self['lista'].setIndex(self['lista'].count() - 1)
        else:
            self['lista'].selectPrevious()

    def keyDown(self):
        if self['lista'].count() <= 0:
            return
        self.tiempo = -2
        indice = self['lista'].getIndex()
        if indice == self['lista'].count() - 1:
            self['lista'].setIndex(0)
        else:
            self['lista'].selectNext()


def Plugins(**kwargs):
    return PluginDescriptor(name=_('Advanced TimeShift'), description=_('Create a recordable timeshift'), where=PluginDescriptor.WHERE_EXTENSIONSMENU, fnc=main)
