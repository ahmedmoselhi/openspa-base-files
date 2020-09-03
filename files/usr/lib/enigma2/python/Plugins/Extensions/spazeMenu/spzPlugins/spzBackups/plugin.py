from Components.Label import Label
from Components.MenuList import MenuList
from Components.PluginComponent import plugins
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaBlend
from enigma import eListboxPythonMultiContent, gFont, BT_SCALE, BT_KEEP_ASPECT_RATIO
from enigma import eTimer
from Components.Pixmap import Pixmap
from Tools.LoadPixmap import LoadPixmap
from Components.ScrollLabel import ScrollLabel
from Components.Sources.StaticText import StaticText
from Components.FileList import MultiFileSelectList
from Screens.ChoiceBox import ChoiceBox
from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Components.ConfigList import ConfigListScreen
from Screens.MessageBox import MessageBox
from Screens.Console import Console
from Screens import Standby
from Plugins.Extensions.spazeMenu.sbar import openspaSB
from Screens.Standby import TryQuitMainloop
from Components.ActionMap import ActionMap
from Components.Button import Button
from Components.config import getConfigListEntry, configfile, ConfigEnableDisable, ConfigYesNo, ConfigText, ConfigClock, ConfigNumber, ConfigSelection, config, ConfigSubsection, ConfigSubList, ConfigSubDict, ConfigDirectory
from Tools import Notifications
from time import localtime, time, gmtime, strftime
from datetime import datetime
from Plugins.Extensions.spazeMenu.plugin import esHD, fhd
from Tools.Directories import fileExists, pathExists, resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE, SCOPE_SKIN
from Components.Language import language
from os import environ
import os
import gettext
lang = language.getLanguage()
environ['LANGUAGE'] = lang[:2]
gettext.bindtextdomain('enigma2', resolveFilename(SCOPE_LANGUAGE))
gettext.textdomain('enigma2')
gettext.bindtextdomain('spzBackups', '%s%s' % (resolveFilename(SCOPE_PLUGINS), 'Extensions/spazeMenu/spzPlugins/spzBackups/locale/'))

def _(txt):
    t = gettext.dgettext('spzBackups', txt)
    if t == txt:
        t = gettext.gettext(txt)
    return t


def formateafecha(lafecha = None, sepa = '-'):
    if not lafecha == None:
        t2 = lafecha
    else:
        t2 = localtime()
    cdia = str(strftime('%d', t2))
    cmes = str(strftime('%B', t2))
    cano = str(strftime('%Y', t2))
    csemana = str(strftime('%A', t2))
    return _(csemana) + ', ' + cdia + sepa + _(cmes) + sepa + cano


config.plugins.spzBackups = ConfigSubsection()
config.plugins.spzBackups.lastcopy = ConfigYesNo(default=True)
config.plugins.spzBackups.lastprofile = ConfigText(default='StandarCopy')
carpetaimg = '/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/spzBackups/img/'

def vaciarlista(cuallista):
    for iji in range(0, len(cuallista)):
        del cuallista[0]


class IniciaSelListRestore(MenuList):

    def __init__(self, list, enableWrapAround = False):
        MenuList.__init__(self, list, enableWrapAround, eListboxPythonMultiContent)
        self.l.setItemHeight(fhd(50))
        self.l.setFont(0, gFont('Regular', 19))
        self.l.setFont(1, gFont('Regular', 17))


def IniciaSelListEntryRestore(texto, texto2, tipo = 1):
    global carpetaimg
    res = [texto]
    res.append(MultiContentEntryText(pos=(fhd(70), fhd(4)), size=(1000, fhd(30)), font=0, text=texto))
    res.append(MultiContentEntryText(pos=(fhd(90), fhd(28)), size=(1000, fhd(30)), font=1, text=texto2, color=8947848))
    imagen = 'tarfs8.png'
    if tipo == 2:
        imagen = 'tare2fs8.png'
    elif tipo == 3:
        imagen = 'tare2hfs8.png'
    elif tipo == 4:
        imagen = 'tarspa-fs8.png'
    elif tipo == 5:
        imagen = 'tarspav-fs8.png'
    elif tipo == 6:
        imagen = 'tarspax-fs8.png'
    png = '' + carpetaimg + '' + imagen + ''
    if fileExists(png):
        fpng = LoadPixmap(png)
        res.append(MultiContentEntryPixmapAlphaBlend(pos=(fhd(2), fhd(2)), size=(fhd(48), fhd(48)), png=fpng, flags=BT_SCALE | BT_KEEP_ASPECT_RATIO))
    return res


class IniciaSelListFaqs(MenuList):

    def __init__(self, list, enableWrapAround = False):
        MenuList.__init__(self, list, enableWrapAround, eListboxPythonMultiContent)
        self.l.setItemHeight(30)
        self.l.setFont(0, gFont('Regular', 19))
        self.l.setFont(1, gFont('Regular', 17))


def IniciaSelListEntryFaqs(texto, yavista = False):
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


def ulineas(deque):
    try:
        cret = deque.split('\n')[-4] + '\n'
        cret = cret + deque.split('\n')[-3] + '\n'
        cret = cret + deque.split('\n')[-2] + '\n'
        cret = cret + deque.split('\n')[-1] + ''
    except:
        cret = ' '

    return cret


def cargaosinfo(orden, nulo = False, guardarlog = None, corto = False):
    ret = ''
    arlog = 'tempinfo'
    if not guardarlog == None:
        arlog = guardarlog
    if ';' in orden:
        prime = True
        lordenes = orden.split(';')
        for iji in lordenes:
            iji = iji.replace(';', '')
            if prime:
                os.system(iji + ' >/tmp/' + arlog)
            else:
                os.system(iji + ' >>/tmp/' + arlog)
            prime = False

    else:
        os.system(orden + ' >/tmp/' + arlog)
    booklist = None
    if fileExists('/tmp/' + arlog):
        try:
            booklist = open('/tmp/' + arlog, 'r')
        except:
            pass

        anterior = ''
        if booklist is not None:
            for oneline in booklist:
                try:
                    texto2 = '/'.join(oneline.split('/')[:-1]) + '/'
                    if not anterior == '' and len(texto2) > 3 and anterior == texto2 and corto:
                        ret = ret + oneline.replace(texto2, ' .../')
                    else:
                        ret = ret + oneline
                    anterior = texto2
                except:
                    ret = ret + oneline

            booklist.close()
        if guardarlog == None:
            os.system('rm /tmp/' + arlog)
    if len(ret) <= 1:
        if nulo == True:
            ret = ''
        else:
            ret = _('Error')
    if len(ret) > 9000:
        ultimas = ulineas(ret)
        ret = ret[0:9000] + '...\n...\n'
        ret = ret + ultimas
        ret = ret + '\n*** ' + _('Log file to long. Truncated. See file /tmp/spztBklog.log for complete view') + ' ***'
    return ret


def cargalista(self, nombre = 'StandarCopy'):
    lista = []
    listarutas = []
    booklist = None
    if not fileExists('/etc/openSPAv2_' + nombre + '.conf'):
        ret = cargaosinfo('cp /usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/spzBackups/etc/openSPAv2_' + nombre + '.conf /etc/')
    try:
        booklist = open('/etc/openSPAv2_' + nombre + '.conf')
    except:
        Notifications.AddPopup(text=_('Error creating profile') + ' ' + nombre, type=MessageBox.TYPE_ERROR, timeout=10, id='spzBackups')
        config.plugins.spzBackups.lastprofile.value = 'StandarCopy'
        config.plugins.spzBackups.lastprofile.save()
        config.plugins.spzBackups.save()
        configfile.save()
        return

    nombre = ''
    ruta = ''
    seccion = None
    incluir = False
    if booklist is not None:
        for oneline in booklist:
            cadena = oneline[0:1]
            linea = oneline.replace('\n', '')
            if oneline[0:3] == '###':
                nombre = linea.replace('#', '')
            elif oneline[0:2] == '##':
                ruta = linea.replace('#', '')
            elif cadena == '#':
                if not seccion == None:
                    lista.append((seccion.replace('<1>', '').replace('<0>', ''), listarutas, incluir))
                listarutas = []
                seccion = linea.replace('#', '')
                if '<1>' in seccion:
                    incluir = True
                else:
                    incluir = False
            elif len(linea) > 2 and linea[0:1] == '/':
                listarutas.append(linea)

        if not seccion == None:
            lista.append((seccion.replace('<1>', '').replace('<0>', ''), listarutas, incluir))
        booklist.close()
    return [(lista, ruta, nombre)]


