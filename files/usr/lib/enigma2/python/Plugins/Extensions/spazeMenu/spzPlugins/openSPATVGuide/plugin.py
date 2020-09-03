from Components.config import config, ConfigClock, ConfigDateTime, ConfigSubsection, ConfigYesNo
from Components.Pixmap import Pixmap
from Components.Button import Button
from Components.ActionMap import ActionMap, HelpableActionMap
from Components.HTMLComponent import HTMLComponent
from Components.GUIComponent import GUIComponent
from Components.EpgList import Rect, EPGList
from Components.Sources.Event import Event
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest, MultiContentEntryPixmapAlphaBlend
from Components.Label import Label
from Plugins.Plugin import PluginDescriptor
from Screens.ChannelSelection import BouquetSelector
from Screens.ChoiceBox import ChoiceBox
from Screens.Screen import Screen
from Screens.HelpMenu import HelpableScreen
from Screens.EventView import EventViewBase
from Screens.TimeDateInput import TimeDateInput
from Screens.TimerEntry import TimerEntry
from Screens.EpgSelection import EPGSelection
from Screens.TimerEdit import TimerSanityConflict
from Screens.MessageBox import MessageBox
from Tools.Directories import resolveFilename, SCOPE_CURRENT_SKIN, fileExists
from RecordTimer import RecordTimerEntry, parseEvent, AFTEREVENT
from ServiceReference import ServiceReference
from Tools.LoadPixmap import LoadPixmap
from Tools import Notifications
from enigma import eSize, ePoint
from Plugins.Extensions.spazeMenu.plugin import esHD, fhd
from enigma import eEPGCache, eListbox, ePicLoad, gFont, eListboxPythonMultiContent, RT_HALIGN_LEFT, RT_HALIGN_RIGHT, RT_HALIGN_CENTER, RT_VALIGN_CENTER, RT_VALIGN_TOP, RT_WRAP, eRect, getDesktop, eTimer, eServiceCenter, eServiceReference, getBestPlayableServiceReference
from time import localtime, time, strftime, mktime, strptime
config.plugins.openSPATVGuide = ConfigSubsection()
config.plugins.openSPATVGuide.show_picons = ConfigYesNo(default=True)
config.plugins.openSPATVGuide.show_colors = ConfigYesNo(default=True)
from os import environ
import gettext
from Components.Language import language
from Tools.Directories import SCOPE_PLUGINS, SCOPE_LANGUAGE
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


def nombrepix(cualo):
    rutapix = None
    rutapix = '/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/newChannelSelection/spzTeam/' + cualo + '.png'
    if not fileExists(rutapix):
        rutapix = None
    return rutapix


from EPGSearch import EPGSearch, rutapiconS, isInTimer, getgenero, getcolorgenero
Session = None
Servicelist = None
spa_bouquets = []
man_bouquets = None
bouquetSel = None
epg_bouquet = None
dlg_stack = []
from EPGSimple import spaEPGSelection

class SpaViewSimple(Screen, EventViewBase):

    def __init__(self, session, Event, Ref, callback = None, similarEPGCB = None):
        Screen.__init__(self, session)
        self.skinName = 'EventView'
        EventViewBase.__init__(self, Event, Ref, callback, similarEPGCB)
        self['key_blue'].setText(_('Search'))
        self['Spaman'] = HelpableActionMap(self, 'CTVGuideActions', {'CBlue': (self.SpaSearch, _('Search'))})

    def SpaSearch(self):
        href = None
        try:
            cur = SpaList.getCurrent()
            event = cur[0]
            name = event.getEventName()
            href = cur[1]
        except:
            name = ''

        if name == '' or name.upper() == _('No Information').upper() or name.upper() == '(' + _('No Information').upper() + ')':
            name = 'xNAx'
        if EPGSearch is not None:
            self.session.open(EPGSearch, name, href, False)


from Screens.EventView import EventViewEPGSelect

def changeEventView():
    EventViewEPGSelect.__init__ = EventViewEPGSelectSPA__init__


def EPGSelection__init__(self, session, service, zapFunc = None, eventid = None, bouquetChangeCB = None, serviceChangeCB = None):
    baseEPGSelection__init__(self, session, service, zapFunc, eventid, bouquetChangeCB, serviceChangeCB)
    if self.type != EPG_TYPE_MULTI and True:

        def bluePressed():
            cur = self['list'].getCurrent()
            if cur[0] is not None:
                name = cur[0].getEventName()
            else:
                name = ''
            href = cur[1]
            if name == '' or name.upper() == _('No Information').upper() or name.upper() == '(' + _('No Information').upper() + ')':
                name = 'xNAx'
            self.session.open(EPGSearch, name, href, False)

        self['epgsearch_actions'] = ActionMap(['EPGSelectActions'], {'blue': bluePressed,
         'yellow': yellowPressed})
        self['key_blue'].text = _('Search')


def EventViewEPGSelectSPA__init__(self, session, Event, Ref, callback = None, singleEPGCB = None, multiEPGCB = None, similarEPGCB = None):
    Screen.__init__(self, session)
    self.skinName = 'EventView'
    EventViewBase.__init__(self, Event, Ref, callback, similarEPGCB)
    self['key_yellow'].setText(_('Single EPG'))
    self['key_blue'].setText(_('Search'))

    def yellowPressed():
        serviceref = self.currentService.ref
        if serviceref:
            self.session.open(spaEPGSelection, serviceref)

    def bluePressed():
        event = self.event
        serviceref = self.currentService
        if event is None:
            name = ''
        else:
            name = event.getEventName()
        if name == '' or name.upper() == _('No Information').upper() or name.upper() == '(' + _('No Information').upper() + ')':
            name = 'xNAx'
        self.session.open(EPGSearch, name, serviceref, False)

    self['epgactions'] = ActionMap(['EventViewEPGActions'], {'openSingleServiceEPG': yellowPressed,
     'openMultiServiceEPG': bluePressed})


prev_time = ConfigClock(default=time())
prev_fecha = ConfigDateTime(default=time(), formatstring=_('%d.%B %Y'), increment=86400)
SpaPrimetime1 = 22
SpaPrimetime2 = 0
autostart_bouquet = False
channel1 = False
prev_time_period = 240
Spa_Fontsize = 18
Spa_Left_Fontsize = 20
Spa_Timeline = 20
items_per_page = 14
spa_left16 = 190
overjump = False
Spa16 = 46
SpaEPGheight = int(items_per_page * Spa16)

def resizaLista():
    global Spa16
    global items_per_page
    global SpaEPGheight
    global spa_left16
    if config.plugins.openSPATVGuide.show_picons.value:
        items_per_page = fhd(11, 1.27)
        spa_left16 = fhd(220)
        Spa16 = fhd(40, 1.2)
    else:
        items_per_page = fhd(14, 1)
        spa_left16 = 190
        Spa16 = fhd(32)
    SpaEPGheight = int(items_per_page * Spa16)


resizaLista()

