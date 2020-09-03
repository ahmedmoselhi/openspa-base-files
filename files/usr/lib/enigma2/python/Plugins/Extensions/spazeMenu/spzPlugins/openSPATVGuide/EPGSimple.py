from Components.config import config
from Screens import Standby
from os import system
from Tools.LoadPixmap import LoadPixmap
from Components.ActionMap import ActionMap
from Plugins.Plugin import PluginDescriptor
from enigma import eEPGCache, eListbox, gFont, eListboxPythonMultiContent, RT_HALIGN_LEFT, RT_HALIGN_RIGHT, RT_HALIGN_CENTER, RT_VALIGN_CENTER, RT_VALIGN_TOP, RT_WRAP, BT_SCALE, BT_KEEP_ASPECT_RATIO, eRect, getDesktop, eTimer, eServiceCenter, eServiceReference, getBestPlayableServiceReference
from ServiceReference import ServiceReference
from Screens.EpgSelection import EPGSelection
from Screens.InfoBarGenerics import SimpleServicelist
from Screens.TimerEdit import TimerSanityConflict
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Components.Pixmap import Pixmap
from Components.Label import Label, MultiColorLabel
from Screens.ChoiceBox import ChoiceBox
from Screens.EventView import EventViewBase
from Screens.TimerEntry import TimerEntry
from RecordTimer import RecordTimerEntry, parseEvent, AFTEREVENT
from Components.EpgList import EPGList, EPG_TYPE_SINGLE
from time import localtime, strftime, time
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaBlend
from Plugins.Extensions.spazeMenu.spzPlugins.openSPATVGuide.EPGSearch import EPGSearch, rutapiconS, isInTimer, getgenero, getcolorgenero, geticonogenero, getBouquetServices
from Plugins.Extensions.spazeMenu.plugin import esHD, fhd
from skin import parseColor, parseFont
from os import environ
import gettext
from Components.Language import language
from Tools.Directories import SCOPE_PLUGINS, SCOPE_LANGUAGE
from Tools.Directories import resolveFilename, SCOPE_CURRENT_SKIN, fileExists
lang = language.getLanguage()
environ['LANGUAGE'] = lang[:2]
lenguaje = str(lang[:2])
gettext.bindtextdomain('enigma2', resolveFilename(SCOPE_LANGUAGE))
gettext.textdomain('enigma2')
gettext.bindtextdomain('openSPATVGuide', '%s%s' % (resolveFilename(SCOPE_PLUGINS), 'Extensions/spazeMenu/spzPlugins/openSPATVGuide/locale/'))

def _(txt):
    t = gettext.dgettext('openSPATVGuide', txt)
    if t == txt:
        t = gettext.gettext(txt)
    return t


def formateafechacorta(lafecha = None, sepa = '/'):
    if not lafecha == None:
        t2 = lafecha
    else:
        t2 = localtime()
    cdia = str(strftime('%d', t2))
    cmes = str(strftime('%B', t2))
    csemana = _(str(strftime('%A', t2))).replace('\xc3\xa1', 'a').replace('\xc3\xa9', 'e').replace('\xc3\xad', 'i').replace('\xc3\xb3', 'o').replace('\xc3\xba', 'u')
    return csemana[0:3].capitalize() + '. ' + cdia


def formateafecha(lafecha = None, sepa = ' ' + _('of') + ' '):
    if not lafecha == None:
        t2 = lafecha
    else:
        t2 = localtime()
    cdia = str(strftime('%d', t2))
    cmes = str(strftime('%B', t2))
    cano = str(strftime('%Y', t2))
    csemana = str(strftime('%A', t2))
    return _(csemana).capitalize() + ', ' + cdia + sepa + _(cmes).capitalize() + sepa + cano


class SpaViewSimple(Screen, EventViewBase):

    def __init__(self, session, Event, Ref, callback = None, similarEPGCB = None):
        Screen.__init__(self, session)
        self.skinName = 'EventView'
        EventViewBase.__init__(self, Event, Ref, callback, similarEPGCB)
        self['key_blue'].setText(_('Search'))
        self['key_red'].setText(_('Internet info'))
        self['Spaman'] = ActionMap(['CTVGuideActions'], {'CBlue': self.SpaSearch,
         'CRed': self.SpaInet}, -6)

    def SpaInet(self):
        try:
            name = self.event.getEventName()
        except:
            name = ''

        try:
            from Plugins.Extensions.spzIMDB.plugin import spzIMDB
            spzIMDB(self.session, tbusqueda=name)
        except:
            pass

    def SpaSearch(self):
        try:
            name = self.event.getEventName()
        except:
            name = ''

        if name == '' or name.upper() == _('No Information').upper() or name.upper() == '(' + _('No Information').upper() + ')':
            name = 'xNAx'
        self.session.open(EPGSearch, name, False)


