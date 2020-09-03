from Components.Label import Label
from Components.MenuList import MenuList
from Screens.ChannelSelection import SimpleChannelSelection
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest, MultiContentEntryPixmapAlphaBlend
from enigma import eTimer, eListboxPythonMultiContent, getDesktop, eServiceCenter, gFont, eServiceReference, iServiceInformation, BT_SCALE, BT_KEEP_ASPECT_RATIO, RT_HALIGN_RIGHT, RT_HALIGN_LEFT, RT_HALIGN_CENTER, getBestPlayableServiceReference
from ServiceReference import ServiceReference
from Components.Pixmap import Pixmap, MovingPixmap
from Tools.LoadPixmap import LoadPixmap
from Components.Harddisk import harddiskmanager
from RecordTimer import AFTEREVENT
from Screens.ChoiceBox import ChoiceBox
from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.Standby import TryQuitMainloop
from Components.ActionMap import ActionMap
from Components.ScrollLabel import ScrollLabel
from Tools.FuzzyDate import FuzzyTime
import NavigationInstance
from Plugins.Extensions.spazeMenu.sbar import openspaSB
from Components.config import getConfigListEntry, ConfigEnableDisable, ConfigYesNo, ConfigText, ConfigClock, ConfigNumber, ConfigSelection, config, ConfigSubsection, ConfigSubList, ConfigSubDict, ConfigDirectory
from Tools import Notifications
from Tools.HardwareInfo import HardwareInfo
from time import localtime, time
from Tools.Directories import fileExists, resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE, SCOPE_SKIN
from Components.Language import language
from boxbranding import getImageVersion, getImageBuild, getMachineBrand, getMachineName, getMachineBuild, getDriverDate, getImageDistro, getOEVersion
from os import environ, path
import os
import gettext
import sys
from Plugins.Extensions.spazeMenu.plugin import esHD, fhd
lang = language.getLanguage()
environ['LANGUAGE'] = lang[:2]
gettext.bindtextdomain('enigma2', resolveFilename(SCOPE_LANGUAGE))
gettext.textdomain('enigma2')
gettext.bindtextdomain('InfoAz', '%s%s' % (resolveFilename(SCOPE_PLUGINS), 'Extensions/spazeMenu/spzPlugins/InfoAz/locale/'))
lenguaje = str(lang[:2])

def _(txt):
    t = gettext.dgettext('InfoAz', txt)
    if t == txt:
        t = gettext.gettext(txt)
    return t


filename = ''
carpetaimg = '/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/InfoAz/res/'
nommodelo = 'NA'
listamenu = []
listamenu.append((_('Record'), _('Current recording information'), 1))
listamenu.append((_('Tuning'), _('Information about tunning and current channel'), 2))
listamenu.append((_('Storage'), _('Hard disk devices information'), 6))
listamenu.append((_('Memory'), _('Free memory table'), 7))
listamenu.append((_('Emulation'), _('Information for cams and emulation'), 11))
listamenu.append((_('Net'), _('Network conection information'), 5))
listamenu.append((_('Hardware'), _('Cpu, model information'), 3))
listamenu.append((_('Display'), _('AV settings, skin information'), 9))
listamenu.append((_('Operating system'), _('Current operating system information'), 4))
listamenu.append((_('Processes'), _('List of current processes running'), 8))
listamenu.append((_('OpenSPA'), _('About this panel...'), 10))

def getTemperatura():
    tempinfo = ''
    cret = ''
    try:
        if path.exists('/proc/stb/sensors/temp0/value'):
            f = open('/proc/stb/sensors/temp0/value', 'r')
            tempinfo = f.read()
            f.close()
        elif path.exists('/proc/stb/fp/temp_sensor'):
            f = open('/proc/stb/fp/temp_sensor', 'r')
            tempinfo = f.read()
            f.close()
        if tempinfo and int(tempinfo.replace('\n', '')) > 0:
            mark = str('\xc2\xb0')
            cret += _('System') + ': ' + tempinfo.replace('\n', '').replace(' ', '') + mark + 'C'
        tempinfo = ''
        if path.exists('/proc/stb/fp/temp_sensor_avs'):
            f = open('/proc/stb/fp/temp_sensor_avs', 'r')
            tempinfo = f.read()
            f.close()
        if tempinfo and int(tempinfo.replace('\n', '')) > 0:
            mark = str('\xc2\xb0')
            cret += _('Processor') + ': ' + tempinfo.replace('\n', '').replace(' ', '') + mark + 'C'
    except:
        pass

    return cret


def getMemoria():
    cret = ''
    try:
        out_lines = file('/proc/meminfo').readlines()
        totmem = 0
        freemem = 0
        for lidx in range(len(out_lines) - 1):
            tstLine = out_lines[lidx].split()
            if 'MemTotal:' in tstLine:
                MemTotal = out_lines[lidx].split()
                totmem = int(MemTotal[1])
            if 'MemFree:' in tstLine:
                MemFree = out_lines[lidx].split()
                freemem = int(MemFree[1])

        if totmem > 0:
            porcentaje = int(freemem * 100 / totmem)
            laram = Humanizer(freemem * 1024)
            cret = 'RAM ' + _('Free') + ': ' + laram.split('.')[0] + ' ' + laram.split(' ')[1] + ' (' + str(porcentaje) + '%)' + '/' + Humanizer(totmem * 1024)
    except:
        cret = ' err mem'

    return cret


def getTitulo():
    cret = ''
    csep = ''
    try:
        cret = '' + getImageVersion() + '.' + getImageBuild()
        csep = ' | '
    except:
        pass

    tempret = getTemperatura()
    if not tempret == '':
        cret = cret + csep + tempret
        csep = ' | '
    tempret = getMemoria()
    if not tempret == '':
        cret = cret + csep + tempret
        csep = ' | '
    if not cret == '':
        cret = ' ' + cret
    return cret


from Components.About import about
errordream = False
try:
    from Tools.DreamboxHardware import getFPVersion
except:
    errordream = True

if errordream:
    try:
        from Tools.StbHardware import getFPVersion
    except:
        pass

from Components.NimManager import nimmanager

def getPliInfo():
    AboutText = ''
    try:
        AboutText = _('Model: ') + getMachineBrand() + ' ' + getMachineName() + ' ' + '(' + getMachineBuild().upper() + ')' + '\n'
        if path.exists('/proc/stb/info/chipset'):
            AboutText += _('Chipset: ') + about.getChipSetString() + '\n'
        cpuMHz = ''
        if path.exists('/proc/cpuinfo'):
            f = open('/proc/cpuinfo', 'r')
            temp = f.readlines()
            f.close()
            try:
                for lines in temp:
                    lisp = lines.split(': ')
                    if lisp[0].startswith('cpu MHz'):
                        cpuMHz = ' (' + str(int(float(lisp[1].replace('\n', '')))) + ' MHz)'
                        break

            except:
                pass

        AboutText += _('CPU: %s') % about.getCPUString() + cpuMHz + '\n'
        AboutText += _('Cores: ') + str(about.getCpuCoresString()) + '\n'
        AboutText += _('OE: ') + getOEVersion() + '\n'
        AboutText += _('Distro: ') + getImageDistro() + '\n'
        AboutText += _('Version: ') + getImageVersion() + '\n'
        AboutText += _('Build: ') + getImageBuild() + '\n'
        AboutText += _('Kernel Version: ') + about.getKernelVersionString() + '\n'
        string = getDriverDate()
        year = string[0:4]
        month = string[4:6]
        day = string[6:8]
        driversdate = '-'.join((year, month, day))
        AboutText += _('Drivers: ') + driversdate + '\n'
        AboutText += _('GStreamer: ') + about.getGStreamerVersionString().replace('GStreamer', '') + '\n'
        AboutText += _('Python version: ') + about.getPythonVersionString() + '\n'
        AboutText += _('Enigma: ') + about.getEnigmaVersionString() + '\n'
        AboutText += _('Installed: ') + about.getFlashDateString() + '\n'
        AboutText += _('Last Upgrade: ') + about.getImageVersionString() + '\n'
    except:
        pass

    try:
        fp_version = getFPVersion()
        if fp_version is None:
            fp_version = ''
        else:
            fp_version = _('Frontprocessor version: %d') % fp_version
            AboutText += fp_version + '\n'
    except:
        pass

    AboutText += '\n' + _('Detected NIMs:') + '\n'
    nims = nimmanager.nimList()
    for count in range(len(nims)):
        AboutText += nims[count] + '\n'

    return AboutText


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


def ponPorcen(valor):
    ret = '|'
    for i in range(0, 10):
        if i < valor / 10:
            ret = ret + '_'
        else:
            ret = ret + '  '

    ret = ret + '| ' + str(valor) + '%'
    return ret


def getKernelVersionString():
    try:
        result = popen('uname -r', 'r').read().strip('\n').split('-')
        kernel_version = result[0]
        return kernel_version
    except:
        pass

    return ' '


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


def inforecord():
    global filename
    ret = []
    filename = ''
    for timer in NavigationInstance.instance.RecordTimer.timer_list:
        if timer.state == timer.StateRunning and not timer.disabled:
            nombre = str(timer.name) + ''
            try:
                if len(nombre) < 2:
                    nombre = os.path.split(timer.Filename)[1]
                archivo = str(timer.Filename)
                filename = str(timer.Filename)
            except:
                archivo = 'NA'
                filename = 'NA'

            if filename != 'NA':
                inicio = str(FuzzyTime(timer.begin)[1])
                fin = str(FuzzyTime(timer.end)[1])
                duracion = str((timer.end - timer.begin) / 60) + ' ' + _('mins')
                nfaltan = (timer.end - time()) / 60
                cvan = str((time() - timer.begin) / 60)
                if nfaltan >= 1:
                    faltan = str(int(nfaltan)) + ' ' + _('mins')
                else:
                    faltan = str(int(nfaltan * 60)) + ' ' + _('secs')
                nomcan = timer.service_ref.getServiceName()
                now = int(time())
                start_time = timer.begin
                duration = timer.end - timer.begin
                valor = int((int(time()) - timer.begin) * 100 / duration)
                pos = valor
                nlen = 100
                valor = pos * 100 / nlen
                ret.append((nombre,
                 nomcan,
                 inicio,
                 fin,
                 duracion,
                 faltan,
                 cvan,
                 valor,
                 archivo))

    return ret


def grabando(selfse):
    recordings = len(selfse.session.nav.getRecordings())
    if recordings > 0:
        return True
    else:
        return False


class IniciaSelListLista(MenuList):

    def __init__(self, list, enableWrapAround = False):
        MenuList.__init__(self, list, enableWrapAround, eListboxPythonMultiContent)
        self.l.setItemHeight(29)
        self.l.setFont(0, gFont('Regular', 18))
        self.l.setFont(1, gFont('Regular', 16))


def IniciaSelListEntryLista(texto1):
    res = [texto1]
    res.append(MultiContentEntryText(pos=(5, 1), size=(1000, 33), font=0, text=texto1))
    return res


class IniciaSelListInfo(MenuList):

    def __init__(self, list, enableWrapAround = False):
        MenuList.__init__(self, list, enableWrapAround, eListboxPythonMultiContent)
        self.l.setItemHeight(fhd(100))
        self.l.setFont(0, gFont('Regular', 18))
        self.l.setFont(1, gFont('Regular', 16))


