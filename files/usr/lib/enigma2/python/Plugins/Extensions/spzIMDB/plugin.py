from enigma import iPlayableService, eTimer, eWidget, eRect, eServiceCenter, eServiceReference, iServiceInformation, iServiceKeys, getDesktop, eListboxPythonMultiContent, gFont, BT_SCALE, BT_KEEP_ASPECT_RATIO
from Screens.Screen import Screen
from Screens.MinuteInput import MinuteInput
from Screens.ServiceInfo import ServiceInfoList, ServiceInfoListEntry
from Screens.HelpMenu import HelpableScreen
from Screens.MessageBox import MessageBox
from Screens.ChoiceBox import ChoiceBox
from Screens.InfoBarGenerics import InfoBarSeek, InfoBarPVRState, InfoBarCueSheetSupport, InfoBarShowHide, InfoBarNotifications, InfoBarAudioSelection, InfoBarSubtitleSupport
from Components.ProgressBar import ProgressBar
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaBlend
from Tools.LoadPixmap import LoadPixmap
from Screens.ChannelSelection import SimpleChannelSelection
from Components.ActionMap import ActionMap, NumberActionMap, HelpableActionMap
from Components.Pixmap import Pixmap, MovingPixmap
from Components.Label import Label
from Components.Sources.List import List
from Components.Sources.StaticText import StaticText
from Components.Button import Button
from Components.ServiceEventTracker import ServiceEventTracker
from Components.ConfigList import ConfigList, ConfigListScreen
from Components.config import *
from Components.Harddisk import harddiskmanager
from Tools.Directories import resolveFilename, pathExists, createDir, SCOPE_MEDIA
from Components.Sources.StaticText import StaticText
from Components.MenuList import MenuList
from Components.ServiceEventTracker import ServiceEventTracker, InfoBarBase
from Components.Sources.ServiceEvent import ServiceEvent
from Components.ScrollLabel import ScrollLabel
from Plugins.Plugin import PluginDescriptor
from enigma import ePicLoad
from twisted.web.client import downloadPage
from Components.AVSwitch import AVSwitch
import os
from os import path as os_path, remove as os_remove, listdir as os_listdir, system
import time
import re
import WebGrabber
import Utf8
from os import environ
import gettext
from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE
from Plugins.Extensions.spazeMenu.plugin import esHD, fhd
lang = language.getLanguage()
environ['LANGUAGE'] = lang[:2]
lenguaje = str(lang[:2])
gettext.bindtextdomain('enigma2', resolveFilename(SCOPE_LANGUAGE))
gettext.textdomain('enigma2')
gettext.bindtextdomain('spzIMDB', '%s%s' % (resolveFilename(SCOPE_PLUGINS), 'Extensions/spzIMDB/locale/'))

def _(txt):
    t = gettext.dgettext('spzIMDB', txt)
    if t == txt:
        t = gettext.gettext(txt)
    return t


re_digits_nondigits = re.compile('\\d+|\\D+')

def FormatWithCommas(value, sepmil = '.', sepdec = ',', ndecimales = 2, cmoneda = ''):
    format = '%.' + str(ndecimales) + 'f' + cmoneda
    if value == None:
        return ''
    if str(value) == '':
        return ''
    cvalue = str(value)
    fvalue = float(value)
    parts = re_digits_nondigits.findall(format % (fvalue,))
    for i in xrange(len(parts)):
        s = parts[i]
        if s.isdigit():
            parts[i] = _commafy(s)
            break

    return ''.join(parts).replace('.', sepdec).replace('#', sepmil)


def _commafy(s):
    r = []
    for i, c in enumerate(reversed(s)):
        if i and not i % 3:
            r.insert(0, '#')
        r.insert(0, c)

    return ''.join(r)


def formateafecha(lafecha = None, sepa = _(' of '), corta = False, hora = False):
    try:
        if not lafecha == None:
            t2 = time.localtime(time.mktime(time.strptime(lafecha, '%Y-%m-%d')))
        else:
            return ''
        cdia = str(time.strftime('%d', t2))
        cmes = str(time.strftime('%B', t2))
        cano = str(time.strftime('%Y', t2))
        csemana = str(time.strftime('%A', t2))
        chora = ''
        if hora:
            chora = ' ' + str(time.strftime('%H:%M', t2))
        if corta:
            cmes = _(cmes)
            cmes = cmes[0:3]
            csemana = _(csemana)
            csemana = csemana[0:3]
            return cdia + sepa + cmes + sepa + cano + chora
        return _(csemana) + ', ' + cdia + sepa + _(cmes) + sepa + cano + chora
    except:
        return lafecha


def stripHTMLTags(html):
    """
    Strip HTML tags from any string and transfrom special entities
    """
    text = html
    rules = [{'>\\s+': u'>'},
     {'\\s+': u' '},
     {'\\s*<br\\s*/?>\\s*': u'\n'},
     {'</(div)\\s*>\\s*': u'\n'},
     {'</(p|h\\d)\\s*>\\s*': u'\n\n'},
     {'<head>.*<\\s*(/head|body)[^>]*>': u''},
     {'<a\\s+href="([^"]+)"[^>]*>([^"]+)</a>': '[\\1]\\2<p>'},
     {'[ \\t]*<[^<]*?/?>': u''},
     {'^\\s+': u''}]
    for rule in rules:
        for k, v in rule.items():
            regex = re.compile(k)
            text = regex.sub(v, text)

    special = {'&nbsp;': ' ',
     '&amp;': '&',
     '&quot;': '"',
     '&lt;': '<',
     '&gt;': '>',
     '&#x22;': '-'}
    for k, v in special.items():
        text = text.replace(k, v)

    return text


def remove_refs(data):
    p = re.compile('<a.*?>')
    return p.sub('', data)


def remove_html_tags(data):
    p = re.compile('<.*?>')
    return p.sub('', data)


def borraenlaces(data):
    p = re.compile('\\[.*?\\]')
    return p.sub('', data)


def limpialineas(texto):
    arrtemp = texto.split('\n')
    cret = ''
    for elet in arrtemp:
        if len(elet) > 3:
            cret = cret + elet + '\n'

    return cret


def devStr(cadena, inicio, fin):
    try:
        if inicio not in cadena:
            return ''
        str = cadena.split(inicio)[1]
        if fin in cadena:
            str = str.split(fin)[0]
        return str
    except:
        return ''


class ResultList(MenuList):

    def __init__(self, list, enableWrapAround = False):
        MenuList.__init__(self, list, enableWrapAround, eListboxPythonMultiContent)
        self.l.setItemHeight(fhd(50))
        self.l.setFont(0, gFont('Regular', 20))
        self.l.setFont(1, gFont('Regular', 18))


