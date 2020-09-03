from enigma import RT_HALIGN_LEFT, eListboxPythonMultiContent, gFont, BT_SCALE, BT_KEEP_ASPECT_RATIO
from Components.Label import Label
from Components.MenuList import MenuList
from Components.PluginComponent import plugins
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaBlend
from enigma import eListboxPythonMultiContent, gFont, getDesktop
from enigma import eTimer
from Components.Pixmap import Pixmap
from Tools.LoadPixmap import LoadPixmap
import keymapparser
from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Screens.ChoiceBox import ChoiceBox
from Components.ConfigList import ConfigListScreen
from Screens.MessageBox import MessageBox
from Screens.ParentalControlSetup import ProtectedScreen
from Screens.Standby import TryQuitMainloop
from Screens import Standby
from Components.ActionMap import ActionMap
from Components.Button import Button
from GlobalActions import globalActionMap
from Components.config import getConfigListEntry, ConfigYesNo, ConfigText, ConfigSelection, config, ConfigSubsection
from Tools import Notifications
from time import localtime, time, strftime
from Tools.Directories import fileExists, resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE, SCOPE_SKIN, SCOPE_SYSETC
from Components.Language import language
from os import environ
import os
import gettext
lang = language.getLanguage()
environ['LANGUAGE'] = lang[:2]
gettext.bindtextdomain('enigma2', resolveFilename(SCOPE_LANGUAGE))
gettext.textdomain('enigma2')
gettext.bindtextdomain('spazeMenu', '%s%s' % (resolveFilename(SCOPE_PLUGINS), 'Extensions/spazeMenu/locale/'))

def _(txt):
    t = gettext.dgettext('spazeMenu', txt)
    if t == txt:
        t = gettext.gettext(txt)
    return t


def esHD():
    if getDesktop(0).size().width() > 1400:
        return True
    else:
        return False


def fhd(num, factor = 1.5):
    if esHD():
        prod = num * factor
    else:
        prod = num
    return int(round(prod))


from os.path import isdir as esCarpeta

def devRutaSkin(rutacarpeta, rutaalternativa = '/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/'):
    nomskin = str(config.skin.primary_skin.value).split('/')[0]
    rutaSkin = resolveFilename(SCOPE_SKIN) + nomskin + '/' + rutacarpeta + '/'
    rutaSkin = rutaSkin.replace('//', '/')
    if esCarpeta(rutaSkin):
        return rutaSkin
    elif rutaalternativa == None:
        return
    else:
        return (rutaalternativa + '/' + rutacarpeta + '/').replace('//', '/')


def devrutaimagen(rutacarpeta):
    rutaret = devRutaSkin(rutacarpeta, None)
    if rutaret == None and esHD() and esCarpeta('/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/' + rutacarpeta + 'HD/'):
        rutaret = '/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/' + rutacarpeta + 'HD/'
    elif rutaret == None:
        rutaret = '/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/' + rutacarpeta + '/'
    return rutaret.replace('//', '/')


from Plugins.Extensions.spazeMenu.hardinfo import tipoModelo
MODELOSPZ = tipoModelo(False)
archivoXml = '/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/homemenu.xml'
config.plugins.spzMenu = ConfigSubsection()
config.plugins.spzMenu.showinmenu = ConfigYesNo(default=True)
VALOR_DEFECTO = 'home'
if MODELOSPZ == 'vuplus' or MODELOSPZ == 'golden':
    VALOR_DEFECTO = 'menu_long'
config.plugins.spzMenu.mapkey = ConfigSelection(default=VALOR_DEFECTO, choices=[('home', _('Key Home')),
 ('stop', _('Key Stop long')),
 ('help', _('Key Help')),
 ('menu_long', _('Key Menu long')),
 ('recordlist', _('Key RecordList')),
 ('radio', _('Key Radio')),
 ('tv', _('Key Tv')),
 ('none', _('Deactivate'))])
config.plugins.spzMenu.overwritemenu = ConfigYesNo(default=True)
config.plugins.spzMenu.showaudio = ConfigYesNo(default=True)
config.plugins.spzMenu.showrecord = ConfigYesNo(default=True)
config.plugins.spzMenu.showscaling = ConfigYesNo(default=True)
config.plugins.spzMenu.showhelpline = ConfigYesNo(default=True)
config.misc.spazeuseemc = ConfigYesNo(default=True)
config.misc.spazeupdates = ConfigYesNo(default=True)
config.misc.spazeclearram = ConfigYesNo(default=True)
config.misc.replacespzkeyboard = ConfigYesNo(default=True)

class boundFunction():

    def __init__(self, fnc, *args):
        self.fnc = fnc
        self.args = args

    def __call__(self):
        self.fnc(*self.args)


tmpPausedAnimation = False

def desactivaAnimaciones():
    global g_animation_paused
    global tmpPausedAnimation
    hayanimaciones = False
    try:
        from enigma import setAnimation_current
        setAnimation_current(0)
        hayanimaciones = True
        from Plugins.SystemPlugins.AnimationSetup.plugin import g_animation_paused
        tmpPausedAnimation = g_animation_paused
        g_animation_paused = True
        setAnimation_current(0)
    except:
        pass

    return hayanimaciones


def activaAnimaciones(hayanimaciones = True):
    global g_animation_paused
    if hayanimaciones:
        try:
            from enigma import setAnimation_current
            setAnimation_current(config.misc.window_animation_default.value)
            from Plugins.SystemPlugins.AnimationSetup.plugin import g_animation_paused
            g_animation_paused = tmpPausedAnimation
        except:
            pass


def VersionImagen():
    image_type = ''
    if True:
        file = open(resolveFilename(SCOPE_SYSETC, 'image-version'), 'r')
        lines = file.readlines()
        for x in lines:
            splitted = x.split('=')
            if splitted[0] == 'version':
                version = splitted[1]
                image_type = version[0].replace('\n', '')

        file.close()
    return image_type


PARABETATESTERS = False

def chequeaVersion():
    global PARABETATESTERS
    if not PARABETATESTERS:
        if False:
            PARABETATESTERS = True
        else:
            from __init__ import macs
            if len(macs) <= 8:
                PARABETATESTERS = True
                return True
            cmac = '0'
            try:
                carray = cargaosinfo('ifconfig eth0 | grep HWaddr')
                if 'HWaddr' not in carray:
                    carray = cargaosinfo('ifconfig | grep HWaddr')
                array = carray.split('HWaddr')
                if len(array) > 1:
                    cmac = array[1].replace(' ', '').replace('\n', '')
            except:
                pass

            if len(cmac) > 1 and '' + cmac in str(macs):
                print 'spazeimage: valid mac:[' + cmac + ']'
                PARABETATESTERS = True
            else:
                print 'spazeimage: NO VALID mac:[' + cmac + ']'
                PARABETATESTERS = False
    return PARABETATESTERS


baserunPlugin = None
PACKAGE_PATH = os.path.dirname(str(globals()['__file__']))
KEYMAPPINGS = {'home': os.path.join(PACKAGE_PATH, 'keymap-home.xml'),
 'stop': os.path.join(PACKAGE_PATH, 'keymap-stop.xml'),
 'help': os.path.join(PACKAGE_PATH, 'keymap-help.xml'),
 'menu_long': os.path.join(PACKAGE_PATH, 'keymap-menu_long.xml'),
 'recordlist': os.path.join(PACKAGE_PATH, 'keymap-recordlist.xml'),
 'radio': os.path.join(PACKAGE_PATH, 'keymap-radio.xml')}
cambiadalista = False
home_menu_sw = None
home_pulsado = None

class IniciaSelList(MenuList):

    def __init__(self, list, enableWrapAround = False):
        MenuList.__init__(self, list, enableWrapAround, eListboxPythonMultiContent)
        self.l.setItemHeight(80)
        self.l.setFont(0, gFont('Regular', 20))
        self.l.setFont(1, gFont('Regular', 16))


def IniciaSelListEntry(serviceName, eventName, numero = 0):
    res = [serviceName]
    if len(serviceName) > 18:
        serviceName = serviceName[:16] + '...'
    if numero < 0:
        numero = numero * -1
    laruta = devrutaimagen('iconosMenus')
    laimagen = laruta + 'ico' + str(numero) + '.png'
    if not fileExists(laimagen):
        laimagen = laruta + 'ico0.png'
    postexto = 4
    if fileExists(laimagen):
        png = LoadPixmap(laimagen)
        res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND,
         7,
         8,
         28,
         28,
         png))
        postexto = 35
    res.append(MultiContentEntryText(pos=(postexto, 6), size=(236, 24), font=0, text=serviceName))
    res.append(MultiContentEntryText(pos=(8, 33), size=(236, 48), font=1, text=eventName, color=10066329))
    return res


def guardaxml(lista = None):
    global archivoXml
    sourceEncoding = 'iso-8859-1'
    targetEncoding = 'utf-8'
    if lista == None:
        return False
    archivo = archivoXml
    target = open(archivo, 'w')
    target.write('<?xml version="1.0" encoding="UTF-8" ?>\n')
    target.write('<xml>\n')
    target.write('\t<homemenu>\n')
    for ij in range(0, len(lista)):
        if lista[ij][4] < 2:
            target.write('\t\t<content>\n')
            target.write('\t\t\t<texto>' + lista[ij][0] + '</texto>\n')
            target.write('\t\t\t<ayuda>' + lista[ij][1] + '</ayuda>\n')
            target.write('\t\t\t<visible>' + str(lista[ij][4]) + '</visible>\n')
            target.write('\t\t\t<accion>' + str(lista[ij][2]) + '</accion>\n')
            if str(lista[ij][2]) == '-1':
                codigo = str(lista[ij][3])
                arrcodigo = codigo.split('#x#')
                submenu = arrcodigo[0]
                ayudas = arrcodigo[1]
                acciones = arrcodigo[2]
                target.write('\t\t\t<submenu>' + submenu + '</submenu>\n')
                target.write('\t\t\t<submenuyuda>' + ayudas + '</submenuyuda>\n')
                target.write('\t\t\t<submenuacciones>' + acciones + '</submenuacciones>\n')
                target.write('\t\t\t<codigo></codigo>\n')
            else:
                target.write('\t\t\t<codigo>' + str(lista[ij][3]) + '</codigo>\n')
            target.write('\t\t</content>\n')

    target.write('\t</homemenu>\n')
    target.write('</xml>\n')
    target.close()
    return True


def devXml(cadena, etiqueta):
    tempcad = devStrTm(cadena, '<' + etiqueta + '>', '</' + etiqueta + '>')
    return tempcad


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


def cargaxml2(visibles = False):
    archivo = archivoXml
    texto = ayuda = accion = codigo = visible = submenus = ayudasub = accionessub = ''
    tempmenu = []
    ret = ''
    if fileExists(archivo):
        try:
            f = open(archivo, 'r')
            ret = f.read()
            f.close()
        except:
            return []

    arrmenu = ret.split('<content>')
    for ele in arrmenu:
        if '<texto>' in ele:
            texto = devXml(ele, 'texto')
            ayuda = devXml(ele, 'ayuda')
            accion = devXml(ele, 'accion')
            codigo = devXml(ele, 'codigo')
            visible = devXml(ele, 'visible')
            submenus = devXml(ele, 'submenu')
            ayudasub = devXml(ele, 'submenuyuda')
            accionessub = devXml(ele, 'submenuacciones')
            if accion == '44' and MODELOSPZ == 'vuplus' and fileExists('/usr/lib/enigma2/python/Plugins/Extensions/xbmc/plugin.pyo'):
                texto = 'XBMC'
            if int(visible) == 1 or visibles:
                if len(submenus) > 0:
                    codigo = submenus + '#x#' + ayudasub + '#x#' + accionessub
                if not accion == '-22' or config.plugins.spzMenu.overwritemenu.value:
                    if accion != '44' or accion == '44' and (fileExists('/usr/lib/enigma2/python/Plugins/Extensions/xbmc/plugin.pyo') and MODELOSPZ == 'vuplus' or fileExists('/usr/lib/enigma2/python/Plugins/Extensions/Kodi/plugin.pyo') and MODELOSPZ == 'vuplus' or fileExists('/usr/lib/enigma2/python/Plugins/Extensions/Kodi/plugin.pyo') and MODELOSPZ == 'formuler' or fileExists('/usr/lib/enigma2/python/Plugins/Extensions/StartKodi/plugin.pyo') and MODELOSPZ == 'wetek'):
                        tempmenu.append((_(texto),
                         _(ayuda),
                         int(accion),
                         codigo,
                         int(visible)))

    return tempmenu