def IniciaSelListEntryInfo(texto1, texto2 = None, texto3 = None, texto4 = None, texto5 = None, imagen1 = None, progreso = None, ruta = None):
    global carpetaimg
    if ruta == None:
        res = [texto1]
    else:
        res = [ruta]
    inifile = ''
    if esHD():
        inifile = 'HD'
    res.append(MultiContentEntryText(pos=(fhd(68), fhd(16, 1.1)), size=(fhd(1000), fhd(33)), font=0, text=texto1))
    if not texto2 == None:
        res.append((eListboxPythonMultiContent.TYPE_TEXT,
         0,
         fhd(43, 1.4),
         fhd(744),
         fhd(22),
         0,
         RT_HALIGN_CENTER,
         texto2))
    if not texto3 == None:
        res.append((eListboxPythonMultiContent.TYPE_TEXT,
         0,
         fhd(60, 1.4),
         fhd(216),
         fhd(30),
         0,
         RT_HALIGN_RIGHT,
         texto3))
    if not texto4 == None:
        res.append((eListboxPythonMultiContent.TYPE_TEXT,
         fhd(528, 1.5),
         fhd(60, 1.44),
         fhd(318),
         fhd(30),
         0,
         RT_HALIGN_LEFT,
         texto4))
    if not texto5 == None:
        res.append((eListboxPythonMultiContent.TYPE_TEXT,
         0,
         fhd(76, 1.54),
         fhd(744),
         fhd(25),
         0,
         RT_HALIGN_CENTER,
         texto5))
    if not imagen1 == None:
        imagen = 'list' + str(imagen1) + '-fs8.png'
        png = '' + carpetaimg + '' + inifile + imagen + ''
        if fileExists(png):
            fpng = LoadPixmap(png)
            res.append(MultiContentEntryPixmapAlphaBlend(pos=(5, fhd(1, 1)), size=(fhd(50), fhd(50)), png=fpng, flags=BT_SCALE | BT_KEEP_ASPECT_RATIO))
    if not progreso == None:
        imagen = 'infoprogreso0-fs8.png'
        png = '' + carpetaimg + '' + inifile + imagen + ''
        if fileExists(png):
            fpng = LoadPixmap(png)
            res.append(MultiContentEntryPixmapAlphaTest(pos=(fhd(223), fhd(66, 1.4)), size=(fhd(300), fhd(13)), png=fpng))
        imagen = 'infoprogreso1-fs8.png'
        if progreso > 35 and not imagen1 == 5:
            imagen = 'infoprogreso2-fs8.png'
        if progreso > 60 and not imagen1 == 5:
            imagen = 'infoprogreso3-fs8.png'
        if progreso > 80 or imagen1 == 5:
            imagen = 'infoprogreso4-fs8.png'
        png = '' + carpetaimg + '' + inifile + imagen + ''
        if fileExists(png):
            fpng = LoadPixmap(png)
            res.append(MultiContentEntryPixmapAlphaBlend(pos=(fhd(223), fhd(66, 1.4)), size=(fhd(progreso * 3), fhd(13)), png=fpng))
    return res


class IniciaSelList(MenuList):

    def __init__(self, list, enableWrapAround = False):
        MenuList.__init__(self, list, enableWrapAround, eListboxPythonMultiContent)
        self.l.setItemHeight(fhd(50, 1.6))
        self.l.setFont(0, gFont('Regular', 21))
        self.l.setFont(1, gFont('Regular', 17))


def IniciaSelListEntry(texto, info, numero):
    inifile = ''
    if esHD():
        inifile = 'HD'
    res = [texto]
    res.append(MultiContentEntryText(pos=(fhd(54), fhd(14)), size=(1000, fhd(30)), font=0, text=texto))
    imagen = 'info' + str(numero) + '-fs8.png'
    png = '' + carpetaimg + '' + inifile + imagen + ''
    if fileExists(png):
        fpng = LoadPixmap(png)
        res.append(MultiContentEntryPixmapAlphaBlend(pos=(fhd(1), fhd(1, 5)), size=(fhd(48), fhd(48)), png=fpng, flags=BT_SCALE | BT_KEEP_ASPECT_RATIO))
    return res


def cargalista(valor, sigrabando = False):
    global listamenu
    templista = []
    indice = -1
    for i in range(0, len(listamenu)):
        eltexto = '' + listamenu[i][0]
        lainfo = '' + listamenu[i][1]
        elnumero = listamenu[i][2]
        if elnumero == valor:
            indice = i
        if elnumero == 1 and sigrabando:
            elnumero = 99
        templista.append(IniciaSelListEntry(eltexto, lainfo, elnumero))

    return [indice, templista]


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


TYPE_TEXT = 0
TYPE_VALUE_HEX = 1
TYPE_VALUE_DEC = 2
TYPE_VALUE_HEX_DEC = 3
TYPE_SLIDER = 4
TYPE_VALUE_ORBIT_DEC = 5

def ajustafr(frecu):
    return int(round(float(frecu) / 1000000, 0)) * 1000


def devchfr(frecu):
    ret = 'NA'
    arrfecs = [(21, 474),
     (22, 482),
     (23, 490),
     (24, 498),
     (25, 506),
     (26, 514),
     (27, 522),
     (28, 530),
     (29, 538),
     (30, 546),
     (31, 554),
     (32, 562),
     (33, 570),
     (34, 578),
     (35, 586),
     (36, 594),
     (37, 602),
     (38, 610),
     (39, 618),
     (40, 626),
     (41, 634),
     (42, 642),
     (43, 650),
     (44, 658),
     (45, 666),
     (46, 674),
     (47, 682),
     (48, 690),
     (49, 698),
     (50, 706),
     (51, 714),
     (52, 722),
     (53, 730),
     (54, 738),
     (55, 746),
     (56, 754),
     (57, 762),
     (58, 770),
     (59, 778),
     (60, 786),
     (61, 794),
     (62, 802),
     (63, 810),
     (64, 818),
     (65, 826),
     (66, 834),
     (67, 842),
     (68, 850),
     (69, 858)]
    nfrecu = ajustafr(frecu) / 1000
    for ele in arrfecs:
        if ele[1] == nfrecu:
            ret = ele[0]
            return ret

    return ret


def infocanal(servicio, sinfo):
    texto = '\n'
    laref = ''
    try:
        laref = servicio.toString() + ''
    except:
        pass

    if laref.startswith('4097:0:0:'):
        ref = laref
        laurl = ''
        nombre = ''
        try:
            laurl = _('URL') + '-> ' + ref.replace('4097:0:0:0:0:0:0:0:0:0:', '').split(':')[0].replace('%3a', ':') + '\n'
        except:
            pass

        try:
            nombre = _('Channel') + '-> ' + ref.split(':')[-1] + '\n'
        except:
            pass

        texto = texto + nombre
        texto = texto + _('System') + '-> ' + ' IPTV (Internet Protocol Television)\n'
        texto = texto + laurl
        texto = texto + _('Service reference') + '-> ' + laref + '\n'
        return texto
    try:
        nomcan = ServiceReference(servicio).getServiceName().replace('\xc2\x86', '').replace('\xc2\x87', '')
        texto = texto + _('Channel') + '-> ' + nomcan
    except:
        pass

    try:
        texto = texto + '\n'
        texto = texto + _('Service reference') + '-> ' + servicio.toString() + ''
    except:
        pass

    from Tools.Transponder import ConvertToHumanReadable
    try:
        info = eServiceCenter.getInstance().info(servicio)
        texto = texto + '\n'
        transponder_info = info.getInfoObject(servicio, iServiceInformation.sTransponderData)
        tp_info = ConvertToHumanReadable(transponder_info)
        conv = {'tuner_type': '1-> ' + _('Transponder Type'),
         'system': '2-> ' + _('System'),
         'modulation': '8-> ' + _('Modulation'),
         'orbital_position': '3-> ' + _('Orbital Position'),
         'frequency': '4-> ' + _('Frequency'),
         'symbol_rate': '6-> ' + _('Symbolrate'),
         'bandwidth': '5-> ' + _('Bandwidth'),
         'polarization': '7-> ' + _('Polarization'),
         'inversion': '9-> ' + _('Inversion'),
         'pilot': '9-> ' + _('Pilot'),
         'rolloff': '9-> ' + _('Rolloff'),
         'fec_inner': '9-> ' + _('FEC'),
         'code_rate_lp': '9-> ' + _('Coderate LP'),
         'code_rate_hp': '9-> ' + _('Coderate HP'),
         'constellation': '9-> ' + _('Constellation'),
         'transmission_mode': '9-> ' + _('Transmission Mode'),
         'guard_interval': '9-> ' + _('Guard Interval'),
         'hierarchy_information': '9-> ' + _('Hierarchy Information')}
        Labels = [ (conv[i], tp_info[i], i == 'orbital_position' and TYPE_VALUE_ORBIT_DEC or TYPE_VALUE_DEC) for i in tp_info.keys() if i in conv ]
        try:
            Labels.sort(key=lambda x: x[0])
        except:
            pass

        esdvt = False
        for item in Labels:
            if item[1] is None:
                continue
            value = item[1]
            nombre = item[0]
            try:
                nombre = item[0].split('-> ')[1]
            except:
                pass

            if nombre == _('System') and item[1] == 'DVB-T':
                esdvt = True
            try:
                if esdvt and nombre == _('Frequency'):
                    value = str(value) + ' (Mux ' + str(devchfr(int(item[1]))) + ')'
            except:
                pass

            if len(item) < 4:
                texto = texto + '\n' + nombre + '-> ' + str(value)
            else:
                texto = texto + '\n' + nombre + '-> ' + str(value)

    except:
        pass

    return texto


def normalizatam(cualo):
    valor = 0
    if 'M' in cualo:
        valor = float(cualo.replace('M', ''))
    if 'K' in cualo:
        valor = float(cualo.replace('K', '')) / 1024
    if 'G' in cualo:
        valor = float(cualo.replace('G', '')) * 1024
    if 'T' in cualo:
        valor = float(cualo.replace('T', '')) * 1024 * 1024
    return valor


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