def ResultListEntry(serviceName, eventName, ervalor, ericono = 'imdbmovie-fs8.png'):
    res = [(serviceName, ervalor)]
    if esHD():
        png = LoadPixmap('/usr/lib/enigma2/python/Plugins/Extensions/spzIMDB/res/hd' + ericono)
    else:
        png = LoadPixmap('/usr/lib/enigma2/python/Plugins/Extensions/spzIMDB/res/' + ericono)
    res.append(MultiContentEntryText(pos=(fhd(60), 0), size=(fhd(800), fhd(22)), font=0, text=serviceName))
    res.append(MultiContentEntryText(pos=(fhd(70), fhd(22)), size=(fhd(800), fhd(18)), font=1, text=eventName, color=8947848))
    res.append(MultiContentEntryPixmapAlphaBlend(pos=(fhd(5), fhd(3)), size=(fhd(49), fhd(32)), png=png, flags=BT_SCALE | BT_KEEP_ASPECT_RATIO))
    return res


from Plugins.Extensions.spazeMenu.sbar import openspaSB

class scr_spzIMDB(Screen):
    if esHD():
        skin = '\n\t\t<screen name="scr_spzIMDB" position="center,center" size="1680,900" title="%s">\n\t\t\t<widget name="poster" position="1,45" size="420,630" alphatest="on" zPosition="1" />\n\t\t\t<widget name="fondoposter" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spzIMDB/res/hdnoposter.png" position="1,45" size="420,630" alphatest="on" />\n\t\t\t<widget name="esperaposter" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spzIMDB/res/hdesperaposter-fs8.png" position="1,45" size="420,630" alphatest="blend" zPosition="10" />\n\t\t\t<widget name="img_tmdb" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spzIMDB/res/hdtmdb_icon-fs8.png" position="1605,18" size="73,49" transparent="1" alphatest="blend" />\n\t\t\t<widget name="img_imdb" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spzIMDB/res/hdimdb_icon-fs8.png" position="1605,18" size="73,49" transparent="1" alphatest="blend" />\n\t\t\t<widget name="serverinfo" position="1285,27" size="315,33" transparent="1" zPosition="10" font="Regular; 16" valign="center" halign="right" />\n\t\t\t\n\t\t\t<widget name="texto" position="0,0" size="1600,40" transparent="0" zPosition="10" font="Regular; 22" valign="top" />\t\t\n\t\t\t\n\t\t\t<widget name="myMenu" position="442,67" size="1236,750" transparent="1" zPosition="11" scrollbarMode="showOnDemand" />\n\t\t\t<widget name="argumento" position="442,67" size="1236,774" transparent="1" zPosition="10" font="Regular; 19" valign="top" itemHeight="40" />\t\t\n\n\t\t\t<widget name="img_red" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spzIMDB/res/redhd.png" position="7,858" size="60,37" transparent="1" alphatest="on" />\n\t\t\t<widget name="key_red" position="67,858" zPosition="1" size="171,37" font="Regular;16" valign="center" halign="left" transparent="1" />\n\n\t\t\t<widget name="img_green" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spzIMDB/res/greenhd.png" position="277,858" size="60,37" transparent="1" alphatest="on" />\n\t\t\t<widget name="key_green" position="337,858" zPosition="1" size="487,37" font="Regular;16" valign="center" halign="left" transparent="1" />\n\t\t\t\n\t\t\t<widget name="img_yellow" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spzIMDB/res/yellowhd.png" position="705,858" size="60,37" transparent="1" alphatest="on" />\n\t\t\t<widget name="key_yellow" position="765,858" zPosition="1" size="487,37" font="Regular;16" valign="center" halign="left" transparent="1" />\n\n\t\t\t<widget name="img_blue" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spzIMDB/res/bluehd.png" position="1215,858" size="60,37" transparent="1" alphatest="on" />\n\t\t\t<widget name="key_blue" position="1275,858" zPosition="1" size="337,37" font="Regular;16" valign="center" halign="left" transparent="1" />\n\n\t\t\t\n\t\t\t<eLabel name="linea" position="0,853" size="1680,1" backgroundColor="#10444444" />\n\t\t\t<eLabel name="lineah" position="430,45" size="1,802" backgroundColor="#10444444" />\n\t\t\t\n\t\t\t<widget name="starsbg" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spzIMDB/res/starsbar_empty.png" position="49,720" zPosition="11" size="315,31" transparent="1" alphatest="on" />\n\t\t\t<widget name="stars" position="49,720" size="315,31" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spzIMDB/res/starsbar_filled.png" zPosition="12" transparent="1" />\n\t\t\t\n\t\t\t<widget name="url" position="1,681" size="420,37" transparent="1" zPosition="10" font="Regular; 16" valign="center" halign="left" />\n\t\t\t<widget name="puntos" position="1,757" size="420,57" transparent="1" zPosition="10" font="Regular; 34" valign="center" halign="center" />\n\t\t\t<widget name="votos" position="1,807" size="420,39" transparent="1" zPosition="10" font="Regular; 18" valign="center" halign="center" />\n\t\t\t<widget name="barrapix_arr" position="0,0" zPosition="19" size="30,30" alphatest="blend" transparent="1" />\n\t\t\t<widget name="barrapix_abj" position="0,0" zPosition="19" size="30,30" alphatest="blend" transparent="1" />\n\t\t\t<widget name="barrapix2_arr" position="442,67" zPosition="19" size="1236,774" alphatest="blend" transparent="1" />\n\t\t\t<widget name="barrapix2_abj" position="0,0" zPosition="19" size="30,30" alphatest="blend" transparent="1" />\t\t\n\t\t</screen>' % _('spzInternet Movie Information').replace('spzInternet', 'openSPA')
    else:
        skin = '\n\t\t<screen name="scr_spzIMDB" position="center,center" size="1120,600" title="%s">\n\t\t\t<widget name="poster" position="1,30" size="280,420" alphatest="on" zPosition="1" />\n\t\t\t<widget name="fondoposter" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spzIMDB/res/noposter.png" position="1,30" size="280,420" alphatest="on" />\n\t\t\t<widget name="esperaposter" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spzIMDB/res/esperaposter-fs8.png" position="1,30" size="280,420" alphatest="blend" zPosition="10" />\n\t\t\t<widget name="img_tmdb" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spzIMDB/res/tmdb_icon-fs8.png" position="1070,12" size="49,33" transparent="1" alphatest="blend" />\n\t\t\t<widget name="img_imdb" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spzIMDB/res/imdb_icon-fs8.png" position="1070,12" size="49,33" transparent="1" alphatest="blend" />\n\t\t\t<widget name="serverinfo" position="857,18" size="210,22" transparent="1" zPosition="10" font="Regular; 16" valign="center" halign="right" />\n\t\t\t\n\t\t\t<widget name="texto" position="0,0" size="1067,27" transparent="0" zPosition="10" font="Regular; 22" valign="top" />\t\t\n\t\t\t\n\t\t\t<widget name="myMenu" position="295,45" size="824,500" transparent="1" zPosition="11" scrollbarMode="showOnDemand" />\n\t\t\t<widget name="argumento" position="295,45" size="824,516" transparent="1" zPosition="10" font="Regular; 19" valign="top" />\t\t\n\n\t\t\t<widget name="img_red" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spzIMDB/res/red.png" position="5,572" size="40,25" transparent="1" alphatest="on" />\n\t\t\t<widget name="key_red" position="45,572" zPosition="1" size="114,25" font="Regular;16" valign="center" halign="left" transparent="1" />\n\n\t\t\t<widget name="img_green" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spzIMDB/res/green.png" position="185,572" size="40,25" transparent="1" alphatest="on" />\n\t\t\t<widget name="key_green" position="225,572" zPosition="1" size="325,25" font="Regular;16" valign="center" halign="left" transparent="1" />\n\t\t\t\n\t\t\t<widget name="img_yellow" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spzIMDB/res/yellow.png" position="470,572" size="40,25" transparent="1" alphatest="on" />\n\t\t\t<widget name="key_yellow" position="510,572" zPosition="1" size="325,25" font="Regular;16" valign="center" halign="left" transparent="1" />\n\n\t\t\t<widget name="img_blue" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spzIMDB/res/blue.png" position="810,572" size="40,25" transparent="1" alphatest="on" />\n\t\t\t<widget name="key_blue" position="850,572" zPosition="1" size="225,25" font="Regular;16" valign="center" halign="left" transparent="1" />\n\n\t\t\t\n\t\t\t<eLabel name="linea" position="0,569" size="1120,1" backgroundColor="#10444444" />\n\t\t\t<eLabel name="lineah" position="287,30" size="1,535" backgroundColor="#10444444" />\n\t\t\t\n\t\t\t<widget name="starsbg" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spzIMDB/res/starsbar_empty.png" position="33,480" zPosition="11" size="210,21" transparent="1" alphatest="on" />\n\t\t\t<widget name="stars" position="33,480" size="210,21" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spzIMDB/res/starsbar_filled.png" zPosition="12" transparent="1" />\n\t\t\t\n\t\t\t<widget name="url" position="1,454" size="280,25" transparent="1" zPosition="10" font="Regular; 16" valign="center" halign="left" />\n\t\t\t<widget name="puntos" position="1,505" size="280,38" transparent="1" zPosition="10" font="Regular; 34" valign="center" halign="center" />\n\t\t\t<widget name="votos" position="1,538" size="280,26" transparent="1" zPosition="10" font="Regular; 18" valign="center" halign="center" />\n\t\t\t<widget name="barrapix_arr" position="0,0" zPosition="19" size="20,20" alphatest="blend" transparent="1" />\n\t\t\t<widget name="barrapix_abj" position="0,0" zPosition="19" size="20,20" alphatest="blend" transparent="1" />\n\t\t\t<widget name="barrapix2_arr" position="295,45" zPosition="19" size="824,516" alphatest="blend" transparent="1" />\n\t\t\t<widget name="barrapix2_abj" position="0,0" zPosition="19" size="20,20" alphatest="blend" transparent="1" />\t\t\n\t\t</screen>' % _('spzInternet Movie Information').replace('spzInternet', 'openSPA')

    def __init__(self, session, busqueda = None, rutaguardar = None):
        global lenguaje
        Screen.__init__(self, session)
        VALIDS_LANGS = 'es pt fr de it'
        if busqueda is None:
            try:
                refcu = session.nav.getCurrentlyPlayingServiceReference()
                serviceHandler = eServiceCenter.getInstance()
                info = serviceHandler.info(refcu)
                if info:
                    event = info.getEvent(refcu)
                    if event is not None:
                        eventName = event.getEventName()
                        if eventName is None:
                            eventName = ''
                    else:
                        eventName = ''
                if eventName == '':
                    s = self.session.nav.getCurrentService()
                    info = s.info()
                    event = info.getEvent(0)
                    if event:
                        self.busqueda = event.getEventName()
                    else:
                        self.busqueda = _('Title')
                else:
                    self.busqueda = eventName
            except:
                self.busqueda = _('Title')

        else:
            self.busqueda = busqueda
        if rutaguardar == '':
            self.rutaguardar = None
        else:
            self.rutaguardar = rutaguardar
        self['argumento'] = ScrollLabel('-----------------------------------------------------------------------------------------\n' + _('spzInternet Search').replace('spzInternet', 'openSPA') + '\n' + _('Movie information from the Internet Movies Databases') + '\n' + 'openSPA, 201' + '\n-----------------------------------------------------------------------------------------\n')
        lista = []
        self.iniciadoS = False
        self['barrapix_arr'] = Pixmap()
        self['barrapix_abj'] = Pixmap()
        self['barrapix2_arr'] = Pixmap()
        self['barrapix2_abj'] = Pixmap()
        self['myMenu'] = ResultList([])
        self['texto'] = Label(' ')
        self['url'] = Label(' ')
        self['votos'] = Label(' ')
        self['puntos'] = Label(' ')
        self['serverinfo'] = Label(' ')
        self['poster'] = Pixmap()
        self['esperaposter'] = Pixmap()
        self['fondoposter'] = Pixmap()
        self['img_green'] = Pixmap()
        self['img_blue'] = Pixmap()
        self['img_imdb'] = Pixmap()
        self['img_tmdb'] = Pixmap()
        self['img_yellow'] = Pixmap()
        if not self.rutaguardar == None:
            self['key_yellow'] = Label(_('Save'))
        else:
            self['key_yellow'] = Label(_('Select channel/event'))
        self['img_red'] = Pixmap()
        self['key_red'] = Label(_('Exit'))
        self['key_green'] = Label(_('New search'))
        self['key_blue'] = Label(_('Back to list'))
        self.picload = ePicLoad()
        self.picload.PictureData.get().append(self.paintPosterPixmapCB)
        self['stars'] = ProgressBar()
        self['starsbg'] = Pixmap()
        if lenguaje in VALIDS_LANGS:
            self.lang = lenguaje
        elif lenguaje == 'ca' or lenguaje == 'eu' or lenguaje == 'ga' or lenguaje == 'va':
            self.lang = 'es'
        else:
            self.lang = 'com'
        self['actions'] = ActionMap(['OkCancelActions',
         'ColorActions',
         'DirectionActions',
         'DirectionActions',
         'ShortcutActions',
         'WizardActions'], {'green': self.nuevaB,
         'red': self.Exit,
         'blue': self.atras,
         'yellow': self.selCanal,
         'cancel': self.atrasexit,
         'down': self.pageDown,
         'up': self.pageUp,
         'ok': self.KeyOk}, -1)
        self.retornar = False
        self.iniciado = False
        self.cancelar = True
        self.listado = True
        self.onShow.append(self.iniciaP)
        self.onLayoutFinish.append(self.inicio)

    def inicio(self):
        self['esperaposter'].hide()
        self['poster'].hide()

    def getEvento(self, ref):
        eventName = ''
        try:
            serviceHandler = eServiceCenter.getInstance()
            info = serviceHandler.info(ref)
            if info:
                event = info.getEvent(ref)
                if event is not None:
                    eventName = event.getEventName()
                    if eventName is None:
                        eventName = ''
                else:
                    eventName = ''
        except:
            pass

        return eventName

    def guardainfo(self, verinfo = True):
        xmlarchivo = self.rutaguardar
        jpgarchivo = self.rutaguardar.replace('.spztxt', '.jpg')
        try:
            booklist = open(xmlarchivo, 'w')
            booklist.write(self['argumento'].getText())
            booklist.close()
            os.system("mv /tmp/cachehttp/poster.jpg '" + jpgarchivo + "'")
            if fileExists(xmlarchivo):
                if verinfo:
                    ctext = _('The movie information and cover have been saved!')
                    dei = self.session.open(MessageBox, ctext, MessageBox.TYPE_INFO)
                    dei.setTitle(_('Save'))
                self.retornar = False
        except:
            pass

    def selCanal(self):
        if not self.rutaguardar == None:
            if not self['argumento'].getText() == _('No matches found for') + ' [' + self.busqueda + ']' and not self.listado:
                self.guardainfo()
        else:
            self.session.openWithCallback(self.finishedServiceSelection2, SimpleChannelSelection, _('Select channel'))

    def finishedServiceSelection2(self, *args):
        if args:
            laref = args[0]
            retbus = self.getEvento(laref)
            if not retbus == '':
                self.busqueda = retbus
                self.nuevaB()

    def atras(self):
        if len(self['myMenu'].list) <= 0:
            return
        if not self.rutaguardar == None:
            self['key_yellow'].hide()
        if self.retornar:
            self.session.openWithCallback(self.cbGuardar, MessageBox, _('Want to save the cover art and movie information?'), MessageBox.TYPE_YESNO)
        try:
            self['texto'].setText(_('Search for') + ': [' + self.busqueda + ']' + ' :: (' + self.lang + ')')
        except:
            pass

        self['myMenu'].show()
        self['argumento'].hide()
        self['stars'].hide()
        self['starsbg'].hide()
        self['key_blue'].hide()
        self['img_blue'].hide()
        self['url'].hide()
        self['votos'].hide()
        self['puntos'].hide()
        self['img_imdb'].hide()
        self['serverinfo'].hide()
        self['img_tmdb'].hide()
        self['poster'].hide()
        self['esperaposter'].hide()
        self['fondoposter'].show()
        self.listado = True
        self.actualizaScrolls()

    def cbGuardar(self, repuesta):
        if repuesta:
            self.retornar = False
            self.guardainfo(True)

    def pageUp(self):
        self['argumento'].pageUp()
        self['myMenu'].up()

    def pageDown(self):
        self['argumento'].pageDown()
        self['myMenu'].down()

    def IMDBPoster(self, string = False):
        if not string:
            filename = '/tmp/cachehttp/poster.jpg'
        else:
            if esHD():
                filename = resolveFilename(SCOPE_PLUGINS, 'Extensions/spzIMDB/res/hdno_poster.jpg')
            else:
                filename = resolveFilename(SCOPE_PLUGINS, 'Extensions/spzIMDB/res/no_poster.jpg')
            os.system('rm /tmp/cachehttp/poster.jpg')
            self['poster'].hide()
            self['esperaposter'].hide()
            self['fondoposter'].show()
            return
        sc = AVSwitch().getFramebufferScale()
        self.picload.setPara((self['poster'].instance.size().width(),
         self['poster'].instance.size().height(),
         sc[0],
         sc[1],
         False,
         1,
         '#00000000'))
        self.picload.startDecode(filename)

    def paintPosterPixmapCB(self, picInfo = None):
        ptr = self.picload.getData()
        if ptr != None:
            self['poster'].instance.setPixmap(ptr.__deref__())
            self['poster'].show()
            self['fondoposter'].hide()
        else:
            self['poster'].hide()
            self['fondoposter'].show()
        self['esperaposter'].hide()

    def KeyOk(self):
        Value = None
        titulo = None
        estmdb = False
        if True:
            lalista = self['myMenu'].list
            length = len(lalista)
            if length > 0:
                idx = self['myMenu'].getSelectionIndex()
                Value = str(lalista[idx][0][1])
                if 'tmdb_' in Value:
                    estmdb = True
                    Value = Value.replace('tmdb_', '')
                titulo = str(lalista[idx][0][0])
                if not estmdb:
                    erano = str(lalista[idx][2][7])
                    if len(erano) > 2:
                        titulo = titulo + ' | ' + erano + ''
                if not estmdb:
                    if len(Value) > 2 and len(titulo) >= 1:
                        self.listado = False
                        self.muestraInfo(titulo, Value)
                        self['key_blue'].show()
                        self['img_blue'].show()
                else:
                    self.listado = False
                    self.muestraInfo2(titulo, Value)
                    self['key_blue'].show()
                    self['img_blue'].show()
        self.actualizaScrolls()

    def muestraInfo2(self, titulo, valor):
        try:
            self.IMDBPoster('Sin Poster')
        except:
            pass

        self['myMenu'].hide()
        self['argumento'].show()
        self['texto'].setText(titulo)
        self['img_tmdb'].show()
        self['img_imdb'].hide()
        self['serverinfo'].show()
        self['serverinfo'].setText('tmdb.org[' + self.lang + ']')
        textoinfo = ''
        calificacion = ''
        laimagen = 'na'
        elimdb = ''
        lainfo = strInfo(getTMDBInfo(valor))
        try:
            textoinfo = lainfo[0][0]
        except:
            self['argumento'].setText(_('No info avaible for this movie'))
            return

        calificacion = lainfo[0][1]
        laimagen = lainfo[0][2]
        laimagen = getTMDBimgage(0, laimagen)
        elimdb = lainfo[0][3]
        if textoinfo == '':
            self['argumento'].setText(_('No info avaible for this movie'))
            return
        self['argumento'].setText(str(textoinfo))
        valora = devStr('xxx' + calificacion, 'xxx', '/')
        if len(valora) > 0:
            clifica = str(calificacion)
            nvo = ' ' + devStr(clifica, '/10', 'xx') + ' ' + _('votes')
            self['url'].setText(_('Ratings') + ': ')
            self['puntos'].setText(' ' + str(valora).replace('.', ',') + ' ')
            self['votos'].setText(nvo)
            self['votos'].show()
            self['puntos'].show()
            self['url'].show()
        else:
            self['url'].hide()
            self['votos'].hide()
            self['puntos'].hide()
        ratingstars = 0
        if len(valora) > 0:
            ratingstars = int(10 * round(float(valora.replace(',', '.')), 1))
        if ratingstars > 0:
            self['starsbg'].show()
            self['stars'].show()
            self['stars'].setValue(ratingstars)
        if not self.rutaguardar == None:
            if not fileExists(self.rutaguardar):
                self.retornar = True
            self['key_yellow'].show()
        localfile = '/tmp/cachehttp/poster.jpg'
        self['esperaposter'].show()
        downloadPage(str(laimagen), localfile).addCallback(self.IMDBPoster).addErrback(self.fetchFailed)
        self.actualizaScrolls()

    def muestraInfo(self, titulo, valor):
        sepa = '-----------------------------------------------------------------------------------------'
        urlbase = 'http://www.imdb.com'
        lang = self.lang
        try:
            self.IMDBPoster('Sin Poster')
        except Exception as e:
            pass

        urlbase = re.sub('<lang>', lang, urlbase)
        iniciotrama = '<div id="swiki.2.1">'
        self['myMenu'].hide()
        self['argumento'].show()
        self['img_imdb'].show()
        self['img_tmdb'].hide()
        self['serverinfo'].show()
        self['serverinfo'].setText('imdb.' + self.lang + '')
        self['texto'].setText(titulo)
        url = urlbase
        url = url + valor
        html = WebGrabber.getHtml(url)
        if html == None:
            self['argumento'].setText(_('No info avaible for this movie'))
            return
        textohtml = _('Title') + '-> ' + titulo + '\n' + sepa + '\n'
        calificacion = devStr(html, 'Ratings:', '</span> users')
        valora = devStr(calificacion, '<span itemprop="ratingValue">', '</span>')
        nvo = devStr(calificacion, '<span itemprop="ratingCount">', '</span>')
        calificacion = stripHTMLTags(calificacion)
        calificacion = borraenlaces(calificacion)
        if len(calificacion) > 3:
            if True:
                self['url'].setText(_('Ratings') + ': ')
                if len(valora) > 5:
                    valora = '--'
                self['puntos'].setText(' ' + str(valora) + ' ')
                self['votos'].setText(str(nvo) + ' ' + _('votes'))
                self['votos'].show()
                self['puntos'].show()
                self['url'].show()
            else:
                textohtml = textohtml + _('Ratings') + ': ' + calificacion + '\n' + sepa + '\n'
        else:
            self['votos'].hide()
            self['puntos'].hide()
            self['url'].hide()
        ratingstars = 0
        try:
            if len(valora) > 0:
                ratingstars = int(10 * round(float(valora.replace(',', '.')), 1))
        except:
            pass

        if ratingstars > 0:
            self['starsbg'].show()
            self['stars'].show()
            self['stars'].setValue(ratingstars)
        ficha = devStr(html, '<div class="txt-block" itemprop="director" itemscope itemtype="http://schema.org/Person">', '<div class="txt-block" itemprop="actors"')
        arrficha = ficha.split('<h4 class="inline">')
        laurl = ''
        textotemp = ''
        carsep = ''
        for elemento in arrficha:
            elemento = stripHTMLTags(elemento)
            elemento = borraenlaces(elemento)
            elemento = limpialineas(elemento)
            if len(elemento) > 2:
                elemento = elemento.replace('\n', '')
                textotemp = textotemp + carsep + elemento
                carsep = ', '

        if len(textotemp) > 4:
            textohtml = textohtml + textotemp + '\n' + sepa + '\n'
        ficha = devStr(html, '<div class="infobar">', '</div>')
        ficha = stripHTMLTags(ficha)
        ficha = limpialineas(ficha)
        ficha = borraenlaces(ficha)
        ficha = ficha.replace('\n', '')
        if ficha[0] == 'T':
            ficha = ficha[1:]
        textohtml = textohtml + ficha + '\n' + sepa + '\n'
        laurl = ''
        try:
            laurl = url.split('?')[0]
            laurl = laurl + 'plotsummary'
        except:
            pass

        argu = _('Synopsis') + '-> '
        textoargu = ''
        ahtml = None
        if not laurl == '':
            ahtml = WebGrabber.getHtml(laurl)
            if not ahtml == None:
                textoargu = devStr(ahtml, '<p class="plotpar">', '<div class="info">').replace('</p>', '_xxYxx_</p>')
                textoargu = '' + stripHTMLTags(textoargu)
                textoargu = borraenlaces(textoargu)
                textoargu = limpialineas(textoargu).replace('_xxYxx_', '\n')
            if len(textoargu) < 15:
                argu = argu + _('There is no argument to show') + '\n'
            else:
                argu = argu + '(' + _('in') + ' ' + _('English') + ') ' + textoargu + ''
        else:
            argu = argu + _('There is no argument to show') + '\n'
        argu = argu + sepa
        textohtml = textohtml + argu
        reparto = ''
        creparto = '' + devStr(html, 'class="castlist_label">', '</table>')
        arrreparto = creparto.split('</tr>')
        carsep = _('Cast') + ': '
        for actor in arrreparto:
            if '<tr ' in actor:
                actor = stripHTMLTags(actor)
                actor = borraenlaces(actor)
                actor = limpialineas(actor)
                actor = actor.replace('(', '-').replace(')', '-')
                actor = actor.replace('\n', '').replace('...', ' (') + ')'
                if len(actor) > 3:
                    reparto = reparto + carsep + actor
                    carsep = ', '

        reparto = limpialineas(reparto)
        if len(reparto) > 3:
            textohtml = textohtml + '\n' + reparto + sepa + '\n'
        masdetal = ''
        cdetal = devStr(html, '</h3><div class="info">', '<hr/>')
        arrdetal = cdetal.split('<div class="info">')
        conta = 0
        for elemento in arrdetal:
            if '<h5>' in elemento:
                if conta > 0:
                    encabezado = devStr(elemento, '<h5>', '</h5>')
                    lainfo = devStr(elemento, '<div class="info-content">', '</div>')
                    lainfo = devStr('***x***' + lainfo, '***x***', '<a class="tn15more')
                    encabezado = stripHTMLTags(encabezado)
                    encabezado = borraenlaces(encabezado)
                    encabezado = limpialineas2(encabezado)
                    lainfo = stripHTMLTags(lainfo)
                    lainfo = borraenlaces(lainfo)
                    lainfo = limpialineas2(lainfo)
                    if len(lainfo) > 0 and len(encabezado) > 0:
                        masdetal = masdetal + encabezado + ' ' + lainfo + '\n' + sepa + '\n'
                conta = conta + 1

        if len(masdetal) > 3:
            textohtml = textohtml + masdetal
        lafoto = devStr(html, '<div class="image">', '</div>')
        lafoto = devStr(lafoto, 'src="', '"')
        textolatin = Utf8.utf8ToLatin(textohtml)
        sourceEncoding = 'iso-8859-1'
        targetEncoding = 'utf-8'
        textoutf = unicode(textolatin, sourceEncoding).encode(targetEncoding)
        self['argumento'].setText(textoutf)
        if not self.rutaguardar == None:
            self['key_yellow'].show()
            if not fileExists(self.rutaguardar):
                self.retornar = True
        localfile = '/tmp/cachehttp/poster.jpg'
        self['esperaposter'].show()
        downloadPage(str(lafoto), localfile).addCallback(self.IMDBPoster).addErrback(self.fetchFailed)
        self.actualizaScrolls()

    def fetchFailed(self, string):
        self['poster'].hide()
        self['esperaposter'].hide()
        self['fondoposter'].show()

    def atrasexit(self):
        if self.listado or len(self['myMenu'].list) <= 0:
            self.Exit()
        else:
            self.atras()

    def iniciaP(self):
        if not self.iniciado:
            try:
                if not self.rutaguardar == None:
                    self['key_yellow'].hide()
                self.IMDBPoster('Sin Poster')
                self['key_blue'].hide()
                self['img_blue'].hide()
                self['stars'].hide()
                self['starsbg'].hide()
                self['votos'].hide()
                self['puntos'].hide()
                self['url'].hide()
            except Exception as e:
                pass

            self.nuevaB()
        self.iniciado = True
        if not self.iniciadoS:
            self.actualizaScrolls()
            self.iniciadoS = True

    def actualizaScrolls(self):
        if self.listado:
            self['barrapix2_arr'].hide()
            self['barrapix2_abj'].hide()
            openspaSB(objectoself=self, nombrelista='myMenu', barra='barrapix', altoitem=50, imagen=True)
        else:
            self['barrapix_arr'].hide()
            self['barrapix_abj'].hide()
            self['barrapix2_arr'].show()
            self['barrapix2_abj'].show()
            openspaSB(objectoself=self, nombrelista='barrapix2', barra='barrapix2', altoitem=20, imagen=True)

    def nuevaB(self):
        self.busqueda = self.busqueda.replace('(HD)', '')
        self.busqueda = self.busqueda.replace('Cine:', '')
        if '(' in self.busqueda:
            sipar = devStr(self.busqueda, '(', ')')
            if len(sipar) > 1:
                self.busqueda = self.busqueda.replace(sipar, '')
                sipar = devStr(self.busqueda, '(', ')')
                if len(sipar) > 1:
                    self.busqueda = self.busqueda.replace(sipar, '')
        self.busqueda = self.busqueda.replace('()', '').replace('(', '').replace('...', ' ').strip()
        from Plugins.Extensions.spazeMenu.spzVirtualKeyboard import spzVirtualKeyboard
        self.session.openWithCallback(self.nuevaBcb, spzVirtualKeyboard, titulo=_('Search Movie') + '. ' + _('Title for Internet search') + ':', texto=self.busqueda, ok=True)

    def nuevaBcb(self, ernombre):
        if ernombre == '' or ernombre == None:
            return
        self.cancelar = False
        self.busqueda = ernombre
        self['texto'].setText(_('Search for') + ': [' + self.busqueda + ']' + ' :: (' + self.lang + ')')
        limdb = clase_imdb()
        ret1 = limdb.buscarImdb(texto=self.busqueda, lang=self.lang)
        ret2 = buscarTmdb(self.busqueda)
        self.listado = True
        lista = []
        self['myMenu'].setList(lista)
        self['myMenu'].hide()
        self['argumento'].hide()
        self['stars'].hide()
        self['starsbg'].hide()
        self['key_blue'].hide()
        self['img_blue'].hide()
        self['votos'].hide()
        self['puntos'].hide()
        if not self.rutaguardar == None:
            self['key_yellow'].hide()
        self['url'].hide()
        self['img_imdb'].hide()
        self['img_tmdb'].hide()
        self['serverinfo'].hide()
        self['url'].setText(' ')
        try:
            self.IMDBPoster('Sin Poster')
        except:
            pass

        if len(ret1) == 0 and len(ret2) == 0:
            self['argumento'].show()
            self['argumento'].setText(_('No matches found for') + ' [' + self.busqueda + ']')
        elif len(ret1) + len(ret2) == 1:
            self['argumento'].show()
            if len(ret2) == 1:
                try:
                    self.listado = False
                    self.muestraInfo2(str(ret2[0].name), str(ret2[0].id).replace('tmdb_', ''))
                except:
                    self['argumento'].show()
                    self['argumento'].setText(_('No matches found for') + ' [' + self.busqueda + '] tmdb.org')

            else:
                try:
                    self.listado = False
                    self.muestraInfo(str(ret1[0].Title), str(ret1[0].ImdbId))
                except:
                    self['argumento'].show()
                    self['argumento'].setText(_('No matches found for') + ' [' + self.busqueda + '] imdb.es')

        else:
            try:
                self.IMDBPoster('Sin Poster')
            except:
                pass

            try:
                for iji in ret2:
                    ertitulo = str(iji.name)
                    erano = iji.released[0:4]
                    cover = ''
                    if '-' in erano or len(erano) < 4:
                        pass
                    else:
                        cover = _('Year ') + erano
                    if not iji.overview == '':
                        cover = cover + ' - ' + iji.overview
                    valor = str(iji.id)
                    if esHD():
                        ericono = 'hdtmdb_icon-fs8.png'
                    else:
                        ericono = 'tmdb_icon-fs8.png'
                    lista.append(ResultListEntry(ertitulo, cover, valor, ericono))

            except:
                pass

            try:
                for iji in ret1:
                    ertitulo = str(iji.Title)
                    erano = devStr(ertitulo, '(', ')')
                    if len(erano) == 4:
                        ertitulo = ertitulo.replace('(' + erano + ')', '')
                        erano = _('Year ') + erano
                    else:
                        erano = ''
                    erano = erano + ' (' + _('in') + ' ' + _('English') + ') '
                    for ii in range(1, 30):
                        cad = str(ii) + '.'
                        lon = len(cad)
                        if cad in ertitulo:
                            if ertitulo[0:lon] == cad:
                                ertitulo = ertitulo.replace(cad, '')
                                break

                    valor = str(iji.ImdbId)
                    if esHD():
                        ericono = 'hdimdb_icon-fs8.png'
                    else:
                        ericono = 'imdb_icon-fs8.png'
                    lista.append(ResultListEntry(ertitulo, erano, valor, ericono))

            except:
                pass

            if len(lista) > 0:
                self['myMenu'].setList(lista)
                self['myMenu'].show()
                self.listado = True
            else:
                self['argumento'].show()
                self['argumento'].setText(_('No matches found for') + ' [' + self.busqueda + '] imdb.com/tmdb.org')
        self.actualizaScrolls()

    def Exit(self):
        if self.retornar and not self.listado:
            self.session.openWithCallback(self.cbGuardarExit, MessageBox, _('Want to save the cover art and movie information?'), MessageBox.TYPE_YESNO)
        else:
            self.close(None)

    def cbGuardarExit(self, repuesta):
        if repuesta:
            self.retornar = False
            self.guardainfo(False)
        self.close()


