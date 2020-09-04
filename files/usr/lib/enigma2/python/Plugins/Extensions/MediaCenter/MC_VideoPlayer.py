from Screens.Screen import Screen
from Screens.ServiceInfo import ServiceInfoList, ServiceInfoListEntry
from Screens.HelpMenu import HelpableScreen
from Screens.MessageBox import MessageBox
from Screens.ChoiceBox import ChoiceBox
from Components.ActionMap import ActionMap, NumberActionMap, HelpableActionMap
from Components.Pixmap import Pixmap, MovingPixmap
from Components.SystemInfo import SystemInfo
from Components.Label import Label
from Components.Button import Button
from Components.config import *
from Tools.Directories import resolveFilename, fileExists, pathExists, SCOPE_MEDIA
import os
from Plugins.Extensions.spazeMenu.sbar import openspaSB
from MC_Filelist import FileList, setResumePoint, getResumePoint
from enigma import ePicLoad
from Components.AVSwitch import AVSwitch
from Components.MovieList import MovieList
from Plugins.Extensions.spazeMenu.plugin import limpiamemoria
from os import environ
import gettext
from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_CURRENT_SKIN, SCOPE_SKIN_IMAGE, SCOPE_LANGUAGE
from enigma import eServiceCenter
lang = language.getLanguage()
environ['LANGUAGE'] = lang[:2]
gettext.bindtextdomain('enigma2', resolveFilename(SCOPE_LANGUAGE))
gettext.textdomain('enigma2')
gettext.bindtextdomain('MC_VideoPlayer', '%s%s' % (resolveFilename(SCOPE_PLUGINS), 'Extensions/MediaCenter/locale/'))
ismrua = False
if fileExists('/usr/bin/rmfp_player') and fileExists('/usr/bin/dvd_player') and fileExists('/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/serviceazdvd.so') and (fileExists('/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/AZservicemrua.so') or fileExists('/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/serviceazdvd.so')):
    if fileExists('/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/AZservicemrua.so'):
        import AZservicemrua
    elif fileExists('/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/serviceazdvd.so'):
        import servicemrua
    import serviceazdvd
    ismrua = True

def _(txt):
    t = gettext.dgettext('MC_VideoPlayer', txt)
    if t == txt:
        t = gettext.gettext(txt)
    return t


config.plugins.mc_mrua = ConfigSubsection()
config.plugins.mc_mrua.repeat = ConfigYesNo(default=False)
from NO_AZ_utils import *
from Plugins.Extensions.spazeMenu.spzPlugins.scrInformation.plugin import scrInformation, mostrarNotificacion
config.plugins.mc_mrua.list1 = ConfigText(default=_('PlayList File') + '1')
config.plugins.mc_mrua.list2 = ConfigText(default=_('PlayList File') + '2')
config.plugins.mc_mrua.list3 = ConfigText(default=_('PlayList File') + '3')
config.plugins.mc_mrua.list4 = ConfigText(default=_('PlayList File') + '4')
config.plugins.mc_mrua.list5 = ConfigText(default=_('PlayList File') + '5')
config.plugins.mc_mrua.list6 = ConfigText(default=_('PlayList File') + '6')
config.plugins.mc_mrua.list7 = ConfigText(default=_('PlayList File') + '7')
config.plugins.mc_mrua.list8 = ConfigText(default=_('PlayList File') + '8')
config.plugins.mc_mrua.list9 = ConfigText(default=_('PlayList File') + '9')
from enigma import eEnv

def rutapicon(serviceName):
    serviceName = serviceName.replace(':', '_')
    serviceName = serviceName[:-1]
    searchPaths = [eEnv.resolve('${datadir}/enigma2/%s/'), '/media/cf/%s/', '/media/usb/%s/']
    piconpath = 'picon'
    try:
        cpath = str(config.misc.picon_path.value)
    except:
        cpath = 'none'

    pngname = cpath + serviceName + '.png'
    if fileExists(pngname):
        return pngname
    cpath = cpath + '%s/'
    if cpath not in searchPaths:
        searchPaths.append(cpath)
    for path in searchPaths:
        pngname = path % piconpath + serviceName + '.png'
        if fileExists(pngname):
            return pngname


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
    tmpnombre = tmpnombre.replace('.', ' ').replace('ts-screener', '').replace('480p', '').replace('xvid', '').replace(' hq ', '').replace('hdtvscreener', '').replace('screener', '').replace('hdtv', '').replace('dvdrip', '').replace('x264', '').replace('divx', '').replace('720p', '').replace('1080p', '').replace('hd', '').replace('ac3', '').replace('dts', '').replace('dual', '').replace('bluray', '').replace('bdrip', '').replace('  ', ' ').replace('()', '').replace('[]', '').replace('  ', ' ').replace('  ', ' ').replace('_', ' ').replace('Cine:', '')
    return tmpnombre.strip()


from Components.MultiContent import MultiContentEntryText
from enigma import eListboxPythonMultiContent, gFont, getDesktop
from Tools.LoadPixmap import LoadPixmap
from Components.MenuList import MenuList

class IniciaSelList2(MenuList):

    def __init__(self, list, enableWrapAround = False):
        MenuList.__init__(self, list, enableWrapAround, eListboxPythonMultiContent)
        self.l.setItemHeight(64)
        self.l.setFont(0, gFont('Regular', 23))
        self.l.setFont(1, gFont('Regular', 17))


protegidos = 2
haylast = False
haystart = False

def devicono(quelugar, quenombre):
    global haylast
    global haystart
    global protegidos
    ret = ''
    if '[' + _('Last path') + ']' in quenombre and not haylast:
        haylast = True
        ret = ret + 'catlast-fs8.png'
        protegidos = protegidos + 1
    elif '[' + _('Start directory') + ']' in quenombre and not haystart:
        haystart = True
        protegidos = protegidos + 1
        ret = ret + 'cathome-fs8.png'
    elif '[' + _('Records') + ']' in quenombre:
        ret = ret + 'catrecord-fs8.png'
    elif quelugar[:-1] == '/':
        ret = ret + 'catroot-fs8.png'
    elif quelugar[0:10] == '/hdd/movie' or quelugar[0:16] == '/media/hdd/movie':
        ret = ret + 'catfoldermovie-fs8.png'
    elif quelugar[0:12] == '/hdd/picture' or quelugar[0:18] == '/media/hdd/picture':
        ret = ret + 'catphotos-fs8.png'
    elif quelugar[0:10] == '/hdd/music' or quelugar[0:16] == '/media/hdd/music':
        ret = ret + 'catfoldermusic-fs8.png'
    elif quelugar[:-1] == '/hdd/' or quelugar[:-1] == '/media/hdd/' or quelugar[:-1] == '/media/hdd' or quelugar[:-1] == '/hdd':
        ret = ret + 'catdisk-fs8.png'
    elif quenombre[0:1] == '<':
        ret = ret + 'catdisks-fs8.png'
    elif quelugar[0:4] == '/hdd' or quelugar[0:10] == '/media/hdd':
        ret = ret + 'catfolderdisk-fs8.png'
    elif quelugar[:-1] == '/autofs/sda1' or quelugar[:-1] == '/autofs/sdb1' or quelugar[:-1] == '/autofs/sda1/' or quelugar[:-1] == '/autofs/sdb1/' or quelugar[:-1] == '/autofs/sda2' or quelugar[:-1] == '/autofs/sdb2' or quelugar[:-1] == '/autofs/sda2/' or quelugar[:-1] == '/autofs/sdb2/':
        ret = ret + 'catusb-fs8.png'
    elif quelugar[0:11] == '/autofs/sda' or quelugar[0:11] == '/autofs/sdb':
        ret = ret + 'catfolderusb-fs8.png'
    else:
        ret = ret + 'catfolder-fs8.png'
    return ret


