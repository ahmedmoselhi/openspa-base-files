from Components.Label import Label
from Components.MenuList import MenuList
from Screens.ChannelSelection import SimpleChannelSelection
from Components.MultiContent import MultiContentEntryText
from enigma import eListboxPythonMultiContent, eServiceCenter, gFont, eServiceReference
from ServiceReference import ServiceReference
from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens import Standby
from Components.ActionMap import ActionMap
from Components.Button import Button
from Plugins.Extensions.spazeMenu.plugin import esHD, fhd
import string
from Tools.Directories import fileExists, resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE
from Components.Language import language
from os import environ
import os
import gettext
lang = language.getLanguage()
environ['LANGUAGE'] = lang[:2]
gettext.bindtextdomain('enigma2', resolveFilename(SCOPE_LANGUAGE))
gettext.textdomain('enigma2')
gettext.bindtextdomain('seletquiv', '%s%s' % (resolveFilename(SCOPE_PLUGINS), 'Extensions/spazeMenu/spzPlugins/mhw2Timer/locale/'))

def _(txt):
    t = gettext.dgettext('seletquiv', txt)
    if t == txt:
        t = gettext.gettext(txt)
    return t


listacanales = []

def main(session, **kwargs):
    try:
        session.open(IniciaSel)
    except:
        print '[IniciaSel equiv] Pluginexecution failed'


class IniciaSelList2(MenuList):

    def __init__(self, list, enableWrapAround = False):
        MenuList.__init__(self, list, enableWrapAround, eListboxPythonMultiContent)
        self.l.setItemHeight(fhd(25))
        self.l.setFont(0, gFont('Regular', 20))
        self.l.setFont(1, gFont('Regular', 20))


class IniciaSelList(MenuList):

    def __init__(self, list, enableWrapAround = False):
        MenuList.__init__(self, list, enableWrapAround, eListboxPythonMultiContent)
        self.l.setItemHeight(fhd(50))
        self.l.setFont(0, gFont('Regular', 20))
        self.l.setFont(1, gFont('Regular', 18))


def IniciaSelListEntry(serviceName, eventName):
    res = [serviceName]
    res.append(MultiContentEntryText(pos=(fhd(4), 0), size=(fhd(760), fhd(22)), font=0, text=serviceName))
    res.append(MultiContentEntryText(pos=(fhd(24), fhd(22)), size=(fhd(760), fhd(20)), font=1, text=eventName, color=10066329))
    return res


def nombrelista2(reflista, soloref = False):
    global listacanales
    tempret = reflista.replace('1:0:1:', '').replace(':C00000:0:0:0:', '').replace(':C00000:0:0:0', '')
    tempret = tempret.lstrip().rstrip()
    nombre = '(' + _('*** CHANNEL NOT FOUND ***') + ')'
    for elelista in listacanales:
        servicetemp = elelista
        oneline2 = '' + ''.join(servicetemp.split(' --> ')[:-1]) + ''
        numero = '' + servicetemp.split(' --> ')[-1] + ''
        numero = numero.lstrip().rstrip()
        if numero in reflista:
            nombre = '(' + oneline2 + ')'

    return reflista + ' ' + nombre


def nombrelista(reflista, soloref = False):
    templista = '' + ''.join(reflista.split(' (')[:-1]) + ''
    if len(templista) == 0:
        templista = reflista
    templista = templista.lstrip().rstrip()
    if templista[0:3] == '-->':
        templista = templista[3:]
    templista = templista.lstrip().rstrip()
    if soloref:
        nomcan = ''
    else:
        nomcan = _('*** CHANNEL NOT FOUND ***')
        try:
            refser = eServiceReference(templista)
            nomcan = ServiceReference(refser).getServiceName().replace('\xc2\x86', '').replace('\xc2\x87', '')
            if len(nomcan) == 0 or nomcan is None:
                nomcan = _('*** CHANNEL NOT FOUND ***')
        except:
            nomcan = _('*** CHANNEL NOT FOUND ***')

        nomcan = ' (' + nomcan + ')'
    return templista + '' + nomcan + ''


