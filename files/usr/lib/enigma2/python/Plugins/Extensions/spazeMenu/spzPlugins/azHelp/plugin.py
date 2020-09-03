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
from Components.config import getConfigListEntry, ConfigEnableDisable, ConfigYesNo, ConfigText, ConfigClock, ConfigNumber, ConfigSelection, config, ConfigSubsection, ConfigSubList, ConfigSubDict, ConfigDirectory
from Tools import Notifications
from Tools.HardwareInfo import HardwareInfo
import os
import string
from os import popen as os_popen
from time import localtime, asctime, time, gmtime
from Tools.Directories import fileExists, resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE, SCOPE_SKIN
from Components.Language import language
from os import environ
import os
import gettext
import sys
lang = language.getLanguage()
environ['LANGUAGE'] = lang[:2]
gettext.bindtextdomain('enigma2', resolveFilename(SCOPE_LANGUAGE))
gettext.textdomain('enigma2')
gettext.bindtextdomain('azHelp', '%s%s' % (resolveFilename(SCOPE_PLUGINS), 'Extensions/spazeMenu/spzPlugins/azHelp/locale/'))

def _(txt):
    t = gettext.dgettext('azHelp', txt)
    if t == txt:
        t = gettext.gettext(txt)
    return t


carpetaimg = '/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/azHelp/img/'
nommodelo = 'NA'

def devpremium():
    global nommodelo
    if fileExists('/etc/modelo'):
        flines = open('/etc/modelo', 'r')
        ret = ''
        for line in flines:
            ret = ret + line

        flines.close()
        if 'premium' in ret:
            ret = 'premium'
        else:
            ret = 'elite'
        nommodelo = ret
    else:
        ret = HardwareInfo().get_device_name()
        os.system('echo ' + ret + '>/etc/modelo;')
    if ret == 'premium':
        return True
    else:
        return False


class IniciaSelListFaqs(MenuList):

    def __init__(self, list, enableWrapAround = False):
        MenuList.__init__(self, list, enableWrapAround, eListboxPythonMultiContent)
        self.l.setItemHeight(30)
        self.l.setFont(0, gFont('Regular', 19))
        self.l.setFont(1, gFont('Regular', 17))


def IniciaSelListEntryFaqs(texto, yavista = False):
    global carpetaimg
    res = [texto]
    res.append(MultiContentEntryText(pos=(35, 4), size=(1000, 30), font=0, text=texto))
    if not yavista:
        imagen = 'prefs8.png'
    else:
        imagen = 'infochfs8.png'
    png = '' + carpetaimg + '' + imagen + ''
    if fileExists(png):
        fpng = LoadPixmap(png)
        res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHATEST,
         2,
         2,
         24,
         24,
         fpng))
    return res


class IniciaSelList(MenuList):

    def __init__(self, list, enableWrapAround = False):
        MenuList.__init__(self, list, enableWrapAround, eListboxPythonMultiContent)
        self.l.setItemHeight(70)
        self.l.setFont(0, gFont('Regular', 19))
        self.l.setFont(1, gFont('Regular', 17))


def IniciaSelListEntry(imagen, tecla, texto, premiun):
    tecla = '[' + tecla + ']'
    res = [tecla]
    res.append(MultiContentEntryText(pos=(75, 1), size=(700, 25), font=0, text=tecla))
    res.append(MultiContentEntryText(pos=(75, 23), size=(700, 50), font=1, text=texto))
    if premiun:
        png = '' + carpetaimg + '' + imagen + '-fs8.png'
    else:
        png = '' + carpetaimg + 'elite/' + imagen + '-fs8.png'
    if fileExists(png):
        fpng = LoadPixmap(png)
        res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHATEST,
         2,
         2,
         71,
         65,
         fpng))
    return res