def guardalista(listaconfig, lista):
    lalista = lista
    nombre = listaconfig[2][1].value + ''
    filenombre = nombre.replace(' ', '_').replace('\xc3\xb1', 'n')
    try:
        newbooklist = open('/etc/openSPAv2_' + filenombre + '.conf', 'w')
    except:
        dei = self.session.open(MessageBox, _('Error by writing backup config file !!!'), MessageBox.TYPE_ERROR)
        dei.setTitle(_('spazeTeam Backup/Restore').replace('spazeTeam', 'openSPA'))
        return False

    newbooklist.write('###' + nombre + '\n')
    newbooklist.write('\n')
    newbooklist.write('##' + listaconfig[3][1].value + '\n')
    newbooklist.write('\n')
    if newbooklist is not None:
        for i in range(0, len(lalista)):
            seccion = listaconfig[i + 5][2]
            incluir = listaconfig[i + 5][1].value
            if incluir == '1':
                anadido = '<1>'
            else:
                anadido = '<0>'
            newbooklist.write('#' + seccion + anadido + '\n')
            for j in range(0, len(lalista[i][1])):
                newbooklist.write('' + str(lalista[i][1][j]) + '\n')

            newbooklist.write('\n')

        newbooklist.close()
    return True


class spztRestore(Screen):
    if esHD():
        skin = '\n\t\t<screen name="azRestore" position="center,center" size="1500,915" title="%s">\n\t\t<widget name="lista" position="12,100" size="1455,750" scrollbarMode="showOnDemand" zPosition="12" itemHeight="42" />\n\t\t<widget name="modo" position="12,46" size="1455,45" backgroundColor="#ffffff" foregroundColor="#000000" text=" " font="Regular; 22" />\n\t\t<ePixmap name="new ePixmap" position="0,876" size="52,37" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/redHD.png" alphatest="blend" transparent="1" />\n\t\t<ePixmap name="new ePixmap" position="192,876" size="52,37" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/greenHD.png" alphatest="blend" transparent="1" />\n\t\t<ePixmap name="new ePixmap" position="960,876" size="52,37" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/yellowHD.png" alphatest="blend" transparent="1" />\n\t\t<ePixmap name="new ePixmap" position="1158,876" size="52,37" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/blueHD.png" alphatest="blend" transparent="1" />\n\t\t<widget name="key_red" position="51,877" size="243,33" transparent="1" text="Exit" font="Regular; 16"/>\n\t\t<widget name="key_green" position="243,877" size="693,33" transparent="1" text="File Info" font="Regular; 16"/>\n\t\t<widget name="key_yellow" position="1011,877" size="693,33" transparent="1" text="Restore" font="Regular; 16"/>\n\t\t<widget name="key_blue" position="1209,877" size="693,33" transparent="1" text="Restore" font="Regular; 16"/>\n\t\t<widget name="key_help" position="0,877" backgroundColor="#000000" size="1500,33" transparent="1" text=" " font="Regular; 15" halign="right" zPosition="10" />\n\t\t<widget name="key_mode" position="12,12" size="1500,33" transparent="1" text=" " font="Regular; 15" halign="left" />\n\t\t<widget name="barrapix_arr" position="0,0" zPosition="19" size="30,30" alphatest="blend" transparent="1" />\n\t\t<widget name="barrapix_abj" position="0,0" zPosition="19" size="30,30" alphatest="blend" transparent="1" />\t\n\t\t</screen>' % _('Restore')
    else:
        skin = '\n\t\t<screen name="azRestore" position="center,center" size="1000,610" title="%s">\n\t\t<widget name="lista" position="8,67" size="970,500" scrollbarMode="showOnDemand" zPosition="12" />\n\t\t<widget name="modo" position="8,31" size="970,30" backgroundColor="#ffffff" foregroundColor="#000000" text=" " font="Regular; 22" />\n\t\t<ePixmap name="new ePixmap" position="0,584" size="35,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/spzBackups/img/red.png" alphatest="blend" transparent="1" />\n\t\t<ePixmap name="new ePixmap" position="128,584" size="35,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/spzBackups/img/green.png" alphatest="blend" transparent="1" />\n\t\t<ePixmap name="new ePixmap" position="640,584" size="35,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/spzBackups/img/yellow.png" alphatest="blend" transparent="1" />\n\t\t<ePixmap name="new ePixmap" position="772,584" size="35,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/spzBackups/img/blue.png" alphatest="blend" transparent="1" />\n\t\t<widget name="key_red" position="34,585" size="162,22" transparent="1" text="Exit" font="Regular; 16"/>\n\t\t<widget name="key_green" position="162,585" size="462,22" transparent="1" text="File Info" font="Regular; 16"/>\n\t\t<widget name="key_yellow" position="674,585" size="462,22" transparent="1" text="Restore" font="Regular; 16"/>\n\t\t<widget name="key_blue" position="806,585" size="462,22" transparent="1" text="Restore" font="Regular; 16"/>\n\t\t<widget name="key_help" position="0,585" backgroundColor="#000000" size="1000,22" transparent="1" text=" " font="Regular; 15" halign="right" zPosition="10" />\n\t\t<widget name="key_mode" position="8,8" size="1000,22" transparent="1" text=" " font="Regular; 15" halign="left" />\n\t\t<widget name="barrapix_arr" position="0,0" zPosition="19" size="20,20" alphatest="blend" transparent="1" />\n\t\t<widget name="barrapix_abj" position="0,0" zPosition="19" size="20,20" alphatest="blend" transparent="1" />\t\n\t\t</screen>' % _('Restore')

    def __init__(self, session, instance = None, args = 0, ruta = None):
        self.session = session
        Screen.__init__(self, session)
        self.ruta = ruta
        self.cambiado = False
        self.faqs = []
        self.titulo = _('Select file to Restore')
        self['lista'] = IniciaSelListRestore([])
        self.modoactivo = 1
        self.categorias = ['Todo']
        self.vistas = []
        self['modo'] = Label(_(''))
        self['key_help'] = Label(_('To select another path, change the path of current profile') + '. ')
        self['key_mode'] = Label(_(' '))
        self['key_red'] = Label(_('Cancel'))
        self['key_green'] = Label(_('File info'))
        self['key_yellow'] = Label(_('File info'))
        self['key_blue'] = Label(_('More options'))
        self['setupActions'] = ActionMap(['WizardActions',
         'DirectionActions',
         'ColorActions',
         'NumberActions',
         'MenuActions',
         'EPGSelectActions',
         'InfobarActions'], {'green': self.key_info,
         'yellow': self.restore,
         'blue': self.opciones,
         'red': self.exit,
         'back': self.exit,
         'up': self.key_up,
         'down': self.key_down,
         'info': self.key_info,
         'ok': self.key_info}, -2)
        self.onLayoutFinish.append(self.buildList)
        self.onShow.append(self.iniscroll)
        self.iniciadoS = False
        self['barrapix_arr'] = Pixmap()
        self['barrapix_abj'] = Pixmap()

    def iniscroll(self):
        if not self.iniciadoS:
            self.actualizaScrolls()
            self.iniciadoS = True

    def actualizaScrolls(self):
        openspaSB(objectoself=self, nombrelista='lista', barra='barrapix', altoitem=50, imagen=True)

    def opciones(self):
        if len(self['lista'].list) > 0:
            askList = [(_('Cancel'), 'cancel'), (_('Convert to E2 last copy'), 'convert'), (_('Delete file'), 'delete')]
            dei = self.session.openWithCallback(self.cbopciones, ChoiceBox, title=_('Select option'), list=askList)
            dei.setTitle(_('Options') + '')

    def cbopciones(self, answer):
        answer = answer and answer[1]
        if answer == 'delete':
            self.deletefile()
        elif answer == 'convert':
            self.converte2()

    def deletefile(self):
        idx = self['lista'].getSelectionIndex()
        lalista = self['lista'].list
        texto = str(lalista[idx][0])
        laref = _('Delete this file copy?') + '\n' + texto + '\n' + _('This process can not be reversed!')
        dei = self.session.openWithCallback(self.cbdeletefile, MessageBox, laref, MessageBox.TYPE_YESNO, default=False)

    def cbdeletefile(self, respuesta):
        if respuesta:
            idx = self['lista'].getSelectionIndex()
            lalista = self['lista'].list
            texto = str(lalista[idx][0])
            try:
                DELfilename = self.ruta + '/' + texto + '.tar.gz'
                comando = 'rm -f "' + DELfilename + '"'
                ret = cargaosinfo(comando)
                DELfilename = self.ruta + '/' + texto + '.info'
                comando = 'rm -f "' + DELfilename + '"'
                ret = cargaosinfo(comando)
            except:
                pass

            self.buildList()

    def converte2(self):
        idx = self['lista'].getSelectionIndex()
        lalista = self['lista'].list
        texto = str(lalista[idx][0])
        laref = _('Convert this file to last E2 file backup?') + '\n' + texto + '\n' + _('When install new firm this copy will be restored!')
        dei = self.session.openWithCallback(self.cbconverte2, MessageBox, laref, MessageBox.TYPE_YESNO, default=False)

    def cbconverte2(self, respuesta):
        if respuesta:
            idx = self['lista'].getSelectionIndex()
            lalista = self['lista'].list
            texto = str(lalista[idx][0])
            iji = self.ruta + '/enigma2settingsbackup.tar.gz'
            if fileExists(iji):
                dir_stats = os.stat(iji)
                t2 = localtime(dir_stats.st_mtime)
                anadido = strftime('%Y-%m-%d-%H%M-', t2)
                dest = self.ruta + '/' + anadido + 'enigma2settingsbackup.tar.gz'
                try:
                    os.rename(iji, dest)
                except:
                    pass

            iji = self.ruta + '/' + texto + '.tar.gz'
            if fileExists(iji.replace('.tar.gz', '.info')):
                try:
                    DELfilename = iji.replace('.tar.gz', '.info')
                    comando = 'rm -f "' + DELfilename + '"'
                    ret = cargaosinfo(comando)
                except:
                    pass

            try:
                os.rename(iji, self.ruta + '/enigma2settingsbackup.tar.gz')
            except:
                pass

            self.buildList()

    def restore(self):
        if len(self['lista'].list) > 0:
            idx = self['lista'].getSelectionIndex()
            lalista = self['lista'].list
            texto = str(lalista[idx][0])
            laref = _('Restore this copy?') + '\n' + texto + '\n' + _('This process can not be reversed!')
            dei = self.session.openWithCallback(self.cbrestore, MessageBox, laref, MessageBox.TYPE_YESNO)

    def cbrestore(self, respuesta):
        if respuesta:
            self.cambiado = True
            idx = self['lista'].getSelectionIndex()
            lalista = self['lista'].list
            texto = str(lalista[idx][0])
            self.close(texto)

    def Humanizer(self, size, mostrarbytes = False):
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

    def cargapreguntas(self, filtrado = None):
        self.faqs = []
        ret = cargaosinfo('ls -t ' + self.ruta + '/*.tar.gz')
        listatemp = ret.split('\n')
        for iji in listatemp:
            iji = iji.replace('\n', '')
            if len(iji) > 2 and fileExists(iji):
                dir_stats = os.stat(iji)
                texto2 = _('Date') + ': ' + formateafecha(localtime(dir_stats.st_mtime)) + ' :: ' + _('Size') + ': ' + str(self.Humanizer(dir_stats.st_size, mostrarbytes=False))
                texto = iji.replace('\n', '').replace(self.ruta, '').replace('.tar.gz', '').replace('/', '')
                ertipo = 2
                if len(texto + ' ') > 2:
                    if iji == self.ruta + '/enigma2settingsbackup.tar.gz':
                        ertipo = 3
                        texto2 = 'E2-' + _('Default copy') + ' :: ' + texto2
                    elif iji == self.ruta + '/openspabackup.tar.gz':
                        ertipo = 4
                        texto2 = 'openSPA-' + _('Upgrade copy pending') + ' :: ' + texto2
                    elif iji == self.ruta + '/openspabackup.done.tar.gz':
                        ertipo = 5
                        texto2 = 'openSPA-' + _('Upgrade copy restored') + ' :: ' + texto2
                    elif iji == self.ruta + '/openspabackup.cancel.tar.gz':
                        ertipo = 6
                        texto2 = 'openSPA-' + _('Upgrade copy canceled') + ' :: ' + texto2
                    elif fileExists(iji.replace('.tar.gz', '.info')):
                        ertipo = 1
                        texto2 = 'spzt-' + _('Copy') + ' :: ' + texto2
                    else:
                        texto2 = 'E2-' + _('Copy') + ' :: ' + texto2
                    self.faqs.append((texto, texto2, ertipo))

    def buildList(self, modolista = 1):
        self['key_mode'].setText(_('To select another path, change the path of current profile') + '. ')
        titulo = _(self.titulo)
        cfiltrado = None
        self['key_help'].setText(_(' '))
        self['key_green'].setText(_('File info'))
        self['key_yellow'].setText(_('Restore'))
        self['key_blue'].setText(_('More options'))
        self.cargapreguntas(cfiltrado)
        list = []
        conta = 0
        for i in range(0, len(self.faqs)):
            texto = '' + self.faqs[i][0]
            texto2 = '' + self.faqs[i][1]
            tipo = self.faqs[i][2]
            list.append(IniciaSelListEntryRestore(texto, texto2, tipo))

        self['modo'].setText(titulo)
        self['lista'].setList(list)
        self.actualizaScrolls()

    def key_info(self):
        if len(self['lista'].list) > 0:
            lalista = self['lista'].list
            idx = self['lista'].getSelectionIndex()
            texto = str(lalista[idx][0])
            cret = "cat '" + self.ruta + '/' + texto + ".info'; echo '******* " + _('List files for .tar') + " *******'; tar -tzf '" + self.ruta + '/' + texto + ".tar.gz'"
            dei = self.session.open(infoSel, textoinfo=_('Retrieving file info') + '...', titulo=texto, comando=cret)

    def key_up(self):
        self['lista'].up()

    def key_down(self):
        self['lista'].down()

    def exit(self):
        self.close(None)