def cargalista():
    global listacanales
    listacanales = []
    archivo = '/etc/mhw_Chann.epg'
    sourceEncoding = 'iso-8859-1'
    targetEncoding = 'utf-8'
    source = open(archivo)
    linea = source.read()
    source.close()
    archivo = '/etc/mhw_Chann_utf8.epg'
    target = open(archivo, 'w')
    target.write(unicode(linea, sourceEncoding).encode(targetEncoding))
    target.close()
    booklist = open(archivo, 'r')
    booklist = None
    if fileExists(archivo):
        try:
            booklist = open(archivo, 'r')
        except:
            dei = self.session.open(MessageBox, _('Error reading') + ' /etc/mhw_Chann.epg!', MessageBox.TYPE_ERROR)
            dei.setTitle(_('Select source channel'))

        if booklist is not None:
            for oneline in booklist:
                cadena = oneline[0:1]
                if '#' not in oneline and len(oneline) > 7:
                    listacanales.append(string.upper(oneline.replace('(', '').replace(') ', ' --> ')))

            booklist.close()
        listacanales.sort()
        os.system('rm ' + archivo)
    return len(listacanales)


class ElegirCanal(Screen):
    if esHD():
        skin = '\n\t\t<screen position="center,center" size="700,450" title="%s" backgroundColor="#000000">\n\t\t<ePixmap pixmap="usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/hdred.png" position="0,400" size="140,40" transparent="1" alphatest="blend" />\n\t\t<ePixmap pixmap="usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/hdgreen.png" position="140,400" size="140,40" transparent="1" alphatest="blend" />\n\t\t<widget name="key_red" position="0,400" zPosition="1" size="140,40" font="Regular;16" valign="center" halign="center" backgroundColor="#1f771f" transparent="1" />\n\t\t<widget name="key_green" position="140,400" zPosition="1" size="140,40" font="Regular;16" valign="center" halign="center" backgroundColor="#1f771f" transparent="1" />\n\t\t<widget name="list" position="0,0" size="700,400" scrollbarMode="showOnDemand" />\n\t\t</screen>' % _('Select source channel')
    else:
        skin = '\n\t\t<screen position="center,center" size="700,450" title="%s" backgroundColor="#000000">\n\t\t<ePixmap pixmap="skin_default/buttons/red.png" position="0,400" size="140,40" transparent="1" alphatest="on" />\n\t\t<ePixmap pixmap="skin_default/buttons/green.png" position="140,400" size="140,40" transparent="1" alphatest="on" />\n\t\t<widget name="key_red" position="0,400" zPosition="1" size="140,40" font="Regular;16" valign="center" halign="center" backgroundColor="#1f771f" transparent="1" />\n\t\t<widget name="key_green" position="140,400" zPosition="1" size="140,40" font="Regular;16" valign="center" halign="center" backgroundColor="#1f771f" transparent="1" />\n\t\t<widget name="list" position="0,0" size="700,400" scrollbarMode="showOnDemand" />\n\t\t</screen>' % _('Select source channel')

    def __init__(self, session, inicial):
        Screen.__init__(self, session)
        self['list'] = IniciaSelList2([])
        self['key_red'] = Label(_('Cancel'))
        self['key_green'] = Label(_('Ok'))
        self.ini = inicial.replace('1:0:1:', '').replace(':C00000:0:0:0:', '')
        self.setTitle(_('Source channel') + ' :: ' + self.ini)
        self['actions'] = ActionMap(['OkCancelActions', 'ColorActions'], {'red': self.cerrar,
         'cancel': self.cerrar,
         'green': self.guardar,
         'ok': self.guardar}, prio=-1)
        self.onLayoutFinish.append(self.buildList3)

    def cerrar(self):
        self.close(False)

    def guardar(self):
        lalista = self['list'].list
        length = len(lalista)
        if length > 0:
            idx = self['list'].getSelectionIndex()
            servicetemp = str(lalista[idx][0])
            oneline2 = '' + ''.join(servicetemp.split(' --> ')[:-1]) + ''
            numero = '' + servicetemp.split(' --> ')[-1]
            numero = numero.lstrip().rstrip()
            nombre = ' (' + oneline2 + ')'
            ret = '1:0:1:' + numero + ':C00000:0:0:0:' + nombre
            self.close(ret)

    def buildList3(self):
        list = []
        pos = 0
        posini = 0
        prime = '' + ''.join(self.ini.split(' (')[:-1]) + ''
        for elelista in listacanales:
            list.append(IniciaSelListEntry(elelista, ''))
            if prime in elelista and len(prime) > 7:
                posini = pos
            pos = pos + 1

        self['list'].setList(list)
        self['list'].moveToIndex(posini)