class azVerfaq(Screen):
    skin = '\n\t<screen name="azVerFaqsScr" position="center,center" size="1000,610" title="%s">\n\n\t<widget name="respuesta" position="8,87" size="970,470"  zPosition="12" text=" " font="Regular; 19" />\n\t<ePixmap name="new ePixmap" position="10,33" size="35,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/azHelp/img/prefs8.png" alphatest="blend" transparent="1" zPosition="10"/>\n\n\t<widget name="modo" position="8,31" size="970,50" backgroundColor="#ffffff" foregroundColor="#000000" text=" " font="Regular; 22" />\n\n\t<widget name="key_red" position="654,585" size="162,22" transparent="1" text="Exit" font="Regular; 16"/>\n\n\t<widget name="key_mode" position="8,8" size="685,22" transparent="1" text=" " font="Regular; 15" halign="left" />\n\t</screen>' % _('FAQs')

    def __init__(self, session, numeropregunta = None):
        self.session = session
        Screen.__init__(self, session)
        self.npregunta = numeropregunta
        self['respuesta'] = Label(_(''))
        self.modoactivo = 1
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
         'up': self.exit,
         'down': self.exit,
         'info': self.exit,
         'ok': self.exit}, -2)
        self.onLayoutFinish.append(self.cargapregunta)

    def exit(self):
        self.close(True)

    def cargapregunta(self):
        self['key_red'].setText(_(' '))
        self['key_mode'].setText(_('Press any key to go back'))
        archivo = '/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/azHelp/faqs/faqsazhelp.xml'
        import xml.sax.xmlreader
        from xml.dom import minidom, Node
        from Tools.XMLTools import stringToXML
        menu = xml.dom.minidom.parse(archivo)
        rootNode = menu.childNodes[0]
        contador = 0
        for node in rootNode.childNodes:
            if node.nodeType == Node.ELEMENT_NODE:
                for node2 in node.childNodes:
                    if node2.nodeType == Node.ELEMENT_NODE:
                        id = pregunta = categoria = respuesta = ''
                        for node3 in node2.childNodes:
                            if node2.nodeType == Node.ELEMENT_NODE:
                                for node4 in node3.childNodes:
                                    if node3.nodeType == Node.ELEMENT_NODE:
                                        if node4.nodeType == Node.TEXT_NODE:
                                            if node3.nodeName == 'categoria':
                                                categoria = node4.nodeValue.encode('utf-8')
                                            elif node3.nodeName == 'id':
                                                id = node4.nodeValue.encode('utf-8')
                                            elif node3.nodeName == 'pregunta':
                                                pregunta = node4.nodeValue.encode('utf-8')
                                            elif node3.nodeName == 'respuesta':
                                                respuesta = node4.nodeValue.encode('utf-8')

                        contador = contador + 1
                        if self.npregunta == str(contador):
                            self['modo'].setText('     ' + pregunta + ' (' + categoria + ')')
                            self['respuesta'].setText(respuesta)
                            break