class editaLista(ConfigListScreen, Screen):
    if esHD():
        skin = '\n\t\t\t<screen position="150,150" size="1425,615" title="%s"  zPosition="11">\n\t\t\t<widget name="config" position="0,5" size="1425,525" scrollbarMode="showOnDemand" itemHeight="42" />\n\n\t\t\t<widget name="key_red" position="0,532" size="180,60" valign="center" halign="center" backgroundColor="#000000" foregroundColor="#ffffff" zPosition="4" font="Regular;17" transparent="1"/> \n\t\t\t<widget name="key_green" position="210,532" size="180,60" valign="center" halign="center" backgroundColor="#000000" foregroundColor="#ffffff" zPosition="4" font="Regular;17" transparent="1"/>  \n\t\t\t<widget name="key_yellow" position="915,532" size="180,60" valign="center" halign="center" backgroundColor="#000000" foregroundColor="#ffffff" zPosition="4" font="Regular;17" transparent="1"/> \n\t\t\t<widget name="key_blue" position="1125,532" size="180,60" valign="center" halign="center" backgroundColor="#000000" foregroundColor="#ffffff" zPosition="4" font="Regular;17" transparent="1"/> \n\n\t\t\t<ePixmap name="red"    position="0,540"   zPosition="2" size="195,60" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/rednHD.png" transparent="1" alphatest="blend" />\n\t\t\t<ePixmap name="green"  position="210,540" zPosition="2" size="195,60" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/greennHD.png" transparent="1" alphatest="blend" />\n\t\t\t\n\t\t\t<ePixmap name="yellow"  position="915,540" zPosition="2" size="195,60" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/yellownHD.png" transparent="1" alphatest="blend" />\n\t\t\t<ePixmap name="blue"  position="1125,540" zPosition="2" size="195,60" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/bluenHD.png" transparent="1" alphatest="blend" />\n\n\t\t</screen>' % (_('openSPA Menu') + ' ' + _('Setup'))
    else:
        skin = '\n\t\t\t<screen position="100,100" size="950,410" title="%s"  zPosition="11">\n\t\t\t<widget name="config" position="0,0" size="950,350" scrollbarMode="showOnDemand" />\n\n\t\t\t<widget name="key_red" position="0,355" size="120,40" valign="center" halign="center" backgroundColor="#000000" foregroundColor="#ffffff" zPosition="4" font="Regular;17" transparent="1"/> \n\t\t\t<widget name="key_green" position="140,355" size="120,40" valign="center" halign="center" backgroundColor="#000000" foregroundColor="#ffffff" zPosition="4" font="Regular;17" transparent="1"/>  \n\t\t\t<widget name="key_yellow" position="610,355" size="120,40" valign="center" halign="center" backgroundColor="#000000" foregroundColor="#ffffff" zPosition="4" font="Regular;17" transparent="1"/> \n\t\t\t<widget name="key_blue" position="750,355" size="120,40" valign="center" halign="center" backgroundColor="#000000" foregroundColor="#ffffff" zPosition="4" font="Regular;17" transparent="1"/> \n\n\t\t\t<ePixmap name="red"    position="0,360"   zPosition="2" size="130,40" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/img/redn.png" transparent="1" alphatest="on" />\n\t\t\t<ePixmap name="green"  position="140,360" zPosition="2" size="130,40" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/img/greenn.png" transparent="1" alphatest="on" />\n\t\t\t\n\t\t\t<ePixmap name="yellow"  position="610,360" zPosition="2" size="130,40" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/img/yellown.png" transparent="1" alphatest="on" />\n\t\t\t<ePixmap name="blue"  position="750,360" zPosition="2" size="130,40" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/img/bluen.png" transparent="1" alphatest="on" />\n\n\t\t</screen>' % (_('openSPA Menu') + ' ' + _('Setup'))

    def __init__(self, session):
        self.session = session
        Screen.__init__(self, session)
        self.lista = cargaxml2(True)
        self.list = []
        self.needrestart = False
        self.cambiado = False
        for ij in range(0, len(self.lista)):
            defa = str(self.lista[ij][4])
            if self.lista[ij][2] == 0:
                self.list.append(getConfigListEntry(_(self.lista[ij][0]), ConfigSelection(default=defa, choices=[('1', _('Show')), ('0', _('Hide')), ('2', _('Delete'))]), self.lista[ij][1], self.lista[ij][2], self.lista[ij][3]))
            else:
                self.list.append(getConfigListEntry(_(self.lista[ij][0]), ConfigSelection(default=defa, choices=[('1', _('Show')), ('0', _('Hide'))]), self.lista[ij][1], self.lista[ij][2], self.lista[ij][3]))

        ConfigListScreen.__init__(self, self.list)
        self['key_red'] = Button(_('Add Extension'))
        self['key_green'] = Button(_('Options'))
        self['key_yellow'] = Button(_('Up'))
        self['key_blue'] = Button(_('Down'))
        self['setupActions'] = ActionMap(['WizardActions',
         'ColorActions',
         'DirectionActions',
         'NumberActions',
         'MenuActions'], {'ok': self.save,
         'red': self.add,
         'green': self.options,
         'blue': self.baja,
         'left': self.key_Left,
         'right': self.key_Right,
         'yellow': self.sube,
         'back': self.cancel}, -2)

    def getPluginsList(self, solomenu = False):
        unic = []
        twins = ['']
        if solomenu:
            pluginlist = plugins.getPlugins([PluginDescriptor.WHERE_PLUGINMENU])
        else:
            pluginlist = plugins.getPlugins([PluginDescriptor.WHERE_PLUGINMENU, PluginDescriptor.WHERE_EXTENSIONSMENU, PluginDescriptor.WHERE_EVENTINFO])
        pluginlist.sort(key=lambda p: p.name)
        conta = 0
        for plugin in pluginlist:
            conta = conta + 1
            if plugin.name in twins:
                pass
            else:
                descripcion = plugin.description
                if len(descripcion) > 26:
                    descripcion = descripcion[:26] + '\n' + descripcion[26:]
                if len(descripcion) > 53:
                    descripcion = descripcion[:50] + '...'
                unic.append((plugin.name, descripcion))
                twins.append(plugin.name)

        return unic

    def add(self):
        self.session.openWithCallback(self.PluginSelected, ChoiceBox, 'Plugins', self.getPluginsList())

    def PluginSelected(self, choice):
        if choice:
            for x in self['config'].list:
                if x[0] == choice[0]:
                    self.session.open(MessageBox, _('Entry %s already exists.') % x[0], type=MessageBox.TYPE_ERROR, timeout=5)
                    return

            self.cambiado = True
            self.list = self['config'].list
            self.list.append(getConfigListEntry(_(choice[0]), ConfigSelection(default='1', choices=[('1', _('Show')), ('0', _('Hide')), ('2', _('Delete'))]), choice[1], 0, choice[0]))
            self['config'].setList(self.list)
            self['config'].setCurrentIndex(len(self.list) - 1)

    def options(self):
        self.session.openWithCallback(self.vuelta, configuraspzmenu)

    def vuelta(self, respuesta):
        if respuesta:
            self.needrestart = True

    def sube(self):
        nuevalista = []
        conta = 0
        idx = self['config'].getCurrentIndex()
        if idx > 0:
            mover = self['config'].list[idx]
            for x in self['config'].list:
                if conta == idx - 1:
                    nuevalista.append(mover)
                if not conta == idx:
                    nuevalista.append(x)
                conta = conta + 1

            self.list = nuevalista
            self['config'].setList(self.list)
            self['config'].setCurrentIndex(idx - 1)
            self.cambiado = True

    def baja(self):
        nuevalista = []
        conta = 0
        idx = self['config'].getCurrentIndex()
        if idx < len(self['config'].list) - 1:
            mover = self['config'].list[idx]
            for x in self['config'].list:
                if not conta == idx:
                    nuevalista.append(x)
                if conta == idx + 1:
                    nuevalista.append(mover)
                conta = conta + 1

            self.list = nuevalista
            self['config'].setList(self.list)
            self['config'].setCurrentIndex(idx + 1)
            self.cambiado = True

    def key_Left(self):
        self.cambiado = True
        ConfigListScreen.keyLeft(self)

    def key_Right(self):
        self.cambiado = True
        ConfigListScreen.keyRight(self)

    def save(self):
        global cambiadalista
        cambiado = False
        conta = 0
        nuevalista = []
        for x in self['config'].list:
            visible = x[1].value
            texto = x[0]
            ayuda = x[2]
            accion = x[3]
            codigo = x[4]
            nuevalista.append((_(texto),
             _(ayuda),
             int(accion),
             codigo,
             int(visible)))
            conta = conta + 1

        cambiadalista = True
        guardaxml(nuevalista)
        if self.needrestart:
            laref = _('Restart GUI to apply changes?')
            dei = self.session.openWithCallback(self.reiniciar, MessageBox, laref, MessageBox.TYPE_YESNO)
        else:
            self.close()

    def reiniciar(self, respuesta):
        if respuesta:
            self.session.open(TryQuitMainloop, 3)
        else:
            self.close()

    def cancel(self):
        if self.cambiado:
            laref = _('List changed. Save this changes?')
            dei = self.session.openWithCallback(self.acambiado, MessageBox, laref, MessageBox.TYPE_YESNO)
        elif self.needrestart:
            laref = _('Restart GUI to apply changes?')
            dei = self.session.openWithCallback(self.reiniciar, MessageBox, laref, MessageBox.TYPE_YESNO)
        else:
            self.close()

    def acambiado(self, respuesta):
        if respuesta:
            self.save()
        else:
            self.close()


class configuraspzmenu(ConfigListScreen, Screen):
    if esHD():
        skin = '\n\t\t\t<screen position="150,150" size="1425,615" title="%s"  zPosition="11">\n\t\t\t<widget name="config" position="0,5" size="1425,390" scrollbarMode="showOnDemand" itemHeight="42" />\n\n\t\t\t<widget name="key_red" position="0,532" size="180,60" valign="center" halign="center" backgroundColor="#000000" foregroundColor="#ffffff" zPosition="4" font="Regular;17" transparent="1"/> \n\t\t\t<widget name="key_green" position="210,532" size="180,60" valign="center" halign="center" backgroundColor="#000000" foregroundColor="#ffffff" zPosition="4" font="Regular;17" transparent="1"/>  \n\t\t\t<widget name="key_blue" position="1125,532" size="180,60" valign="center" halign="center" backgroundColor="#000000" foregroundColor="#ffffff" zPosition="4" font="Regular;17" transparent="1"/> \n\t\t\t\n\t\t\t<ePixmap name="red"    position="0,540"   zPosition="2" size="195,60" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/rednHD.png" transparent="1" alphatest="on" />\n\t\t\t<ePixmap name="green"  position="210,540" zPosition="2" size="195,60" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/greennHD.png" transparent="1" alphatest="on" />\n\t\t\t<ePixmap name="blue"  position="1125,540" zPosition="2" size="195,60" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/bluenHD.png" transparent="1" alphatest="on" />\n\n\t\t</screen>' % (_('openSPA Menu') + ' ' + _('Setup'))
    else:
        skin = '\n\t\t\t<screen position="100,100" size="950,410" title="%s"  zPosition="11">\n\t\t\t<widget name="config" position="0,0" size="950,260" scrollbarMode="showOnDemand" />\n\n\t\t\t<widget name="key_red" position="0,355" size="120,40" valign="center" halign="center" backgroundColor="#000000" foregroundColor="#ffffff" zPosition="4" font="Regular;17" transparent="1"/> \n\t\t\t<widget name="key_green" position="140,355" size="120,40" valign="center" halign="center" backgroundColor="#000000" foregroundColor="#ffffff" zPosition="4" font="Regular;17" transparent="1"/>  \n\t\t\t<widget name="key_blue" position="750,355" size="120,40" valign="center" halign="center" backgroundColor="#000000" foregroundColor="#ffffff" zPosition="4" font="Regular;17" transparent="1"/> \n\t\t\t\n\t\t\t<ePixmap name="red"    position="0,360"   zPosition="2" size="130,40" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/img/redn.png" transparent="1" alphatest="on" />\n\t\t\t<ePixmap name="green"  position="140,360" zPosition="2" size="130,40" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/img/greenn.png" transparent="1" alphatest="on" />\n\t\t\t<ePixmap name="blue"  position="750,360" zPosition="2" size="130,40" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/img/bluen.png" transparent="1" alphatest="on" />\n\n\t\t</screen>' % (_('openSPA Menu') + ' ' + _('Setup'))

    def __init__(self, session):
        self.session = session
        Screen.__init__(self, session)
        self.list = []
        self.list.append(getConfigListEntry(_('Overwrite menu enigma with openSPA Menu'), config.plugins.spzMenu.overwritemenu, None, None))
        self.list.append(getConfigListEntry(_('Show Home Menu in main menu'), config.plugins.spzMenu.showinmenu, None, None))
        self.list.append(getConfigListEntry(_('Activate home menu with'), config.plugins.spzMenu.mapkey, None, None))
        self.list.append(getConfigListEntry(_('Show audio/subtitles in main menu'), config.plugins.spzMenu.showaudio, None, None))
        self.list.append(getConfigListEntry(_('Show record options in main menu'), config.plugins.spzMenu.showrecord, None, None))
        self.list.append(getConfigListEntry(_('Show scaling options in main menu'), config.plugins.spzMenu.showscaling, None, None))
        self.list.append(getConfigListEntry(_('Show help line in home menu'), config.plugins.spzMenu.showhelpline, None, None))
        ConfigListScreen.__init__(self, self.list)
        self['key_red'] = Button(_('Cancel'))
        self['key_green'] = Button(_('Save'))
        self['key_blue'] = Button(_('About'))
        self['setupActions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.save,
         'red': self.cancel,
         'green': self.save,
         'blue': self.about,
         'save': self.save,
         'cancel': self.cancel}, -2)

    def edita(self):
        pass

    def about(self):
        cmens = _('Home Menu') + ' ' + _('by openSPA') + ' 2012\n' + _('For azboxhd.es').replace('azboxhd.es', 'openspa.info')
        dei = self.session.open(MessageBox, cmens, MessageBox.TYPE_INFO)
        dei.setTitle(_('openSPA Menu'))

    def save(self):
        cambiado = False
        for x in self['config'].list:
            if x[1].isChanged():
                cambiado = True
                x[1].save()

        if cambiado:
            self.close(True)
        else:
            self.close(False)

    def cancel(self):
        for x in self['config'].list:
            x[1].cancel()

        self.close(False)