class selPlugins(Screen):
    if esHD():
        skin = '\n\t\t<screen name="azSel" position="center,center" size="1500,915" title="%s">\n\n\t\t<widget name="lista" position="12,100" size="1455,735" scrollbarMode="showOnDemand" zPosition="12" itemHeight="42" />\n\t\t<widget name="modo" position="12,46" size="1455,45" backgroundColor="#ffffff" foregroundColor="#000000" text=" " font="Regular; 22" />\n\n\t\t<ePixmap name="new ePixmap" position="0,876" size="52,37" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/redHD.png" alphatest="blend" transparent="1" />\n\t\t<widget name="key_red" position="51,877" size="243,33" transparent="1" text="Exit" font="Regular; 16"/>\n\n\t\t<widget name="key_green" position="1123,877" size="693,33" transparent="1" text="Remote" font="Regular; 16"/>\n\t\t<widget name="key_help" position="8,585" backgroundColor="#000000" size="1284,33" transparent="1" text="This help is avaible in tv screen pressing home menu key" font="Regular; 15" halign="left" zPosition="10" />\n\t\t<widget name="key_mode" position="12,12" size="1027,33" transparent="1" text=" " font="Regular; 15" halign="left" />\n\t\t<widget name="barrapix_arr" position="0,0" zPosition="19" size="30,30" alphatest="blend" transparent="1" />\n\t\t<widget name="barrapix_abj" position="0,0" zPosition="19" size="30,30" alphatest="blend" transparent="1" />\t\n\t\t</screen>' % _('Select')
    else:
        skin = '\n\t\t<screen name="azSel" position="center,center" size="1000,610" title="%s">\n\n\t\t<widget name="lista" position="8,67" size="970,490" scrollbarMode="showOnDemand" zPosition="12" />\n\t\t<widget name="modo" position="8,31" size="970,30" backgroundColor="#ffffff" foregroundColor="#000000" text=" " font="Regular; 22" />\n\n\t\t<ePixmap name="new ePixmap" position="0,584" size="35,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/spzBackups/img/red.png" alphatest="blend" transparent="1" />\n\t\t<widget name="key_red" position="34,585" size="162,22" transparent="1" text="Exit" font="Regular; 16"/>\n\n\t\t<widget name="key_green" position="749,585" size="462,22" transparent="1" text="Remote" font="Regular; 16"/>\n\t\t<widget name="key_help" position="8,585" backgroundColor="#000000" size="856,22" transparent="1" text="This help is avaible in tv screen pressing home menu key" font="Regular; 15" halign="left" zPosition="10" />\n\t\t<widget name="key_mode" position="8,8" size="685,22" transparent="1" text=" " font="Regular; 15" halign="left" />\n\t\t<widget name="barrapix_arr" position="0,0" zPosition="19" size="20,20" alphatest="blend" transparent="1" />\n\t\t<widget name="barrapix_abj" position="0,0" zPosition="19" size="20,20" alphatest="blend" transparent="1" />\t\n\t\t</screen>' % _('Select')

    def __init__(self, session, listaini = [], titulo = 'PlugIns', instance = None, args = 0):
        self.session = session
        Screen.__init__(self, session)
        if listaini == None:
            listaini = []
        self.cambiado = False
        self.listaini = listaini
        self.faqs = []
        self.titulo = titulo
        self['lista'] = IniciaSelListFaqs([])
        self.modoactivo = 1
        self.categorias = ['Todo']
        self.vistas = []
        self['modo'] = Label(_(''))
        self['key_help'] = Label(_(''))
        self['key_mode'] = Label(_(''))
        self['key_red'] = Label(_('Clear'))
        self['key_green'] = Label(_(' '))
        self['setupActions'] = ActionMap(['WizardActions',
         'DirectionActions',
         'ColorActions',
         'NumberActions',
         'MenuActions',
         'EPGSelectActions',
         'InfobarActions'], {'green': self.volver,
         'red': self.vacia,
         'back': self.volver,
         'up': self.key_up,
         'down': self.key_down,
         'info': self.key_info,
         'ok': self.key_ok}, -2)
        self.onLayoutFinish.append(self.buildList)
        self.onShow.append(self.iniscroll)
        self.iniciadoS = False
        self['barrapix_arr'] = Pixmap()
        self['barrapix_abj'] = Pixmap()

    def iniscroll(self):
        if not self.iniciadoS:
            self.actualizaScrolls()
            self.iniciadoS = True

    def actualizaScrolls(self):
        openspaSB(objectoself=self, nombrelista='lista', barra='barrapix', altoitem=30, imagen=True)

    def vacia(self):
        laref = _('Delete all entries from list?')
        dei = self.session.openWithCallback(self.resvacia, MessageBox, laref, MessageBox.TYPE_YESNO)

    def resvacia(self, respuesta):
        if respuesta:
            vaciarlista(self.listaini)
            self.buildList()

    def cargapreguntas(self, filtrado = None):
        self.categorias = ['Todo']
        self.faqs = []
        if self.titulo == _('PlugIns'):
            archivo = '/usr/lib/enigma2/python/Plugins/Extensions/'
            ret = cargaosinfo('ls ' + archivo, True)
            listatemp = ret.split('\n')
            for ii in listatemp:
                ii = ii.replace('\n', '')
                if not ii + ' ' == ' ' and len(ii) > 1 and '.py' not in ii:
                    self.faqs.append('Extensions/' + ii)

            archivo = '/usr/lib/enigma2/python/Plugins/SystemPlugins/'
            ret = cargaosinfo('ls ' + archivo, True)
            listatemp = ret.split('\n')
            for ii in listatemp:
                ii = ii.replace('\n', '')
                if not ii + ' ' == ' ' and len(ii) > 1 and '.py' not in ii:
                    self.faqs.append('SystemPlugins/' + ii)

        else:
            ret = cargaosinfo('find /share/enigma2/ -name skin.xml -mindepth 2', True)
            listatemp = ret.split('\n')
            for ii in listatemp:
                ii = ii.replace('\n', '')
                if not ii + ' ' == ' ' and len(ii) > 1:
                    self.faqs.append('' + ii.replace('/share/enigma2/', '').replace('/skin.xml', ''))

    def buildList(self, modolista = 1):
        self['key_mode'].setText(_('Press [OK] to select/unselect'))
        titulo = ' ' + _('Select') + ' ' + _(self.titulo)
        cfiltrado = None
        self['key_help'].setText(_(' '))
        self['key_green'].setText(_(' '))
        self['key_red'].setText(_('Clear'))
        self.modoactivo = modolista
        self.cargapreguntas(cfiltrado)
        list = []
        conta = 0
        for i in range(0, len(self.faqs)):
            texto = '' + self.faqs[i]
            if '/usr/lib/enigma2/python/Plugins/' + texto + '/' in self.listaini or '/share/enigma2/' + texto + '/' in self.listaini:
                vista = True
                conta = conta + 1
            else:
                vista = False
            list.append(IniciaSelListEntryFaqs(texto, vista))

        self['modo'].setText(titulo + ' (' + str(conta) + ' ' + _('of') + ' ' + str(len(self.faqs)) + '):')
        self['lista'].setList(list)

    def key_ok(self):
        lalista = self['lista'].list
        idx = self['lista'].getSelectionIndex()
        self.cambiado = True
        texto = str(lalista[idx][0])
        if '/usr/lib/enigma2/python/Plugins/' + texto + '/' in self.listaini or '/share/enigma2/' + texto + '/' in self.listaini:
            for iji in range(0, len(self.listaini)):
                if '/usr/lib/enigma2/python/Plugins/' + texto + '/' == self.listaini[iji] or '/share/enigma2/' + texto + '/' == self.listaini[iji]:
                    del self.listaini[iji]
                    break

        elif self.titulo == _('PlugIns'):
            self.listaini.append('/usr/lib/enigma2/python/Plugins/' + texto + '/')
        else:
            self.listaini.append('/share/enigma2/' + texto + '/')
        self.buildList()

    def acambiado(self, respuesta):
        if respuesta:
            self.close(self.listaini)
        else:
            self.close(None)

    def key_info(self):
        pass

    def key_up(self):
        self['lista'].up()

    def key_down(self):
        self['lista'].down()

    def exit(self):
        self.close(True)

    def volver(self):
        if self.cambiado:
            self.close(True)
        else:
            self.close(None)


