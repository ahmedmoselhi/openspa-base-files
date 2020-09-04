from Components.ActionMap import ActionMap
from Components.Pixmap import Pixmap
from Components.Label import Label
from Tools.Directories import resolveFilename, fileExists, pathExists
from Components.ScrollLabel import ScrollLabel
from ServiceReference import ServiceReference
from enigma import eServiceReference, eServiceCenter, eSize, ePoint
from Screens.EventView import EventViewSimple
from enigma import ePicLoad
from Components.AVSwitch import AVSwitch
import os
from os import environ
import gettext
from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE
lang = language.getLanguage()
environ['LANGUAGE'] = lang[:2]
gettext.bindtextdomain('enigma2', resolveFilename(SCOPE_LANGUAGE))
gettext.textdomain('enigma2')
gettext.bindtextdomain('AZ_MRUAvideoinfo', '%s%s' % (resolveFilename(SCOPE_PLUGINS), 'Extensions/MediaCenter/locale/'))

def _(txt):
    t = gettext.dgettext('AZ_MRUAvideoinfo', txt)
    if t == txt:
        t = gettext.gettext(txt)
    return t


from time import localtime, strftime

def Humanizer(size, mostrarbytes = False):
    if size < 1024:
        humansize = str(size) + ' bytes'
    elif size < 1048576:
        humansize = '%.2f Kb' % (float(size) / 1024)
        if mostrarbytes:
            humansize = humansize + ' (' + str(size) + ' bytes)'
    elif size < 1073741824:
        humansize = '%.2f Mb' % (float(size) / 1048576)
        if mostrarbytes:
            humansize = humansize + ' (' + str(size) + ' bytes)'
    else:
        humansize = '%.2f Gb' % (float(size) / 1073741824)
        if mostrarbytes:
            humansize = humansize + ' (' + str(size) + ' bytes)'
    return humansize


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


def limpianombre(quenombre):
    tmpnombre = quenombre.lower()
    if '.' in tmpnombre:
        tmpnombre = '.'.join(tmpnombre.split('.')[:-1]) + '.'
    siwww = devStr(tmpnombre, 'www', 'xxx')
    if len(siwww) > 1:
        tmpnombre = tmpnombre.replace(siwww, '').replace('www', '')
    tmpnombre = tmpnombre.replace('.', ' ').replace('ts-screener', '').replace('480p', '').replace('xvid', '').replace(' hq ', '').replace('hdtvscreener', '').replace('screener', '').replace('hdtv', '').replace('dvdrip', '').replace('x264', '').replace('divx', '').replace('720p', '').replace('1080p', '').replace('hd', '').replace('ac3', '').replace('dts', '').replace('dual', '').replace('bluray', '').replace('bdrip', '').replace('  ', ' ').replace('()', '').replace('[]', '').replace('  ', ' ').replace('  ', ' ').replace('_', ' ')
    return tmpnombre.strip()


def formatDate(lafecha = None, sepa = '-'):
    if not lafecha == None:
        t2 = lafecha
    else:
        t2 = localtime()
    cdia = str(strftime('%d', t2))
    cmes = str(strftime('%B', t2))
    cano = str(strftime('%Y', t2))
    csemana = str(strftime('%A', t2))
    return _(csemana) + ', ' + cdia + sepa + _(cmes) + sepa + cano


