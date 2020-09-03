from Screens.PictureInPicture import PictureInPicture
from Components.ActionMap import HelpableActionMap, ActionMap
from Screens.HelpMenu import HelpableScreen
from enigma import iServiceInformation
from Components.Label import Label
from Screens.ChannelSelection import ChannelSelection, ChannelSelectionBase, ChannelSelectionEdit, ChannelSelectionEPG, SelectionEventInfo, BouquetSelector
OFF = 0
EDIT_BOUQUET = 1
EDIT_ALTERNATIVES = 2
from Components.SystemInfo import SystemInfo
from enigma import eServiceCenter, gFont, eServiceReference, getBestPlayableServiceReference, getPrevAsciiCode
from enigma import eTimer
from enigma import eSize, ePoint
from ServiceReference import ServiceReference
from Components.Pixmap import Pixmap, MovingPixmap
from Tools.LoadPixmap import LoadPixmap
from Screens import Standby
from Screens.ChoiceBox import ChoiceBox
from RecordTimer import RecordTimerEntry, parseEvent, AFTEREVENT
from Components.UsageConfig import preferredTimerPath
from Screens.TimerEntry import TimerEntry
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.Button import Button
from Components.config import ConfigYesNo, ConfigText, ConfigSelection, config, ConfigSubsection, ConfigSelectionNumber
from Plugins.Extensions.spazeMenu.spzPlugins.openSPATVGuide.EPGSimple import spaEPGList, SpaViewSimple
from Tools import Notifications
from Plugins.Extensions.spazeMenu.sbar import openspaSB
from time import localtime, time, strftime
from Tools.Directories import fileExists, resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE, SCOPE_SKIN, SCOPE_CURRENT_SKIN, SCOPE_SKIN_IMAGE
from Components.Language import language
from os import environ
from Plugins.Extensions.spazeMenu.plugin import fhd
from Plugins.Extensions.spazeMenu.spzVirtualKeyboard import spzVirtualKeyboard
import gettext
lang = language.getLanguage()
environ['LANGUAGE'] = lang[:2]
gettext.bindtextdomain('enigma2', resolveFilename(SCOPE_LANGUAGE))
gettext.textdomain('enigma2')
gettext.bindtextdomain('newChannelSelection', '%s%s' % (resolveFilename(SCOPE_PLUGINS), 'Extensions/spazeMenu/spzPlugins/newChannelSelection/locale/'))

def _(txt):
    t = gettext.dgettext('newChannelSelection', txt)
    if t == txt:
        t = gettext.gettext(txt)
    return t


config.tv = ConfigSubsection()
config.tv.lastservice = ConfigText()
config.tv.lastroot = ConfigText()
config.tvspaze = ConfigSubsection()
config.tvspaze.spazeChannelMode = ConfigSelection(default='0', choices=[('0', _('Translucent Mode')), ('1', _('PIP Mode'))])
config.tvspaze.showtpinfo = ConfigYesNo(default=True)
config.tvspaze.maxdaysEPG = ConfigSelectionNumber(min=1, max=7, stepwidth=1, default=1, wraparound=True)
config.radio = ConfigSubsection()
config.radio.lastservice = ConfigText()
config.radio.lastroot = ConfigText()
config.servicelist = ConfigSubsection()
config.servicelist.lastmode = ConfigText(default='tv')
config.servicelist.startupservice = ConfigText()
config.servicelist.startupservice_onstandby = ConfigYesNo(default=False)
config.servicelist.startuproot = ConfigText()
config.servicelist.startupmode = ConfigText(default='tv')
TYPE_VALUE_DEC = 2
TYPE_VALUE_ORBIT_DEC = 5
from Components.Sources.ServiceEvent import ServiceEvent

class ServiceEvent2(ServiceEvent):

    def __init__(self):
        ServiceEvent.__init__(self)
        self.evento = 1

    def getCurrentEvent(self):
        if self.evento != 1:
            return self.evento
        else:
            return self.service and self.info and self.info.getEvent(self.service)

    event = property(getCurrentEvent)

    def EnewService(self, ref, evt = 1):
        if evt != 1:
            if not self.evento or not evt or self.evento != evt:
                self.service = ref
                self.evento = evt
                if not evt:
                    self.changed((self.CHANGED_CLEAR,))
                else:
                    self.changed((self.CHANGED_ALL,))
        else:
            self.evento = 1
            if not self.service or not ref or self.service != ref:
                self.service = ref
                if not ref:
                    self.changed((self.CHANGED_CLEAR,))
                else:
                    self.changed((self.CHANGED_ALL,))


def ajustafr(frecu):
    return int(round(float(frecu) / 1000000, 0)) * 1000


def devchfr(frecu):
    ret = 'NA'
    arrfecs = [(21, 474),
     (22, 482),
     (23, 490),
     (24, 498),
     (25, 506),
     (26, 514),
     (27, 522),
     (28, 530),
     (29, 538),
     (30, 546),
     (31, 554),
     (32, 562),
     (33, 570),
     (34, 578),
     (35, 586),
     (36, 594),
     (37, 602),
     (38, 610),
     (39, 618),
     (40, 626),
     (41, 634),
     (42, 642),
     (43, 650),
     (44, 658),
     (45, 666),
     (46, 674),
     (47, 682),
     (48, 690),
     (49, 698),
     (50, 706),
     (51, 714),
     (52, 722),
     (53, 730),
     (54, 738),
     (55, 746),
     (56, 754),
     (57, 762),
     (58, 770),
     (59, 778),
     (60, 786),
     (61, 794),
     (62, 802),
     (63, 810),
     (64, 818),
     (65, 826),
     (66, 834),
     (67, 842),
     (68, 850),
     (69, 858)]
    nfrecu = ajustafr(frecu) / 1000
    for ele in arrfecs:
        if ele[1] == nfrecu:
            ret = ele[0]
            return ret

    return ret


def infocanalnc(servicio):
    texto = '\xe2\x80\xa2'
    ref = ''
    laref = ''
    try:
        ref = servicio.toString() + ''
        laref = servicio.toString() + ''
        ref = ref[4:-11]
    except:
        pass

    if len(ref) <= len(':0:0:0:0:0'):
        return ' '
    if laref.startswith('4097:0:0:'):
        ref = laref
        textoret = '\xe2\x80\xa2 IPTV - '
        try:
            textoret = textoret + ref.replace('4097:0:0:0:0:0:0:0:0:0:', '').split(':')[0].replace('%3a', ':')
        except:
            textoret = textoret + ref.replace('4097:0:0:0:0:0:0:0:0:0:', '')

        textoret = textoret + ' \xe2\x80\xa2'
        return textoret
    from Tools.Transponder import ConvertToHumanReadable
    try:
        info = eServiceCenter.getInstance().info(servicio)
        transponder_info = info.getInfoObject(servicio, iServiceInformation.sTransponderData)
        tp_info = ConvertToHumanReadable(transponder_info)
    except:
        return ref

    conv = {'system': '1-> ' + _('System'),
     'orbital_position': '2-> ' + _('Orbital Position'),
     'frequency': '3-> ' + _('Frequency'),
     'symbol_rate': '4-> ' + _('Symbolrate'),
     'fec_inner': '5-> ' + _('FEC'),
     'bandwidth': '7-> ' + _('Bandwidth'),
     'polarization': '6-> ' + _('Polarization')}
    Labels = [ (conv[i], tp_info[i], i == 'orbital_position' and TYPE_VALUE_ORBIT_DEC or TYPE_VALUE_DEC) for i in tp_info.keys() if i in conv ]
    try:
        Labels.sort(key=lambda x: x[0])
    except:
        pass

    esdvt = False
    espacio = ' '
    for item in Labels:
        if item[1] is None:
            continue
        value = item[1]
        nombre = item[0]
        try:
            nombre = item[0].split('-> ')[1]
        except:
            pass

        if nombre == _('Orbital Position'):
            value = str(value)
            if len(value) > 25:
                value = value[:23] + '...'
        if nombre == _('System') and item[1] == 'DVB-T':
            esdvt = True
        if nombre == _('Frequency') or nombre == _('Symbolrate'):
            value = str(value)[:-3]
        elif nombre == _('Polarization'):
            value = str(value)[0]
        try:
            if esdvt and nombre == _('Frequency'):
                value = str(ajustafr(int(item[1]))) + ' Khz (Mux ' + str(devchfr(int(item[1]))) + ')'
            elif nombre == _('Frequency'):
                value = str(value) + ' Mhz'
        except:
            pass

        texto = texto + espacio + str(value)
        if nombre == _('Frequency') or nombre == _('Symbolrate'):
            espacio = ' '
        else:
            espacio = '  '

    texto = texto + '  ' + ref + ' \xe2\x80\xa2'
    return texto


import threading

class segundoplano(threading.Thread):

    def __init__(self, parametro, max):
        threading.Thread.__init__(self)
        self.parametro = parametro
        self.max = max

    def run(self):
        self.parametro.actualizaepg(self.max)


def formateafecha(lafecha = None, sepa = '-'):
    if not lafecha == None:
        t2 = lafecha
    else:
        t2 = localtime()
    cdia = str(strftime('%d', t2))
    cmes = str(strftime('%B', t2))
    cano = str(strftime('%Y', t2))
    csemana = str(strftime('%A', t2))
    return _(csemana) + ', ' + cdia + sepa + _(cmes) + sepa + cano


def formateafechacorta(lafecha = None, sepa = '-'):
    if not lafecha == None:
        t2 = lafecha
    else:
        t2 = localtime()
    cdia = str(strftime('%d', t2))
    cmes = str(strftime('%B', t2))
    csemana = str(strftime('%A', t2))
    return _(csemana).replace('\xc3\xa1', 'a').replace('\xc3\xa9', 'e').replace('\xc3\xad', 'i').replace('\xc3\xb3', 'o').replace('\xc3\xba', 'u')[0:3] + '., ' + cdia + sepa + _(cmes)[0:3] + '.'