class spaEPGList(EPGList):

    def __init__(self, type = EPG_TYPE_SINGLE, selChangedCB = None, timer = None, sigenero = True):
        EPGList.__init__(self, type, selChangedCB, timer)
        self.oldfec = None
        self.orden = 0
        self.cambiado = True
        self.genero = sigenero
        self.colorDate = None
        self.colorDeactivated = None
        self.colorBegin = None
        self.colorDuration = None
        self.colorEvent = None
        self.sizeDate = None
        self.sizeBegin = None
        self.sizeDuration = None
        self.sizeEvent = None
        self.posBegin = None
        self.posDuration = None
        self.posEvent = None
        self.posyBegin = None
        self.posyDuration = None
        self.posyEvent = None
        self.sizey = None
        self.esFecha = None
        self.l.setFont(0, gFont('Regular', 19))
        self.l.setFont(1, gFont('Regular', 20))
        self.l.setFont(2, gFont('Regular', 21))
        self.l.setFont(3, gFont('Regular', 19))
        self.clock_pixmap = LoadPixmap(cached=True, path='/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/newChannelSelection/spzTeam/epgclock.png')
        self.clock_add_pixmap = LoadPixmap(cached=True, path='/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/newChannelSelection/spzTeam/epgclock_add.png')
        self.clock_pre_pixmap = LoadPixmap(cached=True, path='/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/newChannelSelection/spzTeam/epgclock_post.png')
        self.clock_post_pixmap = LoadPixmap(cached=True, path='/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/newChannelSelection/spzTeam/epgclock_pre.png')
        self.clock_prepost_pixmap = LoadPixmap(cached=True, path='/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/newChannelSelection/spzTeam/epgclock_prepost.png')
        self.clocks = [self.clock_add_pixmap,
         self.clock_pre_pixmap,
         self.clock_pixmap,
         self.clock_prepost_pixmap,
         self.clock_post_pixmap,
         LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_SKIN, 'skin_default/icons/zapclock_add.png')),
         LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_SKIN, 'skin_default/icons/zapclock_pre.png')),
         LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_SKIN, 'skin_default/icons/zapclock.png')),
         LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_SKIN, 'skin_default/icons/zapclock_prepost.png')),
         LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_SKIN, 'skin_default/icons/zapclock_post.png')),
         LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_SKIN, 'skin_default/icons/zaprecclock_add.png')),
         LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_SKIN, 'skin_default/icons/zaprecclock_pre.png')),
         LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_SKIN, 'skin_default/icons/zaprecclock.png')),
         LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_SKIN, 'skin_default/icons/zaprecclock_prepost.png')),
         LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_SKIN, 'skin_default/icons/zaprecclock_post.png')),
         LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_SKIN, 'skin_default/icons/repepgclock_add.png')),
         LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_SKIN, 'skin_default/icons/repepgclock_pre.png')),
         LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_SKIN, 'skin_default/icons/repepgclock.png')),
         LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_SKIN, 'skin_default/icons/repepgclock_prepost.png')),
         LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_SKIN, 'skin_default/icons/repepgclock_post.png')),
         LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_SKIN, 'skin_default/icons/repzapclock_add.png')),
         LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_SKIN, 'skin_default/icons/repzapclock_pre.png')),
         LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_SKIN, 'skin_default/icons/repzapclock.png')),
         LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_SKIN, 'skin_default/icons/repzapclock_prepost.png')),
         LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_SKIN, 'skin_default/icons/repzapclock_post.png')),
         LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_SKIN, 'skin_default/icons/repzaprecclock_add.png')),
         LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_SKIN, 'skin_default/icons/repzaprecclock_pre.png')),
         LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_SKIN, 'skin_default/icons/repzaprecclock.png')),
         LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_SKIN, 'skin_default/icons/repzaprecclock_prepost.png')),
         LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_SKIN, 'skin_default/icons/repzaprecclock_post.png'))]

    def formatTiempo(self, ertiempo, signo = None):
        csig = ''
        if signo:
            csig = '+'
        if ertiempo <= 60:
            ret = csig + '%d s' % ertiempo
        elif ertiempo / 60 < 60:
            ret = csig + '%d min' % (ertiempo / 60)
        elif ertiempo / 3600 > 24:
            ret = '>24h'
        elif ertiempo / 3600 > 9:
            ret = csig + '%dh' % (ertiempo / 3600)
        else:
            minutos = ' %dm' % (ertiempo % 3600 / 60)
            ret = csig + '%dh' % (ertiempo / 3600)
            if not minutos == ' 0m':
                ret = ret + minutos
        return ret

    def getSizeSkin(self, nombreatr, valordefecto):
        cret = valordefecto
        for attr, value in self.skinAttributes:
            if attr == nombreatr:
                cret = value

        aret = cret.split(';')
        if len(aret) <= 1:
            vret1 = 'Regular'
            vret2 = int(aret[0])
        else:
            vret1 = aret[0]
            vret2 = int(aret[1])
        return [vret1, vret2]

    def getColorSkin(self, nombreatr, valordefecto):
        for attr, value in self.skinAttributes:
            if attr == nombreatr:
                return value

        return valordefecto

    def devColor(self, ercolor):
        fincolor = parseColor(ercolor).argb()
        return fincolor

    def buildSingleEntry(self, service, eventId, beginTime, duration, EventName, elgenero = None):
        margen = 16
        coldur = 19
        test = ''
        add1 = 28
        postxt = 135 + margen + coldur
        if self.colorDate == None:
            self.colorDate = self.getColorSkin('colorDate', '#53a9ff')
            self.colorDeactivated = self.getColorSkin('colorDeactivated', '#777777')
            self.colorBegin = self.getColorSkin('colorBegin', '#e5b243')
            self.colorDuration = self.getColorSkin('colorDuration', '#999999')
            self.colorEvent = self.getColorSkin('colorEvent', '#ffffff')
            self.sizeDate = self.getSizeSkin('fontDate', '21')
            self.sizeBegin = self.getSizeSkin('fontBegin', '19')
            self.sizeDuration = self.getSizeSkin('fontDuration', '19')
            self.sizeEvent = self.getSizeSkin('fontEvent', '20')
            self.posBegin = int(self.getColorSkin('posBegin', str(margen - 2)))
            self.posDuration = int(self.getColorSkin('posDuration', str(155)))
            self.posEvent = int(self.getColorSkin('posEvent', str(postxt)))
            self.posyBegin = int(self.getColorSkin('posyBegin', '0'))
            self.posyDuration = int(self.getColorSkin('posyDuration', '0'))
            self.posyEvent = int(self.getColorSkin('posyEvent', '3'))
            self.sizey = int(self.getColorSkin('sizey', '25'))
            self.esFecha = int(self.getColorSkin('esFecha', '0'))
            self.l.setFont(0, gFont(self.sizeBegin[0], self.sizeBegin[1]))
            self.l.setFont(1, gFont(self.sizeEvent[0], self.sizeEvent[1]))
            self.l.setFont(2, gFont(self.sizeDate[0], self.sizeDate[1]))
            self.l.setFont(3, gFont(self.sizeDuration[0], self.sizeDuration[1]))
        if service == None and eventId == None and EventName == None:
            res = [None]
            if beginTime[0:4] == '-- (':
                res.append(MultiContentEntryText(pos=(5, 0), size=(840, self.sizey), font=2, flags=RT_HALIGN_LEFT, text=beginTime.replace('--', ''), color=self.devColor(self.colorDeactivated)))
            else:
                linea = ' ---------------------------------------------------------------------------------------------------------------------------------------------------------'
                png = LoadPixmap('/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/newChannelSelection/spzTeam/calendario.png')
                res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND,
                 0,
                 3,
                 21,
                 21,
                 png))
                res.append(MultiContentEntryText(pos=(22, 0), size=(840, self.sizey), font=2, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=beginTime + linea, color=self.devColor(self.colorDate)))
            return res
        clock_types = self.getClockTypesForEntry(service, eventId, beginTime, duration)
        r1 = self.weekday_rect
        r2 = self.datetime_rect
        r3 = self.descr_rect
        t = localtime(beginTime)
        res = [None]
        if beginTime <= time() and beginTime + duration >= time():
            ertiempo = beginTime + duration - time()
            timedisplay = self.formatTiempo(ertiempo, True)
        else:
            timedisplay = self.formatTiempo(duration)
        anchodur = 90 + (self.posDuration - fhd(155, 1.2))
        res.append(MultiContentEntryText(pos=(self.posBegin, self.posyBegin), size=(60 + add1 + 200, self.sizey), font=0, text='%02d:%02d' % (t[3], t[4]), flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, color=self.devColor(self.colorBegin)))
        res.append(MultiContentEntryText(pos=(self.posDuration - anchodur, self.posyDuration), size=(anchodur, self.sizey), font=3, flags=RT_HALIGN_RIGHT | RT_VALIGN_CENTER, text=timedisplay, color=self.devColor(self.colorDuration)))
        if clock_types:
            res.append(MultiContentEntryText(pos=(self.posEvent + fhd(20), self.posyEvent), size=(1040, self.sizey), font=1, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=test + EventName, color=self.devColor(self.colorEvent)))
            for i in range(len(clock_types)):
                res.append(MultiContentEntryPixmapAlphaBlend(pos=(fhd(postxt - 15 + 10 - 24 * i, 1.45), fhd(2)), size=(fhd(24), fhd(24)), png=self.clocks[clock_types[len(clock_types) - 1 - i]], flags=BT_SCALE | BT_KEEP_ASPECT_RATIO))

        else:
            res.append(MultiContentEntryText(pos=(self.posEvent, self.posyEvent), size=(1040, self.sizey), font=1, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=test + EventName, color=self.devColor(self.colorEvent)))
        if self.genero:
            try:
                if elgenero:
                    clock_pic = geticonogenero(elgenero[0][0], 23)
                    if clock_pic is not None:
                        png = LoadPixmap(cached=True, path=clock_pic)
                        res.append(MultiContentEntryPixmapAlphaBlend(pos=(fhd(793, 1.5), fhd(1)), size=(fhd(23, 1.7), fhd(23, 1.7)), png=png, flags=BT_SCALE | BT_KEEP_ASPECT_RATIO))
            except:
                pass

        return res

    def fillSingleEPG(self, service, maximo = 9999, dias = 0):
        if dias > 0:
            minutos = dias * 24 * 60
        else:
            minutos = -1
        if self.genero:
            test = ['RIBDTW', (service.ref.toString(),
              0,
              -1,
              minutos)]
        else:
            test = ['RIBDT', (service.ref.toString(),
              0,
              -1,
              minutos)]
        listatemp = self.queryEPG(test)
        if self.orden == 1:
            listatemp.sort(key=lambda x: (x[4] and x[4].lower(), x[3]))
        self.list = []
        oldfec = None
        conta = 0
        for ele in listatemp:
            if conta > maximo:
                break
            beginTime = ele[2]
            t = localtime(beginTime)
            fecha1 = '%2d.%02d' % (t[2], t[1])
            if fecha1 != oldfec and self.orden == 0:
                oldfec = fecha1
                tfor = formateafecha(t)
                if formateafecha() == tfor:
                    tfor = _('Today') + ' ' + tfor
                else:
                    try:
                        dia1 = strftime('%d', localtime())
                        dia2 = strftime('%d', t)
                        if int(dia2) == int(dia1) + 1:
                            tfor = _('Tomorrow') + ' ' + tfor
                    except:
                        pass

                self.list.append((None,
                 None,
                 tfor,
                 None,
                 None))
                conta = conta + 1
                if conta > maximo:
                    break
            self.list.append(ele)
            conta = conta + 1

        if len(self.list) == 0:
            self.list.append((None,
             None,
             '-- (' + _('No events available') + ') --',
             None,
             None))
        self.l.setList(self.list)
        self.selectionChanged()
        self.cambiado = True

    def infoKeyPressed(self):
        cur = self['list'].getCurrent()
        event = cur[0]
        service = cur[1]
        if event is not None:
            self.session.open(SpaViewSimple, event, service, self.eventViewCallback, self.openSimilarList)

    def sortSingleEPG(self, type):
        list = self.list
        if list:
            event_id = self.getSelectedEventId()
            if type == 1:
                self.orden = 1
            else:
                self.orden = 0
            self.fillSingleEPG(self.getCurrent()[1])
            self.moveToEventId(event_id)