class MC_VideoInfo(Screen):
    skin = '\n\t\t<screen name="MRUPlayerInfo" position="center,center" size="845,500" title="%s" backgroundColor="#00000000" >\n\t\t<widget name="nombre" position="220,5" size="618,48" font="Regular; 20" transparent="1" />\n\t\t<widget name="carpeta" position="220,59" size="618,25" font="Regular; 20" transparent="1" />\n\t\t<widget name="fecha" position="220,88" size="618,25" font="Regular; 20" transparent="1" />\n\t\t<widget name="tamano" position="220,117" size="618,25" font="Regular; 20" transparent="1" />\n\t\t<eLabel name="linea2" position="4,153" zPosition="5" size="835,1" transparent="0" foregroundColor="#10555555" backgroundColor="#10555555" />\t\n\t\t<widget name="t1" position="10,6" size="199,25" transparent="1" font="Regular; 20" halign="right" />\n\t\t<widget name="t2" position="10,59" size="199,25" transparent="1" font="Regular; 20" halign="right" />\n\t\t<widget name="t3" position="10,88" size="199,25" transparent="1" font="Regular; 20" halign="right" />\n\t\t<widget name="t4" position="10,117" size="199,25" transparent="1" font="Regular; 20" halign="right" />\n\t\t\n\t\t<widget name="caratula" position="10,164" size="215,282" alphatest="on" />\n\t\t<widget name="argumento" position="235,163" size="605,281" transparent="1" zPosition="10" font="Regular; 20" valign="top" />\n\t\t\n\t\t<eLabel name="linea" position="4,452" zPosition="5" size="835,1" transparent="0" foregroundColor="#10555555" backgroundColor="#10555555" />\n\t\t<widget name="pred" position="4,460" zPosition="4" size="35,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/images/red.png" transparent="1" alphatest="blend" />\n\t\t<widget name="buttonreed" position="42,460" zPosition="5" size="210,25" valign="center" halign="left" font="Regular; 16" transparent="1" />\n\t\t<widget name="pgreen" position="150,460" zPosition="4" size="35,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/images/green.png" transparent="1" alphatest="blend" />\n\t\t<widget name="buttongreen" position="188,460" zPosition="5" size="329,25" valign="center" halign="left" font="Regular; 16" transparent="1" />\n\t\t<widget name="pinfo" position="510,460" zPosition="4" size="35,25" transparent="1" alphatest="blend" />\n\t\t<widget name="buttoninfo" position="548,460" zPosition="5" size="310,25" valign="center" halign="left" font="Regular; 16" transparent="1" />\n\t\t<!--<widget name="imagen_fondo" position="0,0" zPosition="1" size="1280,720" alphatest="on" />-->\n\t\t</screen>' % _('Movie Information')

    def __init__(self, session, mreference = None, mfolder = None, mfile = None):
        Screen.__init__(self, session)
        self.pluginimdb = 'spzIMDB'
        archivo = 'NA'
        ruta = 'NA'
        if mfolder == None:
            try:
                foldername = mreference.rpartition('/')
                archivo = foldername[2]
                ruta = foldername[0]
            except:
                pass

        else:
            archivo = mfile
            ruta = mfolder
        self.archivo = archivo
        self.ruta = ruta
        mfilePath = self.ruta + '/' + self.archivo
        self.fileinfo = self.ruta + '/' + self.archivo + '.spztxt'
        self.ref = mreference
        self.titulo = self.archivo
        self['caratula'] = Pixmap()
        self['buttonreed'] = Label(_('Back'))
        self['buttongreen'] = Label(_('Internet info'))
        self['pgreen'] = Pixmap()
        self['pred'] = Pixmap()
        self['pinfo'] = Pixmap()
        self['buttoninfo'] = Label(' ')
        self['argumento'] = ScrollLabel(_('There is no argument available for this film'))
        self['t1'] = Label(_('File') + ':')
        self['t2'] = Label(_('Folder') + ':')
        self['t3'] = Label(_('File date') + ':')
        self['t4'] = Label(_('Size') + ':')
        self['nombre'] = Label(' ')
        self['carpeta'] = Label(' ')
        self['fecha'] = Label(' ')
        self['tamano'] = Label(' ')
        self.picload = ePicLoad()
        self.picload.PictureData.get().append(self.paintPosterPixmapCB)
        self['actions'] = ActionMap(['OkCancelActions',
         'ColorActions',
         'DirectionActions',
         'WizardActions',
         'EPGSelectActions',
         'InfobarActions'], {'red': self.Exit,
         'green': self.getInetInfo,
         'cancel': self.Exit,
         'ok': self.Exit,
         'cancel': self.Exit,
         'info': self.Exit,
         'up': self.kup,
         'down': self.kdown}, -1)
        self.onShow.append(self.getInfoFile)

    def kup(self):
        self['argumento'].pageUp()

    def kdown(self):
        self['argumento'].pageDown()

    def IMDBPoster(self, string = ''):
        filename = ''
        if not string == '':
            filename = string
        if filename == '' or not fileExists(filename):
            filename = '/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/images/no_poster.jpg'
        sc = AVSwitch().getFramebufferScale()
        self.picload.setPara((self['caratula'].instance.size().width(),
         self['caratula'].instance.size().height(),
         sc[0],
         sc[1],
         False,
         1,
         '#00000000'))
        self.picload.startDecode(filename)

    def paintPosterPixmapCB(self, picInfo = None):
        ptr = self.picload.getData()
        if ptr != None:
            self['caratula'].instance.setPixmap(ptr.__deref__())

    def ocultacaratula(self):
        pass

    def muestracaratula(self):
        pass

    def infoview(self):
        rutacompleta = self.ruta + '/' + self.archivo
        if self.archivo.endswith('.ts'):
            serviceref = eServiceReference('1:0:0:0:0:0:0:0:0:0:' + rutacompleta)
            serviceHandler = eServiceCenter.getInstance()
            info = serviceHandler.info(serviceref)
            evt = info.getEvent(serviceref)
            if evt:
                self.session.open(EventViewSimple, evt, ServiceReference(serviceref))

    def getInfoFile(self):
        self['nombre'].setText(self.archivo)
        self['carpeta'].setText(self.ruta)
        rutacompleta = self.ruta + '/' + self.archivo
        try:
            dir_stats = os.stat(rutacompleta)
        except:
            pass

        try:
            self['fecha'].setText(formatDate(localtime(dir_stats.st_mtime)))
        except:
            self['fecha'].setText('---')

        try:
            self['tamano'].setText(Humanizer(dir_stats.st_size, mostrarbytes=True))
        except:
            self['tamano'].setText('---')

        if not fileExists('/usr/lib/enigma2/python/Plugins/Extensions/' + self.pluginimdb + '/plugin.pyo'):
            self['buttongreen'].hide()
            self['pgreen'].hide()
        self['buttoninfo'].hide()
        self['pinfo'].hide()
        infots = True
        textadd = ''
        if not self.fileinfo == '' and fileExists(self.fileinfo):
            jpg = self.fileinfo.replace('.spztxt', '.jpg')
            if fileExists(jpg):
                self.IMDBPoster(jpg)
            else:
                self.IMDBPoster('')
            try:
                booklist = open(self.fileinfo, 'r')
            except:
                pass

            ret = ''
            if booklist is not None:
                for oneline in booklist:
                    ret = ret + oneline

                booklist.close()
            if len(ret.replace('\n', '')) > 5:
                self['argumento'].setText(ret)
                textadd = '\n' + ret
        else:
            self.IMDBPoster('')
        text = ''
        if infots:
            try:
                if rutacompleta.endswith('.ts'):
                    serviceref = eServiceReference('1:0:0:0:0:0:0:0:0:0:' + rutacompleta)
                    serviceHandler = eServiceCenter.getInstance()
                    info = serviceHandler.info(serviceref)
                    evt = info.getEvent(serviceref)
                    txt = ''
                    if info is not None:
                        txt = info.getName(serviceref)
                        if txt is not '' and txt is not None:
                            self.titulo = txt
                    if evt:
                        if evt is None:
                            return
                        text = text + evt.getEventName()
                        short = evt.getShortDescription()
                        ext = evt.getExtendedDescription()
                        if short and short != text:
                            text += '\n\n' + short
                        if ext:
                            if text:
                                text += '\n\n'
                            text += ext
                        argumento = ''
                        self.titulo = evt.getEventName()
                        argumento = argumento + _('Recording Date') + ': ' + evt.getBeginTimeString() + ', '
                        argumento = argumento + _('Duration') + ': ' + _('%d min') % (evt.getDuration() / 60) + '\n'
                        argumento = argumento + '---------------------------------------------------------------------\n'
                        argumento = argumento + text + textadd
                        if len(argumento) > 5:
                            self['argumento'].setText(argumento)
                        else:
                            self['argumento'].setText(_('There is no argument available for this film'))
                    elif txt is not '' and txt is not None:
                        self['argumento'].setText(_('Title') + ': ' + txt)
            except Exception as e:
                self['argumento'].setText(_('There is no argument available for this film'))

    def getInetInfo(self):
        if fileExists('/usr/lib/enigma2/python/Plugins/Extensions/' + self.pluginimdb + '/plugin.pyo'):
            ernombre = limpianombre(self.titulo)
            self.getInetInfoCallBack(ernombre)

    def getInetInfoCallBack(self, ernombre):
        if ernombre == '' or ernombre == None:
            return
        try:
            from Plugins.Extensions.spzIMDB.plugin import spzIMDB
            spzIMDB(self.session, tbusqueda=ernombre, truta=self.fileinfo)
        except:
            pass

    def Exit(self):
        self.close(None)