rutaimagen = devrutaimagen('iconosMenus')
from enigma import eSize, ePoint

class spazeTeamMenu(Screen, ProtectedScreen):
    if esHD():
        skin = '\n\t\t<screen name="spazeTeamMenu" position="0,8" size="1921,1081" title="Home Menu" zPosition="10" flags="wfNoBorder" backgroundColor="#ff000000">\n\t\t\t<widget name="seleccion" position="91,979" size="192,175" zPosition="0" transparent="0" alphatest="blend" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/image/nm_sel-fs8.png" />\n\t\t\t<ePixmap position="333,891" size="24,39" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/image/nm_left-fs8.png" alphatest="blend" />\n\t\t\t<ePixmap position="1800,891" size="24,39" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/image/nm_right-fs8.png" alphatest="blend" />\n\t\t\t<widget name="estado" position="309,1002" zPosition="1" size="1545,30" font="Regular;16" valign="center" halign="center" transparent="1" foregroundColor="#9999aa" backgroundColor="#000000"/>\n\t\t\t<widget name="estado2" position="103,1002" zPosition="1" size="150,30" font="Regular;18" valign="center" halign="right" transparent="1" foregroundColor="#888899" backgroundColor="#000000" shadowColor="#000000" shadowOffset="-1,-1" />\n \n\t\t\t<eLabel name="fondo" position="1,822" size="1920,258" zPosition="-5" backgroundColor="#20000010" />\n\t\t\t<widget name="imagen1" position="379,837" size="192,175" alphatest="blend" zPosition="5" />\n\t\t\t<widget name="texto1" position="379,958" size="192,30" halign="center" transparent="1" backgroundColor="#000000" shadowColor="#000000" shadowOffset="-1,-1" zPosition="6" font="Regular;16"  foregroundColor="#00ffffff" />\n\t\t\t<widget name="imagen2" position="582,837" size="192,175" alphatest="blend" zPosition="5" />\n\t\t\t<widget name="texto2" position="582,958" size="192,30" halign="center" transparent="1" backgroundColor="#000000" shadowColor="#000000" shadowOffset="-1,-1" zPosition="6" font="Regular;16" foregroundColor="#00ffffff"/>\n\t\t\t<widget name="imagen3" position="784,837" size="192,175" alphatest="blend" zPosition="5" />\n\t\t\t<widget name="texto3" position="784,958" size="192,30" halign="center" transparent="1" backgroundColor="#000000" shadowColor="#000000" shadowOffset="-1,-1" zPosition="6" font="Regular;16" foregroundColor="#00ffffff"/>\n\t\t\t<widget name="imagen4" position="987,837" size="192,175" alphatest="blend" zPosition="5" />\n\t\t\t<widget name="texto4" position="987,958" size="192,30" halign="center" transparent="1" backgroundColor="#000000" shadowColor="#000000" shadowOffset="-1,-1" zPosition="6" font="Regular;16" foregroundColor="#00ffffff"/>\n\t\t\t<widget name="imagen5" position="1189,837" size="192,175" alphatest="blend" zPosition="5" />\n\t\t\t<widget name="texto5" position="1189,958" size="192,30" halign="center" transparent="1" backgroundColor="#000000" shadowColor="#000000" shadowOffset="-1,-1" zPosition="6" font="Regular;16" foregroundColor="#00ffffff"/>\n\t\t\t<widget name="imagen6" position="1392,837" size="192,175" alphatest="blend" zPosition="5" />\n\t\t\t<widget name="texto6" position="1392,958" size="192,30" halign="center" transparent="1" backgroundColor="#000000" shadowColor="#000000" shadowOffset="-1,-1" zPosition="6" font="Regular;16" foregroundColor="#00ffffff"/>\n\t\t\t<widget name="imagen7" position="1594,837" size="192,175" alphatest="blend" zPosition="5" />\n\t\t\t<widget name="texto7" position="1594,958" size="192,30" halign="center" transparent="1" backgroundColor="#000000" shadowColor="#000000" shadowOffset="-1,-1" zPosition="6" font="Regular;16" foregroundColor="#00ffffff"/>\n \n\t\t\t<widget source="global.CurrentTime" render="Label" position="73,832" size="142,42" font="Regular;26" valign="top" halign="right" backgroundColor="#000000" transparent="1" shadowColor="#000000" shadowOffset="-1,-1">\n \t\t\t  <convert type="ClockToText">Default</convert>\n \t\t\t</widget>\n\t\t\t<widget source="global.CurrentTime" render="Label" position="214,837" size="69,30" font="Regular;18" valign="top" halign="left" backgroundColor="#000000" transparent="1" shadowColor="#000000" shadowOffset="-1,-1">\n \t\t\t  <convert type="ClockToText">Format::%S</convert>\n \t\t\t</widget>\n\t\t\t<eLabel name="linea" position="283,823" size="1,256" zPosition="-4" backgroundColor="#10101020" />\n\t\t</screen>'
    else:
        skin = '\n\t\t\t<screen name="spazeTeamMenu" position="0,8" size="1281,721" title="Home Menu" zPosition="10" flags="wfNoBorder" backgroundColor="#ff000000">\n\t\t\t<widget name="seleccion" position="61,653" size="128,117" zPosition="0" transparent="0" alphatest="blend" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/image/nm_sel-fs8.png" />\n\t\t\t<ePixmap position="222,594" size="16,26" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/image/nm_left-fs8.png" alphatest="blend" />\n\t\t\t<ePixmap position="1200,594" size="16,26" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/image/nm_right-fs8.png" alphatest="blend" />\n\t\t\t<widget name="estado" position="206,668" zPosition="1" size="1030,20" font="Regular;16" valign="center" halign="center" transparent="1" foregroundColor="#9999aa" backgroundColor="#000000"/>\n\t\t\t<widget name="estado2" position="69,668" zPosition="1" size="100,20" font="Regular;18" valign="center" halign="right" transparent="1" foregroundColor="#888899" backgroundColor="#000000" shadowColor="#000000" shadowOffset="-1,-1" />\n\n\t\t\t<eLabel name="fondo" position="1,548" size="1280,172" zPosition="-5" backgroundColor="#20000010" />\n\t\t\t<widget name="imagen1" position="253,558" size="128,117" alphatest="blend" zPosition="5" />\n\t\t\t<widget name="texto1" position="253,639" size="128,20" halign="center" transparent="1" backgroundColor="#000000" shadowColor="#000000" shadowOffset="-1,-1" zPosition="6" font="Regular;16"  foregroundColor="#00ffffff" />\n\t\t\t<widget name="imagen2" position="388,558" size="128,117" alphatest="blend" zPosition="5" />\n\t\t\t<widget name="texto2" position="388,639" size="128,20" halign="center" transparent="1" backgroundColor="#000000" shadowColor="#000000" shadowOffset="-1,-1" zPosition="6" font="Regular;16" foregroundColor="#00ffffff"/>\n\t\t\t<widget name="imagen3" position="523,558" size="128,117" alphatest="blend" zPosition="5" />\n\t\t\t<widget name="texto3" position="523,639" size="128,20" halign="center" transparent="1" backgroundColor="#000000" shadowColor="#000000" shadowOffset="-1,-1" zPosition="6" font="Regular;16" foregroundColor="#00ffffff"/>\n\t\t\t<widget name="imagen4" position="658,558" size="128,117" alphatest="blend" zPosition="5" />\n\t\t\t<widget name="texto4" position="658,639" size="128,20" halign="center" transparent="1" backgroundColor="#000000" shadowColor="#000000" shadowOffset="-1,-1" zPosition="6" font="Regular;16" foregroundColor="#00ffffff"/>\n\t\t\t<widget name="imagen5" position="793,558" size="128,117" alphatest="blend" zPosition="5" />\n\t\t\t<widget name="texto5" position="793,639" size="128,20" halign="center" transparent="1" backgroundColor="#000000" shadowColor="#000000" shadowOffset="-1,-1" zPosition="6" font="Regular;16" foregroundColor="#00ffffff"/>\n\t\t\t<widget name="imagen6" position="928,558" size="128,117" alphatest="blend" zPosition="5" />\n\t\t\t<widget name="texto6" position="928,639" size="128,20" halign="center" transparent="1" backgroundColor="#000000" shadowColor="#000000" shadowOffset="-1,-1" zPosition="6" font="Regular;16" foregroundColor="#00ffffff"/>\n\t\t\t<widget name="imagen7" position="1063,558" size="128,117" alphatest="blend" zPosition="5" />\n\t\t\t<widget name="texto7" position="1063,639" size="128,20" halign="center" transparent="1" backgroundColor="#000000" shadowColor="#000000" shadowOffset="-1,-1" zPosition="6" font="Regular;16" foregroundColor="#00ffffff"/>\n\n\t\t\t<widget source="global.CurrentTime" render="Label" position="49,555" size="95,28" font="Regular;26" valign="top" halign="right" backgroundColor="#000000" transparent="1" shadowColor="#000000" shadowOffset="-1,-1">\n\t\t\t  <convert type="ClockToText">Default</convert>\n\t\t\t</widget>\n\t\t\t<widget source="global.CurrentTime" render="Label" position="143,558" size="46,20" font="Regular;18" valign="top" halign="left" backgroundColor="#000000" transparent="1" shadowColor="#000000" shadowOffset="-1,-1">\n\t\t\t  <convert type="ClockToText">Format::%S</convert>\n\t\t\t</widget>\n\t\t\t<eLabel name="linea" position="189,549" size="1,171" zPosition="-4" backgroundColor="#10101020" />\n\t\t</screen>'

    def __init__(self, session, args = 0):
        global archivoXml
        archivoXml = '/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/homemenu.xml'
        self.session = session
        self.modoayuda = False
        Screen.__init__(self, session)
        ProtectedScreen.__init__(self)
        self.skin = spazeTeamMenu.skin
        self.servicelist = None
        try:
            from Screens.InfoBar import InfoBar
            if InfoBar and InfoBar.instance:
                self.servicelist = InfoBar.instance.servicelist
        except:
            self.servicelist = None

        self.listaMenus = cargaxml2()
        self.listapluginsmenu = []
        self.mostrado = False
        self.ventanaactiva = session.current_dialog
        self.ventanas = ''
        self.ventanas = str(session.dialog_stack)
        self.menuactivo = 1
        self.maxentry = len(self.listaMenus)
        self.actual = 2
        self.maxpantalla = 7
        if self.maxpantalla > self.maxentry:
            self.maxpantalla = self.maxentry
        self['imagen1'] = Pixmap()
        self['imagen2'] = Pixmap()
        self['imagen3'] = Pixmap()
        self['imagen4'] = Pixmap()
        self['imagen5'] = Pixmap()
        self['imagen6'] = Pixmap()
        self['imagen7'] = Pixmap()
        self['seleccion'] = Pixmap()
        self['texto1'] = Label()
        self['texto2'] = Label()
        self['texto3'] = Label()
        self['texto4'] = Label()
        self['texto5'] = Label()
        self['texto6'] = Label()
        self['texto7'] = Label()
        try:
            self['texto1p'] = Label()
            self['texto2p'] = Label()
            self['texto3p'] = Label()
            self['texto4p'] = Label()
            self['texto5p'] = Label()
            self['texto6p'] = Label()
            self['texto7p'] = Label()
        except:
            pass

        self['estado2'] = Label()
        self['estado'] = Label('1/' + str(self.maxentry))
        self['setupActions'] = ActionMap(['GlobalActions',
         'WizardActions',
         'DirectionActions',
         'ColorActions',
         'NumberActions',
         'MenuActions',
         'EPGSelectActions',
         'InfobarActions'], {'yellow': self.ira,
         'red': self.cambia,
         'back': self.n_exit,
         'home': self.exit,
         'ok': self.n_ok,
         'left': self.n_key_left,
         'right': self.n_key_right,
         'up': self.n_key_up,
         'down': self.n_key_down,
         'info': self.key_info,
         'menu': self.key_menu,
         'MostrarMenuHome': self.exit,
         'power_down': self.apagar,
         'power_up': self.apagar}, -2)
        self.SUBMENUdialog = None
        self.activadalista = False
        self.TimerClose = eTimer()
        self.timerMenu = eTimer()
        self.iniciado = False
        self.scrSpz = False
        self.TimerTemp = eTimer()
        self.timerMenu.callback.append(self.mostrar_sub)
        self.TimerClose.callback.append(self.exit)
        self.onLayoutFinish.append(self.buildList)
        self.onShow.append(self.mostrar)
        self.nombredes = ''
        self.hayiconos = True

    def apagar(self):
        Notifications.AddNotification(Standby.Standby)
        self.exit()

    def cambia(self):
        self.scrSpz = not self.scrSpz

    def pontitulo(self, texto):
        self.setTitle(texto + ' - ' + _('Menu'))

    def n_key_left(self):
        self.timerMenu.stop()
        self.key_left()
        accionMenu = self.listaMenus[self.menuactivo - 1][2]
        self.pontitulo(self.listaMenus[self.menuactivo - 1][0])
        if accionMenu < 0 and self.SUBMENUdialog == None:
            self.timerMenu.start(1000, True)

    def n_key_right(self):
        self.timerMenu.stop()
        self.key_right()
        accionMenu = self.listaMenus[self.menuactivo - 1][2]
        self.pontitulo(self.listaMenus[self.menuactivo - 1][0])
        if accionMenu < 0 and self.SUBMENUdialog == None:
            self.timerMenu.start(1000, True)

    def mostrar_sub(self):
        self.timerMenu.stop()
        self.activadalista = False
        accionMenu = self.listaMenus[self.menuactivo - 1][2]
        if accionMenu < 0 and self.SUBMENUdialog == None:
            self.activadalista = True
            self.runMenu()

    def n_ok(self):
        self.timerMenu.stop()
        if not self.SUBMENUdialog == None:
            self.devSub()
        else:
            self.activadalista = True
            self.runMenu()

    def pontitulosub(self):
        try:
            if self.activadalista:
                lalista = self.SUBMENUdialog['lista'].list
                idx = self.SUBMENUdialog['lista'].getSelectionIndex()
                valormenu = str(lalista[idx][1][7])
                self.setTitle(valormenu + ' - ' + self.listaMenus[self.menuactivo - 1][0])
        except:
            pass

    def fnombredes(self, nom):
        cret = nom.replace('Extensions/spazeMenu/spzPlugins/', _('openSPA Plugins/'))
        cret = cret.replace('Extensions/', _('Extensions') + '/')
        cret = cret.replace('SystemPlugins/', _('SystemPlugins') + '/')
        cret = cret.replace('.tar.gz.back', '')
        return cret

    def desactivadoPlugin(self, rutaplugin):
        nombreplugin = '/usr/lib/enigma2/python/' + rutaplugin.replace('.', '/') + '.pyo'
        if not fileExists(nombreplugin):
            nombredes = nombreplugin.split('/')[-1]
            rutades = nombreplugin.replace('/' + nombredes, '')
            self.nombredes = rutades.replace('/usr/lib/enigma2/python/Plugins/', '')
            if fileExists(rutades + '.tar.gz.back'):
                laref = 'Plugin [' + self.fnombredes(self.nombredes) + ']\n' + _('This plugin are deactivated.\n Do you want go to Plugin Manager for active it?')
                dei = self.session.openWithCallback(self.cbdes, MessageBox, laref, MessageBox.TYPE_YESNO)
                dei.setTitle(_('Deactivated Plugin'))
                return True
            else:
                laref = '[' + self.fnombredes(self.nombredes) + '] ' + _('This plugin is not installed.\n You want to access the OpenSPA Extra Plugins Manager to install it?')
                dei = self.session.openWithCallback(self.cbdw, MessageBox, laref, MessageBox.TYPE_YESNO)
                dei.setTitle(_('Download Plugin') + '[' + self.fnombredes(self.nombredes) + '] ')
                return True
        return False

    def cbdw(self, respuesta = None):
        if respuesta:
            self.cierraSub()
            try:
                from Plugins.Extensions.OpenSPAPlug.plugin import OpenSPAPlug
                from Screens.InfoBar import InfoBar
                InfoBar.instance.session.openWithCallback(self.comprueba, OpenSPAPlug)
            except:
                pass

    def comprueba(self, retval = True):
        pass

    def cbdes(self, respuesta = None):
        if respuesta:
            self.cierraSub()
            try:
                from Plugins.Extensions.spazeMenu.spzPlugins.gesPluginsOpenSpa.plugin import gesPlugins
                from Screens.InfoBar import InfoBar
                InfoBar.instance.session.open(gesPlugins, inicial=self.nombredes)
            except:
                pass

    def devSub(self):
        if not self.SUBMENUdialog == None:
            if not self.activadalista:
                self.SUBMENUdialog['lista'].selectionEnabled(1)
                self.SUBMENUdialog['lista'].moveToIndex(len(self.SUBMENUdialog['lista'].list) - 1)
                self.pontitulosub()
                self.activadalista = True
                return
            cmens = 'NA'
            lalista = self.SUBMENUdialog['lista'].list
            idx = self.SUBMENUdialog['lista'].getSelectionIndex()
            valormenu = str(lalista[idx][0])
            sierror = False
            self.cierraSub()
            if valormenu == '11':
                if self.desactivadoPlugin('Plugins.Extensions.spazeMenu.spzPlugins.descargasSPZ.plugin'):
                    return
                try:
                    from Plugins.Extensions.spazeMenu.spzPlugins.descargasSPZ.plugin import main
                    main(self.session)
                except:
                    sierror = True

            elif valormenu == '70':
                if self.desactivadoPlugin('Plugins.Extensions.MediaCenter.MC_VideoPlayer'):
                    return
                try:
                    from Plugins.Extensions.MediaCenter.MC_VideoPlayer import MC_VideoPlayer
                    from Screens.InfoBar import InfoBar
                    InfoBar.instance.session.open(MC_VideoPlayer)
                except:
                    sierror = True

            elif valormenu == '71':
                if self.desactivadoPlugin('Plugins.Extensions.MediaCenter.MC_AudioPlayer'):
                    return
                try:
                    from Plugins.Extensions.MediaCenter.MC_AudioPlayer import MC_AudioPlayer
                    from Screens.InfoBar import InfoBar
                    InfoBar.instance.session.open(MC_AudioPlayer)
                except:
                    sierror = True

            elif valormenu == '72':
                if self.desactivadoPlugin('Plugins.Extensions.PicturePlayer.plugin'):
                    return
                try:
                    from Plugins.Extensions.PicturePlayer.plugin import main
                    from Screens.InfoBar import InfoBar
                    main(InfoBar.instance.session)
                except:
                    sierror = True

            elif valormenu == '80':
                try:
                    from Screens.InfoBar import InfoBar
                    from Screens.PluginBrowser import PluginBrowser
                    InfoBar.instance.session.open(PluginBrowser)
                except:
                    pass

            elif valormenu == '88':
                try:
                    from Screens.InfoBar import InfoBar
                    if InfoBar and InfoBar.instance:
                        InfoBar.startTeletext(InfoBar.instance)
                except:
                    pass

            elif valormenu == '81':
                try:
                    from Screens.Menu import MainMenu
                    import xml.etree.cElementTree
                    xmdom = xml.etree.cElementTree.parse(resolveFilename(SCOPE_SKIN, 'menu.xml'))
                    root = xmdom.getroot()
                    for x in root.findall('menu'):
                        y = x.find('id')
                        if y is not None:
                            id = y.get('val')
                            if id and id == 'shutdown':
                                self.session.infobar = self
                                menu_screen = self.session.openWithCallback(self.MenuClosed, MainMenu, x)
                                menu_screen.setTitle(_('Standby / Restart'))

                except:
                    sierror = True

            elif '99_' in valormenu:
                numero = int(valormenu.split('_')[1])
                selection = self.listapluginsmenu[numero]
                try:
                    if selection is not None:
                        selection[1]()
                except:
                    sierror = True

            elif valormenu == '1':
                from Screens.InfoBar import InfoBar
                if InfoBar and InfoBar.instance:
                    InfoBar.showTv(InfoBar.instance)
            elif valormenu == '7':
                from Screens.InfoBar import InfoBar
                if InfoBar and InfoBar.instance:
                    InfoBar.showRadio(InfoBar.instance)
            elif valormenu == '90':
                from Screens.InfoBar import InfoBar
                if InfoBar and InfoBar.instance:
                    set_audio(InfoBar.instance.session)
            elif valormenu == '91':
                from Screens.InfoBar import InfoBar
                if InfoBar and InfoBar.instance:
                    set_scaling(InfoBar.instance.session)
            elif valormenu == '92':
                try:
                    from Screens.TimerEdit import TimerEditList
                    from Screens.InfoBar import InfoBar
                    if InfoBar and InfoBar.instance:
                        InfoBar.instance.session.open(TimerEditList)
                except:
                    sierror = True

            elif valormenu == '93':
                from Screens.InfoBar import InfoBar
                if InfoBar and InfoBar.instance:
                    set_record(InfoBar.instance.session)
            elif valormenu == '94':
                try:
                    from Screens.InfoBar import InfoBar
                    if InfoBar and InfoBar.instance:
                        servicelist = InfoBar.instance.servicelist
                    from Plugins.Extensions.spazeMenu.spzPlugins.openSPATVGuide.plugin import main
                    main(self.session, servicelist)
                except:
                    sierror = True

            elif valormenu == '5':
                if self.desactivadoPlugin('Plugins.Extensions.spazeMenu.spzPlugins.AzExplorer.plugin'):
                    return
                try:
                    from Plugins.Extensions.spazeMenu.spzPlugins.AzExplorer.plugin import main
                    main(self.session)
                except:
                    sierror = True

            elif valormenu == '13':
                if self.desactivadoPlugin('Plugins.Extensions.spazeMenu.spzPlugins.spzBackups.plugin'):
                    return
                try:
                    from Plugins.Extensions.spazeMenu.spzPlugins.spzBackups.plugin import mainHome
                    mainHome(self.session)
                except:
                    sierror = True

            elif valormenu == '37':
                if self.desactivadoPlugin('Plugins.Extensions.spazeMenu.spzPlugins.gesPluginsOpenSpa.plugin'):
                    return
                try:
                    from Plugins.Extensions.spazeMenu.spzPlugins.gesPluginsOpenSpa.plugin import main
                    main(self.session)
                except:
                    sierror = True

            elif valormenu == '38':
                if self.desactivadoPlugin('Plugins.Extensions.OpenSPAPlug.plugin'):
                    return
                try:
                    from Plugins.Extensions.OpenSPAPlug.plugin import startConfig
                    startConfig(self.session)
                except:
                    sierror = True

            elif valormenu == '33':
                if self.desactivadoPlugin('Plugins.Extensions.spazeMenu.spzPlugins.spzCAMD.plugin'):
                    return
                try:
                    from Plugins.Extensions.spazeMenu.spzPlugins.spzCAMD.plugin import startConfig
                    startConfig(self.session)
                except:
                    sierror = True

            elif valormenu == '34':
                if self.desactivadoPlugin('Plugins.SystemPlugins.DeviceManager.plugin'):
                    return
                try:
                    from Plugins.SystemPlugins.DeviceManager.plugin import DeviceManagerMain
                    DeviceManagerMain(self.session)
                except:
                    sierror = True

                if sierror:
                    try:
                        from Plugins.SystemPlugins.DeviceManager.plugin import deviceManagerMain
                        deviceManagerMain(self.session)
                        sierror = False
                    except:
                        sierror = True

            elif valormenu == '61':
                if self.desactivadoPlugin('Plugins.Extensions.spaQButton.plugin'):
                    return
                try:
                    from Plugins.Extensions.spaQButton.spaQButton import spaQButton
                    from Screens.InfoBar import InfoBar
                    if InfoBar and InfoBar.instance:
                        InfoBar.instance.session.open(spaQButton, mostrarayuda=True)
                except Exception as e:
                    dei = self.session.open(MessageBox, 'Error ' + e.message, MessageBox.TYPE_INFO)
                    sierror = True

            elif valormenu == '8':
                if self.desactivadoPlugin('Plugins.Extensions.spazeMenu.spzPlugins.azHelp.plugin'):
                    return
                try:
                    from Plugins.Extensions.spazeMenu.spzPlugins.azHelp.plugin import azFaqs
                    self.session.open(azFaqs)
                except Exception as e:
                    sierror = True

            elif valormenu == '9':
                try:
                    from Screens.Menu import MainMenu
                    import xml.etree.cElementTree
                    xmdom = xml.etree.cElementTree.parse(resolveFilename(SCOPE_SKIN, 'menu.xml'))
                    root = xmdom.getroot()
                    for x in root.findall('menu'):
                        y = x.find('id')
                        if y is not None:
                            id = y.get('val')
                            if id and id == 'setup':
                                self.session.infobar = self
                                menu_screen = self.session.openWithCallback(self.MenuClosed, MainMenu, x)
                                menu_screen.setTitle(_('Setup'))

                except:
                    sierror = True

            elif valormenu == '40':
                try:
                    from Plugins.Extensions.spazeMenu.spzPlugins.spzOptions.plugin import mainOptions
                    mainOptions(self.session)
                except:
                    sierror = True

            elif valormenu == '41':
                if self.desactivadoPlugin('Plugins.Extensions.spaQButton.plugin'):
                    return
                try:
                    from Plugins.Extensions.spaQButton.plugin import main
                    main(self.session)
                except:
                    sierror = True

            elif valormenu == '42':
                self.edita_menu()
            elif valormenu == '2':
                if self.desactivadoPlugin('Plugins.Extensions.MyTube.plugin'):
                    return
                haymedia = False
                if not haymedia:
                    try:
                        from Plugins.Extensions.MyTube.plugin import MyTubeMain
                        MyTubeMain(self.session)
                    except:
                        pass

            elif valormenu == '6':
                self.TimerClose.stop()
                runExtensiones()
                cerrar = False
            elif valormenu == '10':
                if self.desactivadoPlugin('Plugins.Extensions.spazeMenu.spzPlugins.InfoAz.plugin'):
                    return
                try:
                    from Plugins.Extensions.spazeMenu.spzPlugins.InfoAz.plugin import iniciainfo
                    iniciainfo(self.session)
                except:
                    pass

            elif valormenu == '12':
                if self.desactivadoPlugin('Plugins.Extensions.spazeMenu.spzPlugins.spzSimpleRSS.plugin'):
                    return
                sierror = False
                try:
                    from Plugins.Extensions.spazeMenu.spzPlugins.spzSimpleRSS.plugin import main
                    main(self.session)
                    cerrar = False
                except:
                    sierror = True

            elif valormenu == '14':
                if self.desactivadoPlugin('Plugins.Extensions.spzWeather.plugin'):
                    return
                try:
                    from Plugins.Extensions.spzWeather.plugin import main
                    main(self.session)
                except:
                    pass

            elif valormenu == '15':
                if self.desactivadoPlugin('Plugins.Extensions.TVweb.plugin'):
                    return
                try:
                    from Plugins.Extensions.TVweb.plugin import main
                    main(self.session)
                except:
                    pass

            elif valormenu == '50':
                if self.desactivadoPlugin('Plugins.Extensions.spazeMenu.spzPlugins.mhw2Timer.plugin'):
                    return
                try:
                    from Plugins.Extensions.spazeMenu.spzPlugins.mhw2Timer.plugin import main
                    main(self.session)
                except:
                    sierror = True

            else:
                sierror = True
            if sierror:
                cmens = _('Program not found for menu item ') + valormenu + '\n' + _('It is possible that the program has been deleted or is disabled.')
                dei = self.session.open(MessageBox, cmens, MessageBox.TYPE_ERROR, timeout=10)
                dei.setTitle(_('openSPA Menu'))
            self.cierraSub()

    def n_key_up(self):
        if not self.SUBMENUdialog == None:
            try:
                if not self.activadalista:
                    self.SUBMENUdialog['lista'].selectionEnabled(1)
                    self.SUBMENUdialog['lista'].moveToIndex(len(self.SUBMENUdialog['lista'].list) - 1)
                    self.activadalista = True
                elif self.SUBMENUdialog['lista'].getSelectionIndex() == 0:
                    self.SUBMENUdialog['lista'].moveToIndex(len(self.SUBMENUdialog['lista'].list) - 1)
                else:
                    self.SUBMENUdialog['lista'].up()
            except:
                pass

            self.pontitulosub()
            self.autoclose()
        else:
            self.key_up()

    def n_key_down(self):
        if not self.SUBMENUdialog == None:
            try:
                if not self.activadalista:
                    self.SUBMENUdialog['lista'].selectionEnabled(1)
                    self.SUBMENUdialog['lista'].moveToIndex(0)
                    self.activadalista = True
                elif self.SUBMENUdialog['lista'].getSelectionIndex() == len(self.SUBMENUdialog['lista'].list) - 1:
                    self.SUBMENUdialog['lista'].moveToIndex(0)
                else:
                    self.SUBMENUdialog['lista'].down()
            except:
                pass

            self.pontitulosub()
            self.autoclose()
        else:
            self.key_down()

    def n_exit(self):
        if not self.SUBMENUdialog == None:
            self.cierraSub()
        else:
            self.exit()

    def cierraSub(self):
        self.pontitulo(self.listaMenus[self.menuactivo - 1][0])
        self.activadalista = False
        if not self.SUBMENUdialog == None:
            try:
                self.SUBMENUdialog.TimerAnima.stop()
                self.session.deleteDialog(self.SUBMENUdialog)
                self.activadalista = False
                self.SUBMENUdialog = None
            except Exception as e:
                dei = self.session.open(MessageBox, 'Error ' + e.message, MessageBox.TYPE_INFO)
                self.SUBMENUdialog = None

    def autoclose(self):
        self.TimerClose.stop()
        self.TimerClose.startLongTimer(16)

    def anadeLista(self, numero, texto, info, naccion):
        global rutaimagen
        self['texto' + numero].setText(texto)
        try:
            self['texto' + numero + 'p'].setText(texto)
        except:
            pass

        if naccion < 0:
            naccion = naccion * -1
        if self.hayiconos:
            icono = rutaimagen + 'nm_' + str(naccion) + '-fs8.png'
            if not fileExists(icono):
                icono = rutaimagen + 'nm_0-fs8.png'
            if fileExists(icono):
                self['imagen' + numero].instance.setPixmapFromFile(icono)
                if esHD():
                    self['imagen' + numero].instance.setScale(1)
                else:
                    self['imagen' + numero].instance.setScale(0)

    def mostrar(self):
        global cambiadalista
        if 'spazeTeamMenu' in str(self.ventanaactiva):
            self.close()
        else:
            if self.modoayuda:
                if not self.mostrado:
                    self.mostrado = True
                    return
                self.close()
            if cambiadalista:
                cambiadalista = False
                self.listaMenus = cargaxml2()
                self.menuactivo = 1
                self.maxentry = len(self.listaMenus)
                self.actual = 2
                self.maxpantalla = 7
                if self.maxpantalla > self.maxentry:
                    self.maxpantalla = self.maxentry
                self.buildList()
            if not self.iniciado:
                self.iniciado = True
                self.timerMenu.stop()
                accionMenu = self.listaMenus[self.menuactivo - 1][2]
                if accionMenu < 0 and self.SUBMENUdialog == None:
                    self.timerMenu.start(1100, True)
        self.autoclose()
        self.pontitulo(self.listaMenus[self.menuactivo - 1][0])

    def buildList(self):
        if self['imagen1'].instance.size().height() == 1 and self['imagen1'].instance.size().width() == 1:
            self.hayiconos = False
        if self.modoayuda:
            pass
        else:
            if config.plugins.spzMenu.showhelpline.value:
                self['estado'].show()
            else:
                self['estado'].hide()
            inicio = self.actual
            activa = self.menuactivo
            ainicio = self.menuactivo - inicio
            if ainicio < 0:
                ainicio = self.maxentry - (inicio - self.menuactivo)
            try:
                cret = self.anadeLista('1', self.listaMenus[ainicio][0], self.listaMenus[ainicio][1], self.listaMenus[ainicio][2])
            except:
                pass

            valorinicio = self.menuactivo - inicio + 1
            for i in range(2, self.maxpantalla + 1):
                cret = self.anadeLista(str(i), self.listaMenus[valorinicio][0], self.listaMenus[valorinicio][1], self.listaMenus[valorinicio][2])
                valorinicio += 1
                if valorinicio >= self.maxentry:
                    valorinicio = 0

            self.activamenu(inicio)
            if not self.mostrado:
                self.mostrado = True
                cana = self.listaMenus[self.menuactivo - 1][1].replace('\n', ' ')
                self['estado'].setText(cana)
                self['estado2'].setText(str(self.menuactivo) + '/' + str(self.maxentry))
        self.autoclose()

    def activamenu(self, mactivo):
        for i in range(1, self.maxpantalla + 1):
            if i == mactivo:
                self['texto' + str(mactivo)].show()
                laposx = self['imagen' + str(mactivo)].instance.position().x()
                laposy = self['imagen' + str(mactivo)].instance.position().y() - 9
                self['seleccion'].instance.move(ePoint(laposx, laposy))
            else:
                self['texto' + str(i)].hide()

    def resh(self, resp):
        if resp:
            self.TimerTemp = eTimer()
            self.TimerTemp.callback.append(self.exit)
            self.TimerTemp.startLongTimer(1)

    def key_menu(self):
        if config.plugins.spzMenu.overwritemenu.value:
            self.exit()
        else:
            self.exit()

    def edita_menu(self):
        self.cierraSub()
        self.TimerClose.stop()
        self.timerMenu.stop()
        self.session.open(editaLista)

    def key_up(self):
        pass

    def key_down(self):
        pass

    def key_info(self):
        pass

    def key_left(self):
        if not self.SUBMENUdialog == None:
            self.cierraSub()
        self.menuactivo -= 1
        if self.menuactivo < 1:
            self.menuactivo = self.maxentry
        self.actual -= 1
        if self.actual < 2:
            self.actual = 2
            self.repintar()
        else:
            self.activamenu(self.actual)
        cana = self.listaMenus[self.menuactivo - 1][1].replace('\n', ' ')
        self['estado'].setText(cana)
        self['estado2'].setText(str(self.menuactivo) + '/' + str(self.maxentry))
        self.autoclose()

    def key_right(self):
        if not self.SUBMENUdialog == None:
            self.cierraSub()
        self.menuactivo += 1
        if self.menuactivo > self.maxentry:
            self.menuactivo = 1
        self.actual += 1
        if self.actual > self.maxpantalla - 1:
            self.actual = self.maxpantalla - 1
            self.repintar()
        else:
            self.activamenu(self.actual)
        cana = self.listaMenus[self.menuactivo - 1][1].replace('\n', ' ')
        self['estado'].setText(cana)
        self['estado2'].setText(str(self.menuactivo) + '/' + str(self.maxentry))
        self.autoclose()

    def repintar(self):
        self.buildList()

    def ira(self):
        pass

    def buildListSubMenu(self, listamenu):
        if not self.SUBMENUdialog == None:
            list = []
            for i in range(0, len(listamenu)):
                texto = '' + listamenu[i][0]
                imagen = str(listamenu[i][1])
                infotexto = str(listamenu[i][2])
                valor = listamenu[i][1]
                list.append(IniciaSelListEntrySub(texto, infotexto, valor, imagen))

            self.SUBMENUdialog['lista'].setList(list)
            self.SUBMENUdialog.updatescr()
            if self.activadalista:
                self.SUBMENUdialog['lista'].moveToIndex(len(self.SUBMENUdialog['lista'].list) - 1)

    def obtenlistaplugins(self):
        self.listapluginsmenu = []
        menuID = 'mainmenu'
        if menuID is not None:
            for l in plugins.getPluginsForMenu(menuID):
                plugin_menuid = l[2]
                for x in self.listapluginsmenu:
                    if x[2] == plugin_menuid:
                        self.listapluginsmenu.remove(x)
                        break

                if 'spazeTeam' not in str(l[2]) and not str(l[2]) == 'TVweb' and not str(l[2]) == 'info_screen' and 'Enhanced Movie Center' not in l[0]:
                    self.listapluginsmenu.append((l[0],
                     boundFunction(l[1], self.session),
                     l[2],
                     l[3] or 50))

            if len(self.listapluginsmenu) > 1:
                self.listapluginsmenu.sort(key=lambda x: int(x[3]))

    def runMenu(self):
        self.timerMenu.stop()
        self.autoclose()
        accionMenu = self.listaMenus[self.menuactivo - 1][2]
        cerrar = True
        cerrarActiva = False
        if accionMenu < 0:
            if self.SUBMENUdialog == None:
                codigo = self.listaMenus[self.menuactivo - 1][3]
                arrcodigo = codigo.split('#x#')
                submenu = arrcodigo[0]
                ayudas = arrcodigo[1]
                acciones = arrcodigo[2]
                posx = (self.actual - 1) * 230 + 30
                posx = self['imagen' + str(self.actual)].instance.position().x() - fhd(20)
                if posx + 440 > fhd(1280):
                    posx = fhd(1280) - 440
                if True:
                    arrsubmenu = submenu.split(';')
                    arrayudas = ayudas.split(';')
                    arracciones = acciones.split(';')
                    milista = []
                    if accionMenu == -22:
                        self.obtenlistaplugins()
                        conta = 0
                        for eleplu in self.listapluginsmenu:
                            milista.append((_(eleplu[0]), '99_' + str(conta), _('Plugin for system main menu')))
                            conta = conta + 1

                    for iji in range(0, len(arrsubmenu)):
                        if str(arracciones[iji]) == '7' and config.servicelist.lastmode.value == 'radio':
                            milista.append((_('View Tv'), '1', _('Toggle to tv view')))
                        else:
                            milista.append((_(arrsubmenu[iji]), arracciones[iji], _(arrayudas[iji])))

                    from Screens.InfoBar import InfoBar
                    self.SUBMENUdialog = self.session.instantiateDialog(spzSubMenu, filas=len(milista), titulo=_(str(self.listaMenus[self.menuactivo - 1][0])), posicionx=posx, activar=self.activadalista)
                    self.SUBMENUdialog.show()
                    self.buildListSubMenu(milista)
                else:
                    dei = self.session.open(MessageBox, 'Error build list ' + e.message, MessageBox.TYPE_INFO)
                    self.SUBMENUdialog = None
            return
        if accionMenu == 0:
            cerrarActiva = True
            codigo = self.listaMenus[self.menuactivo - 1][3]
            if not codigo == None and not codigo == '':
                self.runPlugin(codigo)
        elif accionMenu == 44:
            if MODELOSPZ == 'vuplus' and fileExists('/usr/lib/enigma2/python/Plugins/Extensions/XBMC/plugin.pyo'):
                try:
                    from Plugins.Extensions.XBMC.plugin import plugin_start_xbmc
                    from Screens.InfoBar import InfoBar
                    plugin_start_xbmc(InfoBar.instance.session)
                except:
                    pass

            elif MODELOSPZ == 'vuplus' and fileExists('/usr/lib/enigma2/python/Plugins/Extensions/Kodi/plugin.pyo'):
                try:
                    from Plugins.Extensions.Kodi.plugin import startLauncher
                    from Screens.InfoBar import InfoBar
                    startLauncher(InfoBar.instance.session)
                except:
                    pass

            elif MODELOSPZ == 'formuler':
                try:
                    from Plugins.Extensions.Kodi.plugin import KodiMainScreen
                    from Screens.InfoBar import InfoBar
                    InfoBar.instance.session.open(KodiMainScreen)
                except:
                    pass

            elif MODELOSPZ == 'wetek':
                try:
                    from Plugins.Extensions.StartKodi.plugin import StartKodi
                    from Screens.InfoBar import InfoBar
                    InfoBar.instance.session.open(StartKodi)
                except:
                    pass

        elif accionMenu == 3:
            cerrar = False
            self.TimerClose.stop()
            try:
                useemc = config.misc.spazeuseemc.value
            except:
                useemc = True

            if useemc == True:
                try:
                    from Plugins.Extensions.EnhancedMovieCenter.plugin import recordingsOpen
                    recordingsOpen(self.session)
                except:
                    useemc = False

            if useemc == False:
                from Screens.InfoBar import InfoBar
                if InfoBar and InfoBar.instance:
                    cerrar = False
                    InfoBar.showMovies(InfoBar.instance)
        if cerrar:
            self.TimerTemp = eTimer()
            self.TimerTemp.callback.append(self.exit)
            self.TimerTemp.startLongTimer(1)

    def mostrarExtensiones(self, arg1, arg2):
        from Screens.InfoBar import InfoBar
        cret = False
        if InfoBar and InfoBar.instance:
            cret = InfoBar.showExtensionSelection(InfoBar.instance)
            cret = True
        return cret

    def calbacksel(self, respuesta):
        if respuesta:
            self.close()

    def exit(self):
        self.TimerClose.stop()
        self.timerMenu.stop()
        self.TimerTemp.stop()
        if not self.SUBMENUdialog == None:
            self.cierraSub()
        self.close()

    def MenuClosed(self, dummy):
        pass

    def mainMenuClosed(self, dummy = False):
        pass

    def runPlugin(self, nombre):
        if nombre == 'Cool TV Guide':
            try:
                from Screens.InfoBar import InfoBar
                if InfoBar and InfoBar.instance:
                    servicelist = InfoBar.instance.servicelist
                from Plugins.Extensions.CoolTVGuide.plugin import main
                main(self.session, servicelist)
            except:
                Notifications.AddPopup(text=_('Error in Plugin or not exist (%s).') % nombre, type=MessageBox.TYPE_ERROR, timeout=20, id='HomeMenu')

        elif nombre == _('Graphical Multi EPG'):
            try:
                from Screens.InfoBar import InfoBar
                if InfoBar and InfoBar.instance:
                    servicelist = InfoBar.instance.servicelist
                from Plugins.Extensions.GraphMultiEPG.plugin import main
                main(self.session, servicelist)
            except:
                Notifications.AddPopup(text=_('Error in Plugin or not exist (%s).') % nombre, type=MessageBox.TYPE_ERROR, timeout=20, id='HomeMenu')

        else:
            try:
                from Components.PluginComponent import plugins
                for plugin in plugins.getPlugins([PluginDescriptor.WHERE_PLUGINMENU, PluginDescriptor.WHERE_EXTENSIONSMENU, PluginDescriptor.WHERE_EVENTINFO]):
                    if plugin.name == _(nombre):
                        runPlug = plugin
                        runPlug(session=self.session)
                        break

            except:
                Notifications.AddPopup(text=_('Error in Plugin or not exist (%s).') % nombre, type=MessageBox.TYPE_ERROR, timeout=20, id='HomeMenu')

    def ejecutaPlugin(self, nombre):
        try:
            from Components.PluginComponent import plugins
            for plugin in plugins.getPlugins([PluginDescriptor.WHERE_PLUGINMENU, PluginDescriptor.WHERE_EXTENSIONSMENU, PluginDescriptor.WHERE_EVENTINFO]):
                if plugin.name == _(nombre):
                    plugin(session=self.session)
                    break

        except:
            pass