class infoSel(Screen):
    if esHD():
        skin = '\n\t\t<screen name="azbInfo" position="center,center" size="1500,915" title="%s">\n\t\t<widget name="texto" position="12,100" size="1455,735"  zPosition="12" font="Regular; 18" itemHeight="42" />\n\t\t<widget name="modo" position="12,46" size="1455,45" backgroundColor="#ffffff" foregroundColor="#000000" text=" " font="Regular; 22" />\n\t\t<ePixmap name="new ePixmap" position="0,876" size="52,37" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/redHD.png" alphatest="blend" transparent="1" />\n\t\t<widget name="key_red" position="51,877" size="243,33" transparent="1" text="Exit" font="Regular; 16"/>\n\t\t<widget name="key_green" position="1123,877" size="693,33" transparent="1" text="Remote" font="Regular; 16"/>\n\t\t<widget name="key_help" position="8,585" backgroundColor="#000000" size="1284,33" transparent="1" text="This help is avaible in tv screen pressing home menu key" font="Regular; 15" halign="left" zPosition="10" />\n\t\t<widget name="key_mode" position="12,12" size="1027,33" transparent="1" text=" " font="Regular; 15" halign="left" />\n\t\t<widget name="barrapix_arr" position="12,100" zPosition="19" size="1455,735" alphatest="blend" transparent="1" />\n\t\t<widget name="barrapix_abj" position="0,0" zPosition="19" size="30,30" alphatest="blend" transparent="1" />\t\n\t\t</screen>' % _('Information')
    else:
        skin = '\n\t\t<screen name="azbInfo" position="center,center" size="1000,610" title="%s">\n\t\t<widget name="texto" position="8,67" size="970,490"  zPosition="12" font="Regular; 18" />\n\t\t<widget name="modo" position="8,31" size="970,30" backgroundColor="#ffffff" foregroundColor="#000000" text=" " font="Regular; 22" />\n\t\t<ePixmap name="new ePixmap" position="0,584" size="35,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/spzBackups/img/red.png" alphatest="blend" transparent="1" />\n\t\t<widget name="key_red" position="34,585" size="162,22" transparent="1" text="Exit" font="Regular; 16"/>\n\t\t<widget name="key_green" position="749,585" size="462,22" transparent="1" text="Remote" font="Regular; 16"/>\n\t\t<widget name="key_help" position="8,585" backgroundColor="#000000" size="856,22" transparent="1" text="This help is avaible in tv screen pressing home menu key" font="Regular; 15" halign="left" zPosition="10" />\n\t\t<widget name="key_mode" position="8,8" size="685,22" transparent="1" text=" " font="Regular; 15" halign="left" />\n\t\t<widget name="barrapix_arr" position="8,67" zPosition="19" size="970,490" alphatest="blend" transparent="1" />\n\t\t<widget name="barrapix_abj" position="0,0" zPosition="19" size="20,20" alphatest="blend" transparent="1" />\t\n\t\t</screen>' % _('Information')

    def __init__(self, session, textoinfo = ' ', titulo = ' ', comando = None, instance = None, args = 0):
        self.session = session
        Screen.__init__(self, session)
        self.textoinfo = textoinfo
        self.titulo = titulo
        self['texto'] = ScrollLabel(' ')
        self.comando = comando
        self['modo'] = Label(_(''))
        self['key_help'] = Label(_(''))
        self['key_mode'] = Label(_(''))
        self.TimerTemp = eTimer()
        self.TimerTemp.callback.append(self.ejecutar)
        self.TimerSalir = eTimer()
        self.TimerSalir.callback.append(self.exit)
        self['key_red'] = Label(_('Exit'))
        self['key_green'] = Label(_(' '))
        self['barrapix_arr'] = Pixmap()
        self['barrapix_abj'] = Pixmap()
        self['setupActions'] = ActionMap(['WizardActions',
         'DirectionActions',
         'ColorActions',
         'NumberActions',
         'MenuActions',
         'EPGSelectActions',
         'InfobarActions'], {'blue': self.bkexit,
         'red': self.exit,
         'back': self.exit,
         'left': self.key_up,
         'right': self.key_down,
         'up': self.key_up,
         'down': self.key_down,
         'ok': self.exit}, -2)
        self.onLayoutFinish.append(self.buildList)

    def key_up(self):
        self.TimerSalir.stop()
        self['texto'].pageUp()

    def key_down(self):
        self.TimerSalir.stop()
        self['texto'].pageDown()

    def ejecutar(self):
        ret = cargaosinfo(self.comando, nulo=True, guardarlog='spztBklog.log', corto=True)
        self['texto'].setText(ret)
        if not self.comando[0:4] == 'cat ':
            dei = self.session.open(MessageBox, self.titulo + ' ' + _('finished!'), MessageBox.TYPE_INFO, timeout=15)
            self.TimerSalir.start(20000, True)

    def buildList(self, modolista = 1):
        self['key_help'].setText(_(' '))
        self['key_green'].setText(_(' '))
        self['modo'].setText(self.titulo)
        self['texto'].setText(self.textoinfo)
        if not self.comando == None:
            self.TimerTemp.start(1000, True)
        openspaSB(objectoself=self, nombrelista='barrapix', barra='barrapix', altoitem=25, imagen=True)

    def bkexit(self):
        self.TimerSalir.stop()
        if not self.comando == None:
            self.close('no')
        else:
            self.close()

    def exit(self):
        self.TimerSalir.stop()
        if not self.comando == None:
            self.close('si')
        else:
            self.close()