class spaEPGSelection(EPGSelection):
    if esHD():
        skin = '\n\t\t\t <screen name="spaEPGSelection" position="0,0" size="1920,1080" backgroundColor="#030813" title="EPG" flags="wfNoBorder">\n \t\t\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/openSPATVGuide/Pic/imgcalHDfs8.png" position="352,280" size="192,189" alphatest="blend" zPosition="-2" />\n \t\t\t\t<widget source="Title" render="Label" position="858,28" size="640,34" font="Regular; 20" foregroundColor="#00c0c0c0" backgroundColor="#00113778" halign="center" transparent="0" valign="center" />\n \n \t\t\t\t<widget source="Event" render="Label" position="507,28" size="349,34" font="Regular;20" halign="left" foregroundColor="#000000" backgroundColor="#e5b243" transparent="0" valign="center">\n \t\t\t\t\t<convert type="EventTime">StartTime</convert>\n \t\t\t\t\t<convert type="ClockToText">Format: %A, %d</convert>\n \t\t\t\t</widget>\n \n \t\t\t\t<widget source="session.RecordState" render="Pixmap" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/openSPATVGuide/img/rec.png" position="1732,31" size="30,30" zPosition="3" alphatest="blend">\n \t\t\t\t\t<convert type="ConditionalShowHide" />\n \t\t\t\t</widget>\n \t\t\t\t<widget source="global.CurrentTime" render="Label" position="1711,28" size="150,34" font="Regular; 19" foregroundColor="#999999" backgroundColor="#132d53" shadowColor="#000000" halign="right" transparent="0" valign="center">\n \t\t\t\t\t<convert type="ClockToText">Default</convert>\n \t\t\t\t</widget>\n \t\t\t\t<widget source="global.CurrentTime" render="Label" position="1500,28" size="226,34" font="Regular; 19" foregroundColor="#999999" backgroundColor="#132d53" shadowColor="#000000" halign="right" transparent="0" valign="center" zPosition="1">\n \t\t\t\t\t<convert type="ClockToText">Format:%d-%b-%Y</convert>\n \t\t\t\t</widget>\n \n \t\t\t\t<widget name="list" position="570,313" size="1260,645" scrollbarMode="showNever" transparent="0" foregroundColor="#e0e0e0" backgroundColor="#101b21" backgroundColorSelected="#00e5b243" foregroundColorSelected="#000000" posyBegin="3" posDuration="230" posyDuration="2" posEvent="250" posyEvent="1" sizey="40" itemHeight="40" />\n \n \t\t\t\t<widget source="Event" render="Label" position="507,70" size="150,37" font="Regular; 19" foregroundColor="#00e5b243" backgroundColor="#31000000" shadowColor="#000000" halign="left" transparent="1">\n \t\t\t\t\t<convert type="EventTime">StartTime</convert>\n \t\t\t\t\t<convert type="ClockToText" />\n \t\t\t\t</widget>\n \t\t\t\t<widget source="Event" render="Label" position="600,70" size="150,37" font="Regular; 19" foregroundColor="#00e5b243" backgroundColor="#31000000" shadowColor="#000000" halign="left" transparent="1">\n \t\t\t\t\t<convert type="EventTime">EndTime</convert>\n \t\t\t\t\t<convert type="ClockToText">Format:- %H:%M</convert>\n \t\t\t\t</widget>\n \t\t\t\t<widget source="Event" render="Label" position="847,70" size="705,37" font="Regular; 18" foregroundColor="#0053a9ff" backgroundColor="#31000000" transparent="1" halign="left" noWrap="1">\n \t\t\t\t\t<convert type="EventName">Name</convert>\n \t\t\t\t</widget>\n \n \t\t\t\t<widget source="Event" render="Label" position="690,70" size="169,37" font="Regular; 19" foregroundColor="#00ffffff" backgroundColor="#31000000" shadowColor="#000000" halign="center" transparent="1" text="1440 min">\n \t\t\t\t\t<convert type="EventTime">Duration</convert>\n \t\t\t\t\t<convert type="ClockToText">InMinutes</convert>\n \t\t\t\t</widget>\n \t\t\t\t<widget source="Event" render="Label" position="511,108" zPosition="1" size="1290,174" font="Regular; 18" foregroundColor="#00bbbbbb" backgroundColor="#31000000" shadowColor="#000000" transparent="1" valign="top">\n \t\t\t\t\t<convert type="EventName">ExtendedDescription</convert>\n \t\t\t\t</widget>\n \n \t\t\t\t<widget name="key_red" position="567,1303" size="184,36" font="Regular; 17" foregroundColor="#aeaeae" backgroundColor="#000000" shadowColor="#000000" halign="left" valign="center" transparent="1" noWrap="1" />\n \n \t\t\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/greenHD.png" position="570,1001" size="52,37" alphatest="blend" />\n \t\t\t\t<widget name="key_green" position="627,1003" size="244,36" font="Regular; 17" foregroundColor="#aeaeae" backgroundColor="#000000" shadowColor="#000000" halign="left" valign="center" transparent="1" noWrap="1" />\n \t\t\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/yellowHD.png" position="892,1001" size="52,37" alphatest="blend" />\n \t\t\t\t<widget name="key_yellow" position="950,1003" size="244,36" font="Regular; 17" foregroundColor="#aeaeae" backgroundColor="#000000" shadowColor="#000000" halign="left" valign="center" transparent="1" noWrap="1" />\n \t\t\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/blueHD.png" position="1222,1001" size="52,37" alphatest="blend" />\n \t\t\t\t<widget name="key_blue" position="1280,1003" size="288,36" font="Regular; 17" foregroundColor="#aeaeae" backgroundColor="#000000" shadowColor="#000000" halign="left" valign="center" transparent="1" noWrap="1" />\n \n \t\t\t\t<eLabel position="120,471" size="447,157" backgroundColor="#101b22" zPosition="-2" />\n \t\t\t\t<!--<eLabel position="549,292" size="1299,759" backgroundColor="#101b22" zPosition="-1" transparent="0" />-->\n \n \t\t\t\t<widget source="session.VideoPicture" render="Pig" position="60,28" size="442,244" zPosition="-1" backgroundColor="transparent2" />\n \t\t\t\t<eLabel name="tapapip" position="58,27" size="445,247" zPosition="-2" backgroundColor="#777777" />\n \t\t\t\t<widget source="session.CurrentService" render="Label" position="66,28" size="430,34" font="Regular; 17" transparent="1" valign="center" zPosition="6" backgroundColor="black" foregroundColor="#20ffffcc" noWrap="1" borderColor="#11000000" borderWidth="1">\n \t\t\t\t\t<convert type="ServiceName">Name</convert>\n \t\t\t\t</widget>\n \t\t\t\t<eLabel name="tapainfocanal" position="60,28" size="442,34" backgroundColor="#66111111" foregroundColor="#2253a9ff" transparent="0" zPosition="0" />\n \n \t\t\t\t<!--<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/openSPATVGuide/img/key_id.png" position="1654,1003" size="72,37" alphatest="blend" />-->\n \n \t\t\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/infoHD.png" position="1719,1003" size="52,37" alphatest="blend" />\n \t\t\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/exitHD.png" position="1767,1003" size="52,37" alphatest="blend" />\n \n \t\t\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/izqHD.png" position="1447,1001" size="52,37" alphatest="blend" />\n \t\t\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/dchaHD.png" position="1500,1001" size="52,37" alphatest="blend" />\n \t\t\t\t<widget name="key_rw" position="1560,1003" size="60,36" font="Regular; 17" foregroundColor="#aeaeae" backgroundColor="#000000" shadowColor="#000000" halign="left" valign="center" transparent="1" noWrap="1" />\n \t\t\t\t<eLabel name="smenos1" position="1543,1029" size="12,3" transparent="0" backgroundColor="#aeaeae" zPosition="21" />\n \t\t\t\t<eLabel name="smas1" position="1542,1002" size="25,25" text="+" transparent="1" foregroundColor="#aeaeae" zPosition="21" halign="left" font="Regular; 17" valign="center" />\t\n \n \t\t\t\t<widget source="Service" render="Label" position="126,481" size="421,139" font="Regular; 20" foregroundColor="#00ffffff" backgroundColor="#31000000" borderWidth="2" borderColor="#000000" halign="right" transparent="1" valign="center" zPosition="40" noWrap="1">\n \t\t\t\t\t<convert type="ServiceName">Name</convert>\n \t\t\t\t</widget>\n \n \t\t\t\t<eLabel backgroundColor="#101b22" position="345,631" size="222,157" zPosition="-2" />\n \t\t\t\t<eLabel name="tapa_picon" position="357,661" size="60,93" zPosition="-1" backgroundColor="#101b22" />\t\n \t\t\t\t<eLabel name="marco_picon" position="378,661" size="153,93" zPosition="9" backgroundColor="#2b3949" />\t\n \t\t\t\t<widget name="img_picon" position="379,663" size="150,90" zPosition="10" transparent="1" />\n \t\t\t\t<widget name="dia" position="375,369" size="144,75" font="Regular; 40" foregroundColor="#000000" backgroundColor="#c0c0c0" halign="center" transparent="1" valign="center" />\t\n \t\t\t\t<widget name="mes" position="367,309" size="163,30" font="Regular; 19" foregroundColor="#ffffff" backgroundColor="#31000000" halign="center" transparent="1" valign="top" />\n \n \t\t\t\t<widget name="semana1" position="370,343" size="21,25" font="Regular; 15" foregroundColors="#7a7a7a,#ffffff" backgroundColors="#b0b0b0,#7b1d15" backgroundColor="#777777" halign="center" valign="top" transparent="1" foregroundColor="#a0a0a0" zPosition="10" />\t\n \t\t\t\t<widget name="semana2" position="393,343" size="21,25" font="Regular; 15" foregroundColors="#7a7a7a,#ffffff" backgroundColors="#b0b0b0,#7b1d15" backgroundColor="#777777" halign="center" valign="top" transparent="1" foregroundColor="#a0a0a0" zPosition="10" />\n \t\t\t\t<widget name="semana3" position="415,343" size="21,25" font="Regular; 15" foregroundColors="#7a7a7a,#ffffff" backgroundColors="#b0b0b0,#7b1d15" backgroundColor="#777777" halign="center" valign="top" transparent="1" foregroundColor="#a0a0a0" zPosition="10" />\n \t\t\t\t<widget name="semana4" position="438,343" size="21,25" font="Regular; 15" foregroundColors="#7a7a7a,#ffffff" backgroundColors="#b0b0b0,#7b1d15" backgroundColor="#777777" halign="center" valign="top" transparent="1" foregroundColor="#a0a0a0" zPosition="10" />\n \t\t\t\t<widget name="semana5" position="460,343" size="21,25" font="Regular; 15" foregroundColors="#7a7a7a,#ffffff" backgroundColors="#b0b0b0,#7b1d15" backgroundColor="#777777" halign="center" valign="top" transparent="1" foregroundColor="#a0a0a0" zPosition="10" />\n \t\t\t\t<widget name="semana6" position="484,343" size="21,25" font="Regular; 15" foregroundColors="#7a7a7a,#ffffff" backgroundColors="#b0b0b0,#7b1d15" backgroundColor="#777777" halign="center" valign="top" transparent="1" foregroundColor="#a0a0a0" zPosition="10" />\n \t\t\t\t<widget name="semana7" position="507,343" size="21,25" font="Regular; 15" foregroundColors="#7a7a7a,#ffffff" backgroundColors="#b0b0b0,#7b1d15" backgroundColor="#777777" halign="center" valign="top" transparent="1" foregroundColor="#a0a0a0" zPosition="10" />\n \n \t\t\t\t<widget name="fsemana1" position="370,346" size="21,22" font="Regular; 16" foregroundColors="#7a7a7a,#ffffff" backgroundColors="#b0b0b0,#7b1d15" backgroundColor="#555555" halign="center" valign="top" transparent="0" foregroundColor="#a0a0a0" />\t\n \t\t\t\t<widget name="fsemana2" position="393,346" size="21,22" font="Regular; 16" foregroundColors="#7a7a7a,#ffffff" backgroundColors="#b0b0b0,#7b1d15" backgroundColor="#555555" halign="center" valign="top" transparent="0" foregroundColor="#a0a0a0" />\n \t\t\t\t<widget name="fsemana3" position="415,346" size="21,22" font="Regular; 16" foregroundColors="#7a7a7a,#ffffff" backgroundColors="#b0b0b0,#7b1d15" backgroundColor="#555555" halign="center" valign="top" transparent="0" foregroundColor="#a0a0a0" />\n \t\t\t\t<widget name="fsemana4" position="438,346" size="21,22" font="Regular; 16" foregroundColors="#7a7a7a,#ffffff" backgroundColors="#b0b0b0,#7b1d15" backgroundColor="#555555" halign="center" valign="top" transparent="0" foregroundColor="#a0a0a0" />\n \t\t\t\t<widget name="fsemana5" position="460,346" size="21,22" font="Regular; 16" foregroundColors="#7a7a7a,#ffffff" backgroundColors="#b0b0b0,#7b1d15" backgroundColor="#555555" halign="center" valign="top" transparent="0" foregroundColor="#a0a0a0" />\n \t\t\t\t<widget name="fsemana6" position="484,346" size="21,22" font="Regular; 16" foregroundColors="#7a7a7a,#ffffff" backgroundColors="#b0b0b0,#7b1d15" backgroundColor="#555555" halign="center" valign="top" transparent="0" foregroundColor="#a0a0a0" />\n \t\t\t\t<widget name="fsemana7" position="507,346" size="21,22" font="Regular; 16" foregroundColors="#7a7a7a,#ffffff" backgroundColors="#b0b0b0,#7b1d15" backgroundColor="#555555" halign="center" valign="top" transparent="0" foregroundColor="#a0a0a0" />\t\n \n \t\t\t\t<!--<widget name="barrapix" position="1792,313" zPosition="19" size="37,675" alphatest="blend" transparent="1" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/openSPATVGuide/img/scrollepgfs8.png" />-->\n \n \t\t\t\t<widget name="sitimer" position="820,28" size="36,36" zPosition="25" alphatest="blend" />\n \t\t\t\t<widget source="Event" render="Label" position="1791,246" size="70,37" font="Regular; 17" foregroundColor="#949494" transparent="0" halign="center" noWrap="1" zPosition="20" backgroundColor="#030813">\n \t\t\t\t\t<convert type="EventRating">Rating</convert>\n \t\t\t\t</widget>\n \t\t\t\t<widget name="genero" position="1456,70" size="405,37" zPosition="16" transparent="0" backgroundColor="#030813" font="Regular; 17" foregroundColor="#949494" halign="right" valign="bottom" noWrap="1" />\n \t\t\t\t<widget name="img_gen" position="1801,112" size="60,60" zPosition="10" transparent="1" alphatest="blend" />\n \n \t\t\t\t<!--<widget name="genero_arr" position="1500,70" size="361,4" zPosition="20" transparent="0" backgroundColor="#030813" />-->\n \t\t\t</screen>'
    else:
        skin = '\n\t\t\t<screen name="spaEPGSelection" position="0,0" size="1281,721" backgroundColor="#030813" title="EPG" flags="wfNoBorder">\n\t\t\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/openSPATVGuide/Pic/imgcalfs8.png" position="235,187" size="128,126" alphatest="blend" zPosition="-2" />\n\t\t\t\t<widget source="Title" render="Label" position="572,19" size="427,23" font="Regular; 20" foregroundColor="#00c0c0c0" backgroundColor="#00113778" halign="center" transparent="0" valign="center" />\n\n\t\t\t\t<widget source="Event" render="Label" position="338,19" size="233,23" font="Regular;20" halign="left" foregroundColor="#000000" backgroundColor="#e5b243" transparent="0" valign="center">\n\t\t\t\t\t<convert type="EventTime">StartTime</convert>\n\t\t\t\t\t<convert type="ClockToText">Format: %A, %d</convert>\n\t\t\t\t</widget>\n\n\t\t\t\t<widget source="session.RecordState" render="Pixmap" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/openSPATVGuide/img/rec.png" position="1155,21" size="20,20" zPosition="3" alphatest="blend">\n\t\t\t\t\t<convert type="ConditionalShowHide" />\n\t\t\t\t</widget>\n\t\t\t\t<widget source="global.CurrentTime" render="Label" position="1141,19" size="100,23" font="Regular; 19" foregroundColor="#999999" backgroundColor="#132d53" shadowColor="#000000" halign="right" transparent="0" valign="center">\n\t\t\t\t\t<convert type="ClockToText">Default</convert>\n\t\t\t\t</widget>\n\t\t\t\t<widget source="global.CurrentTime" render="Label" position="1000,19" size="151,23" font="Regular; 19" foregroundColor="#999999" backgroundColor="#132d53" shadowColor="#000000" halign="right" transparent="0" valign="center" zPosition="1">\n\t\t\t\t\t<convert type="ClockToText">Format:%d-%b-%Y</convert>\n\t\t\t\t</widget>\n\n\t\t\t\t<widget name="list" position="380,209" size="840,450" scrollbarMode="showOnDemand" transparent="0" itemHeight="25" foregroundColor="#e0e0e0" backgroundColor="#101b21" backgroundColorSelected="#00e5b243" foregroundColorSelected="#000000" />\n\n\t\t\t\t<widget source="Event" render="Label" position="338,47" size="100,25" font="Regular; 19" foregroundColor="#00e5b243" backgroundColor="#31000000" shadowColor="#000000" halign="left" transparent="1">\n\t\t\t\t\t<convert type="EventTime">StartTime</convert>\n\t\t\t\t\t<convert type="ClockToText" />\n\t\t\t\t</widget>\n\t\t\t\t<widget source="Event" render="Label" position="400,47" size="100,25" font="Regular; 19" foregroundColor="#00e5b243" backgroundColor="#31000000" shadowColor="#000000" halign="left" transparent="1">\n\t\t\t\t\t<convert type="EventTime">EndTime</convert>\n\t\t\t\t\t<convert type="ClockToText">Format:- %H:%M</convert>\n\t\t\t\t</widget>\n\t\t\t\t<widget source="Event" render="Label" position="565,47" size="470,25" font="Regular; 18" foregroundColor="#0053a9ff" backgroundColor="#31000000" transparent="1" halign="left" noWrap="1">\n\t\t\t\t\t<convert type="EventName">Name</convert>\n\t\t\t\t</widget>\n\n\t\t\t\t<widget source="Event" render="Label" position="460,47" size="113,25" font="Regular; 19" foregroundColor="#00ffffff" backgroundColor="#31000000" shadowColor="#000000" halign="center" transparent="1" text="1440 min">\n\t\t\t\t\t<convert type="EventTime">Duration</convert>\n\t\t\t\t\t<convert type="ClockToText">InMinutes</convert>\n\t\t\t\t</widget>\n\t\t\t\t<widget source="Event" render="Label" position="341,72" zPosition="1" size="860,116" font="Regular; 18" foregroundColor="#00bbbbbb" backgroundColor="#31000000" shadowColor="#000000" transparent="1" valign="top">\n\t\t\t\t\t<convert type="EventName">ExtendedDescription</convert>\n\t\t\t\t</widget>\n\n\t\t\t\t<widget name="key_red" position="378,869" size="123,24" font="Regular; 17" foregroundColor="#aeaeae" backgroundColor="#000000" shadowColor="#000000" halign="left" valign="center" transparent="1" noWrap="1" />\n\n\t\t\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/openSPATVGuide/img/green.png" position="380,669" size="35,25" alphatest="blend" />\n\t\t\t\t<widget name="key_green" position="415,669" size="163,24" font="Regular; 17" foregroundColor="#aeaeae" backgroundColor="#000000" shadowColor="#000000" halign="left" valign="center" transparent="1" noWrap="1" />\n\t\t\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/openSPATVGuide/img/yellow.png" position="595,669" size="35,25" alphatest="blend" />\n\t\t\t\t<widget name="key_yellow" position="630,669" size="163,24" font="Regular; 17" foregroundColor="#aeaeae" backgroundColor="#000000" shadowColor="#000000" halign="left" valign="center" transparent="1" noWrap="1" />\n\t\t\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/openSPATVGuide/img/blue.png" position="815,669" size="35,25" alphatest="blend" />\n\t\t\t\t<widget name="key_blue" position="850,669" size="192,24" font="Regular; 17" foregroundColor="#aeaeae" backgroundColor="#000000" shadowColor="#000000" halign="left" valign="center" transparent="1" noWrap="1" />\n\n\t\t\t\t<eLabel position="80,314" size="298,105" backgroundColor="#101b22" zPosition="-2" />\n\t\t\t\t<!--<eLabel position="366,195" size="866,506" backgroundColor="#101b22" zPosition="-1" transparent="0" />-->\n\n\t\t\t\t<widget source="session.VideoPicture" render="Pig" position="40,19" size="295,163" zPosition="-1" backgroundColor="transparent2" />\n\t\t\t\t<eLabel name="tapapip" position="39,18" size="297,165" zPosition="-2" backgroundColor="#777777" />\n\t\t\t\t<widget source="session.CurrentService" render="Label" position="44,19" size="287,23" font="Regular; 17" transparent="1" valign="center" zPosition="6" backgroundColor="black" foregroundColor="#20ffffcc" noWrap="1" borderColor="#11000000" borderWidth="1">\n\t\t\t\t\t<convert type="ServiceName">Name</convert>\n\t\t\t\t</widget>\n\t\t\t\t<eLabel name="tapainfocanal" position="40,19" size="295,23" backgroundColor="#66111111" foregroundColor="#2253a9ff" transparent="0" zPosition="0" />\n\n\t\t\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/openSPATVGuide/img/key_id.png" position="1103,669" size="48,25" alphatest="blend" />\n\n\t\t\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/openSPATVGuide/img/key_info.png" position="1146,669" size="35,25" alphatest="blend" />\n\t\t\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/openSPATVGuide/img/key_exit.png" position="1178,669" size="35,25" alphatest="blend" />\n\n\t\t\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/openSPATVGuide/img/key_rw.png" position="965,669" size="63,25" alphatest="blend" />\n\t\t\t\t<widget name="key_rw" position="1040,669" size="40,24" font="Regular; 17" foregroundColor="#aeaeae" backgroundColor="#000000" shadowColor="#000000" halign="left" valign="center" transparent="1" noWrap="1" />\n\t\t\t\t<eLabel name="smenos1" position="1029,686" size="8,2" transparent="0" backgroundColor="#aeaeae" zPosition="21" />\n\t\t\t\t<eLabel name="smas1" position="1028,668" size="17,17" text="+" transparent="1" foregroundColor="#aeaeae" zPosition="21" halign="left" font="Regular; 17" valign="center" />\t\n\n\t\t\t\t<widget source="Service" render="Label" position="84,321" size="281,93" font="Regular; 20" foregroundColor="#00ffffff" backgroundColor="#31000000" borderWidth="2" borderColor="#000000" halign="right" transparent="1" valign="center" zPosition="40" noWrap="1">\n\t\t\t\t\t<convert type="ServiceName">Name</convert>\n\t\t\t\t</widget>\n\n\t\t\t\t<eLabel backgroundColor="#101b22" position="230,421" size="148,105" zPosition="-2" />\n\t\t\t\t<eLabel name="tapa_picon" position="238,441" size="40,62" zPosition="-1" backgroundColor="#101b22" />\t\n\t\t\t\t<eLabel name="marco_picon" position="252,441" size="102,62" zPosition="9" backgroundColor="#2b3949" />\t\n\t\t\t\t<widget name="img_picon" position="253,442" size="100,60" zPosition="10" transparent="1" />\n\t\t\t\t<widget name="dia" position="250,246" size="96,50" font="Regular; 40" foregroundColor="#000000" backgroundColor="#c0c0c0" halign="center" transparent="1" valign="center" />\t\n\t\t\t\t<widget name="mes" position="245,206" size="109,20" font="Regular; 19" foregroundColor="#ffffff" backgroundColor="#31000000" halign="center" transparent="1" valign="top" />\n\n\t\t\t\t<widget name="semana1" position="247,229" size="14,17" font="Regular; 15" foregroundColors="#7a7a7a,#ffffff" backgroundColors="#b0b0b0,#7b1d15" backgroundColor="#777777" halign="center" valign="top" transparent="1" foregroundColor="#a0a0a0" zPosition="10" />\t\n\t\t\t\t<widget name="semana2" position="262,229" size="14,17" font="Regular; 15" foregroundColors="#7a7a7a,#ffffff" backgroundColors="#b0b0b0,#7b1d15" backgroundColor="#777777" halign="center" valign="top" transparent="1" foregroundColor="#a0a0a0" zPosition="10" />\n\t\t\t\t<widget name="semana3" position="277,229" size="14,17" font="Regular; 15" foregroundColors="#7a7a7a,#ffffff" backgroundColors="#b0b0b0,#7b1d15" backgroundColor="#777777" halign="center" valign="top" transparent="1" foregroundColor="#a0a0a0" zPosition="10" />\n\t\t\t\t<widget name="semana4" position="292,229" size="14,17" font="Regular; 15" foregroundColors="#7a7a7a,#ffffff" backgroundColors="#b0b0b0,#7b1d15" backgroundColor="#777777" halign="center" valign="top" transparent="1" foregroundColor="#a0a0a0" zPosition="10" />\n\t\t\t\t<widget name="semana5" position="307,229" size="14,17" font="Regular; 15" foregroundColors="#7a7a7a,#ffffff" backgroundColors="#b0b0b0,#7b1d15" backgroundColor="#777777" halign="center" valign="top" transparent="1" foregroundColor="#a0a0a0" zPosition="10" />\n\t\t\t\t<widget name="semana6" position="323,229" size="14,17" font="Regular; 15" foregroundColors="#7a7a7a,#ffffff" backgroundColors="#b0b0b0,#7b1d15" backgroundColor="#777777" halign="center" valign="top" transparent="1" foregroundColor="#a0a0a0" zPosition="10" />\n\t\t\t\t<widget name="semana7" position="338,229" size="14,17" font="Regular; 15" foregroundColors="#7a7a7a,#ffffff" backgroundColors="#b0b0b0,#7b1d15" backgroundColor="#777777" halign="center" valign="top" transparent="1" foregroundColor="#a0a0a0" zPosition="10" />\n\n\t\t\t\t<widget name="fsemana1" position="247,231" size="14,15" font="Regular; 16" foregroundColors="#7a7a7a,#ffffff" backgroundColors="#b0b0b0,#7b1d15" backgroundColor="#555555" halign="center" valign="top" transparent="0" foregroundColor="#a0a0a0" />\t\n\t\t\t\t<widget name="fsemana2" position="262,231" size="14,15" font="Regular; 16" foregroundColors="#7a7a7a,#ffffff" backgroundColors="#b0b0b0,#7b1d15" backgroundColor="#555555" halign="center" valign="top" transparent="0" foregroundColor="#a0a0a0" />\n\t\t\t\t<widget name="fsemana3" position="277,231" size="14,15" font="Regular; 16" foregroundColors="#7a7a7a,#ffffff" backgroundColors="#b0b0b0,#7b1d15" backgroundColor="#555555" halign="center" valign="top" transparent="0" foregroundColor="#a0a0a0" />\n\t\t\t\t<widget name="fsemana4" position="292,231" size="14,15" font="Regular; 16" foregroundColors="#7a7a7a,#ffffff" backgroundColors="#b0b0b0,#7b1d15" backgroundColor="#555555" halign="center" valign="top" transparent="0" foregroundColor="#a0a0a0" />\n\t\t\t\t<widget name="fsemana5" position="307,231" size="14,15" font="Regular; 16" foregroundColors="#7a7a7a,#ffffff" backgroundColors="#b0b0b0,#7b1d15" backgroundColor="#555555" halign="center" valign="top" transparent="0" foregroundColor="#a0a0a0" />\n\t\t\t\t<widget name="fsemana6" position="323,231" size="14,15" font="Regular; 16" foregroundColors="#7a7a7a,#ffffff" backgroundColors="#b0b0b0,#7b1d15" backgroundColor="#555555" halign="center" valign="top" transparent="0" foregroundColor="#a0a0a0" />\n\t\t\t\t<widget name="fsemana7" position="338,231" size="14,15" font="Regular; 16" foregroundColors="#7a7a7a,#ffffff" backgroundColors="#b0b0b0,#7b1d15" backgroundColor="#555555" halign="center" valign="top" transparent="0" foregroundColor="#a0a0a0" />\t\n\n\t\t\t\t<widget name="barrapix" position="1195,209" zPosition="19" size="25,450" alphatest="blend" transparent="1" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/openSPATVGuide/img/scrollepgfs8.png" />\n\n\t\t\t\t<widget name="sitimer" position="547,19" size="24,24" zPosition="25" alphatest="blend" />\n\t\t\t\t<widget source="Event" render="Label" position="1194,164" size="47,25" font="Regular; 17" foregroundColor="#949494" transparent="0" halign="center" noWrap="1" zPosition="20" backgroundColor="#030813">\n\t\t\t\t\t<convert type="EventRating">Rating</convert>\n\t\t\t\t</widget>\n\t\t\t\t<widget name="genero" position="971,47" size="270,25" zPosition="16" transparent="0" backgroundColor="#030813" font="Regular; 17" foregroundColor="#949494" halign="right" valign="bottom" noWrap="1" />\n\t\t\t\t<widget name="img_gen" position="1201,75" size="40,40" zPosition="10" transparent="1" alphatest="blend" />\n\n\t\t\t\t<!--<widget name="genero_arr" position="1000,47" size="241,3" zPosition="20" transparent="0" backgroundColor="#030813" />-->\n\t\t\t</screen>'

    def __init__(self, session, service = None, zapFunc = None, eventid = None, bouquetChangeCB = None, serviceChangeCB = None):
        if not service:
            service = session.nav.getCurrentlyPlayingServiceReference()
        EPGSelection.__init__(self, session, service, zapFunc, eventid, bouquetChangeCB, serviceChangeCB)
        self.skinName = ['spaEPGSelection']
        self['key_blue'].setText(_('Search'))
        self['list'] = spaEPGList(type=EPG_TYPE_SINGLE, selChangedCB=self.spaonSelectionChanged, timer=session.nav.RecordTimer)
        self['actions1'] = ActionMap(['CTVGuideActions', 'ColorActions', 'EPGSelectActions'], {'Cpvr': self.closeScreen,
         'CBlue': self.MenuBuscar,
         'blue': self.MenuBuscar,
         'CBack': self.prevPressed,
         'CFwd': self.nextPressed,
         'C7': self.prevPressed,
         'C9': self.nextPressed,
         'C1': self.gotop}, -2)
        self['sitimer'] = Pixmap()
        self['sitimer'].hide()
        self['barrapix'] = Pixmap()
        self['barrapix'].hide()
        self['img_picon'] = Pixmap()
        self['img_gen'] = Pixmap()
        self['key_rw'] = Label(_('Day'))
        self['dia'] = Label('')
        self['genero'] = Label()
        self['genero'].hide()
        self['mes'] = Label('')
        self.days = [_('Monday'),
         _('Tuesday'),
         _('Wednesday'),
         _('Thursday'),
         _('Friday'),
         _('Saturday'),
         _('Sunday')]
        for ele in range(1, 8):
            erdia = _(self.days[ele - 1])
            self['semana' + str(ele)] = MultiColorLabel(erdia[0])
            self['fsemana' + str(ele)] = MultiColorLabel(' ')

        self.antdia = None
        self.ufecha = None
        self.timeract = eTimer()
        self.timeract.callback.append(self.actualizaRet)
        self.onLayoutFinish.append(self.actualizapicon)

    def actualizapicon(self):
        try:
            self.setTitle('EPG - ' + self.currentService.getServiceName())
        except:
            pass

        try:
            serviceref = self.currentService
            if not serviceref:
                return
            ref = serviceref.ref
            if ref.flags & eServiceReference.isGroup:
                ref = getBestPlayableServiceReference(ref, eServiceReference(), True)
            cual = rutapiconS(ref.toString())
            if fileExists(cual):
                self['img_picon'].instance.setScale(1)
                self['img_picon'].instance.setPixmapFromFile(cual)
        except:
            pass

        self.actualizaScrolls()

    def actualizaScrolls(self):
        try:
            if len(self['list'].list) <= 18:
                self['barrapix'].hide()
            else:
                self['barrapix'].show()
        except:
            self['barrapix'].hide()

    def prevPressed(self):
        if self['list'].orden != 0:
            return
        try:
            lalista = self['list'].list
            length = len(lalista)
            if length > 1:
                idx = self['list'].instance.getCurrentIndex()
                conta = idx - 2
                for ele in range(0, idx):
                    if conta < 0:
                        break
                    if lalista[conta][0] == None:
                        self['list'].instance.moveSelectionTo(conta)
                        break
                    conta = conta - 1

                if idx == self['list'].instance.getCurrentIndex():
                    self['list'].instance.moveSelectionTo(length - 1)
                    conta = length - 1
                    for ele in range(0, length - 1):
                        if conta < 0:
                            break
                        if lalista[conta][0] == None:
                            self['list'].instance.moveSelectionTo(conta)
                            break
                        conta = conta - 1

        except:
            pass

    def nextPressed(self):
        if self['list'].orden != 0:
            return
        try:
            lalista = self['list'].list
            length = len(lalista)
            if length > 1:
                idx = self['list'].instance.getCurrentIndex()
                for ele in range(idx + 1, length):
                    if lalista[ele][0] == None:
                        self['list'].instance.moveSelectionTo(ele)
                        break

                if idx == self['list'].instance.getCurrentIndex():
                    self.gotop()
        except:
            pass

    def removeTimer(self, timer):
        timer.afterEvent = AFTEREVENT.NONE
        self.session.nav.RecordTimer.removeEntry(timer)
        self.actualizainfo()

    def timerAdd(self):
        cur = self['list'].getCurrent()
        event = cur[0]
        ref = cur[1]
        if not ref or not event:
            return
        serviceref = ref
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
                    self.session.openWithCallback(self.finishSanityCorrection, TimerSanityConflict, simulTimerList)
                    return
            self.actualizainfo()

    def spaonSelectionChanged(self):
        if self['list'].cambiado:
            self.actualizaScrolls()
        self.onSelectionChanged()
        self.actualizainfo()
        self['list'].cambiado = False

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

    def actualizaclock(self, ref, event):
        serviceref = ref
        if event is None or ref is None:
            return
        eventid = event.getEventId()
        refstr = serviceref.ref.toString()
        tiporec = self.egetClockPixmap(refstr, event.getBeginTime(), event.getDuration(), eventid, refstr)
        if tiporec > 0:
            nomrec = 'epgclock'
            if tiporec == 2:
                nomrec = 'epgclock_pre'
            if tiporec == 3:
                nomrec = 'epgclock_post'
            if tiporec == 4:
                nomrec = 'epgclock_add'
            if tiporec == 5:
                nomrec = 'epgclock_prepost'
            self['sitimer'].instance.setPixmapFromFile('/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/newChannelSelection/spzTeam/' + nomrec + '.png')
            self['sitimer'].show()
            return
        self['sitimer'].hide()

    def actualizainfo(self):
        self.timeract.stop()
        self['sitimer'].hide()
        cur = self['list'].getCurrent()
        event = cur[0]
        ref = cur[1]
        self['img_gen'].hide()
        self['genero'].hide()
        if not ref or not event:
            return
        self.timeract.stop()
        self.timeract.start(700, True)

    def actualizaRet(self):
        self.timeract.stop()
        self['sitimer'].hide()
        cur = self['list'].getCurrent()
        event = cur[0]
        ref = cur[1]
        self['img_gen'].hide()
        if not ref or not event:
            self['genero'].hide()
            return
        try:
            tuplagenero = getgenero(event, 70)
            clock_pic = tuplagenero[2]
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

        lalista = self['list'].list
        length = len(lalista)
        if length > 1:
            t = localtime(event.getBeginTime())
            self.actualizaclock(ref, event)
            if self.ufecha != str(strftime('%d %m %y', t)):
                self.ufecha = str(strftime('%d %m %y', t))
                self['dia'].setText(str(strftime('%d', t)))
                self['mes'].setText(str(strftime('%B', t)).lower())
                if self.antdia == None:
                    for ele in range(1, 8):
                        erdia = _(self.days[ele - 1])
                        if erdia.upper() == _(str(strftime('%A', t))).upper():
                            self.antdia = ele
                            self['semana' + str(ele)].setForegroundColorNum(1)
                            self['fsemana' + str(ele)].setBackgroundColorNum(1)
                            self['semana' + str(ele)].setBackgroundColorNum(1)
                        else:
                            self['semana' + str(ele)].setForegroundColorNum(0)
                            self['fsemana' + str(ele)].setBackgroundColorNum(0)
                            self['semana' + str(ele)].setBackgroundColorNum(0)

                else:
                    for ele in range(1, 8):
                        erdia = _(self.days[ele - 1])
                        if erdia.upper() == _(str(strftime('%A', t))).upper() and self.antdia != ele:
                            self['semana' + str(self.antdia)].setForegroundColorNum(0)
                            self['fsemana' + str(self.antdia)].setBackgroundColorNum(0)
                            self['semana' + str(self.antdia)].setBackgroundColorNum(0)
                            self['semana' + str(ele)].setForegroundColorNum(1)
                            self['fsemana' + str(ele)].setBackgroundColorNum(1)
                            self['semana' + str(ele)].setBackgroundColorNum(1)
                            self.antdia = ele
                            break

    def gotop(self):
        try:
            self['list'].instance.moveSelectionTo(0)
        except:
            pass

    def MenuBuscar(self):
        nkeys = []
        askList = []
        askList.append((_('Search in EPG') + ' (' + _('All channels') + ')', 'epg'))
        nkeys.append('1')
        try:
            serviceref = self.currentService
            askList.append((_('Search in') + ' [' + serviceref.getServiceName() + ']', 'epgc'))
            nkeys.append('2')
        except:
            pass

        askList.append(('--', 'nada'))
        nkeys.append('')
        askList.append((_('Search by genre') + ' (' + _('All channels') + ')', 'gen1'))
        nkeys.append('3')
        try:
            serviceref = self.currentService
            askList.append((_('Search by genre in') + ' [' + serviceref.getServiceName() + ']', 'gen2'))
            nkeys.append('4')
        except:
            pass

        askList.append(('--', 'nada'))
        nkeys.append('')
        askList.append((_('Search in Internet Database movies'), 'inet'))
        nkeys.append('5')
        dei = self.session.openWithCallback(self.callbackmenu, ChoiceBox, keys=nkeys, title=_('Search options') + '.\n' + _('Select option') + ':', list=askList)

    def callbackmenu(self, answer = None):
        answer = answer and answer[1]
        if answer:
            cur = self['list'].getCurrent()
            event = cur[0]
            serviceref = self.currentService
            ref = serviceref.ref
            servicios = None
            servicios = getBouquetServices()
            try:
                name = event.getEventName()
            except:
                name = ''

            titulo = name
            if name == '' or name.upper() == _('No Information').upper() or name.upper() == '(' + _('No Information').upper() + ')':
                name = 'xNAx'
            if answer == 'epg':
                if EPGSearch is not None:
                    self.session.open(EPGSearch, name, serviceref, False, servicios)
            elif answer == 'epgc':
                if EPGSearch is not None:
                    self.session.open(EPGSearch, name, serviceref, False, servicios, True)
            elif answer == 'gen1':
                if EPGSearch is not None:
                    self.session.open(EPGSearch, ':genero:', serviceref, False, servicios)
            elif answer == 'gen2':
                if EPGSearch is not None:
                    self.session.open(EPGSearch, ':genero:', serviceref, False, servicios, True)
            elif answer == 'inet':
                try:
                    from Plugins.Extensions.spzIMDB.plugin import spzIMDB
                    spzIMDB(self.session, tbusqueda=titulo)
                except:
                    pass