from Screens.InputBox import InputBox
from Screens.VirtualKeyBoard import VirtualKeyBoard

class vInputBox(InputBox):
    vibnewx = '600'
    sknew = '<screen name="vInputBox" position="center,center" size="' + vibnewx + ',85" title="' + _('Title input') + '...">\n'
    sknew = sknew + '<widget name="text" position="5,0" size="590,50" font="Regular;18"/>\n<widget name="input" position="0,40" size="'
    sknew = sknew + vibnewx + ',30" font="Regular;18"/>\n</screen>'
    skin = sknew

    def __init__(self, session, title = '', windowTitle = _('Title input'), useableChars = None, **kwargs):
        InputBox.__init__(self, session, title, windowTitle, useableChars, **kwargs)
        self.texto = _('Title')
        try:
            self.texto = text
        except:
            pass

        self['actions'] = ActionMap(['ColorActions'], {'blue': self.openKeyboard}, -1)

    def openKeyboard(self):
        self.session.openWithCallback(self.SearchEntryCallback, VirtualKeyBoard, title=_('Title input'), text=self.texto)

    def SearchEntryCallback(self, callback = None):
        if callback is not None and len(callback):
            self.close(callback)


def spzIMDB(session, tbusqueda = None, truta = None, **kwargs):
    from Tools.Directories import fileExists
    if not fileExists('/usr/bin/chkvs'):
        from Tools import Notifications
        Notifications.AddPopup(text=_('Not spazeTeam image found!\nMore info in www.azboxhd.es'), type=MessageBox.TYPE_ERROR, timeout=10, id='spzIMDB')
    else:
        session.open(scr_spzIMDB, busqueda=tbusqueda, rutaguardar=truta)


