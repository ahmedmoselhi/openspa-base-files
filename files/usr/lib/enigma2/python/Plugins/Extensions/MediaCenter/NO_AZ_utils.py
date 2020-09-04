from Screens.MinuteInput import MinuteInput
from Screens.ServiceInfo import ServiceInfoList, ServiceInfoListEntry
from Screens.HelpMenu import HelpableScreen
from Screens.MessageBox import MessageBox
from Screens.ChoiceBox import ChoiceBox
from Screens.InfoBarGenerics import InfoBarSeek, InfoBarPVRState, InfoBarCueSheetSupport, InfoBarShowHide, InfoBarNotifications, InfoBarAudioSelection, InfoBarSubtitleSupport
from Tools import Notifications
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
from Tools.Directories import resolveFilename, fileExists, pathExists, createDir, SCOPE_MEDIA
from Components.Sources.StaticText import StaticText
from Components.MenuList import MenuList
from Components.ServiceEventTracker import ServiceEventTracker, InfoBarBase
import os
from os import path as os_path, remove as os_remove, listdir as os_listdir, system
from MC_SeekInput import SeekInput
from MC_Menus import IniciaSelListMC, Scalingmode_Menu, ScalingmodeEntryComponent, SubOptionsEntryComponent
config.plugins.mc_mrua = ConfigSubsection()
config.plugins.mc_mrua.subenc = ConfigSelection(default='43', choices=[('42', _('Latin')), ('43', _('Utf-8'))])
config.plugins.mc_mrua.subpos = ConfigInteger(default=40, limits=(0, 100))
config.plugins.mc_mrua.subcolorname = ConfigText('White', fixed_size=False)
config.plugins.mc_mrua.subcolorinside = ConfigText('FFFFFFFF', fixed_size=False)
config.plugins.mc_mrua.subcoloroutside = ConfigText('FF000000', fixed_size=False)
config.plugins.mc_mrua.subsize = ConfigInteger(default=30, limits=(5, 100))
config.plugins.mc_mrua.subdelay = ConfigInteger(default=0, limits=(-999999, 999999))
config.plugins.mc_mrua.screenres = ConfigInteger(default=0, limits=(-999999, 999999))
config.plugins.mc_mrua.repeat = ConfigYesNo(default=False)
from Plugins.Extensions.spazeMenu.spzPlugins.scrInformation.plugin import scrInformation, mostrarNotificacion
from timeSleepMRU import timesleep, timesleepBack
from time import localtime

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


from os import environ
import gettext
from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE
lang = language.getLanguage()
environ['LANGUAGE'] = lang[:2]
gettext.bindtextdomain('enigma2', resolveFilename(SCOPE_LANGUAGE))
gettext.textdomain('enigma2')
gettext.bindtextdomain('AZ_MRUAPlayer', '%s%s' % (resolveFilename(SCOPE_PLUGINS), 'Extensions/MediaCenter/locale/'))

def _(txt):
    t = gettext.dgettext('AZ_MRUAPlayer', txt)
    if t == txt:
        t = gettext.gettext(txt)
    return t


config.plugins.mc_mrua.list1 = ConfigText(default=_('PlayList File') + '1')
config.plugins.mc_mrua.list2 = ConfigText(default=_('PlayList File') + '2')
config.plugins.mc_mrua.list3 = ConfigText(default=_('PlayList File') + '3')
config.plugins.mc_mrua.list4 = ConfigText(default=_('PlayList File') + '4')
config.plugins.mc_mrua.list5 = ConfigText(default=_('PlayList File') + '5')
config.plugins.mc_mrua.list6 = ConfigText(default=_('PlayList File') + '6')
config.plugins.mc_mrua.list7 = ConfigText(default=_('PlayList File') + '7')
config.plugins.mc_mrua.list8 = ConfigText(default=_('PlayList File') + '8')
config.plugins.mc_mrua.list9 = ConfigText(default=_('PlayList File') + '9')