def rutapicon(serviceName):
    from Components.Renderer import Picon
    tmp = Picon.getPiconName(serviceName)
    if fileExists(tmp):
        return tmp
    tmp = resolveFilename(SCOPE_CURRENT_SKIN, 'picon_default.png')
    if fileExists(tmp):
        return tmp
    tmp = resolveFilename(SCOPE_SKIN_IMAGE, 'skin_default/picon_default.png')
    if fileExists(tmp):
        return resolveFilename(SCOPE_SKIN_IMAGE, 'skin_default/picon_default.png')
    else:
        return ''


def nombrepix(cualo):
    rutapix = None
    rutapix = '/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/newChannelSelection/spzTeam/' + cualo + '.png'
    if not fileExists(rutapix):
        rutapix = None
    return rutapix


MODE_TV = 0
MODE_RADIO = 1
BouquetSelectorScreen = None
cbGuia = None

def isInTimerSPA(listatimer, eventid, begin, duration, service):
    vret = None
    bend = begin + duration
    for x in listatimer.timer_list:
        check = x.service_ref.ref
        reftimer = check.toString()
        try:
            cret = check
            if cret.flags & eServiceReference.isGroup:
                xref = getBestPlayableServiceReference(cret, eServiceReference(), True)
                reftimer = xref.toString()
        except:
            pass

        if str(reftimer) == str(service):
            if x.eit == eventid:
                return x
            beg = x.begin
            try:
                end = x.end
                if begin >= beg and bend <= end:
                    return x
            except:
                pass

    return vret


def muestraguia():
    global cbGuia
    from Screens.InfoBar import InfoBar
    if InfoBar and InfoBar.instance:
        if fileExists('/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/openSPATVGuide/plugin.pyo'):
            try:
                from Plugins.Extensions.spazeMenu.spzPlugins.openSPATVGuide.plugin import main
                main(InfoBar.instance.session, InfoBar.instance.servicelist)
            except:
                pass

        else:
            try:
                from Plugins.Extensions.CoolTVGuide.plugin import main
                main(InfoBar.instance.session, InfoBar.instance.servicelist)
            except:
                pass

    cbGuia.callback.remove(muestraguia)
    cbGuia = None