def Plugins(**kwargs):
    os.system('rm ' + WebGrabber.cacheDir + '/*')
    os.system('rm ' + WebGrabber.downloadDir + '/*')
    return [PluginDescriptor(name=_('spzInternet Search').replace('spzInternet', 'openSPA Internet'), description=_('Movie information from the Internet Movies Databases'), icon='imdb.png', where=PluginDescriptor.WHERE_PLUGINMENU, fnc=spzIMDB)]


class clase_imdb():
    URL = 'http://www.imdb.com/'
    apiSearch = URL + 'find?s=tt&ttype=ft&exact=true&q=<search>'
    DIV_LIST_START = '<table class="findList">'
    DIV_LIST_END = '</table>'

    class ResultEntry:
        ImdbId = ''
        Title = ''

        def __init__(self):
            ImdbId = ''
            Title = ''

        def __str__(self):
            return Utf8.utf8ToLatin(self.Title + ':' + self.ImdbId)

    def getResults(self, html):
        temphtml = devStr(html, self.DIV_LIST_START, self.DIV_LIST_END)
        arrhtml = temphtml.split('</tr>')
        resultstmp = []
        n = 0
        for linea in arrhtml:
            n = n + 1
            if len(linea) > 1:
                try:
                    templinea = stripHTMLTags(linea)
                    url = devStr(templinea, '[', ']')
                    titulo = templinea.replace('[' + url + ']', '')
                    entry = self.ResultEntry()
                    if len(url) > 3 and '[' not in str(titulo):
                        entry.Title = titulo
                        entry.ImdbId = url
                        resultstmp.append(entry)
                except:
                    pass

        return resultstmp

    def buscarImdb(self, texto, lang):
        results = []
        texto = texto + ''
        url = self.apiSearch
        url = re.sub('<search>', texto, url)
        url = re.sub('<lang>', lang, url)
        html = WebGrabber.getHtml(url)
        if html is None:
            return []
        results = self.getResults(html)
        return results