class IniciaSelListSub(MenuList):

    def __init__(self, list, enableWrapAround = False):
        MenuList.__init__(self, list, enableWrapAround, eListboxPythonMultiContent)
        self.l.setItemHeight(fhd(50))
        self.l.setFont(0, gFont('Regular', 19))
        self.l.setFont(1, gFont('Regular', 17))


def IniciaSelListEntrySub(texto, infotexto = '', ervalor = 0, numero = 0):
    res = [ervalor]
    nx = fhd(40)
    ny = fhd(1)
    nh = fhd(24)
    dx = fhd(42)
    dy = fhd(23)
    dh = fhd(19)
    anchoimagen = fhd(25)
    laruta = devrutaimagen('iconosMenus')
    archivo = laruta + 'ico' + str(numero) + '.png'
    if fileExists(archivo):
        png = LoadPixmap(archivo)
    elif fileExists(laruta + 'icon.png'):
        png = LoadPixmap(laruta + 'icon.png')
    else:
        png = None
        dx = dx - anchoimagen
        nx = nx - anchoimagen
    res.append(MultiContentEntryText(pos=(nx, ny), size=(1000, nh), font=0, flags=RT_HALIGN_LEFT, text=texto))
    if '99_' in str(numero):
        numero = '99'
    res.append(MultiContentEntryText(pos=(dx, dy), size=(760, dh), font=1, flags=RT_HALIGN_LEFT, text=infotexto, color=8947848))
    if not png == None:
        res.append(MultiContentEntryPixmapAlphaBlend(pos=(fhd(7, 1), fhd(7)), size=(fhd(25), fhd(25)), png=png, flags=BT_SCALE | BT_KEEP_ASPECT_RATIO))
    return res