def IniciaSelListEntry2(nombre, lugar):
    nuevonombre = '' + ''.join(nombre.split('->')[:-1]) + ''
    if len(nuevonombre) <= 0:
        nuevonombre = nombre
    if len(nuevonombre) <= 0:
        nuevonombre = 'NA'
    res = [lugar]
    if nuevonombre[0] == '[':
        nuevonombre = nuevonombre.replace('[', '').replace(']', '')
    nuevolugar = lugar
    if nuevolugar == '$$&$$':
        nuevolugar = ''
    if nuevolugar == '/ ':
        nuevolugar = _('root folder')
    res.append(MultiContentEntryText(pos=(75, 4), size=(700, 32), font=0, text=nuevonombre))
    res.append(MultiContentEntryText(pos=(85, 32), size=(700, 50), font=1, text=nuevolugar))
    png = '/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/images/'
    png = png + devicono(lugar, nombre)
    if fileExists(png):
        fpng = LoadPixmap(png)
    else:
        png = '/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/images/catfolder-fs8.png'
        fpng = LoadPixmap(png)
    res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHATEST,
     1,
     1,
     63,
     64,
     fpng))
    return res


protegidos = 2

class mc_azFavoritos(Screen):

    def __init__(self, session, list, curpat = '/'):
        Screen.__init__(self, session)
        self.lista = list
        self.curpat = curpat
        self['list'] = IniciaSelList2([])
        self['key_red'] = Label(_('Delete'))
        self['titulo'] = Label(_('Bookmarks'))
        self['linea'] = MovingPixmap()
        if self.curpat == None:
            self.curpat = 'None'
        if self.curpat == 'None':
            self['key_green'] = Label(_(' '))
        else:
            self['key_green'] = Label(_('Add current'))
        self.warning = False
        self['key_yellow'] = Label(_('Up'))
        self['key_blue'] = Label(_('Down'))
        self['img_red'] = Pixmap()
        self['img_green'] = Pixmap()
        self['img_yellow'] = Pixmap()
        self['img_blue'] = Pixmap()
        self.cambiado = False
        self['actions'] = ActionMap(['OkCancelActions', 'ColorActions', 'DirectionActions'], {'red': self.borrar,
         'cancel': self.cerrar,
         'green': self.anadir,
         'yellow': self.sube,
         'blue': self.baja,
         'ok': self.volver}, prio=-1)
        self.onLayoutFinish.append(self.buildList3)
        self.onShow.append(self.mostrar)

    def mostrar(self):
        pass

    def buildList3(self):
        global haylast
        global haystart
        global protegidos
        haystart = False
        haylast = False
        protegidos = 2
        nlista = []
        for iji in self.lista:
            nlista.append(IniciaSelListEntry2(iji[0], iji[1]))

        self['list'].setList(nlista)
        if self.curpat == 'None':
            self['img_green'].hide()
        self.muevesel()
        self['list'].onSelectionChanged.append(self.muevesel)

    def muevesel(self):
        idx = self['list'].getSelectionIndex()
        if idx >= protegidos + 1:
            self['key_yellow'].show()
            self['img_yellow'].show()
        else:
            self['key_yellow'].hide()
            self['img_yellow'].hide()
        if idx < len(self['list'].list) - 1 and idx >= protegidos:
            self['key_blue'].show()
            self['img_blue'].show()
        else:
            self['key_blue'].hide()
            self['img_blue'].hide()
        if idx >= protegidos:
            self['key_red'].show()
            self['img_red'].show()
        else:
            self['key_red'].hide()
            self['img_red'].hide()
        if idx <= 6:
            self['linea'].show()
        else:
            self['linea'].hide()

    def muevelin(self):
        idx = self['list'].getSelectionIndex()

    def key_left(self):
        self['list'].pageUp()
        self.muevelin()

    def key_right(self):
        self['list'].pageDown()
        self.muevelin()

    def key_up(self):
        self['list'].up()
        self.muevelin()

    def key_down(self):
        self['list'].down()
        self.muevelin()

    def sube(self):
        nuevalista = []
        nuevalista2 = []
        conta = 0
        idx = self['list'].getSelectionIndex()
        if idx >= protegidos + 1:
            mover = self['list'].list[idx]
            moverlista = self.lista[idx]
            for x in self['list'].list:
                if conta == idx - 1:
                    nuevalista.append(mover)
                    nuevalista2.append(moverlista)
                if not conta == idx:
                    nuevalista.append(x)
                    nuevalista2.append(self.lista[conta])
                conta = conta + 1

            self.lista = nuevalista2
            self['list'].setList(nuevalista)
            self['list'].moveToIndex(idx - 1)
            self.cambiado = True
        elif not self.warning:
            self.warning = True
            self.session.open(MessageBox, _('First elements protected, unable to move'), MessageBox.TYPE_INFO, timeout=5)

    def baja(self):
        nuevalista = []
        nuevalista2 = []
        conta = 0
        idx = self['list'].getSelectionIndex()
        if idx < len(self['list'].list) - 1 and idx >= protegidos:
            mover = self['list'].list[idx]
            moverlista = self.lista[idx]
            for x in self['list'].list:
                if not conta == idx:
                    nuevalista.append(x)
                    nuevalista2.append(self.lista[conta])
                if conta == idx + 1:
                    nuevalista2.append(moverlista)
                    nuevalista.append(mover)
                conta = conta + 1

            self.lista = nuevalista2
            self['list'].setList(nuevalista)
            self['list'].moveToIndex(idx + 1)
            self.cambiado = True
        elif idx < protegidos and not self.warning:
            self.warning = True
            self.session.open(MessageBox, _('First elements protected, unable to move'), MessageBox.TYPE_INFO, timeout=5)

    def anadir(self):
        if not self.curpat == 'None':
            yahay = False
            idx = 0
            lalista = self['list'].list
            for iji in self.lista:
                if self.curpat.strip() == iji[1][:-1].strip():
                    yahay = True
                    break
                idx = idx + 1

            if not yahay:
                RENfilename = self.curpat.split('/')[-2]
                self.session.openWithCallback(self.anadeBook, vInputBox, title=_('Set name') + ':', windowTitle=_('Add directory to Bookmarks') + ': [' + self.curpat + ']', text=RENfilename)
            else:
                self['list'].moveToIndex(idx)

    def anadeBook(self, nombre):
        if nombre is not None:
            if not nombre == '':
                lista = self['list'].list
                lista.append(IniciaSelListEntry2(nombre, self.curpat + '\n'))
                self.lista.append((nombre, self.curpat + '\n'))
                self['list'].setList(lista)
                self['list'].moveToIndex(len(lista) - 1)
                self.cambiado = True

    def borrar(self):
        lista = self['list'].list
        length = len(lista)
        if length > 0:
            idx = self['list'].getSelectionIndex()
            if idx >= protegidos:
                dei = self.session.openWithCallback(self.callbackborrar, MessageBox, _('Delete current bookmark from list?') + '\n' + lista[idx][0], MessageBox.TYPE_YESNO)
                dei.setTitle(_('MediaCenter'))
            else:
                self.session.open(MessageBox, _('Protected element, unable to delete'), MessageBox.TYPE_INFO, timeout=5)

    def callbackborrar(self, answer):
        if answer is True:
            lista = self['list'].list
            idx = self['list'].getSelectionIndex()
            self.cambiado = True
            del lista[idx]
            del self.lista[idx]
            self['list'].setList(lista)

    def cerrar(self):
        if self.cambiado:
            listaret = self.lista
        else:
            listaret = None
        self.close([('None', listaret)])

    def volver(self):
        lalista = self['list'].list
        idx = self['list'].getSelectionIndex()
        if self.cambiado:
            listaret = self.lista
        else:
            listaret = None
        ruta = str(lalista[idx][0])
        if ruta == '':
            ruta = '$$&$$'
        if ruta == _('root folder'):
            ruta = '/ '
        listaruta = [(ruta, listaret)]
        self.close(listaruta)


