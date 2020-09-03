from Screens.Screen import Screen
from Plugins.Plugin import PluginDescriptor
from Components.ActionMap import ActionMap
from Components.Label import Label
from Tools.Directories import fileExists, SCOPE_PLUGINS, resolveFilename
import os
from Components.ScrollLabel import ScrollLabel
from Screens.ChoiceBox import ChoiceBox
from Components.PluginComponent import plugins
from Tools.LoadPixmap import LoadPixmap
from enigma import eTimer
from Components.Pixmap import Pixmap
from Screens.MessageBox import MessageBox
from Screens.Standby import TryQuitMainloop
from Tools import Notifications
from os import environ
import gettext
from Components.Language import language
from Tools.Directories import SCOPE_LANGUAGE
lang = language.getLanguage()
environ['LANGUAGE'] = lang[:2]
gettext.bindtextdomain('enigma2', resolveFilename(SCOPE_LANGUAGE))
gettext.textdomain('enigma2')
gettext.bindtextdomain('gesPluginsOpenSpa', '%s%s' % (resolveFilename(SCOPE_PLUGINS), 'Extensions/spazeMenu/spzPlugins/gesPluginsOpenSpa/locale/'))

def _(txt):
    t = gettext.dgettext('gesPluginsOpenSpa', txt)
    if t == txt:
        t = gettext.gettext(txt)
    return t


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


from Components.MenuList import MenuList
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaBlend
from enigma import eListboxPythonMultiContent, gFont, BT_SCALE, BT_KEEP_ASPECT_RATIO
from Plugins.Extensions.spazeMenu.plugin import esHD, fhd

class IniciaSelListFaqs(MenuList):

    def __init__(self, list, enableWrapAround = False):
        MenuList.__init__(self, list, enableWrapAround, eListboxPythonMultiContent)
        self.l.setItemHeight(fhd(30))
        self.l.setFont(0, gFont('Regular', 19))
        self.l.setFont(1, gFont('Regular', 17))


def fnombre(nom):
    cret = nom.replace('Extensions/spazeMenu/spzPlugins/', _('openSPA Plugins/'))
    cret = cret.replace('Extensions/', _('Extensions') + '/')
    cret = cret.replace('SystemPlugins/', _('SystemPlugins') + '/')
    cret = cret.replace('.tar.gz.back', '')
    return cret


def IniciaSelListEntryPlugin(texto, instalado, cambiado, nombre, inicial):
    res = [texto]
    textofin = fnombre(texto) + nombre
    addpos = 0
    colort = None
    if inicial and '' + inicial in texto:
        addpos = 10
        colort = 16772744
    if instalado:
        if cambiado:
            imagen = 'v'
        else:
            imagen = 'icov'
        if not colort:
            colort = 16777215
    else:
        if cambiado:
            imagen = 'x'
        else:
            imagen = 'icox'
        if not colort:
            colort = 10066329
    res.append(MultiContentEntryText(pos=(fhd(30 + addpos), fhd(3)), size=(fhd(1000), fhd(25)), font=0, text=textofin, color=colort))
    carpetaimg = '/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/gesPluginsOpenSpa/img/'
    png = '' + carpetaimg + '' + imagen + '.png'
    if fileExists(png):
        fpng = LoadPixmap(png)
        res.append(MultiContentEntryPixmapAlphaBlend(pos=(fhd(2 + addpos), fhd(3)), size=(fhd(25), fhd(25)), png=fpng, flags=BT_SCALE | BT_KEEP_ASPECT_RATIO))
    if addpos > 0:
        png = '' + carpetaimg + 'sel.png'
        if fileExists(png):
            fpng = LoadPixmap(png)
            res.append(MultiContentEntryPixmapAlphaBlend(pos=(fhd(1), fhd(7)), size=(fhd(8), fhd(13)), png=fpng, flags=BT_SCALE | BT_KEEP_ASPECT_RATIO))
    return res


