from enigma import *
from Components.Label import Label
from Components.MenuList import MenuList
from Screens.ChannelSelection import SimpleChannelSelection
from Components.MultiContent import MultiContentEntryText
from enigma import eListboxPythonMultiContent, eServiceCenter, gFont
from enigma import eTimer, eConsoleAppContainer
from ServiceReference import ServiceReference
from Screens.InfoBarGenerics import *
from Components.Pixmap import Pixmap, MovingPixmap
from Tools.LoadPixmap import LoadPixmap
import calendar, keymapparser
from keyids import KEYIDS
from Plugins.Plugin import PluginDescriptor
from Tools.KeyBindings import addKeyBinding
from Screens.Screen import Screen
from Components.ConfigList import ConfigListScreen
from Screens.MessageBox import MessageBox
from Screens.Console import Console
from Screens import Standby
from Screens.InfoBarGenerics import InfoBarPlugins
from Screens.Standby import TryQuitMainloop
from Components.ActionMap import ActionMap
from Components.Button import Button
from Components.ScrollLabel import ScrollLabel
from Components.config import getConfigListEntry, ConfigEnableDisable, ConfigYesNo, ConfigText, ConfigClock, ConfigNumber, ConfigSelection, config, ConfigSubsection, ConfigSubList, ConfigSubDict, ConfigDirectory
from Tools import Notifications
from Tools.HardwareInfo import HardwareInfo
import os
import string
from os import popen as os_popen
from time import localtime, asctime, time, gmtime
from Tools.Directories import fileExists, resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE, SCOPE_SKIN
from Components.Language import language
import urllib2
from os import environ
import os
import gettext
import sys
lang = language.getLanguage()
environ['LANGUAGE'] = lang[:2]
gettext.bindtextdomain('enigma2', resolveFilename(SCOPE_LANGUAGE))
gettext.textdomain('enigma2')
gettext.bindtextdomain('spzCAMD', '%s%s' % (resolveFilename(SCOPE_PLUGINS), 'Extensions/spazeMenu/spzPlugins/spzCAMD/locale/'))
TimerGoUpdates = None
TimerMirar = None

def _(txt):
    t = gettext.dgettext('spzCAMD', txt)
    if t == txt:
        t = gettext.gettext(txt)
    return t


def cargaosinfo(orden, nulo = False):
    ret = ''
    os.system(orden + ' >/tmp/tempinfo')
    booklist = None
    if fileExists('/tmp/tempinfo'):
        try:
            booklist = open('/tmp/tempinfo', 'r')
        except:
            pass

        if booklist is not None:
            for oneline in booklist:
                ret = ret + oneline

            booklist.close()
        os.system('rm /tmp/tempinfo')
    if len(ret) <= 1:
        if nulo == True:
            ret = ''
        else:
            ret = _('Error 501')
    return ret


filetmp = None
tamanotemp = None
nombretmp = ''
progresotemp = 0
bloquetemp = 0
globalsession = None

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


def grabarfichero(block):
    global filetmp
    try:
        filetmp.write(block)
    except:
        pass


def gfic(block):
    try:
        filetmp.write(block)
    except:
        pass


def devhtml(url, usuario = '', pwd = '', pcarpeta = None):
    import ftplib
    ret = None
    try:
        ftp = ftplib.FTP(url, timeout=5)
        ftp.login(usuario, pwd)
    except:
        return

    try:
        lista = []
        ret = ''
        ftp.retrlines('RETR ' + pcarpeta, lista.append)
        for jj in lista:
            ret = ret + jj + '\n'

        ret = ret + '----------------------------------x----------------------------------'
    except:
        ret = None

    return ret


def devhtmlNO(url, usuario = '', pwd = '', pcarpeta = None):
    global filetmp
    import ftplib
    ret = None
    try:
        ftp = ftplib.FTP(url, timeout=5)
        ftp.login(usuario, pwd)
    except:
        return

    progresotemp = 0
    nombretmp = '/tmp/tmpdwnd'
    filetmp = open(nombretmp, 'wb')
    try:
        ftp.retrbinary('RETR ' + pcarpeta, gfic)
    except:
        filetmp.close()
        os.system('rm ' + nombretmp)
        return

    filetmp.close()
    ftp.close()
    cdes = None
    booklist = None
    if fileExists(nombretmp):
        try:
            booklist = open(nombretmp, 'r')
        except:
            pass

        if booklist is not None:
            cdes = ''
            for oneline in booklist:
                cdes = cdes + oneline

            booklist.close()
        os.system('rm ' + nombretmp)
    return cdes