class SpaEPGList(EPGList):

    def __init__(self, selChangedCB = None, timer = None, time_epoch = 120, overjump_empty = False):
        self.cur_event = None
        self.cur_service = None
        self.offs = 0
        self.timer = timer
        self.onSelChanged = []
        self.type = SpaEPGList
        self.picload = ePicLoad()
        if selChangedCB is not None:
            self.onSelChanged.append(selChangedCB)
        GUIComponent.__init__(self)
        self.l = eListboxPythonMultiContent()
        self.curr_refspa = None
        self.spaheight = 54
        self.l.setBuildFunc(self.buildEntry)
        self.setOverjump_Empty(overjump_empty)
        self.epgcache = None
        self.SpaNowS = LoadPixmap(cached=True, path='/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/openSPATVGuide/Pic/SpaNowS.png')
        self.SpaBackS = LoadPixmap(cached=True, path='/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/openSPATVGuide/Pic/SpaBackS.png')
        self.SpaBackS2 = LoadPixmap(cached=True, path='/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/openSPATVGuide/Pic/SpaBackSi.png')
        self.SpaRecS = LoadPixmap(cached=True, path='/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/openSPATVGuide/Pic/SpaRecS.png')
        self.SpaPicons = LoadPixmap(cached=True, path='/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/openSPATVGuide/Pic/SpaPicons.png')
        self.SpaPiconsSelect = LoadPixmap(cached=True, path='/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/openSPATVGuide/Pic/SpaPiconsSelect.png')
        self.time_base = None
        self.time_epoch = time_epoch
        self.list = None
        self.event_rect = None
        self.nowForeColor = 0
        self.nowForeColorSelected = 0
        self.foreColor = 1651533
        self.foreColor2 = 2572380
        self.foreColorSelected = 16777215
        self.borderColor = 12632256
        self.backColor = 2966878
        self.backColorSelected = 15053379
        self.nowBackColor = 33375
        self.nowBackColorSelected = 4718847
        self.foreColorService = 16777215
        self.foreColorServiceS = 16777215
        self.backColorService = 10066329
        self.backColorServiceS = 13684991
        self.colorBordeService = 0
        self.colorBordeLista = 2840687
        self.colorBordeListaRec = 12213083
        self.colorBordeListaNow = 3767640
        self.colorBordeListaNow = self.colorBordeLista = self.colorBordeListaRec = 0
        self.anabordeListaBack = 0

    def applySkin(self, desktop, screen):
        if self.skinAttributes is not None:
            attribs = []
            for attrib, value in self.skinAttributes:
                if attrib == 'EntryForegroundColor':
                    pass
                else:
                    attribs.append((attrib, value))

            self.skinAttributes = attribs
        rc = GUIComponent.applySkin(self, desktop, screen)
        self.setItemsPerPage()
        return rc

    def isSelectable(self, service, sname, event_list):
        return event_list and len(event_list) and True or False

    def setOverjump_Empty(self, overjump_empty):
        if overjump_empty:
            self.l.setSelectableFunc(self.isSelectable)

    def setEpoch(self, epoch):
        self.offs = 0
        self.time_epoch = epoch
        self.fillSpaTVGuide(None)

    def setEpoch2(self, epoch):
        self.offs = 0
        self.time_epoch = epoch

    def getEventFromId(self, service, eventid):
        event = None
        if self.epgcache is not None and eventid is not None:
            event = self.epgcache.lookupEventId(service.ref, eventid)
        return event

    def moveToService(self, serviceref):
        if serviceref is not None:
            for x in range(len(self.list)):
                if self.getmejor(self.list[x][0]) == serviceref.toString():
                    self.instance.moveSelectionTo(x)
                    break

    def getIndexFromService(self, serviceref):
        if serviceref is not None:
            for x in range(len(self.list)):
                if self.list[x][0] == serviceref.toString():
                    return x

    def setCurrentIndex(self, index):
        if self.instance is not None:
            self.instance.moveSelectionTo(index)

    def getCurrentEventId(self):
        if self.cur_service is None:
            return
        events = self.cur_service[2]
        refstr = self.cur_service[0]
        if self.cur_event is None or not events or not len(events):
            return
        event = events[self.cur_event]
        eventid = event[0]
        return eventid

    def getCurrent(self):
        if self.cur_service is None:
            return (None, None)
        old_service = self.cur_service
        events = self.cur_service[2]
        refstr = self.cur_service[0]
        if self.cur_event is None or not events or not len(events):
            return (None, ServiceReference(refstr))
        event = events[self.cur_event]
        eventid = event[0]
        service = ServiceReference(refstr)
        event = self.getEventFromId(service, eventid)
        return (event, service)

    def connectSelectionChanged(func):
        if not self.onSelChanged.count(func):
            self.onSelChanged.append(func)

    def disconnectSelectionChanged(func):
        self.onSelChanged.remove(func)

    def serviceChanged(self):
        cur_sel = self.l.getCurrentSelection()
        if cur_sel:
            self.findBestEvent()

    def findBestEvent(self):
        old_service = self.cur_service
        cur_service = self.cur_service = self.l.getCurrentSelection()
        last_time = 0
        time_base = self.getTimeBase()
        if old_service and self.cur_event is not None:
            events = old_service[2]
            cur_event = events[self.cur_event]
            last_time = cur_event[2]
            if last_time < time_base:
                last_time = time_base
        if cur_service:
            self.cur_event = 0
            events = cur_service[2]
            if events and len(events):
                if last_time:
                    best_diff = 0
                    best = len(events)
                    idx = 0
                    for event in events:
                        ev_time = event[2]
                        if ev_time < time_base:
                            ev_time = time_base
                        diff = abs(ev_time - last_time)
                        if best == len(events) or diff < best_diff:
                            best = idx
                            best_diff = diff
                        idx += 1

                    if best != len(events):
                        self.cur_event = best
            else:
                self.cur_event = None
        self.selEntry(0)

    def selectionChanged(self):
        for x in self.onSelChanged:
            if x is not None:
                x()

    GUI_WIDGET = eListbox

    def setItemsPerPage(self):
        self.spaheight = Spa16
        self.l.setItemHeight(Spa16)

    def setServiceFontsize(self):
        self.l.setFont(0, gFont('Regular', Spa_Left_Fontsize))

    def setEventFontsize(self):
        self.l.setFont(1, gFont('Regular', Spa_Fontsize))

    def postWidgetCreate(self, instance):
        instance.setWrapAround(True)
        instance.selectionChanged.get().append(self.serviceChanged)
        instance.setContent(self.l)
        self.l.setSelectionClip(eRect(0, 0, 0, 0), False)
        self.setServiceFontsize()
        self.setEventFontsize()

    def preWidgetRemove(self, instance):
        instance.selectionChanged.get().remove(self.serviceChanged)
        instance.setContent(None)

    def recalcEntrySize(self):
        global SpaNoPicon
        esize = self.l.getItemSize()
        width = esize.width()
        height = esize.height()
        xpos = 0
        w = spa_left16
        SpaNoPicon = 2
        self.service_rect = Rect(xpos, 0, w, height)
        xpos += w
        w = width - xpos
        self.event_rect = Rect(xpos, 0, w, height)

    def calcEntryPosAndWidthHelper(self, stime, duration, start, end, width):
        xpos = (stime - start) * width / (end - start)
        ewidth = (stime + duration - start) * width / (end - start) + 1
        ewidth -= xpos
        if xpos < 0:
            ewidth += xpos
            xpos = 0
        if xpos + ewidth > width:
            ewidth = width - xpos
        return (xpos, ewidth)

    def calcEntryPosAndWidth(self, event_rect, time_base, time_epoch, ev_start, ev_duration):
        xpos, width = self.calcEntryPosAndWidthHelper(ev_start, ev_duration, time_base, time_base + time_epoch * 60, event_rect.width())
        return (xpos + event_rect.left(), width)

    def getmejor(self, laref):
        try:
            cret = ServiceReference(eServiceReference(laref)).ref
            if cret.flags & eServiceReference.isGroup:
                xref = getBestPlayableServiceReference(cret, eServiceReference(), True)
                fref = xref.toString()
                return fref
        except:
            pass

        return laref

    def buildEntry(self, service, service_name, events):
        if service == self.cur_service[0]:
            piconbkcolor = 0
        else:
            piconbkcolor = 0
        r1 = self.service_rect
        r2 = self.event_rect
        foreColor = self.foreColor
        foreColorSelected = self.foreColorSelected
        backColor = self.backColor
        backColorSelected = self.backColorSelected
        borderColor = self.borderColor
        backColorService = self.backColorService
        backColorOrig = self.backColor
        SpaEvent = 2
        if self.curr_refspa.toString() == service:
            backColorService = self.backColorServiceS
        res = [None]
        picon = None
        grosorborde = 1
        if SpaEvent == 2:
            if True:
                displayPicon = None
                addpicon = 0
                nfont = 0
                nborde = 1
                if config.plugins.openSPATVGuide.show_picons.value:
                    picon = 'na'
                    piconHeight = Spa16 - 4
                    piconWidth = int(piconHeight * 100 / 60)
                    pospicon = spa_left16 - piconWidth - 2
                    picon = rutapiconS(self.getmejor(service))
                    nfont = 1
                    nborde = 0
                    if fileExists(picon) and 'picon_default.png' not in picon:
                        self.picload.setPara((piconWidth,
                         piconHeight,
                         1,
                         1,
                         1,
                         1,
                         '#000000'))
                        self.picload.startDecode(picon, 0, 0, False)
                        displayPicon = self.picload.getData()
                        addpicon = piconWidth + 6
                ref = self.curr_refspa
                refs = self.getmejor(service)
                if not refs:
                    refs = service
                colorbg = self.backColorService
                colorfr = self.foreColorService
                prev = '  '
                if ref.toString() == refs:
                    colorbg = self.backColorServiceS
                    colorfr = self.foreColorServiceS
                    prev = '  '
                    npng = self.SpaPiconsSelectdef()
                else:
                    npng = self.SpaPiconsdef()
                res.append(MultiContentEntryText(pos=(r1.left() + 1, r1.top() - nfont), size=(r1.width() - 1 - addpicon, r1.height()), font=nfont, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=prev + service_name, color=colorfr, backcolor=9810, backcolor_sel=9810, color_sel=colorfr, border_width=nborde, border_color=self.colorBordeService))
                res.append(MultiContentEntryPixmapAlphaBlend(pos=(r1.left() + 2, r1.top()), size=(r1.width() - 1, r1.height()), png=npng))
                if displayPicon is not None:
                    res.append(MultiContentEntryPixmapAlphaTest(pos=(pospicon, 2), size=(piconWidth, piconHeight), png=displayPicon, backcolor=None, backcolor_sel=None))
            upos = -1
            esimpar = True
            colorborde = self.colorBordeLista
            if events:
                colorborde = self.colorBordeLista
                start = self.time_base + self.offs * self.time_epoch * 60
                end = start + self.time_epoch * 60
                left = r2.left()
                top = r2.top()
                width = r2.width()
                height = r2.height()
                spaflags = RT_HALIGN_LEFT | RT_VALIGN_CENTER
                thepraefix = '   '
                now = int(time())
                for ev in events:
                    colorborde = self.colorBordeLista
                    rec = ev[2] and self.timer.isInTimer(ev[0], ev[2], ev[3], service)
                    xpos, ewidth = self.calcEntryPosAndWidthHelper(ev[2], ev[3], start, end, width)
                    rewidth = ewidth
                    if ewidth > 1:
                        rewidth = ewidth - 1
                    addrec = False
                    if rec:
                        spatyp = self.SpaRecRed(service, ev[2], ev[3], ev[0])
                        if spatyp == 'record':
                            addrec = True
                            colorborde = self.colorBordeListaRec
                            res.append(MultiContentEntryPixmapAlphaTest(pos=(left + xpos, top), size=(rewidth, height), png=self.SpaRecSdef(service, ev[2], ev[3], ev[0])))
                            backColorSelected = 10420224
                        elif spatyp == 'justplay':
                            backColor = 6722662
                            backColorSelected = 6398305
                        else:
                            backColor = backColorOrig
                            backColorSelected = self.backColorSelected
                    if not addrec:
                        if ev[2] <= now and ev[2] + ev[3] > now:
                            colorborde = self.colorBordeListaNow
                            foreColor = self.nowForeColor
                            foreColorSelected = self.nowForeColorSelected
                            backColor = self.nowBackColor
                            res.append(MultiContentEntryPixmapAlphaTest(pos=(left + xpos, top), size=(rewidth, height), png=self.SpaNowSdef(service, ev[2], ev[3], ev[0])))
                        else:
                            backColor = backColorOrig
                            backColorSelected = self.backColorSelected
                            foreColor = self.foreColor
                            foreColorSelected = self.foreColorSelected
                            if esimpar:
                                erpng = self.SpaBackSdef(service, ev[2], ev[3], ev[0])
                                foreColor = self.foreColor
                            else:
                                erpng = self.SpaBackSdef2(service, ev[2], ev[3], ev[0])
                                foreColor = self.foreColor2
                            esimpar = not esimpar
                            anaborde = self.anabordeListaBack
                            res.append(MultiContentEntryPixmapAlphaTest(pos=(left + xpos + anaborde, top), size=(rewidth - anaborde * 2, height), png=erpng))
                    res.append(MultiContentEntryText(pos=(left + xpos, top), size=(rewidth, height), font=1, flags=spaflags, text=thepraefix + ev[1], color=foreColor, border_width=grosorborde, border_color=colorborde))
                    if config.plugins.openSPATVGuide.show_colors.value:
                        try:
                            elcolor = getcolorgenero(ev[4][0][0], True)
                            if elcolor:
                                res.append(MultiContentEntryText(pos=(left + xpos + 1, top + 1), size=(rewidth - 2, 3), font=1, flags=spaflags, text=' ', backcolor=elcolor, backcolor_sel=elcolor, border_width=0))
                        except:
                            pass

            else:
                left = r2.left()
                top = r2.top()
                width = r2.width()
                height = r2.height()
                res.append(MultiContentEntryText(pos=(left, top), size=(width, height), font=1, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text='  (' + _('No Information') + ')', color=6908264, color_sel=foreColorSelected, backcolor=12040129, border_width=grosorborde, backcolor_sel=backColorSelected, border_color=colorborde))
            return res

    def selEntry(self, dir, visible = True):
        cur_service = self.cur_service
        self.recalcEntrySize()
        valid_event = self.cur_event is not None
        if cur_service:
            update = True
            entries = cur_service[2]
            if dir == 0:
                update = False
            elif dir == +1:
                if valid_event and self.cur_event + 1 < len(entries):
                    self.cur_event += 1
                else:
                    self.offs += 1
                    self.fillSpaTVGuide(None)
                    return True
            elif dir == -1:
                if valid_event and self.cur_event - 1 >= 0:
                    self.cur_event -= 1
                elif self.offs > 0:
                    self.offs -= 1
                    self.fillSpaTVGuide(None)
                    return True
            else:
                if dir == +2:
                    self.offs += 1
                    self.fillSpaTVGuide(None)
                    return True
                if dir == -2:
                    if self.offs > 0:
                        self.offs -= 1
                        self.fillSpaTVGuide(None)
                        return True
        self.l.setSelectionClip(eRect(self.service_rect.left(), self.service_rect.top(), 0, 0), False)
        if cur_service and valid_event:
            entry = entries[self.cur_event]
            time_base = self.time_base + self.offs * self.time_epoch * 60
            xpos, width = self.calcEntryPosAndWidth(self.event_rect, time_base, self.time_epoch, entry[2], entry[3])
            self.l.setSelectionClip(eRect(xpos, 0, 0, 0), visible and update)
        else:
            self.l.setSelectionClip(eRect(self.event_rect.left(), self.event_rect.top(), 0, 0), False)
        self.selectionChanged()
        return False

    def queryEPG(self, list, buildFunc = None):
        if self.epgcache is not None:
            if buildFunc is not None:
                return self.epgcache.lookupEvent(list, buildFunc)
            else:
                return self.epgcache.lookupEvent(list)
        return []

    def fillSpaTVGuide(self, services, stime = -1):
        if services is None:
            time_base = self.time_base + self.offs * self.time_epoch * 60
            test = [ (service[0],
             0,
             time_base,
             self.time_epoch) for service in self.list ]
        else:
            self.cur_event = None
            self.cur_service = None
            self.time_base = int(stime)
            test = [ (service.ref.toString(),
             0,
             self.time_base,
             self.time_epoch) for service in services ]
        test.insert(0, 'XRnITBDW')
        epg_data = self.queryEPG(test)
        self.list = []
        tmp_list = None
        service = ''
        sname = ''
        for x in epg_data:
            if service != x[0]:
                if tmp_list is not None:
                    self.list.append((service, sname, tmp_list[0][0] is not None and tmp_list or None))
                service = x[0]
                sname = x[1]
                tmp_list = []
            tmp_list.append((x[2],
             x[3],
             x[4],
             x[5],
             x[6]))

        if tmp_list and len(tmp_list):
            self.list.append((service, sname, tmp_list[0][0] is not None and tmp_list or None))
        self.l.setList(self.list)
        self.findBestEvent()

    def getEventRect(self):
        rc = self.event_rect
        return Rect(rc.left() + (self.instance and self.instance.position().x() or 0), rc.top(), rc.width(), rc.height())

    def getTimeEpoch(self):
        return self.time_epoch

    def getTimeBase(self):
        return self.time_base + self.offs * self.time_epoch * 60

    def resetOffset(self):
        self.offs = 0

    def SpaPiconsdef(self):
        return self.SpaPicons

    def SpaPiconsSelectdef(self):
        return self.SpaPiconsSelect

    def SpaNowdef(self, refstr, beginTime, duration, eventId):
        return self.SpaNow

    def SpaNowSdef(self, refstr, beginTime, duration, eventId):
        return self.SpaNowS

    def SpaBackSdef(self, refstr, beginTime, duration, eventId):
        return self.SpaBackS

    def SpaBackSdef2(self, refstr, beginTime, duration, eventId):
        return self.SpaBackS2

    def SpaRecSdef(self, refstr, beginTime, duration, eventId):
        return self.SpaRecS

    def SpaRecRed(self, refstr, beginTime, duration, eventId):
        pre_clock = 1
        post_clock = 2
        clock_type = 0
        endTime = beginTime + duration
        for x in self.timer.timer_list:
            if x.service_ref.ref.toString() == refstr:
                if x.eit == eventId:
                    return 'record'
                beg = x.begin
                end = x.end
                if beginTime > beg and beginTime < end and endTime > end:
                    clock_type |= pre_clock
                elif beginTime < beg and endTime > beg and endTime < end:
                    clock_type |= post_clock

        if clock_type == 0:
            return 'record'
        elif clock_type == pre_clock:
            return 'pre'
        elif clock_type == post_clock:
            return 'post'
        else:
            return 'nichts'