class newChannelSelection(HelpableScreen, ChannelSelection, ChannelSelectionBase, ChannelSelectionEdit, ChannelSelectionEPG, SelectionEventInfo):

    def __init__(self, session):
        ChannelSelection.__init__(self, session)
        HelpableScreen.__init__(self)
        if config.tvspaze.spazeChannelMode.value == '0':
            from Plugins.Extensions.spazeMenu.spzPlugins.newChannelSelection.skinsch import newChannelSelectionNOPIPskin
            self.skin = newChannelSelectionNOPIPskin
            self.skinName = 'newChannelSelectionNOPIP'
        else:
            from Plugins.Extensions.spazeMenu.spzPlugins.newChannelSelection.skinsch import newChannelSelectionskin
            self.skin = newChannelSelectionskin
            self.skinName = 'newChannelSelection'
        self.lascreen = Screen
        self.bsel = None
        self.pipAvailable = False
        self['ServiceEvent'] = ServiceEvent2()
        self['servicelist_arr'] = Pixmap()
        self['servicelist_abj'] = Pixmap()
        self['eventos_arr'] = Pixmap()
        self['eventos_abj'] = Pixmap()
        self['list2'] = spaEPGList(selChangedCB=self.selcblista2, timer=session.nav.RecordTimer, sigenero=False)
        self['list2'].l.setItemHeight(30)
        self['list2'].l.setFont(0, gFont('Regular', 19))
        self['list2'].l.setFont(1, gFont('Regular', 19))
        self['list2'].l.setFont(2, gFont('Regular', 21))
        self['flecha_arr'] = MovingPixmap()
        self['flecha_abj'] = MovingPixmap()
        self['flecha_medio'] = Pixmap()
        self['img_picon'] = Pixmap()
        self['key_menu'] = Button(_('Options'))
        self['key_info'] = Button(_('Event Info'))
        self['linea_arr'] = Button(' ')
        self['linea_abj'] = Button(' ')
        self['key_chmenos'] = Button(_('Events'))
        self['key_chmas'] = Button(_('Zap'))
        self['icanal'] = Label(' ')
        self['ititulo'] = Label(' ')
        self['infodch'] = Label(' ')
        self.seg_plano = None
        self['hactions2'] = HelpableActionMap(self, 'ColorActions', {'red': (self.inetinfo, _('Internet database search')),
         'green': (self.timerAdd, _('Add record timer')),
         'yellow': (self.eshowSatellites, _('Show Satellites list') + ' / ' + _('Search in EPG')),
         'blue': (self.eshowFavourites, _('Show Favorites list'))})
        self['hactions3'] = HelpableActionMap(self, 'OkCancelActions', {'cancel': (self.ecancel, _('Exit channel list')),
         'ok': (self.keyok, _('Zap and Exit channel list'))})
        self['hactions8'] = HelpableActionMap(self, 'DirectionActions', {'right': (self.key_pageDown, _('Page Down in list')),
         'left': (self.key_pageUp, _('Page Up in list'))})
        self['hactions4'] = HelpableActionMap(self, 'EPGSelectActions', {'nextBouquet': (self.cambialista, _('Switch to channel list/event list')),
         'prevBouquet': (self.cambialista, _('Switch to channel list/event list')),
         'nextService': (self.nextMarker, _('Goto next marker in boutquet list')),
         'prevService': (self.prevMarker, _('Goto previous marker in boutquet list')),
         'menu': (self.prevMarker, _('Show menu with more options')),
         'info': (self.prevMarker, _('Show event view screen information'))})
        self['hactions6'] = HelpableActionMap(self, 'MediaPlayerActions', {'play': (self.zapea, _('Quick Zap/Search in epg list')),
         'pause': (self.zapea, _('Quick Zap/Search in epg list')),
         'stop': (self.muestraMosaico, _('Channels Mosaic'))})
        self['hactions7'] = HelpableActionMap(self, 'NumberActions', {'0': (self.key0, _('Show selected channel in PiP window')),
         '1': (self.key1, _('Show Goto menu for quick search')),
         '2': (self.key2, _('Show transponder/channel information')),
         '3': (self.key3, _('Show event list for selected channel')),
         '4': (self.key4, _('Show advanced EPG Guide')),
         '7': (self.key7, _('Channels Mosaic')),
         '8': (self.key8, _('Show alternative channels')),
         '9': (self.key9, _('More options (system default menu)'))})
        self['hactions1'] = HelpableActionMap(self, 'TvRadioActions', {'keyRadio': (self.setModeRadio, _('Show the radio player...')),
         'keyTV': (self.setModeTv, _('Show the tv player...'))})
        self['hactions5'] = HelpableActionMap(self, 'GlobalActions', {'power_down': (self.apagar, _('Go to standby mode and exit channel list'))})
        self['actions'] = ActionMap(['OkCancelActions', 'TvRadioActions'], {'cancel': self.ecancel,
         'ok': self.keyok,
         'keyRadio': self.setModeRadio,
         'keyTV': self.setModeTv})
        self['ChannelSelectBaseActions'] = ActionMap(['ListboxActions',
         'InfobarChannelSelection',
         'OkCancelActions',
         'WizardActions',
         'DirectionActions',
         'ColorActions',
         'MenuActions',
         'InfobarActions',
         'ChannelSelectEPGActions',
         'ChannelSelectBaseActions',
         'MoviePlayerActions',
         'MediaPlayerActions',
         'InfobarTimeshiftActions',
         'InfobarEPGActions',
         'EPGSelectActions',
         'NumberActions',
         'InputAsciiActions',
         'GlobalActions',
         'InfobarSeekActions'], {'cancel': self.ecancel,
         'power_down': self.apagar,
         'power_up': self.apagar,
         'exit': self.ecancel,
         'ok': self.keyok,
         'red': self.inetinfo,
         'green': self.timerAdd,
         'nextBouquet': self.cambialista,
         'prevBouquet': self.cambialista,
         'blue': self.eshowFavourites,
         'yellow': self.eshowSatellites,
         'gotAsciiCode': self.keyAsciiCode,
         'up': self.key_Up,
         'down': self.key_Down,
         'left': self.key_pageUp,
         'right': self.key_pageDown,
         'switchChannelUp': self.key_Up,
         'switchChannelDown': self.key_Down,
         'zapDown': self.key_pageDown,
         'zapUp': self.key_pageUp,
         'moveUp': self.key_Up,
         'moveDown': self.key_Down,
         'pageUp': self.key_pageUp,
         'pageDown': self.key_pageDown,
         'info': self.key_info,
         'menu': self.key_menu,
         'showEPGList': self.key_info,
         'showEventInfo': self.key_info,
         'showEventInfoPlugin': self.key_info,
         'showGraphEPG': self.key_info,
         'nextMarker': self.nextMarker,
         'prevMarker': self.prevMarker,
         '1': self.key1,
         '8': self.key8,
         '9': self.key9,
         '0': self.key0,
         'play': self.zapea,
         'pause': self.zapea,
         'stop': self.muestraMosaico}, -2)
        self.cbTimer = eTimer()
        self.cbTimer.callback.append(self.actualizaLista2)
        self.timerEpg = eTimer()
        self.timerEpg.callback.append(self.ttimer)
        self.tempTimer = eTimer()
        self.tempTimer.callback.append(self.ecancel)
        self.activo = 'list2'
        self.objcal = None
        self.tamtit = 0
        self.onShow.append(self.cbEV)
        self.onLayoutFinish.append(self.alcrear)
        self.utextobuscar = ''
        self.seg_plano_exit = False
        self.lastalter = None
        self.lastalterroot = None

    def selcblista2(self):
        if self.activo == 'list2':
            cur = self['list2'].getCurrent()
            event = cur[0]
            curs = self.getCurrentSelection()
            self['ServiceEvent'].EnewService(curs, event)

    def prevPressed(self):
        if self['list2'].orden != 0:
            return
        try:
            lalista = self['list2'].list
            length = len(lalista)
            if length > 1:
                idx = self['list2'].instance.getCurrentIndex()
                conta = idx - 2
                for ele in range(0, idx):
                    if conta < 0:
                        break
                    if lalista[conta][0] == None:
                        self['list2'].instance.moveSelectionTo(conta)
                        break
                    conta = conta - 1

                if idx == self['list2'].instance.getCurrentIndex():
                    self['list2'].instance.moveSelectionTo(length - 1)
                    conta = length - 1
                    for ele in range(0, length - 1):
                        if conta < 0:
                            break
                        if lalista[conta][0] == None:
                            self['list2'].instance.moveSelectionTo(conta)
                            break
                        conta = conta - 1

        except:
            pass

    def nextPressed(self):
        if self['list2'].orden != 0:
            return
        try:
            lalista = self['list2'].list
            length = len(lalista)
            if length > 1:
                idx = self['list2'].instance.getCurrentIndex()
                for ele in range(idx + 1, length):
                    if lalista[ele][0] == None:
                        self['list2'].instance.moveSelectionTo(ele)
                        break

                if idx == self['list2'].instance.getCurrentIndex():
                    self['list2'].instance.moveSelectionTo(0)
        except:
            pass

    def nada(self):
        pass

    def guia(self):
        global cbGuia
        if fileExists('/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/openSPATVGuide/plugin.pyo') or fileExists('/usr/lib/enigma2/python/Plugins/Extensions/CoolTVGuide/plugin.pyo'):
            cbGuia = eTimer()
            cbGuia.callback.append(muestraguia)
            cbGuia.start(200, True)
            self.ecancel()

    def apagar(self):
        Notifications.AddNotification(Standby.Standby)
        self.ecancel()

    def keyNumberGlobal(self, number = ''):
        if str(number) == '0':
            self.key0()
        elif str(number) == '1':
            self.key1()
        elif str(number) == '8':
            self.key8()
        elif str(number) == '9':
            self.key9()

    def zapea(self):
        if self.activo == 'list':
            if self.canalvalido():
                self.zap(enable_pipzap=True, preview_zap=True)
        else:
            self.texto_buscaepg()

    def key4(self):
        self.guia()

    def showEPGListSPA(self):
        if fileExists('/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/openSPATVGuide/plugin.pyo'):
            if self.activo == 'list':
                event = self['ServiceEvent'].getCurrentEvent()
                service = self['ServiceEvent'].getCurrentService()
            else:
                service = self['ServiceEvent'].getCurrentService()
                cur = self['list2'].getCurrent()
                event = cur[0]
            if event is None:
                return
            try:
                from Plugins.Extensions.spazeMenu.spzPlugins.openSPATVGuide.EPGSimple import spaEPGSelection
                self.session.open(spaEPGSelection, service)
                return
            except:
                pass

        self.showEPGList()

    def key3(self):
        self.prevBouquet()
        self.showEPGListSPA()

    def key7(self):
        self.muestraMosaico()

    def key2(self):
        self.tpinfocanal()

    def keyAsciiCode(self, number = ''):
        unichar = unichr(getPrevAsciiCode())
        charstr = unichar.encode('utf-8')
        if len(charstr) == 1:
            number = charstr
        if str(number) == '0':
            self.key0()
        elif str(number) == '1':
            self.key1()
        elif str(number) == '2':
            self.key2()
        elif str(number) == '4':
            self.key4()
        elif str(number) == '3':
            self.key3()
        elif str(number) == '7':
            self.key7()
        elif str(number) == '8':
            self.key8()
        elif str(number) == '9':
            self.key9()

    def actualizaScrolls(self, nocargar = None):
        openspaSB(objectoself=self, nombrelista='list2', barra='eventos', altoitem=30)

    def ecancel(self):
        self.prevBouquet()
        self.lastalter = None
        self.lastalterroot = None
        self.desactivaedicion()
        self.cancel()

    def keyok(self):
        if self.activo == 'list2':
            self.key_info()
            return
        self.prevBouquet()
        root = self.getRoot()
        if root.flags & eServiceReference.isGroup:
            if self.bouquet_mark_edit == OFF and not self.movemode:
                self.zap(preview_zap=True)
                if self.lastalterroot:
                    self.enterPath(self.lastalterroot)
                    if self.lastalter:
                        self.setCurrentSelection(self.lastalter)
                self.ecancel()
                return
        self.channelSelected()

    def desactivaedicion(self):
        try:
            if self.movemode:
                self.toggleMoveMode()
                self.actualizaepgtmp()
            elif self.bouquet_mark_edit != OFF:
                self.endMarkedEdit(abort=False)
        except:
            pass

    def nextMarker(self):
        if self.activo == 'list':
            self.prevBouquet()
            self.servicelist.moveToNextMarker()
        else:
            self.nextPressed()

    def prevMarker(self):
        if self.activo == 'list':
            self.prevBouquet()
            self.servicelist.moveToPrevMarker()
        else:
            self.prevPressed()

    def enextMarker(self):
        self.prevBouquet()
        self['key_red'].setText('next')
        self.nextMarker()

    def eprevMarker(self):
        self.prevBouquet()
        self.prevMarker()

    def ekeyAsciiCode(self):
        self.prevBouquet()
        self.keyAsciiCode()

    def ekeyNumberGlobal(self):
        pass

    def ekeyNumber0(self, num = 0):
        self.prevBouquet()
        if len(self.servicePath) > 1:
            self.keyGoUp()
        else:
            self.keyNumberGlobal(num)

    def inetinfo(self):
        titulo = None
        if self.activo == 'list':
            if self.canalvalido():
                event = self['ServiceEvent'].getCurrentEvent()
                titulo = _('Title')
                try:
                    titulo = event.getEventName()
                except:
                    pass

        else:
            cur = self['list2'].getCurrent()
            event = cur[0]
            if not event:
                return
            titulo = event.getEventName()
        if titulo:
            try:
                from Plugins.Extensions.spzIMDB.plugin import spzIMDB
                spzIMDB(self.session, tbusqueda=titulo)
                return
            except:
                pass

    def key_menu(self):
        if self.siedicion():
            self.prevBouquet()
            self.doContext()
            return
        nkeys = ['red', 'green']
        askList = []
        askList.append((_('Show') + ' [' + _('All') + ']', '1'))
        askList.append((_('Show') + ' [' + _('Providers') + ']', '3'))
        askList.append(('--', 'nada'))
        nkeys.append('')
        nombrecanal = ''
        cvalido = self.canalvalido()
        if cvalido:
            try:
                service = ServiceReference(self['ServiceEvent'].getCurrentService())
                ref = self.getCurrentSelection()
                info = service and service.info()
                name = ref and info.getName(ref)
                if name is None:
                    name = info.getName()
                name = name.replace('\xc2\x86', '').replace('\xc2\x87', '')
                nombrecanal = ' (' + name + ')'
            except:
                try:
                    servicio = self.servicelist.getCurrent()
                    name = ServiceReference(servicio).getServiceName().replace('\xc2\x86', '').replace('\xc2\x87', '')
                    nombrecanal = ' (' + name + ')'
                except:
                    pass

            if nombrecanal == '':
                cvalido = False
        if cvalido:
            try:
                self.pipAvailable = False
                if SystemInfo.get('NumVideoDecoders', 1) > 1:
                    if not self.dopipzap:
                        askList.append((_('play as picture in picture') + nombrecanal, 'pip'))
                        self.pipAvailable = True
                    else:
                        askList.append((_('play in mainwindow') + nombrecanal, 'main'))
                    nkeys.append('0')
            except:
                pass

        askList.append((_('Go to') + '...' + '', 'goto'))
        nkeys.append('1')
        if cvalido:
            askList.append((_('Transponder Information') + nombrecanal, 'info'))
            nkeys.append('2')
            askList.append((_('Single EPG for') + nombrecanal, '5'))
            nkeys.append('3')
        if fileExists('/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/openSPATVGuide/plugin.pyo') or fileExists('/usr/lib/enigma2/python/Plugins/Extensions/CoolTVGuide/plugin.pyo'):
            askList.append((_('EPG Guide'), 'guia'))
            nkeys.append('4')
        askList.append(('--', 'nada'))
        nkeys.append('')
        askList.append((_('Remote control Help'), 'help'))
        nkeys.append('-')
        askList.append((_('Channel selection options'), 'options'))
        nkeys.append('-')
        askList.append((_('Standard Channel Selection'), '6'))
        nkeys.append('-')
        if cvalido:
            askList.append((_('remove entry') + '', 'remove'))
            nkeys.append('-')
            askList.append((_('add service to') + '...', 'add'))
            nkeys.append('-')
            try:
                if self.bouquet_mark_edit == OFF and self.getMutableList() is not None:
                    if not self.movemode:
                        askList.append((_('enable move mode') + '', 'move'))
                        nkeys.append('-')
            except:
                pass

        askList.append(('--', 'nada'))
        nkeys.append('')
        askList.append((_('Channels Mosaic') + '[STOP]', '88'))
        nkeys.append('7')
        if cvalido:
            try:
                ref = self.getCurrentSelection()
                if ref.flags & eServiceReference.isGroup:
                    askList.append((_('Show alternative channels'), 'alter'))
                    nkeys.append('8')
            except:
                pass

        askList.append((_('More options') + '...', '9'))
        nkeys.append('9')
        dei = self.session.openWithCallback(self.callbackmenu, ChoiceBox, keys=nkeys, title=_('Select option') + ':', list=askList)
        dei.setTitle(_('Options') + ' ' + _('Channel Selection'))

    def configurach(self):
        nkeys = []
        askList = []
        if config.tvspaze.showtpinfo.value:
            askList.append((_('Hide channel/transponder info in title'), 'tpinfo'))
        else:
            askList.append((_('Show channel/transponder info in title'), 'tpinfo'))
        nkeys.append('red')
        if config.tvspaze.spazeChannelMode.value == '1':
            askList.append((_('Switch to') + ' ' + _('Translucent Mode') + '', '10'))
        else:
            askList.append((_('Switch to') + ' ' + _('PIP Mode') + '', '11'))
        nkeys.append('green')
        dei = self.session.openWithCallback(self.callbackmenu, ChoiceBox, keys=nkeys, title=_('Channel selection options') + '.\n' + _('Select option') + ':', list=askList)

    def haycar(self, quecar, acar):
        if quecar.upper() == acar.upper():
            return 0
        index = self.servicelist.l.getNextBeginningWithChar(quecar.lower())
        indexup = self.servicelist.l.getNextBeginningWithChar(quecar.upper())
        if indexup != 0:
            if index > indexup or index == 0:
                index = indexup
        if index > 0:
            return index
        return -1

    def goto(self):
        askList = []
        conta = 0
        activo = 0
        validos1 = 'ABCDEFGHIJKLMN\xc3\x91OPQRSTUVWXYZ'
        validos2 = '0123456789'
        listad = []
        listad2 = []
        nkeys = []
        donde = ''
        cdonde = ''
        try:
            serviceHandler = eServiceCenter.getInstance()
            root = self.getRoot()
            donde = ''
            cdonde = ''
            erpath = str(root.getPath()).upper()
            inBouquet = 'USERBOUQUET.' in erpath
            if inBouquet:
                donde = 'bouquets'
                cdonde = _('Favourites')
            elif 'FROM PROVIDERS' in erpath:
                donde = 'providers'
                cdonde = _('Providers')
            elif 'FROM SATELLITES' in erpath:
                donde = 'satellites'
                cdonde = _('Satellites')
            elif 'FROM BOUQUET' in erpath:
                donde = 'bouquets'
                cdonde = _('Favourites')
            else:
                donde = 'channels'
                cdonde = _('Channels')
            conta = 1
            conta2 = 1
            numero = 0
            if inBouquet:
                list = serviceHandler.list(root)
                if list is not None:
                    while 1:
                        s = list.getNext()
                        if s.valid():
                            pass
                        else:
                            break
                        ref = str(s.toString())
                        path = ServiceReference(s).getServiceName()
                        if s.flags & eServiceReference.isMarker and ref not in listad:
                            listad.append((path.replace('--', ''), str(numero)))
                        else:
                            if conta >= 10:
                                listad2.append(('' + str(conta2) + '', str(numero)))
                                conta = 0
                            conta = conta + 1
                            conta2 = conta2 + 1
                        numero = numero + 1

            elif donde == 'satellites':
                idx = self.servicelist.getCurrentIndex()
                self.servicelist.moveToIndex(0)
                numsat = 0
                listastr = 'xxxyyyzzz'
                while 1:
                    texto = 'NA'
                    try:
                        cur_service = ServiceReference(self.getCurrentSelection())
                        texto = cur_service.getServiceName()
                        texto = texto.split(' - ')[0]
                        if texto == _('Current Transponder'):
                            texto = '(' + texto + ')'
                        if ',' + texto + ',' not in listastr:
                            listad.append((texto, str(numsat)))
                            listastr = listastr + ',' + texto + ','
                    except:
                        pass

                    self.servicelist.moveDown()
                    numsat = numsat + 1
                    if texto == 'NA' or self.servicelist.atEnd() or numsat > 200:
                        break

                listad.sort(key=lambda x: x[0].upper())
                self.servicelist.moveToIndex(idx)
            elif donde == 'providers' or donde == 'channels':
                idx = self.servicelist.getCurrentIndex()
                self.servicelist.moveToIndex(0)
                curlista = '-'
                try:
                    service = ServiceReference(self['ServiceEvent'].getCurrentService())
                    ref = self.getCurrentSelection()
                    info = service and service.info()
                    name = ref and info.getName(ref)
                    if name is None:
                        name = info.getName()
                    name = name.replace('\xc2\x86', '').replace('\xc2\x87', '')
                    curlista = '' + name[0].upper() + ''
                except:
                    try:
                        servicio = self.servicelist.getCurrent()
                        name = ServiceReference(servicio).getServiceName().replace('\xc2\x86', '').replace('\xc2\x87', '')
                        curlista = '' + name[0].upper() + ''
                    except:
                        pass

                for car in validos1:
                    pos = self.haycar(car, curlista)
                    if pos >= 0:
                        listad.append((car, '' + str(pos)))

                for car in validos2:
                    pos = self.haycar(car, curlista)
                    if pos >= 0:
                        listad.append((car, '' + str(pos)))

                self.servicelist.moveToIndex(idx)
        except:
            pass

        askList.append((_('Go to first element'), 'gotop'))
        nkeys.append('red')
        askList.append((_('Go to last element'), 'gobottom'))
        nkeys.append('blue')
        curlista = None
        if self.canalvalido():
            try:
                service = ServiceReference(self['ServiceEvent'].getCurrentService())
                ref = self.getCurrentSelection()
                info = service and service.info()
                name = ref and info.getName(ref)
                if name is None:
                    name = info.getName()
                name = name.replace('\xc2\x86', '').replace('\xc2\x87', '')
                curlista = '' + name[0].upper() + ''
            except:
                try:
                    servicio = self.servicelist.getCurrent()
                    name = ServiceReference(servicio).getServiceName().replace('\xc2\x86', '').replace('\xc2\x87', '')
                    curlista = '' + name[0].upper() + ''
                except:
                    pass

        try:
            if len(listad) > 0 or len(listad2) > 3:
                askList.append(('--', 'nada'))
                nkeys.append('')
                conta = 0
                listakeys = ''
                tadd = '...'
                for path in listad:
                    valoradd = path[0]
                    if not donde == 'bouquets':
                        if donde == 'satellites':
                            tadd = ''
                            prime = valoradd[0]
                            if prime not in listakeys and prime in validos2:
                                nkeys.append(str(prime))
                                listakeys = listakeys + prime
                            else:
                                nkeys.append('-')
                        else:
                            nkeys.append('-')
                        askList.append((valoradd + tadd, str(path[1])))
                        if activo == 0 and not curlista == None:
                            if valoradd == curlista:
                                activo = conta + 3
                        conta = conta + 1
                    else:
                        askList.append((valoradd + '', str(path[1])))
                        if conta < 10:
                            nkeys.append(str(conta))
                        else:
                            nkeys.append('-')
                        conta = conta + 1

                if donde == 'bouquets':
                    if len(listad2) > 3:
                        if len(listad) > 0:
                            askList.append(('--', 'nada'))
                            nkeys.append('')
                    else:
                        listad2 = []
                for path in listad2:
                    valoradd = str(path[0])
                    askList.append((valoradd + '', str(path[1])))

        except:
            pass

        if len(askList) > 3 and activo == 0:
            activo = 3
        self.session.openWithCallback(self.respgoto, ChoiceBox, keys=nkeys, selection=activo, title=_('Select option to go in ') + cdonde, list=askList)

    def respgoto(self, answer = None):
        answer = answer and answer[1]
        if answer:
            if answer == 'nada':
                return
            self.prevBouquet()
            if answer == 'gotop':
                try:
                    self.servicelist.moveToIndex(0)
                except:
                    pass

                return
            if answer == 'gobottom':
                try:
                    self.servicelist.moveToIndex(0)
                    self.servicelist.moveUp()
                except:
                    pass

                return
            try:
                elid = int(answer)
                self.servicelist.moveToIndex(elid)
            except:
                pass

    def canalvalido(self):
        if self.servicelist.getCurrentIndex() == None or self.servicelist.getCurrentIndex() < 0:
            return False
        ref = self.getCurrentSelection()
        if ref is None:
            return False
        if not ref.flags & eServiceReference.isMarker:
            root = self.getRoot()
            if not root or not root.flags & eServiceReference.isGroup or True:
                if not ref.flags & 7 == 7:
                    return True
        return False

    def key0(self):
        if self.canalvalido():
            self.pipAvailable = False
            if SystemInfo.get('NumVideoDecoders', 1) > 1:
                if not self.dopipzap:
                    listacall = ['', 'pip']
                    self.pipAvailable = True
                    self.callbackmenu(listacall)
                else:
                    listacall = ['', 'main']
                    self.callbackmenu(listacall)

    def key1(self):
        self.goto()

    def key8(self):
        if self.canalvalido():
            try:
                ref = self.getCurrentSelection()
                if ref.flags & eServiceReference.isGroup:
                    listacall = ['', 'alter']
                    self.callbackmenu(listacall)
            except:
                pass

    def key9(self):
        listacall = ['', '9']
        self.callbackmenu(listacall)

    def ajustatitulo(self):
        if not config.tvspaze.showtpinfo.value:
            ancho = self['icanal'].instance.size().width()
            listsize = (ancho, self['ititulo'].instance.size().height())
            self['ititulo'].instance.resize(eSize(*listsize))
            self['icanal'].hide()
        else:
            ancho = self.tamtit
            listsize = (ancho, self['ititulo'].instance.size().height())
            self['ititulo'].instance.resize(eSize(*listsize))
            self['icanal'].show()

    def callbackmenu(self, answer):
        answer = answer and answer[1]
        if answer:
            if answer == '1':
                self.prevBouquet()
                self.showAllServices()
            elif answer == 'tpinfo':
                config.tvspaze.showtpinfo.value = not config.tvspaze.showtpinfo.value
                config.tvspaze.showtpinfo.save()
                config.tvspaze.save()
                self.ajustatitulo()
                self.minfocanal()
            elif answer == 'options':
                self.configurach()
            elif answer == 'guia':
                self.guia()
            elif answer == 'help':
                self.showHelp()
            elif answer == 'goto':
                self.goto()
            elif answer == 'info':
                self.tpinfocanal()
            elif answer == 'alter':
                try:
                    self.lastalter = self.getCurrentSelection()
                    elroot = self.getRoot()
                    self.saveRoot()
                    self.saveChannel(self.lastalter)
                    self.enterPath(self.getCurrentSelection())
                    self.startRoot = elroot
                    self.lastalterroot = elroot
                except:
                    pass

            elif answer == 'pip':
                try:
                    self.prevBouquet()
                    self.showServiceInPiP()
                except:
                    pass

            elif answer == 'main':
                try:
                    self.prevBouquet()
                    self.playMain()
                except:
                    pass

            elif answer == 'remove':
                try:
                    self.removeCurrentService()
                except:
                    pass

            elif answer == 'move':
                try:
                    self.toggleMoveMode()
                    self.actualizaepgtmp()
                except:
                    pass

            elif answer == 'add':
                try:
                    self.addServiceToBouquetSelected()
                except:
                    pass

            elif answer == '2':
                self.prevBouquet()
                self.showSatellites()
            elif answer == '3':
                self.prevBouquet()
                self.showProviders()
            elif answer == '3':
                self.prevBouquet()
                self.showFavourites()
            elif answer == '5':
                self.prevBouquet()
                self.showEPGListSPA()
            elif answer == '6':
                from Screens.InfoBar import InfoBar
                if InfoBar and InfoBar.instance:
                    InfoBar.instance.session.open(ChannelSelection)
            elif answer == '7':
                self.timerAdd()
            elif answer == '9':
                self.prevBouquet()
                self.doContext()
            elif answer == '10':
                self.prevBouquet()
                config.tvspaze.spazeChannelMode.value = '0'
                config.tvspaze.spazeChannelMode.save()
                self.cambiaskin()
            elif answer == '11':
                self.prevBouquet()
                config.tvspaze.spazeChannelMode.value = '1'
                config.tvspaze.spazeChannelMode.save()
                self.cambiaskin()
            elif answer == '12':
                self.nextBouquet()
            elif answer == '13':
                self.prevBouquet()
            elif answer == '88':
                self.muestraMosaico()

    def tpinfocanal(self):
        if self.canalvalido():
            try:
                from Plugins.Extensions.spazeMenu.spzPlugins.InfoAz.plugin import InfoAz
                nref = self.getCurrentSelection()
                if nref.flags & eServiceReference.isGroup:
                    oldref = eServiceReference()
                    ref = getBestPlayableServiceReference(nref, oldref, True)
                else:
                    ref = self.servicelist.getCurrent()
                self.session.open(InfoAz, infoservice=ref)
            except:
                pass

    def showServiceInPiP(self):
        try:
            if not self.pipAvailable:
                return
            if self.session.pipshown:
                del self.session.pip
            self.session.pip = self.session.instantiateDialog(PictureInPicture)
            self.session.pip.show()
            newservice = self.servicelist.getCurrent()
            if self.session.pip.playService(newservice):
                self.session.pipshown = True
                self.session.pip.servicePath = self.getCurrentServicePath()
                self.cancel()
            else:
                self.session.pipshown = False
                del self.session.pip
        except:
            pass

    def playMain(self):
        sel = self.getCurrentSelection()
        self.zap()
        self.setCurrentSelection(sel)

    def addServiceToBouquetSelected(self):
        bouquets = self.getBouquetList()
        if bouquets is None:
            cnt = 0
        else:
            cnt = len(bouquets)
        if cnt > 1:
            self.bsel = self.session.openWithCallback(self.bouquetSelClosed, BouquetSelector, bouquets, self.addCurrentServiceToBouquet)
        elif cnt == 1:
            self.addCurrentServiceToBouquet(bouquets[0][1], closeBouquetSelection=False)

    def addCurrentServiceToBouquet(self, dest, closeBouquetSelection = True):
        self.addServiceToBouquet(dest)
        if self.bsel is not None:
            self.bsel.close(True)
        elif closeBouquetSelection:
            self.cancel()

    def bouquetSelClosed(self, recursive):
        self.bsel = None

    def retMosaico(self, ret = None):
        global BouquetSelectorScreen
        if BouquetSelectorScreen is not None:
            BouquetSelectorScreen.close()
            BouquetSelectorScreen = None
        if ret:
            self.tempTimer.start(300, True)

    def getBouquetServices(self, bouquet):
        services = []
        Servicelist = eServiceCenter.getInstance().list(bouquet)
        if Servicelist is not None:
            while True:
                service = Servicelist.getNext()
                if not service.valid():
                    break
                if service.flags & (eServiceReference.isDirectory | eServiceReference.isMarker):
                    continue
                services.append(service)

        return services

    def retBouquet(self, bouquet):
        global BouquetSelectorScreen
        if bouquet is not None:
            services = self.getBouquetServices(bouquet)
            if len(services):
                try:
                    from Plugins.Extensions.spzMosaic.plugin import Mosaic
                    self.session.openWithCallback(self.retMosaico, Mosaic, services)
                except:
                    pass

                return
        if BouquetSelectorScreen is not None:
            try:
                BouquetSelectorScreen.close()
            except:
                pass

        BouquetSelectorScreen = None

    def muestraMosaico(self):
        global BouquetSelectorScreen
        if len(self.session.nav.getRecordings()) > 0:
            cmens = _('Mosaic Plugin is disabled when recordings are runnign!')
            dei = self.session.open(MessageBox, text=cmens, type=MessageBox.TYPE_INFO, timeout=5)
            dei.setTitle('openSPA - ' + _('Channel Selection'))
            return
        if not fileExists('/usr/lib/enigma2/python/Plugins/Extensions/spzMosaic/plugin.pyo'):
            cmens = _('Plugin openSPA Mosaic not installed!\nGo to donwloads section and download it.')
            dei = self.session.open(MessageBox, text=cmens, type=MessageBox.TYPE_INFO, timeout=5)
            dei.setTitle('openSPA - ' + _('Channel Selection'))
            return
        if not fileExists('/usr/bin/chkds'):
            self.session.open(MessageBox, text=_('This plugin is only for customers of Don Satelite\nMore info: www.donsatelite.es :: +34 967 492 025'), type=MessageBox.TYPE_INFO, timeout=10)
            return
        self.prevBouquet()
        bouquets = self.getBouquetList()
        BouquetSelectorScreen = self.session.open(BouquetSelector, bouquets, self.retBouquet, enableWrapAround=True)

    def cambiaskin(self):
        try:
            from Screens.InfoBar import InfoBar
            if InfoBar and InfoBar.instance:
                Notifications.AddPopup(text=_('Channel Selection mode changed!') + '\n' + _('Open Channel Selection again!!'), type=MessageBox.TYPE_INFO, timeout=20, id='NewChannelSelection')
                InfoBar.instance.servicelist = InfoBar.instance.session.instantiateDialog(newChannelSelection)
                self.cancel()
        except:
            pass

    def cbcs(self, resp):
        self.cancel()

    def siedicion(self):
        if self.movemode:
            self['infodch'].setText(_('Edit mode enabled') + '!\n' + _('Press [MENU] to disable it.'))
            self['infodch'].show()
            self.buildTitleString()
            return True
        if not self.bouquet_mark_edit == OFF:
            self['infodch'].setText(_('Edit mode enabled') + '!\n' + _('Press [MENU] to disable it.'))
            self['infodch'].show()
            return True
        self['infodch'].setText(' ')
        self['infodch'].hide()
        return False

    def timerAdd(self):
        if self.activo == 'list':
            if not self.canalvalido():
                return
            event = self['ServiceEvent'].getCurrentEvent()
            serviceref = ServiceReference(self['ServiceEvent'].getCurrentService())
            try:
                titulo = event.getEventName()
            except:
                titulo = _('Title')

        else:
            cur = self['list2'].getCurrent()
            event = cur[0]
            serviceref = cur[1]
            if not event:
                return
            titulo = event.getEventName()
        if event is None:
            return
        try:
            eventid = event.getEventId()
        except:
            eventid = None

        refstr = serviceref.ref.toString()
        try:
            cret = serviceref.ref
            if cret.flags & eServiceReference.isGroup:
                xref = getBestPlayableServiceReference(cret, eServiceReference(), True)
                refstr = xref.toString()
        except:
            pass

        rec = isInTimerSPA(self.session.nav.RecordTimer, eventid, event.getBeginTime(), event.getDuration(), refstr)
        try:
            nombre = rec.name
        except:
            nombre = _('Record')

        if rec is not None:
            cb_func = lambda ret: not ret or self.removeTimer(rec)
            self.session.openWithCallback(cb_func, MessageBox, _('Event exists!!') + '\n' + _('Do you want to delete %s?') % nombre)
        else:
            newEntry = RecordTimerEntry(serviceref, checkOldTimers=True, dirname=preferredTimerPath(), *parseEvent(event))
            self.session.openWithCallback(self.finishedAdd, TimerEntry, newEntry)

    def finishedAdd(self, answer):
        if answer[0]:
            entry = answer[1]
            simulTimerList = self.session.nav.RecordTimer.record(entry)
            if simulTimerList is not None:
                for x in simulTimerList:
                    if x.setAutoincreaseEnd(entry):
                        self.session.nav.RecordTimer.timeChanged(x)

                simulTimerList = self.session.nav.RecordTimer.record(entry)
                if simulTimerList is not None:
                    from Screens.TimerEdit import TimerSanityConflict
                    self.session.openWithCallback(self.finishSanityCorrection, TimerSanityConflict, simulTimerList)
        else:
            self['key_green'].setText(_('Add timer'))
        if self.activo == 'list2':
            try:
                idx = self['list2'].instance.getCurrentIndex()
            except:
                pass

        else:
            self.prevBouquet()
            self.updateLListas()
        if self.activo == 'list2':
            return

    def finishSanityCorrection(self, answer):
        self.finishedAdd(answer)

    def removeTimer(self, timer):
        timer.afterEvent = AFTEREVENT.NONE
        self.session.nav.RecordTimer.removeEntry(timer)
        if self.activo == 'list2':
            try:
                idx = self['list2'].instance.getCurrentIndex()
            except:
                pass

        else:
            self.prevBouquet()
            self.updateLListas()
        if self.activo == 'list2':
            return

    def texto_buscaepg(self):
        lalista = self['list2'].list
        if len(lalista) > 1:
            cur = self['list2'].getCurrent()
            event = cur[0]
            if not event:
                return
            if self.utextobuscar == '':
                textobus = str(event.getEventName())
                textobus = textobus.replace(' (HD)', '').replace('(HD)', '')
                if textobus.endswith('...'):
                    textobus = textobus[:-3]
                if textobus.endswith('...'):
                    textobus = textobus[:-3]
                if textobus.endswith('..'):
                    textobus = textobus[:-2]
            else:
                textobus = self.utextobuscar
            try:
                self.session.openWithCallback(self.busca_epg, spzVirtualKeyboard, titulo=_('Search in EPG'), texto=textobus, ok=True)
            except:
                pass

    def busca_epg(self, loque, inicio = None):
        if not loque == None:
            if len(loque) <= 0:
                return
            self.utextobuscar = loque
            lalista = self['list2'].list
            if len(lalista) > 1:
                idx = self['list2'].instance.getCurrentIndex()
                if inicio == None:
                    inicio = idx
                conta = inicio
                for ele in range(inicio, len(lalista)):
                    if conta > inicio:
                        servicetemp = lalista[ele]
                        if servicetemp[0]:
                            nombre = str(servicetemp[4])
                            textoepg = nombre
                            if loque.upper() in textoepg.upper():
                                self['list2'].instance.moveSelectionTo(conta)
                                break
                    conta = conta + 1

                if self['list2'].instance.getCurrentIndex() == idx:
                    if inicio == idx and idx > 1:
                        self.busca_epg(loque, 0)
                    else:
                        self.session.open(MessageBox, text=_('No more search found for') + ':\n[' + loque.upper() + ']', type=MessageBox.TYPE_INFO, timeout=5)

    def key_info(self):
        if self.activo == 'list':
            event = self['ServiceEvent'].getCurrentEvent()
            service = self['ServiceEvent'].getCurrentService()
            if event is not None:
                try:
                    self.session.open(SpaViewSimple, event, ServiceReference(service), self.eventViewCallback2, self.openSimilarList)
                except:
                    pass

        else:
            cur = self['list2'].getCurrent()
            event = cur[0]
            service = cur[1]
            if event is not None:
                try:
                    self.session.open(SpaViewSimple, event, service, self.eventViewCallback, self.openSimilarList)
                except:
                    pass

    def openSimilarList(self, eventid, refstr):
        pass

    def eventViewCallback2(self, setEvent, setService, val):
        old = self.servicelist.getCurrent()
        salir = False
        conta = 0
        while not salir:
            if val == -1:
                self.servicelist.moveUp()
            elif val == +1:
                self.servicelist.moveDown()
            self.updateEventInfo()
            cur = ServiceReference(self['ServiceEvent'].getCurrentService())
            event = self['ServiceEvent'].getCurrentEvent()
            conta = conta + 1
            if cur and event:
                setService(cur)
                setEvent(event)
                break
            if conta > 110:
                break

    def eventViewCallback(self, setEvent, setService, val):
        l = self['list2']
        old = l.getCurrent()
        if val == -1:
            self['list2'].moveUp()
        elif val == +1:
            self['list2'].moveDown()
        cur = l.getCurrent()
        setService(cur[1])
        setEvent(cur[0])

    def updateEventInfo(self):
        if self.activo == 'list2':
            return
        cur = self.getCurrentSelection()
        self['ServiceEvent'].EnewService(cur)

    def ocultalista1(self):
        pass

    def cbEV(self):
        if self.activo == 'list2':
            self.ocultalista1()
        sie = self.siedicion()
        if self.activo == 'list2':
            self.cbTimer.start(100, True)
        else:
            self.ttimer()

    def key_pageDown(self):
        if self.activo == 'list':
            self.servicelist.instance.moveSelection(self.servicelist.instance.pageDown)
        else:
            self['list2'].instance.moveSelection(self['list2'].instance.pageDown)
            self.actualizaLista2()

    def key_pageUp(self):
        if self.activo == 'list':
            self.servicelist.instance.moveSelection(self.servicelist.instance.pageUp)
        else:
            self['list2'].instance.moveSelection(self['list2'].instance.pageUp)
            self.actualizaLista2()

    def cambialista(self):
        if self.siedicion():
            return
        if self.activo == 'list':
            self.nextBouquet()
        else:
            self.prevBouquet()

    def nextBouquet(self):
        if self.activo == 'list' and not self.siedicion():
            lalista = self['list2'].list
            longi = len(lalista)
            if longi > 1:
                try:
                    self['list2'].instance.setSelectionEnable(1)
                except:
                    pass

                self['key_chmas'].setText(_('Epg Search'))
                self['key_yellow'].setText(_('Single EPG'))
                self.utextobuscar = ''
                self.mueveflecha('list2')
                self['key_chmenos'].setText(_('Channels'))
                self.ttimer(420)
                self.activo = 'list2'
                try:
                    self['list2'].instance.setSelectionEnable(1)
                except:
                    pass

    def prevBouquet(self):
        if self.activo == 'list2' or True:
            try:
                self['list2'].instance.setSelectionEnable(0)
            except:
                pass

            try:
                self['list2'].instance.moveSelectionTo(0)
            except:
                pass

            self.activo = 'list'
            self.mueveflecha('list')
            self['key_chmas'].setText(_('Zap'))
            self['key_yellow'].setText(_('Satellites'))
            self['key_chmenos'].setText(_('Events'))
            self.ttimer()
            cur = self.getCurrentSelection()
            self['ServiceEvent'].newService(cur)
            self.minfocanal(cur)

    def updateLListas(self):
        if self.activo == 'list':
            self.ttimer()
        else:
            self.ttimer(400)

    def mostrarmensaje(self, quemensaje):
        self['infodch'].setText(quemensaje)
        self['infodch'].show()

    def finmensaje(self):
        self['infodch'].setText(' ')
        self['infodch'].hide()

    def actualizaepg(self, emaximo = 0):
        if emaximo == 0:
            emaximo = self.getjusto()
        if self.siedicion():
            return
        if self.seg_plano_exit:
            return
        self.minfocanal()
        if emaximo == 19 and self.activo == 'list2':
            self.prevBouquet()
        service = ServiceReference(self['ServiceEvent'].getCurrentService())
        l = self['list2']
        l.recalcEntrySize()
        l.fillSingleEPG(service, emaximo, int(config.tvspaze.maxdaysEPG.value))
        if emaximo == self.getjusto():
            self['list2'].instance.moveSelectionTo(0)
            try:
                self['list2'].instance.setSelectionEnable(0)
            except:
                pass

        self.actualizaScrolls()

    def getjusto(self):
        altolista = 16
        try:
            altolista = int(self['list2'].instance.size().height() / 30) - 1
        except:
            pass

        return altolista

    def egetClockPixmap(self, refstr, beginTime, duration, eventId, service):
        pre_clock = 1
        post_clock = 2
        clock_type = 0
        timer = self.session.nav.RecordTimer
        endTime = beginTime + duration
        rec = beginTime and timer.isInTimer(eventId, beginTime, duration, service)
        if not rec:
            return 0
        elif len(timer.timer_list) <= 0:
            return 0
        for x in timer.timer_list:
            if x.service_ref.ref.toString() == refstr:
                if x.eit == eventId:
                    return 1
                beg = x.begin
                end = x.end
                if beginTime > beg and beginTime < end and endTime > end:
                    clock_type |= pre_clock
                elif beginTime < beg and endTime > beg and endTime < end:
                    clock_type |= post_clock

        if clock_type == 0:
            return 4
        elif clock_type == pre_clock:
            return 2
        elif clock_type == post_clock:
            return 3
        else:
            return 5
        return 0

    def mueveflecha(self, objeto):
        try:
            altoimg = self['flecha_arr'].instance.size().height()
            anchoimg = self['flecha_arr'].instance.size().width() / 2
            ancho = self[objeto].instance.size().width() / 2
            alto = self[objeto].instance.size().height()
            lax = self[objeto].instance.position().x()
            lay = self[objeto].instance.position().y() - 1
            self['flecha_arr'].instance.move(ePoint(lax + ancho - anchoimg, lay - altoimg - 3))
            self['flecha_abj'].instance.move(ePoint(lax + ancho - anchoimg, lay + alto + 4))
            if objeto == 'list':
                cual = 'spzRight.png'
            else:
                cual = 'spzLeft.png'
            imagencual = '/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/newChannelSelection/spzTeam/' + cual
            if fileExists(imagencual):
                self['flecha_medio'].instance.setPixmapFromFile(imagencual)
            self['linea_abj'].instance.move(ePoint(lax, lay + alto + 1))
            self['linea_arr'].instance.move(ePoint(lax, lay - 1))
            altolin = self['linea_arr'].instance.size().height()
            listsize = (ancho * 2, altolin)
            self['linea_arr'].instance.resize(eSize(*listsize))
            self['linea_abj'].instance.resize(eSize(*listsize))
        except:
            pass

    def cambia(self, cual = None):
        if cual == None:
            if self.activo == 'list':
                self.activo = 'list2'
            else:
                self.activo = 'list'
        else:
            self.activo = cual

    def eshowFavourites(self):
        self.prevBouquet()
        self.showFavourites()

    def eshowSatellites(self):
        if self.activo == 'list':
            self.prevBouquet()
            self.showSatellites()
        else:
            self.key3()

    def alcrear(self):
        openspaSB(objectoself=self, nombrelista='list', barra='servicelist')
        self.servicelist.onSelectionChanged.append(self.actualizaepgtmp)
        self['key_red'].setText(_('Internet info'))
        self['key_green'].setText(_('Add timer'))
        self['key_yellow'].setText(_('Satellites'))
        self.tamtit = self['ititulo'].instance.size().width()
        self.prevBouquet()
        self.actualizaepgtmp()
        self.ajustatitulo()

    def actualizaLista2(self):
        lalista = self['list2'].list
        length = len(lalista)
        self.ocultalista1()
        if length > 1:
            pass

    def buildTitleString(self):
        titleStr = ''
        Len = len(self.servicePath)
        if Len > 0:
            base_ref = self.servicePath[0]
            if Len > 1:
                end_ref = self.servicePath[Len - 1]
            else:
                end_ref = None
            nameStr = self.getServiceName(base_ref)
            titleStr = nameStr
            if end_ref is not None:
                nameStr = self.getServiceName(end_ref)
                titleStr = nameStr
        if self.dopipzap:
            titleStr = 'PiP-' + titleStr
        self.setTitle(titleStr)
        self['ititulo'].setText(titleStr)

    def actualizaepgtmp(self):
        self.seg_plano_exit = True
        try:
            self.seg_plano._Thread__stop()
        except:
            pass

        self.seg_plano = None
        list = []
        self['list2'].l.setList(list)
        if self.siedicion():
            return
        ref = self.getCurrentSelection()
        if ref.flags & eServiceReference.isGroup:
            ref = getBestPlayableServiceReference(ref, eServiceReference(), True)
        try:
            cual = rutapicon(ref.toString())
            if fileExists(cual):
                self['img_picon'].instance.setPixmapFromFile(cual)
                self['img_picon'].instance.setScale(1)
        except:
            pass

        self.timerEpg.stop()
        self.timerEpg.start(800, True)

    def minfocanal(self, pref = None):
        if config.tvspaze.showtpinfo.value:
            if self.canalvalido():
                try:
                    if not pref == None:
                        ref = pref
                    else:
                        ref = self.getCurrentSelection()
                    addtexto = ''
                    if ref.flags & eServiceReference.isGroup:
                        oldref = eServiceReference()
                        ref = getBestPlayableServiceReference(ref, eServiceReference(), True)
                        addtexto = '(' + _('Group') + ') '
                    self['icanal'].setText(addtexto + infocanalnc(ref))
                    return
                except:
                    pass

        self['icanal'].setText(' ')

    def ttimer(self, max = 0):
        self.timerEpg.stop()
        self.seg_plano_exit = False
        self.seg_plano = segundoplano(self, max)
        self.seg_plano.start()

    def key_Up(self):
        if self.activo == 'list':
            self.servicelist.moveUp()
        else:
            self['list2'].moveUp()
            self.actualizaLista2()

    def key_Down(self):
        if self.activo == 'list':
            self.servicelist.moveDown()
        else:
            self['list2'].moveDown()
            self.actualizaLista2()