from sbar import openspaSB

class spzSubMenu(Screen):
    if esHD():
        skin = '\n\t\t\t <screen flags="wfBorder" name="spzSubMenu" zPosition="13" position="100,505" size="585,150" title="SubMenu">\n \t\t\t<widget name="titulodummy" position="-7,0" size="1,60" zPosition="12" backgroundColor="#ff000000" alphatest="blend" transparent="1" />\n \t\t\t<widget name="arriba" position="0,0" size="585,6" zPosition="12" backgroundColor="#12333333" alphatest="blend" transparent="1" />\n \t\t\t<widget name="izquierda" position="0,0" size="6,150" zPosition="12" backgroundColor="#12333333" alphatest="blend" transparent="1"/>\n \t\t\t<widget name="lista" position="0,0" size="585,144" scrollbarMode="showOnDemand" zPosition="10" />\n \t\t\t<widget name="derecha" position="0,150" size="3,150" zPosition="12" backgroundColor="#12333333" alphatest="blend" transparent="1" />\n \t\t\t<widget name="abajo" position="0,600" size="150,3" zPosition="12" backgroundColor="#12333333" alphatest="blend" transparent="1" />\n \t\t\t<widget name="fondo" position="0,0" size="585,150" zPosition="1" />\n\t\t\t<widget name="barrascroll_arr" position="0,0" zPosition="19" size="30,30" alphatest="blend" transparent="1" />\n\t\t\t<widget name="barrascroll_abj" position="0,0" zPosition="19" size="30,30" alphatest="blend" transparent="1" />\t\t\t\t\n\t\t\t</screen>'
    else:
        skin = '\n\t\t\t<screen flags="wfBorder" name="spzSubMenu" zPosition="13" position="100,505" size="390,100" title="SubMenu">\n\t\t\t<widget name="titulodummy" position="-5,0" size="1,40" zPosition="12" backgroundColor="#ff000000" alphatest="blend" transparent="1" />\n\t\t\t<widget name="arriba" position="0,0" size="390,4" zPosition="12" backgroundColor="#12333333" alphatest="blend" transparent="1" />\n\t\t\t<widget name="izquierda" position="0,0" size="4,100" zPosition="12" backgroundColor="#12333333" alphatest="blend" transparent="1"/>\n\t\t\t<widget name="lista" position="0,0" size="390,96" scrollbarMode="showOnDemand" zPosition="10" />\n\t\t\t<widget name="derecha" position="0,100" size="2,100" zPosition="12" backgroundColor="#12333333" alphatest="blend" transparent="1" />\n\t\t\t<widget name="abajo" position="0,400" size="100,2" zPosition="12" backgroundColor="#12333333" alphatest="blend" transparent="1" />\n\t\t\t<widget name="fondo" position="0,0" size="390,100" zPosition="1" />\n\t\t\t<widget name="barrascroll_arr" position="0,0" zPosition="19" size="20,20" alphatest="blend" transparent="1" />\n\t\t\t<widget name="barrascroll_abj" position="0,0" zPosition="19" size="20,20" alphatest="blend" transparent="1" />\t\t\t\t\n\t\t\t</screen>'

    def __init__(self, session, numele = 4, filas = 3, posicionx = 600, titulo = 'Submenu', activar = True):
        Screen.__init__(self, session)
        self.session = session
        self.activar = activar
        self.alto = 0
        self.origpos = 0
        self.posicionx = posicionx
        self.posiciony = 0
        self.setTitle(titulo)
        self.titulo = titulo
        self.altotitulo = 0
        self.margen = 4
        self.ancho = 0
        self.filas = filas
        self.aumento = 0
        self.skin = spzSubMenu.skin
        self.onShow.append(self.anima)
        self['lista'] = IniciaSelListSub([])
        self['barrascroll_arr'] = Pixmap()
        self['barrascroll_abj'] = Pixmap()
        self['arriba'] = Pixmap()
        self['abajo'] = Pixmap()
        self['izquierda'] = Pixmap()
        self['derecha'] = Pixmap()
        self['fondo'] = Pixmap()
        self['titulodummy'] = Pixmap()
        try:
            self['borde'] = Label()
        except:
            pass

        self.TimerAnima = eTimer()
        self.TimerAnima.callback.append(self.anima)
        self.tempalto = 0
        self.onLayoutFinish.append(self.buildListSub)

    def buildListSub(self):
        self['barrascroll_arr'].hide()
        self['barrascroll_abj'].hide()
        try:
            self.posiciony = self.instance.position().y()
        except:
            pass

        self.origpos = self.posiciony
        margenextra = 0
        try:
            margenextra = self['borde'].instance.size().width()
        except:
            pass

        margen = self.margen
        margeny = self['arriba'].instance.size().height()
        margenyb = self['abajo'].instance.size().height()
        margenx = self['izquierda'].instance.size().width()
        self.altotitulo = self['titulodummy'].instance.size().height()
        if self.altotitulo == 1:
            self.altotitulo = 0
        self.alto = self.filas * fhd(50) + margeny + margenyb + margenextra * 2
        if self.alto + (720 - self.origpos) > 655:
            self.alto = 655 - (720 - self.origpos) + margeny
        self.posiciony = self.posiciony - self.alto
        wsizex = self.instance.size().width() + margenextra * 2
        wsizey = self.alto
        wsize = (wsizex, wsizey)
        listsize = (wsizex - margenx * 2 - margenextra * 2, wsizey - margeny - margenyb - margenextra * 2)
        self['lista'].instance.move(ePoint(margenx + margenextra, margeny + margenextra))
        self['lista'].instance.resize(eSize(*listsize))
        self['derecha'].instance.move(ePoint(wsizex - margenx, margeny))
        self['arriba'].instance.move(ePoint(0, 0))
        self['abajo'].instance.move(ePoint(0, margeny + wsizey - margeny - margenyb))
        self['izquierda'].instance.move(ePoint(0, margeny))
        temp = (wsizex - margenx * 2, wsizey - margeny - margenyb)
        self['fondo'].instance.move(ePoint(margenx, margeny))
        self['fondo'].instance.resize(eSize(*temp))
        try:
            self['borde'].instance.move(ePoint(margenx, margeny))
            self['borde'].instance.resize(eSize(*temp))
        except:
            pass

        temp = (margenx, wsizey - margeny - margenyb)
        self['izquierda'].instance.resize(eSize(*temp))
        self['derecha'].instance.resize(eSize(*temp))
        temp = (wsizex, margeny)
        self['arriba'].instance.resize(eSize(*temp))
        temp = (wsizex, margenyb)
        self['abajo'].instance.resize(eSize(*temp))
        self.origpos = self.origpos + self.altotitulo
        self.aumento = int(self.alto / 3) + 1
        self.tempalto = self.aumento
        py = self.origpos - self.alto
        self.instance.move(ePoint(self.posicionx, py))
        wsizetemp = (wsizex, self.alto)
        self.tempalto = self.alto
        self.instance.resize(eSize(*wsizetemp))
        self.ancho = wsizex
        if not self.activar:
            self['lista'].selectionEnabled(0)
        self.setTitle(self.titulo)

    def anima(self):
        xxalto = self.tempalto
        self.TimerAnima.stop()
        if xxalto < self.alto:
            xxalto = xxalto + self.aumento
            self.tempalto = self.tempalto + self.aumento
            if xxalto > self.alto:
                xxalto = self.alto
            wsizex = self.ancho
            wsizey = xxalto
            wsize = (wsizex, wsizey)
            self.instance.resize(eSize(*wsize))
            py = self.origpos - xxalto
            self.instance.move(ePoint(self.posicionx, py))
            self.TimerAnima.start(1, True)

    def updatescr(self):
        openspaSB(objectoself=self, altoitem=50)