class TimelineText(HTMLComponent, GUIComponent):

    def __init__(self):
        GUIComponent.__init__(self)
        self.l = eListboxPythonMultiContent()
        self.l.setSelectionClip(eRect(0, 0, 0, 0))
        self.l.setItemHeight(fhd(25))
        self.l.setFont(0, gFont('Regular', Spa_Timeline))
        self.hayprime = False

    GUI_WIDGET = eListbox

    def postWidgetCreate(self, instance):
        instance.setContent(self.l)

    def setEntries(self, entries):
        self.hayprime = False
        res = [None]
        for x in entries:
            tm = x[0]
            xpos = x[1]
            lttm = localtime(tm)
            strt = strftime('%H:%M', lttm)
            lt2 = SpaPrimetime1
            carini = ' '
            npos = xpos
            res.append(MultiContentEntryText(pos=(npos, fhd(3)), size=(fhd(1), fhd(21)), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=carini, color=9933219, backcolor=9933219, backcolor_sel=9933219))
            npos = npos + 4
            if not self.hayprime and strt[:2] == str(SpaPrimetime1):
                self.hayprime = True
                res.append(MultiContentEntryText(pos=(npos, fhd(1)), size=(fhd(70), fhd(25)), font=0, flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER, text=strt, color=8520, backcolor_sel=15053379, backcolor=15053379))
            else:
                res.append(MultiContentEntryText(pos=(npos, fhd(1)), size=(fhd(70), fhd(25)), font=0, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER, text=strt, color=15053379, backcolor=8520))

        self.l.setList([res])