class SelEquiv(Screen):
    if esHD():
        skin = '\n\t\t<screen position="center,center" size="1050,750" title="%s" backgroundColor="#000000">\n\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/hdred.png" position="0,0" size="210,60" transparent="1" alphatest="blend" />\n\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/hdgreen.png" position="210,0" size="210,60" transparent="1" alphatest="blend" />\n\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/hdyellow.png" position="630,0" size="210,60" transparent="1" alphatest="blend" />\n\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/hdblue.png" position="840,0" size="210,60" transparent="1" alphatest="blend" />\n\t\t<widget name="key_red" position="0,0" zPosition="1" size="210,60" font="Regular;16" valign="center" halign="center" backgroundColor="#1f771f" transparent="1"  borderColor="black" borderWidth="1" noWrap="1"/>\n\t\t<widget name="key_green" position="210,0" zPosition="1" size="210,60" font="Regular;16" valign="center" halign="center" backgroundColor="#1f771f" transparent="1" borderColor="black" borderWidth="1" noWrap="1"/>\n\t\t<widget name="key_yellow" position="630,0" zPosition="1" size="210,60" font="Regular;16" valign="center" halign="center" backgroundColor="#1f771f" transparent="1" borderColor="black" borderWidth="1" noWrap="1"/>\n\t\t<widget name="key_blue" position="840,0" zPosition="1" size="210,60" font="Regular;16" valign="center" halign="center" backgroundColor="#1f771f" transparent="1" borderColor="black" borderWidth="1" noWrap="1"/>\n\t\t<widget name="status" position="0,675" zPosition="1" size="1050,60" font="Regular;16" valign="center" halign="center" backgroundColor="#1f771f" transparent="1" />\n\t\t<widget name="list" position="0,60" size="1050,600" scrollbarMode="showOnDemand" />\n\t\t</screen>' % _('Edit equivalence')
    else:
        skin = '\n\t\t<screen position="center,center" size="700,500" title="%s" backgroundColor="#000000">\n\t\t<ePixmap pixmap="skin_default/buttons/red.png" position="0,0" size="140,40" transparent="1" alphatest="on" />\n\t\t<ePixmap pixmap="skin_default/buttons/green.png" position="140,0" size="140,40" transparent="1" alphatest="on" />\n\t\t<ePixmap pixmap="skin_default/buttons/yellow.png" position="420,0" size="140,40" transparent="1" alphatest="on" />\n\t\t<ePixmap pixmap="skin_default/buttons/blue.png" position="560,0" size="140,40" transparent="1" alphatest="on" />\n\t\t<widget name="key_red" position="0,0" zPosition="1" size="140,40" font="Regular;16" valign="center" halign="center" backgroundColor="#1f771f" transparent="1"  borderColor="black" borderWidth="1" noWrap="1"/>\n\t\t<widget name="key_green" position="140,0" zPosition="1" size="140,40" font="Regular;16" valign="center" halign="center" backgroundColor="#1f771f" transparent="1" borderColor="black" borderWidth="1" noWrap="1"/>\n\t\t<widget name="key_yellow" position="420,0" zPosition="1" size="140,40" font="Regular;16" valign="center" halign="center" backgroundColor="#1f771f" transparent="1" borderColor="black" borderWidth="1" noWrap="1"/>\n\t\t<widget name="key_blue" position="560,0" zPosition="1" size="140,40" font="Regular;16" valign="center" halign="center" backgroundColor="#1f771f" transparent="1" borderColor="black" borderWidth="1" noWrap="1"/>\n\t\t<widget name="status" position="0,450" zPosition="1" size="700,40" font="Regular;16" valign="center" halign="center" backgroundColor="#1f771f" transparent="1" />\n\t\t<widget name="list" position="0,40" size="700,400" scrollbarMode="showOnDemand" />\n\t</screen>' % _('Edit equivalence')

    def __init__(self, session, tsource = None, ttarget = None):
        Screen.__init__(self, session)
        self.tmp1 = tsource
        self.tmp2 = ttarget
        self.cambiado = False
        self['list'] = IniciaSelList2([])
        self['key_red'] = Label(_('Cancel'))
        self['key_green'] = Label(_('Save'))
        self['key_yellow'] = Label(_('Zap to source'))
        self['key_blue'] = Label(_('Zap to target'))
        self['status'] = Label('')
        self['actions'] = ActionMap(['OkCancelActions', 'ColorActions'], {'red': self.cerrar,
         'cancel': self.cerrar,
         'yellow': self.zap1,
         'green': self.guardar,
         'ok': self.editarLinea,
         'blue': self.zap2}, prio=-1)
        self.onLayoutFinish.append(self.buildList2)

    def editarLinea(self):
        idx = self['list'].getSelectionIndex()
        if idx == 0:
            self.editar()
        if idx == 1:
            self.editar2()

    def guardar(self):
        self.volver(True)

    def volver(self, answer):
        if answer:
            lalista = self['list'].list
            lista = []
            lista.append(lalista[0][0])
            lista.append(lalista[1][0])
            self.close(lista)
        else:
            self.close(False)

    def cerrar(self):
        if self.cambiado:
            laref = _('Save changes to this equivalence?')
            dei = self.session.openWithCallback(self.volver, MessageBox, laref, MessageBox.TYPE_YESNO)
            dei.setTitle(_('Equivalence changed'))
        else:
            self.close(False)

    def buildList2(self):
        lista = []
        lista.append(IniciaSelListEntry(self.tmp1, ''))
        lista.append(IniciaSelListEntry(self.tmp2, ''))
        self['list'].setList(lista)

    def editar(self):
        lista = self['list'].list
        length = len(lista)
        if length > 0:
            self.session.openWithCallback(self.finishedServiceSelection1, ElegirCanal, lista[0][0])

    def editar2(self):
        self.session.openWithCallback(self.finishedServiceSelection2, SimpleChannelSelection, _('Select target channel'))

    def finishedServiceSelection1(self, args):
        if args:
            self.cambiado = True
            origen = args
            lista = self['list'].list
            ele = lista[1][0]
            lista = []
            lista.append(IniciaSelListEntry(origen, ''))
            lista.append(IniciaSelListEntry(ele, ''))
            self['list'].setList(lista)

    def finishedServiceSelection2(self, *args):
        if args:
            self.cambiado = True
            laref = args[0].toString()
            nombrecanal = ServiceReference(args[0]).getServiceName().replace('\xc2\x86', '').replace('\xc2\x87', '')
            origen = '-->' + laref + ' (' + nombrecanal + ')'
            lista = self['list'].list
            ele = lista[0][0]
            lista = []
            lista.append(IniciaSelListEntry(ele, ''))
            lista.append(IniciaSelListEntry(origen, ''))
            self['list'].setList(lista)

    def zap1(self):
        lalista = self['list'].list
        length = len(lalista)
        if length > 0:
            idx = self['list'].getSelectionIndex()
            servicetemp = str(lalista[0][0])
            service = nombrelista(servicetemp, True)
            self['status'].setText(_('Zap to source') + ': ' + service)
            if service:
                self.session.nav.playService(eServiceReference(service))

    def zap2(self):
        lalista = self['list'].list
        length = len(lalista)
        if length > 0:
            idx = self['list'].getSelectionIndex()
            servicetemp = str(lalista[1][0])
            service = nombrelista(servicetemp, True)
            self['status'].setText(_('Zap to target') + ': ' + service)
            if service:
                self.session.nav.playService(eServiceReference(service))