def devFtp(url, usuario = '', pwd = '', pcarpeta = None, archivo = None):
    global tamanotemp
    global filetmp
    global progresotemp
    global nombretmp
    import ftplib
    try:
        ftp = ftplib.FTP(url, timeout=15)
        ftp.login(usuario, pwd)
    except:
        return

    progresotemp = 0
    nombretmp = '/tmp/' + archivo
    filetmp = open(nombretmp, 'wb')
    try:
        tamanotemp = ftp.size(pcarpeta + '/' + archivo)
    except:
        filetmp.close()
        ftp.close()
        return

    try:
        ftp.retrbinary('RETR ' + pcarpeta + '/' + archivo, grabarfichero)
    except:
        filetmp.close()
        return

    filetmp.close()
    ftp.close()
    return True


def devUrlContenido(url, usuario = '', pwd = '', pcarpeta = None, extension = '.ipk', extension2 = '.tar', privado = False):
    import ftplib
    try:
        ftp = ftplib.FTP(url, timeout=15)
        ftp.login(usuario, pwd)
    except:
        ftp = None

    if ftp == None:
        return ftp
    if pcarpeta == None or pcarpeta == '/':
        pcarpeta = ''
    try:
        listaftp = ftp.nlst(pcarpeta)
    except:
        return

    listafin = []
    if not pcarpeta == 'Camds' and not pcarpeta + ' ' == ' ':
        listafin.append(('<' + _('Home') + '>', 'd', False))
        listafin.append(('<' + _('Parent directory') + '>', 'd', False))
    contaarchivos = 0
    contacategorias = 0
    for iji in listaftp:
        tamano = None
        try:
            tamano = ftp.size(iji)
        except:
            pass

        if '.' in iji:
            tamano = 1
        archivo = iji.replace(pcarpeta + '/', '')
        tipo = 'o'
        hayinfo = False
        if not tamano == None:
            if archivo.endswith(extension) or archivo.endswith(extension2):
                tipo = 'a'
                temptxt = archivo.replace(extension, '.txt').replace(extension2, '.txt')
                contaarchivos = contaarchivos + 1
                if temptxt in str(listaftp):
                    hayinfo = True
        elif archivo == 'Privado':
            if privado:
                tipo = 'd'
            else:
                tipo = 'o'
        elif not archivo == '..' and not archivo == '.':
            tipo = 'd'
            contacategorias = contacategorias + 1
        if not tipo == 'o':
            listafin.append((archivo, tipo, hayinfo))

    ftp.close()
    return [contacategorias, contaarchivos, listafin]


carpetaimg = '/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/spzCAMD/images/'
nommodelo = 'NA'

class IniciaSelListCarpeta(MenuList):

    def __init__(self, list, enableWrapAround = False):
        MenuList.__init__(self, list, enableWrapAround, eListboxPythonMultiContent)
        self.l.setItemHeight(50)
        self.l.setFont(0, gFont('Regular', 19))
        self.l.setFont(1, gFont('Regular', 17))


def IniciaSelListEntryCarpeta(texto, imagen = 'cOtros'):
    global carpetaimg
    res = [texto]
    res.append(MultiContentEntryText(pos=(77, 14), size=(1000, 30), font=0, text=texto))
    png = '' + carpetaimg + '' + imagen + '-fs8.png'
    if fileExists(png):
        fpng = LoadPixmap(png)
        res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND,
         27,
         2,
         48,
         48,
         fpng))
    return res


class IniciaSelListArchivo(MenuList):

    def __init__(self, list, enableWrapAround = True):
        MenuList.__init__(self, list, enableWrapAround, eListboxPythonMultiContent)
        self.l.setItemHeight(32)
        self.l.setFont(0, gFont('Regular', 19))
        self.l.setFont(1, gFont('Regular', 17))