def devJson(cadena, tag):
    cret = ''
    if cadena and tag in cadena:
        try:
            cret = str(cadena[tag])
        except:
            pass

    return cret


def devXml(cadena, tag):
    return devStrTm(cadena, '<' + tag + '>', '</' + tag + '>')


def devNames(cadena, tag, sep = ', '):
    tempxml = devXml(cadena, tag)
    arrtemp = []
    arrtemp = tempxml.split('<')
    ret = ''
    csepa = ''
    for ele in arrtemp:
        if 'name' in ele:
            temp = devStrTm(ele, 'name="', '"')
            ret = ret + csepa + temp
            csepa = sep

    return ret


def devNamesj(cadena, tag, sep = ', '):
    ret = ''
    if not cadena or str(cadena) == '':
        return ''
    try:
        tempxml = eval(devJson(cadena, tag))
        csepa = ''
        if not tempxml:
            return ''
        for ele in tempxml:
            if 'name' in ele:
                temp = ele['name']
                ret = ret + csepa + temp
                csepa = sep

    except:
        pass

    return ret


def devCast(cadena, tag, sepcat = '\n', sep = ', '):
    tempxml = devXml(cadena, tag)
    arrtemp = []
    arrtemp = tempxml.split('<person')
    ret = ''
    csepa = ''
    csepa1 = ''
    categoria = ''
    job = ''
    csepa0 = ''
    for ele in arrtemp:
        if 'department' in ele:
            departamento = devStrTm(ele, 'department="', '"')
            if not departamento == categoria:
                categoria = departamento
                ret = ret + csepa1 + _(categoria) + ': '
                csepa1 = sepcat
                csepa = ''
            trabajo = devStrTm(ele, 'job="', '"')
            nombre = devStrTm(ele, 'name="', '"')
            caracter = devStrTm(ele, 'character="', '"')
            temp = nombre
            if not trabajo == 'Actor':
                temp = temp + ' (' + _(trabajo) + ')'
            if not caracter == '':
                temp = temp + ' (' + _(caracter) + ')'
            ret = ret + csepa + temp
            csepa = sep

    return ret