class gesPlugins(Screen):
    if esHD():
        skin = '\n\t\t<screen name="gesPlugins" position="center,center" size="1500,915" backgroundColor="#000000" title="%s">\n\t\t\t<widget name="lista" position="12,100" size="1455,720" scrollbarMode="showOnDemand" zPosition="12" transparent="1" />\n\t\t\t<widget name="modo" position="12,12" size="1476,853" backgroundColor="#000000" foregroundColor="#ffffff" text=" " font="Regular; 21" halign="left" valign="top" zPosition="13" />\n\t\t\t<eLabel name="linea" position="12,871" size="1476,1" backgroundColor="#555555" />\n\t\t\t<widget name="key_red" position="412,874" size="330,37" transparent="1" font="Regular; 20" zPosition="14" valign="center" />\n\t\t\t<widget name="key_green" position="823,874" size="300,37" transparent="1" font="Regular; 20" zPosition="14" valign="center" />\n\t\t\t<widget name="key_help" position="799,874" backgroundColor="#000000" size="318,37" transparent="1" font="Regular; 20" halign="left" zPosition="14" valign="center" />\n\t\t\t<widget name="key_mode" position="12,12" size="1476,45" transparent="0" text=" " font="Regular; 16" halign="left" backgroundColor="#ffffff" foregroundColor="#000000" valign="center" noWrap="1" />\n\t\t\t<widget name="img_red" position="355,874" size="52,37" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/redHD.png" alphatest="blend" zPosition="15" />\n\t\t\t<widget name="img_green" position="766,874" size="52,37" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/greenHD.png" alphatest="blend" zPosition="15" />\n\t\t\t<widget name="img_ok" position="750,874" size="52,37" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/okHD.png" alphatest="blend" zPosition="15" />\n\t\t\t<widget name="key_yellow" position="67,874" size="900,37" transparent="1" font="Regular; 20" zPosition="15" valign="center" />\n\t\t\t<widget name="img_yellow" position="12,874" size="52,37" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/yellowHD.png" alphatest="blend" zPosition="15" />\n\t\t\t<widget name="img_exit" position="1116,874" size="52,37" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/exitHD.png" alphatest="blend" zPosition="15" />\n\t\t\t<widget name="key_exit" position="1173,874" backgroundColor="#000000" size="256,37" transparent="1" font="Regular; 20" halign="left" zPosition="14" valign="center" />\n\t\t\t<widget name="img_info" position="364,874" size="52,37" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/infoHD.png" alphatest="blend" zPosition="15" />\n\t\t\t<widget name="key_info" position="420,874" backgroundColor="#000000" size="348,37" transparent="1" font="Regular; 20" halign="left" zPosition="14" valign="center" />\n\t\t</screen>' % _('Plugins administrator openSPA')
    else:
        skin = '\n\t\t<screen name="gesPlugins" position="center,center" size="1000,610" backgroundColor="#000000" title="%s">\n\n\t\t<widget name="lista" position="8,67" size="970,480" scrollbarMode="showOnDemand" zPosition="12" transparent="1" />\n\t\t<widget name="modo" position="8,8" size="984,569" backgroundColor="#000000" foregroundColor="#ffffff" text=" " font="Regular; 21" halign="left" valign="top" zPosition="13" />\n\t\t<eLabel name="linea" position="8,581" size="984,1" backgroundColor="#555555" />\n\t\t\n\t\t<widget name="key_red" position="275,583" size="220,25" transparent="1" font="Regular; 20" zPosition="14" valign="center" />\n\n\t\t<widget name="key_green" position="549,583" size="200,25" transparent="1" font="Regular; 20" zPosition="14" valign="center" />\n\t\t<widget name="key_help" position="533,583" backgroundColor="#000000" size="212,25" transparent="1" font="Regular; 20" halign="left" zPosition="14" valign="center" />\n\t\t<widget name="key_mode" position="8,8" size="984,30" transparent="0" text=" " font="Regular; 16" halign="left" backgroundColor="#ffffff" foregroundColor="#000000" valign="center" noWrap="1" />\n\t\t<widget name="img_red" position="237,583" size="35,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/gesPluginsOpenSpa/img/red.png" alphatest="blend" zPosition="15" />\n\t\t<widget name="img_green" position="511,583" size="35,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/gesPluginsOpenSpa/img/green.png" alphatest="blend" zPosition="15" />\n\t\t<widget name="img_ok" position="500,583" size="35,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/gesPluginsOpenSpa/img/ok.png" alphatest="blend" zPosition="15" />\n\n\t\t<widget name="key_yellow" position="45,583" size="600,25" transparent="1" font="Regular; 20" zPosition="15" valign="center" />\n\t\t<widget name="img_yellow" position="8,583" size="35,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/gesPluginsOpenSpa/img/yellow.png" alphatest="blend" zPosition="15" />\n\n\t\t<widget name="img_exit" position="744,583" size="35,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/gesPluginsOpenSpa/img/exit.png" alphatest="blend" zPosition="15" />\n\t\t<widget name="key_exit" position="782,583" backgroundColor="#000000" size="171,25" transparent="1" font="Regular; 20" halign="left" zPosition="14" valign="center" />\n\t\t<widget name="img_info" position="243,583" size="35,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/gesPluginsOpenSpa/img/info.png" alphatest="blend" zPosition="15" />\n\t\t<widget name="key_info" position="280,583" backgroundColor="#000000" size="232,25" transparent="1" font="Regular; 20" halign="left" zPosition="14" valign="center" />\n\t\t</screen>' % _('Plugins administrator openSPA')

    def __init__(self, session, inicial = None, instance = None, args = 0):
        self.session = session
        Screen.__init__(self, session)
        self.faqs = []
        self.marcas = []
        self.cambiados = []
        self.nombres = []
        self['lista'] = IniciaSelListFaqs([])
        self.inicial = inicial
        self['modo'] = Label(_(''))
        self['key_help'] = Label(_('Continue'))
        self['key_mode'] = Label(_(''))
        self['img_red'] = Pixmap()
        self['img_green'] = Pixmap()
        self['img_yellow'] = Pixmap()
        self['img_ok'] = Pixmap()
        self['img_info'] = Pixmap()
        self['key_info'] = Label(_('Plugin Information'))
        self['img_exit'] = Pixmap()
        self['key_exit'] = Label(_('Exit'))
        self['key_red'] = Label(_('Cancel and Exit'))
        self['key_green'] = Label(_('Process'))
        self['key_yellow'] = Label(_('Delete plugin'))
        self['setupActions'] = ActionMap(['WizardActions',
         'DirectionActions',
         'ColorActions',
         'NumberActions',
         'MenuActions',
         'EPGSelectActions',
         'InfobarActions'], {'back': self.exit,
         'up': self.key_up,
         'down': self.key_down,
         'right': self.key_right,
         'left': self.key_left,
         'info': self.key_info,
         'ok': self.key_ok,
         'red': self.kred,
         'yellow': self.kyellow,
         'green': self.kgreen}, -2)
        self.escepciones = ',gesPluginsOpenSpa,spazeMenu,mhw2Timer,newChannelSelection,openSPATVGuide,scrInformation,spzOptions,InfoAz,VideoTune,SkinSelector,Satfinder,Hotplug,Videomode,PositionerSetup,SoftwareManager,NetworkBrowser,spzZapHistory,spaQButton,'
        cfiltrado = None
        self.onShow.append(self.aliniciar)
        self.actual = None
        self.Timertemp = eTimer()
        self.Timertemp.callback.append(self.buildList)
        self.iniciado = False
        self.bloqueado = False
        self.confirmar = False
        self['lista'].onSelectionChanged.append(self.muevesel)
        self['img_yellow'].hide()
        self['key_yellow'].hide()

    def ponmensaje(self, quemensaje, preguntar = None):
        self['modo'].show()
        self.bloqueado = True
        self['key_info'].hide()
        self['key_exit'].hide()
        self['img_info'].hide()
        self['img_exit'].hide()
        if preguntar:
            self.confirmar = True
            self['key_red'].show()
            self['img_red'].show()
            self['key_green'].show()
            self['img_green'].show()
            self['img_yellow'].hide()
            self['key_yellow'].hide()
            self['key_help'].hide()
            self['img_ok'].hide()
        else:
            self.confirmar = False
            self['key_red'].hide()
            self['img_red'].hide()
            self['key_green'].hide()
            self['img_green'].hide()
            self['img_yellow'].hide()
            self['key_yellow'].hide()
            if self.iniciado:
                self['key_help'].setText(_('Back'))
            self['key_help'].show()
            self['img_ok'].show()
        self['modo'].setText('\n' + quemensaje)

    def quitamensaje(self):
        if self.confirmar:
            return
        self.bloqueado = False
        self['key_help'].setText(_('Activate/Deactivate'))
        self['key_help'].show()
        self['key_red'].hide()
        self['img_red'].hide()
        self['key_green'].hide()
        self['img_green'].hide()
        self.muevesel()
        self['key_info'].show()
        self['img_ok'].show()
        self['modo'].hide()
        self['key_exit'].show()
        self['img_info'].show()
        self['img_exit'].show()

    def kred(self):
        if self.confirmar:
            self.confimar = False
            self.quitamensaje()
            self.cbsalir(False)
            return
        if self.bloqueado:
            self.quitamensaje()
            return

    def kgreen(self):
        if self.confirmar:
            self.confimar = False
            self.quitamensaje()
            self.cbsalir(True)
            return
        if self.bloqueado:
            self.quitamensaje()
            return

    def aliniciar(self):
        if not self.iniciado:
            self['key_mode'].setText(' ' + _('Loading') + '...' + _('Wait') + '...')
            if not self.inicial:
                laref = _('This plugin allow activate/deactivate plugins.') + '\n\n' + _('Select plugins pressing [OK] and press [EXIT] for process.') + '\n' + _('Press [INFO/EPG] for show information about the selected plugin.') + '\n\n' + _('Some plugins rely on others to run.') + '\n' + _('Some plugins are protected and can not be disabled.') + '\n\n' + _('When one or more plugins are activated/deactivated, the plugin list will be reloaded.') + ' ' + _('Some Plugins (with Autostart functions) require a restar GUI, and may appear a crash green screen.') + '\n\n' + _('When a plugin is disabled you can remove it by pressing [YELLOW]') + '\n\n' + _('Use this tool with care!')
                self.ponmensaje(laref)
            else:
                self.quitamensaje()
            self.cargapreguntas()
            self.iniciado = True
            self.Timertemp.start(200, True)

    def haypy(self, valor):
        return fileExists(valor + '/plugin.py') or fileExists(valor + '/plugin.pyc') or fileExists(valor + '/plugin.pyo')

    def esplugin(self, valor, rutaabs):
        cret = False
        cret = not valor + ' ' == ' ' and len(valor) > 1 and '.py' not in valor and '.tar.gz.back' not in valor and ',' + valor + ',' not in self.escepciones
        if cret and not self.haypy(rutaabs + valor):
            cret = False
        return cret

    def pluginx(self, valor, archivo):
        return valor.endswith('.tar.gz.back') and not self.haypy(archivo + valor.replace('.tar.gz.back', ''))

    def recargarLista(self):
        from Components.PluginComponent import plugins
        plugins.clearPluginList()
        plugins.readPluginList(resolveFilename(SCOPE_PLUGINS))

    def cargapreguntas(self, filtrado = None):
        self.faqs = []
        self.marcas = []
        self.cambiados = []
        self.nombres = []
        archivo = '/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/'
        ret = cargaosinfo('ls ' + archivo, True)
        listatemp = ret.split('\n')
        for ii in listatemp:
            ii = ii.replace('\n', '')
            if self.pluginx(ii, archivo):
                self.faqs.append('Extensions/spazeMenu/spzPlugins/' + ii)
                self.marcas.append(False)
                self.cambiados.append(False)
                self.nombres.append('')
            elif self.esplugin(ii, archivo):
                self.faqs.append('Extensions/spazeMenu/spzPlugins/' + ii)
                self.marcas.append(True)
                self.cambiados.append(False)
                try:
                    self.nombres.append(self.nombre_plugin('Extensions/spazeMenu/spzPlugins/' + ii))
                except:
                    self.nombres.append('')

        archivo = '/usr/lib/enigma2/python/Plugins/Extensions/'
        ret = cargaosinfo('ls ' + archivo, True)
        listatemp = ret.split('\n')
        for ii in listatemp:
            ii = ii.replace('\n', '')
            if self.pluginx(ii, archivo):
                self.faqs.append('Extensions/' + ii)
                self.marcas.append(False)
                self.cambiados.append(False)
                self.nombres.append('')
            elif self.esplugin(ii, archivo):
                self.faqs.append('Extensions/' + ii)
                self.marcas.append(True)
                self.cambiados.append(False)
                try:
                    self.nombres.append(self.nombre_plugin('Extensions/' + ii))
                except:
                    self.nombres.append('')

        archivo = '/usr/lib/enigma2/python/Plugins/SystemPlugins/'
        ret = cargaosinfo('ls ' + archivo, True)
        listatemp = ret.split('\n')
        for ii in listatemp:
            ii = ii.replace('\n', '')
            if self.pluginx(ii, archivo):
                self.faqs.append('SystemPlugins/' + ii)
                self.marcas.append(False)
                self.cambiados.append(False)
                self.nombres.append('')
            elif self.esplugin(ii, archivo):
                self.faqs.append('SystemPlugins/' + ii)
                self.marcas.append(True)
                self.cambiados.append(False)
                try:
                    self.nombres.append(self.nombre_plugin('SystemPlugins/' + ii))
                except:
                    self.nombres.append('')

    def buildList(self, modolista = 1):
        self['key_mode'].setText(' ' + _('Press [OK] to change plugin. The change will be confirmed when exit. Press [INFO/EPG] for plugin information.'))
        list = []
        conta = -1
        try:
            lalista = self['lista'].list
            if len(lalista) > 0:
                conta = self['lista'].getSelectionIndex()
        except:
            pass

        for i in range(0, len(self.faqs)):
            texto = '' + self.faqs[i]
            if conta == -1 and self.inicial:
                if '' + self.inicial in texto:
                    conta = i
            siinstalado = self.marcas[i]
            if self.cambiados[i]:
                self['key_exit'].setText(_('Exit') + '/' + _('Process'))
            list.append(IniciaSelListEntryPlugin(texto, siinstalado, self.cambiados[i], self.nombres[i], self.inicial))

        self['lista'].setList(list)
        if conta >= 0:
            try:
                self['lista'].moveToIndex(conta)
            except:
                pass

    def kyellow(self):
        if self.bloqueado:
            return
        try:
            lalista = self['lista'].list
            if len(self['lista'].list) <= 0:
                return
        except:
            return

        idx = self['lista'].getSelectionIndex()
        try:
            texto = fnombre(str(lalista[idx][0]))
        except:
            return

        plug = self.faqs[idx]
        if not self.marcas[idx] and not self.cambiados[idx] and plug.endswith('.tar.gz.back'):
            menadd = _('You are sure to DELETE the selected plugin?') + '\n[' + texto + ']'
            dei = self.session.openWithCallback(self.borrap, MessageBox, menadd, MessageBox.TYPE_YESNO)
            dei.setTitle(_('Delete PlugIn'))

    def borrap(self, ret = True):
        if ret:
            idx = self['lista'].getSelectionIndex()
            try:
                lalista = self['lista'].list
                texto = fnombre(str(lalista[idx][0]))
            except:
                return

            ruta = '/usr/lib/enigma2/python/Plugins/'
            plug = self.faqs[idx]
            ruta = ruta + plug
            orden = ''
            orden = orden + 'rm -f ' + ruta
            os.system(orden)
            cmens = _('The selected plugin has been removed.\n To reinstall go to openSPA download center.')
            dei = self.session.open(MessageBox, cmens + '\n[' + texto + ']', MessageBox.TYPE_INFO)
            dei.setTitle(_('Delete PlugIn'))
            self.cargapreguntas()
            self.buildList()

    def muevesel(self):
        if self.bloqueado:
            return
        try:
            lalista = self['lista'].list
            if len(self['lista'].list) <= 0:
                return
        except:
            return

        idx = self['lista'].getSelectionIndex()
        plug = self.faqs[idx]
        if not self.marcas[idx] and not self.cambiados[idx] and plug.endswith('.tar.gz.back'):
            self['key_yellow'].show()
            self['img_yellow'].show()
        else:
            self['key_yellow'].hide()
            self['img_yellow'].hide()

    def key_ok(self):
        if self.bloqueado:
            self.quitamensaje()
            return
        try:
            if len(self['lista'].list) <= 0:
                return
        except:
            return

        lalista = self['lista'].list
        idx = self['lista'].getSelectionIndex()
        try:
            texto = str(lalista[idx][0])
        except:
            return

        self.actual = idx
        self.key_okcb()

    def key_okcb(self, respuesta = True):
        templista = []
        if not respuesta:
            return
        valorcambiado = self.cambiados[self.actual]
        tcambiados = []
        for i in range(0, len(self.marcas)):
            if i == self.actual:
                templista.append(not self.marcas[i])
                tcambiados.append(not valorcambiado)
            else:
                templista.append(self.marcas[i])
                tcambiados.append(self.cambiados[i])

        self.marcas = []
        self.cambiados = []
        for i in range(0, len(templista)):
            self.marcas.append(templista[i])
            self.cambiados.append(tcambiados[i])

        self.buildList()

    def devwhere(self, tupla):
        pfun = {0: _('Extensions Menu'),
         1: _('Main Menu'),
         2: _('Plugins Menu'),
         3: _('Movielist'),
         4: _('Menu'),
         5: _('Autostart'),
         6: _('Wizard'),
         7: _('Session start'),
         8: _('Teletext'),
         9: _('Filescan'),
         10: _('Network setup'),
         11: _('Event info menu'),
         12: _('Network config'),
         13: _('Audio menu'),
         14: _('Software manager')}
        cret = ''
        sepa = ''
        for ele in tupla:
            if ele in pfun:
                cret = cret + sepa + pfun[ele]
            else:
                cret = cret + sepa + _('Function #') + str(ele)
            sepa = ','

        return cret

    def nombre_plugin(self, laruta):
        ruta = '/usr/lib/enigma2/python/Plugins/' + laruta
        pluginlist = plugins.getPlugins([0,
         1,
         2,
         3,
         4,
         5,
         6,
         7,
         8,
         9,
         10,
         11,
         12,
         13,
         14,
         15,
         16])
        cret = ''
        for plugin in pluginlist:
            if plugin.path + '' == ruta and plugin.name != 'Plugin' and plugin.name != '' and 'Project-Id-Version:' not in plugin.name:
                if ' (' + plugin.name + ')' not in cret:
                    cret = cret + ' (' + plugin.name + ')'

        return cret

    def key_info(self):
        if self.bloqueado:
            self.quitamensaje()
            return
        try:
            if len(self['lista'].list) <= 0:
                return
        except:
            return

        lalista = self['lista'].list
        ruta = '/usr/lib/enigma2/python/Plugins/'
        try:
            idx = self['lista'].getSelectionIndex()
            ruta = '/usr/lib/enigma2/python/Plugins/' + self.faqs[idx]
        except:
            return

        txtinfo = ''
        txtnom = ''
        txtdes = ''
        txtfun = ''
        pluginlist = plugins.getPlugins([0,
         1,
         2,
         3,
         4,
         5,
         6,
         7,
         8,
         9,
         10,
         11,
         12,
         13,
         14,
         15,
         16])
        for plugin in pluginlist:
            if plugin.path + '' == ruta:
                try:
                    nom = str(plugin.name)
                    if nom == 'Plugin':
                        nom = plugin.path.split('/')[-1]
                    if ',' + nom + ',' not in ',' + txtnom + ',' and nom != '' and 'Project-Id-Version:' not in nom:
                        if txtnom != '':
                            txtnom = txtnom + ','
                        txtnom = txtnom + nom
                except:
                    pass

                try:
                    nom = plugin.description
                    if ',' + nom + ',' not in ',' + txtdes + ',' and nom != '' and 'Project-Id-Version:' not in nom:
                        if txtdes != '':
                            txtdes = txtdes + ','
                        txtdes = txtdes + nom
                except:
                    pass

                try:
                    nom = self.devwhere(plugin.where)
                    if ',' + nom + ',' not in ',' + txtfun + ',' and nom != '':
                        if txtfun != '':
                            txtfun = txtfun + ','
                        txtfun = txtfun + nom
                except:
                    pass

        if txtnom != '':
            txtinfo = txtinfo + '' + _('Name') + ': ' + txtnom
        if txtdes != '':
            txtinfo = txtinfo + '\n\n' + _('Description') + ': ' + txtdes
        if txtfun != '':
            txtinfo = txtinfo + '\n\n' + _('Function') + ': ' + txtfun
        if txtinfo == '':
            txtinfo = '' + _('Name') + ': ' + fnombre(self.faqs[idx].split('/')[-1])
            if self.pluginx(self.faqs[idx], ruta.replace(ruta.split('/')[-1], '')):
                txtinfo = txtinfo + '\n\n********** ' + _('Deactivated') + ' **********'
        cmens = txtinfo
        self.ponmensaje(fnombre(self.faqs[idx]) + '\n-------------------------------------------------------------------------------------------------\n\n' + cmens)

    def key_right(self):
        if self.bloqueado:
            self.quitamensaje()
            return
        try:
            if len(self['lista'].list) <= 0:
                return
        except:
            return

        self['lista'].pageDown()

    def key_left(self):
        if self.bloqueado:
            self.quitamensaje()
            return
        try:
            if len(self['lista'].list) <= 0:
                return
        except:
            return

        self['lista'].pageUp()

    def key_up(self):
        if self.bloqueado:
            self.quitamensaje()
            return
        try:
            if len(self['lista'].list) <= 0:
                return
        except:
            return

        lalista = len(self['lista'].list)
        idx = self['lista'].getSelectionIndex()
        if idx == 0:
            self['lista'].moveToIndex(lalista - 1)
        else:
            self['lista'].up()

    def key_down(self):
        if self.bloqueado:
            self.quitamensaje()
            return
        try:
            if len(self['lista'].list) <= 0:
                return
        except:
            return

        lalista = len(self['lista'].list)
        idx = self['lista'].getSelectionIndex()
        if idx >= lalista - 1:
            self['lista'].moveToIndex(0)
        else:
            self['lista'].down()

    def exit(self):
        if self.confirmar:
            self.confirmar = False
        if self.bloqueado:
            self.quitamensaje()
            return
        archivoipk = ''
        lalista = self['lista'].list
        conta = 0
        for i in range(0, len(self.cambiados)):
            if self.cambiados[i]:
                if self.marcas[i]:
                    archivoipk = archivoipk + '[v] ' + _('Activate') + ' => '
                else:
                    archivoipk = archivoipk + '[x] ' + _('Desactivate') + ' => '
                archivoipk = archivoipk + fnombre(str(lalista[i][0]))
                archivoipk = archivoipk + '\n'
                conta = conta + 1

        if archivoipk != '':
            self['key_green'].setText(_('Process') + '(' + str(conta) + ')')
            self.ponmensaje(_('Do you want start process for activate/deactivate selected plugins?') + '\n-------------------------------------------------------------------------------------------------\n' + archivoipk + '-------------------------------------------------------------------------------------------------\n' + _('Press [GREEN] for process, [RED] for exit without process, [EXIT] for back to list.'), True)
            return
        self.salir()

    def activaplugin(self, id):
        ruta = '/usr/lib/enigma2/python/Plugins/'
        plug = self.faqs[id]
        ruta = ruta + plug
        orden = 'tar -xvzf ' + ruta + ' -C /'
        orden = orden + ';'
        orden = orden + 'rm -f ' + ruta
        os.system("echo '-------------- [V]" + plug + " ------------------'>>/tmp/gesPlugin.log")
        os.system("echo '" + orden + "'>>/tmp/gesPlugin.log")
        os.system(orden)
        if self.haypy(ruta.replace('.tar.gz.back', '')):
            cret = True
        else:
            cret = False
        return cret

    def quitaplugin(self, ruta):
        pluginlist = plugins.getPlugins([0,
         1,
         2,
         3,
         4,
         5,
         6,
         7,
         8,
         9,
         10,
         11,
         12,
         13,
         14,
         15,
         16])
        for plugin in pluginlist:
            if plugin.path + '' == ruta:
                try:
                    plugins.removePlugin(plugin)
                except:
                    pass

    def desactivaplugin(self, id):
        ruta = '/usr/lib/enigma2/python/Plugins/'
        plug = self.faqs[id]
        ruta = ruta + plug
        nombre = ruta.split('/')[-1]
        destino = ruta.replace(nombre, '')
        nombre = nombre + '.tar.gz.back'
        orden = 'tar -cvzf ' + destino + nombre + ' ' + ruta
        orden = orden + ';chmod 755 ' + destino + nombre
        os.system("echo '-------------- [X]" + plug + " -----------------------'>>/tmp/gesPlugin.log")
        os.system("echo '" + orden + "'>>/tmp/gesPlugin.log")
        os.system(orden)
        try:
            self.quitaplugin(ruta)
        except:
            pass

        cret = False
        if fileExists(destino + nombre):
            cret = True
            orden = 'rm -f -r ' + ruta
            os.system("echo '" + orden + "'>>/tmp/gesPlugin.log")
            os.system(orden)
        return cret

    def cbsalir(self, respuesta = False):
        if respuesta:
            archivoipk = ''
            lalista = self['lista'].list
            os.system('date>/tmp/gesPlugin.log')
            conta = 0
            maxp = 5
            for i in range(0, len(self.cambiados)):
                if self.cambiados[i]:
                    if self.marcas[i]:
                        if self.activaplugin(i):
                            if conta < maxp:
                                archivoipk = archivoipk + '[' + _('Reactivated') + '] '
                            elif conta == maxp:
                                archivoipk = archivoipk + '\n...'
                        elif conta < maxp:
                            archivoipk = archivoipk + '[' + _('Reactivated') + ' ' + _('ERROR') + '] '
                        elif conta == maxp:
                            archivoipk = archivoipk + '\n...'
                    elif self.desactivaplugin(i):
                        if conta < maxp:
                            archivoipk = archivoipk + '[' + _('Deactivated') + '] '
                        elif conta == maxp:
                            archivoipk = archivoipk + '\n...'
                    elif conta < maxp:
                        archivoipk = archivoipk + '[' + _('Deactivated') + ' ' + _('ERROR') + '] '
                    elif conta == maxp:
                        archivoipk = archivoipk + '\n...'
                    if conta < maxp:
                        archivoipk = archivoipk + fnombre(str(lalista[i][0]))
                        archivoipk = archivoipk + '\n'
                    conta = conta + 1

            menadd = _('Remember that some Plugins require restart GUI.') + '\n'
            dei = self.session.openWithCallback(self.salir2, MessageBox, menadd + _('Do you want restart GUI now?') + '\n\n' + archivoipk, MessageBox.TYPE_YESNO)
            dei.setTitle(_('Plugins administrator openSPA'))
            return
        self.salir()

    def salir2(self, respuesta = False):
        if respuesta:
            self.salir(True)
            return
        try:
            plugins.resetWarnings()
            plugins.readPluginList(resolveFilename(SCOPE_PLUGINS))
        except:
            pass

        self.salir()

    def salir(self, respuesta = False):
        if respuesta:
            self.session.open(TryQuitMainloop, 3)
        self.close()


def main(session, **kwargs):
    session.open(gesPlugins)


def Plugins(**kwargs):
    return PluginDescriptor(name=_('Plugins administrator openSPA'), description=_('Allow activate/Desactivate plugins for system optimize'), where=PluginDescriptor.WHERE_PLUGINMENU, fnc=main)