class azFaqs(Screen):
    skin = '\n\t<screen name="azFaqsScr" position="center,center" size="1000,610" title="%s">\n\n\t<widget name="lista" position="8,67" size="970,490" scrollbarMode="showOnDemand" zPosition="12" />\n\t<widget name="modo" position="8,31" size="970,30" backgroundColor="#ffffff" foregroundColor="#000000" text=" " font="Regular; 22" />\n\n\t<ePixmap name="new ePixmap" position="620,584" size="35,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/azHelp/img/red.png" alphatest="blend" transparent="1" />\n\t<widget name="key_red" position="654,585" size="162,22" transparent="1" text="Exit" font="Regular; 16"/>\n\t<!--<ePixmap name="new ePixmap" position="715,584" size="35,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/azHelp/img/green.png" alphatest="blend" transparent="1" />-->\n\t<widget name="key_green" position="749,585" size="462,22" transparent="1" text=" " font="Regular; 16"/>\n\t<widget name="key_help" position="8,585" backgroundColor="#000000" size="856,22" transparent="1" text="This help is avaible in tv screen pressing home menu key" font="Regular; 15" halign="left" zPosition="10" />\n\t<widget name="key_mode" position="8,8" size="685,22" transparent="1" text=" " font="Regular; 15" halign="left" />\n\t</screen>' % _('FAQs openSPA')

    def __init__(self, session, instance = None, args = 0):
        self.session = session
        Screen.__init__(self, session)
        self.faqs = []
        self['lista'] = IniciaSelListFaqs([])
        self.modoactivo = 1
        self.categorias = ['Todo']
        self.vistas = []
        self['modo'] = Label(_(''))
        self['key_help'] = Label(_(''))
        self['key_mode'] = Label(_(''))
        self['key_red'] = Label(_('Exit'))
        self['key_green'] = Label('')
        self['setupActions'] = ActionMap(['WizardActions',
         'DirectionActions',
         'ColorActions',
         'NumberActions',
         'MenuActions',
         'EPGSelectActions',
         'InfobarActions'], {'green': self.volver,
         'red': self.exit,
         'back': self.exit,
         'left': self.key_left,
         'right': self.key_right,
         'up': self.key_up,
         'down': self.key_down,
         'info': self.key_info,
         'ok': self.key_ok}, -2)
        self.onLayoutFinish.append(self.buildList)

    def cargapreguntas(self, filtrado = None):
        self.categorias = ['Todo']
        self.faqs = []
        archivo = '/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/azHelp/faqs/faqsazhelp.xml'
        import xml.sax.xmlreader
        from xml.dom import minidom, Node
        from Tools.XMLTools import stringToXML
        menu = xml.dom.minidom.parse(archivo)
        rootNode = menu.childNodes[0]
        contador = 0
        for node in rootNode.childNodes:
            if node.nodeType == Node.ELEMENT_NODE:
                for node2 in node.childNodes:
                    if node2.nodeType == Node.ELEMENT_NODE:
                        id = pregunta = categoria = respuesta = ''
                        for node3 in node2.childNodes:
                            if node2.nodeType == Node.ELEMENT_NODE:
                                for node4 in node3.childNodes:
                                    if node3.nodeType == Node.ELEMENT_NODE:
                                        if node4.nodeType == Node.TEXT_NODE:
                                            if node3.nodeName == 'categoria':
                                                categoria = node4.nodeValue.encode('utf-8')
                                            if node3.nodeName == 'id':
                                                id = node4.nodeValue.encode('utf-8')
                                            elif node3.nodeName == 'pregunta':
                                                pregunta = node4.nodeValue.encode('utf-8')

                        contador = contador + 1
                        if filtrado == None or filtrado == categoria:
                            self.faqs.append((contador, pregunta, categoria))
                        if categoria not in self.categorias:
                            self.categorias.append(categoria)

    def buildList(self, modolista = 1):
        self['key_mode'].setText(_('Utiliza los cursores izquierdo(<) y derecho (>) para filtrar por categor\xc3\xada'))
        titulo = _(' FAQs')
        cfiltrado = None
        if modolista > 1:
            titulo = titulo + ' :: Mostrando categor\xc3\xada: ' + self.categorias[modolista - 1]
            cfiltrado = self.categorias[modolista - 1]
        else:
            titulo = titulo + ' :: Mostrando todo'
        self['key_help'].setText(_('This help is avaible in tv screen pressing home menu key'))
        self.modoactivo = modolista
        self.cargapreguntas(cfiltrado)
        self['modo'].setText(titulo + ' (' + str(len(self.faqs)) + ') <>')
        list = []
        for i in range(0, len(self.faqs)):
            lafaq = '' + self.faqs[i][1]
            numero = str(self.faqs[i][0])
            vista = False
            if numero in self.vistas:
                vista = True
            list.append(IniciaSelListEntryFaqs(lafaq, vista))

        self['lista'].setList(list)

    def key_ok(self):
        lalista = self['lista'].list
        idx = self['lista'].getSelectionIndex()
        texto = str(lalista[idx][0])
        numero = str(self.faqs[idx][0])
        if numero not in self.vistas:
            self.vistas.append(numero)
        info1 = ''
        info2 = texto + ''
        self.buildList(self.modoactivo)
        self.session.openWithCallback(self.callBackFaqsVer, azVerfaq, numeropregunta=numero)

    def callBackFaqsVer(self, respuesta):
        if respuesta:
            pass

    def key_info(self):
        info1 = 'FAQs'
        info2 = 'by spazeTeam (azboxhd.es), 2012'
        cmens = _(info1) + ' [' + nommodelo + ']\n' + _(info2).replace('spazeTeam', 'openSPA')
        dei = self.session.open(MessageBox, cmens, MessageBox.TYPE_INFO)
        dei.setTitle(_('openSPA') + ' ' + _('Help'))

    def key_left(self):
        self.modoactivo -= 1
        if self.modoactivo < 1:
            self.modoactivo = len(self.categorias)
        self.buildList(self.modoactivo)
        self['lista'].moveToIndex(0)

    def key_right(self):
        self.modoactivo += 1
        if self.modoactivo > len(self.categorias):
            self.modoactivo = 1
        self.buildList(self.modoactivo)
        self['lista'].moveToIndex(0)

    def key_up(self):
        self['lista'].up()

    def key_down(self):
        self['lista'].down()

    def volver(self):
        self.close(False)

    def exit(self):
        self.close(True)