def devStrTm(cadena, inicio, fin):
    try:
        if inicio not in cadena:
            return ''
        str = cadena.split(inicio)[1]
        if not fin == '':
            str = str.split(fin)[0]
        return str
    except:
        return ''


languagetm = 'es'
languages = {'en': 'en',
 'es': 'es',
 'fr': 'fr'}

def getTMDB(comando, valor):
    global languages
    try:
        l = languages[lenguaje]
    except:
        if lenguaje == 'ca' or lenguaje == 'eu' or lenguaje == 'ga' or lenguaje == 'va':
            l = 'es'
        else:
            l = 'en'

    APIKEY = u'558f65e7d735d0af64f0bd49c5ee7b96'
    laurl = u'http://api.themoviedb.org/3/<command>?language=<lang>&api_key=' + APIKEY + u'&<imdbid>'
    laurl = re.sub('<lang>', l, laurl)
    laurl = re.sub('<command>', comando, laurl)
    if valor == 'image':
        laurl = u'http://api.themoviedb.org/3/configuration?api_key=' + APIKEY
    else:
        data = {}
        data['query'] = valor
        url_values = urllib.urlencode(data)
        laurl = re.sub('<imdbid>', url_values, laurl)
    html = WebGrabber.getJson(laurl.replace(' ', ''))
    if html == None:
        return ''
    else:
        return html