remapear = config.plugins.spzMenu.mapkey.value

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
            ret = _('No info avaiable')
    return ret


def versionOk():
    return chequeaVersion() and fileExists('/usr/bin/chkvs')


def homeMenu(instance, fwd = True):
    if not versionOk():
        Notifications.AddPopup(text=_('Not openSPA image found!\nMore info in www.azboxhd.es').replace('azboxhd.es', 'openspa.info'), type=MessageBox.TYPE_ERROR, timeout=10, id='spazeMenu')
    else:
        from Screens.InfoBar import InfoBar
        if InfoBar and InfoBar.instance:
            InfoBar.instance.session.open(spazeTeamMenu, fwd)


def iniciaHome():
    if not versionOk():
        Notifications.AddPopup(text=_('Not openSPA image found!\nMore info in www.azboxhd.es').replace('azboxhd.es', 'openspa.info'), type=MessageBox.TYPE_ERROR, timeout=10, id='spazeMenu')
    else:
        try:
            from Screens.InfoBar import InfoBar
            if InfoBar and InfoBar.instance:
                InfoBar.instance.session.open(spazeTeamMenu)
        except:
            pass


class HomeMenuSw():

    def __init__(self):
        pass

    def change_keymap(self, keymap):
        global globalActionMap
        if config.plugins.spzMenu.mapkey.value == 'none':
            return
        if keymap not in KEYMAPPINGS:
            return
        self.unload_keymap()
        try:
            keymapparser.readKeymap(KEYMAPPINGS[keymap])
        except IOError as (errno, strerror):
            self.disable()
            Notifications.AddPopup(text=_('Changing keymap failed (%s).') % strerror, type=MessageBox.TYPE_ERROR, timeout=10, id='HomeMenuSw')
            return

        globalActionMap.actions['MostrarMenuHome'] = self.cambiaraMenuHome

    def unload_keymap(self):
        for keymap in KEYMAPPINGS.values():
            keymapparser.removeKeymap(keymap)

        if 'MostrarMenuHome' in globalActionMap.actions:
            del globalActionMap.actions['MostrarMenuHome']

    def enable(self):
        self.change_keymap(config.plugins.spzMenu.mapkey.value)

    def disable(self):
        global home_menu_sw
        self.unload_keymap()
        home_menu_sw = None

    def cambiaraMenuHome(self):
        self.switchHome()

    def switchHome(self):
        global home_pulsado
        if not versionOk():
            Notifications.AddPopup(text=_('Not openSPA image found!\nMore info in www.azboxhd.es').replace('azboxhd.es', 'openspa.info'), type=MessageBox.TYPE_ERROR, timeout=10, id='spazeMenu')
        else:
            try:
                home_pulsado = True
                from Screens.InfoBar import InfoBar
                if InfoBar and InfoBar.instance:
                    if self.posibleHome(InfoBar.instance.session):
                        InfoBar.instance.session.open(spazeTeamMenu)
            except:
                pass

    def posibleHome(self, session):
        modoayuda = 0
        try:
            if 'Screens.InfoBar.InfoBar' in str(session.current_dialog):
                modoayuda = 1
            elif 'Screens.Menu.MainMenu' in str(session.current_dialog):
                modoayuda = 3
        except:
            pass

        if modoayuda == 3:
            try:
                session.current_dialog.closeRecursive()
            except:
                try:
                    session.current_dialog.close()
                except:
                    pass

        if modoayuda == 0:
            return False
        else:
            return True