class MC_VideoInfoFull(MC_VideoInfo):
    skin = '\n\t\t<screen name="MRUPlayerInfoFull" position="0,0" size="1280,720" title="%s" flags="wfNoBorder" backgroundColor="#030000">\n\t\t  <widget name="nombre" position="383,167" size="712,50" font="Regular; 20" transparent="1" valign="top" />\n\t\t  <widget name="carpeta" position="383,222" size="712,25" font="Regular; 20" transparent="1" />\n\t\t  <widget name="fecha" position="383,252" size="712,25" font="Regular; 20" transparent="1" />\n\t\t  <widget name="tamano" position="383,282" size="712,25" font="Regular; 20" transparent="1" />\n\t\t  <eLabel name="linea2" position="170,316" zPosition="5" size="930,1" transparent="0" foregroundColor="#10555555" backgroundColor="#10555555" />\n\t\t  <widget name="t1" position="172,167" size="199,25" transparent="1" font="Regular; 20" halign="right" backgroundColor="#30000000" foregroundColor="#bbbbbb" />\n\t\t  <widget name="t2" position="172,222" size="199,25" transparent="1" font="Regular; 20" halign="right" foregroundColor="#bbbbbb" />\n\t\t  <widget name="t3" position="172,252" size="199,25" transparent="1" font="Regular; 20" halign="right" foregroundColor="#bbbbbb" />\n\t\t  <widget name="t4" position="172,282" size="199,25" transparent="1" font="Regular; 20" halign="right" foregroundColor="#bbbbbb" />\n\t\t\t<widget name="caratula" position="170,325" size="215,271" alphatest="on" />\n\t\t  <widget name="argumento" position="395,326" size="705,269" transparent="1" zPosition="10" font="Regular; 21" valign="top" />\n\t\t  <widget name="pred" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/skins/default/images/icons/key-red.png" position="136,630" zPosition="2" size="150,30" transparent="1" alphatest="on" />\n\t\t  <widget name="buttonreed" position="136,630" zPosition="5" size="150,30" valign="center" halign="center" font="Regular; 16" transparent="1" />\n\t\t  <widget name="pgreen" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/skins/default/images/icons/key-green.png" position="422,630" zPosition="2" size="150,30" transparent="1" alphatest="on" />\n\t\t  <widget name="buttongreen" position="422,630" zPosition="5" size="150,30" valign="center" halign="center" font="Regular; 16" transparent="1" />\n\t\t  <widget name="pinfo" position="776,636" zPosition="4" size="35,25" transparent="1" alphatest="blend" />\n\t\t  <widget name="buttoninfo" position="810,636" zPosition="5" size="310,25" valign="center" halign="left" font="Regular; 16" transparent="1" />\n\t\t  <ePixmap name="fondo" position="0,0" size="1278,720" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/skins/default/images/videobginfo.jpg" zPosition="-3" />\n\t\t  <!--<widget name="imagen_fondo" position="0,0" zPosition="-2" size="1280,720" alphatest="on" />-->\n\t\t</screen>' % _('Movie Information')

    def __init__(self, session, reference = None, folder = None, file = None, **kwargs):
        MC_VideoInfo.__init__(self, session, mreference=reference, mfolder=folder, mfile=file, **kwargs)


def VideoInfoMain(session, reference = None, folder = None, file = None, fullScreen = False, **kwargs):
    if fullScreen:
        session.open(MC_VideoInfoFull, reference, folder, file)
    else:
        session.open(MC_VideoInfo, reference, folder, file)