class openSPATVGuide(Screen, HelpableScreen):
    EMPTY = 0
    ADD_TIMER = 1
    REMOVE_TIMER = 2
    ZAP = 1
    if esHD():
        skin = '\n\t\t\t<screen name="openSPATVGuide" position="center,center" size="1920,1080" backgroundColor="#00071219" title="Electronic Program Guide (EPG)" flags="wfNoBorder">\n \t\t\t\t<widget source="Title" render="Label" position="858,28" size="640,34" font="Regular; 20" foregroundColor="#00c0c0c0" backgroundColor="#00113778" halign="center" transparent="0" valign="center" />\n \t\t\t\t<widget name="date" position="507,28" size="349,34" font="Regular;20" halign="left" foregroundColor="#000000" backgroundColor="#e5b243" transparent="0" valign="center" />\n \t\t\t\t\n \t\t\t\t<widget source="session.RecordState" render="Pixmap" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/openSPATVGuide/img/rec.png" position="1732,31" size="30,30" zPosition="3" alphatest="blend">\n \t\t\t\t  <convert type="ConditionalShowHide" />\n \t\t\t\t</widget>\n \t\t\t\t<widget source="global.CurrentTime" render="Label" position="1711,28" size="150,34" font="Regular; 19" foregroundColor="#999999" backgroundColor="#132d53" shadowColor="#000000" halign="right" transparent="0" valign="center">\n \t\t\t\t\t<convert type="ClockToText">Default</convert>\n \t\t\t\t</widget>\n \t\t\t\t<widget source="global.CurrentTime" render="Label" position="1500,28" size="226,34" font="Regular; 19" foregroundColor="#999999" backgroundColor="#132d53" shadowColor="#000000" halign="right" transparent="0" valign="center" zPosition="1">\n \t\t\t\t  <convert type="ClockToText">Format:%d-%b-%Y</convert>\n \t\t\t\t</widget>\n \t\t\t\n \t\t\t\t<widget name="timeline_text" position="0,288" size="1824,37" foregroundColor="#00e5b243" backgroundColor="#31000000" transparent="1" />\n \n \t\t\t\t<widget name="selector" position="0,0" size="1,1" font="Regular;18" foregroundColor="#000000" backgroundColor="#00e5b243" borderColor="#00e5b243" borderWidth="1" halign="left" valign="center" transparent="1" zPosition="20" noWrap="1" />\n \t\t\t\t<widget name="selector_r" position="0,0" size="15,13" transparent="1" zPosition="21" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/openSPATVGuide/Pic/sel800r.png" alphatest="blend" />\n \t\t\t\t<widget name="selectorpixmap" position="0,0" size="15,15" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/openSPATVGuide/Pic/select.png" transparent="0" zPosition="19" alphatest="blend" />\n \t\t\t\t<widget name="selectorservice" position="0,0" size="12,19" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/openSPATVGuide/Pic/selser-fs8.png" transparent="0" zPosition="19" alphatest="blend" />\n \n \t\t\t\t<eLabel name="bg1" position="73,325" size="375,672" transparent="0" backgroundColor="#002148" zPosition="-2" />\n \t\t\t\t<widget name="espera" position="358,325" size="1479,672" transparent="0" foregroundColor="#000000" backgroundColor="#a7a7b1" zPosition="-1" halign="center" font="Regular; 21" valign="center" />\t\t\t\t\n \t\t\t\t<widget name="list" position="70,325" size="1770,672" scrollbarMode="showNever" transparent="1" backgroundColor="#c0c0c0" />\n \t\t\t\t\n \t\t\t\t<widget name="timeline0" position="0,210" zPosition="1" size="0,0" pixmap="skin_default/timeline.png" />\n \t\t\t\t<widget name="timeline1" position="0,210" zPosition="1" size="0,0" pixmap="skin_default/timeline.png" />\n \t\t\t\t<widget name="timeline2" position="0,210" zPosition="1" size="0,0" pixmap="skin_default/timeline.png" />\n \t\t\t\t<widget name="timeline3" position="0,210" zPosition="1" size="0,0" pixmap="skin_default/timeline.png" />\n \t\t\t\t<widget name="timeline4" position="0,210" zPosition="1" size="0,0" pixmap="skin_default/timeline.png" />\n \t\t\t\t<widget name="timeline5" position="0,210" zPosition="1" size="0,0" pixmap="skin_default/timeline.png" />\n \n \t\t\t\t<widget name="timeline_now" position="0,318" zPosition="22" size="28,880" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/openSPATVGuide/hdtimeline-now.png" alphatest="blend" />\n \t\t\t\t<widget source="Event" render="Label" position="507,70" size="150,37" font="Regular; 19" foregroundColor="#00e5b243" backgroundColor="#31000000" shadowColor="#000000" halign="left" transparent="1">\n \t\t\t\t  <convert type="EventTime">StartTime</convert>\n \t\t\t\t  <convert type="ClockToText" />\n \t\t\t\t</widget>\n \t\t\t\t<widget source="Event" render="Label" position="600,70" size="150,37" font="Regular; 19" foregroundColor="#00e5b243" backgroundColor="#31000000" shadowColor="#000000" halign="left" transparent="1">\n \t\t\t\t  <convert type="EventTime">EndTime</convert>\n \t\t\t\t  <convert type="ClockToText">Format:- %H:%M</convert>\n \t\t\t\t</widget>\n \t\t\t\t<widget source="Event" render="Label" position="847,70" size="705,37" font="Regular; 18" foregroundColor="#0053a9ff" backgroundColor="#31000000" transparent="1" halign="left" noWrap="1">\n \t\t\t\t  <convert type="EventName">Name</convert>\n \t\t\t\t</widget>\n \n\t\t\t\t<widget source="Event" render="Label" position="690,70" size="169,37" font="Regular; 19" foregroundColor="#00ffffff" backgroundColor="#31000000" shadowColor="#000000" halign="center" transparent="1">\n\t\t\t\t  <convert type="EventTime">Duration</convert>\n\t\t\t\t  <convert type="ClockToText">InMinutes</convert>\n\t\t\t\t</widget>\n \t\t\t\t<widget source="Event" render="Label" position="511,108" zPosition="1" size="1221,174" font="Regular; 18" foregroundColor="#00bbbbbb" backgroundColor="#31000000" shadowColor="#000000" transparent="1" valign="top">\n \t\t\t\t  <convert type="EventName">ExtendedDescription</convert>\n \t\t\t\t</widget>\n \t\t\t\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/redHD.png" position="79,1001" size="52,37" alphatest="blend" transparent="0" />\n \t\t\t\t<widget name="key_red" position="135,1003" size="102,36" font="Regular; 17" foregroundColor="#aeaeae" backgroundColor="#000000" shadowColor="#000000" halign="left" valign="center" transparent="1" noWrap="1" />\n \t\t\t\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/greenHD.png" position="247,1001" size="52,37" alphatest="blend" />\n \t\t\t\t<widget name="key_green" position="305,1003" size="235,36" font="Regular; 17" foregroundColor="#aeaeae" backgroundColor="#000000" shadowColor="#000000" halign="left" valign="center" transparent="1" noWrap="1" />\n \t\t\t\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/yellowHD.png" position="540,1001" size="52,37" alphatest="blend" />\n \t\t\t\t<widget name="key_yellow" position="597,1003" size="175,36" font="Regular; 17" foregroundColor="#aeaeae" backgroundColor="#000000" shadowColor="#000000" halign="left" valign="center" transparent="1" noWrap="1" />\n \t\t\t\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/blueHD.png" position="772,1001" size="52,37" alphatest="blend" />\n \t\t\t\t<widget name="key_blue" position="830,1003" size="124,36" font="Regular; 17" foregroundColor="#aeaeae" backgroundColor="#000000" shadowColor="#000000" halign="left" valign="center" transparent="1" noWrap="1" />\n\t\t\t\t\n\t\t\t\t<eLabel backgroundColor="#15243a" position="61,285" size="1789,763" zPosition="-2" />\n\t\t\t\t\n\t\t\t\t<widget source="session.VideoPicture" render="Pig" position="57,28" size="442,244" zPosition="-1" backgroundColor="transparent2" />\n\t\t\t\t<eLabel name="tapapip" position="54,25" size="448,250" zPosition="-2" backgroundColor="#2b3949" />\n\t\t\t\t<widget source="session.CurrentService" render="Label" position="63,28" size="430,34" font="Regular; 17" transparent="1" valign="center" zPosition="6" backgroundColor="black" foregroundColor="#20ffffcc" noWrap="1" borderColor="#11000000" borderWidth="1">\n\t\t\t\t  <convert type="ServiceName">Name</convert>\n\t\t\t\t</widget>\n\t\t\t\t<eLabel name="tapainfocanal" position="57,28" size="442,34" backgroundColor="#66111111" foregroundColor="#2253a9ff" transparent="0" zPosition="0" />\n \t\t\t\n\t\t\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/izqHD.png" position="960,1001" size="52,37" alphatest="blend" />\n\t\t\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/dchaHD.png" position="1012,1001" size="52,37" alphatest="blend" />\n\t\t\t\t<widget name="key_rw" position="1072,1003" size="60,36" font="Regular; 17" foregroundColor="#aeaeae" backgroundColor="#000000" halign="left" valign="center" transparent="1" noWrap="1" />\n\t\t\t\t<eLabel name="smenos1" position="1056,1029" size="12,3" transparent="0" backgroundColor="#aeaeae" zPosition="21" />\n\t\t\t\t<eLabel name="smas1" position="1054,1002" size="25,25" text="+" transparent="1" foregroundColor="#aeaeae" zPosition="21" halign="left" font="Regular; 17" valign="center" />\t\t\t\n\t\t\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/chHD.png" position="1131,1001" size="63,37" alphatest="blend" />\n\t\t\t\t<widget name="key_ch" position="1213,1003" size="102,36" font="Regular; 17" foregroundColor="#aeaeae" backgroundColor="#000000" halign="left" valign="center" transparent="1" noWrap="1" />\n\t\t\t\t<eLabel name="smenos1" position="1197,1029" size="12,3" transparent="0" backgroundColor="#aeaeae" zPosition="21" />\n\t\t\t\t<eLabel name="smas1" position="1195,1002" size="25,25" text="+" transparent="1" foregroundColor="#aeaeae" zPosition="21" halign="left" font="Regular; 17" valign="center" />\t\t\t\t\t\n \n\t\t\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/menuHD.png" position="1323,1001" size="67,37" alphatest="blend" />\n\t\t\t\t<widget name="key_menu" position="1390,1003" size="135,36" font="Regular; 17" foregroundColor="#aeaeae" backgroundColor="#000000" halign="left" valign="center" transparent="1" noWrap="1" />\n \n\t\t\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/infoHD.png" position="1522,1001" size="52,37" alphatest="blend" />\n\t\t\t\t<widget name="key_info" position="1575,1003" size="157,36" font="Regular; 17" foregroundColor="#aeaeae" backgroundColor="#000000" halign="left" valign="center" transparent="1" noWrap="1" />\n \n\t\t\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/okHD.png" position="1731,1001" size="52,37" alphatest="blend" />\n\t\t\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/exitHD.png" position="1780,1001" size="52,37" alphatest="blend" />\n\t\t\t\t<widget name="sitimer" position="820,28" size="36,36" zPosition="25" alphatest="blend" />\n\t\t\t\t<widget name="nom_lista" position="78,289" size="276,36" font="Regular; 18" halign="left" foregroundColor="#89919c" backgroundColor="#000000" transparent="1" valign="center" zPosition="10" noWrap="1" />\n \n\t\t\t\t<widget name="nom_canal" position="1561,73" size="300,30" font="Regular; 17" halign="right" foregroundColor="#ffffff" backgroundColor="#000000" transparent="1" valign="center" zPosition="10" noWrap="1" />\t\t\t\n\t\t\t\t<widget name="img_picon" position="1741,127" size="121,75" zPosition="20" />\t\n\t\t\t\t<widget name="tapa_picon" position="1740,126" size="124,78" zPosition="19" transparent="0" backgroundColor="#4b5460" />\n \t\t\t\n\t\t\t\t<widget source="Event" render="Label" position="1740,243" size="124,37" font="Regular; 17" foregroundColor="#949494" transparent="1" halign="right" noWrap="1">\n\t\t\t\t  <convert type="EventRating">Rating</convert>\n\t\t\t\t</widget>\t\t\n\t\t\t\t<widget name="genero" position="1422,70" size="405,37" zPosition="19" transparent="0" backgroundColor="#030813" font="Regular; 16" foregroundColor="#949494" halign="right" valign="bottom" noWrap="1" />\n\t\t\t\t<!--<widget name="genero_arr" position="1500,70" size="361,4" zPosition="20" transparent="0" backgroundColor="#030813" />-->\n\t\t\t\t<widget name="img_gen" position="1827,73" size="34,34" zPosition="19" transparent="0" alphatest="blend" />\t\n\t\t\t</screen>'
    else:
        skin = '\n\t\t\t<screen name="openSPATVGuide" position="center,center" size="1280,720" backgroundColor="#00071219" title="Electronic Program Guide (EPG)" flags="wfNoBorder">\n\t\t\t\t<widget source="Title" render="Label" position="572,19" size="427,23" font="Regular; 20" foregroundColor="#00c0c0c0" backgroundColor="#00113778" halign="center" transparent="0" valign="center" />\n\t\t\t\t<widget name="date" position="338,19" size="233,23" font="Regular;20" halign="left" foregroundColor="#000000" backgroundColor="#e5b243" transparent="0" valign="center" />\n\t\t\t\t\n\t\t\t\t<widget source="session.RecordState" render="Pixmap" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/openSPATVGuide/img/rec.png" position="1155,21" size="20,20" zPosition="3" alphatest="blend">\n\t\t\t\t  <convert type="ConditionalShowHide" />\n\t\t\t\t</widget>\n\t\t\t\t<widget source="global.CurrentTime" render="Label" position="1141,19" size="100,23" font="Regular; 19" foregroundColor="#999999" backgroundColor="#132d53" shadowColor="#000000" halign="right" transparent="0" valign="center">\n\t\t\t\t\t<convert type="ClockToText">Default</convert>\n\t\t\t\t</widget>\n\t\t\t\t<widget source="global.CurrentTime" render="Label" position="1000,19" size="151,23" font="Regular; 19" foregroundColor="#999999" backgroundColor="#132d53" shadowColor="#000000" halign="right" transparent="0" valign="center" zPosition="1">\n\t\t\t\t  <convert type="ClockToText">Format:%d-%b-%Y</convert>\n\t\t\t\t</widget>\n\t\t\t\n\t\t\t\t<widget name="timeline_text" position="0,192" size="1216,25" foregroundColor="#00e5b243" backgroundColor="#31000000" transparent="1" />\n\n\t\t\t\t<widget name="selector" position="0,0" size="1,1" font="Regular;18" foregroundColor="#000000" backgroundColor="#00e5b243" borderColor="#00e5b243" borderWidth="1" halign="left" valign="center" transparent="1" zPosition="20" noWrap="1" />\n\t\t\t\t<widget name="selector_r" position="0,0" size="10,9" transparent="1" zPosition="21"  pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/openSPATVGuide/Pic/sel800r.png" alphatest="blend" />\n\t\t\t\t<widget name="selectorpixmap" position="0,0" size="10,10" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/openSPATVGuide/Pic/select.png" transparent="0" zPosition="19" alphatest="blend" />\n\t\t\t\t<widget name="selectorservice" position="0,0" size="8,13" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/openSPATVGuide/Pic/selser-fs8.png" transparent="0" zPosition="19" alphatest="blend" />\n\n\t\t\t\t<eLabel name="bg1" position="49,217" size="250,448" transparent="0" backgroundColor="#002148" zPosition="-2" />\n\t\t\t\t<widget name="espera" position="239,217" size="986,448" transparent="0" foregroundColor="#000000" backgroundColor="#a7a7b1" zPosition="-1" halign="center" font="Regular; 21" valign="center" />\t\t\t\t\n\t\t\t\t<widget name="list" position="47,217" size="1180, 448" scrollbarMode="showNever" transparent="1" backgroundColor="#c0c0c0" />\n\t\t\t\t\n\t\t\t\t<widget name="timeline0" position="0,140" zPosition="1" size="0,0" pixmap="skin_default/timeline.png" />\n\t\t\t\t<widget name="timeline1" position="0,140" zPosition="1" size="0,0" pixmap="skin_default/timeline.png" />\n\t\t\t\t<widget name="timeline2" position="0,140" zPosition="1" size="0,0" pixmap="skin_default/timeline.png" />\n\t\t\t\t<widget name="timeline3" position="0,140" zPosition="1" size="0,0" pixmap="skin_default/timeline.png" />\n\t\t\t\t<widget name="timeline4" position="0,140" zPosition="1" size="0,0" pixmap="skin_default/timeline.png" />\n\t\t\t\t<widget name="timeline5" position="0,140" zPosition="1" size="0,0" pixmap="skin_default/timeline.png" />\n\n\t\t\t\t<widget name="timeline_now" position="0,212" zPosition="22" size="19, 460" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/openSPATVGuide/timeline-now.png" alphatest="blend" />\n\t\t\t\t<widget source="Event" render="Label" position="338,47" size="100,25" font="Regular; 19" foregroundColor="#00e5b243" backgroundColor="#31000000" shadowColor="#000000" halign="left" transparent="1">\n\t\t\t\t<convert type="EventTime">StartTime</convert>\n\t\t\t\t  <convert type="ClockToText" />\n\t\t\t\t</widget>\n\t\t\t\t<widget source="Event" render="Label" position="400,47" size="100,25" font="Regular; 19" foregroundColor="#00e5b243" backgroundColor="#31000000" shadowColor="#000000" halign="left" transparent="1">\n\t\t\t\t  <convert type="EventTime">EndTime</convert>\n\t\t\t\t  <convert type="ClockToText">Format:- %H:%M</convert>\n\t\t\t\t</widget>\n\t\t\t\t<widget source="Event" render="Label" position="565,47" size="470,25" font="Regular; 18" foregroundColor="#0053a9ff" backgroundColor="#31000000" transparent="1" halign="left" noWrap="1">\n\t\t\t\t  <convert type="EventName">Name</convert>\n\t\t\t\t</widget>\n\n\t\t\t\t<widget source="Event" render="Label" position="460,47" size="113,25" font="Regular; 19" foregroundColor="#00ffffff" backgroundColor="#31000000" shadowColor="#000000" halign="center" transparent="1">\n\t\t\t\t  <convert type="EventTime">Duration</convert>\n\t\t\t\t  <convert type="ClockToText">InMinutes</convert>\n\t\t\t\t</widget>\n\t\t\t\t<widget source="Event" render="Label" position="341,72" zPosition="1" size="814,116" font="Regular; 18" foregroundColor="#00bbbbbb" backgroundColor="#31000000" shadowColor="#000000" transparent="1" valign="top">\n\t\t\t\t  <convert type="EventName">ExtendedDescription</convert>\n\t\t\t\t</widget>\n\t\t\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/openSPATVGuide/img/red.png" position="53,669" size="35,25" alphatest="blend" transparent="0" />\n\t\t\t\t<widget name="key_red" position="88,669" size="68,24" font="Regular; 17" foregroundColor="#aeaeae" backgroundColor="#000000" shadowColor="#000000" halign="left" valign="center" transparent="1" noWrap="1" />\n\t\t\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/openSPATVGuide/img/green.png" position="165,669" size="35,25" alphatest="blend" />\n\t\t\t\t<widget name="key_green" position="200,669" size="157,24" font="Regular; 17" foregroundColor="#aeaeae" backgroundColor="#000000" shadowColor="#000000" halign="left" valign="center" transparent="1" noWrap="1" />\n\t\t\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/openSPATVGuide/img/yellow.png" position="360,669" size="35,25" alphatest="blend" />\n\t\t\t\t<widget name="key_yellow" position="395,669" size="117,24" font="Regular; 17" foregroundColor="#aeaeae" backgroundColor="#000000" shadowColor="#000000" halign="left" valign="center" transparent="1" noWrap="1" />\n\t\t\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/openSPATVGuide/img/blue.png" position="515,669" size="35,25" alphatest="blend" />\n\t\t\t\t<widget name="key_blue" position="550,669" size="83,24" font="Regular; 17" foregroundColor="#aeaeae" backgroundColor="#000000" shadowColor="#000000" halign="left" valign="center" transparent="1" noWrap="1" />\n\t\t\t\n\t\t\t\t<eLabel backgroundColor="#15243a" position="41,190" size="1193,509" zPosition="-2" />\n\t\t\t\n\t\t\t\t<widget source="session.VideoPicture" render="Pig" position="38,19" size="295,163" zPosition="-1" backgroundColor="transparent2" />\n\t\t\t\t<eLabel name="tapapip" position="36,17" size="299,167" zPosition="-2" backgroundColor="#2b3949" />\n\t\t\t\t<widget source="session.CurrentService" render="Label" position="42,19" size="287,23" font="Regular; 17" transparent="1" valign="center" zPosition="6" backgroundColor="black" foregroundColor="#20ffffcc" noWrap="1" borderColor="#11000000" borderWidth="1">\n\t\t\t\t  <convert type="ServiceName">Name</convert>\n\t\t\t\t</widget>\n\t\t\t\t<eLabel name="tapainfocanal" position="38,19" size="295,23" backgroundColor="#66111111" foregroundColor="#2253a9ff" transparent="0" zPosition="0" />\n\t\t\t\n\t\t\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/openSPATVGuide/img/key_rw.png" position="640,669" size="63,25" alphatest="blend" />\n\t\t\t\t<widget name="key_rw" position="715,669" size="40,24" font="Regular; 17" foregroundColor="#aeaeae" backgroundColor="#000000"  halign="left" valign="center" transparent="1" noWrap="1" />\n\t\t\t\t<eLabel name="smenos1" position="704,686" size="8,2" transparent="0" backgroundColor="#aeaeae" zPosition="21" />\n\t\t\t\t<eLabel name="smas1" position="703,668" size="17,17" text="+" transparent="1" foregroundColor="#aeaeae" zPosition="21" halign="left" font="Regular; 17" valign="center" />\t\t\t\n\t\t\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/openSPATVGuide/img/key_ch.png" position="754,669" size="42,25" alphatest="blend" />\n\t\t\t\t<widget name="key_ch" position="809,669" size="68,24" font="Regular; 17" foregroundColor="#aeaeae" backgroundColor="#000000" halign="left" valign="center" transparent="1" noWrap="1" />\n\t\t\t\t<eLabel name="smenos1" position="798,686" size="8,2" transparent="0" backgroundColor="#aeaeae" zPosition="21" />\n\t\t\t\t<eLabel name="smas1" position="797,668" size="17,17" text="+" transparent="1" foregroundColor="#aeaeae" zPosition="21" halign="left" font="Regular; 17" valign="center" />\t\t\t\t\t\n\n\t\t\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/openSPATVGuide/img/key_menu.png" position="882,669" size="45,25" alphatest="blend" />\n\t\t\t\t<widget name="key_menu" position="927,669" size="90,24" font="Regular; 17" foregroundColor="#aeaeae" backgroundColor="#000000" halign="left" valign="center" transparent="1" noWrap="1" />\n\n\t\t\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/openSPATVGuide/img/key_info.png" position="1017,669" size="35,25" alphatest="blend" />\n\t\t\t\t<widget name="key_info" position="1050,669" size="105,24" font="Regular; 17" foregroundColor="#aeaeae" backgroundColor="#000000"  halign="left" valign="center" transparent="1" noWrap="1" />\n\n\t\t\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/openSPATVGuide/img/key_ok.png" position="1154,669" size="35,25" alphatest="blend" />\n\t\t\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/openSPATVGuide/img/key_exit.png" position="1187,669" size="35,25" alphatest="blend" />\n\t\t\t\t<widget name="sitimer" position="547,19" size="24,24" zPosition="25" alphatest="blend" />\n\t\t\t\t<widget name="nom_lista" position="52,193" size="184,24" font="Regular; 18" halign="left" foregroundColor="#89919c" backgroundColor="#000000" transparent="1" valign="center" zPosition="10" noWrap="1" />\n\n\t\t\t\t<widget name="nom_canal" position="1041,49" size="200,20" font="Regular; 17" halign="right" foregroundColor="#ffffff" backgroundColor="#000000" transparent="1" valign="center" zPosition="10" noWrap="1" />\t\t\t\n\t\t\t\t<widget name="img_picon" position="1161,85" size="81,50" zPosition="20" />\t\n\t\t\t\t<widget name="tapa_picon" position="1160,84" size="83,52" zPosition="19" transparent="0" backgroundColor="#4b5460" />\n\t\t\t\n\t\t\t\t<widget source="Event" render="Label" position="1160,162" size="83,25" font="Regular; 17" foregroundColor="#949494" transparent="1" halign="right" noWrap="1">\n\t\t\t\t  <convert type="EventRating">Rating</convert>\n\t\t\t\t</widget>\t\t\n\t\t\t\t<widget name="genero" position="948,47" size="270,25" zPosition="19" transparent="0" backgroundColor="#030813" font="Regular; 16" foregroundColor="#949494" halign="right" valign="bottom" noWrap="1" />\n\t\t\t\t<!--<widget name="genero_arr" position="1000,47" size="241,3" zPosition="20" transparent="0" backgroundColor="#030813" />-->\n\t\t\t\t<widget name="img_gen" position="1218,49" size="23,23" zPosition="19" transparent="0" alphatest="blend"/>\t\n\t\t\t</screen>'

    def __init__(self, session, services, zapFunc = None, bouquetChangeCB = None, bouquetname = ''):
        global SpaList
        Screen.__init__(self, session)
        HelpableScreen.__init__(self)
        self.bouquetChangeCB = bouquetChangeCB
        now = time()
        self.poslistax = -1
        self.poslistay = -1
        tmp = now % 900
        self.ask_time = now - tmp
        self.closeRecursive = False
        self.setTitle(_('Electronic Programa Guide (EPG)'))
        self['key_red'] = Button('')
        self['key_green'] = Button('')
        self['key_yellow'] = Button('')
        self['key_blue'] = Button('')
        self['key_rw'] = Button(_('4h.'))
        self['key_ch'] = Button(_('Page'))
        self['key_info'] = Button(_('Event Info'))
        self['key_menu'] = Button(_('Options'))
        self['nom_lista'] = Label(bouquetname)
        self.key_red_choice = self.EMPTY
        self.key_green_choice = self.EMPTY
        self.key_yellow_choice = self.EMPTY
        self.key_blue_choice = self.EMPTY
        self['timeline_text'] = TimelineText()
        self['Event'] = Event()
        self.time_lines = []
        for x in (0, 1, 2, 3, 4, 5):
            pm = Pixmap()
            self.time_lines.append(pm)
            self['timeline%d' % x] = pm

        self['timeline_now'] = Pixmap()
        self.services = services
        self.zapFunc = zapFunc
        self['list'] = SpaEPGList(selChangedCB=self.onSelectionChanged, timer=self.session.nav.RecordTimer, time_epoch=prev_time_period, overjump_empty=overjump)
        SpaList = self['list']
        self['actions01'] = HelpableActionMap(self, 'CTVGuideActions', {'CnextBouquet': (self.key2, _('Page Down')),
         'CprevBouquet': (self.key8, _('Page Up'))}, -1)
        self['actions0'] = HelpableActionMap(self, 'CTVGuideActions', {'CBack': (self.prevPressed2, _('Go to -24h.').replace('24', '4')),
         'CFwd': (self.nextPressed2, _('Go to +24h.').replace('24', '4'))}, -1)
        self['actions1'] = HelpableActionMap(self, 'CTVGuideActions', {'COK': (self.zap, _('Zap and Exit')),
         'Ccancel': (self.SpaClose, _('Exit')),
         'CInfo': (self.infoKeyPressed, _('Show Event Information'))}, -1)
        self['actions2'] = HelpableActionMap(self, 'CTVGuideActions', {'C1': (self.key5, _('Go top')),
         'C2': (self.key9, _('Go to prime time')),
         'C3': (self.enterDateTime, _('Enter Date Time')),
         'C4': (self.SpaSearch, _('Search in EPG')),
         'C5': (self.inet, _('Search in Internet Database movies')),
         'C6': (self.SpaBouquetlist, _('Select bouquet list'))}, -1)
        self['actions20'] = HelpableActionMap(self, 'CTVGuideActions', {'C7': (self.prevPressed, _('Go to -24h.')),
         'C9': (self.nextPressed, _('Go to +24h.'))}, -1)
        self['actions3'] = HelpableActionMap(self, 'CTVGuideActions', {'CRecord': (self.record_manager, _('Show timer list')),
         'CRed': (self.zapTo, _('Zap to selected channel')),
         'CGreen': (self.timerAdd, _('Add record timer')),
         'CYellow': (self.SpaInfo, _('Show current Channel single EPG')),
         'CBlue': (self.MenuBuscar, _('Search in epg list or internet movie database'))}, -1)
        self['actions30'] = HelpableActionMap(self, 'CTVGuideActions', {'CMenu': (self.MenuOpciones, _('Show options menu')),
         'Cpvr': (self.cambiaVista, _('Show') + '/' + _('Hide') + ' ' + _('channels picons'))}, -1)
        self['actions4'] = HelpableActionMap(self, 'CTVGuideActions', {'Cup': self.kup,
         'Cdown': self.kdown,
         'Cleft': self.leftPressed,
         'Cright': self.rightPressed,
         'C0': self.showHelp,
         'C8': self.infoKeyPressed,
         'power': self.apagar}, -1)
        self['key_red'].setText(_('Zap'))
        self['key_green'].setText(_('Timer'))
        self['key_yellow'].setText(_('Channel EPG'))
        self['key_blue'].setText(_('Search') + '...')
        self.updateTimelineTimer = eTimer()
        self.picontimer = eTimer()
        self.picontimer.callback.append(self.actualizapicon)
        self.cargaguia = eTimer()
        self.cargaguia.callback.append(self.onCreate)
        self.updateTimelineTimer.start(60000)
        self.updateTimelineTimer.callback.append(self.moveTimeLines)
        self.iniciadoLista = True
        self.onShow.append(self.almostrar)
        self.seg_plano = None
        self['date'] = Label()
        self['selector'] = Label()
        self['tapa_picon'] = Label()
        self['nom_canal'] = Label()
        self['tapa_picon'].hide()
        self['espera'] = Label(_('Loading epg data...'))
        self['list'].hide()
        self['genero'] = Label()
        self['genero'].hide()
        self['selectorpixmap'] = Pixmap()
        self['selector_r'] = Pixmap()
        self['img_gen'] = Pixmap()
        self['img_picon'] = Pixmap()
        self.picloadpicon = ePicLoad()
        self.picloadpicon.PictureData.get().append(self.pintaPicon)
        self.oldservice = None
        self['selectorservice'] = Pixmap()
        self['sitimer'] = Pixmap()
        self['sitimer'].hide()
        self['selector'].hide()
        self['selectorservice'].hide()
        self['selectorpixmap'].hide()
        self['selector_r'].hide()
        self.movido = False
        self.timeract = eTimer()
        self.timeract.callback.append(self.actualizaclock)

    def reajusta(self):
        alto = SpaEPGheight
        ancho = self['list'].instance.size().width()
        temp2 = (ancho, alto)
        self['list'].instance.resize(eSize(*temp2))
        temp2 = (spa_left16 - 2, self['nom_lista'].instance.size().height())
        self['nom_lista'].instance.resize(eSize(*temp2))
        ancho = ancho - spa_left16
        temp2 = (ancho, alto)
        self['espera'].instance.move(ePoint(self['list'].instance.position().x() + spa_left16, self['list'].instance.position().y()))
        self['espera'].instance.resize(eSize(*temp2))
        self['list'].setItemsPerPage()

    def apagar(self):
        from Screens import Standby
        Notifications.AddNotification(Standby.Standby)
        self.SpaClose()

    def MenuOpciones(self):
        nkeys = []
        askList = []
        askList.append((_('Go top'), 'top'))
        nkeys.append('1')
        askList.append((_('Go to prime time') + ' (' + str(SpaPrimetime1) + ':00)', 'prime'))
        nkeys.append('2')
        askList.append((_('Enter Date Time'), 'time'))
        nkeys.append('3')
        askList.append(('--', 'nada'))
        nkeys.append('')
        askList.append((_('Search in EPG'), 'epg'))
        nkeys.append('4')
        try:
            cur = self['list'].getCurrent()
            serviceref = cur[1]
            askList.append((_('Search in') + ' [' + serviceref.getServiceName() + ']', 'epgc'))
            nkeys.append('')
        except:
            pass

        askList.append((_('Search by genre'), 'gen1'))
        nkeys.append('')
        askList.append((_('Search in Internet Database movies'), 'inet'))
        nkeys.append('5')
        askList.append(('--', 'nada'))
        nkeys.append('')
        askList.append((_('Select bouquet list'), 'sw'))
        nkeys.append('6')
        askList.append(('--', 'nada'))
        nkeys.append('')
        askList.append((_('Go to -24h.'), '-24'))
        nkeys.append('7')
        askList.append((_('Show Event Information'), 'event'))
        nkeys.append('8')
        askList.append((_('Go to +24h.'), '+24'))
        nkeys.append('9')
        askList.append(('--', 'nada'))
        nkeys.append('')
        askList.append((_('Timer list'), 'record'))
        nkeys.append('')
        valor = _('Change to list mode with picons')
        if config.plugins.openSPATVGuide.show_picons.value:
            valor = _('Change to list mode compact (without picons)')
        askList.append((_(valor), 'picons'))
        nkeys.append('')
        valor = 'Show'
        if config.plugins.openSPATVGuide.show_colors.value:
            valor = 'Hide'
        askList.append((_(valor) + ' ' + _('genre colors in list'), 'colors'))
        nkeys.append('')
        askList.append((_('Graphic Help'), 'help'))
        nkeys.append('0')
        dei = self.session.openWithCallback(self.callbackmenu, ChoiceBox, keys=nkeys, title=_('EPG Options') + '.\n' + _('Select option') + ':', list=askList)

    def record_manager(self):
        try:
            from Screens.TimerEdit import TimerEditList
            self.session.open(TimerEditList)
        except:
            pass

    def MenuBuscar(self):
        nkeys = []
        askList = []
        askList.append((_('Search in EPG') + ' (' + _('All channels') + ')', 'epg'))
        nkeys.append('1')
        try:
            cur = self['list'].getCurrent()
            serviceref = cur[1]
            askList.append((_('Search in') + ' [' + serviceref.getServiceName() + ']', 'epgc'))
            nkeys.append('2')
        except:
            pass

        askList.append(('--', 'nada'))
        nkeys.append('')
        askList.append((_('Search by genre') + ' (' + _('All channels') + ')', 'gen1'))
        nkeys.append('3')
        try:
            cur = self['list'].getCurrent()
            serviceref = cur[1]
            askList.append((_('Search by genre') + ' [' + serviceref.getServiceName() + ']', 'gen2'))
            nkeys.append('4')
        except:
            pass

        askList.append(('--', 'nada'))
        nkeys.append('')
        askList.append((_('Search in Internet Database movies'), 'inet'))
        nkeys.append('5')
        dei = self.session.openWithCallback(self.callbackmenu, ChoiceBox, keys=nkeys, title=_('Search options') + '.\n' + _('Select option') + ':', list=askList)

    def inet(self):
        self.callbackmenu(['inet', 'inet'])

    def cambiaColores(self):
        config.plugins.openSPATVGuide.show_colors.value = not config.plugins.openSPATVGuide.show_colors.value
        config.plugins.openSPATVGuide.show_colors.save()
        config.plugins.openSPATVGuide.save()
        resizaLista()
        self.onCreate()

    def cambiaVista(self):
        config.plugins.openSPATVGuide.show_picons.value = not config.plugins.openSPATVGuide.show_picons.value
        config.plugins.openSPATVGuide.show_picons.save()
        config.plugins.openSPATVGuide.save()
        resizaLista()
        self.onCreate()

    def callbackmenu(self, answer = None):
        answer = answer and answer[1]
        if answer:
            if answer == 'epg':
                self.SpaSearch(False, False, self.services, False)
            elif answer == 'gen1':
                self.SpaSearch(True, False, self.services)
            elif answer == 'gen2':
                self.SpaSearch(True, False, self.services, True)
            elif answer == 'picons':
                self.cambiaVista()
            elif answer == 'colors':
                self.cambiaColores()
            elif answer == 'epgc':
                self.SpaSearch(False, True, self.services, True)
            elif answer == 'help':
                self.showHelp()
            elif answer == 'prime':
                self.key9()
            elif answer == 'top':
                self.key5()
            elif answer == '+24':
                self.nextPressed()
            elif answer == '-24':
                self.prevPressed()
            elif answer == 'time':
                self.enterDateTime()
            elif answer == 'sw':
                self.SpaBouquetlist()
            elif answer == 'record':
                self.record_manager()
            elif answer == 'event':
                self.infoKeyPressed()
            elif answer == 'single':
                self.SpaInfoLong()
            elif answer == 'inet':
                try:
                    cur = self['list'].getCurrent()
                    event = cur[0]
                    titulo = event.getEventName()
                except:
                    titulo = ''

                try:
                    from Plugins.Extensions.spzIMDB.plugin import spzIMDB
                    spzIMDB(self.session, tbusqueda=titulo)
                except:
                    pass

    def SpaInfo(self):
        cur = self['list'].getCurrent()
        event = cur[0]
        eservice = cur[1]
        if eservice:
            self.session.open(spaEPGSelection, eservice.ref)

    def SpaInfoLong(self):
        pass

    def SpaSearch(self, txt = None, canalactivo = False, genero = None, encanal = False):
        serviceref = None
        try:
            cur = self['list'].getCurrent()
            event = cur[0]
            name = event.getEventName()
            if canalactivo or True:
                serviceref = cur[1]
        except:
            name = ''

        if genero and txt:
            name = ':genero:'
        elif name == '' or name.upper() == _('No Information').upper() or name.upper() == '(' + _('No Information').upper() + ')':
            name = 'xNAx'
        if EPGSearch is not None:
            self.session.open(EPGSearch, name, serviceref, False, genero, encanal)

    def prevPressed(self):
        ant = None
        try:
            ant = self['list'].cur_event
        except:
            ant = None

        spahilf = prev_time_period
        if spahilf == 240:
            for i in range(6):
                self.updEvent(-2)

        try:
            if str(ant) == str(self['list'].cur_event):
                self.key5(False)
                return
        except:
            pass

        oldevent = self['list'].cur_event
        try:
            self['list'].cur_event = 0
            self['list'].selEntry(0, True)
        except:
            try:
                self['list'].cur_event = oldevent
                self['list'].selEntry(0, True)
            except:
                pass

    def nextPressed(self):
        spahilf = prev_time_period
        if spahilf == 240:
            for i in range(6):
                self.updEvent(+2)

    def prevPressed2(self):
        ant = None
        try:
            ant = self['list'].cur_event
        except:
            ant = None

        spahilf = prev_time_period
        if spahilf == 240:
            self.updEvent(-2)
        try:
            if str(ant) == str(self['list'].cur_event):
                self.key5(False)
                return
        except:
            pass

        oldevent = self['list'].cur_event
        try:
            self['list'].cur_event = 0
            self['list'].selEntry(0, True)
        except:
            try:
                self['list'].cur_event = oldevent
                self['list'].selEntry(0, True)
            except:
                pass

    def nextPressed2(self):
        spahilf = prev_time_period
        if spahilf == 240:
            self.updEvent(+2)

    def leftPressed(self):
        ant = None
        try:
            ant = self['list'].cur_event
        except:
            ant = None

        self.updEvent(-1)
        try:
            cur = self['list'].getCurrent()
            event = cur[0]
            if event is None:
                self.key5(False)
        except:
            self.key5(False)

        try:
            if str(ant) == str(self['list'].cur_event):
                self.key5(False)
        except:
            pass

    def rightPressed(self):
        self.updEvent(+1)

    def updEvent(self, dir, visible = True):
        ret = self['list'].selEntry(dir, visible)
        if ret:
            self.moveTimeLines(True)

    def key2(self):
        self['list'].instance.moveSelection(self['list'].instance.pageUp)

    def kup(self):
        try:
            nindex = self['list'].instance.getCurrentIndex()
            if nindex > 0:
                self['list'].instance.moveSelectionTo(nindex - 1)
            else:
                self['list'].instance.moveSelectionTo(len(self['list'].list) - 1)
        except:
            pass

    def kdown(self):
        try:
            nindex = self['list'].instance.getCurrentIndex()
            if nindex >= len(self['list'].list) - 1:
                self['list'].instance.moveSelectionTo(0)
            else:
                self['list'].instance.moveSelectionTo(nindex + 1)
        except:
            pass

    def key5(self, ira1 = True):
        if ira1:
            self['list'].instance.moveSelectionTo(0)
        now = time()
        tmp = now % 900
        spatime = now - tmp
        self['list'].resetOffset()
        self['list'].fillSpaTVGuide(self.services, spatime)
        self.moveTimeLines(True)
        self.movido = False

    def key8(self):
        self['list'].instance.moveSelection(self['list'].instance.pageDown)

    def key9(self):
        spatime = localtime(self['list'].getTimeBase())
        hilf = (spatime[0],
         spatime[1],
         spatime[2],
         SpaPrimetime1 - 1,
         SpaPrimetime2,
         0,
         spatime[6],
         spatime[7],
         spatime[8])
        spatime = mktime(hilf)
        self['list'].resetOffset()
        self['list'].fillSpaTVGuide(self.services, spatime)
        self.moveTimeLines(True)

    def nextBouquet(self):
        if self.bouquetChangeCB:
            self.bouquetChangeCB(1, self)

    def prevBouquet(self):
        if self.bouquetChangeCB:
            self.bouquetChangeCB(-1, self)

    def SpaBouquetlist(self):
        global bouquetSel
        global Session
        bouquetSel = Session.openWithCallback(closed, BouquetSelector, bouquets, openBouquetEPG, enableWrapAround=True)
        dlg_stack.append(bouquetSel)

    def enterDateTime(self):
        global prev_time
        global prev_fecha
        hora = localtime()
        try:
            cur = self['list'].getCurrent()
            event = cur[0]
            if event is not None:
                beg = event.getBeginTime() + 14400
                hora = localtime(beg)
        except:
            pass

        t2 = hora
        cdia = str(int(strftime('%d', t2)))
        cmes = str(strftime('%m', t2))
        cano = str(strftime('%Y', t2))
        tiempo = mktime(strptime(cdia + ' ' + cmes + ' ' + cano, '%d %m %Y'))
        prev_fecha = ConfigDateTime(default=tiempo, formatstring=_('%d.%B %Y'), increment=86400)
        prev_time = ConfigClock(default=mktime(hora))
        dei = self.session.openWithCallback(self.onDateTimeInputClosed, TimeDateInput, prev_time, prev_fecha)
        dei.setTitle(_('Enter Date Time') + ' ')

    def onDateTimeInputClosed(self, ret):
        if len(ret) > 1:
            if ret[0]:
                self.ask_time = ret[1]
                l = self['list']
                l.resetOffset()
                l.fillSpaTVGuide(self.services, ret[1])
                self.moveTimeLines(True)

    def SpaClose(self):
        self.closeRecursive = True
        ref = self['list'].getCurrent()[1]
        self.closeScreen()

    def closeScreen(self):
        global SpaList
        SpaList = None
        self.close(self.closeRecursive)

    def infoKeyPressed(self):
        cur = self['list'].getCurrent()
        event = cur[0]
        service = cur[1]
        if event is not None:
            self.session.open(SpaViewSimple, event, service, self.eventViewCallback, self.openSimilarList)

    def openSimilarList(self, eventid, refstr):
        self.session.open(EPGSelection, refstr, None, eventid)

    def setServices(self, services):
        self.services = services
        self.alInicio()

    def almostrar(self):
        if self.iniciadoLista:
            self.iniciadoLista = False
            self.alInicio()
        else:
            self.actualizaclock()

    def alInicio(self):
        self['espera'].setText(_('Loading epg data...'))
        self['list'].hide()
        self['timeline_now'].hide()
        self['selector'].hide()
        self['selectorservice'].hide()
        self['selectorpixmap'].hide()
        self['selector_r'].hide()
        self.cargaguia.start(100, True)

    def onCreate(self):
        self.reajusta()
        if self['list'].epgcache == None:
            self['list'].epgcache = eEPGCache.getInstance()
        self['list'].curr_refspa = self.session.nav.getCurrentlyPlayingServiceReference()
        self['list'].fillSpaTVGuide(self.services, self.ask_time)
        self['timeline_now'].show()
        self['espera'].setText(' ')
        self['list'].show()
        self['timeline_now'].show()
        self['selector'].show()
        self['selectorservice'].show()
        self['selectorpixmap'].show()
        self['list'].moveToService(self.session.nav.getCurrentlyPlayingServiceReference())
        self.moveTimeLines()
        if channel1:
            self['list'].instance.moveSelectionTo(0)
        self['timeline_now'].show()
        self.picloadpicon.setPara((self['img_picon'].instance.size().width(),
         self['img_picon'].instance.size().height(),
         1,
         1,
         1,
         1,
         '#000000'))
        self.actualizapiconT()

    def eventViewCallback(self, setEvent, setService, val):
        l = self['list']
        old = l.getCurrent()
        self.updEvent(val, False)
        cur = l.getCurrent()
        if cur[0] is None and cur[1].ref != old[1].ref:
            self.eventViewCallback(setEvent, setService, val)
        else:
            setService(cur[1])
            setEvent(cur[0])
            self.actualizaclock()

    def zapTo(self):
        if self.zapFunc:
            self.closeRecursive = True
            ref = self['list'].getCurrent()[1]
            xref = ref.ref
            try:
                cret = ref.ref
                if cret.flags & eServiceReference.isGroup:
                    xref = getBestPlayableServiceReference(cret, eServiceReference(), True)
            except:
                pass

            self['list'].curr_refspa = xref
            self['list'].fillSpaTVGuide(None)
            if ref:
                self.zapFunc(ref.ref)

    def zap(self):
        if self.zapFunc:
            self.closeRecursive = True
            ref = self['list'].getCurrent()[1]
            if ref:
                self.zapFunc(ref.ref)
                self.closeScreen()

    def eventSelected(self):
        self.infoKeyPressed()

    def removeTimer(self, timer):
        timer.afterEvent = AFTEREVENT.NONE
        self.session.nav.RecordTimer.removeEntry(timer)
        self['key_green'].setText(_('Timer'))
        self.key_green_choice = self.ADD_TIMER
        self.actualizaclock()

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
            self.key_green_choice = self.REMOVE_TIMER
            self.actualizaclock()
        else:
            self.key_green_choice = self.ADD_TIMER

    def finishSanityCorrection(self, answer):
        self.finishedAdd(answer)

    def actualizaclock(self):
        self.timeract.stop()
        cur = self['list'].getCurrent()
        event = cur[0]
        serviceref = cur[1]
        self['img_gen'].hide()
        if event is None:
            self['sitimer'].hide()
            self['selector_r'].hide()
            self['genero'].hide()
            return
        eventid = event.getEventId()
        refstr = serviceref.ref.toString()
        try:
            tuplagenero = getgenero(event, 23)
            ergenero = tuplagenero[0]
            if ergenero != '':
                self['genero'].setText(ergenero)
                self['genero'].show()
                if tuplagenero[2]:
                    self['img_gen'].instance.setPixmapFromFile(tuplagenero[2])
                    self['img_gen'].instance.setScale(1)
                    self['img_gen'].show()
            else:
                self['genero'].hide()
        except:
            self['genero'].hide()

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
            nombrep = nombrepix(nomrec)
            if nombrep:
                self['sitimer'].instance.setPixmapFromFile(nombrep)
                self['sitimer'].show()
                if nomrec == 'epgclock':
                    self['selector_r'].show()
                    return
        self['sitimer'].hide()
        self['selector_r'].hide()

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

    def timersel(self):
        self['img_gen'].hide()
        self['genero'].hide()
        self.timeract.stop()
        self.timeract.start(700, True)

    def posicionasel(self):
        self.timeract.stop()
        self.timersel()
        obj = self['list']
        cur_service = obj.cur_service
        try:
            serviceref = self['list'].getCurrent()[1]
            self['nom_canal'].setText(serviceref.getServiceName())
        except:
            self['nom_canal'].setText('')

        service = cur_service[0]
        valid_event = obj.cur_event is not None
        if self.poslistax == -1:
            self.poslistax = self['list'].instance.position().x()
            self.poslistay = self['list'].instance.position().y()
        if cur_service and valid_event:
            entries = cur_service[2]
            entry = entries[obj.cur_event]
            time_base = obj.time_base + obj.offs * obj.time_epoch * 60
            xpos, width = obj.calcEntryPosAndWidth(obj.event_rect, time_base, obj.time_epoch, entry[2], entry[3])
            texto = entry[1]
        else:
            texto = '(' + _('No Information') + ')'
            xpos = obj.event_rect.left()
            width = obj.event_rect.width()
        maxpag = items_per_page
        nindex = self['list'].instance.getCurrentIndex()
        npag = int(nindex / maxpag)
        xpos = xpos + 0
        ypos = (nindex - npag * maxpag) * Spa16 + 1
        temp = (width - 3, Spa16 - 4)
        temp2 = (width - 4, Spa16 - 5)
        px = xpos + self.poslistax + 1
        py = ypos + self.poslistay + 2
        epunto = ePoint(px, py)
        self['selector'].instance.move(epunto)
        self['selector'].instance.resize(eSize(*temp2))
        self['selectorpixmap'].instance.move(epunto)
        self['selector_r'].instance.move(ePoint(px + 1, py + 1))
        self['selectorpixmap'].instance.resize(eSize(*temp))
        self.picontimer.stop()
        if self.oldservice != service:
            self['tapa_picon'].hide()
            self['img_picon'].hide()
            self.oldservice = service
            self['selectorservice'].instance.move(ePoint(self.poslistax + 3, py + int(Spa16 / 4)))
            self.picontimer.start(700, True)
        self['selector'].setText('   ' + texto)
        obj = None

    def actualizapiconT(self):
        self.picontimer.stop()
        self.picontimer.start(700, True)

    def actualizapicon(self):
        self.picontimer.stop()
        service = self['list'].cur_service[0]
        if not service:
            return
        picon = rutapiconS(self['list'].getmejor(service))
        if fileExists(picon) and 'picon_default.png' not in picon:
            self.picloadpicon.startDecode(picon)
        else:
            self['img_picon'].hide()
            self['tapa_picon'].hide()

    def pintaPicon(self, picInfo = None):
        ptr = self.picloadpicon.getData()
        if ptr != None:
            self['img_picon'].instance.setPixmap(ptr.__deref__())
            self['img_picon'].show()
            self['tapa_picon'].show()
        else:
            self['img_picon'].hide()
            self['tapa_picon'].hide()

    def onSelectionChanged(self):
        self.posicionasel()
        cur = self['list'].getCurrent()
        if cur is None:
            if self.key_green_choice != self.EMPTY:
                self['key_green'].setText('')
                self.key_green_choice = self.EMPTY
            return
        event = cur[0]
        self['Event'].newEvent(event)
        count = self['list'].getCurrentChangeCount()
        days = [_('Monday'),
         _('Tuesday'),
         _('Wednesday'),
         _('Thursday'),
         _('Friday'),
         _('Saturday'),
         _('Sunday')]
        datestr = ' (' + _('No events') + ')'
        if event is not None:
            now = time()
            beg = event.getBeginTime()
            nowTime = localtime(now)
            begTime = localtime(beg)
            cmes = str(strftime('%B', begTime))
            if nowTime[2] != begTime[2]:
                datestr = ' %s  %d-%s' % (days[begTime[6]], begTime[2], cmes)
            else:
                datestr = ' %s  %d-%s' % (_('Today'), begTime[2], cmes)
        self['date'].setText(datestr)

    def moveTimeLines(self, force = False):
        self.updateTimelineTimer.start((60 - int(time()) % 60) * 1000)
        l = self['list']
        event_rect = l.getEventRect()
        time_epoch = l.getTimeEpoch()
        time_base = l.getTimeBase()
        if event_rect is None or time_epoch is None or time_base is None:
            return
        time_steps = time_epoch > 180 and 60 or 30
        num_lines = time_epoch / time_steps
        incWidth = event_rect.width() / num_lines
        pos = event_rect.left()
        timeline_entries = []
        x = 0
        changecount = 0
        for line in self.time_lines:
            old_pos = line.position
            new_pos = (x == num_lines and event_rect.left() + event_rect.width() or pos, old_pos[1])
            if not x or x >= num_lines:
                line.visible = False
            else:
                if old_pos != new_pos:
                    line.setPosition(new_pos[0], new_pos[1])
                    changecount += 1
                line.visible = True
            if not x or line.visible:
                timeline_entries.append((time_base + x * time_steps * 60, new_pos[0]))
                timeline_entries.append((time_base + x * time_steps * 60 + time_steps * 30, new_pos[0] + incWidth / 2))
            x += 1
            pos += incWidth

        if changecount or force:
            self['timeline_text'].setEntries(timeline_entries)
        now = time()
        timeline_now = self['timeline_now']
        if now >= time_base and now < time_base + time_epoch * 60:
            xpos = int((now - time_base) * event_rect.width() / (time_epoch * 60) - timeline_now.instance.size().width() / 2)
            old_pos = timeline_now.position
            new_pos = (xpos + event_rect.left(), old_pos[1])
            if old_pos != new_pos:
                timeline_now.setPosition(new_pos[0], new_pos[1])
            timeline_now.visible = True
        else:
            timeline_now.visible = False
        l.l.invalidate()