def IniciaSelListEntryArchivo(texto, imagen = 'Otros', instalado = False):
    tecla = '' + texto + ''
    res = [tecla]
    res.append(MultiContentEntryText(pos=(34, 1), size=(700, 25), font=0, text=tecla))
    png = '' + carpetaimg + '' + imagen + '-fs8.png'
    if fileExists(png):
        fpng = LoadPixmap(png)
        res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND,
         0,
         0,
         32,
         32,
         fpng))
    return res


class InfoArchivo(Screen):
    skin = '\n\t<screen name="InfoArchivo" position="center,center" size="1000,610" title="%s">\n\n\t<widget name="respuesta" position="8,87" size="970,520"  zPosition="12" text=" " font="Regular; 19" />\n\t<ePixmap name="new ePixmap" position="3,32" size="35,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/spzCAMD/images/info-fs8.png" alphatest="blend" transparent="1" zPosition="10"/>\n\n\t<widget name="modo" position="8,31" size="970,32" backgroundColor="#ffffff" foregroundColor="#000000" text=" " font="Regular; 22" />\n\n\t<widget name="key_red" position="654,585" size="162,22" transparent="1" text="Exit" font="Regular; 16"/>\n\n\t<widget name="key_mode" position="8,8" size="685,22" transparent="1" text=" " font="Regular; 15" halign="left" />\n\t</screen>' % _('Information')

    def __init__(self, session, titulo = None, textoinfo = None):
        self.session = session
        Screen.__init__(self, session)
        self.texto = textoinfo
        self.titulo = titulo
        self['respuesta'] = ScrollLabel(_(''))
        self['modo'] = Label(_(''))
        self['key_mode'] = Label(_(''))
        self['key_red'] = Label(_('Back'))
        self['setupActions'] = ActionMap(['WizardActions',
         'DirectionActions',
         'ColorActions',
         'NumberActions',
         'MenuActions',
         'EPGSelectActions',
         'InfobarActions'], {'green': self.exit,
         'red': self.exit,
         'back': self.exit,
         'left': self.exit,
         'right': self.exit,
         'up': self.key_up,
         'down': self.key_down,
         'info': self.exit,
         'ok': self.exit}, -2)
        self.onLayoutFinish.append(self.cargapregunta)

    def exit(self):
        self.close()

    def cargapregunta(self):
        self['key_red'].setText(_(' '))
        self['modo'].setText('       ' + self.titulo.replace('.tar', '').replace('.ipk', ''))
        self['respuesta'].setText(self.texto)
        self['key_mode'].setText(_('Press any key to go back'))

    def key_up(self):
        self['respuesta'].pageUp()

    def key_down(self):
        self['respuesta'].pageDown()