def retRuta(rutaarchivo, max = 70, sepa = ' :: '):
    max = max
    ret = rutaarchivo
    carpetas = rutaarchivo.split('/')
    nombre = carpetas[len(carpetas) - 1]
    ruta = rutaarchivo[0:len(rutaarchivo) - len(nombre)]
    ret = nombre + sepa + ruta
    if len(ret) > max and len(carpetas) > 2:
        dife = len(ret) - max + 3
        ruta1 = '/' + carpetas[1]
        carpun = '...'
        if len(carpetas) > 3:
            ruta3 = '/' + carpetas[len(carpetas) - 2] + '/'
            ruta2 = ruta[len(ruta1) + dife:len(ruta) - len(ruta3)]
        else:
            ruta3 = ''
            ruta2 = ''
        if len(carpetas) <= 4:
            carpun = ''
        else:
            ruta1 = ruta1 + '/'
        ruta = ruta1 + carpun + '' + ruta2 + '' + ruta3
        ret = nombre + sepa + ruta
    if len(ret) > max:
        ext = nombre[-4:]
        nombre = nombre.replace(ext, '')
        nmax = len(ret) - max
        nmax = len(nombre) - nmax
        if nmax < 15:
            nmax = 15
        nombre = nombre[0:nmax - 2]
        ret = nombre + '..' + ext + sepa + ruta
    return ret


from Components.MultiContent import MultiContentEntryText
from enigma import eListboxPythonMultiContent, eServiceCenter, gFont, RT_HALIGN_RIGHT
from Tools.LoadPixmap import LoadPixmap

class IniciaSelListMC(MenuList):

    def __init__(self, list, enableWrapAround = False):
        MenuList.__init__(self, list, enableWrapAround, eListboxPythonMultiContent)
        self.l.setItemHeight(30)
        self.l.setFont(0, gFont('Regular', 19))
        self.l.setFont(1, gFont('Regular', 17))


def IniciaSelListEntryMC(texto, imagen = 'na', max = 0):
    res = [texto]
    if max > 0:
        texto = retRuta(texto, max)
        scale = ((1, 1), (1, 1))
        texto1 = texto.split(' :: ')[0]
        texto2 = texto.split(' :: ')[1]
        if max > 90:
            tam = 1148
        else:
            tam = 823
        texto = texto1
        res.append(MultiContentEntryText(pos=(0, 4), size=(tam, 30), font=0, flags=RT_HALIGN_RIGHT, text=texto2, color=8947848))
    res.append(MultiContentEntryText(pos=(42, 4), size=(1000, 30), font=0, text=texto))
    carpetaimg = '/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/images/'
    png = '' + carpetaimg + 'MC_vo' + imagen + '-fs8.png'
    if not fileExists(png):
        png = carpetaimg + 'MC_vona-fs8.png'
    if fileExists(png):
        fpng = LoadPixmap(png)
        res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND,
         2,
         2,
         35,
         25,
         fpng))
    return res


def savefilepl(lista, nombrear):
    if len(lista) < 0:
        return False
    else:
        try:
            booklist = open('/etc/tuxbox/' + nombrear, 'w')
        except:
            return False

        if booklist is not None:
            for elemento in lista:
                nombre = elemento
                booklist.write(nombre + '\n')

            booklist.close()
            return True
        return False


def getfilepl(nombrear):
    list = []
    booklist = None
    try:
        booklist = open('/etc/tuxbox/' + nombrear, 'r')
    except:
        pass

    if booklist is not None:
        for oneline in booklist:
            cadena = oneline.replace('\n', '')
            if len(cadena) > 3:
                list.append(cadena)

        booklist.close()
    return list


def devlistasR():
    listasR = []
    listasR.append((config.plugins.mc_mrua.list1.value, 'mrua_playlist1.txt'))
    listasR.append((config.plugins.mc_mrua.list2.value, 'mrua_playlist2.txt'))
    listasR.append((config.plugins.mc_mrua.list3.value, 'mrua_playlist3.txt'))
    listasR.append((config.plugins.mc_mrua.list4.value, 'mrua_playlist4.txt'))
    listasR.append((config.plugins.mc_mrua.list5.value, 'mrua_playlist5.txt'))
    listasR.append((config.plugins.mc_mrua.list6.value, 'mrua_playlist6.txt'))
    listasR.append((config.plugins.mc_mrua.list7.value, 'mrua_playlist7.txt'))
    listasR.append((config.plugins.mc_mrua.list8.value, 'mrua_playlist8.txt'))
    listasR.append((config.plugins.mc_mrua.list9.value, 'mrua_playlist9.txt'))
    return listasR