import WebGrabber
import Utf8
import urllib
import re

def limpialineas2(texto):
    return str(texto).replace('\n', '')


class ResultEntrytmdb():
    id = ''
    name = ''
    popularity = ''
    adult = ''
    translated = ''
    votes = ''
    rating = ''
    original_name = ''
    alternative_name = ''
    imdb = ''
    overview = ''
    released = ''
    image = ''

    def __init__(self):
        id = ''
        name = ''


class MovieEntry():
    id = ''
    name = ''
    popularity = ''
    adult = ''
    translated = ''
    votes = ''
    rating = ''
    original_name = ''
    alternative_name = ''
    imdb = ''
    overview = ''
    released = ''
    image = ''
    budget = ''
    revenue = ''
    categories = ''
    studios = ''
    countries = ''
    cast = ''

    def __init__(self):
        id = ''
        name = ''


def convierteJson(htmj, clave = None):
    if not htmj:
        return
    try:
        htmj = htmj.encode('UTF-8').decode('UTF-8')
    except:
        try:
            htmj = htmj.decode('windows-1252').encode('utf-8').decode('UTF-8')
        except:
            pass

    htmj = htmj.replace(':false', ':False')
    htmj = htmj.replace(':null', ':None')
    resultados = None
    try:
        resultados = eval(htmj)
    except:
        return

    if resultados and clave and clave in resultados:
        resultados = resultados[clave]
    return resultados