class descargasSPZ(Screen):
    skin = '\n\t<screen name="descargasSPZ" position="center,center" size="1000,610" title="%s">\n\t<widget name="textoinfo" position="8,60" size="970,520" valign="top" halign="left" text=" " font="Regular; 18" zPosition="2" transparent="1"/>\n\n\t<widget name="listaC" position="8,67" size="970,500" scrollbarMode="showOnDemand" zPosition="12" transparent="1"/>\n\t<widget name="listaA" position="8,67" size="970,512" scrollbarMode="showOnDemand" zPosition="12" transparent="1"/>\n\t<widget name="modo" position="8,31" size="970,30" backgroundColor="#ffffff" foregroundColor="#000000" text=" " font="Regular; 22" />\n\n\t<ePixmap name="new ePixmap" position="0,584" size="35,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/spzCAMD/images/red.png" alphatest="blend" transparent="1" />\n\n\t<widget name="key_red" position="34,585" size="162,22" transparent="1" text="Exit" font="Regular; 16"/>\n\t<widget name="img_des" position="200,584" zPosition="2" size="35,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/spzCAMD/images/info.png" transparent="1" alphatest="blend" />\n\t<widget name="key_des" position="234,585" size="462,22" transparent="1" text=" " font="Regular; 16"/>\n\t<widget name="key_help" position="8,585" backgroundColor="#000000" size="856,22" transparent="1" text=" " font="Regular; 15" halign="left" zPosition="10" />\n\t<widget name="key_mode" position="8,8" size="685,22" transparent="1" text=" " font="Regular; 15" halign="left" />\n\t</screen>' % _('spazeTeam Downloads')

    def __init__(self, session, instance = None, args = 0):
        global TimerMirar
        global TimerGoUpdates
        global globalsession
        self.session = session
        Screen.__init__(self, session)
        globalsession = self
        self.listado = []
        self.instalando = False
        self.TimerTemp = eTimer()
        self.TimerTemp.callback.append(self.instalarok)
        self.TimerPrivado = eTimer()
        self.TimerPrivado.callback.append(self.desactivaprivado)
        self.tiempotimer = 600
        self.nprivado = 0
        self.fin = 0
        try:
            TimerGoUpdates.stop()
        except:
            pass

        try:
            TimerMirar.stop()
        except:
            pass

        self.infomostrado = False
        self.carpeta = 'Camds'
        self.modoarchivo = False
        self.url = 'ftp://spazeteam:ad32fG0s@www.azboxhd.es'
        self.url2 = 'www.azboxhd.es'
        self.usuario = 'spazeteam'
        self.pwd = 'ad32fG0s'
        self.privado = False
        self['listaA'] = IniciaSelListArchivo([])
        self['listaC'] = IniciaSelListCarpeta([])
        self['textoinfo'] = ScrollLabel(_(''))
        self['modo'] = Label(_(''))
        self['key_help'] = Label(_(''))
        self['key_mode'] = Label(_(''))
        self['img_des'] = MovingPixmap()
        self.paso = 0
        self.pinfo = ''
        self.titulo = ''
        self.vacio = False
        self['key_red'] = Label(_('Exit'))
        self['key_blue'] = Label(_('Update log'))
        self['key_des'] = Label(_('Description'))
        self['setupActions'] = ActionMap(['WizardActions',
         'DirectionActions',
         'ColorActions',
         'NumberActions',
         'MenuActions',
         'EPGSelectActions',
         'InfobarActions'], {'red': self.exit,
         'back': self.volver,
         'left': self.key_left,
         'right': self.key_right,
         'up': self.key_up,
         'down': self.key_down,
         'info': self.key_info,
         'ok': self.key_ok}, -2)
        self.onLayoutFinish.append(self.buildList)
        self['listaA'].onSelectionChanged.append(self.muevesel)
        self['listaC'].onSelectionChanged.append(self.muevesel)

    def desactivaprivado(self):
        self.nprivado = 0
        self.TimerPrivado.stop()

    def chkprivado1(self):
        if self.nprivado == 0:
            self.nprivado = 1
        else:
            self.nprivado = 0
        self.TimerPrivado.stop()
        self.TimerPrivado.start(2000, True)

    def chkprivado2(self):
        if self.nprivado == 1:
            self.nprivado = 2
        else:
            self.nprivado = 0
        self.TimerPrivado.stop()
        self.TimerPrivado.start(2000, True)

    def chkprivado3(self):
        if self.nprivado == 2:
            self.nprivado = 3
        else:
            self.nprivado = 0
            self.info_ini()
        self.TimerPrivado.stop()
        self.TimerPrivado.start(2000, True)

    def muevesel(self):
        if self.modoarchivo:
            nombrelista = 'listaA'
            numero = self[nombrelista].getSelectionIndex()
            try:
                if self.listado[numero][2]:
                    self['key_des'].show()
                    self['img_des'].show()
                else:
                    self['key_des'].hide()
                    self['img_des'].hide()
            except:
                self['key_des'].hide()
                self['img_des'].hide()

    def buildList(self, carpeta = '', archivos = False):
        if not carpeta == '':
            self.carpeta = carpeta
        list = []
        self['listaA'].setList(list)
        self['listaC'].setList(list)
        self['textoinfo'].hide()
        self['key_mode'].setText(_(' '))
        self['key_des'].setText(_('Description'))
        self['key_blue'].setText(_('Update log'))
        self.bloqueado = False
        self['key_help'].setText(_(' '))
        retvalor = devUrlContenido(self.url2, self.usuario, self.pwd, self.carpeta, privado=self.privado)
        if retvalor == None:
            self.vacio = True
            self['textoinfo'].show()
            self['textoinfo'].setText(_('URL Request error. Check internet conection.') + '\n' + _('Press [OK] to retry'))
            self['listaA'].hide()
            self['listaC'].hide()
        else:
            self['listaA'].show()
            self['listaC'].show()
            self['textoinfo'].hide()
            self.vacio = False
            self.listado = retvalor[2]
            if retvalor[0] > 0:
                self.modoarchivo = False
                anadido = ' :: ' + str(retvalor[0]) + ' ' + _('Categorie(s)') + ''
            else:
                self.modoarchivo = True
                anadido = ' :: ' + str(retvalor[1]) + ' ' + _('File(s)') + ''
            self['modo'].setText(' ' + _('Home') + '' + carpeta[5:] + anadido)
            self.titulo = ' ' + _('Home') + '' + carpeta[5:] + anadido
            for i in range(0, len(self.listado)):
                texto = '' + self.listado[i][0].replace('.ipk', '').replace('.tar', '')
                if self.modoarchivo:
                    imagen = 'Otros'
                    if texto == '<' + _('Home') + '>':
                        imagen = 'chome'
                    elif texto == '<' + _('Parent directory') + '>':
                        imagen = 'catras'
                    elif '/PlugIns' in self.carpeta:
                        imagen = 'PlugIns'
                    elif '/Skins' in self.carpeta:
                        imagen = 'Skins'
                    elif '/Listas' in self.carpeta:
                        imagen = 'Listas'
                    else:
                        imagen = 'Actualizaciones'
                    sinsta = False
                    list.append(IniciaSelListEntryArchivo(texto, imagen, sinsta))
                else:
                    imagen = 'cOtros'
                    if texto == '<' + _('Home') + '>':
                        imagen = 'chome'
                    elif texto == '<' + _('Parent directory') + '>':
                        imagen = 'catras'
                    elif texto[:len('PlugIns')] == 'PlugIns':
                        imagen = 'cPlugIns'
                    elif texto[:len('Skins')] == 'Skins':
                        imagen = 'cSkins'
                    elif texto[:len('Listas')] == 'Listas':
                        imagen = 'cListas'
                    elif texto[:len('Actualizaciones')] == 'Actualizaciones':
                        imagen = 'cActualizaciones'
                    list.append(IniciaSelListEntryCarpeta(texto, imagen))

            if self.modoarchivo:
                self['listaA'].show()
                self['listaA'].setList(list)
                self['listaC'].selectionEnabled(0)
                self['listaA'].selectionEnabled(1)
                self['listaC'].hide()
            else:
                self['listaC'].show()
                self['listaC'].setList(list)
                self['listaA'].selectionEnabled(0)
                self['listaC'].selectionEnabled(1)
                self['listaA'].hide()

    def mostrar(self):
        if not self.infomostrado:
            self.info_ini()

    def key_ok(self):
        if self.nprivado == 3:
            self.TimerPrivado.stop()
            self.privado = True
            self.buildList()
        elif self.vacio:
            self.buildList(self.carpeta)
        elif self.bloqueado:
            pass
        elif self.instalando:
            self.instalando = False
            self['listaA'].show()
            self['textoinfo'].hide()
            self['modo'].setText(self.titulo)
        else:
            if self.modoarchivo:
                nombrelista = 'listaA'
            else:
                nombrelista = 'listaC'
            lalista = self[nombrelista].list
            idx = self[nombrelista].getSelectionIndex()
            texto = str(self.listado[idx][0])
            if texto == '<' + _('Home') + '>':
                self.buildList('Camds')
            elif texto == '<' + _('Parent directory') + '>':
                nuevacarpeta = str(self.carpeta.split('/')[-1])
                nuevacarpeta = self.carpeta.replace('/' + nuevacarpeta, '')
                if nuevacarpeta == '/' or nuevacarpeta == '' + _('Home') + '':
                    nuevacarpeta = ''
                self.buildList(nuevacarpeta)
            elif self.modoarchivo:
                self.instalar(idx)
            else:
                self.buildList(self.carpeta + '/' + texto)
        self.nprivado = 0

    def instalar(self, numero):
        archivoipk = self.listado[numero][0]
        dei = self.session.openWithCallback(self.callbackInstall, MessageBox, _('Do you want to install?') + '\n' + archivoipk, MessageBox.TYPE_YESNO)
        dei.setTitle(_('spazeTeam Downloads'))

    def callbackInstall(self, respuesta):
        if respuesta:
            if self.modoarchivo and not self.bloqueado:
                self.instalando = True
                self.bloqueado = True
                self['textoinfo'].show()
                self['textoinfo'].setText('\n\n' + _('Wait...'))
                self['listaA'].hide()
                self.TimerTemp.start(self.tiempotimer, True)
                self.paso = 1
                self.pinfo = ''

    def instalarok(self):
        self.TimerTemp.stop()
        nombrelista = 'listaA'
        numero = self[nombrelista].getSelectionIndex()
        archivoipk = self.listado[numero][0]
        archivoremoto = self.url + self.carpeta + '/' + archivoipk
        self['modo'].setText(self.carpeta + ' :: ' + _('Installing...').replace('...', '') + ' ' + archivoipk)
        comando1 = "cd /tmp;wget '" + archivoremoto + "';" + 'chmod 755 /tmp/' + archivoipk
        if archivoipk.endswith('.tar'):
            comando2 = "tar -xvf '/tmp/" + archivoipk + "' -C /"
        else:
            comando2 = "opkg install --force-overwrite '/tmp/" + archivoipk + "'"
        comando3 = 'rm /tmp/' + archivoipk
        if self.paso == 1:
            self.paso = self.paso + 1
            self.pinfo = '\n\n' + _('Downloading') + '...'
            self['textoinfo'].setText(self.pinfo)
            self.TimerTemp.start(self.tiempotimer, True)
        elif self.paso == 2:
            self.paso = self.paso + 1
            retfile = devFtp(self.url2, usuario=self.usuario, pwd=self.pwd, pcarpeta=self.carpeta, archivo=archivoipk)
            if retfile == None:
                rest = cargaosinfo(comando3, True)
                self.bloqueado = False
                self.paso = 0
                self.pinfo = self.pinfo + '\n\n**********************************\n' + _('Error downloading') + ' (TimeOut)!!! ' + self.carpeta + '/' + archivoipk + '\n**********************************\n' + _('Press any key to back')
                self['textoinfo'].setText(self.pinfo)
                dei = self.session.open(MessageBox, _('Error downloading') + ' (TimeOut)!!!\n ' + self.carpeta + '/' + archivoipk, MessageBox.TYPE_ERROR)
                dei.setTitle(_('spazeTeam') + ' ' + _('Installation'))
            else:
                rest = cargaosinfo('chmod 755 /tmp/' + archivoipk, True)
                if fileExists('/tmp/' + archivoipk):
                    self.TimerTemp.start(self.tiempotimer, True)
                else:
                    self.bloqueado = False
                    self.pinfo = self.pinfo + '\n\n**********************************\n' + _('Error downloading') + '!!! ' + self.carpeta + '/' + archivoipk + '\n**********************************\n' + _('Press any key to back')
                    self['textoinfo'].setText(self.pinfo)
                    dei = self.session.open(MessageBox, _('Error downloading') + '!!!\n ' + self.carpeta + '/' + archivoipk, MessageBox.TYPE_ERROR)
                    dei.setTitle(_('spazeTeam') + ' ' + _('Installation'))
        elif self.paso == 3:
            self.pinfo = self.pinfo + '[' + _('COMPLETED') + ']' + '\n\n' + _('Installing...')
            self['textoinfo'].setText(self.pinfo)
            self.paso = self.paso + 1
            self.TimerTemp.start(self.tiempotimer, True)
        elif self.paso == 4:
            if fileExists('/tmp/' + archivoipk):
                self['textoinfo'].setText(self.pinfo)
                self.paso = self.paso + 1
                rest = cargaosinfo(comando2, True)
                self.pinfo = self.pinfo + '[' + _('COMPLETED') + ']'
                if len(rest.replace('\n', '')) > 2:
                    self.pinfo = self.pinfo + '\n*******************************************************\n' + rest + '\n*******************************************************'
                self.pinfo = self.pinfo + '\n\n' + _('Finish...')
                self['textoinfo'].setText(self.pinfo)
                self['textoinfo'].lastPage()
                self.TimerTemp.start(self.tiempotimer, True)
            else:
                self.pinfo = self.pinfo + '\n\n**********************************\n' + _('Error downloading') + '!!! ' + self.carpeta + '/' + archivoipk + '\n**********************************\n' + _('Press any key to back')
                dei = self.session.open(MessageBox, _('Error downloading') + '!!!\n ' + self.carpeta + '/' + archivoipk, MessageBox.TYPE_ERROR)
                dei.setTitle(_('spazeTeam') + ' ' + _('Installation'))
                self.bloqueado = False
                self['textoinfo'].setText(self.pinfo)
        elif self.paso == 5:
            self.paso = 0
            rest = cargaosinfo(comando3, True)
            self.pinfo = self.pinfo + '[' + _('COMPLETED') + ']' + '\n' + _('Finished') + ' :: ' + _('Press any key to back')
            idx = self['listaA'].getSelectionIndex()
            nombreipk = self.listado[idx][0]
            sinsta = False
            self['textoinfo'].setText(self.pinfo)
            self['textoinfo'].lastPage()
            self.bloqueado = False

    def key_info(self):
        if self.vacio:
            pass
        elif self.bloqueado:
            pass
        elif self.instalando:
            self.instalando = False
            self['listaA'].show()
            self['textoinfo'].hide()
            self['modo'].setText(self.titulo)
        elif self.modoarchivo:
            nombrelista = 'listaA'
            try:
                lalista = self[nombrelista].list
                idx = self[nombrelista].getSelectionIndex()
                if self.listado[idx][2]:
                    texto = str(self.listado[idx][0])
                    if texto == '<' + _('Home') + '>':
                        pass
                    elif texto == '<' + _('Parent directory') + '>':
                        pass
                    else:
                        laurl = self.carpeta + '/' + texto.replace('.ipk', '.txt').replace('.tar', '.txt')
                        ttemp = str(self.listado[idx])
                        ttemp = ''
                        intentos = 3
                        html = None
                        for iji in range(intentos):
                            html = devhtml(self.url2, usuario=self.usuario, pwd=self.pwd, pcarpeta=laurl)
                            if not html == None:
                                if len(str(html)) > 5:
                                    break

                        if not html == None:
                            dei = self.session.open(InfoArchivo, titulo=texto, textoinfo=ttemp + '\n' + html)
                        else:
                            dei = self.session.open(MessageBox, ttemp + '\n' + _('Error reading remote file') + '\n' + texto, MessageBox.TYPE_ERROR)
            except:
                pass

    def info_ini(self):
        laurl = '/updates.txt'
        intentos = 3
        html = None
        for iji in range(intentos):
            html = devhtml(self.url2, usuario=self.usuario, pwd=self.pwd, pcarpeta=laurl)
            if not html == None:
                if len(str(html)) > 5:
                    break

        if not html == None:
            self.infomostrado = True
            dei = self.session.open(InfoArchivo, titulo=_('Updates log'), textoinfo=html)

    def key_left(self):
        if self.vacio:
            pass
        elif self.bloqueado:
            pass

    def key_right(self):
        if self.vacio:
            pass
        elif self.bloqueado:
            pass

    def key_up(self):
        if self.vacio:
            pass
        elif self.bloqueado:
            pass
        elif self.instalando:
            self['textoinfo'].pageUp()
        else:
            self['listaC'].up()
            self['listaA'].up()

    def key_down(self):
        if self.vacio:
            pass
        elif self.bloqueado:
            pass
        elif self.instalando:
            self['textoinfo'].pageDown()
        else:
            self['listaA'].down()
            self['listaC'].down()

    def volver(self):
        if self.vacio:
            self.exit()
        elif self.bloqueado:
            pass
        elif self.instalando:
            self.instalando = False
            self['listaA'].show()
            self['textoinfo'].hide()
            self['modo'].setText(self.titulo)
        elif self.carpeta == 'Camds':
            self.exit()
        else:
            nuevacarpeta = str(self.carpeta.split('/')[-1])
            nuevacarpeta = self.carpeta.replace('/' + nuevacarpeta, '')
            if nuevacarpeta == '/' or nuevacarpeta == '' + _('Home') + '':
                nuevacarpeta = ''
            self.buildList(nuevacarpeta)

    def callbackSetSalir(self, respuesta):
        if respuesta:
            self.exit()

    def exit(self):
        self.fin = 1
        self.close(True)


global bloquetemp ## Warning: Unused global