class spzCopiar(ConfigListScreen, Screen):
    if esHD():
        skin = '\n\t\t\t<screen position="center,center" size="930,907" title="%s"  zPosition="11">\n\t\t\t<widget name="config" position="0,0" size="930,862" scrollbarMode="showOnDemand" itemHeight="42" />\n\t\t\t<widget name="key_red" position="0,844" size="180,60" valign="center" halign="center" backgroundColor="#000000" foregroundColor="#ffffff" zPosition="4" font="Regular;17" transparent="1"/> \n\t\t\t<widget name="key_green" position="210,844" size="180,60" valign="center" halign="center" backgroundColor="#000000" foregroundColor="#ffffff" zPosition="4" font="Regular;17" transparent="1"/>  \n\t\t\t<widget name="key_yellow" position="420,844" size="180,60" valign="center" halign="center" backgroundColor="#000000" foregroundColor="#ffffff" zPosition="4" font="Regular;17" transparent="1"/> \n\t\t\t<widget name="key_blue" position="705,844" size="180,60" valign="center" halign="center" backgroundColor="#000000" foregroundColor="#ffffff" zPosition="4" font="Regular;17" transparent="1"/> \n\t\t\t<ePixmap name="red"    position="0,855"   zPosition="2" size="195,60" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/rednHD.png" transparent="1" alphatest="blend" />\n\t\t\t<ePixmap name="green"  position="210,855" zPosition="2" size="195,60" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/greennHD.png" transparent="1" alphatest="blend" />\n\t\t\t<ePixmap name="yellow"  position="420,855" zPosition="2" size="195,60" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/yellownHD.png" transparent="1" alphatest="blend" />\n\t\t\t<ePixmap name="blue"  position="705,855" zPosition="2" size="195,60" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/bluenHD.png" transparent="1" alphatest="blend" />\n\t\t\t<widget name="barrapix_arr" position="0,0" zPosition="19" size="30,30" alphatest="blend" transparent="1" />\n\t\t\t<widget name="barrapix_abj" position="0,0" zPosition="19" size="30,30" alphatest="blend" transparent="1" />\n\t\t\t<widget name="tapa" position="0,180" size="930,660" valign="center" halign="left" font="Regular;19" transparent="0" zPosition="9"/> \n\t\t\t</screen>' % (_('spazeTeam ').replace('spazeTeam', 'openSPA') + ' ' + _('Backup'))
    else:
        skin = '\n\t\t\t<screen position="center,center" size="620,605" title="%s"  zPosition="11">\n\t\t\t<widget name="config" position="0,0" size="620,575" scrollbarMode="showOnDemand" />\n\n\t\t\t<widget name="key_red" position="0,563" size="120,40" valign="center" halign="center" backgroundColor="#000000" foregroundColor="#ffffff" zPosition="4" font="Regular;17" transparent="1"/> \n\t\t\t<widget name="key_green" position="140,563" size="120,40" valign="center" halign="center" backgroundColor="#000000" foregroundColor="#ffffff" zPosition="4" font="Regular;17" transparent="1"/>  \n\t\t\t<widget name="key_yellow" position="280,563" size="120,40" valign="center" halign="center" backgroundColor="#000000" foregroundColor="#ffffff" zPosition="4" font="Regular;17" transparent="1"/> \n\t\t\t<widget name="key_blue" position="470,563" size="120,40" valign="center" halign="center" backgroundColor="#000000" foregroundColor="#ffffff" zPosition="4" font="Regular;17" transparent="1"/> \n\n\t\t\t\n\t\t\t<ePixmap name="red"    position="0,570"   zPosition="2" size="130,40" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/spzBackups/img/redn.png" transparent="1" alphatest="on" />\n\t\t\t<ePixmap name="green"  position="140,570" zPosition="2" size="130,40" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/spzBackups/img/greenn.png" transparent="1" alphatest="on" />\n\t\t\t\n\t\t\t<ePixmap name="yellow"  position="280,570" zPosition="2" size="130,40" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/spzBackups/img/yellown.png" transparent="1" alphatest="on" />\n\t\t\t<ePixmap name="blue"  position="470,570" zPosition="2" size="130,40" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/spzBackups/img/bluen.png" transparent="1" alphatest="on" />\n\t\t\t<widget name="barrapix_arr" position="0,0" zPosition="19" size="20,20" alphatest="blend" transparent="1" />\n\t\t\t<widget name="barrapix_abj" position="0,0" zPosition="19" size="20,20" alphatest="blend" transparent="1" />\n\t\t\t<widget name="tapa" position="0,120" size="620,440" valign="center" halign="left" font="Regular;19" transparent="0" zPosition="9"/> \n\t\t\t</screen>' % (_('spazeTeam ').replace('spazeTeam', 'openSPA') + ' ' + _('Backup'))

    def __init__(self, session):
        self.session = session
        Screen.__init__(self, session)
        self.iniciado = False
        self.list = []
        self.lista = []
        self.needrestart = False
        self.cambiado = False
        self.perfiles = []
        nombre = 'StandarCopy'
        if not pathExists('/hdd/backup'):
            try:
                os.mkdir('/hdd/backup')
            except:
                pass

        if not fileExists('/etc/openSPAv2_' + nombre + '.conf'):
            ret = cargaosinfo('cp /usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/spzBackups/etc/openSPAv2_*.conf /etc/')
        ret = cargaosinfo('ls /etc/openSPAv2_*')
        listatemp = ret.split('\n')
        for iji in listatemp:
            texto = iji.replace('\n', '').replace('/etc/', '').replace('.conf', '')
            texto2 = texto.replace('openSPAv2_', '')
            if len(texto + ' ') > 2:
                self.perfiles.append((texto2, _(texto2)))

        self.nombretemp = ''
        self.crealista()
        ConfigListScreen.__init__(self, self.list)
        self.textoini = '- ' + formateafecha()
        self.textoini = self.textoini + '\n\n' + _('For custom copy press [DOWN] key and choose profile, and customize wath sections/plugins/skin/files you want backup.')
        self.textoini = self.textoini + '\n\n' + _('Press [BLUE] for go to restore screen.')
        self['key_red'] = Button(_(' '))
        self['key_green'] = Button(_(' '))
        self['key_blue'] = Button(_('Restore') + '...')
        self['key_yellow'] = Button(_(' '))
        self['tapa'] = Label(self.textoini)
        self['setupActions'] = ActionMap(['WizardActions',
         'ColorActions',
         'DirectionActions',
         'NumberActions',
         'MenuActions'], {'ok': self.pasa,
         'red': self.iniciacopia,
         'green': self.verarchivos,
         'yellow': self.guardar,
         'left': self.key_Left,
         'right': self.key_Right,
         'blue': self.restaura,
         'up': self.key_U,
         'down': self.key_D,
         'back': self.cancel}, -2)
        self.onShow.append(self.iniscroll)
        self.iniciadoS = False
        self['barrapix_arr'] = Pixmap()
        self['barrapix_abj'] = Pixmap()

    def iniscroll(self):
        if not self.iniciadoS:
            self.actualizaScrolls()
            self.iniciadoS = True
        try:
            self['tapa'].setText(self.textoini + '\n\n' + _('Last backup file') + ':\n' + self.devultimo())
        except:
            pass

    def devultimo(self):
        try:
            ruta = self['config'].list[3][1].value + '/'
        except:
            return 'NA'

        ret = cargaosinfo('ls ' + ruta + '*.tar.gz -t -c -w 1')
        lista = ret.split('\n')
        cret = _('No backups files found') + '(' + ruta + ')'
        for ele in lista:
            ele = ele.replace('\n', '')
            if '.tar.gz' in ele:
                cret = ele
                try:
                    dir_stats = os.stat(cret)
                    cret = '   ' + cret + '\n   ' + formateafecha(localtime(dir_stats.st_mtime)) + ' :: ' + str(self.Humanizer(dir_stats.st_size, mostrarbytes=False))
                except:
                    pass

                break

        return cret

    def Humanizer(self, size, mostrarbytes = False):
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

    def actualizaScrolls(self):
        openspaSB(objectoself=self, nombrelista='config', barra='barrapix', altoitem=25, imagen=True)

    def crealista(self, archivilista = None):
        self.list = []
        if self.iniciado:
            dei = self.session.open(MessageBox, _('Loading Profile...'), MessageBox.TYPE_INFO)
            dei.setTitle(_('Wait...'))
        if archivilista == None:
            try:
                if len(config.plugins.spzBackups.lastprofile.value) > 0 and not config.plugins.spzBackups.lastprofile.value == None:
                    archivilista = config.plugins.spzBackups.lastprofile.value
                else:
                    archivilista = 'StandarCopy'
            except:
                archivilista = 'StandarCopy'

        retlista = cargalista(self, archivilista)
        if not retlista == None:
            self.lista = retlista[0][0]
            self.list.append(getConfigListEntry(_('Select option'), ConfigSelection(default='', choices=[('', '')]), None, None))
            self.list.append(getConfigListEntry(_('---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------'), ConfigSelection(default='', choices=[('', '')]), None, None))
            self.list.append(getConfigListEntry(_('Profile'), ConfigSelection(default=archivilista, choices=self.perfiles), None, None))
            self.list.append(getConfigListEntry(_('Save backup into location'), ConfigText(default=retlista[0][1], visible_width=50, fixed_size=False), None, self.openLocationBox))
            self.list.append(getConfigListEntry(_('---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------'), ConfigSelection(default='', choices=[('', '')]), None, None))
            for ij in range(0, len(self.lista)):
                if self.lista[ij][2]:
                    defa = '1'
                else:
                    defa = '0'
                if _(self.lista[ij][0]) == _('PlugIns'):
                    self.list.append(getConfigListEntry(_(self.lista[ij][0]), ConfigSelection(default=defa, choices=[('1', _('Press [OK] to choose PlugIns')), ('0', _('None'))]), 'PlugIns', None))
                elif _(self.lista[ij][0]) == _('Skins'):
                    self.list.append(getConfigListEntry(_(self.lista[ij][0]), ConfigSelection(default=defa, choices=[('1', _('Press [OK] to choose Skins')), ('0', _('None'))]), 'Skins', None))
                elif _(self.lista[ij][0]) == _('Other files/folders'):
                    self.list.append(getConfigListEntry(_(self.lista[ij][0]), ConfigSelection(default=defa, choices=[('1', _('Press [OK] to choose Files')), ('0', _('None'))]), 'Other files/folders', None))
                else:
                    self.list.append(getConfigListEntry(_(self.lista[ij][0]), ConfigSelection(default=defa, choices=[('1', _('INCLUDE')), ('0', _('No'))]), self.lista[ij][0], None))

        if self.iniciado:
            dei.close()
        self.iniciado = True

    def openpliauto(self):
        return
        cmens = _('Do you want to run openPLI AutoBackup utility?')
        dei = self.session.openWithCallback(self.cbopa, MessageBox, cmens, MessageBox.TYPE_YESNO)
        dei.setTitle('openSPA - ' + _('Backup'))

    def cbopa(self, resp = None):
        if resp:
            try:
                from Plugins.Extensions.AutoBackup.plugin import main
                main(self.session)
            except:
                dei = self.session.open(MessageBox, _('Autobackup utility not found'), MessageBox.TYPE_ERROR, timeout=8)
                dei.setTitle(_('openPLI AutoBackup utility'))

    def dirSelected(self, res):
        if res is not None:
            if res.endswith('/') and not res == '/':
                res = res[0:len(res) - 1]
            self.list[self['config'].getCurrentIndex()][1].value = res

    def openLocationBox(self):
        try:
            path = self.list[self['config'].getCurrentIndex()][1].value
            if not path.endswith('/'):
                path = path + '/'
            from Screens.LocationBox import LocationBox
            self.session.openWithCallback(self.dirSelected, LocationBox, text=_('Choose directory'), filename='', currDir=path, minFree=40000)
        except:
            pass

    def iniciacopia(self):
        if self['config'].getCurrentIndex() == 0:
            self.openpliauto()
            return
        ruta = self['config'].list[3][1].value + '/'
        if not pathExists(ruta):
            dei = self.session.open(MessageBox, _('The path does not exist!') + '\n' + ruta, MessageBox.TYPE_ERROR)
            dei.setTitle(_('spazeTeam Backup/Restore').replace('spazeTeam', 'openSPA'))
        else:
            ntime = datetime.now()
            ctime = str(ntime.strftime('%d%m%Y_%H%M%S')).replace('/', '').replace(':', '')
            filenombre = '' + _(self['config'].list[2][1].value) + '_' + ctime
            filenombre = filenombre.replace(' ', '').replace('\xc3\xb1', 'n').replace('\xc3\xa1', 'a').replace('\xc3\xa9', 'e').replace('\xc3\xad', 'i').replace('\xc3\xb3', 'o').replace('\xc3\xba', 'u').replace('.', '').replace(':', '')
            from Plugins.Extensions.spazeMenu.spzVirtualKeyboard import spzVirtualKeyboard
            self.session.openWithCallback(self.iniciacopia2, spzVirtualKeyboard, titulo=_('Create backup') + '. ' + _('File Name (without extension)') + ':', texto=filenombre, caracteres='[FILESIMPLE]', ok=True)

    def iniciacopia2(self, nombre):
        if nombre is None:
            return
        if nombre == '' or nombre == ' ':
            return
        nombre = nombre.replace(' ', '_').replace('\xc3\xb1', 'n').replace('\xc3\xa1', 'a').replace('\xc3\xa9', 'e').replace('\xc3\xad', 'i').replace('\xc3\xb3', 'o').replace('\xc3\xba', 'u').replace('.', '').replace(':', '')
        nombreinfo = self['config'].list[3][1].value + '/' + nombre + '.info'
        newbooklist = None
        try:
            newbooklist = open(nombreinfo, 'w')
        except:
            dei = self.session.open(MessageBox, _('The filename is invalid !!!') + '\n' + nombreinfo, MessageBox.TYPE_ERROR)
            dei.setTitle(_('spazeTeam Backup/Restore').replace('spazeTeam', 'openSPA'))
            return

        config.plugins.spzBackups.lastprofile.value = str(self['config'].list[2][1].value)
        config.plugins.spzBackups.lastprofile.save()
        config.plugins.spzBackups.save()
        configfile.save()
        total = 0
        filenombre = nombre + '.tar.gz'
        cmens = 'tar -czvf ' + slash(self['config'].list[3][1].value + '/' + filenombre + '')
        nmens = _('File') + ': ' + self['config'].list[3][1].value + '/' + filenombre + '\n'
        nmens = nmens + _('Date') + ': ' + formateafecha(sepa=' ' + _('of') + ' ') + '\n'
        self.nombretemp = self['config'].list[3][1].value + '/' + filenombre
        for aaj in range(4, len(self['config'].list)):
            if self['config'].list[aaj][1].value == '1':
                nmens = nmens + '' + self['config'].list[aaj][0] + ' :: ' + str(len(self.lista[aaj - 5][1])) + ' ' + _('entrie(s)') + '\n'
                for iij in self.lista[aaj - 5][1]:
                    if iij.endswith('*'):
                        cmens = cmens + ' ' + iij + ''
                    else:
                        cmens = cmens + ' ' + slash(iij) + ''
                    if iij == '/etc/enigma2/settings':
                        if fileExists('/usr/bin/chkds'):
                            cmens = cmens + ' ' + slash('/usr/bin/chkds') + ''
                        if fileExists('/usr/bin/chkvs'):
                            cmens = cmens + ' ' + slash('usr/bin/chkvs') + ''
                        if fileExists('/usr/bin/vbinds'):
                            cmens = cmens + ' ' + slash('/usr/bin/vbinds') + ''

        nombreinfo = self['config'].list[3][1].value + '/' + filenombre.replace('.tar.gz', '.info')
        newbooklist = None
        try:
            newbooklist = open(nombreinfo, 'w')
        except:
            dei = self.session.open(MessageBox, _('Error by writing backup info file !!!') + '\n' + nombreinfo, MessageBox.TYPE_ERROR)
            dei.setTitle(_('spazeTeam Backup/Restore').replace('spazeTeam', 'openSPA'))

        if newbooklist is not None:
            newbooklist.write(nmens)
            newbooklist.write('\n')
            newbooklist.close()
        xmens = _('Copy creation') + ' (' + self['config'].list[3][1].value + '/' + filenombre + ')'
        dei = self.session.openWithCallback(self.cbCopia, infoSel, textoinfo='\n' + _('This task may take several minutes') + '\n\n' + _('Copying files') + '. ' + _('Wait...'), titulo=xmens, comando=cmens)

    def cbCopia(self, respuesta):
        if not fileExists(self.nombretemp):
            dei = self.session.open(MessageBox, self.nombretemp + '\n' + _('The backup file has been created !!!. Verify that enough space on the target drive and writable'), MessageBox.TYPE_ERROR)
            dei.setTitle(_('spazeTeam Backup/Restore').replace('spazeTeam', 'openSPA'))
        self.nombretemp = ''

    def verarchivos(self):
        idx = self['config'].getCurrentIndex()
        cmens = ''
        if idx == 0:
            return
        if idx > 4:
            xmens = self['config'].list[idx][0] + ' :: ' + str(len(self.lista[idx - 5][1])) + ' ' + _('entrie(s)') + ''
            for iij in self.lista[idx - 5][1]:
                cmens = cmens + iij + '\n'

        else:
            total = 0
            for aaj in range(4, len(self['config'].list)):
                if self['config'].list[aaj][1].value == '1':
                    cmens = cmens + '' + self['config'].list[aaj][0] + ' :: ' + str(len(self.lista[aaj - 5][1])) + ' ' + _('entrie(s)') + ':\n'
                    total = total + len(self.lista[aaj - 5][1])
                    for iij in self.lista[aaj - 5][1]:
                        cmens = cmens + '      ' + iij + '\n'

            xmens = _(self['config'].list[2][1].value) + ' :: ' + str(total) + ' ' + _('entrie(s)') + ' (' + self['config'].list[3][1].value + ')'
        dei = self.session.open(infoSel, textoinfo=cmens, titulo=xmens)

    def restaura(self):
        ruta = self['config'].list[3][1].value + '/'
        if not pathExists(ruta):
            dei = self.session.open(MessageBox, _('The path does not exist!') + '\n' + ruta, MessageBox.TYPE_ERROR)
            dei.setTitle(_('spazeTeam Backup/Restore').replace('spazeTeam', 'openSPA'))
        else:
            dei = self.session.openWithCallback(self.cbRestaura, spztRestore, ruta=self['config'].list[3][1].value)

    def cbRestaura(self, respuesta):
        if not respuesta == None:
            ruta = self['config'].list[3][1].value + '/'
            filenombre = '' + respuesta
            filenombre = filenombre + '.tar.gz'
            cmens = "tar -xzvf '" + self['config'].list[3][1].value + '/' + filenombre + "' -C /"
            xmens = _('Restore copy') + ' (' + self['config'].list[3][1].value + '/' + filenombre + ')'
            dei = self.session.openWithCallback(self.vuelta, infoSel, textoinfo='*** ' + _('This task may take several minutes') + ' ***\n' + _('The system must be restarted to apply changes') + '\n' + _('Restoring files') + '. ' + _('Wait...'), titulo=xmens, comando=cmens)

    def xsave(self):
        pass

    def pasa(self):
        idx = self['config'].getCurrentIndex()
        texto = self['config'].list[idx][0]
        if idx == 3 or idx == 0:
            try:
                self.list[self['config'].getCurrentIndex()][3]()
            except:
                pass

        elif _(texto) == _('PlugIns'):
            self['config'].list[idx][1].value = '1'
            self.selPlugins()
        elif _(texto) == _('Skins'):
            self['config'].list[idx][1].value = '1'
            self.selSkins()
        elif _(texto) == _('Other files/folders'):
            self['config'].list[idx][1].value = '1'
            self.selFiles()
        elif idx > 4:
            ConfigListScreen.keyRight(self)

    def vuelta(self, respuesta):
        if respuesta == 'no':
            pass
        elif respuesta == 'si':
            self.needrestart = True
            laref = _('The system will be restarted to complete the restoration')
            self.TimerRes = eTimer()
            self.TimerRes.callback.append(self.resetea)
            self.TimerRes.start(5000, True)
            dei = self.session.open(MessageBox, laref, MessageBox.TYPE_INFO, timeout=6, enable_input=False)

    def resetea(self):
        os.system('killall -9 enigma2')

    def actualizapantalla(self):
        idx = self['config'].getCurrentIndex()
        if idx == 0:
            self['tapa'].show()
            self['key_red'].setText(_('Run'))
            self['key_green'].setText(_(' '))
            self['key_yellow'].setText(_(' '))
        else:
            self['tapa'].hide()
            self['key_red'].setText(_('Start backup'))
            self['key_green'].setText(_('View files'))
            self['key_yellow'].setText(_('Save profile'))

    def key_U(self):
        idx = self['config'].getCurrentIndex()
        if idx == 0:
            try:
                self['config'].setCurrentIndex(len(self['config'].list) - 1)
            except:
                pass

        else:
            self['config'].setCurrentIndex(idx - 1)
        idx = self['config'].getCurrentIndex()
        if self.list[self['config'].getCurrentIndex()][1].value == '':
            try:
                self['config'].setCurrentIndex(idx - 1)
            except:
                pass

        self.actualizapantalla()

    def key_D(self):
        idx = self['config'].getCurrentIndex()
        if idx == len(self['config'].list) - 1:
            try:
                self['config'].setCurrentIndex(0)
            except:
                pass

        else:
            self['config'].setCurrentIndex(idx + 1)
        idx = self['config'].getCurrentIndex()
        if self.list[self['config'].getCurrentIndex()][1].value == '':
            try:
                self['config'].setCurrentIndex(idx + 1)
            except:
                pass

        self.actualizapantalla()

    def key_Left(self):
        idx = self['config'].getCurrentIndex()
        if idx == 2:
            if self.cambiado:
                laref = _('List changed. Save this changes?')
                dei = self.session.openWithCallback(self.acambiadoact2, MessageBox, laref, MessageBox.TYPE_YESNO)
            else:
                ConfigListScreen.keyLeft(self)
                self.actlista()
        else:
            ConfigListScreen.keyLeft(self)
            self.cambiado = True

    def actlista(self):
        self.cambiado = False
        valor = self['config'].list[2][1].value
        self.crealista(valor)
        self['config'].setList(self.list)
        self.actualizaScrolls()

    def key_Right(self):
        idx = self['config'].getCurrentIndex()
        if idx == 2:
            if self.cambiado:
                laref = _('List changed. Save this changes?')
                dei = self.session.openWithCallback(self.acambiadoact1, MessageBox, laref, MessageBox.TYPE_YESNO)
            else:
                ConfigListScreen.keyRight(self)
                self.actlista()
        else:
            ConfigListScreen.keyRight(self)
            self.cambiado = True

    def acambiadoact1(self, respuesta):
        if respuesta:
            self.guardar()
            self.cambiado = False
        ConfigListScreen.keyRight(self)
        self.actlista()

    def acambiadoact2(self, respuesta):
        if respuesta:
            self.guardar()
            self.cambiado = False
        ConfigListScreen.keyLeft(self)
        self.actlista()

    def guardar(self):
        global cambiadalista
        self.cambiado = False
        if guardalista(self['config'].list, self.lista):
            laref = _('List changes saved')
            dei = self.session.open(MessageBox, laref, MessageBox.TYPE_INFO)
        cambiadalista = False

    def reiniciar(self, respuesta):
        if respuesta:
            self.session.open(TryQuitMainloop, 3)

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
            self.guardar()
            self.close()
        else:
            self.close()

    def selPlugins(self):
        idx = self['config'].getCurrentIndex()
        if idx > 4:
            xlista = self.lista[idx - 5][1]
            dei = self.session.openWithCallback(self.cbselPlugins, selPlugins, listaini=xlista)

    def selSkins(self):
        idx = self['config'].getCurrentIndex()
        if idx > 4:
            xlista = self.lista[idx - 5][1]
        dei = self.session.openWithCallback(self.cbselPlugins, selPlugins, titulo='Skins', listaini=xlista)

    def cbselPlugins(self, respuesta):
        if not respuesta == None:
            self.cambiado = True

    def selFiles(self):
        idx = self['config'].getCurrentIndex()
        if idx > 4:
            xlista = self.lista[idx - 5][1]
            dei = self.session.openWithCallback(self.cbSelFiles, BackupSelectionSP, listaarchivos=xlista)

    def cbSelFiles(self, resp):
        if not resp == None:
            self.cambiado = True