def ajustaLogo():
    try:
        os.system("echo 'modelo[" + MODELOSPZ + "]'>>/tmp/debug_logo.log")
        cad = ''
        if MODELOSPZ == 'vuplus':
            cad = 'vu'
        elif MODELOSPZ == 'golden':
            cad = 'gm'
        elif MODELOSPZ == 'azbox':
            cad = 'az'
        elif MODELOSPZ == 'opticum':
            cad = 'opticum'
        elif MODELOSPZ == 'xtrend':
            cad = 'xtrend'
        elif MODELOSPZ == 'e3hd':
            cad = 'e3hd'
        elif MODELOSPZ == 'vnet':
            cad = 'vnet'
        elif MODELOSPZ == 'gigablue':
            cad = 'gigablue'
        elif MODELOSPZ == 'mkdigital':
            cad = 'mkdigital'
        elif MODELOSPZ == 'zgemma':
            cad = 'zgemma'
        elif MODELOSPZ == 'wetek':
            cad = 'wetek'
        elif MODELOSPZ == 'gi':
            cad = 'gi'
        elif MODELOSPZ == 'formuler':
            cad = 'formuler'
        if cad == '' or cad == 'NA':
            return
        nomskin = str(config.skin.primary_skin.value).split('/')[0]
        rutaSkin = resolveFilename(SCOPE_SKIN) + nomskin + '/'
        if fileExists(rutaSkin + 'spamodel.nfo'):
            fp = open(rutaSkin + 'spamodel.nfo', 'r')
            result = fp.read().replace('\n', '')
            fp.close()
            if result == cad + '-' + nomskin:
                return
        os.system("echo '" + cad + '-' + nomskin + "'>" + rutaSkin + 'spamodel.nfo')
        rutalogos = devrutaimagen('logos')
        archivo1 = 'logo' + cad + '.png'
        archivo2 = 'logo' + cad + 'med-fs8.png'
        archivo3 = 'no_poster_vp' + cad + '.jpg'
        if fileExists(rutaSkin + 'menu/logo.png') and fileExists(rutaSkin + 'logoazmed-fs8.png'):
            os.system("cp -f '" + rutalogos + archivo1 + "' '" + rutaSkin + "menu/logo.png'")
            os.system("cp -f '" + rutalogos + archivo2 + "' '" + rutaSkin + "logoazmed-fs8.png'")
            os.system("cp -f '" + rutalogos + archivo2 + "' '/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/image/logoazmed-fs8.png'")
            os.system("cp -f '" + rutalogos + archivo3 + "' '/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/images/no_poster_vp.jpg'")
    except:
        pass


def pondebug(texto):
    if True:
        os.system('date > /tmp/autoclean.log')
        os.system("echo '" + texto + "'>>/tmp/autoclean.log")
        os.system("echo '*******************************'>>/tmp/autoclean.log")


def limpiamemoria(num = 3, txtdebug = 'free ram'):
    pondebug(txtdebug)
    if num >= 0:
        os.system('sync')
        os.system('echo ' + str(num) + ' > /proc/sys/vm/drop_caches')


def sessionautostart(session, **kwargs):
    if config.misc.spazeclearram.value:
        config.misc.standbyCounter.addNotifier(enterStandby, initial_call=False)


def enterStandby(self = None, configElement = None):
    limpiamemoria(3, 'enterStandby - free ram')


def leaveStandby():
    pass


def autostart(reason, **kwargs):
    global home_menu_sw
    ajustaLogo()
    if reason == 0:
        if not config.plugins.spzMenu.mapkey.value == 'none' and home_menu_sw is None and (not config.plugins.spzMenu.overwritemenu.value or config.plugins.spzMenu.mapkey.value == 'home'):
            home_menu_sw = HomeMenuSw()
            home_menu_sw.enable()
    elif reason == 1:
        if home_menu_sw is not None:
            home_menu_sw.disable()
    auto_start_Plugins(reason, **kwargs)
    if reason == 0:
        limpiamemoria(3, 'restart - free ram')


def start_from_mainmenu(menuid, **kwargs):
    if menuid == 'mainmenu':
        return [(_('Home Menu'),
          mainHome,
          'spazeTeamMenu',
          1)]
    return []


def record_menu(menuid, **kwargs):
    if menuid == 'mainmenu':
        return [(_('Record'),
          set_record,
          'spazeTeamRecord',
          48)]
    return []


def scaling_menu(menuid, **kwargs):
    if menuid == 'mainmenu':
        return [(_('Scaling modes'),
          set_scaling,
          'spazeTeamScaling',
          47)]
    return []


def info_menu(menuid, **kwargs):
    if menuid == 'mainmenu':
        return [(_('Information'),
          set_info,
          'info_screen',
          49)]
    return []


def audio_menu(menuid, **kwargs):
    if menuid == 'mainmenu':
        return [(_('Audio/Subtitles'),
          set_audio,
          'spazeTeamAudio',
          48)]
    return []


def set_info(session, **kwargs):
    try:
        from Plugins.Extensions.spazeMenu.spzPlugins.InfoAz.plugin import iniciainfo
        iniciainfo(session)
    except:
        pass


def set_audio(session, **kwargs):
    from Screens.InfoBar import InfoBar
    if InfoBar and InfoBar.instance:
        InfoBar.audioSelection(InfoBar.instance)


def set_record(session, **kwargs):
    from Screens.InfoBar import InfoBar
    if InfoBar and InfoBar.instance:
        InfoBar.instantRecord(InfoBar.instance)


def set_scaling(session, **kwargs):
    if fileExists('/usr/lib/enigma2/python/Plugins/Extensions/ScalingModes/plugin.pyo'):
        try:
            from Plugins.Extensions.ScalingModes.plugin import main
            main(session)
            return
        except:
            pass

    try:
        from Screens.VideoMode import VideoSetup
        session.open(VideoSetup)
    except:
        pass


def runExtensiones():
    from Screens.InfoBar import InfoBar
    if InfoBar and InfoBar.instance:
        InfoBar.showExtensionSelection(InfoBar.instance)


TimerTempMN = eTimer()

def mainHome(session, **kwargs):
    global TimerTempMN
    if 'Screens.Menu.MainMenu' in str(session.current_dialog):
        try:
            session.current_dialog.close()
        except:
            pass

        TimerTempMN.callback.append(iniciaHome)
        TimerTempMN.start(1000, True)
    elif not versionOk():
        Notifications.AddPopup(text=_('Not openSPA image found!\nMore info in www.azboxhd.es'), type=MessageBox.TYPE_ERROR, timeout=10, id='spazeMenu')
    else:
        try:
            session.open(spazeTeamMenu)
        except:
            pass


def main_guia(session, servicelist, **kwargs):
    from Plugins.Extensions.spazeMenu.spzPlugins.openSPATVGuide.plugin import main
    main(session, servicelist)


def main_epg(session, servicelist, **kwargs):
    servicio = session.nav.getCurrentlyPlayingServiceReference()
    if servicio:
        from Plugins.Extensions.spazeMenu.spzPlugins.openSPATVGuide.EPGSimple import spaEPGSelection
        session.open(spaEPGSelection, session.nav.getCurrentlyPlayingServiceReference())


def filescan_open(list, session, **kwargs):
    filelist = [ ((file.path, False), None) for file in list ]
    try:
        ruta = file.path
        archivo = ruta.split('/')[-1]
        ruta = ruta.replace(archivo, '')
        from Plugins.Extensions.spazeMenu.spzPlugins.AzExplorer.plugin import main
        main(session, ruta)
    except:
        pass


def filescan_opena(list, session, **kwargs):
    filelist = [ ((file.path, False), None) for file in list ]
    try:
        ruta = file.path
        archivo = ruta.split('/')[-1]
        ruta = ruta.replace(archivo, '')
        from Plugins.Extensions.MediaCenter.MC_AudioPlayer import MC_AudioPlayer
        from Screens.InfoBar import InfoBar
        InfoBar.instance.session.open(MC_AudioPlayer, ruta_inicio=ruta)
    except:
        pass


def filescan_openv(list, session, **kwargs):
    filelist = [ ((file.path, False), None) for file in list ]
    try:
        ruta = file.path
        archivo = ruta.split('/')[-1]
        ruta = ruta.replace(archivo, '')
        from Plugins.Extensions.MediaCenter.MC_VideoPlayer import MC_VideoPlayer
        from Screens.InfoBar import InfoBar
        InfoBar.instance.session.open(MC_VideoPlayer, ruta_inicio=ruta)
    except:
        pass