class MRUA_playlistSelection(Screen):
    skin = '\n\t\t<screen name="MRUAPlayer_playlistSelection" position="center,center" size="1200,500" title="%s">\n\t\t<widget name="list" zPosition="5" transparent="1" position="10,20" size="300,450" scrollbarMode="showOnDemand" />\n\t\t<eLabel name="bandaver" position="312,22" size="1,450" zPosition="10" backgroundColor="#10555555" />\n\t\t<widget name="list2" zPosition="5" transparent="1" position="315,22" size="855,450" scrollbarMode="showOnDemand" />\n\t\t\n\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/images/green.png" position="45,475" zPosition="2" size="35,25" transparent="1" alphatest="on" />\n\t\t<widget name="key_green" zPosition="5" transparent="1" position="80,475" size="100,25" font="Regular;18" />\t\n\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/images/yellow.png" position="315,475" zPosition="2" size="35,25" transparent="1" alphatest="on" />\n\t\t<widget name="key_yellow" zPosition="5" transparent="1" position="350,475" size="239,25" font="Regular;18" />\n\t\t<widget name="key_info" zPosition="5" transparent="1" position="617,475" size="553,20" font="Regular; 16" halign="right" shadowColor="#000000" shadowOffset="-2,-2" foregroundColor="#999999" backgroundColor="#000000" />\n\t\t<widget name="key_titulo" zPosition="5" transparent="1" position="315,0" size="855,20" font="Regular; 16" halign="center" shadowColor="#000000" shadowOffset="-2,-2" foregroundColor="#999999" backgroundColor="#000000" />\n\t</screen>' % _('PlayList')

    def __init__(self, session, titulo, list, laaccion):
        Screen.__init__(self, session)
        self['list'] = IniciaSelListMC([])
        self['list2'] = IniciaSelListMC([])
        self.list = list
        self['key_green'] = Label(_('Rename'))
        self['key_yellow'] = Label(_('Clear'))
        self['key_titulo'] = Label(_(' '))
        self['key_info'] = Label(_(' '))
        self.accion = laaccion
        self['actions'] = ActionMap(['OkCancelActions', 'ColorActions', 'DirectionActions'], {'yellow': self.limpiar,
         'red': self.nada,
         'green': self.renombra,
         'blue': self.nada,
         'right': self.key_right,
         'left': self.key_left,
         'up': self.key_up,
         'down': self.key_down,
         'cancel': self.Exit,
         'ok': self.okbuttonClick}, -1)
        self.setTitle(titulo)
        self.onLayoutFinish.append(self.inicia)
        self.tiempo = eTimer()
        self.tiempo.callback.append(self.cargalista)

    def Exit(self):
        self.close(None)

    def limpiar(self):
        laref = _('Are you sure to clear all items in current list?')
        nombrear = self.list[self['list'].getSelectionIndex()][0]
        laref = laref + '\n' + nombrear
        dei = self.session.openWithCallback(self.cblimpiar, MessageBox, laref, MessageBox.TYPE_YESNO)
        dei.setTitle(_('Clear'))

    def renombra(self):
        from Plugins.Extensions.spazeMenu.spzVirtualKeyboard import spzVirtualKeyboard
        nombrear = self.list[self['list'].getSelectionIndex()][0]
        self.session.openWithCallback(self.nuevaBcb, spzVirtualKeyboard, titulo=_('Rename') + ' ' + _('PlayList'), texto=nombrear, ok=False)

    def nuevaBcb(self, ernombre):
        if ernombre == '' or ernombre == None:
            return
        numero = self['list'].getSelectionIndex()
        if numero == 0:
            config.plugins.mc_mrua.list1.value = ernombre
            config.plugins.mc_mrua.list1.save()
        elif numero == 1:
            config.plugins.mc_mrua.list2.value = ernombre
            config.plugins.mc_mrua.list2.save()
        elif numero == 2:
            config.plugins.mc_mrua.list3.value = ernombre
            config.plugins.mc_mrua.list3.save()
        elif numero == 3:
            config.plugins.mc_mrua.list4.value = ernombre
            config.plugins.mc_mrua.list4.save()
        elif numero == 4:
            config.plugins.mc_mrua.list5.value = ernombre
            config.plugins.mc_mrua.list5.save()
        elif numero == 5:
            config.plugins.mc_mrua.list6.value = ernombre
            config.plugins.mc_mrua.list6.save()
        elif numero == 6:
            config.plugins.mc_mrua.list7.value = ernombre
            config.plugins.mc_mrua.list7.save()
        elif numero == 7:
            config.plugins.mc_mrua.list8.value = ernombre
            config.plugins.mc_mrua.list8.save()
        elif numero == 8:
            config.plugins.mc_mrua.list9.value = ernombre
            config.plugins.mc_mrua.list9.save()
        config.plugins.mc_mrua.save()
        self.list = []
        listatemp = devlistasR()
        for ele in listatemp:
            self.list.append(ele)

        self.buildList()

    def cblimpiar(self, respuesta):
        if respuesta:
            listavacia = []
            numero = self['list'].getSelectionIndex() + 1
            nombrear = self.list[self['list'].getSelectionIndex()][1]
            try:
                booklist = open('/etc/tuxbox/' + nombrear, 'w')
                nombrear = self.list[self['list'].getSelectionIndex()][0]
                dei = self.session.open(MessageBox, _('PlayList saved to disk') + '\n' + nombrear, MessageBox.TYPE_INFO, timeout=4)
                dei.setTitle(_('Clear'))
            except:
                return False

            self.cargalista()

    def nada(self):
        pass

    def okbuttonClick(self):
        self.close(self.accion + str(self['list'].getSelectionIndex() + 1))

    def key_left(self):
        self['list2'].pageUp()

    def key_right(self):
        self['list2'].pageDown()

    def cargalista(self):
        self.tiempo.stop()
        self.buildList2()

    def key_up(self):
        self.tiempo.stop()
        self.limpialista()
        if self['list'].getSelectionIndex() == 0:
            self['list'].moveToIndex(len(self['list'].list) - 1)
        else:
            self['list'].up()
        self.tiempo.start(1500, True)

    def key_down(self):
        self.tiempo.stop()
        self.limpialista()
        if self['list'].getSelectionIndex() == len(self['list'].list) - 1:
            self['list'].moveToIndex(0)
        else:
            self['list'].down()
        self.tiempo.start(1500, True)

    def inicia(self):
        self.buildList()
        self['list2'].selectionEnabled(0)
        self.cargalista()

    def limpialista(self):
        list = []
        self['key_titulo'].setText(' ')
        self['key_info'].setText(' ')
        self['list2'].setList(list)
        self['list2'].selectionEnabled(0)

    def buildList(self):
        list = []
        for i in range(0, len(self.list)):
            texto = '' + self.list[i][0]
            icono = '7'
            list.append(IniciaSelListEntryMC(texto, icono))

        self['list'].setList(list)

    def buildList2(self):
        list = []
        nombrear = self.list[self['list'].getSelectionIndex()][1]
        listacontenido = getfilepl(nombrear)
        if len(listacontenido) == 0:
            list.append(IniciaSelListEntryMC('(' + _('Empty list. No file found in playlist.') + ')', '5'))
        else:
            for i in range(0, len(listacontenido)):
                texto = '' + listacontenido[i]
                icono = '90'
                if not fileExists(texto):
                    icono = '91'
                list.append(IniciaSelListEntryMC(texto, icono, 78))

        self['list2'].setList(list)
        ele = self.list[self['list'].getSelectionIndex()]
        self['key_titulo'].setText(_(ele[0]))
        if len(listacontenido) == 0:
            self['key_info'].setText('0 ' + _('item(s) in list'))
        else:
            self['key_info'].setText(str(len(list)) + ' ' + _('item(s) in list'))