def getTMDBInfo(id):
    elhtml = getTMDB('movie/' + str(id), id)
    linea = convierteJson(elhtml)
    os.system("echo '" + str(linea) + "'>>/tmp/tmdbinfo_result.txt")
    if not linea:
        return None
    entry = MovieEntry()
    entry.id = devJson(linea, 'id')
    entry.name = devJson(linea, 'title')
    entry.popularity = devJson(linea, 'popularity')
    entry.adult = devJson(linea, 'adult')
    entry.translated = devJson(linea, 'translated')
    entry.votes = devJson(linea, 'vote_count')
    entry.rating = devJson(linea, 'vote_average')
    entry.original_name = devJson(linea, 'original_title')
    entry.alternative_name = devJson(linea, 'alternative_name')
    entry.imdb = devJson(linea, 'imdb_id')
    entry.overview = devJson(linea, 'overview')
    entry.released = devJson(linea, 'release_date')
    entry.budget = devJson(linea, 'budget')
    entry.revenue = devJson(linea, 'revenue')
    if entry.revenue == '0':
        entry.revenue = ''
    entry.studios = devNamesj(linea, 'production_companies', ' | ')
    entry.countries = devNamesj(linea, 'production_countries', ' | ')
    entry.categories = devNamesj(linea, 'genres', ' | ')
    imagenes = devJson(linea, 'poster_path')
    elhtml = getTMDB('movie/' + str(id) + '/casts', id)
    linea = convierteJson(elhtml, 'cast')
    csepa = ''
    ercast = ''
    if linea:
        for ele in linea:
            try:
                ercast = ercast + csepa + ele['name'] + ' (' + ele['character'] + ')'
                csepa = ', '
            except:
                pass

    linea = convierteJson(elhtml, 'crew')
    csepa = '\n-----------------------\n'
    if linea:
        for ele in linea:
            ercast = ercast + csepa + ele['name'] + ' (' + _(ele['job']) + ')'
            csepa = ', '

    entry.cast = ercast
    entry.image = imagenes
    return entry


def devEle(sepa, nombre, elele):
    if not elele == '' and not elele == '0':
        if not nombre == '':
            if nombre == 'Title' or nombre == 'Synopsis':
                xnombre = _(nombre) + '-> '
            else:
                xnombre = _(nombre) + ': '
        else:
            xnombre = ''
        return sepa + xnombre + elele
    else:
        return ''


def strInfo(lainfo, infosepa = '\n-------------------------------------------------\n'):
    arr = []
    ret = ''
    if not lainfo:
        return []
    sepa = ''
    ret = devEle(sepa, 'Title', lainfo.name)
    sepa = '\n'
    ret = ret + devEle(sepa, 'Original Title', lainfo.original_name)
    sepa = '\n'
    ret = ret + devEle(sepa, 'Alternative Title', lainfo.alternative_name)
    sepa = infosepa
    fecha = formateafecha(lainfo.released)
    ret = ret + devEle(sepa, 'Date', fecha)
    ret = ret + devEle(sepa, 'Categories', lainfo.categories)
    ret = ret + devEle(sepa, 'Countries', lainfo.countries)
    laover = lainfo.overview
    if laover == None or str(laover) == 'None' or str(laover) == '':
        laover = _('There is no argument to show') + '\n'
    ret = ret + devEle(sepa, 'Synopsis', laover)
    ret = ret + devEle(sepa, 'Cast', str(lainfo.cast))
    ret = ret + devEle(sepa, 'Budget', FormatWithCommas(lainfo.budget, cmoneda='$'))
    sepa = ' , '
    elmoney = FormatWithCommas(lainfo.revenue, cmoneda='$')
    if not str(elmoney) == '0,00$':
        ret = ret + devEle(sepa, 'Revenue', elmoney)
    sepa = infosepa
    ret = ret + devEle(sepa, 'Studios', lainfo.studios)
    arr.append((ret,
     lainfo.rating + '/10 ' + lainfo.votes,
     lainfo.image,
     lainfo.imdb))
    return arr


def getTMDBList(busqueda, notranslated = False):
    elhtml = getTMDB('search/movie', busqueda)
    resultstmp = []
    n = 0
    resultstr = convierteJson(elhtml, 'results')
    if resultstr:
        for linea in resultstr:
            n = n + 1
            entry = ResultEntrytmdb()
            entry.id = 'tmdb_' + str(devJson(linea, 'id'))
            entry.name = devJson(linea, 'title')
            entry.popularity = devJson(linea, 'popularity')
            entry.adult = devJson(linea, 'adult')
            entry.translated = devJson(linea, 'translated')
            entry.votes = devJson(linea, 'vote_count')
            entry.rating = devJson(linea, 'vote_average')
            entry.original_name = devJson(linea, 'original_title')
            entry.alternative_name = devJson(linea, 'alternative_name')
            entry.imdb = devJson(linea, 'imdb_id')
            overv = ''
            if entry.original_name == entry.name:
                overv = ''
            else:
                overv = '(' + entry.original_name + ') '
            if not entry.rating == '' and not entry.rating == '0.0':
                overv = overv + ' ' + _('Ratings') + ': ' + entry.rating
            if not entry.votes == '' and not entry.votes == '0':
                overv = overv + ' / ' + entry.votes + ' ' + _('votes')
            entry.overview = overv
            entry.released = devJson(linea, 'release_date')
            imagenes = devJson(linea, 'poster_path')
            entry.image = imagenes
            if not entry.id == '':
                resultstmp.append(entry)

    return resultstmp


def getTMDBimgage(id, ruta):
    elhtml = getTMDB('configuration', 'image')
    try:
        temp = eval(elhtml)
        temp1 = temp['images']['base_url']
    except:
        return ''

    return str(temp1) + 'w342' + ruta


def buscarTmdb(texto):
    listanueva = getTMDBList(texto)
    return listanueva
