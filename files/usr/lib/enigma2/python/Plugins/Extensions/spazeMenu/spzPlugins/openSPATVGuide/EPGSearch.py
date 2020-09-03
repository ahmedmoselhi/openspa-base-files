from enigma import eEPGCache, eTimer, gFont, eServiceReference, RT_HALIGN_LEFT, RT_HALIGN_RIGHT, eListboxPythonMultiContent, getBestPlayableServiceReference
from Tools.Directories import resolveFilename, SCOPE_CURRENT_SKIN, SCOPE_SKIN_IMAGE, fileExists
from Tools.LoadPixmap import LoadPixmap
from ServiceReference import ServiceReference
from Components.Pixmap import Pixmap
from Screens.ChoiceBox import ChoiceBox
from Screens.EpgSelection import EPGSelection
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from RecordTimer import RecordTimerEntry, parseEvent
from Screens.TimerEntry import TimerEntry
from Components.UsageConfig import preferredTimerPath
from Components.ActionMap import ActionMap
from Components.Button import Button
from Components.Label import Label
from Components.config import config
from Components.EpgList import EPGList, EPG_TYPE_SINGLE, EPG_TYPE_MULTI
from Components.Sources.ServiceEvent import ServiceEvent
from Components.Sources.Event import Event
from Components.MultiContent import MultiContentEntryText
from time import localtime, strftime, time
from operator import itemgetter
from Components.config import config, ConfigSet, ConfigSubsection, ConfigText, ConfigNumber, ConfigYesNo
config.plugins.epgsearchOS = ConfigSubsection()
config.plugins.epgsearchOS.history = ConfigSet(choices=[])
config.plugins.epgsearchOS.encoding = ConfigText(default='UTF-8', fixed_size=False)
config.plugins.epgsearchOS.history_length = ConfigNumber(default=10)
config.plugins.epgsearchOS.add_search_to_epg = ConfigYesNo(default=True)
from Components.Converter.genre import getGenreStringMain, getGenreStringSub, getGenreStringLong
from skin import parseColor
from os import environ
import gettext
from Components.Language import language
from Tools.Directories import SCOPE_PLUGINS, SCOPE_LANGUAGE
lang = language.getLanguage()
environ['LANGUAGE'] = lang[:2]
lenguaje = str(lang[:2])
gettext.bindtextdomain('enigma2', resolveFilename(SCOPE_LANGUAGE))
gettext.textdomain('enigma2')
gettext.bindtextdomain('EPGSearch', '%s%s' % (resolveFilename(SCOPE_PLUGINS), 'Extensions/spazeMenu/spzPlugins/openSPATVGuide/locale/'))

def _(txt):
    t = gettext.dgettext('EPGSearch', txt)
    if t == txt:
        t = gettext.gettext(txt)
    return t


def geticonogenero(numero, tam = 23):
    path = None
    if numero >= 1 and numero <= 11:
        path = '/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/openSPATVGuide/g/' + str(tam) + '/ico' + str(numero) + '-fs8.png'
        if fileExists(path):
            return path


def getcolorgenero(numero, enhex = False):
    colores = [None,
     '#86bbff',
     '#a6ad40',
     '#ffff00',
     '#ff83ff',
     '#93f500',
     '#aa88ff',
     '#afafaf',
     '#c9af96',
     '#a87f57',
     '#ff9933',
     None,
     None,
     None,
     None,
     None,
     None,
     None,
     None,
     None,
     None,
     None,
     None]
    valor = colores[numero]
    if valor:
        if enhex:
            valor = parseColor(valor).argb()
        else:
            valor = parseColor(valor)
    return valor


def getgenero(evento, tam = 23, cortar = True):
    try:
        genre = evento.getGenreData()
        if genre is None:
            return ['', None, None]
        if genre.getLevel1() == 15:
            return ['', None, None]
        txto = getGenreStringSub(genre.getLevel1(), genre.getLevel2())
        submain = getGenreStringMain(genre.getLevel1(), genre.getLevel2())
        if _('User defined') in txto or txto == '':
            txto = _(submain)
        elif _('User defined') in submain or _('Reserved') in submain or _('Other') in submain:
            pass
        else:
            txto = _(submain) + ' ' + _(txto)
        if _('User defined') in txto or _('Reserved') in txto or _('Other') in txto:
            return ['', None, None]
        if 'project-id-version' in txto.lower():
            return ['', None, None]
        if len(txto) > 35 and cortar:
            txto = txto[:35] + '...'
        return [txto, getcolorgenero(genre.getLevel1()), geticonogenero(genre.getLevel1(), tam)]
    except:
        return ['', None, None]