class MRUAPlayer_playlist(Screen):
    skin = '\n\t\t<screen name="MRUAPlayer_playlist" position="center,center" size="1200,500" title="%s">\n\t\t\t\t<widget name="info" transparent="1" zPosition="2" position="0,0" size="1200,20" font="Regular;16" foregroundColor="#999999" backgroundColor="#000000" shadowColor="#000000" shadowOffset="-2,-2" />\n\t\t\t\t<widget name="list" zPosition="5" transparent="1" position="10,20" size="1180,450" scrollbarMode="showOnDemand" />\n\t\t\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/images/red.png" position="5,475" zPosition="2" size="35,25" transparent="1" alphatest="on" />\n\t\t\t\t<widget name="key_red" zPosition="5" transparent="1" position="40,475" size="100,25" font="Regular;18" />\n\t\t\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/images/yellow.png" position="140,475" zPosition="2" size="35,25" transparent="1" alphatest="on" />\n\t\t\t\t<widget name="key_yellow" zPosition="5" transparent="1" position="175,475" size="100,25" font="Regular;18" />\t\n\n\t\t\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/images/green.png" position="280,475" zPosition="2" size="35,25" transparent="1" alphatest="on" />\n\t\t\t\t<widget name="key_green" zPosition="5" transparent="1" position="315,475" size="160,25" font="Regular;18" />\t\n\t\t\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/images/blue.png" position="480,475" zPosition="2" size="35,25" transparent="1" alphatest="on" />\n\t\t\t\t<widget name="key_blue" zPosition="5" transparent="1" position="515,475" size="200,25" font="Regular;18" />\t\t\n\t\t\t\t<widget name="key_chmas" zPosition="5" transparent="1" position="890,475" size="136,25" font="Regular;18" />\n\t\t\t\t<widget name="key_chmenos" zPosition="5" transparent="1" position="1065,475" size="135,25" font="Regular;18" />\n\t\t\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/images/chmas.png" position="853,475" zPosition="15" size="35,25" transparent="1" alphatest="on" />\n\t\t\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/images/chmenos.png" position="1028,475" zPosition="15" size="35,25" transparent="1" alphatest="on" />\n\t\t\t\t<widget name="key_info" zPosition="15" transparent="1" position="755,475" size="96,25" font="Regular;18" />\n\t\t\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/images/info.png" position="719,475" zPosition="15" size="35,25" transparent="1" alphatest="on" />\n\n\t\t</screen>' % _('PlayList')

    def __init__(self, session, lista, lainfo = '', selini = ''):
        Screen.__init__(self, session)
        self['list'] = IniciaSelListMC([])
        self.list = []
        self.selini = selini
        if len(lista) == 0:
            lainfo = '(' + _('Empty list. No file found in playlist.') + ')' + ' :: ' + _('Add files or load saved playlist with [BLUE] button')
        else:
            if not lainfo == '':
                lainfo = lainfo + ' :: '
            lainfo = lainfo + str(len(lista)) + ' ' + _('item(s) in list') + ':'
        self['info'] = Label(_(lainfo))
        self['key_red'] = Label(_('Delete'))
        self['key_yellow'] = Label(_('Clear'))
        self['key_green'] = Label(_('Save to disk'))
        self['key_blue'] = Label(_('Load playlist'))
        self['key_chmas'] = Label(_('Move Up'))
        self['key_chmenos'] = Label(_('Move Down'))
        self['key_info'] = Label(_('Info'))
        self.archivo = 'mura_playlist.txt'
        self.listasR = []
        listatemp = devlistasR()
        for ele in listatemp:
            self.listasR.append(ele)

        for ele in lista:
            self.list.append(ele)

        self['actions'] = ActionMap(['OkCancelActions',
         'ColorActions',
         'ChannelSelectBaseActions',
         'DirectionActions',
         'InfobarEPGActions'], {'yellow': self.limpiar,
         'red': self.borrar,
         'green': self.guardar,
         'blue': self.cargar,
         'cancel': self.Exit,
         'ok': self.okbuttonClick,
         'right': self.key_right,
         'left': self.key_left,
         'up': self.key_up,
         'down': self.key_down,
         'nextBouquet': self.mueveup,
         'prevBouquet': self.muevedw,
         'showEventInfo': self.movieinfo}, -1)
        self.gnom = ''
        self.gnum = ''
        self.onLayoutFinish.append(self.buildList)

    def movieinfo(self):
        if len(self.list) < 1:
            return
        selection = self['list'].getSelectionIndex()
        refar = self.list[selection]
        if not fileExists(refar):
            dei = self.session.open(MessageBox, _('File not avaiable!') + ':\n' + refar, MessageBox.TYPE_ERROR)
            dei.setTitle(_('PlayList'))
        else:
            from AZ_MRUAvideoinfo import VideoInfoMain
            VideoInfoMain(self.session, reference=refar)

    def key_left(self):
        self['list'].pageUp()
        self.actualizabotones()

    def key_right(self):
        self['list'].pageDown()
        self.actualizabotones()

    def key_up(self):
        if len(self.list) <= 1:
            return
        selection = self['list'].getSelectionIndex()
        if selection == 0:
            self['list'].moveToIndex(len(self.list) - 1)
        else:
            self['list'].up()
        self.actualizabotones()

    def key_down(self):
        if len(self.list) <= 1:
            return
        selection = self['list'].getSelectionIndex()
        if selection == len(self.list) - 1:
            self['list'].moveToIndex(0)
        else:
            self['list'].down()
        self.actualizabotones()

    def menulistas(self, accion):
        dei = self.session.openWithCallback(self.cbmenulistasS, MRUA_playlistSelection, titulo=_('Select playlist to') + ' ' + _(accion), list=self.listasR, laaccion=accion)

    def cbmenulistasS(self, answer):
        self.listasR = []
        listatemp = devlistasR()
        for ele in listatemp:
            self.listasR.append(ele)

        if answer == None:
            return
        if 'save' in answer:
            numero = int(answer.replace('save', ''))
            self.guardararchivo(self.listasR[numero - 1][1], numero)
        elif 'load' in answer:
            numero = int(answer.replace('load', ''))
            self.cargararchivo(self.listasR[numero - 1][1], numero)

    def buildList(self):
        list = []
        activo = -1
        for i in range(0, len(self.list)):
            texto = '' + self.list[i]
            icono = '90'
            if not fileExists(texto):
                icono = '91'
            list.append(IniciaSelListEntryMC(texto, icono, 104))
            if not self.selini == '' and texto == self.selini:
                self.selini = ''
                activo = i

        self['list'].setList(list)
        if activo >= 0:
            self['list'].moveToIndex(activo)
        self.actualizabotones()

    def mueveup(self):
        if len(self.list) <= 1:
            return
        selection = self['list'].getSelectionIndex()
        if selection == 0:
            return
        newindex = selection - 1
        self.list.insert(newindex, self.list.pop(selection))
        self.buildList()
        self['list'].moveToIndex(newindex)
        self.actualizabotones()

    def muevedw(self):
        if len(self.list) <= 1:
            return
        selection = self['list'].getSelectionIndex()
        if selection >= len(self.list) - 1:
            return
        newindex = selection + 1
        self.list.insert(newindex, self.list.pop(selection))
        self.buildList()
        self['list'].moveToIndex(newindex)
        self.actualizabotones()

    def actualizabotones(self):
        if len(self.list) <= 1:
            self['key_chmas'].hide()
            self['key_chmenos'].hide()
            if len(self.list) == 0:
                self['key_info'].hide()
                self['info'].setText('(' + _('Empty list. No file found in playlist.') + ')' + ' :: ' + _('Add files or load saved playlist with [BLUE] button'))
            else:
                self['info'].setText(str(len(self.list)) + ' ' + _('item(s) in list') + ':')
            return
        selection = self['list'].getSelectionIndex()
        if selection == 0:
            self['key_chmas'].hide()
        else:
            self['key_chmas'].show()
        if selection >= len(self.list) - 1:
            self['key_chmenos'].hide()
        else:
            self['key_chmenos'].show()
        self['key_info'].show()
        self['info'].setText(str(len(self.list)) + ' ' + _('item(s) in list') + ':')

    def guardar(self):
        self.menulistas('save')

    def guardararchivo(self, nombre, numero):
        mesn = _('Overwrite playlist') + ':\n' + self.listasR[numero - 1][0] + '?'
        self.gnom = nombre
        self.gnum = numero
        self.session.openWithCallback(self.cbguarda, MessageBox, mesn)

    def cbguarda(self, resp):
        if resp:
            nombre = self.gnom
            numero = self.gnum
            ret = savefilepl(self.list, nombre)
            if ret:
                dei = self.session.open(MessageBox, _('PlayList saved to disk') + '\n' + self.listasR[numero - 1][0] + '\n' + _('File') + ': ' + '/etc/tuxbox/' + nombre, MessageBox.TYPE_INFO, timeout=4)
                dei.setTitle(_('Save to disk'))

    def cargar(self):
        if len(self.list) > 0:
            mesn = _('The current playlist are loss.\nLoad saved playlist?')
            self.session.openWithCallback(self.cbcargar, MessageBox, mesn)
        else:
            self.menulistas('load')

    def cbcargar(self, resp):
        if resp:
            self.menulistas('load')

    def cargararchivo(self, nombre, numero):
        ret = getfilepl(nombre)
        if len(ret) == 0:
            dei = self.session.open(MessageBox, _('Saved PlayList is empty!!!') + '\n' + self.listasR[numero - 1][0], MessageBox.TYPE_INFO, timeout=4)
            dei.setTitle(_('Load playlist'))
            return
        self.list = []
        for ele in ret:
            self.list.append(ele)

        self.session.open(scrInformation, texto=_('Playlist loaded'), segundos=1, mostrarSegundos=False)
        self.buildList()

    def borrar(self):
        selection = self['list'].getSelectionIndex()
        del self.list[selection]
        self.buildList()

    def limpiar(self):
        mesn = _('Do you want to clear playlist?')
        self.session.openWithCallback(self.cblimpiar, MessageBox, mesn)

    def cblimpiar(self, resp):
        if resp:
            self.list = []
            self.buildList()

    def okbuttonClick(self):
        if len(self.list) > 0:
            selection = self['list'].getSelectionIndex()
        else:
            selection = None
        tlista = []
        tlista.append(selection)
        tlista.append(self.list)
        self.close(tlista)

    def Exit(self):
        tlista = []
        tlista.append(None)
        tlista.append(self.list)
        self.close(tlista)