class IniciaSel(Screen):
    if esHD():
        skin = '\n\t\t<screen position="center,center" size="1140,750" title="%s" backgroundColor="#000000">\n\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/hdred.png" position="0,0" size="210,60" transparent="1" alphatest="blend" />\n\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/hdgreen.png" position="210,0" size="210,60" transparent="1" alphatest="blend" />\n\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/hdyellow.png" position="630,0" size="210,60" transparent="1" alphatest="blend" />\n\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/hdblue.png" position="840,0" size="210,60" transparent="1" alphatest="blend" />\n\t\t<widget name="key_red" position="0,0" zPosition="1" size="210,60" font="Regular;16" valign="center" halign="center" backgroundColor="#000000" transparent="1" borderColor="black" borderWidth="1"/>\n\t\t<widget name="key_green" position="210,0" zPosition="1" size="210,60" font="Regular;16" valign="center" halign="center" backgroundColor="#000000" transparent="1" borderColor="black" borderWidth="1"/>\n\t\t<widget name="key_yellow" position="630,0" zPosition="1" size="210,60" font="Regular;16" valign="center" halign="center" backgroundColor="#000000" transparent="1" borderColor="black" borderWidth="1" />\n\t\t<widget name="key_blue" position="840,0" zPosition="1" size="210,60" font="Regular;16" valign="center" halign="center" backgroundColor="#000000" transparent="1" borderColor="black" borderWidth="1" />\n\t\t<widget name="status" position="0,675" zPosition="1" size="1140,60" font="Regular;16" valign="center" halign="center" backgroundColor="#000000" transparent="1" borderColor="black" borderWidth="1" />\n\t\t<widget name="list" position="0,60" size="1140,600" scrollbarMode="showOnDemand" />\n\t\t</screen>' % _('Channel equivalence mhw2 by spaZeTeam (azboxhd.es)')
    else:
        skin = '\n\t\t<screen position="center,center" size="760,500" title="%s" backgroundColor="#000000">\n\t\t<ePixmap pixmap="skin_default/buttons/red.png" position="0,0" size="140,40" transparent="1" alphatest="on" />\n\t\t<ePixmap pixmap="skin_default/buttons/green.png" position="140,0" size="140,40" transparent="1" alphatest="on" />\n\t\t<ePixmap pixmap="skin_default/buttons/yellow.png" position="420,0" size="140,40" transparent="1" alphatest="on" />\n\t\t<ePixmap pixmap="skin_default/buttons/blue.png" position="560,0" size="140,40" transparent="1" alphatest="on" />\n\t\t<widget name="key_red" position="0,0" zPosition="1" size="140,40" font="Regular;16" valign="center" halign="center" backgroundColor="#000000" transparent="1" borderColor="black" borderWidth="1"/>\n\t\t<widget name="key_green" position="140,0" zPosition="1" size="140,40" font="Regular;16" valign="center" halign="center" backgroundColor="#000000" transparent="1" borderColor="black" borderWidth="1"/>\n\t\t<widget name="key_yellow" position="420,0" zPosition="1" size="140,40" font="Regular;16" valign="center" halign="center" backgroundColor="#000000" transparent="1" borderColor="black" borderWidth="1" />\n\t\t<widget name="key_blue" position="560,0" zPosition="1" size="140,40" font="Regular;16" valign="center" halign="center" backgroundColor="#000000" transparent="1" borderColor="black" borderWidth="1" />\n\t\t<widget name="status" position="0,450" zPosition="1" size="760,40" font="Regular;16" valign="center" halign="center" backgroundColor="#000000" transparent="1" borderColor="black" borderWidth="1" />\n\t\t<widget name="list" position="0,40" size="760,400" scrollbarMode="showOnDemand" />\n\t\t</screen>' % _('Channel equivalence mhw2 by spaZeTeam (azboxhd.es)')

    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session
        self.tempch1 = None
        self.tempna1 = None
        self.tempch2 = None
        self.tempna2 = None
        self.oldService = None
        self.cambiado = False
        try:
            self.oldService = self.session.nav.getCurrentlyPlayingServiceOrGroup()
        except Exception as e:
            self.oldService = None

        self.serviceHandler = eServiceCenter.getInstance()
        self['list'] = IniciaSelList([])
        self['key_red'] = Label(_('Delete'))
        self['key_yellow'] = Label(_('Zap to source'))
        self['key_green'] = Label(_('Add entry'))
        self['key_blue'] = Label(_('Zap to target'))
        self['status'] = Label('')
        self['actions'] = ActionMap(['OkCancelActions', 'ColorActions'], {'red': self.delete,
         'cancel': self.exitsave,
         'green': self.anadir,
         'yellow': self.zap1,
         'ok': self.editar,
         'blue': self.zap2}, prio=-1)
        self.onLayoutFinish.append(self.buildList)

    def editar(self):
        lalista = self['list'].list
        length = len(lalista)
        if length > 0:
            idx = self['list'].getSelectionIndex()
            s1 = str(lalista[idx][0])
            s2 = str(lalista[idx][2][7])
            dei = self.session.openWithCallback(self.callbackeditar, SelEquiv, tsource=s1, ttarget=s2)

    def callbackeditar(self, answer):
        if answer:
            idx = self['list'].getSelectionIndex()
            lista = self['list'].list
            origen = str(answer[0])
            destino = str(answer[1])
            lalista = []
            conta = 0
            for i in range(len(lista)):
                valor1 = str(lista[i][0])
                valor2 = str(lista[i][2][7])
                if conta == idx:
                    lalista.append(IniciaSelListEntry(origen, destino))
                else:
                    lalista.append(IniciaSelListEntry(valor1, valor2))
                conta = conta + 1

            self.cambiado = True
            self['list'].setList(lalista)
            self['status'].setText(origen + destino + ' ' + _('Modified'))

    def anadir(self):
        lista = self['list'].list
        lista.append(IniciaSelListEntry('<' + _('Source channel') + '>', '--><' + _('Target channel') + '>'))
        self['list'].setList(lista)
        self['status'].setText(_('New entry') + ' ' + _('Added') + ' ' + str(len(lista)) + ' ' + _('equivalences'))
        self['list'].moveToIndex(len(lista) - 1)

    def salir(self):
        global listacanales
        listacanales = []
        self.close()

    def exitsave(self):
        if self.cambiado:
            laref = _('Save changes to equiv file?') + '\n' + _('By choosing NO all changes will be lost!')
            dei = self.session.openWithCallback(self.savefile, MessageBox, laref, MessageBox.TYPE_YESNO)
            dei.setTitle(_('Select equiv channels'))
        else:
            if self.oldService:
                self.session.nav.playService(self.oldService)
            self.salir()

    def savefile(self, answer):
        if self.oldService:
            self.session.nav.playService(self.oldService)
        if answer:
            lalista = self['list'].list
            try:
                newbooklist = open('/etc/mhw_Equiv.epg', 'w')
            except:
                dei = self.session.open(MessageBox, _('Error by writing equiv file !!!'), MessageBox.TYPE_ERROR)
                dei.setTitle(_('Select equiv channels'))

            newbooklist.write('#######################################################################\n')
            newbooklist.write('#\n')
            newbooklist.write('#  Channels Equivalences File for\n')
            newbooklist.write('#  mhw2 download by spaZeTeam(azboxhd.es)\n')
            newbooklist.write('#\n')
            newbooklist.write('#  First Field : Data for original Channel [SERVICE REFERENCE FORMAT]\n')
            newbooklist.write('#\n')
            newbooklist.write('#  Second Field: Data for equivalent Channel [SERVICE REFERENCE FORMAT]\n')
            newbooklist.write('#  Third field: [(Optional Channel name)].\n')
            newbooklist.write('#\n')
            newbooklist.write('#######################################################################\n')
            newbooklist.write('#\n')
            if newbooklist is not None:
                for i in range(len(lalista)):
                    valor1 = str(lalista[i][0])
                    valor2 = str(lalista[i][2][7])
                    if not valor1[0:1] == '<' and not valor2[0:1] == '<':
                        valor1 = nombrelista(valor1, True)
                        valor2 = nombrelista(valor2)
                        newbooklist.write(valor1 + ' ' + valor2 + '\n')

                newbooklist.close()
        self.salir()

    def buildList(self):
        nreg = cargalista()
        list = []
        booklist = None
        if fileExists('/etc/mhw_Equiv.epg'):
            try:
                booklist = open('/etc/mhw_Equiv.epg', 'r')
            except:
                dei = self.session.open(MessageBox, _('Error reading') + ' /etc/mhw_Equiv.epg!', MessageBox.TYPE_ERROR)
                dei.setTitle(_('Select equiv channels'))

            if booklist is not None:
                for oneline in booklist:
                    cadena = oneline[0:1]
                    if cadena == '1' or cadena == '2' or cadena == '3' or cadena == '4' or cadena == '5' or cadena == '6' or cadena == '7' or cadena == '8' or cadena == '9' or cadena == '0':
                        oneline2 = '' + ''.join(oneline.split(' (')[:-1]) + ''
                        nombre = '' + oneline.split(' (')[-1] + ''
                        origen = '' + ''.join(oneline2.split(' ')[:-1]) + ''
                        destino = oneline2.split(' ')[-1] + ' (' + nombre
                        origen = nombrelista2(origen)
                        destino = '-->' + nombrelista(destino)
                        list.append(IniciaSelListEntry(origen, destino))

                booklist.close()
        self['status'].setText(str(len(list)) + ' ' + _('equivalences') + ' :: ' + str(nreg) + ' ' + _('source channels'))
        self['list'].setList(list)

    def zap1(self):
        lalista = self['list'].list
        length = len(lalista)
        if length > 0:
            idx = self['list'].getSelectionIndex()
            servicetemp = str(lalista[idx][0])
            service = nombrelista(servicetemp, True)
            self['status'].setText(_('Zap to source') + ': ' + service)
            if service:
                self.session.nav.playService(eServiceReference(service))

    def zap2(self):
        lalista = self['list'].list
        length = len(lalista)
        if length > 0:
            idx = self['list'].getSelectionIndex()
            servicetemp = str(lalista[idx][2][7])
            service = nombrelista(servicetemp, True)
            self['status'].setText(_('Zap to target') + ': ' + service)
            if service:
                self.session.nav.playService(eServiceReference(service))

    def delete(self):
        lista = self['list'].list
        length = len(lista)
        if length > 0:
            self.cambiado = True
            idx = self['list'].getSelectionIndex()
            del lista[idx]
            self['list'].setList(lista)
            self['status'].setText(_('Entry') + ' ' + _('Deleted') + ' ' + str(len(lista)) + ' ' + _('equivalences'))