def zapToService(service):
    global Servicelist
    global epg_bouquet
    if service is not None:
        if Servicelist.getRoot() != epg_bouquet:
            Servicelist.clearPath()
            if Servicelist.bouquet_root != epg_bouquet:
                Servicelist.enterPath(Servicelist.bouquet_root)
            Servicelist.enterPath(epg_bouquet)
        Servicelist.setCurrentSelection(service)
        Servicelist.zap()


def getBouquetServices(bouquet):
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


def cleanup():
    global Servicelist
    global Session
    Session = None
    Servicelist = None


def closed(ret = False):
    global bouquetSel
    closedScreen = dlg_stack.pop()
    if bouquetSel and closedScreen == bouquetSel:
        bouquetSel = None
    dlgs = len(dlg_stack)
    if ret and dlgs > 0:
        dlg_stack[dlgs - 1].close(dlgs > 1)
    if dlgs <= 0:
        cleanup()


def openBouquetEPG(bouquet):
    global epg_bouquet
    services = getBouquetServices(bouquet)
    if len(services):
        epg_bouquet = bouquet
        dlg_stack.append(Session.openWithCallback(closed, openSPATVGuide, services, zapToService, changeBouquetCB, ServiceReference(epg_bouquet).getServiceName()))
        return True
    return False