class MRUAPlayer_Menu(Screen):
    skin = '\n\t<screen name="MRUAPlayer_Menu" position="30,55" size="350,240" title="%s" >\n\t<widget name="pathlabel" transparent="1" zPosition="2" position="0,220" size="380,20" font="Regular;16" />\n\t<widget name="list" zPosition="5" transparent="1" position="10,10" size="330,200" scrollbarMode="showOnDemand" />\n\t</screen>' % _('VideoPlayer - Menu')

    def __init__(self, session):
        Screen.__init__(self, session)
        self['list'] = IniciaSelListMC([])
        self.list = []
        self.list.append(_('Go to position'))
        self.list.append(_('Brigtness setup'))
        self.list.append(_('Scaling mode'))
        self.list.append(_('Subtitle Selection'))
        self.list.append(_('Audio Selection'))
        self.list.append(_('Movie Information'))
        valorrepeat = config.plugins.mc_mrua.repeat.value
        if valorrepeat:
            txtr = _('Repeat') + '(' + _('Yes') + ')'
        else:
            txtr = _('Repeat') + '(' + _('No') + ')'
        self.list.append(txtr)
        self.list.append(_('PlayList') + '...')
        self['pathlabel'] = Label(_('Select option'))
        self['actions'] = ActionMap(['OkCancelActions', 'ColorActions'], {'yellow': self.setaudio,
         'red': self.setsubtitle,
         'cancel': self.Exit,
         'ok': self.okbuttonClick}, -1)
        self.onLayoutFinish.append(self.buildList)

    def buildList(self):
        list = []
        for i in range(0, len(self.list)):
            texto = '' + self.list[i]
            list.append(IniciaSelListEntryMC(texto, str(i)))

        self['list'].setList(list)

    def setaudio(self):
        self.close(2)

    def setsubtitle(self):
        self.close(3)

    def okbuttonClick(self):
        selection = self['list'].getSelectionIndex()
        self.close(selection)

    def Exit(self):
        self.close(None)