def filescan(**kwargs):
    from Components.Scanner import Scanner, ScanPath

    class ExplorerScanner(Scanner):

        def checkFile(self, file):
            return True

    lista = []
    if fileExists('/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/MC_VideoPlayer.pyo'):
        lista.append(ExplorerScanner(mimetypes=None, paths_to_scan=(ScanPath(path='', with_subdirs=False),), name='Video Files', description=_('Explore with MediaCenter - Videos') + '...', openfnc=filescan_openv))
    if fileExists('/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/MC_AudioPlayer.pyo'):
        lista.append(ExplorerScanner(mimetypes=None, paths_to_scan=(ScanPath(path='', with_subdirs=False),), name='Music Files', description=_('Explore with MediaCenter - Audio') + '...', openfnc=filescan_opena))
    if fileExists('/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/AzExplorer/plugin.pyo'):
        lista.append(ExplorerScanner(mimetypes=None, paths_to_scan=(ScanPath(path='', with_subdirs=False),), name='Files/Folders', description=_('Open files/folders Explorer') + '...', openfnc=filescan_open))
    if lista:
        return lista


def Plugins(**kwargs):
    name = _('openSPA Menu')
    descr = _('openSPA Home Menu')
    list = [PluginDescriptor(name=name, description=descr, where=PluginDescriptor.WHERE_EXTENSIONSMENU, fnc=mainHome)]
    list.append(PluginDescriptor(where=[PluginDescriptor.WHERE_SESSIONSTART, PluginDescriptor.WHERE_AUTOSTART], fnc=autostart))
    list.append(PluginDescriptor(where=[PluginDescriptor.WHERE_SESSIONSTART], fnc=sessionautostart))
    if config.plugins.spzMenu.showinmenu.value and not config.plugins.spzMenu.overwritemenu.value:
        list.append(PluginDescriptor(name=_('Home Menu'), description=descr, where=PluginDescriptor.WHERE_MENU, fnc=start_from_mainmenu))
    if config.plugins.spzMenu.showaudio.value:
        list.append(PluginDescriptor(name=_('Audio/Subtitles'), description='', where=PluginDescriptor.WHERE_MENU, fnc=audio_menu))
    if config.plugins.spzMenu.showrecord.value:
        list.append(PluginDescriptor(name=_('Record'), description='', where=PluginDescriptor.WHERE_MENU, fnc=record_menu))
    if config.plugins.spzMenu.showscaling.value:
        list.append(PluginDescriptor(name=_('Scaling modes'), description='', where=PluginDescriptor.WHERE_MENU, fnc=scaling_menu))
    list.append(PluginDescriptor(name=_('Information'), description='', where=PluginDescriptor.WHERE_MENU, fnc=info_menu))
    list.append(PluginDescriptor(name=_('Programs Guide') + ' - openSPA', description='', where=PluginDescriptor.WHERE_EXTENSIONSMENU, fnc=main_guia))
    list.append(PluginDescriptor(name=_('Programs Guide') + ' - openSPA', description='', where=PluginDescriptor.WHERE_EVENTINFO, fnc=main_guia))
    list.append(PluginDescriptor(name=_('Single EPG') + ' - openSPA', description='', where=PluginDescriptor.WHERE_EXTENSIONSMENU, fnc=main_epg))
    list.append(PluginDescriptor(name=_('Single EPG') + ' - openSPA', description='', where=PluginDescriptor.WHERE_EVENTINFO, fnc=main_epg))
    list.append(PluginDescriptor(name=_('Open files/folders Explorer'), where=PluginDescriptor.WHERE_FILESCAN, needsRestart=False, fnc=filescan))
    try:
        from Plugins.Extensions.spazeMenu.spzPlugins.spaTimerEntry.plugin import mainmenu as seriestimer
        list.append(PluginDescriptor(name=_('TV Series Timers'), where=PluginDescriptor.WHERE_MENU, fnc=seriestimer))
    except:
        pass

    return list


def keyMenuHome(instance):
    from Screens.InfoBar import InfoBar
    iniciaHome()


from spzVirtualKeyboard import spzVirtualKeyboard
from enigma import eServiceReference
from Components.ScrollLabel import ScrollLabel
from skin import parseColor
from Components.Sources.ServiceEvent import ServiceEvent
from Components.Sources.Event import Event

def spa_EventView_init(self, event, Ref, callback = None, similarEPGCB = None, par1 = None, par2 = None):
    self.similarEPGCB = similarEPGCB
    self.cbFunc = callback
    self.currentService = Ref
    self.isRecording = not Ref.ref.flags & eServiceReference.isGroup and Ref.ref.getPath()
    self.event = event
    self['Service'] = ServiceEvent()
    self['Event'] = Event()
    self['epg_description'] = ScrollLabel()
    try:
        self['FullDescription'] = ScrollLabel()
    except:
        pass

    self['datetime'] = Label()
    self['channel'] = Label()
    self['duration'] = Label()
    self.hayextra = False
    try:
        self['extrainfo'] = Label()
        self['rating'] = Label()
        self['icoevent'] = Pixmap()
        self.hayextra = True
    except:
        pass

    self['key_red'] = Button('')
    if similarEPGCB is not None:
        self.SimilarBroadcastTimer = eTimer()
        self.SimilarBroadcastTimer.callback.append(self.getSimilarEvents)
    else:
        self.SimilarBroadcastTimer = None
    self.key_green_choice = self.ADD_TIMER
    if self.isRecording:
        self['key_green'] = Button('')
    else:
        self['key_green'] = Button(_('Add timer'))
    self['key_yellow'] = Button('')
    self['key_blue'] = Button('')
    self['actions'] = ActionMap(['OkCancelActions', 'EventViewActions'], {'cancel': self.close,
     'ok': self.close,
     'pageUp': self.pageUp,
     'pageDown': self.pageDown,
     'prevEvent': self.prevEvent,
     'nextEvent': self.nextEvent,
     'timerAdd': self.timerAdd,
     'openSimilarList': self.openSimilarList,
     'contextMenu': self.doContext})
    self.onShown.append(self.onCreate)


def spa_EventView_OnCreate(dummy):
    dummy.setService(dummy.currentService)
    dummy.setEvent(dummy.event)
    dummy['key_red'].setText(_('Internet info'))
    dummy.similarEPGCB = 1
    dummy.getSimilarEvents()


def spa_prevEvent(self):
    if self.cbFunc is not None:
        self.cbFunc(self.setEvent, self.setService, -1)
    self.getSimilarEvents()


def spa_nextEvent(self):
    if self.cbFunc is not None:
        self.cbFunc(self.setEvent, self.setService, +1)
    self.getSimilarEvents()


def spa_EventView_getSimilarEvents(dummy):
    try:
        if dummy.hayextra:
            dummy['icoevent'].hide()
            dummy['extrainfo'].hide()
            dummy['rating'].hide()
            from Plugins.Extensions.spazeMenu.spzPlugins.openSPATVGuide.EPGSearch import getgenero
            textoextra = ''
            lang = language.getLanguage()
            idioma = str(lang[:2])
            if idioma == 'ca' or idioma == 'eu' or idioma == 'ga' or idioma == 'va':
                idioma = 'es'
            rating = dummy.event.getParentalData()
            textorat = ''
            colorrat = '#999999'
            if rating is None:
                textorat = ''
            else:
                age = rating.getRating()
                if age == 0 or age == 29 or age >= 16 and age <= 17:
                    if idioma == 'es':
                        textorat = 'TP'
                    else:
                        textorat = 'G'
                    colorrat = '#28a351'
                elif age == 30:
                    textorat = '+1'
                    colorrat = '#28a351'
                elif age == 31:
                    textorat = 'X'
                    colorrat = '#ff0000'
                elif age > 15:
                    textorat = ''
                else:
                    age += 3
                    cret = '+%d' % age
                    textorat = cret
                    if age <= 8:
                        colorrat = '#28a351'
                    elif age <= 13:
                        colorrat = '#4177ac'
                    elif age <= 17:
                        colorrat = '#cc5100'
                    else:
                        colorrat = '#cc0000'
            if textorat != '':
                dummy['rating'].setText(textorat)
                dummy['rating'].instance.setBackgroundColor(parseColor(colorrat))
                dummy['rating'].show()
            tuplagenero = getgenero(dummy.event, 70, False)
            dummy['extrainfo'].setText(textoextra)
            ergenero = tuplagenero[0]
            if ergenero != '':
                textoextra = textoextra + ergenero
                if tuplagenero[2]:
                    dummy['icoevent'].instance.setPixmapFromFile(tuplagenero[2])
                    dummy['icoevent'].show()
            dummy['extrainfo'].setText(textoextra)
            dummy['extrainfo'].show()
    except:
        pass

    dummy['key_red'].setText(_('Internet info'))
    ctiempo = ''
    try:
        tiempo = dummy.event.getBeginTime()
        t2 = localtime(tiempo)
        cdia = str(strftime('%d', t2))
        cmes = _(str(strftime('%B', t2)))
        csemana = _(str(strftime('%A', t2))).replace('\xc3\xa1', 'a').replace('\xc3\xa9', 'e').replace('\xc3\xad', 'i').replace('\xc3\xb3', 'o').replace('\xc3\xba', 'u')
        ctiempo = csemana[:3].capitalize() + ', ' + cdia + '-' + cmes[:3].capitalize()
        ctiempo = ctiempo + ' \xe2\x80\xa2 ' + strftime('%H:%M', t2)
    except:
        pass

    try:
        t2 = localtime(tiempo + dummy.event.getDuration())
        ctiempo = ctiempo + ' - ' + strftime('%H:%M', t2)
    except:
        pass

    try:
        if ctiempo != '':
            dummy['datetime'].setText(ctiempo)
    except:
        pass

    try:
        dummy.setService(dummy.currentService)
        txta = dummy['channel'].getText()
        txta = txta + ' \xe2\x80\xa2 ' + dummy.event.getEventName()
        dummy['channel'].setText(txta)
    except:
        pass

    try:
        tiempo = dummy.event.getDuration()
        txta = _('%d min') % (tiempo / 60)
        t2 = localtime(tiempo - 3600)
        adddur = strftime('%H:%M', t2)
        txta = txta + ' (' + adddur + ')'
        dummy['duration'].setText(txta)
    except:
        pass


def spa_EventView_openSimilarList(dummy):
    if not dummy.event:
        return
    try:
        titulo = dummy.event.getEventName()
        from Plugins.Extensions.spzIMDB.plugin import spzIMDB
        spzIMDB(dummy.session, tbusqueda=titulo)
        return
    except:
        pass


def auto_start_Plugins(reason, **kwargs):
    if not fileExists('/usr/bin/chkvs'):
        textocat = cargaosinfo('cat /proc/version')
        valids = 'spaze@spaze-desktop,asus@asus-K52Je,morser@morser-H61M-S2-B3'
        for ele in valids.split(','):
            if ele in textocat:
                os.system('date >/usr/bin/chkvs')
                break

    if fileExists('/usr/lib/enigma2/python/Screens/newChannelSelection.pyo'):
        try:
            from Plugins.Extensions.spazeMenu.spzPlugins.newChannelSelection.plugin import autostart
            autostart(reason, **kwargs)
        except Exception as e:
            pass

    if config.misc.replacespzkeyboard.value:
        from modE2 import modE2components
        modE2components()
    from Screens.EventView import EventViewBase
    try:
        EventViewBase.__init__ = spa_EventView_init
        EventViewBase.onCreate = spa_EventView_OnCreate
        EventViewBase.getSimilarEvents = spa_EventView_getSimilarEvents
        EventViewBase.openSimilarList = spa_EventView_openSimilarList
        EventViewBase.nextEvent = spa_nextEvent
        EventViewBase.prevEvent = spa_prevEvent
    except:
        pass

    if config.plugins.spzMenu.overwritemenu.value:
        from Screens.InfoBar import InfoBar
        try:
            InfoBar.mainMenu = keyMenuHome
        except:
            pass

    if config.misc.spazeupdates.value:
        try:
            from Plugins.Extensions.spazeMenu.spzPlugins.descargasSPZ.plugin import autostart
            autostart(reason, **kwargs)
        except:
            pass

    try:
        from Plugins.Extensions.spazeMenu.spzPlugins.spzCAMD.plugin import autostart
        autostart(reason, **kwargs)
    except:
        pass

    try:
        from Plugins.Extensions.spazeMenu.spzPlugins.mhw2Timer.plugin import autostart
        autostart(reason, **kwargs)
    except:
        pass

    try:
        if config.plugins.spzsimpleRSS.autostart.value:
            from Plugins.Extensions.spazeMenu.spzPlugins.spzSimpleRSS.plugin import autostart
            autostart(reason, **kwargs)
    except Exception as e:
        pass

    try:
        from Plugins.Extensions.spazeMenu.spzPlugins.openSPATVGuide.plugin import autostart
        autostart(reason, **kwargs)
    except:
        pass

    try:
        from Plugins.Extensions.spazeMenu.spzPlugins.spaTimerEntry.plugin import autostart
        autostart(reason, **kwargs)
    except:
        pass