from Screens.InputBox import InputBox

class vInputBox(InputBox):
    sknew = '<screen name="vInputBox" position="center,center" size="250,85" title="' + _('Input') + '...">\n'
    sknew = sknew + '<widget name="text" position="5,0" size="200,50" font="Regular;15"/>\n<widget name="input" position="0,40" size="'
    sknew = sknew + '200,30" font="Regular;18"/>\n</screen>'
    skin = sknew

    def __init__(self, session, title = '', windowTitle = _('Input'), useableChars = None, **kwargs):
        InputBox.__init__(self, session, title, windowTitle, useableChars, **kwargs)


config.plugins.mc_vp = ConfigSubsection()
config.plugins.mc_vp.lastDir = ConfigText(default='mountpoint')
config.plugins.mc_vp.orden = ConfigText(default='2')
config.plugins.mc_vp.ordenmi = ConfigText(default='1')

class MC_VideoPlayer(Screen, HelpableScreen):

    def __init__(self, session, ruta_inicio = None):
        Screen.__init__(self, session)
        HelpableScreen.__init__(self)
        limpiamemoria(3, 'mc_init')
        self.oldService = self.session.nav.getCurrentlyPlayingServiceOrGroup()
        self.session.nav.stopService()
        from Tools.HardwareInfo import HardwareInfo
        box = HardwareInfo().get_device_name()
        if not box.startswith('spark'):
            os.system('/usr/bin/showiframe /usr/share/enigma2/black.mvi &')
        self['key_red'] = Button(_('Home'))
        self.iniciadoS = False
        self['barrapix_arr'] = Pixmap()
        self['barrapix_abj'] = Pixmap()
        self['key_blue'] = Button(_('Bookmarks'))
        self['key_0'] = Button(_('PlayList'))
        self['key_pause'] = Button(_('Add to list'))
        self['currentfolder'] = Label('')
        self['currentfavname'] = Label('')
        self.curfavfolder = -1
        self['actions'] = HelpableActionMap(self, 'MC_VideoPlayerActions', {'ok': (self.KeyOk, 'Play selected file'),
         'previous': (self.KeyExit, 'Go parent folder'),
         'cancel': (self.Exit, 'Exit Video Player'),
         'left': (self.leftUp, 'List Top'),
         'right': (self.rightDown, 'List Bottom'),
         'up': (self.up, 'List up'),
         'down': (self.down, 'List down'),
         'menu': (self.showMenu, 'File / Folder Options'),
         'info': (self.showFileInfo, 'Show File Info'),
         'red': (self.Exit, 'Exit Videos'),
         'green': (self.getInetInfo, 'Search Internet Movie Info'),
         'yellow': (self.menuorden, 'Order'),
         'blue': (self.goToBookmark, 'Bookmarks'),
         'home': (self.Exit, 'Exit Videos'),
         'pause': self.selecciona,
         'release': self.SelectionChanged,
         'playlist': self.manageplaylist}, -2)
        if ruta_inicio == None:
            currDir = config.plugins.mc_vp.lastDir.value
        else:
            currDir = ruta_inicio
        if not pathExists(currDir):
            currDir = None
        self['currentfolder'].setText(str(currDir))
        if not os.path.exists('/media/MediaServers'):
            os.system('mkdir -p /media/MediaServers')
        try:
            os.system('modprobe fuse')
            os.system('djmount -o allow_other -o iocharset=utf8 /media/MediaServers')
        except:
            pass

        import time
        time.sleep(5)
        self.filelist = FileList(currDir, showMountpoints=True, useServiceRef=False, showDirectories=True, showFiles=True, matchingPattern='(?i)^.*\\.(ts|vob|mpg|mpeg|avi|mkv|dat|iso|img|mp4|divx|m2ts|wmv|flv|mov)')
        self['filelist'] = self.filelist
        nomorden = ''
        self.iniciado = False
        self['filelist'].tipo = 'video'
        valororden = self['filelist'].getOrden()
        try:
            if valororden == '1':
                nomorden = '(' + _('Name') + ')'
            elif valororden == '2':
                nomorden = '(' + _('Date') + ')'
            elif valororden == '3':
                nomorden = '(' + _('Size') + ')'
        except:
            pass

        self['key_yellow'] = Button(_('Sort') + nomorden)
        self['key_green'] = Label(_('Internet info'))
        self['key_info'] = Label(_('File info'))
        self['coverArt'] = Pixmap()
        self['Poster'] = Pixmap()
        self['title'] = Label()
        self['sinopsis'] = Label()
        self['otrainfo'] = Label()
        self.picload = ePicLoad()
        self.picload.PictureData.get().append(self.paintPoster)
        self.picload2 = ePicLoad()
        self.picload2.PictureData.get().append(self.paintPoster2)
        self.view = False
        self.onShow.append(self.relist)
        self.iniciado = False
        self.booklines2 = []
        self.booklines = []
        self.goBook()

    def relist(self):
        if self.view:
            self['filelist'].actualizarVista()
            self.SelectionChanged()
        else:
            self.SelectionChanged()
        self.view = False

    def actualizaScrolls(self):
        openspaSB(objectoself=self, nombrelista='filelist', barra='barrapix', altoitem=64, imagen=True)

    def manageplaylist(self):
        from NO_AZ_utils import MRUAPlayer_playlist
        selini = ''
        if not self.filelist.canDescent():
            nombre = self['filelist'].getFilename()
            if nombre is not None:
                selini = nombre
        self.session.openWithCallback(self.plcb, MRUAPlayer_playlist, self['filelist'].devRlista(), ' ', selini)

    def plcb(self, respuesta):
        self['filelist'].limpiaRlista()
        for iji in respuesta[1]:
            self['filelist'].anadeRlista(iji, actualizar=False)

        self['filelist'].actualizarVista()
        numele = str(len(self['filelist'].devRlista()))
        self['key_0'].setText(_('PlayList') + '(' + numele + ')')

    def selecciona(self):
        self.isDVD = False
        dvdFilelist = []
        dvdDevice = None
        filename = self['filelist'].getFilename()
        if filename is not None:
            if filename.upper().endswith('VIDEO_TS/\t'):
                pathname = filename[0:-9]
                dvdFilelist.append(str(pathname))
                self.isDVD = True
            if filename.lower().endswith('iso'):
                dvdFilelist.append(str(filename))
                self.isDVD = True
            if filename.lower().endswith('img'):
                dvdFilelist.append(str(filename))
                self.isDVD = True
        if not self.filelist.canDescent() and not self.isDVD:
            nombre = self['filelist'].getFilename()
            if nombre in self['filelist'].devRlista():
                self['filelist'].borraRlista(nombre)
            else:
                self['filelist'].anadeRlista(nombre)
            numele = str(len(self['filelist'].devRlista()))
            self['key_0'].setText(_('PlayList') + '(' + numele + ')')

    def sortName(self):
        self['key_yellow'].setText(_('Sort') + '(' + _('Name') + ')')
        list = self['filelist'].sortName()

    def sortDate(self):
        self['key_yellow'].setText(_('Sort') + '(' + _('Date') + ')')
        list = self['filelist'].sortDate()

    def sortSize(self):
        self['key_yellow'].setText(_('Sort') + '(' + _('Size') + ')')
        list = self['filelist'].sortSize()

    def menuorden(self):
        norden = self['filelist'].getOrden()
        actorden = ''
        n1 = n2 = n3 = ''
        if norden == '1':
            actorden = '' + _('Name') + ''
            n1 = _('(V)')
        elif norden == '2':
            actorden = '' + _('Date') + ''
            n2 = _('(V)')
        elif norden == '3':
            actorden = '' + _('Size') + ''
            n3 = _('(V)')
        contextFileList = [(_('Sort by name') + n1, 'SORTNAME'), (_('Sort by date') + n2, 'SORTDATE'), (_('Sort by size') + n3, 'SORTSIZE')]
        dei = self.session.openWithCallback(self.SysExecution, ChoiceBox, title=_('Sort by') + ' [' + _('Orded by') + ' ' + _(actorden) + ']:', list=contextFileList)
        dei.setTitle(_('MediaCenter'))

    def SysExecution(self, answer):
        answer = answer and answer[1]
        if answer == 'SORTNAME':
            self['filelist'].setOrden('1')
            list = self.sortName()
        elif answer == 'SORTDATE':
            self['filelist'].setOrden('2')
            list = self.sortDate()
        elif answer == 'SORTSIZE':
            self['filelist'].setOrden('3')
            list = self.sortSize()

    def goToBookmark(self, inicio = 'si'):
        bml = [('<' + _('List of Storage Devices') + '>', '$$&$$')]
        try:
            bml.append(('[' + _('Records') + ']', config.usage.default_path.value + ' '))
        except:
            pass

        for onemark in self.booklines2:
            ervalor = onemark.split('#')[-1]
            ertexto = '[' + ''.join(onemark.split('#')[:-1]) + '] ->' + ervalor
            if ertexto == None:
                ertexto = onemark
            if ertexto == '':
                ertexto = onemark
            if ervalor == None:
                ertexto = onemark
            if ervalor == '':
                ertexto = onemark
            bml.append((_(ertexto), ervalor))

        if inicio == 'si':
            patcor = self['filelist'].getCurrentDirectory()
        else:
            patcor = inicio
        dei = self.session.openWithCallback(self.setBookmark, mc_azFavoritos, list=bml, curpat=patcor)

    def goBook(self):
        if fileExists('/etc/azBookmarks_mc'):
            try:
                booklist = open('/etc/azBookmarks_mc', 'r')
            except:
                dei = self.session.open(MessageBox, _('Error by reading bookmarks !!!'), MessageBox.TYPE_ERROR)
                dei.setTitle(_('MediaCenter'))

            if booklist is not None:
                for oneline in booklist:
                    self.booklines.append(oneline.split('#')[-1])
                    self.booklines2.append(oneline)

                booklist.close()
        else:
            oneline = _('Hard disk') + '#' + '/hdd/\n'
            self.booklines.append(oneline.split('#')[-1])
            self.booklines2.append(oneline)
            if pathExists('/hdd/movie/'):
                oneline = _('Movies') + '#' + '/hdd/movie/\n'
                self.booklines.append(oneline.split('#')[-1])
                self.booklines2.append(oneline)
            if pathExists('/hdd/music/'):
                oneline = _('Music') + '#' + '/hdd/music/\n'
                self.booklines.append(oneline.split('#')[-1])
                self.booklines2.append(oneline)
            if pathExists('/hdd/picture/'):
                oneline = _('Picture') + '#' + '/hdd/picture/\n'
                self.booklines.append(oneline.split('#')[-1])
                self.booklines2.append(oneline)

    def setBookmark(self, answer):
        if not answer[0][1] == None:
            try:
                newbooklist = open('/etc/azBookmarks_mc', 'w')
            except:
                dei = self.session.open(MessageBox, _('Error by writing bookmarks !!!'), MessageBox.TYPE_ERROR)
                dei.setTitle(_('MediaCenter'))

            if newbooklist is not None:
                self.booklines2 = []
                self.booklines = []
                conta = 0
                for ele in answer[0][1]:
                    if conta >= protegidos:
                        laruta = ele[1][:-1]
                        elnombre = ele[0]
                        nuevonombre = '' + ''.join(elnombre.split('->')[:-1]) + ''
                        if len(nuevonombre) <= 0:
                            nuevonombre = elnombre
                        if nuevonombre[0] == '[':
                            nuevonombre = nuevonombre.replace('[', '').replace(']', '')
                        self.booklines2.append(str(nuevonombre.strip()) + '#' + str(laruta.strip()) + '\n')
                        self.booklines.append(str(laruta.strip()) + '\n')
                    conta = conta + 1

                for one_line in self.booklines2:
                    newbooklist.write(one_line)

                newbooklist.close()
        if not answer[0][0] == 'None':
            try:
                if answer[0][0][0] == '/':
                    self['filelist'].changeDir(answer[0][0][:-1])
                if answer[0][0] == '$$&$$':
                    self['filelist'].changeDir(None)
            except:
                pass

    def up(self):
        self['filelist'].up()

    def down(self):
        self['filelist'].down()

    def leftUp(self):
        self['filelist'].pageUp()
        self.SelectionChanged()

    def rightDown(self):
        self['filelist'].pageDown()
        self.SelectionChanged()

    def showFileInfo(self):
        if self['filelist'].canDescent():
            return
        from AZ_MRUAvideoinfo import VideoInfoMain
        VideoInfoMain(self.session, reference=self['filelist'].getFilename(), folder=None, file=None, fullScreen=True)

    def KeyExit(self):
        self.filelist.gotoParent()

    def KeyOk(self):
        self.isDVD = False
        self.isIso = False
        self.isFile = False
        self.pathname = ''
        dvdFilelist = []
        filename = self['filelist'].getFilename()
        if filename is not None:
            if filename.lower().endswith('iso') or filename.lower().endswith('img'):
                if ismrua:
                    os.system('mkdir /tmp/discmount')
                    os.system('umount -f /tmp/discmount')
                    os.system('losetup -d /dev/loop0')
                    os.system('losetup /dev/loop0 "' + str(filename) + '"')
                    os.system('mount -t udf /dev/loop0 /tmp/discmount')
                    self.pathname = '/tmp/discmount/'
                    self.isIso = True
                else:
                    if filename.upper().endswith('VIDEO_TS/\t'):
                        self.pathname = filename[0:-9]
                        self.isDVD = True
                    if filename.lower().endswith('iso'):
                        dvdFilelist.append(str(filename))
                        self.isIso = True
                    if filename.lower().endswith('img'):
                        dvdFilelist.append(str(filename))
                        self.isIso = True
            elif self.filelist.canDescent():
                self.filelist.descent()
                self['filelist'].refresh()
                self.SelectionChanged()
                self.actualizaScrolls()
                self.pathname = self['filelist'].getCurrentDirectory() or ''
            else:
                self.isFile = True
        elif self.filelist.canDescent():
            self.filelist.descent()
            self['filelist'].refresh()
            self.SelectionChanged()
            self.actualizaScrolls()
        if self.pathname != '':
            dvdDevice = None
            if fileExists(self.pathname + 'VIDEO_TS.IFO'):
                dvdFilelist.append(str(self.pathname[0:-1]))
                self.isDVD = True
            elif fileExists(self.pathname + 'VIDEO_TS/VIDEO_TS.IFO'):
                dvdFilelist.append(str(self.pathname + 'VIDEO_TS'))
                self.isDVD = True
            elif self.isIso and ismrua:
                self['filelist'].setIsoDir(filename, self['filelist'].getCurrentDirectory())
                self.JumpToFolder('/tmp/discmount/')
                self['filelist'].up()
        if self.isIso:
            if ismrua:
                from AZ_DVDPlayer import AZDVDPlayer
                self.session.open(AZDVDPlayer, dvd_device=dvdDevice, dvd_filelist=dvdFilelist)
            else:
                from Screens import DVD
                self.session.open(DVD.DVDPlayer, dvd_filelist=dvdFilelist)
        elif self.isDVD:
            self.filelist.gotoParent()
            if ismrua:
                from AZ_DVDPlayer import AZDVDPlayer
                self.session.open(AZDVDPlayer, dvd_device=dvdDevice, dvd_filelist=dvdFilelist)
            else:
                print 'Play dvd normal'
                from Screens import DVD
                self.session.open(DVD.DVDPlayer, dvd_device=dvdDevice, dvd_filelist=dvdFilelist)
        elif self.isFile:
            self.view = True
            path = self['filelist'].getCurrentDirectory()
            listatemp = self['filelist'].devRlista()
            if len(listatemp) > 0:
                mesn = _('Do you want to play selected files') + '(' + str(len(listatemp)) + ')?'
                mesn = mesn + '\n' + _('If you chose NO only current file is played')
                self.session.openWithCallback(self.playlista, MessageBox, mesn)
            elif ismrua:
                from AZ_MRUAPlayer import MRUAPlayer
                self.session.open(MRUAPlayer, ref=self['filelist'].getFilename())
            else:
                self.playMoviePlayer()

    def JumpToFolder(self, jumpto = None):
        if jumpto is None:
            return
        self['filelist'].changeDir(jumpto)
        self['currentfolder'].setText('%s' % jumpto)

    def playMoviePlayer(self, lisa = False):
        if lisa:
            self.session.open(MoviePlayerMc, service=None, lastservice=self.oldService, Listado=self['filelist'].devRlista(), ref=None)
        else:
            filename = self['filelist'].getFilename()
            self.session.open(MoviePlayerMc, service=None, lastservice=self.oldService, Listado=[], ref=filename)

    def playlista(self, confirmed):
        if ismrua:
            from AZ_MRUAPlayer import MRUAPlayer
            if confirmed:
                self.session.open(MRUAPlayer, ref=None, Listado=self['filelist'].devRlista())
            else:
                self.session.open(MRUAPlayer, ref=self['filelist'].getFilename())
        elif confirmed:
            self.playMoviePlayer(True)
        else:
            self.playMoviePlayer()

    def JumpToFolder(self, jumpto = None):
        if jumpto is None:
            return
        self['filelist'].changeDir(jumpto)
        self['currentfolder'].setText('%s' % jumpto)

    def KeySettings(self):
        self.session.open(VideoPlayerSettings)

    def Exit(self):
        try:
            config.plugins.mc_vp.lastDir.value = self.filelist.getCurrentDirectory()
        except:
            config.plugins.mc_vp.lastDir.value = 'mountpoint'

        self.session.nav.playService(self.oldService)
        config.plugins.mc_vp.save()
        configfile.save()
        try:
            os.system('fusermount -u /media/MediaServers')
            os.system('modprobe -r fuse')
            os.system('rm -r /media/MediaServers')
        except:
            pass

        limpiamemoria(3, 'mc_close')
        self.close()

    def showMenu(self):
        menu = []
        nkeys = []
        if self.filelist.canDescent():
            x = self.filelist.getName()
            if x == ' ..' or x == '..':
                pass
            else:
                menu.append((_('delete directory') + ': [' + x + ']', 'deletedir'))
                nkeys.append('1')
                menu.append(('--------------------------------------------------------------------------------------------------------------------------------------------------------------------------', 'separator'))
                nkeys.append('')
        else:
            x = self.filelist.getName()
            menu.append((_('delete file') + ': [' + x + ']', 'deletefile'))
            nkeys.append('1')
            menu.append(('--------------------------------------------------------------------------------------------------------------------------------------------------------------------------', 'separator'))
            nkeys.append('')
        norden = self['filelist'].getOrden()
        actorden = ''
        n1 = n2 = n3 = ''
        if norden == '1':
            actorden = '' + _('Name') + ''
            n1 = _('(V)')
        elif norden == '2':
            actorden = '' + _('Date') + ''
            n2 = _('(V)')
        elif norden == '3':
            actorden = '' + _('Size') + ''
            n3 = _('(V)')
        menu.append((_('Sort by name') + n1, 'SORTNAME'))
        menu.append((_('Sort by date') + n2, 'SORTDATE'))
        menu.append((_('Sort by size') + n3, 'SORTSIZE'))
        nkeys.append('red')
        nkeys.append('green')
        nkeys.append('yellow')
        menu.append(('--------------------------------------------------------------------------------------------------------------------------------------------------------------------------', 'separator'))
        nkeys.append('')
        numele = len(self['filelist'].devRlista())
        menu.append((_('Show Playlist') + '(' + str(numele) + ')', 'playlist'))
        nkeys.append('0')
        menu.append((_('Add to playlist all files in folder'), 'all'))
        nkeys.append('2')
        if numele > 0:
            menu.append((_('Clear playlist'), 'clear'))
            nkeys.append('3')
        self.session.openWithCallback(self.menuCallback, ChoiceBox, keys=nkeys, title='', list=menu)

    def menuCallback(self, choice):
        if choice is None:
            return
        if choice[1] == 'deletedir':
            self.deleteDir()
        elif choice[1] == 'deletefile':
            self.deleteFile()
        elif choice[1] == 'SORTNAME':
            self['filelist'].setOrden('1')
            list = self.sortName()
        elif choice[1] == 'SORTDATE':
            self['filelist'].setOrden('2')
            list = self.sortDate()
        elif choice[1] == 'SORTSIZE':
            self['filelist'].setOrden('3')
            list = self.sortSize()
        elif choice[1] == 'playlist':
            self.manageplaylist()
        elif choice[1] == 'clear':
            self.clearPlaylistMenu()
        elif choice[1] == 'all':
            self['filelist'].changeDir(self['filelist'].current_directory, seleccionar=True)
            numele = str(len(self['filelist'].devRlista()))
            self['key_0'].setText(_('PlayList') + '(' + numele + ')')

    def clearPlaylistMenu(self):
        self.session.openWithCallback(self.cbclearPlaylistMenu, MessageBox, _('Do you want to clear playlist?'))

    def cbclearPlaylistMenu(self, respuesta):
        if respuesta:
            self['filelist'].limpiaRlista()
            self['filelist'].refresh()
            self['key_0'].setText(_('PlayList') + '(0)')

    def deleteDir(self):
        self.session.openWithCallback(self.deleteDirConfirmed, MessageBox, _("Do you really want to delete this directory and it's content ?"))

    def deleteDirConfirmed(self, confirmed):
        if confirmed:
            import shutil
            deldir = self.filelist.getSelection()[0]
            shutil.rmtree(deldir)
            self['filelist'].refresh()

    def deleteFile(self):
        self.session.openWithCallback(self.deleteFileConfirmed, MessageBox, _('Do you really want to delete this file ?'))

    def deleteFileConfirmed(self, confirmed):
        if confirmed:
            delfile = self['filelist'].getFilename()
            try:
                os.remove(delfile)
            except:
                self.session.open(scrInformation, texto=_('Can not delete file'))
                return

            try:
                os.remove(delfile + '.spztxt')
            except:
                pass

            try:
                os.remove(delfile + '.jpg')
            except:
                pass

            try:
                os.remove(delfile + '.cuts')
            except:
                pass

            try:
                os.remove(delfile + '.cutsr')
            except:
                pass

            try:
                os.remove(delfile + '.meta')
            except:
                pass

            try:
                os.remove(delfile.replace('.ts', '.eit'))
            except:
                pass

            try:
                os.remove(delfile + '.ap')
            except:
                pass

            try:
                os.remove(delfile + '.sc')
            except:
                pass

            try:
                os.remove(delfile + '.rsp')
            except:
                pass

            self['filelist'].refresh()

    def ReturnDVD(self):
        import time
        time.sleep(2)

    def getInetInfo(self):
        if fileExists('/usr/lib/enigma2/python/Plugins/Extensions/spzIMDB/plugin.pyo'):
            if self['filelist'].canDescent():
                pass
            else:
                ruta = self['filelist'].getFilename()
                try:
                    foldername = ruta.rpartition('/')
                    archivo = foldername[2]
                except:
                    pass

                try:
                    ernombre = ernombre.decode('utf-8').encode('utf-8')
                except:
                    try:
                        ernombre = ernombre.decode('windows-1252').encode('utf-8')
                    except:
                        pass

                ernombre = limpianombre(archivo)
                self.getInetInfoCallBack(ernombre, ruta)

    def getInetInfoCallBack(self, ernombre, archivo):
        if ernombre == '' or ernombre == None:
            return
        try:
            from Plugins.Extensions.spzIMDB.plugin import spzIMDB
            spzIMDB(self.session, tbusqueda=ernombre, truta=archivo + '.spztxt')
        except:
            pass

    def SelectionChanged(self):
        if not self.iniciadoS:
            self.actualizaScrolls()
            self.iniciadoS = True
        titulo = ''
        if self.iniciado:
            sinopsis = ''
        else:
            self.iniciado = True
            sinopsis = '\n(' + _('Use the Play/Pause button [>/||] for select files and press [OK] for play selected files. Press [0] for view PlayList and [MENU] for more options') + ')'
        otrainfo = ''
        movielen = 0
        adebug = ''
        if self['filelist'].canDescent():
            self['key_green'].hide()
            self['key_info'].hide()
            self['key_pause'].hide()
            jfilename = '/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/images/no_poster_vp.jpg'
            pfilename = '/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/skins/default/images/videobg2.jpg'
            path = self['filelist'].getCurrentDirectory()
            titulo = path or ''
        else:
            self['key_green'].show()
            self['key_info'].show()
            self['key_pause'].show()
            if self['filelist'].getFilename() in self['filelist'].devRlista():
                self['key_pause'].setText(_('Delete from list'))
            else:
                self['key_pause'].setText(_('Add to list'))
            ruta = self['filelist'].getFilename()
            try:
                foldername = ruta.rpartition('/')
                try:
                    titulo = foldername[2].decode('utf-8').encode('utf-8')
                except:
                    try:
                        titulo = foldername[2].decode('windows-1252').encode('utf-8')
                    except:
                        pass

            except:
                pass

            jfilename = None
            pfilename = None
            filename = self['filelist'].getFilename()
            if fileExists(str(filename) + '.png'):
                jfilename = str(filename) + '.png'
            elif fileExists(str(filename) + '.gif'):
                jfilename = str(filename) + '.gif'
            elif fileExists(str(filename) + '.jpg'):
                jfilename = str(filename) + '.jpg'
            elif fileExists('/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/images/no_poster_vp.jpg'):
                jfilename = '/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/images/no_poster_vp.jpg'
            if fileExists(str(filename) + '.jpeg'):
                pfilename = str(filename) + '.jpeg'
            elif fileExists('/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/skins/default/images/videobg2.jpg'):
                pfilename = '/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/skins/default/images/videobg2.jpg'
            if filename.endswith('.ts'):
                serviceref = eServiceReference('1:0:0:0:0:0:0:0:0:0:' + str(filename))
                serviceHandler = eServiceCenter.getInstance()
                info = serviceHandler.info(serviceref)
                movielen = info.getLength(serviceref)
                evt = info.getEvent(serviceref)
                if jfilename == '/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/images/no_poster_vp.jpg':
                    xservice = ServiceReference(info.getInfoString(serviceref, iServiceInformation.sServiceref))
                    cservice = None
                    err = False
                    try:
                        cservice = str(xservice)
                    except:
                        pass

                    if cservice:
                        xfilename = rutapicon(str(cservice))
                        if xfilename:
                            jfilename = xfilename
            if fileExists(str(filename) + '.spztxt'):
                f = open(str(filename) + '.spztxt', 'r')
                tok = 0
                for line in f.readlines():
                    if line.split(':')[0] == 'G\xc3\xa9nero':
                        otrainfo = line
                    if line.split(':')[0] == 'Presupuesto':
                        otrainfo = otrainfo + line
                    idx = line.find('->')
                    if idx != -1:
                        if tok == 0:
                            titulo = line[idx + 3:]
                            tok = 1
                        elif tok == 1:
                            sinopsis = line[idx + 3:]

                f.close()
            elif filename.endswith('.ts'):
                txt = ''
                if info is not None:
                    txt = info.getName(serviceref)
                    if txt is not '' and txt is not None:
                        titulo = txt
                text = ''
                if evt:
                    if evt != None:
                        text = evt.getEventName()
                        short = evt.getShortDescription()
                        ext = evt.getExtendedDescription()
                        if short and short != text:
                            text = short
                        else:
                            text = ''
                        if ext:
                            if text:
                                text += '::'
                            text += ext
                        sinopsis = ''
                        titulo = evt.getEventName()
                        sinopsis = sinopsis + _('Recording Date') + ': ' + evt.getBeginTimeString() + ', '
                        sinopsis = sinopsis + _('Duration') + ': %d:%02d ' % (movielen / 60, movielen % 60) + '::'
                        sinopsis = sinopsis + text
            titulo = titulo.upper()
            maxlon = 500
            if len(sinopsis) > maxlon:
                sinopsis = sinopsis[0:maxlon]
                while sinopsis[-1:] != ' ':
                    sinopsis = sinopsis[0:-1]

                sinopsis = sinopsis + '...(' + _('Press [INFO] for more') + ')'
        if jfilename != None:
            sc = AVSwitch().getFramebufferScale()
            self.picload.setPara((self['coverArt'].instance.size().width(),
             self['coverArt'].instance.size().height(),
             sc[0],
             sc[1],
             0,
             1,
             '#00000000'))
            self.picload.startDecode(jfilename)
        if pfilename != None:
            sd = AVSwitch().getFramebufferScale()
            self.picload2.setPara((self['Poster'].instance.size().width(),
             self['Poster'].instance.size().height(),
             sd[0],
             sd[1],
             0,
             1,
             '#00000000'))
            self.picload2.startDecode(pfilename)
        self['title'].setText(titulo)
        self['sinopsis'].setText(adebug + sinopsis)
        self['otrainfo'].setText(otrainfo)

    def paintPoster(self, picInfo = None):
        ptr = self.picload.getData()
        if ptr != None:
            self['coverArt'].instance.setPixmap(ptr.__deref__())
            self['coverArt'].show()

    def paintPoster2(self, picInfo = None):
        ptr2 = self.picload2.getData()
        if ptr2 != None:
            self['Poster'].instance.setPixmap(ptr2.__deref__())
            self['Poster'].show()