class BackupSelectionSP(Screen):
    if esHD():
        skin = '\n\t\t<screen name="BackupSelectionSP" position="center,center" size="1590,960" title="%s">\n\t\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/rednHD.png" position="0,0" size="180,60" alphatest="blend" />\n\t\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/yellownHD.png" position="420,0" size="180,60" alphatest="blend" />\n\t\t\t<widget source="key_red" render="Label" position="0,-7" zPosition="1" size="180,45" font="Regular;17" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />\n\t\t\t<widget source="key_green" render="Label" position="210,-7" zPosition="1" size="180,45" font="Regular;17" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />\n\t\t\t<widget source="key_yellow" render="Label" position="420,-7" zPosition="1" size="180,45" font="Regular;17" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />\n\t\t\t<eLabel name="elinea" position="0,58" size="1590,1" backgroundColor="#30444444" />\n\t\t\t<widget name="k_titulo" position="0,58" zPosition="1" size="1590,33" font="Regular;17" halign="left" valign="top" backgroundColor="#000000" transparent="1" foregroundColor="#888888" />\n\t\t\t<eLabel name="elinea" position="0,88" size="1590,1" backgroundColor="#30444444" />\n\t\t\t<widget name="checkList" position="7,90" size="1582,600" transparent="1" scrollbarMode="showOnDemand" itemHeight="42" />\n\t\t\t<eLabel name="elinea" position="0,699" size="1590,1" backgroundColor="#30444444" />\t\n\t\t\t<widget name="k_info" position="0,699" zPosition="1" size="1590,270" font="Regular;16" halign="left" valign="top" backgroundColor="#000000" foregroundColor="#888888" transparent="1" />\n\t\t\t<widget name="barrapix_arr" position="0,0" zPosition="19" size="30,30" alphatest="blend" transparent="1" />\n\t\t\t<widget name="barrapix_abj" position="0,0" zPosition="19" size="30,30" alphatest="blend" transparent="1" />\n\t\t</screen>' % _('Select Files/Folders')
    else:
        skin = '\n\t\t<screen name="BackupSelectionSP" position="center,center" size="1060,640" title="%s">\n\t\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/spzBackups/img/redn.png" position="0,0" size="120,40" alphatest="on" />\n\t\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/spzBackups/img/yellown.png" position="280,0" size="120,40" alphatest="on" />\n\t\t\t<widget source="key_red" render="Label" position="0,-5" zPosition="1" size="120,30" font="Regular;17" halign="center" valign="center" backgroundColor="#9f1313" transparent="1" />\n\t\t\t<widget source="key_green" render="Label" position="140,-5" zPosition="1" size="120,30" font="Regular;17" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />\n\t\t\t<widget source="key_yellow" render="Label" position="280,-5" zPosition="1" size="120,30" font="Regular;17" halign="center" valign="center" backgroundColor="#1f771f" transparent="1" />\n\t\t\t\n\t\t\t<eLabel name="elinea" position="0,39" size="1060,1" backgroundColor="#30444444" />\n\t\t\t<widget name="k_titulo" position="0,39" zPosition="1" size="1060,22" font="Regular;17" halign="left" valign="top" backgroundColor="#000000" transparent="1" foregroundColor="#888888" />\n\t\t\t<eLabel name="elinea" position="0,59" size="1060,1" backgroundColor="#30444444" />\n\t\t\t<widget name="checkList" position="5,60" size="1055,400" transparent="1" scrollbarMode="showOnDemand" />\n\t\t\t<eLabel name="elinea" position="0,466" size="1060,1" backgroundColor="#30444444" />\t\t\t\n\t\t\t<widget name="k_info" position="0,466" zPosition="1" size="1060,180" font="Regular;16" halign="left" valign="top" backgroundColor="#000000" foregroundColor="#888888" transparent="1" />\n\t\t\t<widget name="barrapix_arr" position="0,0" zPosition="19" size="20,20" alphatest="blend" transparent="1" />\n\t\t\t<widget name="barrapix_abj" position="0,0" zPosition="19" size="20,20" alphatest="blend" transparent="1" />\n\t\t</screen>' % _('Select Files/Folders')

    def __init__(self, session, listaarchivos = None):
        Screen.__init__(self, session)
        self['key_red'] = StaticText(_('Clear'))
        self['key_green'] = StaticText(' ')
        self['key_yellow'] = StaticText()
        self['k_info'] = Label(' ')
        self['k_titulo'] = Label('/')
        self.cambiado = False
        self.selectedFiles = listaarchivos
        self.defaultDir = '/'
        self.inhibitDirs = ['/bin',
         '/boot',
         '/dev',
         '/autofs',
         '/lib',
         '/proc',
         '/sbin',
         '/sys',
         '/hdd',
         '/tmp',
         '/mnt',
         '/media']
        self.filelist = MultiFileSelectList(self.selectedFiles, self.defaultDir, inhibitDirs=self.inhibitDirs)
        self['checkList'] = self.filelist
        self['actions'] = ActionMap(['DirectionActions', 'OkCancelActions', 'ShortcutActions'], {'cancel': self.exit,
         'red': self.vacia,
         'yellow': self.changeSelectionState,
         'ok': self.okClicked,
         'left': self.left,
         'right': self.right,
         'down': self.down,
         'up': self.up}, -1)
        if self.selectionChanged not in self['checkList'].onSelectionChanged:
            self['checkList'].onSelectionChanged.append(self.selectionChanged)
        self.onLayoutFinish.append(self.layoutFinished)
        self.onShow.append(self.iniscroll)
        self.iniciadoS = False
        self['barrapix_arr'] = Pixmap()
        self['barrapix_abj'] = Pixmap()

    def iniscroll(self):
        if not self.iniciadoS:
            self.actualizaScrolls()
            self.iniciadoS = True

    def actualizaScrolls(self):
        openspaSB(objectoself=self, nombrelista='checkList', barra='barrapix', altoitem=25, imagen=True)

    def vacia(self):
        laref = _('Delete all entries from list?')
        dei = self.session.openWithCallback(self.resvacia, MessageBox, laref, MessageBox.TYPE_YESNO)

    def resvacia(self, respuesta):
        if respuesta:
            try:
                vaciarlista(self.selectedFiles)
                self.filelist = MultiFileSelectList(self.selectedFiles, self.defaultDir, inhibitDirs=self.inhibitDirs)
                self.selectionChanged()
                self.exit()
            except:
                pass

    def muestratodos(self):
        tmplista = str(self['checkList'].getSelectedList())
        tmplista = tmplista.replace("',", ';').replace('[', '').replace(']', '').replace('(', '').replace(')', '').replace("'", '')
        self['k_info'].setText(tmplista)
        curdir = str(self['checkList'].current_directory)
        self['k_titulo'].setText(curdir)

    def layoutFinished(self):
        idx = 0
        self['checkList'].moveToIndex(idx)
        self.selectionChanged()

    def selectionChanged(self):
        try:
            current = self['checkList'].getCurrent()[0]
            if not current:
                return
            if current[2] is True:
                self['key_yellow'].setText(_('Deselect'))
            else:
                self['key_yellow'].setText(_('Mark'))
            self.muestratodos()
        except:
            pass

    def up(self):
        self['checkList'].up()

    def down(self):
        self['checkList'].down()

    def left(self):
        self['checkList'].pageUp()

    def right(self):
        self['checkList'].pageDown()

    def changeSelectionState(self):
        self.cambiado = True
        self['checkList'].changeSelectionState()
        self.selectedFiles = self['checkList'].getSelectedList()

    def saveSelection(self, resp):
        if resp:
            self.selectedFiles = self['checkList'].getSelectedList()
            self.close(self.selectedFiles)
        else:
            self.close(None)

    def exit(self):
        self.selectedFiles = self['checkList'].getSelectedList()
        if self.cambiado:
            self.close(True)
        else:
            self.close(None)

    def okClicked(self):
        if self.filelist.canDescent():
            self.filelist.descent()
            self.muestratodos()
        self.actualizaScrolls()


def start_from_mainmenu(menuid, **kwargs):
    if menuid == 'setup':
        return [(_('spazeTeam Backup/Restore').replace('spazeTeam', 'openSPA'),
          mainHome,
          'spazeTeamBackup',
          None)]
    return []


def mainHome(session, **kwargs):
    if not fileExists('/usr/bin/chkvs'):
        Notifications.AddPopup(text=_('Not spazeTeam image found!\nMore info in www.azboxhd.es').replace('spazeTeam', 'openSPA'), type=MessageBox.TYPE_ERROR, timeout=10, id='spzBackups')
    else:
        session.open(spzCopiar)


def Plugins(**kwargs):
    name = _('spazeTeam Backup/Restore').replace('spazeTeam', 'openSPA')
    descr = _('Utility for backup and restore files')
    list = [PluginDescriptor(name=name, description=descr, where=PluginDescriptor.WHERE_PLUGINMENU, icon='azbk.png', fnc=mainHome)]
    list.append(PluginDescriptor(name=name, description=descr, where=PluginDescriptor.WHERE_MENU, fnc=start_from_mainmenu))
    return list


def slash(laruta):
    mret = laruta
    if ' ' in laruta:
        mret = "'" + mret + "'"
    return mret