class infoAzTexto(Screen):
    if esHD():
        skin = '\n\t\t<screen position="center,80" size="1575,903" title="%s">\n\t\t\t<widget name="lista" position="0,0" size="375,903" scrollbarMode="showOnDemand" zPosition="12" transparent="1" />\n\t\t\t<widget name="textoinfo" position="432,55" size="1117,783" valign="top" halign="left" text="%s" font="Regular; 18" zPosition="1" />\n\t\t\t<widget name="listainfo" position="432,55" size="1117,783" zPosition="1" scrollbarMode="showAlways" transparent="1"/>\n\t\t\t<widget name="listaproc" position="432,55" size="1117,783" zPosition="1" scrollbarMode="showAlways" transparent="1"/>\n\t\t\t<widget name="key_izq" position="442,852" size="330,37" valign="center" halign="left" zPosition="4" font="Regular;17" transparent="1" /> \n\t\t\t<widget name="img_izq" position="390,850" zPosition="2" size="52,37" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/izqHD.png" transparent="1" alphatest="on" />\n\t\t\t<widget name="key_dch" position="652,852" size="330,37" valign="center" halign="left" zPosition="4" font="Regular;17" transparent="1" /> \n\t\t\t<widget name="img_dch" position="600,850" zPosition="2" size="52,37" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/dchaHD.png" transparent="1" alphatest="on" />\n\t\t\t<widget name="key_red" position="822,850" size="180,60" valign="center" halign="center" backgroundColor="#000000" foregroundColor="#ffffff" zPosition="4" font="Regular;17" transparent="1" /> \n\t\t\t<widget name="key_green" position="1011,850" size="180,60" valign="center" halign="center" backgroundColor="#000000" foregroundColor="#ffffff" zPosition="4" font="Regular;17" transparent="1" />  \n\t\t\t<widget name="key_yellow" position="1201,850" size="180,60" valign="center" halign="center" backgroundColor="#000000" foregroundColor="#ffffff" zPosition="4" font="Regular;17" transparent="1" /> \n\t\t\t<widget name="key_blue" position="1392,850" size="180,60" valign="center" halign="center" backgroundColor="#000000" foregroundColor="#ffffff" zPosition="4" font="Regular;17" transparent="1" /> \n\t\t\t<widget name="img_red" position="822,858" zPosition="2" size="195,60" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/rednHD.png" transparent="1" alphatest="on" />\n\t\t\t<widget name="img_green" position="1011,858" zPosition="2" size="195,60" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/greennHD.png" transparent="1" alphatest="on" />\n\t\t\t<widget name="img_yellow" position="1201,858" zPosition="2" size="195,60" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/yellownHD.png" transparent="1" alphatest="on" />\n\t\t\t<widget name="img_blue" position="1392,858" zPosition="2" size="195,60" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/bluenHD.png" transparent="1" alphatest="on" />\n\t\t\t<widget name="titulo" position="432,0" size="1119,42" text=" " transparent="1" halign="center" font="Regular; 22" zPosition="1" />\n\t\t\t<ePixmap name="fondo" position="0,0" size="1575,903" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/InfoAz/res/hdfondoinfo-fs8.png" transparent="1" alphatest="blend"/>\n\t\t\t<widget name="barrapix_arr" position="432,55" zPosition="19" size="1117,783" alphatest="blend" transparent="1" />\n\t\t\t<widget name="barrapix_abj" position="0,0" zPosition="19" size="30,30" alphatest="blend" transparent="1" />\n\t\t</screen>' % (_('Information') + ' ' + 'openSPA', _('Wait...'))
    else:
        skin = '\n\t\t<screen position="center,80" size="1050,602" title="%s">\n\t\t\t<widget name="lista" position="0,0" size="250,602" scrollbarMode="showOnDemand" zPosition="12" transparent="1" />\n\t\t\t<widget name="textoinfo" position="288,37" size="745,522" valign="top" halign="left" text="%s" font="Regular; 18" zPosition="1" />\n\t\t\t<widget name="listainfo" position="288,37" size="745,522" zPosition="1" scrollbarMode="showAlways" transparent="1"/>\n\t\t\t<widget name="listaproc" position="288,37" size="745,522" zPosition="1" scrollbarMode="showAlways" transparent="1"/>\n\t\t\t<widget name="key_izq" position="295,568" size="220,25" valign="center" halign="left" zPosition="4" font="Regular;17" transparent="1" /> \n\t\t\t<widget name="img_izq" position="260,567" zPosition="2" size="35,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/InfoAz/res/izq-fs8.png" transparent="1" alphatest="on" />\n\t\t\t<widget name="key_dch" position="435,568" size="220,25" valign="center" halign="left" zPosition="4" font="Regular;17" transparent="1" /> \n\t\t\t<widget name="img_dch" position="400,567" zPosition="2" size="35,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/InfoAz/res/dch-fs8.png" transparent="1" alphatest="on" />\n\t\t\t<widget name="key_red" position="548,567" size="120,40" valign="center" halign="center" backgroundColor="#000000" foregroundColor="#ffffff" zPosition="4" font="Regular;17" transparent="1" /> \n\t\t\t<widget name="key_green" position="674,567" size="120,40" valign="center" halign="center" backgroundColor="#000000" foregroundColor="#ffffff" zPosition="4" font="Regular;17" transparent="1" />  \n\t\t\t<widget name="key_yellow" position="801,567" size="120,40" valign="center" halign="center" backgroundColor="#000000" foregroundColor="#ffffff" zPosition="4" font="Regular;17" transparent="1" /> \n\t\t\t<widget name="key_blue" position="928,567" size="120,40" valign="center" halign="center" backgroundColor="#000000" foregroundColor="#ffffff" zPosition="4" font="Regular;17" transparent="1" /> \n\t\t\t<widget name="img_red" position="548,572" zPosition="2" size="130,40" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/InfoAz/res/redn.png" transparent="1" alphatest="on" />\n\t\t\t<widget name="img_green" position="674,572" zPosition="2" size="130,40" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/InfoAz/res/greenn.png" transparent="1" alphatest="on" />\n\t\t\t<widget name="img_yellow" position="801,572" zPosition="2" size="130,40" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/InfoAz/res/yellown.png" transparent="1" alphatest="on" />\n\t\t\t<widget name="img_blue" position="928,572" zPosition="2" size="130,40" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/InfoAz/res/bluen.png" transparent="1" alphatest="on" />\n\t\t\t<widget name="titulo" position="288,0" size="746,28" text=" " transparent="1" halign="center" font="Regular; 22" zPosition="1" />\n\t\t\t<ePixmap name="fondo" position="0, 0" size="1050, 602" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/InfoAz/res/fondoinfo-fs8.png" transparent="1" alphatest="blend"/>\n\t\t\t<widget name="barrapix_arr" position="288,37" zPosition="19" size="745,522" alphatest="blend" transparent="1" />\n\t\t\t<widget name="barrapix_abj" position="0,0" zPosition="19" size="20,20" alphatest="blend" transparent="1" />\n\t\t</screen>' % (_('Information') + ' ' + 'openSPA', _('Wait...'))

    def __init__(self, session, inicio = 2, servicio = None, **kwargs):
        self.session = session
        Screen.__init__(self, session)
        self.inicio = inicio
        self.iniciado = False
        self.infoservicio = servicio
        self['lista'] = IniciaSelList([])
        self.TimerTemp = eTimer()
        self.TimerCarga = eTimer()
        self.TimerCerrar = eTimer()
        self.tarea = ''
        self.TimerActualizar = eTimer()
        self.TimerActualizar.callback.append(self.buildList)
        self.TimerCerrar.callback.append(self.exit)
        self.indice = 0
        self.bloquear = False
        self.satNames = {}
        self.readSatXml()
        self.tv_list = []
        self.radio_list = []
        self.upagina = False
        self.TimerTemp.callback.append(self.cargar)
        self.TimerCarga.callback.append(self.key_ok)
        self.craslogs = []
        self.actualizar = False
        self['textoinfo'] = ScrollLabel(_(''))
        self['listaproc'] = IniciaSelListLista([])
        self['listainfo'] = IniciaSelListInfo([])
        self.listarec = []
        self.tmrecord = None
        self['titulo'] = Label(' ')
        self['key_red'] = Label(_(''))
        self['key_green'] = Label('')
        self['key_blue'] = Label(_(''))
        self['key_yellow'] = Label('')
        self['key_izq'] = Label('')
        self['key_dch'] = Label('')
        if self.infoservicio:
            service = ServiceReference(self.infoservicio)
            self.servicio = self.infoservicio
        else:
            service = session.nav.getCurrentService()
            self.servicio = self.session.nav.getCurrentlyPlayingServiceReference()
        self.feinfo = None
        if service is not None:
            self.info = service.info()
            try:
                self.feinfo = service.frontendInfo()
            except:
                pass

        else:
            self.info = None
            self.feinfo = None
        self['img_red'] = MovingPixmap()
        self['img_green'] = MovingPixmap()
        self['img_yellow'] = MovingPixmap()
        self['img_blue'] = MovingPixmap()
        self['img_izq'] = MovingPixmap()
        self['img_dch'] = MovingPixmap()
        self['barrapix_arr'] = Pixmap()
        self['barrapix_abj'] = Pixmap()
        self['setupActions'] = ActionMap(['WizardActions',
         'DirectionActions',
         'ColorActions',
         'NumberActions',
         'MenuActions',
         'EPGSelectActions',
         'InfobarActions'], {'green': self.acc_green,
         'red': self.acc_red,
         'yellow': self.acc_yellow,
         'blue': self.acc_blue,
         'back': self.exit,
         'left': self.key_left,
         'right': self.key_right,
         'up': self.key_up,
         'down': self.key_down,
         'info': self.key_info,
         'ok': self.key_re}, -2)
        self.iniciadoS = False
        self.onLayoutFinish.append(self.buildList)
        self.onShow.append(self.cargaacciones)

    def pontitulo(self):
        self.setTitle(_('Information') + ' ' + 'openSPA' + getTitulo())

    def cargar(self):
        self['textoinfo'].setText('\n' + _('Wait...'))
        self['titulo'].setText(' ')
        self['listainfo'].hide()
        self['listaproc'].hide()
        self['key_red'].hide()
        self['img_red'].hide()
        self['key_blue'].hide()
        self['img_blue'].hide()
        self['key_green'].hide()
        self['img_green'].hide()
        self['key_yellow'].hide()
        self['img_yellow'].hide()
        if self.tarea == 'dmesg':
            self.tarea = ''
        self.TimerCarga.start(200, True)

    def cargaacciones(self):
        self['key_red'].hide()
        self['img_red'].hide()
        self['key_blue'].hide()
        self['img_blue'].hide()
        self['key_green'].hide()
        self['img_green'].hide()
        self['key_yellow'].hide()
        self['img_yellow'].hide()
        self.muestra('izq', 'Page Up')
        self.muestra('dch', 'Page Down')
        self.pontitulo()
        if self.inicio == 6:
            if fileExists('/usr/lib/enigma2/python/Plugins/SystemPlugins/DeviceManager/plugin.pyo'):
                self.muestra('green', 'Manage')
            if fileExists('/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/AzExplorer/plugin.pyo'):
                self.muestra('yellow', 'Explore')
            self.muestra('blue', 'Setup')
        elif self.inicio == 2:
            if fileExists('/usr/lib/enigma2/python/Plugins/SystemPlugins/InfoSignal/plugin.pyo'):
                self.muestra('blue', 'Signal info')
            self.muestra('green', 'Event')
            self.muestra('yellow', 'Guide')
        elif self.inicio == 11:
            if fileExists('/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/spzCAMD/plugin.pyo'):
                self.muestra('yellow', 'spzCAMD')
            if fileExists('/usr/lib/enigma2/python/Plugins/Extensions/GlassSysUtil/plugin.pyo'):
                self.muestra('blue', 'Glass Info')
            elif fileExists('/usr/lib/enigma2/python/Screens/CCcamInfo.pyo') or fileExists('/usr/lib/enigma2/python/Screens/OScamInfo.pyo'):
                self.muestra('blue', 'CAM Info')
        elif self.inicio == 5:
            self.muestra('blue', 'Setup')
            self.muestra('yellow', 'Refresh')
        elif self.inicio == 7:
            self.muestra('yellow', 'Clean RAM')
        elif self.inicio == 4:
            if fileExists('/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/spzBackups/plugin.pyo'):
                self.muestra('green', 'Backup')
            self.muestra('blue', 'Reboot')
            self.muestra('yellow', 'Restart')
        elif self.inicio == 9:
            if fileExists('/usr/lib/enigma2/python/Plugins/SystemPlugins/VideoTune/plugin.pyo'):
                self.muestra('green', 'Brightness')
            if fileExists('/usr/lib/enigma2/python/Screens/SkinSelector.pyo'):
                self.muestra('yellow', 'Skins')
            self.muestra('blue', 'Setup')
        elif self.inicio == 8:
            self.muestra('red', 'Del crashlogs')
            self.muestra('green', 'Last crashlog')
            self.muestra('blue', 'Kernel messages')
            self.muestra('yellow', 'Save to file')
        elif self.inicio == 10:
            self.muestra('blue', 'Updates')
        elif self.inicio == 1:
            self.muestra('green', 'Stop')
            if grabando(self):
                self.muestra('green', 'Edit')
                self.muestra('red', 'Stop')
            else:
                self.muestra('green', 'Add rec')
            self.muestra('yellow', 'Movies')
            self.muestra('blue', 'Recording paths')

    def detengrab(self):
        self.listarec = []
        self.tmrecord = None
        for timer in NavigationInstance.instance.RecordTimer.timer_list:
            if timer.state == timer.StateRunning and not timer.disabled:
                try:
                    if timer.Filename:
                        pass
                    self.listarec.append(timer)
                    self.tmrecord = timer
                except:
                    pass

        if len(self.listarec) > 1:
            self.seleGrab()
            return
        if not self.tmrecord == None:
            self.session.openWithCallback(self.stopRecordConfirmation, MessageBox, _('Stop current recording?') + ':\n' + str(self.tmrecord.name), MessageBox.TYPE_YESNO)

    def cbseleGrab(self, answer):
        answer = answer and answer[1]
        if not answer:
            return
        sel = int(answer)
        self.tmrecord = self.listarec[sel]
        if not self.tmrecord == None:
            self.session.openWithCallback(self.stopRecordConfirmation, MessageBox, _('Stop current recording?') + ':\n' + str(self.tmrecord.name), MessageBox.TYPE_YESNO)

    def seleGrab(self):
        list = []
        nkeys = []
        conta = 0
        for elerec in self.listarec:
            nombre = elerec.name
            if len(nombre) > 17:
                nombre = nombre[:15] + '...'
            nombre = nombre + ' (' + str(FuzzyTime(elerec.begin)[1])
            nombre = nombre + ' - ' + str(FuzzyTime(elerec.end)[1])
            nombre = nombre + ') ' + elerec.service_ref.getServiceName()
            list.append((nombre + ' ', str(conta)))
            nkeys.append(str(conta + 1))
            if conta < 9:
                conta = conta + 1

        if len(list) > 0:
            from Screens.ChoiceBox import ChoiceBox
            self.session.openWithCallback(self.cbseleGrab, ChoiceBox, keys=nkeys, title=_('Select Record to stop'), list=list)

    def cbborralogs(self, answer):
        if answer:
            rutacras = '/home/root/logs/enigma2_crash_*.log'
            os.system('rm ' + rutacras)
            cmens = _('Delete crashlogs') + ':\n' + rutacras + '\n' + _('Have been deleted!')
            dei = self.session.open(MessageBox, cmens, MessageBox.TYPE_INFO)
            dei.setTitle(_('Del crashlogs'))

    def devcras(self, siultimo = False):
        self.craslogs = []
        ret = cargaosinfo('ls /home/root/logs/enigma2_crash_*.log -t -c -w 1')
        lista = ret.split('\n')
        conta = 0
        cret = None
        for ele in lista:
            ele = ele.replace('\n', '')
            if '.log' in ele:
                if siultimo and not cret:
                    cret = ele
                self.craslogs.append(ele)

        return cret

    def acc_red(self):
        if self.inicio == 1 and grabando(self):
            self.detengrab()
        elif self.inicio == 8:
            rutacras = '/home/root/logs/enigma2_crash_*.log'
            ret = self.devcras()
            if len(self.craslogs) == 0:
                self.session.open(MessageBox, _('No crashlogs found in path: /home/root/logs/'), MessageBox.TYPE_INFO)
                return
            cmens = _('Delete crashlogs') + ' ' + str(len(self.craslogs)) + ' ' + _('file(s)') + ':\n' + rutacras + '\n' + _('You are sure to delete .log files?')
            dei = self.session.openWithCallback(self.cbborralogs, MessageBox, cmens, MessageBox.TYPE_YESNO)
        elif self.inicio == 11:
            if fileExists('/usr/lib/enigma2/python/Plugins/Extensions/CAMDManager/plugin.pyo'):
                try:
                    from Plugins.Extensions.CAMDManager.plugin import startConfig
                    startConfig(self.session)
                except:
                    pass

        elif self.inicio == 55:
            from Screens.Menu import MainMenu
            import xml.etree.cElementTree
            xmdom = xml.etree.cElementTree.parse(resolveFilename(SCOPE_SKIN, 'menu.xml'))
            root = xmdom.getroot()
            ret = ''
            for x in root.findall('menu'):
                y = x.find('id')
                if y is not None:
                    id = y.get('val')
                    if id and id == 'setup':
                        for j in x:
                            for h in j:
                                ret = ret + str(h) + '\n'
                                mo = h.get('module')
                                sc = h.get('screen')
                                if mo:
                                    ret = ret + mo + ' :: '
                                if sc:
                                    ret = ret + sc
                                ret = ret + '\n'
                                try:
                                    ret = ret + str(h.nodeValue) + '\n'
                                except:
                                    pass

            self['textoinfo'].setText(ret)

    def acc_green(self):
        if self.inicio == 1:
            try:
                from Screens.TimerEdit import TimerEditList
                self.session.open(TimerEditList)
            except:
                pass

        elif self.inicio == 8:
            self.tarea = 'cras'
            self.buildList()
        elif self.inicio == 2:
            from Screens.InfoBar import InfoBar
            if InfoBar and InfoBar.instance:
                InfoBar.openEventView(InfoBar.instance)
        elif self.inicio == 4:
            try:
                from Plugins.Extensions.spazeMenu.spzPlugins.spzBackups.plugin import mainHome
                mainHome(self.session)
            except:
                pass

        elif self.inicio == 11:
            try:
                from Plugins.Extensions.spazeMenu.spzPlugins.spzCAMD.plugin import startConfig
                startConfig(self.session)
            except:
                pass

        elif self.inicio == 6:
            try:
                from Plugins.SystemPlugins.DeviceManager.plugin import deviceManagerMain
                deviceManagerMain(self.session)
            except:
                pass

        elif self.inicio == 9:
            try:
                from Plugins.SystemPlugins.VideoTune.VideoFinetune import VideoFinetune
                self.session.open(VideoFinetune)
            except:
                pass

    def acc_yellow(self):
        if self.inicio == 2:
            try:
                from Screens.InfoBar import InfoBar
                if InfoBar and InfoBar.instance:
                    servicelist = InfoBar.instance.servicelist
                from Plugins.Extensions.spazeMenu.spzPlugins.openSPATVGuide.plugin import main
                main(self.session, servicelist)
            except:
                pass

        elif self.inicio == 4:
            laref = _('Restart GUI?')
            dei = self.session.openWithCallback(self.reiniciargui, MessageBox, laref, MessageBox.TYPE_YESNO)
        elif self.inicio == 7:
            from Plugins.Extensions.spazeMenu.plugin import limpiamemoria
            limpiamemoria(3, 'manual_info_az')
            cmens = _('Cache RAM memory cleaned!')
            dei = self.session.open(MessageBox, cmens, MessageBox.TYPE_INFO)
            dei.setTitle(_('Clean RAM'))
            self.buildList()
        elif self.inicio == 9:
            try:
                from Screens.SkinSelector import SkinSelector
                self.session.open(SkinSelector)
            except:
                pass

        elif self.inicio == 1:
            try:
                useemc = config.misc.spazeuseemc.value
            except:
                useemc = False

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
        elif self.inicio == 5:
            self.tarea = 'ping'
            self.buildList()
        elif self.inicio == 8:
            self.TimerActualizar.stop()
            lalista = self['listaproc'].list
            cadena = ' ******** AzInfoLog ' + cargaosinfo('date').replace('\n', '') + '*************\n'
            try:
                newbooklist = open('/tmp/InfoAz.log', 'w')
            except:
                dei = self.session.open(MessageBox, _('Error by writing log file !!!'), MessageBox.TYPE_ERROR)
                dei.setTitle(_('InfoAz'))

            if newbooklist is not None:
                newbooklist.write(cadena)
                for i in lalista:
                    newbooklist.write(str(i[0]) + '')

                newbooklist.close()
            info1 = _('Log File saved to') + ':\n'
            info2 = '/tmp/InfoAz.log'
            cmens = info1 + '\n' + info2
            dei = self.session.open(MessageBox, cmens, MessageBox.TYPE_INFO)
            dei.setTitle(_('Save to file'))
            self.TimerActualizar.start(15000, True)
        elif self.inicio == 6:
            lalista = self['listainfo'].list
            idx = self['listainfo'].getSelectionIndex()
            ruta = str(lalista[idx][0])
            try:
                from Plugins.Extensions.spazeMenu.spzPlugins.AzExplorer.plugin import main
                main(self.session, ruta)
            except:
                pass

        elif self.inicio == 11:
            try:
                from Plugins.Extensions.spazeMenu.spzPlugins.spzCAMD.plugin import startConfig
                startConfig(self.session)
            except:
                pass

        elif self.inicio == 1111:
            askList = [(_('Start CCAM'), 'start'), (_('Stop CCAM'), 'stop')]
            if fileExists('/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/spzCAMD/plugin.pyo'):
                askList.append((_('spzCAMD Manager'), 'spzCAMD'))
            dei = self.session.openWithCallback(self.ccamscript, ChoiceBox, title=_('Select option'), list=askList)
            dei.setTitle(_('Options') + ' CCAMD')

    def acc_blue(self):
        if self.inicio == 6:
            self.ejecutaMenu2('harddisk')
        elif self.inicio == 2:
            try:
                from Plugins.SystemPlugins.InfoSignal.plugin import InfoSignal
                from Screens.InfoBar import InfoBar
                if InfoBar and InfoBar.instance:
                    NOTIFICATIONID = 'InfoSignalID'
                    from Tools.Notifications import AddNotificationWithID, RemovePopup
                    try:
                        RemovePopup(NOTIFICATIONID)
                    except:
                        pass

                    AddNotificationWithID(NOTIFICATIONID, InfoSignal, InfoBar.instance.servicelist)
                    self.exit()
            except:
                pass

        elif self.inicio == 10:
            try:
                from Plugins.Extensions.spazeMenu.spzPlugins.descargasSPZ.plugin import main
                main(self.session)
            except:
                pass

        elif self.inicio == 11:
            if fileExists('/usr/lib/enigma2/python/Plugins/Extensions/GlassSysUtil/plugin.pyo'):
                try:
                    from Plugins.Extensions.GlassSysUtil.plugin import main
                    main(self.session)
                except:
                    pass

            elif fileExists('/usr/lib/enigma2/python/Screens/CCcamInfo.pyo'):
                from Screens.InfoBar import InfoBar
                if InfoBar and InfoBar.instance:
                    try:
                        from Screens.CCcamInfo import CCcamInfoMain
                        InfoBar.instance.session.open(CCcamInfoMain)
                    except:
                        pass

            elif fileExists('/usr/lib/enigma2/python/Screens/OScamInfo.pyo'):
                from Screens.InfoBar import InfoBar
                if InfoBar and InfoBar.instance:
                    try:
                        from Screens.OScamInfo import OscamInfoMenu
                        InfoBar.instance.session.open(OscamInfoMenu)
                    except:
                        pass

        elif self.inicio == 8:
            self.tarea = 'dmesg'
            self.buildList()
        elif self.inicio == 4:
            laref = _('Reboot system?')
            dei = self.session.openWithCallback(self.reiniciar, MessageBox, laref, MessageBox.TYPE_YESNO)
        elif self.inicio == 9:
            try:
                from Screens.VideoMode import VideoSetup
                self.session.open(VideoSetup)
                return
            except:
                pass

        elif self.inicio == 5:
            try:
                from Screens.NetworkSetup import NetworkAdapterSelection
                self.session.open(NetworkAdapterSelection)
            except:
                pass

        elif self.inicio == 1:
            try:
                from Screens.RecordPaths import RecordPathsSettings
                self.session.open(RecordPathsSettings)
            except:
                pass

    def ccamscript(self, answer):
        answer = answer and answer[1]
        if answer:
            if answer == 'spzCAMD':
                try:
                    from Plugins.Extensions.spazeMenu.spzPlugins.spzCAMD.plugin import startConfig
                    startConfig(self.session)
                except:
                    pass

            else:
                self.tarea = answer
                self.cargar()

    def ejecutaMenu2(self, nombreid):
        from Screens.Menu import MainMenu
        import xml.etree.cElementTree
        ret = '\n\n\n\n\n\n\n**** ' + nombreid + '***\n'
        xmdom = xml.etree.cElementTree.parse(resolveFilename(SCOPE_SKIN, 'menu.xml'))
        root = xmdom.getroot()
        for x in root.findall('menu'):
            y = x.find('id')
            if y is not None:
                id = y.get('val')
                ret = ret + str(id) + '\n'
                if id and id == 'setup':
                    for j in x.findall('menu'):
                        m = j.find('id')
                        if m is not None:
                            id2 = m.get('val')
                            ret = ret + str(id2) + '\n'
                            if id2 and id2 == 'system':
                                for j2 in j.findall('menu'):
                                    m2 = j2.find('id')
                                    if m2 is not None:
                                        id3 = m2.get('val')
                                        ret = ret + str(id3) + '\n'
                                        if id3 and id3 == nombreid:
                                            self.session.infobar = self
                                            menu_screen = self.session.openWithCallback(self.MenuClosed, MainMenu, j2)
                                            menu_screen.setTitle(_('Setup'))

    def ejecutaMenu(self, nombreid):
        from Screens.Menu import MainMenu
        import xml.etree.cElementTree
        xmdom = xml.etree.cElementTree.parse(resolveFilename(SCOPE_SKIN, 'menu.xml'))
        root = xmdom.getroot()
        for x in root.findall('menu'):
            y = x.find('id')
            if y is not None:
                id = y.get('val')
                if id and id == 'setup':
                    for j in x.findall('menu'):
                        m = j.find('id')
                        if m is not None:
                            id2 = m.get('val')
                            if id2 and id2 == nombreid:
                                self.session.infobar = self
                                menu_screen = self.session.openWithCallback(self.MenuClosed, MainMenu, j)
                                menu_screen.setTitle(_('Setup'))

    def reiniciar(self, respuesta):
        if respuesta:
            self.session.open(TryQuitMainloop, 2)

    def MenuClosed(self, dummy):
        pass

    def reiniciargui(self, respuesta):
        if respuesta:
            self.session.open(TryQuitMainloop, 3)

    def ejecutaPlugin(self, nombre):
        from Components.PluginComponent import plugins
        for plugin in plugins.getPlugins([PluginDescriptor.WHERE_PLUGINMENU,
         PluginDescriptor.WHERE_MENU,
         PluginDescriptor.WHERE_EXTENSIONSMENU,
         PluginDescriptor.WHERE_EVENTINFO]):
            if plugin.name == _(nombre):
                plugin(session=self.session)
                break

    def stopRecordConfirmation(self, confirmed):
        if not confirmed:
            return
        if self.tmrecord == None:
            return
        try:
            for timer in NavigationInstance.instance.RecordTimer.timer_list:
                if timer.isRunning() and not timer.justplay and timer.Filename == self.tmrecord.Filename:
                    self.TimerActualizar.stop()
                    self.TimerTemp.stop()
                    if timer.repeated:
                        return False
                    timer.afterEvent = AFTEREVENT.NONE
                    NavigationInstance.instance.RecordTimer.removeEntry(timer)
                    if not grabando(self):
                        self['img_red'].hide()
                    self.buildList()

        except:
            pass

    def muestra(self, cual, texto):
        self['key_' + cual].show()
        self['img_' + cual].show()
        self['key_' + cual].setText(_(texto))

    def accionlistaproc(self):
        self['listaproc'].selectionEnabled(0)
        texto = ' '
        templista = []
        if self.inicio == 8:
            self['listaproc'].selectionEnabled(0)
            if self.tarea == 'dmesg':
                orden = 'dmesg'
            else:
                orden = 'ps'
            os.system(orden + ' >/tmp/tempinfo1')
            booklist = None
            booklist = open('/tmp/tempinfo1', 'r')
            temparray = []
            if booklist is not None:
                for oneline in booklist:
                    temparray.append(oneline)

                booklist.close()
            os.system('rm /tmp/tempinfo1')
            for i in range(0, len(temparray)):
                if i > 0:
                    templista.append(IniciaSelListEntryLista(texto1=temparray[i]))

        if not templista == None:
            self['listaproc'].setList(templista)
        self['listaproc'].show()
        return texto

    def accionlista(self):
        self['listainfo'].selectionEnabled(0)
        texto = ' '
        templista = []
        if self.inicio == 1:
            listarec = inforecord()
            texto = ''
            if len(listarec) == 1:
                texto = _('File name') + ': ' + listarec[0][8] + ''
            else:
                texto = ''
            for infog in listarec:
                templista.append(IniciaSelListEntryInfo(texto1=infog[1] + ' - ' + infog[0], texto2=infog[4] + '(+' + infog[5] + ')', texto3=infog[2], texto4=infog[3], texto5=str(infog[7]) + '%', imagen1=5, progreso=infog[7]))

        elif self.inicio == 6:
            self['listainfo'].selectionEnabled(1)
            sumtam = 0
            sumfree = 0
            sumocupado = 0
            summontado = ''
            sumporcentaje = 0
            contaflash = 0
            entrointernal = False
            for p in harddiskmanager.getMountedPartitions():
                texto = _(str(p.description)).replace('External', _('External'))
                montado = str(p.mountpoint)
                if os.path.exists(p.mountpoint + '/') or p.mountpoint == '/':
                    ntipo = 3
                    if p.mountpoint == '/' or p.mountpoint == '/dev' or p.mountpoint == '/tmp' or p.mountpoint == '/boot' or p.mountpoint == '/media/cf':
                        ntipo = 0
                    elif p.mountpoint[:len('/dev/hda')] == '/dev/hda':
                        ntipo = 0
                    elif p.mountpoint[:len('/autofs/sd')] == '/autofs/sd' or p.mountpoint[:len('/dev/sd')] == '/dev/sd' or p.mountpoint[:len('/media/usb')] == '/media/usb':
                        ntipo = 2
                        texto = 'USB ' + texto
                    elif p.mountpoint[:len('/media/hdd')] == '/media/hdd' or p.mountpoint[:len('/dev/hdb')] == '/dev/hdb':
                        ntipo = 1
                    if p.mountpoint == '/':
                        path = '/'
                    else:
                        path = p.mountpoint + '/'
                    stat = os.statvfs(path)
                    total = stat.f_bsize * stat.f_blocks
                    free = (stat.f_bavail if stat.f_bavail != 0 else stat.f_bfree) * stat.f_bsize
                    ocupado = total - stat.f_bsize * stat.f_bfree
                    porcentaje = int(ocupado * 100 / total)
                    if ntipo == 10:
                        entrointernal = True
                        sumtam = sumtam + total
                        sumfree = sumfree + free
                        sumocupado = sumocupado + ocupado
                        sumporcentaje = sumporcentaje + porcentaje
                        summontado = summontado + '[' + montado + '] '
                        if contaflash == 1:
                            templista.append(IniciaSelListEntryInfo(texto1=texto + ' - ' + summontado, texto2=_('Size') + ' ' + Humanizer(sumtam), texto3=_('Used') + ' ' + Humanizer(sumocupado), texto4=Humanizer(sumfree) + ' ' + _('Frees'), texto5=str(sumporcentaje / 6) + '%', imagen1=ntipo, progreso=sumporcentaje / 6, ruta=path + '/'))
                            entrointernal = False
                        contaflash = contaflash + 1
                    else:
                        if entrointernal:
                            templista.append(IniciaSelListEntryInfo(texto1=texto + ' - ' + summontado, texto2=_('Size') + ' ' + Humanizer(sumtam), texto3=_('Used') + ' ' + Humanizer(sumocupado), texto4=Humanizer(sumfree) + ' ' + _('Frees'), texto5=str(sumporcentaje / 6) + '%', imagen1=ntipo, progreso=sumporcentaje / 6, ruta=path + '/'))
                            entrointernal = False
                            contaflash = 0
                        templista.append(IniciaSelListEntryInfo(texto1=texto + ' - ' + montado, texto2=_('Size') + ' ' + Humanizer(total), texto3=_('Used') + ' ' + Humanizer(ocupado), texto4=Humanizer(free) + ' ' + _('Frees'), texto5=str(porcentaje) + '%', imagen1=ntipo, progreso=porcentaje, ruta=path + '/'))

        elif self.inicio == 7:
            ret = ''
            orden = 'free'
            archivo = '/tmp/tempinfo'
            os.system(orden + ' >/tmp/tempinfo')
            booklist = None
            booklist = open(archivo, 'r')
            temparray = []
            if booklist is not None:
                for oneline in booklist:
                    temparray.append(oneline)

                booklist.close()
            os.system('rm /tmp/tempinfo')
            haytotal = False
            totalmem = 0
            totalused = 0
            totalfree = 0
            haysw = False
            for i in range(0, len(temparray)):
                if i > 0:
                    array = temparray[i].split()
                    tipo = array[0]
                    ntipo = 4
                    if tipo == 'Mem:':
                        tipo = _('Ram memory')
                        ntipo = 4
                    elif tipo == 'Swap:':
                        tipo = _('Swap memory')
                        ntipo = 3
                        haysw = True
                    elif tipo == 'Total:':
                        haytotal = True
                        tipo = _('Total memory')
                        ntipo = 6
                    else:
                        tipo = tipo.replace(':', '')
                        ntipo = 9
                    err = False
                    addint = 0
                    try:
                        total = _('Size') + ' ' + Humanizer(int(array[1]) * 1024)
                        totalmem = totalmem + int(array[1])
                        if tipo == 'Mem:':
                            if len(array) > 5:
                                addint = int(array[5])
                            usado = _('Used') + ' ' + Humanizer(int(array[2]) * 1024 + addint * 1024)
                            totalused = totalused + int(array[2]) + addint
                        else:
                            usado = _('Used') + ' ' + Humanizer(int(array[2]) * 1024)
                            totalused = totalused + int(array[2])
                        libre = _('Free') + ' ' + Humanizer(int(array[3]) * 1024)
                        totalfree = totalfree + int(array[3])
                    except:
                        err = True

                    if not err:
                        if len(array) > 5:
                            if int(array[5]) > 0:
                                tipo = tipo + ' - ' + _('Cache') + ': ' + Humanizer(int(array[5]) * 1024) + ' '
                        try:
                            porcentaje = (int(array[2]) + addint) * 100 / int(array[1])
                        except:
                            porcentaje = 0

                        templista.append(IniciaSelListEntryInfo(texto1=tipo, texto2=total, texto3=usado, texto4=libre, texto5=str(porcentaje) + '%', imagen1=ntipo, progreso=porcentaje))

            if not haytotal:
                try:
                    porcentaje = totalused * 100 / totalmem
                    templista.append(IniciaSelListEntryInfo(texto1=_('Total memory'), texto2=_('Size') + ' ' + Humanizer(totalmem * 1024), texto3=_('Used') + ' ' + Humanizer(totalused * 1024), texto4=_('Free') + ' ' + Humanizer(totalfree * 1024), texto5=str(porcentaje) + '%', imagen1=6, progreso=porcentaje))
                except:
                    pass

        if not templista == None:
            self['listainfo'].setList(templista)
        self['listainfo'].show()
        return texto

    def inicializa(self):
        self.bloquear = False
        self.buildList()
        self.cargaacciones()

    def getListFromRef(self, ref):
        list = []
        serviceHandler = eServiceCenter.getInstance()
        services = serviceHandler.list(ref)
        bouquets = services and services.getContent('SN', True)
        for bouquet in bouquets:
            services = serviceHandler.list(eServiceReference(bouquet[0]))
            channels = services and services.getContent('SN', True)
            for channel in channels:
                if not channel[0].startswith('1:64:'):
                    list.append(channel[1].replace('\xc2\x86', '').replace('\xc2\x87', ''))

        return list

    def getServiceInfoValue(self, what):
        if self.info is None:
            return ''
        v = self.info.getInfo(what)
        if v == -2:
            v = self.info.getInfoString(what)
        elif v == -1:
            v = 'N/A'
        return v

    def getFEData(self, frontendDataOrg):
        from Tools.Transponder import ConvertToHumanReadable
        TYPE_TEXT = 0
        TYPE_VALUE_HEX = 1
        TYPE_VALUE_DEC = 2
        TYPE_VALUE_HEX_DEC = 3
        TYPE_SLIDER = 4
        if frontendDataOrg and len(frontendDataOrg):
            frontendData = ConvertToHumanReadable(frontendDataOrg)
            if frontendDataOrg['tuner_type'] == 'DVB-S':
                return (('NIM', chr(ord('A') + frontendData['tuner_number']), TYPE_TEXT),
                 ('Type', frontendData['system'], TYPE_TEXT),
                 ('Modulation', frontendData['modulation'], TYPE_TEXT),
                 ('Frequency', frontendData['frequency'], TYPE_VALUE_DEC),
                 ('Symbolrate', frontendData['symbol_rate'], TYPE_VALUE_DEC),
                 ('Polarization', frontendData['polarization'], TYPE_TEXT),
                 ('Inversion', frontendData['inversion'], TYPE_TEXT),
                 ('FEC inner', frontendData['fec_inner'], TYPE_TEXT),
                 ('Pilot', frontendData.get('pilot', None), TYPE_TEXT),
                 ('Rolloff', frontendData.get('rolloff', None), TYPE_TEXT))
            if frontendDataOrg['tuner_type'] == 'DVB-C':
                return (('NIM', chr(ord('A') + frontendData['tuner_number']), TYPE_TEXT),
                 ('Type', frontendData['tuner_type'], TYPE_TEXT),
                 ('Frequency', frontendData['frequency'], TYPE_VALUE_DEC),
                 ('Symbolrate', frontendData['symbol_rate'], TYPE_VALUE_DEC),
                 ('Modulation', frontendData['modulation'], TYPE_TEXT),
                 ('Inversion', frontendData['inversion'], TYPE_TEXT),
                 ('FEC inner', frontendData['fec_inner'], TYPE_TEXT))
            if frontendDataOrg['tuner_type'] == 'DVB-T':
                return (('NIM', chr(ord('A') + frontendData['tuner_number']), TYPE_TEXT),
                 ('Type', frontendData['tuner_type'], TYPE_TEXT),
                 ('Frequency', str(frontendData['frequency']) + ' (' + str(ajustafr(int(frontendData['frequency']))) + ' Khz)', TYPE_VALUE_DEC),
                 ('Channel', str(devchfr(frontendData['frequency'])), TYPE_VALUE_DEC),
                 ('Inversion', frontendData['inversion'], TYPE_TEXT),
                 ('Bandwidth', frontendData['bandwidth'], TYPE_VALUE_DEC),
                 ('CodeRateLP', frontendData['code_rate_lp'], TYPE_TEXT),
                 ('CodeRateHP', frontendData['code_rate_hp'], TYPE_TEXT),
                 ('Constellation', frontendData['constellation'], TYPE_TEXT),
                 ('Transmission Mode', frontendData['transmission_mode'], TYPE_TEXT),
                 ('Guard Interval', frontendData['guard_interval'], TYPE_TEXT),
                 ('Hierarchy Inform.', frontendData['hierarchy_information'], TYPE_TEXT))
        return []

    def readSatXml(self):
        from xml.etree.cElementTree import parse
        satXml = parse('/etc/tuxbox/satellites.xml').getroot()
        if satXml is not None:
            for sat in satXml.findall('sat'):
                name = sat.get('name') or None
                position = sat.get('position') or None
                if name is not None and position is not None:
                    position = '%s.%s' % (position[:-1], position[-1:])
                    if position.startswith('-'):
                        position = '%sW' % position[1:]
                    else:
                        position = '%sE' % position
                    if position.startswith('.'):
                        position = '0%s' % position
                    self.satNames[position] = name

    def getOrbitalPosition(self, info):
        transponderData = info.getInfoObject(iServiceInformation.sTransponderData)
        orbital = 0
        if transponderData is not None:
            if isinstance(transponderData, float):
                return ''
            if transponderData.has_key('tuner_type'):
                if transponderData['tuner_type'] == 'DVB-S' or transponderData['tuner_type'] == 'DVB-S2':
                    orbital = transponderData['orbital_position']
                    orbital = int(orbital)
                    if orbital > 1800:
                        orbital = str(float(3600 - orbital) / 10.0) + 'W'
                    else:
                        orbital = str(float(orbital) / 10.0) + 'E'
                    return orbital
        return ''

    def getServiceNumber(self, name, ref):
        list = []
        if ref.startswith('1:0:2'):
            list = self.radio_list
        elif ref.startswith('1:0:1'):
            list = self.tv_list
        number = ''
        if name in list:
            for idx in range(1, len(list)):
                if name == list[idx - 1]:
                    number = str(idx)
                    break

        return number

    def infored(self):
        ret = ''
        from Components.Network import iNetwork
        from os import path as os_path, system as os_system, unlink
        adapters = [ (iNetwork.getFriendlyAdapterName(x), x) for x in iNetwork.getAdapterList() ]
        if not adapters:
            return '\n' + _('No net adapters configured')
        default_gw = None
        num_configured_if = len(iNetwork.getConfiguredAdapters())
        if num_configured_if < 2 and os_path.exists('/etc/default_gw'):
            unlink('/etc/default_gw')
        if os_path.exists('/etc/default_gw'):
            fp = file('/etc/default_gw', 'r')
            result = fp.read()
            fp.close()
            default_gw = result
        hay1 = ''
        if len(adapters) == 0:
            ret = _('iface') + '-> ' + 'eth0' + ' :: ' + _('Name') + '-> ' + _(iNetwork.getFriendlyAdapterName('eth0')) + _('Default') + '-> ' + str(True) + _('Active') + '-> ' + str(True) + '\n'
        else:
            for x in adapters:
                cpre = ''
                if x[1] == default_gw:
                    default_int = True
                    cpre = _('Default')
                else:
                    default_int = False
                if iNetwork.getAdapterAttribute(x[1], 'up') is True:
                    active_int = True
                else:
                    active_int = False
                description = iNetwork.getFriendlyAdapterDescription(x[1])
                if active_int:
                    estado = _('ACTIVE')
                else:
                    estado = _('Inactive')
                ret = ret + _(x[0]) + ' (' + str(x[1]) + ')-> ' + cpre + _('State') + '-> ' + estado + '\n'
                tabu = '        '
                if active_int:
                    iNetwork.loadNameserverConfig()
                    ret = ret + tabu + _('IP') + '-> ' + str(iNetwork.getAdapterAttribute(x[1], 'ip')) + ' :: '
                    ret = ret + _('Mask') + '-> ' + str(iNetwork.getAdapterAttribute(x[1], 'netmask')) + '\n'
                    if iNetwork.getAdapterAttribute(x[1], 'gateway'):
                        dhcpl = _('yes')
                    else:
                        dhcpl = _('no')
                    if iNetwork.getAdapterAttribute(x[1], 'dhcp'):
                        dhcp2 = _('yes')
                    else:
                        dhcp2 = _('no')
                    ret = ret + tabu + _('Gateway') + '-> ' + str(iNetwork.getAdapterAttribute(x[1], 'gateway')) + ' :: '
                    ret = ret + _('Dhcp') + '-> ' + dhcp2 + '\n'
                    nameserver = (iNetwork.getNameserverList() + [[0,
                      0,
                      0,
                      0]] * 2)[0:2]
                    ret = ret + tabu + _('Primary DNS') + '-> ' + str(nameserver[0]) + ' :: '
                    ret = ret + _('Secondary DNS') + '-> ' + str(nameserver[1]) + ''
                    array = cargaosinfo('ifconfig ' + x[1] + ' | grep HWaddr').split('HWaddr')
                    if len(array) > 1:
                        ret = ret + '\n' + tabu + _('MAC adress') + '(' + x[1] + ')-> ' + array[1]
                    else:
                        ret = ret + '\n'
                    ret = ret + '\n'
                    estadis = cargaosinfo('ifconfig ' + x[1] + ' | grep bytes', True)
                    if 'Device not found' in estadis:
                        estadis = ''
                    estadis = estadis.replace('RX bytes', _('Received bytes')).replace('TX bytes', _('Transmited bytes')).replace('   ', ' ')
                    ret = ret + _('Stats') + ':\n ' + estadis + ''
                    if self.tarea == 'ping':
                        cpong = cargaosinfo('ping -c 3 -q -W 4 google.com', True)
                    else:
                        cpong = cargaosinfo('ping -c 1 -q -W 4 google.com', True)
                    ippub = ''
                    if len(cpong + ' ') < 2:
                        cpong = _('Internet conection not avaiable') + '\n'
                    else:
                        laurl = 'http://checkip.dyndns.org/'
                        import urllib2
                        try:
                            response = urllib2.urlopen(laurl, timeout=4)
                            ippub = response.read()
                            xstr = ippub.split('<body>')[1]
                            xstr = xstr.split('</body>')[0]
                            if len(xstr) > 8:
                                ippub = xstr
                            xstr = xstr.split(':')[1]
                            if len(xstr) > 8:
                                ippub = xstr.lstrip().rstrip()
                        except:
                            ippub = _('No info avaiable')

                        if len(ippub) > 8:
                            ippub = '\n' + _('Public IP') + ': ' + ippub + '\n'
                    test = _('Internet Conection TEST') + ':\n ' + cpong.replace('--- azboxhd.es ping statistics ---', '').replace('\n\n', '').replace('packets transmitted', _('packets transmitted')).replace('packets received', _('packets received')).replace('packet loss', _('packet loss')).replace('round-trip', '').replace('azboxhd.es', 'openSPA').replace('google.com', 'openSPA')
                    if test == _('No info avaiable'):
                        test = _('Ping to host azboxhd.es failed\n').replace('azboxhd.es', 'openSPA')
                    ret = hay1 + ret + '\n' + test + ippub
                    hay1 = '\n'

        self.tarea = ''
        return ret

    def buildList(self):
        global lenguaje
        self.TimerActualizar.stop()
        self.TimerTemp.stop()
        self['textoinfo'].setText('\n' + _('Wait...'))
        self['titulo'].setText(' ')
        self['listainfo'].hide()
        self['listaproc'].hide()
        lista = []
        xvalor = cargalista(self.inicio, grabando(self))
        lista = xvalor[1]
        indice = xvalor[0]
        self.indice = indice
        if not self.iniciado:
            self['lista'].setList(lista)
        self.iniciado = True
        if indice >= 0:
            self['lista'].moveToIndex(indice)
            titulo = listamenu[indice][1]
            self['titulo'].setText(titulo)
        texto = _('Information not avaiable')
        self.actualizar = False
        if self.inicio == 1:
            if grabando(self):
                texto = '\n\n\n\n\n'
                texto = texto + self.accionlista() + '\n'
                self.actualizar = True
            else:
                texto = '\n' + _('No records in progress')
                texto = texto + '\n\n' + _('Records path') + ': ' + str(config.usage.default_path.value) + '\n'
                texto = texto + _('Instant Records path') + ': ' + str(config.usage.instantrec_path.value) + '\n'
        if self.inicio == 3:
            texto = ''
            try:
                from Plugins.Extensions.spazeMenu.hardinfo import tipoModelo
                texto = _('Model') + ' ' + tipoModelo(True) + '\n'
            except:
                texto = _('Model') + ' ' + HardwareInfo().get_device_name() + '\n'

            texto = texto + cargaosinfo('cat /proc/cpuinfo')
        elif self.inicio == 7:
            texto = '  '
            ret = self.accionlista()
            self.actualizar = True
        elif self.inicio == 2:
            if self.infoservicio:
                texto = infocanal(self.infoservicio, self.info)
            else:
                texto = ''
                try:
                    name = self.info.getName().replace('\xc2\x86', '').replace('\xc2\x87', '')
                    nomcan = ServiceReference(self.servicio).getServiceName().replace('\xc2\x86', '').replace('\xc2\x87', '')
                    texto = _('Channel') + '-> ' + nomcan + ' :: ' + _('Provider') + '-> ' + self.getServiceInfoValue(iServiceInformation.sProvider) + '\n'
                    laref = self.servicio.toString()
                    if laref.startswith('1:0:0:0') or laref.startswith('4097:0:0:0') and 'http' not in laref:
                        texto = _('Playback') + '-> ' + nomcan + '\n'
                        texto = texto + _('File') + '-> ' + laref.replace('1:0:0:0:0:0:0:0:0:0:', '').replace('4097:0:0:0:0:0:0:0:0:0:', '') + '\n'
                    elif laref.startswith('4097:0:0:'):
                        ref = laref
                        laurl = ''
                        nombre = ''
                        try:
                            laurl = _('URL') + '-> ' + ref.replace('4097:0:0:0:0:0:0:0:0:0:', '').split(':')[0].replace('%3a', ':') + '\n'
                        except:
                            pass

                        texto = texto + _('System') + '-> ' + ' IPTV (Internet Protocol Television)\n'
                        texto = texto + laurl
                        texto = texto + _('Service reference') + '-> ' + laref + '\n'
                    else:
                        if self.servicio.flags & eServiceReference.isGroup:
                            laref = '(' + _('Alternatives') + ') ' + getBestPlayableServiceReference(self.servicio, eServiceReference(), True).toString()
                        texto = texto + _('Service reference') + '-> ' + laref + '\n'
                        calidad = 0
                        status = self.feinfo.getFrontendStatus()
                        calidad = status.get('tuner_signal_quality') * 100 / 65536
                        potencia = 0
                        status = self.feinfo.getFrontendStatus()
                        potencia = status.get('tuner_signal_power') * 100 / 65536
                        terror = 0
                        status = self.feinfo.getFrontendStatus()
                        terror = status.get('tuner_bit_error_rate') * 100 / 65536
                        texto = texto + _('Signal quality') + ' ' + ponPorcen(calidad) + ' :: ' + _('Intensity') + ' ' + ponPorcen(potencia) + ', ' + str(terror) + '% ' + _('of error') + '\n\n'
                        aspect = self.getServiceInfoValue(iServiceInformation.sAspect)
                        if aspect in (1, 2, 5, 6, 9, 10, 13, 14):
                            texto = texto + _('Videoformat') + '-> 4:3'
                        else:
                            texto = texto + _('Videoformat') + '-> 16:9'
                        width = self.info and self.info.getInfo(iServiceInformation.sVideoWidth) or -1
                        height = self.info and self.info.getInfo(iServiceInformation.sVideoHeight) or -1
                        texto = texto + ' :: ' + _('Videosize') + '-> ' + '%dx%d' % (width, height) + '\n'
                        TYPE_VALUE_HEX_DEC = 3
                        xLabels = (('VideoPID',
                          self.getServiceInfoValue(iServiceInformation.sVideoPID),
                          TYPE_VALUE_HEX_DEC,
                          4),
                         ('AudioPID',
                          self.getServiceInfoValue(iServiceInformation.sAudioPID),
                          TYPE_VALUE_HEX_DEC,
                          4),
                         ('PCRPID',
                          self.getServiceInfoValue(iServiceInformation.sPCRPID),
                          TYPE_VALUE_HEX_DEC,
                          4),
                         ('PMTPID',
                          self.getServiceInfoValue(iServiceInformation.sPMTPID),
                          TYPE_VALUE_HEX_DEC,
                          4),
                         ('TXTPID',
                          self.getServiceInfoValue(iServiceInformation.sTXTPID),
                          TYPE_VALUE_HEX_DEC,
                          4),
                         ('TSID',
                          self.getServiceInfoValue(iServiceInformation.sTSID),
                          TYPE_VALUE_HEX_DEC,
                          4),
                         ('ONID',
                          self.getServiceInfoValue(iServiceInformation.sONID),
                          TYPE_VALUE_HEX_DEC,
                          4),
                         ('SID',
                          self.getServiceInfoValue(iServiceInformation.sSID),
                          TYPE_VALUE_HEX_DEC,
                          4))
                        carsep = ' :: '
                        carsep2 = '\n'
                        conta = 0
                        for j in xLabels:
                            texto = texto + j[0] + '-> ' + str(j[1]) + carsep
                            if conta > 2:
                                carsep = ' :: '
                            elif carsep == ' :: ':
                                carsep = '\n'
                            else:
                                carsep = ' :: '
                            conta = conta + 1

                        texto = texto + '\n'
                        frontendData = self.feinfo and self.feinfo.getAll(True)
                        xLabels = self.getFEData(frontendData)
                        tuners = '\n'
                        from Components.NimManager import nimmanager
                        nims = nimmanager.nimList()
                        texto = texto + '\n'
                        orbital = self.getOrbitalPosition(self.info)
                        satName = self.satNames.get(orbital, orbital)
                        conta = 0
                        carsep = ' :: '
                        carsep2 = '\n'
                        for j in xLabels:
                            if conta == 0:
                                numero = j[1]
                                for count in (0, 1, 2, 3):
                                    if count < len(nims):
                                        if numero == str(count):
                                            texto = texto + str(nims[count]) + '\n'
                                            if not satName == None and not satName == '':
                                                texto = texto + _('Service') + '-> ' + satName
                                                if str(orbital) not in satName:
                                                    texto = texto + ' (' + str(orbital) + ')'
                                                texto = texto + '\n'
                                            break

                            else:
                                texto = texto + _(j[0]) + '-> ' + _(str(j[1])) + carsep2
                            conta = conta + 1

                        texto = texto + '\n' + _('Press [BLUE] for floating window signal/quality/ber')
                except:
                    if texto == '':
                        texto = '\n' + _('Information not avaiable')

                self.actualizar = True
        elif self.inicio == 11:
            texto = ''
            fintexto = ''
            cams = ''
            if os.path.isfile('/etc/.BinCamd') and os.path.isfile('/etc/.CamdReStart.sh'):
                ebin = open('/etc/.BinCamd', 'r').read().split()
                caido = False
                for e in ebin:
                    if cams == '':
                        cams = _('State of CAM').replace(' CCAM', '').replace(' CAM', '') + ':'
                    cams = cams + '\n    \xe2\x80\xa2 ' + e
                    check = os.popen('pidof ' + e).read()
                    if check == '':
                        cams = cams + ' ***' + _('Not Running') + '*** ' + _('Press [YELLOW] to start')
                        caido = True
                    else:
                        cams = cams + ' [' + _('Running') + ']'

                self.actualizar = True
            if cams == '':
                cams = _('Emulation') + ' ***' + _('Not Running') + '*** ' + _('Press [YELLOW] to start')
            texto = texto + cams
            if fileExists('/tmp/ecm.info'):
                texto = texto + '\n\n' + _('ECM info') + ':\n' + cargaosinfo('cat /tmp/ecm.info').replace('    ', ' ').replace('   ', ' ').replace('  ', ' ') + '\n'
                self.actualizar = True
            if fileExists('/tmp/emm.info'):
                texto = texto + '\n' + _('EMM info') + ':\n ' + cargaosinfo('cat /tmp/emm.info')
                self.actualizar = True
            if fileExists('/tmp/pid.info'):
                texto = texto + '\n' + _('PID info') + ':\n ' + cargaosinfo('cat /tmp/pid.info')
                self.actualizar = True
            if fileExists('/tmp/cardinfo'):
                texto = texto + '\n' + _('Card info') + ':\n ' + cargaosinfo('cat /tmp/cardinfo')
                self.actualizar = True
            if texto == '':
                texto = '\n' + _('Information CCAM')
            if not self.tarea == '':
                self.actualizar = False
            self.tarea = ''
            texto = texto + fintexto
        elif self.inicio == 9:
            texto = ''
            modosaudio = ['PCM', 'RAW']
            modosdolby = ['Line Mode', 'RF Mode']
            valorvideo = str(config.av.videoport.value)
            if valorvideo == 'DVI':
                valorvideo = 'DVI-HDMI'
            texto = texto + _('Video Mode') + ': ' + valorvideo + '\n'
            if config.av.videoport.value in config.av.videomode:
                try:
                    texto = texto + _('Resolution') + ': ' + str(config.av.videomode[config.av.videoport.value].value) + '\n'
                except:
                    pass

                try:
                    texto = texto + _('Refresh Rate') + ': ' + str(config.av.videorate[config.av.videomode[config.av.videoport.value].value].value) + '\n'
                except:
                    pass

            try:
                texto = texto + _('Aspect ratio') + ': ' + str(config.av.aspect.value) + '\n'
            except:
                pass

            try:
                texto = texto + _('Deinterlace') + ': ' + str(config.av.deinterlace.value) + '\n\n'
            except:
                pass

            try:
                texto = texto + _('Dolby digital') + ': ' + modosaudio[int(config.av.dolbydigital.value)] + '\n'
            except:
                pass

            try:
                texto = texto + _('DTS') + ': ' + modosaudio[int(config.av.dts.value)] + '\n'
            except:
                pass

            try:
                texto = texto + _('AAC') + ': ' + modosaudio[int(config.av.aac.value)] + '\n'
            except:
                pass

            try:
                texto = texto + _('Other') + ': ' + modosaudio[int(config.av.otheraudio.value)] + '\n'
            except:
                pass

            try:
                texto = texto + _('Dolby digital mode') + ': ' + modosaudio[int(config.av.dolbydigitalmode.value)] + '\n\n'
            except:
                pass

            try:
                texto = texto + _('Audio Prebuffering   (ms)') + ': ' + str(config.av.aprebuff.value) + '\n'
                texto = texto + _('Video Prebuffering   (ms)') + ': ' + str(config.av.vprebuff.value) + '\n\n'
            except:
                pass

            nomskin = str(config.skin.primary_skin.value).replace('/skin.xml', '')
            texto = texto + '\n' + _('Skin') + ': ' + nomskin + '\n'
            if fileExists('/share/enigma2/' + nomskin + '/skin.info'):
                texto = texto + '-------------------------------------------------------------------------\n' + cargaosinfo('cat /share/enigma2/' + nomskin + '/skin.info').replace('spazeTeam', 'openSPA').replace('azboxhd.es', 'openspa.info') + ''
            texto = texto + '\n'
        elif self.inicio == 4:
            texto = _('Operating system') + ':\n' + cargaosinfo('cat /proc/version') + '\n'
            retinfo = getPliInfo()
            if retinfo == '':
                texto = texto + _('Version') + ' ' + _('of firmware') + ':\n' + str(about.getImageVersionString()) + '\n' + str(about.getEnigmaVersionString()) + '\n\n'
            else:
                texto = texto + retinfo + '\n'
            texto = texto + _('Date/Time') + ': ' + cargaosinfo('date') + '\n'
            texto = texto + _('Up time') + ':\n ' + cargaosinfo('uptime')
            self.actualizar = True
        elif self.inicio == 6:
            texto = ' '
            ret = self.accionlista()
            textot = '\n\n\n\n\n' + texto
            texto = textot
        elif self.inicio == 5:
            texto = _('Host Name') + '-> ' + cargaosinfo('hostname').replace('\n', '')
            array = cargaosinfo('ifconfig  eth0 | grep HWaddr').split('HWaddr')
            if len(array) > 1:
                texto = texto + ' :: ' + _('MAC adress') + '(LAN)-> ' + array[1]
            texto = texto + '\n'
            texto = texto + self.infored() + '\n'
            lascon = cargaosinfo('netstat -e | grep ESTABLISHED', True)
            arrcon = lascon.split('\n')
            cadcon = ''
            contacon = 1
            for iji in arrcon:
                if len(iji) > 4:
                    cadcon = cadcon + str(contacon) + ') ' + iji.replace('ESTABLISHED', '').replace('    ', ' ').replace('   ', ' ').replace('  ', ' ').replace(' 0', '').replace(' ', ' :: ') + '\n'
                    contacon = contacon + 1

            lascon = lascon
            texto = texto + _('Active connections') + ' (' + str(contacon - 1) + '):\n' + cadcon
            self.actualizar = False
        elif self.inicio == 8:
            if self.tarea == 'cras':
                ucras = self.devcras(True)
                if ucras == None:
                    texto = '\n\n\n' + _('No crashlogs found in path: /home/root/logs/')
                else:
                    texto = '\n' + _('Crashlog file') + ':\n       ' + ucras + '\n'
                    texto = texto + '\n------------------------------------------------------------------\n'
                    lineas = cargaosinfo("cat '" + ucras + "'")
                    textofin = '(exit code 5)'
                    if textofin not in lineas:
                        textofin = 'getResolvedKey config.plugins.crashlogautosubmit.sendAnonCrashlog'
                    lineas = devStrTm(lineas, 'Traceback (most recent call last):', textofin)
                    if len(lineas) < 10:
                        lineas = _('No traceback error found!')
                    else:
                        lineas = 'Traceback (most recent call last):' + lineas
                    texto = texto + lineas
                    texto = texto + '\n------------------------------------------------------------------\n'
                self.actualizar = False
                self.tarea = ''
            else:
                ret = self.accionlistaproc()
                texto = '   '
                self.actualizar = True
        elif self.inicio == 10:
            from Plugins.Extensions.spazeMenu.hardinfo import tipoModelo
            modelospz = tipoModelo(False)
            textoso = 'AZBox: www.openspa.info'
            if modelospz == 'vuplus':
                textoso = 'Vuplus: www.openspa.info'
            elif modelospz == 'golden':
                textoso = 'Golden Media/: www.openspa.info'
            elif modelospz == 'opticum':
                textoso = 'Opticum: www.openspa.info'
            elif modelospz == 'e3hd':
                textoso = 'E3HD: www.openspa.info'
            elif modelospz == 'mkdigital':
                textoso = 'MKDigital: www.openspa.info'
            elif modelospz == 'xtrend':
                textoso = 'Xtrend: www.openspa.info'
            elif modelospz == 'gigablue':
                textoso = 'GigaBlue: www.openspa.info'
            elif modelospz == 'vnet':
                textoso = 'VisionNET: www.openspa.info'
            elif modelospz == 'zgemma':
                textoso = 'Zgemma-Star: www.openspa.info'
            elif modelospz == 'gi':
                textoso = 'Galaxy Innovations: www.openspa.info'
            elif modelospz == 'wetek':
                textoso = 'Wetek: www.openspa.info'
            elif modelospz == 'formuler':
                textoso = 'Formuler: www.openspa.info'
            texto = '\n\n' + _('Advanced system information') + '\n' + _('by openSPA team')
            texto = texto + '\n\n' + _('News and support') + ' ' + textoso
            texto = texto + '\n\n'
            texto = texto + '\n' + _('Members openSPA Team:') + '\n'
            texto = texto + '---------------------------------------------------------------------------\n'
            texto = texto + _('Morser, Mpiero, Darkmantk, Nasky') + '\n'
            texto = texto + _('Pe.tardo, Sergiri, Evox, Oscar_fl ') + '\n'
            texto = texto + _('Yersi, Abdelsat, HSA2000') + '\n'
            texto = texto + '\n\n' + _('Greetings:') + '\n'
            texto = texto + '---------------------------------------------------------------------------\n'
            texto = texto + _('Fundi, Edu1971, Mecha, Jpbravo, Rusoalicia, Milytres, lilo74, Macmanolo and all Betatesters.') + '\n'
            texto = texto + '\n\n'
            siact = ''
            if not lenguaje == 'es':
                lenguaje = 'en'
            from Plugins.Extensions.spazeMenu.spzPlugins.descargasSPZ.plugin import devupdates, guardatxt
            intentos = 3
            html = None
            for iji in range(intentos):
                arrhtml = devupdates(False)
                html = arrhtml[0]
                if not html == None:
                    if arrhtml[1]:
                        actualizarTXT = arrhtml[1]
                        if not actualizarTXT == None:
                            guardatxt(actualizarTXT)
                    break

            if not html == None:
                texto = texto + _('Last Updates') + ':\n' + html
        self['textoinfo'].setText(texto)
        if self.actualizar:
            self.TimerActualizar.start(15000, True)
        if self.upagina:
            self['textoinfo'].lastPage()
        if not self.iniciadoS:
            self.actualizaScrolls()
            self.iniciadoS = True

    def actualizaScrolls(self):
        openspaSB(objectoself=self, nombrelista='barrapix', barra='barrapix', altoitem=25, imagen=True)

    def key_re(self):
        self.TimerActualizar.stop()
        self.TimerTemp.stop()
        self.TimerCarga.stop()
        if self.tarea == 'dmesg':
            self.tarea = ''
        idx = self['lista'].getSelectionIndex()
        if self.indice == idx:
            self.buildList()
        else:
            self.cargar()

    def key_ok(self):
        self.TimerActualizar.stop()
        self.TimerCarga.stop()
        self.TimerTemp.stop()
        if not self.bloquear:
            self['titulo'].setText(' ')
            self['textoinfo'].setText('\n' + _('Wait...'))
            self['listainfo'].hide()
            self['listaproc'].hide()
            self.bloquear = True
            lalista = self['lista'].list
            idx = self['lista'].getSelectionIndex()
            numero = listamenu[idx][2]
            self.inicio = numero
            self.inicializa()

    def key_info(self):
        info1 = _('Advanced Information Panel') + '\n'
        info2 = _('by OpenSPA (openspa.info), 2014-2015')
        cmens = info1 + '\n' + info2
        dei = self.session.open(MessageBox, cmens, MessageBox.TYPE_INFO)
        dei.setTitle(_('About'))

    def key_left2(self):
        if self['listainfo'].getSelectionIndex() == 0:
            self['listainfo'].moveToIndex(len(self['listainfo'].list) - 1)
        else:
            self['listainfo'].up()

    def key_right2(self):
        if self['listainfo'].getSelectionIndex() == len(self['listainfo'].list) - 1:
            self['listainfo'].moveToIndex(0)
        else:
            self['listainfo'].down()

    def key_left(self):
        if self.inicio == 6:
            self.key_left2()
        else:
            self['textoinfo'].pageUp()
            self['listainfo'].selectionEnabled(1)
            self['listainfo'].pageUp()
            self['listainfo'].selectionEnabled(0)
            self['listaproc'].selectionEnabled(1)
            self['listaproc'].pageUp()
            self['listaproc'].selectionEnabled(0)
        self.upagina = False

    def key_right(self):
        if self.inicio == 6:
            self.key_right2()
        else:
            self['textoinfo'].pageDown()
            self['listainfo'].selectionEnabled(1)
            self['listainfo'].pageDown()
            self['listainfo'].selectionEnabled(0)
            self['listaproc'].selectionEnabled(1)
            self['listaproc'].pageDown()
            self['listaproc'].selectionEnabled(0)
        self.upagina = True

    def key_up(self):
        self.TimerActualizar.stop()
        self.TimerCarga.stop()
        self.TimerTemp.stop()
        if self['lista'].getSelectionIndex() == 0:
            self['lista'].moveToIndex(len(self['lista'].list) - 1)
        else:
            self['lista'].up()
        self.upagina = False
        self.TimerTemp.start(2000, True)

    def key_down(self):
        self.TimerTemp.stop()
        self.TimerActualizar.stop()
        self.TimerCarga.stop()
        if self['lista'].getSelectionIndex() == len(self['lista'].list) - 1:
            self['lista'].moveToIndex(0)
        else:
            self['lista'].down()
        self.upagina = False
        self.TimerTemp.start(2000, True)

    def exit(self):
        self.TimerActualizar.stop()
        self.TimerCarga.stop()
        self.TimerTemp.stop()
        self.close(0)