class MC_VideoInfoView(Screen):
    skin = '\n\t\t<screen position="80,130" size="560,320" title="View Video Info" >\n\t\t\t<widget name="infolist" position="5,5" size="550,310" selectionDisabled="1" />\n\t\t</screen>'

    def __init__(self, session, fullname, name, ref):
        self.skin = MC_VideoInfoView.skin
        Screen.__init__(self, session)
        self['actions'] = ActionMap(['OkCancelActions'], {'cancel': self.close,
         'ok': self.close}, -1)
        tlist = []
        self['infolist'] = ServiceInfoList(tlist)
        currPlay = self.session.nav.getCurrentService()
        if currPlay is not None:
            stitle = currPlay.info().getInfoString(iServiceInformation.sTitle)
            if stitle == '':
                stitle = currPlay.info().getName().split('/')[-1]
            tlist.append(ServiceInfoListEntry('Title: ', stitle))
            tlist.append(ServiceInfoListEntry('sNamespace: ', currPlay.info().getInfoString(iServiceInformation.sNamespace)))
            tlist.append(ServiceInfoListEntry('sProvider: ', currPlay.info().getInfoString(iServiceInformation.sProvider)))
            tlist.append(ServiceInfoListEntry('sTimeCreate: ', currPlay.info().getInfoString(iServiceInformation.sTimeCreate)))
            tlist.append(ServiceInfoListEntry('sVideoWidth: ', currPlay.info().getInfoString(iServiceInformation.sVideoWidth)))
            tlist.append(ServiceInfoListEntry('sVideoHeight: ', currPlay.info().getInfoString(iServiceInformation.sVideoHeight)))
            tlist.append(ServiceInfoListEntry('sDescription: ', currPlay.info().getInfoString(iServiceInformation.sDescription)))