def zapSimple():
    from Screens.InfoBar import InfoBar
    if InfoBar and InfoBar.instance:
        InfoBar.instance.session.open(spzSimpleChannelSelection, _('Channel Selection'), currentBouquet=True)


def zapTest():
    from Screens.InfoBar import InfoBar
    if InfoBar and InfoBar.instance:
        InfoBar.instance.session.open(SimpleChannelSelection2, _('Channel'), currentBouquet=True)


from Screens.InfoBar import InfoBar

class spzSimpleChannelSelection(ChannelSelectionBase, SelectionEventInfo):
    skin = '<screen name="spzSimpleChannelSelection" position="55,65" size="430,440" title="Channel">\n\t\t\t  <widget name="list" position="0,5" size="430,390" scrollbarMode="showOnDemand" transparent="1" progressbarHeight="3" itemHeight="30" serviceItemHeight="30" serviceNumberFont="Regular;17" serviceNameFont="Regular;19" serviceInfoFont="Regular;16" />\n\t\t\t  \n\t\t\t  <widget name="key_red" position="54,404" size="91,30" zPosition="1" font="Regular; 15" halign="left" valign="center" backgroundColor="#30000000" transparent="1" noWrap="1" foregroundColor="foreground" />\n\t\t\t  <eLabel name="linearoja" position="146,432" size="42,5" backgroundColor="#10cc0000" />\n\t\t\t  <widget name="key_green" position="146,404" size="132,30" zPosition="1" font="Regular; 15" halign="center" valign="center" backgroundColor="#30000000" transparent="1" noWrap="1" foregroundColor="foreground" />\n\t\t\t\t\n\t\t\t  <widget name="key_yellow" position="292,432" size="130,5" zPosition="1" font="Regular; 15" halign="center" valign="center" backgroundColor="#1022cc22" transparent="0" />\n\t\t\t\t<eLabel name="lineaamarilla" position="191,432" size="42,5" backgroundColor="#00aaaa00" />\n\t\t\t  <widget name="key_blue" position="292,404" size="130,30" zPosition="1" font="Regular; 15" halign="center" valign="center" backgroundColor="#30000000" transparent="1" foregroundColor="foreground" />\n\t\t\t<eLabel name="lineaazul" position="236,432" size="42,5" backgroundColor="#104444cc" />\n\t\t\t<eLabel name="labelok" position="11,404" size="43,30" zPosition="25" transparent="1" text="[OK]" noWrap="1" font="Regular; 15" valign="center" halign="center" />\n\t\t</screen>'

    def __init__(self, session, title = _('Channel Selection'), currentBouquet = True):
        ChannelSelectionBase.__init__(self, session)
        SelectionEventInfo.__init__(self)
        self['ChannelSelectBaseActions'] = ActionMap(['ChannelSelectBaseActions',
         'OkCancelActions',
         'TvRadioActions',
         'ColorActions',
         'MenuActions',
         'ChannelSelectEPGActions',
         'GlobalActions',
         'MediaPlayerActions'], {'cancel': self.close,
         'ok': self.channelSelected,
         'keyRadio': self.ampliacanales,
         'keyTV': self.ampliacanales,
         'blue': self.ampliacanales,
         'red': self.ampliacanales,
         'yellow': self.ampliacanales,
         'green': self.muestralt,
         'menu': self.muestramenu,
         'power_down': self.apagar,
         'showFavourites': self.ampliacanales,
         'showAllServices': self.ampliacanales,
         'showProviders': self.ampliacanales,
         'showSatellites': self.muestralt,
         'nextBouquet': self.bkeyRight,
         'prevBouquet': self.bkeyLeft,
         'nextMarker': self.nextMarker,
         'prevMarker': self.prevMarker,
         'gotAsciiCode': self.keyAsciiCode,
         'keyLeft': self.nkeyLeft,
         'keyRight': self.nkeyRight,
         'keyRecord': self.ampliacanales,
         '1': self.keyNumberGlobal,
         '2': self.keyNumberGlobal,
         '3': self.keyNumberGlobal,
         '4': self.keyNumberGlobal,
         '5': self.keyNumberGlobal,
         '6': self.keyNumberGlobal,
         '7': self.keyNumberGlobal,
         '8': self.keyNumberGlobal,
         '9': self.keyNumberGlobal,
         '0': self.keyNumber0,
         'showEPGList': self.info_epg,
         'play': self.mostrarenpipmain,
         'pause': self.mostrarenpipmain}, -2)
        self.bouquet_mark_edit = OFF
        self.title = title
        self.simpletitle = title
        self.lastalterroot = None
        self.lastservice = config.tv.lastservice
        self.lastroot = config.tv.lastroot
        self.currentBouquet = currentBouquet
        self.onLayoutFinish.append(self.layoutFinished)
        self['key_red'].setText(_('Zap'))
        self['key_green'].setText(_('Extended list'))
        self['key_yellow'].setText(' ')
        self['key_blue'].setText(_('Alternatives'))
        self['key_blue'].hide()
        self['key_yellow'].hide()
        self.enalterna = False
        self.ucanal = None
        self.servicelist.onSelectionChanged.append(self.actualizakeys)

    def actualizakeys(self):
        if self.enalterna:
            return
        cvalido = self.canalvalido()
        if cvalido:
            try:
                ref = self.getCurrentSelection()
                if ref.flags & eServiceReference.isGroup:
                    self['key_blue'].show()
                    self['key_yellow'].show()
                    return
            except:
                pass

        self['key_blue'].hide()
        self['key_yellow'].hide()

    def keyNumberGlobal(self, number = None):
        self.ampliacanales()

    def keyNumber0(self, number = None):
        self.muestralt()

    def muestramenu(self):
        nombrecanal = ''
        cvalido = self.canalvalido()
        if cvalido:
            try:
                service = ServiceReference(self['ServiceEvent'].getCurrentService())
                ref = self.getCurrentSelection()
                info = service and service.info()
                name = ref and info.getName(ref)
                if name is None:
                    name = info.getName()
                name = name.replace('\xc2\x86', '').replace('\xc2\x87', '')
                nombrecanal = ' (' + name + ')'
            except:
                try:
                    servicio = self.servicelist.getCurrent()
                    name = ServiceReference(servicio).getServiceName().replace('\xc2\x86', '').replace('\xc2\x87', '')
                    nombrecanal = ' (' + name + ')'
                except:
                    pass

            if nombrecanal == '':
                cvalido = False
        nkeys = []
        askList = []
        if self.enalterna:
            askList.append((_('Back') + ' - ' + _('Alternatives'), 'alt'))
            nkeys.append('green')
        elif cvalido:
            try:
                ref = self.getCurrentSelection()
                if ref.flags & eServiceReference.isGroup:
                    askList.append((_('Show alternative channels') + nombrecanal, 'alt'))
                    nkeys.append('green')
            except:
                pass

        askList.append((_('Extended list'), 'ext'))
        nkeys.append('red')
        askList.append(('--', 'nada'))
        nkeys.append('')
        if cvalido:
            askList.append((_('Single EPG for') + nombrecanal, 'epg'))
            nkeys.append('1')
            askList.append((_('Event Info') + nombrecanal, 'inf'))
            nkeys.append('2')
        if fileExists('/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/openSPATVGuide/plugin.pyo') or fileExists('/usr/lib/enigma2/python/Plugins/Extensions/CoolTVGuide/plugin.pyo'):
            askList.append((_('EPG Guide'), 'gui'))
            nkeys.append('3')
        if SystemInfo['PIPAvailable']:
            askList.append(('--', 'nada'))
            nkeys.append('')
            if InfoBar.instance.servicelist.dopipzap:
                askList.append(('[>] ' + _('play in mainwindow') + nombrecanal, 'pipmai'))
            else:
                askList.append(('[>] ' + _('play as picture in picture') + nombrecanal, 'pippip'))
            nkeys.append('blue')
        dei = self.session.openWithCallback(self.callbackmenu, ChoiceBox, keys=nkeys, title=_('Select option') + ':', list=askList)
        dei.setTitle(_('Options') + ' ' + _('Channel Selection'))

    def info_epg(self):
        if fileExists('/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/openSPATVGuide/plugin.pyo'):
            event = self['ServiceEvent'].getCurrentEvent()
            service = self['ServiceEvent'].getCurrentService()
            if event is None:
                return
            try:
                from Plugins.Extensions.spazeMenu.spzPlugins.openSPATVGuide.EPGSimple import spaEPGSelection
                self.session.open(spaEPGSelection, service)
                return
            except:
                pass

    def callbackmenu(self, answer):
        global cbGuia
        answer = answer and answer[1]
        if answer:
            if answer == '1':
                self.showAllServices()
            elif answer == 'pippip':
                self.showServiceInPiP()
            elif answer == 'pipmai':
                self.playMain()
            elif answer == 'ext':
                self.ampliacanales()
            elif answer == 'inf':
                self.key_info()
            elif answer == 'epg':
                self.info_epg()
            elif answer == 'gui':
                if fileExists('/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/openSPATVGuide/plugin.pyo') or fileExists('/usr/lib/enigma2/python/Plugins/Extensions/CoolTVGuide/plugin.pyo'):
                    cbGuia = eTimer()
                    cbGuia.callback.append(muestraguia)
                    cbGuia.start(200, True)
                    self.close()
            elif answer == 'alt':
                self.muestralt()
            elif answer == 'sat':
                self.showSatellites()
            elif answer == '3':
                self.showProviders()
            elif answer == 'fav':
                self.showFavourites()

    def mostrarenpipmain(self):
        if InfoBar.instance.servicelist.dopipzap:
            self.playMain()
        else:
            self.showServiceInPiP()

    def showServiceInPiP(self):
        selfbar = InfoBar.instance.servicelist
        try:
            if not SystemInfo['PIPAvailable']:
                return
            if selfbar.session.pipshown:
                del selfbar.session.pip
            selfbar.session.pip = selfbar.session.instantiateDialog(PictureInPicture)
            selfbar.session.pip.show()
            newservice = self.servicelist.getCurrent()
            if selfbar.session.pip.playService(newservice):
                selfbar.session.pipshown = True
                selfbar.session.pip.servicePath = selfbar.getCurrentServicePath()
            else:
                selfbar.session.pipshown = False
                del selfbar.session.pip
        except:
            pass

        self.close()

    def playMain(self):
        try:
            sel = self.getCurrentSelection()
            InfoBar.instance.servicelist.setCurrentSelection(sel)
            InfoBar.instance.servicelist.zap()
            InfoBar.instance.servicelist.setCurrentSelection(sel)
        except:
            pass

        self.close()

    def muestralt(self):
        if self.enalterna:
            self['key_blue'].setText(_('Alternatives'))
            self.layoutFinished()
            self.enalterna = False
            try:
                lastservice = self.ucanal
                if lastservice.valid():
                    self.setCurrentSelection(lastservice)
            except:
                pass

            self.ucanal = None
            self.lastalterroot = None
            return
        try:
            ref = self.getCurrentSelection()
            if ref.flags & eServiceReference.isGroup:
                lastalter = self.getCurrentSelection()
                self.lastalterroot = self.getRoot()
                self.enalterna = True
                self.enterPath(lastalter)
                self.ucanal = ref
                self['key_blue'].setText(_('Back'))
        except:
            pass

    def canalvalido(self):
        if self.servicelist.getCurrentIndex() == None or self.servicelist.getCurrentIndex() < 0:
            return False
        else:
            ref = self.getCurrentSelection()
            if ref is None:
                return False
            if not ref.flags & eServiceReference.isMarker:
                root = self.getRoot()
                if not root or not root.flags & eServiceReference.isGroup or True:
                    if not ref.flags & 7 == 7:
                        return True
            return False
        if fileExists('/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/openSPATVGuide/plugin.pyo'):
            if self.activo == 'list':
                event = self['ServiceEvent'].getCurrentEvent()
                service = self['ServiceEvent'].getCurrentService()
            else:
                service = self['ServiceEvent'].getCurrentService()
                cur = self['list2'].getCurrent()
                event = cur[0]
            if event is None:
                return
            try:
                from Plugins.Extensions.spazeMenu.spzPlugins.openSPATVGuide.EPGSimple import spaEPGSelection
                self.session.open(spaEPGSelection, service)
                return
            except:
                pass

    def moveUp(self):
        self.servicelist.moveUp()

    def moveDown(self):
        self.servicelist.moveDown()

    def nkeyLeft(self):
        if config.usage.oldstyle_channel_select_controls.value:
            self.ampliacanales()
        else:
            self.keyLeft()

    def nkeyRight(self):
        if config.usage.oldstyle_channel_select_controls.value:
            self.ampliacanales()
        else:
            self.keyRight()

    def bkeyLeft(self):
        self.ampliacanales()

    def bkeyRight(self):
        self.ampliacanales()

    def keyRecord(self):
        self.ampliacanales()

    def layoutFinished(self):
        try:
            self.setModeTv()
            self.setTitle(self.simpletitle)
            if self.currentBouquet:
                ref = InfoBar.instance.servicelist.getRoot()
                if ref:
                    self.enterPath(ref)
                    self.gotoCurrentServiceOrProvider(ref)
                try:
                    lastservice = InfoBar.instance.servicelist.getCurrentSelection()
                    if lastservice.valid():
                        self.setCurrentSelection(lastservice)
                except:
                    pass

            self.buildTitleString()
        except:
            pass

    def channelSelected(self, doClose = True):
        try:
            xref = self.getCurrentSelection()
            if xref.flags & eServiceReference.flagDirectory == eServiceReference.flagDirectory:
                from Components import ParentalControl
                if ParentalControl.parentalControl.isServicePlayable(xref, self.bouquetParentalControlCallback, self.session):
                    self.enterPath(xref)
                    self.gotoCurrentServiceOrProvider(xref)
                return
            if not (xref.flags & eServiceReference.isMarker or xref.type == -1):
                root = self.getRoot()
                if True:
                    InfoBar.instance.servicelist.zap(ref=xref, enable_pipzap=doClose, preview_zap=not doClose)
                    if self.enalterna:
                        if self.lastalterroot:
                            InfoBar.instance.servicelist.enterPath(self.lastalterroot)
                            if self.ucanal:
                                InfoBar.instance.servicelist.setCurrentSelection(self.ucanal)
                    if doClose:
                        if InfoBar.instance.servicelist.dopipzap:
                            InfoBar.instance.servicelist.zapBack()
                        InfoBar.instance.servicelist.startServiceRef = None
                        InfoBar.instance.servicelist.startRoot = None
                        InfoBar.instance.servicelist.correctChannelNumber()
                        InfoBar.instance.servicelist.editMode = False
            self.close()
        except:
            pass

    def apagar(self):
        Notifications.AddNotification(Standby.Standby)
        self.close()

    def bouquetParentalControlCallback(self, ref):
        self.enterPath(ref)
        self.gotoCurrentServiceOrProvider(ref)

    def ampliacanales(self):
        if self.servicelist:
            try:
                InfoBar.instance.session.execDialog(InfoBar.instance.servicelist)
            except:
                pass

        try:
            if self.enalterna:
                lastservice = self.ucanal
            else:
                lastservice = self.getCurrentSelection()
            if lastservice.valid():
                InfoBar.instance.servicelist.setCurrentSelection(lastservice)
        except:
            pass

        try:
            self.close()
        except:
            pass

    def setModeTv(self):
        self.lastservice = config.tv.lastservice
        self.lastroot = config.tv.lastroot
        self.setTvMode()
        self.showFavourites()
        self.buildTitleString()

    def buildTitleString(self):
        titleStr = ''
        sepa = ''
        Len = len(self.servicePath)
        if Len > 0:
            base_ref = self.servicePath[0]
            if Len > 1:
                end_ref = self.servicePath[Len - 1]
            else:
                end_ref = None
            nameStr = self.getServiceName(base_ref)
            titleStr = nameStr
            if end_ref is not None:
                nameStr = self.getServiceName(end_ref)
                titleStr = nameStr
        if str(titleStr) == '':
            titleStr = self.simpletitle
        if InfoBar.instance.servicelist.dopipzap:
            titleStr = 'PiP-' + titleStr
        self.setTitle(titleStr)

    def key_info(self):
        event = self['ServiceEvent'].getCurrentEvent()
        service = self['ServiceEvent'].getCurrentService()
        if event is not None:
            try:
                self.session.open(SpaViewSimple, event, ServiceReference(service), self.eventViewCallback2, self.openSimilarList)
            except:
                pass

    def openSimilarList(self, eventid, refstr):
        pass

    def eventViewCallback2(self, setEvent, setService, val):
        pass