class InfoAz(Screen):
    if esHD():
        skin = '\n\t\t<screen position="center,center" size="1575,903" title="%s">\n\t\t\t<widget name="textoinfo" position="432,56" size="1118,783" valign="top" halign="left" text="%s" font="Regular; 18" zPosition="1" />\n\t\t</screen>' % (_('Information') + ' ' + 'openSPA', _('Wait...'))
    else:
        skin = '\n\t\t<screen position="center,center" size="1050,602" title="%s">\n\t\t\t<widget name="textoinfo" position="288,37" size="745,522" valign="top" halign="left" text="%s" font="Regular; 18" zPosition="1" />\n\t\t</screen>' % (_('Information') + ' ' + 'openSPA', _('Wait...'))

    def __init__(self, session, infoservice = None, **kwargs):
        self.session = session
        self['textoinfo'] = Label(_('Wait...'))
        Screen.__init__(self, session)
        self.inicio = 2
        self.infoservice = infoservice
        self.iniciado = False
        self['setupActions'] = ActionMap(['WizardActions'], {'back': self.close}, -2)
        self.onShow.append(self.cargapantalla)

    def cargapantalla(self):
        pinicial = self.inicio
        if grabando(self) and not self.infoservice:
            pinicial = 1
        if not self.iniciado:
            self.iniciado = True
            self.session.openWithCallback(self.vueltapantalla, infoAzTexto, inicio=pinicial, servicio=self.infoservice)

    def vueltapantalla(self, respuesta):
        if respuesta == 0:
            self.close()
        elif respuesta == 1:
            self.session.openWithCallback(self.vueltapantalla, infoAzTexto, inicio=1)
        elif respuesta == 6:
            self.session.openWithCallback(self.vueltapantalla, infoAzTexto, inicio=6)
        elif respuesta == 8:
            self.session.openWithCallback(self.vueltapantalla, infoAzTexto, inicio=8)
        elif respuesta == 10:
            self.session.openWithCallback(self.vueltapantalla, infoAzTexto, inicio=10)
        elif respuesta == 2:
            self.session.openWithCallback(self.vueltapantalla, infoAzTexto, inicio=2)
        elif respuesta == 3:
            self.session.openWithCallback(self.vueltapantalla, infoAzTexto, inicio=3)
        elif respuesta == 5:
            self.session.openWithCallback(self.vueltapantalla, infoAzTexto, inicio=5)
        elif respuesta == 9:
            self.session.openWithCallback(self.vueltapantalla, infoAzTexto, inicio=9)
        elif respuesta == 4:
            self.session.openWithCallback(self.vueltapantalla, infoAzTexto, inicio=4)
        elif respuesta == 7:
            self.session.openWithCallback(self.vueltapantalla, infoAzTexto, inicio=7)
        else:
            self.close()

    def exit(self):
        self.close()


def start_from_mainmenu(menuid, **kwargs):
    if menuid == 'information':
        return [(_('Advanced Information Panel'),
          iniciainfo,
          'InfoAz',
          1)]
    return []


def iniciainfo(session, **kwargs):
    if not fileExists('/usr/bin/chkvs'):
        Notifications.AddPopup(text=_('Not OpenSPA image found!\nMore info in openspa.info'), type=MessageBox.TYPE_ERROR, timeout=10, id='InfoAz')
    else:
        session.open(InfoAz)


def Plugins(**kwargs):
    name = _('Advanced Information Panel')
    descr = _('oPenSPA Advanced Information Panel')
    list = []
    if True:
        list.append(PluginDescriptor(name=_('Advanced Information Panel'), description=descr, where=PluginDescriptor.WHERE_MENU, fnc=start_from_mainmenu))
    return list