def changeBouquetCB(direction, epg):
    global epg_bouquet
    global man_bouquets
    global spa_bouquets
    if bouquetSel:
        if direction > 0:
            bouquetSel.down()
        else:
            bouquetSel.up()
        bouquet = bouquetSel.getCurrent()
        services = getBouquetServices(bouquet)
        if len(services):
            epg_bouquet = bouquet
            epg.setServices(services)
    else:
        for spa in range(len(spa_bouquets)):
            if spa_bouquets[spa][1] == man_bouquets:
                break

        spa = spa + 1
        if direction > 0:
            if spa == len(spa_bouquets):
                man = 0
            else:
                man = spa
        elif spa == 1:
            man = len(spa_bouquets)
            man = man - 1
        else:
            man = spa - 2
        services = getBouquetServices(spa_bouquets[man][1])
        if len(services):
            man_bouquets = spa_bouquets[man][1]
            epg_bouquet = spa_bouquets[man][1]
            epg.setServices(services)


def main(session, servicelist, **kwargs):
    global Servicelist
    global bouquetSel
    global man_bouquets
    global bouquets
    global Session
    if not fileExists('/usr/bin/chkvs'):
        Notifications.AddPopup(text=_('Not spazeTeam image found!\nMore info in www.azboxhd.es'), type=MessageBox.TYPE_ERROR, timeout=10, id='spzspaguide')
        return
    Session = session
    withCallback = True
    Servicelist = servicelist
    man_bouquets = Servicelist.getRoot()
    bouquets = Servicelist.getBouquetList()
    del spa_bouquets[:]
    for spa in range(len(bouquets)):
        services = getBouquetServices(bouquets[spa][1])
        if len(services):
            spa_bouquets.append(bouquets[spa])

    services = getBouquetServices(man_bouquets)
    if bouquets is None:
        cnt = 0
    else:
        cnt = len(bouquets)
    if len(services):
        cnt = 0
    if cnt > 1:
        if withCallback:
            bouquetSel = Session.openWithCallback(closed, BouquetSelector, bouquets, openBouquetEPG, enableWrapAround=True)
            dlg_stack.append(bouquetSel)
    elif cnt == 1:
        openBouquetEPG(bouquets[0][1], withCallback)
        if not openBouquetEPG(bouquets[0][1]):
            cleanup()
    elif autostart_bouquet:
        bouquetSel = Session.openWithCallback(closed, BouquetSelector, bouquets, openBouquetEPG, enableWrapAround=True)
        dlg_stack.append(bouquetSel)
    elif cnt == 0:
        if not openBouquetEPG(man_bouquets):
            cleanup()


def autostart(reason, **kwargs):
    if reason == 0:
        try:
            changeEventView()
        except Exception:
            pass