def rutapicon(serviceName):
    try:
        if '::' in serviceName:
            serviceName = serviceName.split('::')[0] + ':'
    except:
        pass

    serviceName = serviceName.replace(':', '_')
    serviceName = serviceName[:-1]
    from Components.Renderer import Picon
    searchPaths = Picon.searchPaths
    for path in searchPaths:
        pngname = path + serviceName + '.png'
        if fileExists(pngname):
            return pngname

    tmp = resolveFilename(SCOPE_CURRENT_SKIN, 'picon_default.png')
    if fileExists(tmp):
        return tmp
    else:
        return resolveFilename(SCOPE_SKIN_IMAGE, 'skin_default/picon_default.png')
    return ''


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


def isInTimer(listatimer, eventid, begin, duration, service):
    return isInTimerSPA(listatimer, eventid, begin, duration, service)


def rutapiconS(serviceName):
    return rutapicon(serviceName)


maintype = [_('Reserved'),
 _('Movie/Drama'),
 _('News Current Affairs'),
 _('Show Games show'),
 _('Sports'),
 _('Children/Youth'),
 _('Music/Ballet/Dance'),
 _('Arts/Culture'),
 _('Social/Political/Economics'),
 _('Education/Science/...'),
 _('Leisure hobbies'),
 _('Other')]

class EPGSearchList(EPGList):

    def __init__(self, type = EPG_TYPE_SINGLE, selChangedCB = None, timer = None):
        EPGList.__init__(self, type, selChangedCB, timer)
        self.days = (_('Mon') + '.',
         _('Tue') + '.',
         _('Wed') + '.',
         _('Thu') + '.',
         _('Fri') + '.',
         _('Sat') + '.',
         _('Sun') + '.')
        self.l.setBuildFunc(self.buildEPGSearchEntry)
        self.l.setFont(0, gFont('Regular', 19))
        self.clock_pixmap = LoadPixmap(cached=True, path='/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/newChannelSelection/spzTeam/epgclock.png')
        self.clock_add_pixmap = LoadPixmap(cached=True, path='/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/newChannelSelection/spzTeam/epgclock_add.png')
        self.clock_pre_pixmap = LoadPixmap(cached=True, path='/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/newChannelSelection/spzTeam/epgclock_pre.png')
        self.clock_post_pixmap = LoadPixmap(cached=True, path='/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/newChannelSelection/spzTeam/epgclock_post.png')
        self.clock_prepost_pixmap = LoadPixmap(cached=True, path='/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/newChannelSelection/spzTeam/epgclock_prepost.png')
        self.clocks = [self.clock_add_pixmap,
         self.clock_pre_pixmap,
         self.clock_pixmap,
         self.clock_prepost_pixmap,
         self.clock_post_pixmap]

    def buildEPGSearchEntry(self, service, eventId, beginTime, duration, EventName, genero = None):
        now = time()
        nowTime = localtime(now)
        correcion = 20
        posini = 10
        r1 = self.weekday_rect
        r2 = self.datetime_rect
        r3 = self.descr_rect
        t = localtime(beginTime)
        if nowTime[2] != t[2]:
            datestr = self.days[t[6]]
        else:
            datestr = _('Today')
        cmes = str(strftime('%b', t))
        serviceref = ServiceReference(service)
        nombrecanal = serviceref.getServiceName()
        res = [None, MultiContentEntryText(pos=(posini - 2, 0), size=(63, 25), font=0, flags=RT_HALIGN_LEFT, text=datestr, color=12632256), MultiContentEntryText(pos=(posini + 48, 0), size=(140, 25), font=0, flags=RT_HALIGN_LEFT, text='%02d/%s, %02d:%02d' % (t[2],
          cmes,
          t[3],
          t[4]), color=15053379)]
        clock_pic = self.getPixmapForEntry(service, eventId, beginTime, duration)
        if clock_pic is not None:
            res.extend(((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND,
              posini + 50 + 0 + 140 + 165,
              1,
              24,
              24,
              clock_pic), MultiContentEntryText(pos=(posini + 50 + 140, 0), size=(160, 25), font=0, flags=RT_HALIGN_LEFT, text=nombrecanal, color=11579568), MultiContentEntryText(pos=(posini + 50 + 23 + 140 + 165, 0), size=(426, 25), font=0, flags=RT_HALIGN_LEFT, text=EventName, color=16777215)))
        else:
            res.append(MultiContentEntryText(pos=(posini + 50 + 140, 0), size=(160, 25), font=0, flags=RT_HALIGN_LEFT, text=nombrecanal, color=11579568))
            res.append(MultiContentEntryText(pos=(posini + 50 + 140 + 165, 0), size=(426, 25), font=0, flags=RT_HALIGN_LEFT, text=EventName, color=16777215))
        gcolor = 594197
        if genero:
            try:
                clock_pic = geticonogenero(genero[0][0], 23)
                if clock_pic is not None:
                    png = LoadPixmap(cached=True, path=clock_pic)
                    res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND,
                     793,
                     1,
                     23,
                     23,
                     png))
            except:
                pass

        return res

    def getPixmapForEntry(self, service, eventId, beginTime, duration):
        if not beginTime:
            return
        else:
            rec = isInTimerSPA(self.timer, eventId, beginTime, duration, service)
            if rec is not None:
                return self.clocks[2]
            return

    def getmejor(self, laref):
        try:
            cret = ServiceReference(laref).ref
            if cret.flags & eServiceReference.isGroup:
                xref = getBestPlayableServiceReference(cret, eServiceReference(), True)
                fref = eServiceReference(xref.toString())
                return fref
        except:
            pass

        return laref