from Screens.InfoBar import MoviePlayer

class MoviePlayerMc(MoviePlayer):
    ENABLE_RESUME_SUPPORT = False

    def __init__(self, session, service, lastservice = None, Listado = [], ref = None):
        self.session = session
        self.WithoutStopClose = False
        self.tvservice = lastservice
        self.listado = Listado
        self.contador = 0
        self.repetir = False
        self.mpservice = service
        service = None
        self.ref = ref
        MoviePlayer.__init__(self, self.session, service)
        self.skinName = ['MoviePlayer']
        self.__event_tracker = ServiceEventTracker(screen=self, eventmap={iPlayableService.evStart: self.__serviceStarted})
        self['actions'] = ActionMap(['MoviePlayerActions',
         'MenuActions',
         'OkCancelActions',
         'NumberActions',
         'EPGSelectActions'], {'cancel': self.leavePlayer,
         'exit': self.leavePlayer,
         'leavePlayer': self.leavePlayer,
         'menu': self.menu,
         'nextBouquet': self.siguienteLista,
         'prevBouquet': self.anteriorLista,
         'nextService': self.siguienteLista,
         'prevService': self.anteriorLista,
         'ok': self.toggleShow,
         '0': self.menupip}, -3)
        self.Start()

    def siguienteLista(self):
        if len(self.listado) > 0:
            self.doEofInternal(False)

    def anteriorLista(self):
        if len(self.listado) > 0:
            if self.contador >= 1:
                self.contador = self.contador - 2
                self.doEofInternal(False)

    def menupip(self, nnum = 0):
        if SystemInfo.get('NumVideoDecoders', 1) > 1:
            if not self.session.pipshown:
                self.showPiP()
            else:
                from Plugins.Extensions.spazeMenu.spzPlugins.spzPiPMenu.plugin import pipmenu
                pipmenu(self.session, nomenu=False, limitar=True)

    def reinicia(self):
        try:
            mostrarNotificacion(id='az_mruaplayer', texto=_('Repeating title...'), segundos=4)
            self.session.nav.stopService()
            self.session.nav.playService(None)
            self.mpservice = None
            self.ENABLE_RESUME_SUPPORT = False
            self.repetir = True
            self.Start()
        except:
            self.exit()

    def __serviceStarted(self):
        service = self.session.nav.getCurrentService()
        seekable = service.seek()
        ref = self.session.nav.getCurrentlyPlayingServiceReference()
        perc, last, length = getResumePoint(ref)
        if last is None:
            return
        if seekable is None:
            return
        length = seekable.getLength() or (None, 0)
        print 'seekable.getLength() returns:', length
        if last > 900000 and (not length[1] or last < length[1] - 900000):
            self.resume_point = last
            l = last / 90000
            if 'ask' in config.usage.on_movie_start.value or not length[1]:
                Notifications.AddNotificationWithCallback(self.playLastCB, MessageBox, _('Do you want to resume this playback?') + '\n' + _('Resume position at %s') % ('%d:%02d:%02d' % (l / 3600, l % 3600 / 60, l % 60)), timeout=10, default='yes' in config.usage.on_movie_start.value)
            elif config.usage.on_movie_start.value == 'resume':
                Notifications.AddNotificationWithCallback(self.playLastCB, MessageBox, _('Resuming playback'), timeout=2, type=MessageBox.TYPE_INFO)

    def doEofInternal(self, playing):
        ref = self.session.nav.getCurrentlyPlayingServiceOrGroup()
        if ref:
            setResumePoint(self.session, True)
        if len(self.listado) > 0:
            self.contador = self.contador + 1
            if self.contador >= len(self.listado):
                self.contador = 0
            elif not fileExists(self.listado[self.contador]):
                Notifications.AddPopup(text=_('Verify playlist. Press [MENU]') + '\n' + _('File not exists!') + ':\n' + self.listado[self.contador], type=MessageBox.TYPE_ERROR, timeout=8, id='azmruaplayer')
                return
            else:
                try:
                    mostrarNotificacion(id='az_mruaplayer', texto=_('PlayList') + ': ' + str(self.contador + 1) + ' ' + _('of') + ' ' + str(len(self.listado)), segundos=4)
                except:
                    pass

                self.session.nav.stopService()
                self.session.nav.playService(None)
                self.mpservice = None
                self.ENABLE_RESUME_SUPPORT = False
                self.Start()
                return

        if config.plugins.mc_mrua.repeat.value:
            self.reinicia()
        else:
            self.is_closing = True
            self.close()

    def subtitleSelection(self):
        from Screens.AudioSelection import SubtitleSelection
        self.session.open(SubtitleSelection, self)

    def audioSelection(self):
        from Screens.InfoBar import InfoBar
        if InfoBar and InfoBar.instance:
            InfoBar.audioSelection(InfoBar.instance)

    def brillo(self):
        try:
            from Plugins.SystemPlugins.VideoTune.plugin import videoFinetuneMain
            videoFinetuneMain(self.session)
        except:
            pass

    def avmenu(self):
        try:
            from Screens.VideoMode import VideoSetup
            self.session.open(VideoSetup)
        except:
            pass

    def menu(self):
        self.session.openWithCallback(self.menuCallback, MRUAPlayer_Menu)

    def menuCallback(self, value):
        if value == 0:
            from timeSleepMRU import timesleep as tmsrua
            tmsrua(instance=self)
        elif value == 3:
            self.subtitleSelection()
        elif value == 4:
            self.audioSelection()
        elif value == 5:
            self.movieInfo()
        elif value == 6:
            config.plugins.mc_mrua.repeat.value = not config.plugins.mc_mrua.repeat.value
            config.plugins.mc_mrua.repeat.save()
            if config.plugins.mc_mrua.repeat.value:
                textoinfo = _('Repeat mode ACTIVATED')
            else:
                textoinfo = _('Repeat mode DEACTIVATED')
            self.session.open(scrInformation, texto=textoinfo, segundos=2, mostrarSegundos=False)
        elif value == 7:
            selini = ''
            if len(self.listado) > 0 and self.contador < len(self.listado):
                selini = self.listado[self.contador]
            self.session.openWithCallback(self.plcb, MRUAPlayer_playlist, self.listado, 'Select file for play', selini)
        elif value == 2:
            self.avmenu()
        elif value == 1:
            self.brillo()

    def plcb(self, resp):
        if resp:
            num = resp[0]
            self.listado = []
            for iji in resp[1]:
                self.listado.append(iji)

            if num == None or len(self.listado) == 0:
                return
            if not fileExists(self.listado[num]):
                Notifications.AddPopup(text=_('Verify playlist. Press [MENU]') + '\n' + _('File not exists!') + ':\n' + self.listado[num], type=MessageBox.TYPE_ERROR, timeout=8, id='azmruaplayer')
                return
            self.contador = num
            try:
                mostrarNotificacion(id='az_mruaplayer', texto=_('PlayList') + ': ' + str(self.contador + 1) + ' ' + _('of') + ' ' + str(len(self.listado)), segundos=4)
            except:
                pass

            self.session.nav.stopService()
            self.session.nav.playService(None)
            self.mpservice = None
            self.ENABLE_RESUME_SUPPORT = False
            self.Start()

    def movieInfo(self):
        from AZ_MRUAvideoinfo import VideoInfoMain
        VideoInfoMain(self.session, reference=self.ref)

    def devEref(self, cref):
        filename = cref
        testFileName = cref.lower()
        if testFileName != None:
            fileRef = None
            if testFileName.endswith('.ts'):
                fileRef = eServiceReference(1, 0, filename)
            elif testFileName.endswith('.mpg') or testFileName.endswith('.mpeg') or testFileName.endswith('.mkv') or testFileName.endswith('.m2ts') or testFileName.endswith('.vob'):
                fileRef = eServiceReference(4097, 0, filename)
            elif testFileName.endswith('.avi') or testFileName.endswith('.mp4') or testFileName.endswith('.divx') or testFileName.endswith('.mov') or testFileName.endswith('.flv'):
                fileRef = eServiceReference(4097, 0, filename)
            return fileRef

    def Start(self):
        if len(self.listado) > 0:
            self.ref = self.listado[self.contador]
            if not fileExists(self.ref):
                Notifications.AddPopup(text=_('Verify playlist. Press [MENU]') + '\n' + _('File not exists!') + ':\n' + self.listado[self.contador], type=MessageBox.TYPE_ERROR, timeout=8, id='azmruaplayer')
                return
        if self.ref is None:
            self.exit()
        else:
            newref = self.devEref(self.ref)
            try:
                self.cur_service = newref
            except:
                pass

            self.session.nav.playService(newref)
            self.mpservice = self.session.nav.getCurrentService()

    def showPiP(self):
        if self.session.pipshown:
            del self.session.pip
            self.session.pipshown = False
        elif self.tvservice:
            from Screens.PictureInPicture import PictureInPicture
            self.session.pip = self.session.instantiateDialog(PictureInPicture)
            self.session.pip.show()
            self.session.pipshown = True
            self.session.pip.playService(self.tvservice)

    def swapPiP(self):
        pass

    def leavePlayer(self):
        laref = _('Stop play and exit to list movie?')
        try:
            dei = self.session.openWithCallback(self.callbackexit, MessageBox, laref, MessageBox.TYPE_YESNO)
            dei.setTitle(_('Stop play'))
        except:
            self.callbackexit(True)

    def callbackexit(self, respuesta):
        if respuesta:
            self.is_closing = True
            setResumePoint(self.session)
            self.close()

    def leavePlayerConfirmed(self, answer):
        pass

    def exit(self):
        self.callbackexit(True)

    def showMovies(self):
        pass

    def movieSelected(self, service):
        self.leavePlayer(self.de_instance)

    def __onClose(self):
        if not self.WithoutStopClose:
            self.session.nav.playService(self.lastservice)