class EPGSearch(EPGSelection):
    skin = '\n\t\t\t<screen name="EPGSearchOS" position="0,0" size="1281,721" backgroundColor="#030813" title="EPG" flags="wfNoBorder">\n\t\t\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/openSPATVGuide/img/lupafs8.png" position="37,200" size="70,70" alphatest="blend" name="lupa" zPosition="50" />\n\t\t\t\t<widget source="Title" render="Label" position="572,19" size="427,23" font="Regular; 20" foregroundColor="#00c0c0c0" backgroundColor="#00113778" halign="center" transparent="0" valign="center" />\n\t\t\t\t\n\t\t\t<widget source="Event" render="Label" position="338,19" size="233,23" font="Regular;20" halign="left" foregroundColor="#000000" backgroundColor="#e5b243" transparent="0" valign="center">\n\t\t\t  <convert type="EventTime">StartTime</convert>\n\t\t\t  <convert type="ClockToText">Format:%d-%b-%Y</convert>\n\t\t\t</widget>\n\n\n\t\t\t\t<widget source="session.RecordState" render="Pixmap" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/openSPATVGuide/img/rec.png" position="1155,21" size="20,20" zPosition="3" alphatest="blend">\n\t\t\t\t  <convert type="ConditionalShowHide" />\n\t\t\t\t</widget>\n\t\t\t\t<widget source="global.CurrentTime" render="Label" position="1141,19" size="100,23" font="Regular; 19" foregroundColor="#999999" backgroundColor="#132d53" shadowColor="#000000" halign="right" transparent="0" valign="center">\n\t\t\t\t\t<convert type="ClockToText">Default</convert>\n\t\t\t\t</widget>\n\t\t\t\t<widget source="global.CurrentTime" render="Label" position="1000,19" size="151,23" font="Regular; 19" foregroundColor="#999999" backgroundColor="#132d53" shadowColor="#000000" halign="right" transparent="0" valign="center" zPosition="1">\n\t\t\t\t  <convert type="ClockToText">Format:%d-%b-%Y</convert>\n\t\t\t\t</widget>\n\t\t\t\t\n\t\t\t\t<widget name="info" position="389,209" size="820,450" transparent="1" foregroundColor="#e0e0e0" backgroundColor="#000000" font="Regular; 20" borderColor="#00000000" borderWidth="1" zPosition="1" />\n\t\t\t\t\n\t\t\t\t<widget name="list" position="380,209" size="840,450" scrollbarMode="showOnDemand" transparent="0" itemHeight="25" foregroundColor="#e0e0e0" backgroundColor="#101b22" backgroundColorSelected="#00e5b243" foregroundColorSelected="#000000" />\n\t\t\t\t\n\t\t\t\t<widget source="Event" render="Label" position="338,47" size="100,25" font="Regular; 20" foregroundColor="#00e5b243" backgroundColor="#31000000" shadowColor="#000000" halign="left" transparent="1">\n\t\t\t\t  <convert type="EventTime">StartTime</convert>\n\t\t\t\t  <convert type="ClockToText" />\n\t\t\t\t</widget>\n\t\t\t\t<widget source="Event" render="Label" position="400,47" size="100,25" font="Regular; 19" foregroundColor="#00e5b243" backgroundColor="#31000000" shadowColor="#000000" halign="left" transparent="1">\n\t\t\t\t  <convert type="EventTime">EndTime</convert>\n\t\t\t\t  <convert type="ClockToText">Format:- %H:%M</convert>\n\t\t\t\t</widget>\n\t\t\t\t<widget source="Event" render="Label" position="565,47" size="470,25" font="Regular; 18" foregroundColor="#0053a9ff" backgroundColor="#31000000" transparent="1" halign="left" noWrap="1">\n\t\t\t\t  <convert type="EventName">Name</convert>\n\t\t\t\t</widget>\n\n\t\t\t<widget source="Event" render="Label" position="460,47" size="113,25" font="Regular; 19" foregroundColor="#00ffffff" backgroundColor="#31000000" shadowColor="#000000" halign="center" transparent="1" text="1440 min">\n\t\t\t  <convert type="EventTime">Duration</convert>\n\t\t\t  <convert type="ClockToText">InMinutes</convert>\n\t\t\t</widget>\n\t\t\t\t<widget source="Event" render="Label" position="341,72" zPosition="1" size="860,116" font="Regular; 18" foregroundColor="#00bbbbbb" backgroundColor="#31000000" shadowColor="#000000" transparent="1" valign="top">\n\t\t\t\t  <convert type="EventName">ExtendedDescription</convert>\n\t\t\t\t</widget>\n\t\t\t\t<widget name="key_red" position="378,869" size="123,24" font="Regular; 17" foregroundColor="#aeaeae" backgroundColor="#000000" shadowColor="#000000" halign="left" valign="center" transparent="1" noWrap="1" />\n\t\t\t\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/openSPATVGuide/img/green.png" position="380,669" size="35,25" alphatest="blend" />\n\t\t\t\t<widget name="key_green" position="415,669" size="163,24" font="Regular; 17" foregroundColor="#aeaeae" backgroundColor="#000000" shadowColor="#000000" halign="left" valign="center" transparent="1" noWrap="1" />\n\t\t\t\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/openSPATVGuide/img/yellow.png" position="600,669" size="35,25" alphatest="blend" />\n\t\t\t\t<widget name="key_yellow" position="635,669" size="163,24" font="Regular; 17" foregroundColor="#aeaeae" backgroundColor="#000000" shadowColor="#000000" halign="left" valign="center" transparent="1" noWrap="1" />\n\t\t\t\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/openSPATVGuide/img/blue.png" position="800,669" size="35,25" alphatest="blend" />\n\t\t\t\t<widget name="key_blue" position="835,669" size="192,24" font="Regular; 17" foregroundColor="#aeaeae" backgroundColor="#000000" shadowColor="#000000" halign="left" valign="center" transparent="1" noWrap="1" />\n\t\t\t\n\t\t\t<eLabel backgroundColor="#101b22" position="80,224" size="297,105" zPosition="-2" />\n\t\t\t<!--<eLabel backgroundColor="#101b22" position="366,195" size="866,506" zPosition="-1" />-->\n\t\t\t\n\t\t\t<widget source="session.VideoPicture" render="Pig" position="40,19" size="295,163" zPosition="-1" backgroundColor="transparent2" />\n\t\t\t<eLabel name="tapapip" position="39,18" size="297,165" zPosition="-2" backgroundColor="#777777" />\n\t\t\t<widget source="session.CurrentService" render="Label" position="44,19" size="287,23" font="Regular; 17" transparent="1" valign="center" zPosition="6" backgroundColor="black" foregroundColor="#20ffffcc" noWrap="1" borderColor="#11000000" borderWidth="1">\n\t\t\t  <convert type="ServiceName">Name</convert>\n\t\t\t</widget>\n\t\t\t<eLabel name="tapainfocanal" position="40,19" size="295,23" backgroundColor="#66111111" foregroundColor="#2253a9ff" transparent="0" zPosition="0" />\n\t\t\t\n\t\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/openSPATVGuide/img/key_id.png" position="1052,669" size="48,25" alphatest="blend" />\n\n\t\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/openSPATVGuide/img/key_info.png" position="1110,669" size="35,25" alphatest="blend" />\n\t\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/openSPATVGuide/img/key_exit.png" position="1142,669" size="35,25" alphatest="blend" />\n\n\t\t<widget name="titinfo" position="90,242" size="286,70" font="Regular; 18" foregroundColor="#00e5b243" backgroundColor="#31000000" borderWidth="1" borderColor="#000000" halign="left" transparent="1" valign="center" zPosition="40" />\n\n\t<eLabel backgroundColor="#101b22" position="230,331" size="147,105" zPosition="-2" />\n\t<eLabel name="tapa_picon" position="238,351" size="40,62" zPosition="-1" backgroundColor="#101b22" />\t\n\t<eLabel name="marco_picon" position="252,351" size="102,62" zPosition="9" backgroundColor="#2b3949" />\t\n\t<widget name="img_picon" position="253,352" size="100,60" zPosition="10" transparent="1" />\n\t\t<widget name="barrapix" position="1195,209" zPosition="19" size="25,450" alphatest="blend" transparent="1" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/openSPATVGuide/img/scrollepgfs8.png" />\n\t<widget source="Event" render="Label" position="1194,164" size="47,25" font="Regular; 17" foregroundColor="#949494" transparent="0" halign="center" noWrap="1" zPosition="20" backgroundColor="#030813">\n\t  <convert type="EventRating">Rating</convert>\n\t</widget>\t\t\n\t<widget name="genero" position="971,47" size="270,25" zPosition="19" transparent="0" backgroundColor="#030813" font="Regular; 16" foregroundColor="#949494" halign="right" valign="bottom" noWrap="1" />\n\t<!--<widget name="genero_arr" position="1000,47" size="241,3" zPosition="20" transparent="0" backgroundColor="#030813" />-->\n\t<widget name="img_gen" position="1201,75" size="40,40" zPosition="10" transparent="1" alphatest="blend" />\n\n\t\t</screen>'

    def __init__(self, session, searchString = None, searchservice = None, searchSave = True, servicios = None, forzarcanal = False):
        Screen.__init__(self, session)
        self.skinName = ['EPGSearchOS']
        self.services = servicios
        if not self.services:
            self.services = getBouquetServices()
        self.searchString = searchString
        self.searchservice = searchservice
        self.searchSave = searchSave
        self.forzarcanal = forzarcanal
        self.currSearch = ''
        self.iniciadoS = False
        self['barrapix'] = Pixmap()
        self['img_gen'] = Pixmap()
        self['key_blue'] = Button(_('New Search'))
        self['key_yellow'] = Button(_('History'))
        self.bouquetChangeCB = None
        self.serviceChangeCB = None
        self.ask_time = -1
        self['key_red'] = Button('')
        self['titinfo'] = Label('')
        self['info'] = Label('')
        self['genero'] = Label()
        self['genero'].hide()
        self['img_picon'] = Pixmap()
        self.closeRecursive = False
        self.saved_title = None
        self['Service'] = ServiceEvent()
        self['Event'] = Event()
        self.type = EPG_TYPE_SINGLE
        self.currentService = None
        self.zapFunc = None
        self.sort_type = 0
        self['key_green'] = Button(_('Add timer'))
        self.key_green_choice = self.ADD_TIMER
        self.key_red_choice = self.EMPTY
        self.usearch = ''
        self['list'] = EPGSearchList(type=self.type, selChangedCB=self.onSelectionChanged, timer=session.nav.RecordTimer)
        self['actions'] = ActionMap(['EPGSelectActions', 'OkCancelActions', 'MenuActions'], {'menu': self.menu,
         'cancel': self.closeScreen,
         'ok': self.eventSelected,
         'timerAdd': self.timerAdd,
         'yellow': self.blueButtonPressed,
         'blue': self.kyellow,
         'info': self.infoKeyPressed,
         'red': self.zapTo,
         'nextBouquet': self.nextBouquet,
         'prevBouquet': self.prevBouquet,
         'nextService': self.nextService,
         'prevService': self.prevService})
        self['actions'].csel = self
        self.onLayoutFinish.append(self.onCreate)
        self.onShow.append(self.onInicio)
        try:
            self['list'].onSelChanged.append(self.actualizapicon)
        except:
            pass

        self.sservice = None
        self['info'].setText(_('Searching...'))
        self.timeractS = eTimer()
        self.timeractS.callback.append(self.actualizaRetS)

    def actualizaScrolls(self):
        try:
            if len(self['list'].list) <= 18:
                self['barrapix'].hide()
            else:
                self['barrapix'].show()
        except:
            self['barrapix'].hide()

    def timerAdd(self):
        cur = self['list'].getCurrent()
        event = cur[0]
        serviceref = cur[1]
        if event is None:
            return
        eventid = event.getEventId()
        refstr = serviceref.ref.toString()
        try:
            cret = serviceref.ref
            if cret.flags & eServiceReference.isGroup:
                xref = getBestPlayableServiceReference(cret, eServiceReference(), True)
                refstr = xref.toString()
        except:
            pass

        rec = isInTimer(self.session.nav.RecordTimer, eventid, event.getBeginTime(), event.getDuration(), refstr)
        try:
            nombre = rec.name
        except:
            nombre = _('Record')

        if rec is not None:
            cb_func = lambda ret: not ret or self.removeTimer(rec)
            self.session.openWithCallback(cb_func, MessageBox, _('Do you really want to delete %s?') % nombre)
        else:
            newEntry = RecordTimerEntry(serviceref, checkOldTimers=True, *parseEvent(event))
            self.session.openWithCallback(self.finishedAdd, TimerEntry, newEntry)

    def actualizapicon(self):
        self.timeractS.stop()
        self.timeractS.start(700, True)

    def actualizaRetS(self):
        self.timeractS.stop()
        self['img_gen'].hide()
        cur = self['list'].getCurrent()
        try:
            event = cur[0]
            if not event:
                self['genero'].hide()
            tuplagenero = getgenero(event, 70)
            ergenero = tuplagenero[0]
            if ergenero != '':
                self['genero'].setText(ergenero)
                self['genero'].show()
                if tuplagenero[2]:
                    self['img_gen'].instance.setPixmapFromFile(tuplagenero[2])
                    self['img_gen'].show()
            else:
                self['genero'].hide()
        except:
            self['genero'].hide()

        try:
            serviceref = cur[1]
            if not serviceref:
                return
            ref = serviceref.ref
            if ref.flags & eServiceReference.isGroup:
                ref = getBestPlayableServiceReference(ref, eServiceReference(), True)
            cual = rutapiconS(ref.toString())
            if fileExists(cual):
                self['img_picon'].instance.setPixmapFromFile(cual)
        except:
            pass

    def pontitulo(self):
        add = ''
        try:
            if self.sservice:
                add = ' [' + self.sservice.getServiceName() + ']'
        except:
            pass

        if self.usearch != '' and self.usearch:
            self['titinfo'].setText(_('Search:').replace(':', add + ':') + '\n' + self.usearch + '')
        else:
            self['titinfo'].setText(' ')
        self.setTitle(_('EPG Search'))

    def onCreate(self):
        self.setTitle(_('EPG Search'))
        l = self['list']
        l.recalcEntrySize()
        l.list = []
        l.l.setList(l.list)

    def onInicio(self):
        try:
            if self.searchString:
                self.inibusqueda(self.searchString, self.searchservice, self.searchSave)
                self.searchString = None
        except:
            pass

    def closeScreen(self):
        config.plugins.epgsearchOS.save()
        EPGSelection.closeScreen(self)

    def SpaSearchGen(self, encanal = False):
        askList = []
        nkeys = []
        anad = 'a'
        if encanal:
            anad = 'c'
        for ele in maintype:
            if ele != _('Reserved') and ele != _('Other'):
                askList.append((ele, anad + str(len(askList) + 1)))
                nkeys.append(str(len(askList) - 1))

        dei = self.session.openWithCallback(self.callbackGenre, ChoiceBox, keys=nkeys, title=_('Search by genre') + '.\n' + _('Select option') + ':', list=askList)

    def callbackGenre(self, answer = None):
        answer = answer and answer[1]
        if answer:
            resp = answer[1:]
            if int(resp) > 0:
                if answer[0:1] == 'a':
                    xservicio = None
                else:
                    if self.searchservice:
                        xservicio = self.searchservice
                    else:
                        xservicio = self.sservice
                    try:
                        cur = self['list'].getCurrent()
                        if cur[1]:
                            xservicio = cur[1]
                    except:
                        pass

                if self.usearch == None:
                    self.usearch = ''
                self.searchEPG(searchString=None, searchSave=False, searchGenre=resp, searchService=xservicio)
                return
        if self.usearch == None:
            self.close()

    def inibusqueda(self, searchString = None, searchservice = None, searchSave = True):
        if searchString == ':genero:':
            self.usearch = None
            self.SpaSearchGen(self.forzarcanal)
        elif searchString and searchString != '':
            self.sservice = None
            if searchString == 'xNAx':
                searchString = ''
            from Plugins.Extensions.spazeMenu.spzVirtualKeyboard import spzVirtualKeyboard
            add = ''
            try:
                if searchservice and self.forzarcanal:
                    self.sservice = searchservice
                    add = ' [' + searchservice.getServiceName() + ']'
            except:
                pass

            self.session.openWithCallback(self.searchEPG, spzVirtualKeyboard, titulo='EPG - ' + _('Enter text to search for') + add + ':', texto=searchString, ok=True)

    def MenuBuscar(self):
        nkeys = []
        askList = []
        askList.append((_('Search in EPG') + ' (' + _('All channels') + ')', 'epg'))
        nkeys.append('1')
        serviceref = self.searchservice
        try:
            cur = self['list'].getCurrent()
            if cur[1]:
                serviceref = cur[1]
        except:
            pass

        try:
            askList.append((_('Search in') + ' [' + serviceref.getServiceName() + ']', 'epgc'))
            nkeys.append('2')
        except:
            pass

        askList.append(('--', 'nada'))
        nkeys.append('')
        if self.services:
            askList.append((_('Search by genre') + ' (' + _('All channels') + ')', 'gen1'))
            nkeys.append('3')
        try:
            askList.append((_('Search by genre in') + ' [' + serviceref.getServiceName() + ']', 'gen2'))
            nkeys.append('4')
        except:
            pass

        dei = self.session.openWithCallback(self.callbackmenu, ChoiceBox, keys=nkeys, title=_('Search options') + '.\n' + _('Select option') + ':', list=askList)

    def callbackmenu(self, answer = None):
        answer = answer and answer[1]
        if answer:
            if answer == 'epg':
                self.sservice = None
                self.yellowButtonPressed()
            elif answer == 'epgc':
                self.yellowButtonPressed(True)
            elif answer == 'gen1':
                self.sservice = None
                self.SpaSearchGen()
            elif answer == 'gen2':
                self.sservice = None
                self.SpaSearchGen(True)

    def kyellow(self):
        self.MenuBuscar()

    def yellowButtonPressed(self, encanal = False):
        from Plugins.Extensions.spazeMenu.spzVirtualKeyboard import spzVirtualKeyboard
        add = ''
        if encanal:
            try:
                cur = self['list'].getCurrent()
                serviceref = cur[1]
                if serviceref:
                    self.sservice = serviceref
                    add = ' [' + self.sservice.getServiceName() + ']'
            except:
                pass

            try:
                if self.sservice:
                    add = ' [' + self.sservice.getServiceName() + ']'
            except:
                pass

        self.session.openWithCallback(self.searchEPG, spzVirtualKeyboard, titulo='EPG - ' + _('Enter text to search for') + add + ':', texto=self.usearch, ok=False)

    def menu(self):
        pass

    def menuCallback(self, ret):
        ret and ret[1]()

    def blueButtonPressed(self):
        options = [ (x, x) for x in config.plugins.epgsearchOS.history.value ]
        if options:
            self.session.openWithCallback(self.searchEPGWrapper, ChoiceBox, title=_('Select text to search for'), list=options)
        else:
            self.session.open(MessageBox, _('No history'), type=MessageBox.TYPE_INFO)

    def searchEPGWrapper(self, ret):
        if ret:
            self.searchEPG(ret[1])

    def searchEPG(self, searchString = None, searchSave = True, searchGenre = None, searchService = None):
        maximo = 400
        if searchString or searchGenre:
            self['info'].setText(_('Searching...'))
            searchservice = self.sservice
            self['list'].timer = self.session.nav.RecordTimer
            cual = rutapiconS('na')
            if fileExists(cual):
                self['img_picon'].instance.setPixmapFromFile(cual)
            if searchString:
                self.usearch = searchString
                self.currSearch = searchString
                if searchSave:
                    history = config.plugins.epgsearchOS.history.value
                    if searchString not in history:
                        history.insert(0, searchString)
                        maxLen = config.plugins.epgsearchOS.history_length.value
                        if len(history) > maxLen:
                            del history[maxLen:]
                    else:
                        history.remove(searchString)
                        history.insert(0, searchString)
                encoding = config.plugins.epgsearchOS.encoding.value
                if encoding != 'UTF-8':
                    try:
                        searchString = searchString.decode('UTF-8', 'replace').encode(encoding, 'replace')
                    except (UnicodeDecodeError, UnicodeEncodeError):
                        pass

                epgcache = eEPGCache.getInstance()
                ret = epgcache.search(('RIBDTW',
                 5000,
                 eEPGCache.PARTIAL_TITLE_SEARCH,
                 searchString,
                 eEPGCache.NO_CASE_CHECK)) or []
            else:
                epgcache = eEPGCache.getInstance()
                if not searchService and self.services:
                    test = [ (service.ref.toString(),
                     0,
                     -1,
                     -1) for service in self.services ]
                    test.insert(0, 'RIBDTW')
                else:
                    if searchService:
                        sservice = searchService
                    elif self.searchservice:
                        sservice = self.searchservice
                    else:
                        sservice = self.sservice
                    if sservice:
                        ref = sservice.ref
                        if ref.flags & eServiceReference.isGroup:
                            ref = getBestPlayableServiceReference(ref, eServiceReference(), True)
                        test = ['RIBDTW', (ref.toString(),
                          0,
                          -1,
                          -1)]
                    else:
                        self['info'].setText('--- ' + _('No matches found') + ' ---')
                        return
                ret = epgcache.lookupEvent(test)
            ret.sort(key=itemgetter(2))
            ret2 = []
            if searchservice:
                try:
                    ref = searchservice.ref
                    if ref.flags & eServiceReference.isGroup:
                        ref = getBestPlayableServiceReference(ref, eServiceReference(), True)
                    cad = ''
                    for ele in ret:
                        cad = cad + '\n' + str(ele[0])
                        if str(ref.toString()) == str(ele[0]):
                            ret2.append(ele)
                        if len(ret2) > maximo:
                            break

                except:
                    pass

            elif searchGenre:
                for ele in ret:
                    gen = ele[5]
                    if gen and int(gen[0][0]) == int(searchGenre):
                        ret2.append(ele)
                        if len(ret2) > maximo:
                            break

            else:
                for ele in ret:
                    ret2.append(ele)
                    if len(ret2) > maximo:
                        break

            l = self['list']
            l.recalcEntrySize()
            l.list = ret2
            l.l.setList(ret2)
            if len(ret2) <= 0:
                self['info'].setText(_('No matches found'))
            else:
                self['info'].setText(' ')
            try:
                self['list'].instance.moveSelectionTo(0)
            except:
                pass

            self.actualizaScrolls()
        elif self.usearch == '':
            self.close()
        if searchGenre:
            self.usearch = ''
            txto = _('Search by genre') + ':\n'
            try:
                txto = txto + maintype[int(searchGenre)]
            except:
                pass

            self['titinfo'].setText(txto)
        else:
            self.pontitulo()


from enigma import eServiceCenter, eServiceReference

def getBouquetServices(bouquet = None):
    if not bouquet:
        from Screens.InfoBar import InfoBar
        if InfoBar and InfoBar.instance:
            bouquet = InfoBar.instance.servicelist.getRoot()
        else:
            return
    services = []
    Servicelist = eServiceCenter.getInstance().list(bouquet)
    if Servicelist is not None:
        while True:
            service = Servicelist.getNext()
            if not service.valid():
                break
            if service.flags & (eServiceReference.isDirectory | eServiceReference.isMarker):
                continue
            services.append(ServiceReference(service))

    return services
