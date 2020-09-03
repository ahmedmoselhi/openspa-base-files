from Components.Label import Label
from Components.MenuList import MenuList
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaTest, MultiContentEntryPixmapAlphaBlend
from enigma import eListboxPythonMultiContent, gFont, RT_HALIGN_RIGHT, BT_SCALE, BT_KEEP_ASPECT_RATIO, eEnv, getDesktop
from enigma import eTimer
from Components.Pixmap import Pixmap
from enigma import ePicLoad
from Screens.HelpMenu import HelpableScreen, HelpMenu
from Components.AVSwitch import AVSwitch
from Tools.LoadPixmap import LoadPixmap
from Plugins.Extensions.spazeMenu.sbar import openspaSB
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.Standby import TryQuitMainloop
from Components.ActionMap import ActionMap, HelpableActionMap
from Components.ScrollLabel import ScrollLabel
from Components.PluginComponent import plugins
from Components.config import config, ConfigYesNo
from Tools import Notifications
import os
import time
import datetime
from Tools.Directories import fileExists, resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE, SCOPE_SKIN
from Plugins.Extensions.spazeMenu.plugin import esHD, fhd
from Components.Language import language
import urllib2
from os import environ
import gettext
config.misc.spazeupdates = ConfigYesNo(default=True)
URLXML = 'http://team.openspa.info/DescargasFirm/OpenSpa/'
lang = language.getLanguage()
environ['LANGUAGE'] = lang[:2]
gettext.bindtextdomain('enigma2', resolveFilename(SCOPE_LANGUAGE))
gettext.textdomain('enigma2')
gettext.bindtextdomain('descargasSPZ', '%s%s' % (resolveFilename(SCOPE_PLUGINS), 'Extensions/spazeMenu/spzPlugins/descargasSPZ/locale/'))
lenguaje = str(lang[:2])
glenguaje = lenguaje
if not lenguaje == 'es':
    lenguaje = 'en'
TimerGoUpdates = None
TimerMirar = None
actualizarTXT = None
listaini = None
listacarpetas = None
anteriorlistado = None
valor_ordenar = ''
updates_event = []

def func_updates(sihay):
    for x in updates_event:
        x(sihay)


def _(txt):
    t = gettext.dgettext('descargasSPZ', txt)
    if t == txt:
        t = gettext.gettext(txt)
    return t


import re
re_digits_nondigits = re.compile('\\d+|\\D+')
from enigma import eConsoleAppContainer

def _commafy(s):
    r = []
    for i, c in enumerate(reversed(s)):
        if i and not i % 3:
            r.insert(0, '#')
        r.insert(0, c)

    return ''.join(r)


def FormatWithCommas(value, sepmil = '.', sepdec = ',', ndecimales = 0, cmoneda = ''):
    try:
        format = '%.' + str(ndecimales) + 'f' + cmoneda
        if value == None:
            return ''
        if str(value) == '':
            return ''
        cvalue = str(value)
        fvalue = float(value)
        parts = re_digits_nondigits.findall(format % (fvalue,))
        for i in xrange(len(parts)):
            s = parts[i]
            if s.isdigit():
                parts[i] = _commafy(s)
                break

        return ''.join(parts).replace('.', sepdec).replace('#', sepmil)
    except:
        return ''


def execurlext(nscript, parametros):
    global URLXML
    cret = ''
    try:
        laurl = URLXML + nscript
        cquery = ''
        if not parametros == '' and '?' not in parametros:
            cquery = '?'
        cquery = cquery + parametros
        laurl = laurl + cquery
        response = urllib2.urlopen(laurl, timeout=10)
        ippub = response.read()
        if '[*ok*]' in ippub:
            cret = ippub.replace('\n[*ok*]', '')
        else:
            cret = '[*error*]3'
    except:
        cret = '[*error*]4'

    if '[*error*]' in cret:
        cret = None
    try:
        cret = cret.decode('windows-1252').encode('utf-8')
    except:
        pass

    return cret


def execurl(elplugin = None, lacarpeta = None, voto = None, descarga = None):
    cret = ''
    try:
        ertiempo = str(int(time.mktime(time.localtime())))
        laurl = URLXML + 'datosg.php?stamp=' + ertiempo
        cquery = ''
        csepa = '&'
        if not elplugin == None:
            cquery = cquery + csepa + 'plugin=' + elplugin
            csepa = '&'
        if not lacarpeta == None:
            cquery = cquery + csepa + 'carpeta=' + lacarpeta
            csepa = '&'
        if not voto == None:
            cquery = cquery + csepa + 'voto=' + str(voto)
            csepa = '&'
        if not descarga == None:
            cquery = cquery + csepa + 'descarga=' + str(descarga)
            csepa = '&'
        laurl = laurl + cquery
        response = urllib2.urlopen(laurl, timeout=10)
        ippub = response.read()
        if '[*ok*]' in ippub:
            cret = ippub.replace('\n[*ok*]', '')
        else:
            cret = '[*error*]3'
    except:
        cret = '[*error*]4'

    if '[*error*]' in cret:
        cret = None
    return cret


def nunmes(cmes):
    cmes = str(cmes).lower()
    meses = {'jan': 1,
     'feb': 2,
     'mar': 3,
     'apr': 4,
     'may': 5,
     'jun': 6,
     'jul': 7,
     'aug': 8,
     'sep': 9,
     'oct': 10,
     'nov': 11,
     'dec': 12}
    if cmes in meses:
        ret = meses[cmes]
        cret = str(ret)
        if len(cret) == 1:
            cret = '0' + cret
    else:
        return '01'
    return cret


def chequeamaks(urlx, usuariox = 'spaze', pwdx = 'AzboxHD2011'):
    try:
        carray = cargaosinfo('ifconfig eth0 | grep HWaddr')
        if 'HWaddr' not in carray:
            carray = cargaosinfo('ifconfig | grep HWaddr')
        array = carray.split('HWaddr')
        cmac = 'x0x'
        if len(array) > 1:
            cmac = array[1].replace(' ', '').replace('\n', '')
        cmac = '' + str(cmac) + ''
    except:
        return

    if len(cmac) <= 4:
        return
    try:
        ertiempo = str(int(time.mktime(time.localtime())))
        laurl = URLXML + 'macs.php?stamp=' + ertiempo + '&usuario=xaz2012x&mac=' + cmac
        response = urllib2.urlopen(laurl, timeout=10)
        ippub = response.read()
        if ippub == None:
            return
        if '[*error*]' in ippub:
            return
        if '[*ok*]' in ippub:
            if 'vip' + cmac + '*' in ippub:
                os.system('date >/usr/bin/vbinds')
                os.system('date >/usr/bin/chkds')
            elif cmac + '*' in ippub:
                os.system('date >/usr/bin/chkds')
    except:
        pass


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


def quitaextension(deque):
    extension = str(deque.split('.')[-1])
    if len(extension) > 0:
        extension = '.' + extension
        ret = deque.replace(extension, '')
    else:
        ret = deque
    return ret


def findPicon():
    serviceName = '*'
    path = str(config.misc.picon_path.value)
    pngname = path + serviceName + '.png'
    if fileExists(pngname):
        return path
    searchPaths = [eEnv.resolve('${datadir}/enigma2/picon/'), '/media/cf/picon/', '/media/usb/picon/']
    path = path + 'picon/'
    if path not in searchPaths:
        searchPaths.append(path)
    for path in searchPaths:
        pngname = path + serviceName + '.png'
        if fileExists(pngname):
            return path

    return ''


def wlog(texto):
    os.system('date >> /etc/spzbk.log')
    os.system("echo 'spzDescargas: " + texto + "' >> /etc/spzbk.log")
    os.system("echo '************************************************' >> /etc/spzbk.log")


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


def devvalores(valor):
    listavotos = valor.split('_')
    try:
        nvotos = int(listavotos[0])
        valorvotos = int(listavotos[1])
    except:
        nvotos = 0
        valorvotos = 0

    return [nvotos, valorvotos]


def devvotosarchivos(pcarpeta, archivo):
    ret = [0, 0, 0]
    valorurl = execurl(elplugin=archivo, lacarpeta=pcarpeta)
    if not valorurl == None and not valorurl == '[*ok*]':
        try:
            lvotos = devvalores(devStrTm(valorurl, '*.nvotos*', '*'))
            descargas = devStrTm(valorurl, '*.ndescargas*', '*')
            ret = [lvotos[0], lvotos[1], int(descargas)]
        except:
            pass

    return ret


def votaftp(pcarpeta, nombre, valorvoto):
    valorurl = execurl(elplugin=quitaextension(nombre), lacarpeta=None, voto=valorvoto)
    return valorurl


def anadedescarga(pcarpeta, nombre):
    valorurl = execurl(elplugin=quitaextension(nombre), lacarpeta=None, descarga=1)
    return valorurl


def formateafecha(lafecha = None, sepa = '/', corta = True, hora = False):
    if not lafecha == None:
        t2 = lafecha
    else:
        return
    try:
        t3 = time.localtime()
        cdia = str(time.strftime('%d', t2))
        cmes = str(time.strftime('%B', t2))
        cano = str(time.strftime('%Y', t2))
        if int(cano) < 2009:
            return ' '
        xhoy = str(time.strftime('%d', t3)) + str(time.strftime('%B', t3)) + str(time.strftime('%Y', t3))
        diayer = str(int(time.strftime('%d', t3)) - 1)
        if len(diayer) == 1:
            diayer = '0' + diayer
        xay = str(diayer + str(time.strftime('%B', t3)) + str(time.strftime('%Y', t3)))
        eshoy = False
        if cdia + cmes + cano == xhoy:
            csemana = _('Today') + ' ' + _(str(time.strftime('%A', t2)))
            eshoy = True
        elif cdia + cmes + cano == xay:
            csemana = _('Yesterday') + ' ' + _(str(time.strftime('%A', t2)))
            eshoy = True
        else:
            csemana = _(str(time.strftime('%A', t2)))
        chora = ''
        if hora:
            chora = ' ' + str(time.strftime('%H:%M', t2))
        if corta:
            cmes = _(cmes)
            if not eshoy:
                csemana = csemana + ', '
            else:
                csemana = csemana + ', '
            if str(time.strftime('%Y', t3)) == cano:
                cano = ''
            else:
                cano = sepa + cano
                csemana = ''
            return csemana + cdia + sepa + cmes + cano + chora
        return _(csemana) + ', ' + cdia + sepa + _(cmes) + sepa + cano + chora
    except:
        return


def devupdates(simple = True):
    global lenguaje
    codigomodelo = devcodmodelo()[0]
    siprivado = fileExists('/usr/bin/vbinds')
    lospar = 'usuario=xaz2012x'
    if siprivado:
        lospar = lospar + '&privado=1'
    if not lenguaje == 'es':
        lospar = lospar + '&idioma=en'
    if simple:
        lospar = lospar + '&simple=1'
        if fileExists('/etc/updates.txt'):
            udes = ''
            try:
                udes = open('/etc/updates.txt', 'r').read()
            except:
                pass

            if len(udes) > 6:
                lospar = lospar + '&fecha=' + udes.replace('\n', '')
    lospar = lospar + '&modelo=' + codigomodelo
    ertiempo = str(int(time.mktime(time.localtime())))
    lospar = lospar + '&stamp=' + ertiempo
    ret = execurlext('updates.php', lospar)
    if ret == None:
        return [None, None]
    else:
        ret2 = devStrTm(ret, '.lastupdate[*', '*]')
        ret1 = ret.replace('.lastupdate[*' + ret2 + '*]', '')
        if ret2 == 'x' or ret2 == '':
            ret2 = None
        return [ret1, ret2]


def devcodmodelo():
    codmodelo = '0'
    nombre = 'Generic receptor'
    try:
        codmodelo = open('/usr/bin/OpenSPA.info', 'r').read()
        nombre = devStrTm(codmodelo, ']', '\n')
        if nombre == '':
            nombre = 'NA'
        codmodelo = devStrTm(codmodelo, '[', ']')
        if codmodelo == '':
            codmodelo = 'Generic receptor'
    except:
        pass

    return [codmodelo, nombre]


def devDato(cadena, cual, cual2 = None):
    sepa = ':|:'
    if cual2 == None:
        cual2 = sepa
    else:
        cual2 = cual2 + sepa
    return devStrTm(cadena, '.' + cual + sepa, cual2)


def devUrlContenido(pcarpeta = None, nombretit = '', privado = False, siforzar = False):
    global listacarpetas
    global valor_ordenar
    global listaini
    global anteriorlistado
    lcarpetas = []
    if pcarpeta == None:
        pcarpeta = ''
    vordenar = valor_ordenar
    if pcarpeta == '1' or pcarpeta == '-1':
        pcarpeta = ''
    if pcarpeta == '' and vordenar == 'nombre':
        vordenar = ''
    if not siforzar:
        if pcarpeta == '' and not listaini == None:
            return listaini
    else:
        listaini = None
    if pcarpeta == '-2' and not listacarpetas == None:
        return listacarpetas
    if pcarpeta == '0':
        if len(nombretit.split('/*/')) == 1:
            if not listacarpetas == None:
                return listacarpetas
        else:
            return anteriorlistado
    if pcarpeta == '-3':
        lcarpetas.append(['<' + _('Home') + '>',
         'd',
         '-1',
         None,
         None,
         None,
         None,
         None,
         None])
        lcarpetas.append([_('openPLI Downloads (Plugins/Extensions/Skins)').replace('openPLI', 'Enigma2'),
         'd',
         'opdwn',
         '',
         None,
         None,
         None,
         None,
         None])
        lcarpetas.append([_('openPLI Manage Plugins/Extensions').replace('openPLI', 'Enigma2'),
         'd',
         'opman',
         '',
         None,
         None,
         None,
         None,
         None])
        return [len(lcarpetas) - 1, 0, lcarpetas]
    codigomodelo = devcodmodelo()[0]
    siprivado = privado
    lospar = 'usuario=xaz2012x'
    if siprivado:
        lospar = lospar + '&privado=1'
    if _('Search of') + ' [' in nombretit:
        lospar = lospar + '&buscar=' + pcarpeta
    elif not pcarpeta == '':
        lospar = lospar + '&categoria=' + pcarpeta
    if not lenguaje == 'es':
        lospar = lospar + '&idioma=en'
    if not vordenar == '':
        lospar = lospar + '&ordenar=' + vordenar
    lospar = lospar + '&modelo=' + codigomodelo
    ertiempo = str(int(time.mktime(time.localtime())))
    lospar = lospar + '&stamp=' + ertiempo
    ret = execurlext('datosg.php', lospar)
    if ret == None:
        return
    larchivos = []
    strcat = devDato(ret, 'categorias', ':|:.categoriasfin')
    arrcat = strcat.split('\n')
    apadre = '1'
    idpadre = '1'
    numpadre = 0
    for ele in arrcat:
        ele = ele.replace('\n', '')
        if len(ele) > 5:
            id = devDato(ele, 'id')
            nombre = devDato(ele, 'nombre')
            try:
                numero = devDato(ele, 'numero')
            except:
                numero = '0'

            lcarpetas.append([nombre,
             'd',
             id,
             numero,
             None,
             None,
             None,
             None,
             None])

    strcat = devDato(ret, 'categoriasfin', 'categoriasfin2')
    arrcat = strcat.split('\n')
    for ele in arrcat:
        ele = ele.replace('\n', '')
        if len(ele) > 5:
            id = devDato(ele, 'id')
            cvotos = devDato(ele, 'nvotos')
            nombre = devDato(ele, 'nombre')
            if pcarpeta == '' or _('Search of') + ' [' in nombretit:
                nombre = nombre + ' | ' + devDato(ele, 'carpeta')
            archivo = devDato(ele, 'archivo')
            fecha = devDato(ele, 'fecha')
            ndescargas = devDato(ele, 'ndescargas')
            try:
                tamano = int(devDato(ele, 'tamano'))
            except:
                tamano = 0

            lacat = devDato(ele, 'idcat')
            lvotos = devvalores(cvotos)
            nvotos = lvotos[0]
            valorvotos = lvotos[1]
            larchivos.append([archivo,
             'a' + lacat,
             id,
             nombre,
             tamano,
             fecha,
             nvotos,
             valorvotos,
             ndescargas])

    if pcarpeta == '':
        lcarpetas.append(['<' + _('Home') + '>',
         'd',
         '-1',
         None,
         None,
         None,
         None,
         None,
         None])
    lcarpetas.sort(key=lambda x: _(str(x[0])).upper())
    listafin = []
    if pcarpeta == '':
        listafin.append(['<' + _('Categories') + '>',
         'd',
         '-2',
         None,
         None,
         None,
         None,
         None,
         None])
        listafin.append(['<' + _('openPLI downloads').replace('openPLI', 'Enigma2') + '>',
         'd',
         '-3',
         None,
         None,
         None,
         None,
         None,
         None])
    elif not pcarpeta == '':
        listafin.append(['<' + _('Home') + '>',
         'd',
         '-1',
         None,
         None,
         None,
         None,
         None,
         None])
        if '/*/' in nombretit:
            listafin.append(['<' + _('Back') + '>',
             'd',
             '0',
             None,
             None,
             None,
             None,
             None,
             None])
        for ele in lcarpetas:
            listafin.append(ele)

    for ele in larchivos:
        listafin.append(ele)

    if listaini == None and pcarpeta == '':
        listaini = [0, 25, listafin]
        listacarpetas = [len(lcarpetas) - 1, 0, lcarpetas]
    return [len(lcarpetas), len(larchivos), listafin]


carpetaimg = '/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/descargasSPZ/img/'
nommodelo = 'NA'

def formateatextoEx(extexto):
    return _(quitaextension(extexto))


def formateatexto(eltexto):
    eltexto = eltexto.replace('-donsat-', '')
    return eltexto


class IniciaSelListArchivo(MenuList):

    def __init__(self, list, enableWrapAround = True):
        MenuList.__init__(self, list, enableWrapAround, eListboxPythonMultiContent)
        self.l.setItemHeight(fhd(50))
        self.l.setFont(0, gFont('Regular', 19))
        self.l.setFont(1, gFont('Regular', 17))


def IniciaSelListEntryArchivo(texto, imagen = 'Otros', instalado = False, tamano = None, fecha = None, votossi = None, votosno = None):
    global carpetaimg
    esds = False
    tecla = '' + texto + ''
    res = [tecla]
    posyi = 10
    posxi = 27
    tami = 32
    numero = None
    png = '' + carpetaimg + '' + imagen + '-fs8.png'
    arrposx = 0
    if imagen[0] == 'd':
        if not fileExists(png):
            imagen = 'd'
        posyi = 0
        posxi = 6
        tami = 48
        if not tamano == None:
            if tamano != '0' and tamano != '':
                numero = str(tamano) + ' ' + _('File(s)')
        tamano = None
    else:
        arrposx = 13
        if not fileExists(png):
            imagen = 'a'
    if '-donsat-' in texto:
        esds = True
    if len(texto) > 69:
        anac = ''
        maxc = 69
        try:
            temp = texto.split(' | ')
            if len(temp) > 1:
                texto = temp[0]
                anac = ' | ' + temp[1]
                maxc = maxc - len(anac)
        except:
            pass

        texto = texto[:maxc] + '...' + anac
    res.append(MultiContentEntryText(pos=(fhd(61 - arrposx), fhd(12, 1.8)), size=(fhd(655), fhd(25)), font=0, text=formateatexto(texto)))
    if not numero == None:
        valortexto = numero
        if valortexto:
            res.append(MultiContentEntryText(pos=(fhd(300), fhd(12)), size=(fhd(630), fhd(25)), font=1, flags=RT_HALIGN_RIGHT, text=valortexto))
    if not fecha == None:
        valortexto = fecha
        try:
            temptiempo = fecha
            c = time.strptime(fecha, '%d-%m-%Y')
            valortexto = formateafecha(c)
        except:
            pass

        if valortexto:
            res.append(MultiContentEntryText(pos=(fhd(300), 1), size=(fhd(630), fhd(23)), font=1, flags=RT_HALIGN_RIGHT, text=valortexto, color=10066329))
    png = '' + carpetaimg + '' + imagen + '-fs8.png'
    if fileExists(png):
        fpng = LoadPixmap(png)
        res.append(MultiContentEntryPixmapAlphaBlend(pos=(fhd(posxi - arrposx), fhd(posyi)), size=(fhd(tami), fhd(tami)), png=fpng, flags=BT_SCALE | BT_KEEP_ASPECT_RATIO))
    if instalado:
        png = '' + carpetaimg + 'infochfs8.png'
        fpng = LoadPixmap(png)
        res.append(MultiContentEntryPixmapAlphaBlend(pos=(fhd(5), fhd(5)), size=(fhd(20), fhd(20)), png=fpng, flags=BT_SCALE | BT_KEEP_ASPECT_RATIO))
    posini = 750
    posy = 26
    if not votossi == None:
        png = '' + carpetaimg + 'vgreen-fs8.png'
        fpng = LoadPixmap(png)
        res.append(MultiContentEntryPixmapAlphaBlend(pos=(fhd(posini), fhd(posy)), size=(fhd(23), fhd(22)), png=fpng, flags=BT_SCALE | BT_KEEP_ASPECT_RATIO))
        valornumero = '0'
        totalvotos = int(votossi) + int(votosno)
        maxanchobarra = 176
        abarra = 0
        if votossi > 0:
            anchobarra = maxanchobarra * int(votossi) / totalvotos
            if int(anchobarra) == 0 and votossi > 0:
                anchobarra = 2
            png = '' + carpetaimg + 'lver-fs8.png'
            fpng = LoadPixmap(png)
            res.append(MultiContentEntryPixmapAlphaBlend(pos=(fhd(posini + 2), fhd(posy)), size=(fhd(anchobarra), fhd(2)), png=fpng, flags=BT_SCALE | BT_KEEP_ASPECT_RATIO))
            abarra = anchobarra
            valornumero = str(votossi)
        res.append(MultiContentEntryText(pos=(fhd(posini + 24), fhd(posy)), size=(fhd(100), fhd(25)), font=1, text=valornumero))
        png = '' + carpetaimg + 'vred-fs8.png'
        fpng = LoadPixmap(png)
        res.append(MultiContentEntryPixmapAlphaBlend(pos=(fhd(907), fhd(posy)), size=(fhd(23), fhd(22)), png=fpng, flags=BT_SCALE | BT_KEEP_ASPECT_RATIO))
        valornumero = '0'
        if votosno > 0:
            anchobarra = maxanchobarra * int(votosno) / totalvotos
            if int(anchobarra) == 0 and votosno > 0:
                anchobarra = 2
            png = '' + carpetaimg + 'lroj-fs8.png'
            fpng = LoadPixmap(png)
            res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND,
             fhd(posini + 2 + abarra),
             fhd(posy),
             fhd(anchobarra),
             fhd(2),
             fpng))
            valornumero = str(votosno)
        res.append(MultiContentEntryText(pos=(fhd(807), fhd(posy)), size=(fhd(100), fhd(25)), font=1, flags=RT_HALIGN_RIGHT, text=valornumero))
    if esds:
        png = '' + carpetaimg + 'bdsp-fs8.png'
        fpng = LoadPixmap(png)
        res.append(MultiContentEntryPixmapAlphaBlend(pos=(fhd(posini - 36), fhd(posy - 2)), size=(fhd(32), fhd(24)), png=fpng, flags=BT_SCALE | BT_KEEP_ASPECT_RATIO))
    return res


from enigma import eSize

class InfoArchivo(Screen):
    if esHD():
        skin = '\n\t\t<screen name="InfoArchivo" position="center,70" size="1755,915" title="%s">\n\t\t\t<widget name="respuesta" position="0,58" size="805,813" zPosition="12" text=" " font="Regular; 19" transparent="1" />\n\t\t\t<ePixmap name="new ePixmap" position="1,1" size="60,45" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/descargasSPZ/img/info-fs8.png" alphatest="blend" transparent="1" zPosition="10" />\n\t\t\t<widget name="modo" position="0,0" size="1800,48" backgroundColor="#ffffff" foregroundColor="#000000" text=" " font="Regular; 22" />\n\t\t\t<widget name="textodescarga" position="825,187" size="930,300" zPosition="13" halign="center" valign="center" transparent="0" font="Regular; 22" />\n\t\t\t<widget name="key_red" position="339,882" size="300,33" transparent="1" font="Regular; 16" />\n\t\t\t<widget name="key_green" position="54,882" size="300,33" transparent="1" font="Regular; 16" />\n\t\t\t<widget name="key_yellow" position="661,882" size="387,33" transparent="1" font="Regular; 17" />\n\t\t\t<widget name="imagen" position="825,187" size="930,522" zPosition="14" transparent="1" alphatest="blend" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/descargasSPZ/img/hdlogospafs8.png" />\n\t\t\t<widget name="key_mode" position="12,12" size="1027,33" transparent="1" text=" " font="Regular; 15" halign="left" />\n\t\t\t<widget name="barrapix_arr" position="0,58" zPosition="19" size="805,813" alphatest="blend" transparent="1" />\n\t\t\t<widget name="barrapix_abj" position="0,0" zPosition="19" size="30,30" alphatest="blend" transparent="1" />\t\n\t\t\t<eLabel name="linea1" position="814,51" size="1,826" zPosition="50" backgroundColor="#03444444" />\n\t\t\t<eLabel name="linea2" position="0,51" size="1800,1" zPosition="50" backgroundColor="#03444444" />\n\t\t\t<eLabel name="linea3" position="0,876" size="1800,1" zPosition="50" backgroundColor="#03444444" />\n\t\t\t<ePixmap name="new ePixmap" position="0,880" size="52,37" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/greenHD.png" alphatest="blend" />\n\t\t\t<ePixmap name="new ePixmap" position="285,880" size="52,37" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/redHD.png" alphatest="blend" />\n\t\t\t<ePixmap name="new ePixmap" position="607,880" size="52,37" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/yellowHD.png" alphatest="blend" />\n\t\t\t<widget name="key_ok" position="1564,882" size="387,33" transparent="1" font="Regular; 16" />\n\t\t\t<ePixmap name="new ePixmap" position="1455,880" size="52,37" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/exitHD.png" alphatest="blend" />\n\t\t\t<ePixmap name="new ePixmap" position="1507,880" size="52,37" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/img/okHD.png" alphatest="blend" />\n\t\t\t<ePixmap name="new ePixmap" position="825,66" size="34,33" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/descargasSPZ/img/hdvgreen-fs8.png" alphatest="blend" />\n\t\t\t<ePixmap name="new ePixmap" position="825,120" size="34,33" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/descargasSPZ/img/hdvred-fs8.png" alphatest="blend" />\n\t\t\t<widget name="key_pos" position="862,60" size="636,45" transparent="1" font="Regular; 20" foregroundColor="#0000ff00" shadowColor="#000000" shadowOffset="-2,-2" valign="center" />\n\t\t\t<widget name="key_neg" position="862,112" size="636,45" transparent="1" font="Regular; 20" foregroundColor="#00ff0000" shadowColor="#000000" shadowOffset="-2,-2" valign="center" />\n\t\t\t<eLabel name="linea4" position="814,168" size="930,1" zPosition="50" backgroundColor="#03444444" />\n\t\t\t<widget name="key_totg" position="1135,87" size="588,45" transparent="1" font="Regular; 20" foregroundColor="#0000ff00" shadowColor="#000000" shadowOffset="-2,-2" valign="center" halign="right" />\n\t\t\t<widget name="key_totr" position="1135,87" size="588,45" transparent="1" font="Regular; 20" foregroundColor="#00ff0000" shadowColor="#000000" shadowOffset="-2,-2" valign="center" halign="right" />\n\t\t\t<widget name="linver" position="1273,132" size="450,7" transparent="0" backgroundColor="#003dce3d" zPosition="51"/>\n\t\t\t<widget name="linroj" position="1273,132" size="450,7" transparent="0" backgroundColor="#00ff5147" zPosition="50"/>\n\t\t</screen>' % _('openSPA Downloads')
    else:
        skin = '\n\t\t<screen name="InfoArchivo" position="center,70" size="1170,610" title="%s">\n\t\t\t<widget name="respuesta" position="0,39" size="537,542" zPosition="12" text=" " font="Regular; 19" transparent="1" />\n\t\t\t<ePixmap name="new ePixmap" position="1,1" size="40,30" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/descargasSPZ/img/info-fs8.png" alphatest="blend" transparent="1" zPosition="10" />\n\t\t\t<widget name="modo" position="0,0" size="1200,32" backgroundColor="#ffffff" foregroundColor="#000000" text=" " font="Regular; 22" />\n\t\t\t<widget name="textodescarga" position="550,125" size="620,200" zPosition="13" halign="center" valign="center" transparent="0" font="Regular; 22" />\n\t\t\t<widget name="key_red" position="226,588" size="200,22" transparent="1" font="Regular; 16" />\n\t\t\t<widget name="key_green" position="36,588" size="200,22" transparent="1" font="Regular; 16" />\n\t\t\t<widget name="key_yellow" position="441,588" size="258,22" transparent="1" font="Regular; 17" />\n\t\t\t<widget name="imagen" position="550,125" size="620,348" zPosition="14" transparent="1" alphatest="blend" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/descargasSPZ/img/logospafs8.png" />\n\t\t\t<widget name="key_mode" position="8,8" size="685,22" transparent="1" text=" " font="Regular; 15" halign="left" />\n\t\t\t<widget name="barrapix_arr" position="0,39" zPosition="19" size="537,542" alphatest="blend" transparent="1" />\n\t\t\t<widget name="barrapix_abj" position="0,0" zPosition="19" size="20,20" alphatest="blend" transparent="1" />\t\n\t\t\t<eLabel name="linea1" position="543,34" size="1,551" zPosition="50" backgroundColor="#03444444" />\n\t\t\t<eLabel name="linea2" position="0,34" size="1200,1" zPosition="50" backgroundColor="#03444444" />\n\t\t\t<eLabel name="linea3" position="0,584" size="1200,1" zPosition="50" backgroundColor="#03444444" />\n\t\t\t<ePixmap name="new ePixmap" position="0,587" size="35,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/descargasSPZ/img/bgreen-fs8.png" alphatest="blend" />\n\t\t\t<ePixmap name="new ePixmap" position="190,587" size="35,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/descargasSPZ/img/bred-fs8.png" alphatest="blend" />\n\t\t\t<ePixmap name="new ePixmap" position="405,587" size="35,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/descargasSPZ/img/yellow.png" alphatest="blend" />\n\t\t\t<widget name="key_ok" position="1043,588" size="258,22" transparent="1" font="Regular; 16" />\n\t\t\t<ePixmap name="new ePixmap" position="970,587" size="35,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/descargasSPZ/img/bexit-fs8.png" alphatest="blend" />\n\t\t\t<ePixmap name="new ePixmap" position="1005,587" size="35,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/descargasSPZ/img/bok-fs8.png" alphatest="blend" />\n\t\t\t<ePixmap name="new ePixmap" position="550,44" size="23,22" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/descargasSPZ/img/vgreen-fs8.png" alphatest="blend" />\n\t\t\t<ePixmap name="new ePixmap" position="550,80" size="23,22" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/descargasSPZ/img/vred-fs8.png" alphatest="blend" />\n\t\t\t<widget name="key_pos" position="575,40" size="424,30" transparent="1" font="Regular; 20" foregroundColor="#0000ff00" shadowColor="#000000" shadowOffset="-2,-2" valign="center" />\n\t\t\t<widget name="key_neg" position="575,75" size="424,30" transparent="1" font="Regular; 20" foregroundColor="#00ff0000" shadowColor="#000000" shadowOffset="-2,-2" valign="center" />\n\t\t\t<eLabel name="linea4" position="543,112" size="620,1" zPosition="50" backgroundColor="#03444444" />\n\t\t\t<widget name="key_totg" position="757,58" size="392,30" transparent="1" font="Regular; 20" foregroundColor="#0000ff00" shadowColor="#000000" shadowOffset="-2,-2" valign="center" halign="right" />\n\t\t\t<widget name="key_totr" position="757,58" size="392,30" transparent="1" font="Regular; 20" foregroundColor="#00ff0000" shadowColor="#000000" shadowOffset="-2,-2" valign="center" halign="right" />\n\t\t\t<widget name="linver" position="849,88" size="300,5" transparent="0" backgroundColor="#003dce3d" zPosition="51"/>\n\t\t\t<widget name="linroj" position="849,88" size="300,5" transparent="0" backgroundColor="#00ff5147" zPosition="50"/>\n\t\t</screen>' % _('openSPA Downloads')

    def __init__(self, session, parent, lalista):
        self.session = session
        Screen.__init__(self, session)
        self.texto = ''
        self.parent = parent
        textoinfo = ''
        self.listado = lalista
        self['respuesta'] = ScrollLabel(_(''))
        self.titulo = formateatexto(str(self.listado[3]))
        self['modo'] = Label(_(''))
        self['key_mode'] = Label(_(''))
        self['textodescarga'] = Label(' ')
        texto1 = _('-1') + _('(Not recommended)')
        texto2 = _('+1') + _('(Recommended)')
        self['linver'] = Label(_(' '))
        self['linroj'] = Label(_(' '))
        nombre = self.listado[2]
        if nombre + ',' in self.parent.votados:
            texto1 = ' '
            texto2 = ' '
        self['key_red'] = Label(texto1)
        self['key_green'] = Label(texto2)
        self['key_ok'] = Label(_('Close'))
        self['key_yellow'] = Label(_('INSTALL'))
        self['imagen'] = ImagenDescarga()
        self['setupActions'] = ActionMap(['WizardActions',
         'DirectionActions',
         'ColorActions',
         'NumberActions',
         'MenuActions',
         'EPGSelectActions',
         'InfobarActions'], {'green': self.gexit,
         'red': self.rexit,
         'yellow': self.instalar,
         'back': self.exit,
         'left': self.key_up,
         'right': self.key_down,
         'up': self.key_up,
         'down': self.key_down,
         'info': self.exit,
         'ok': self.exit}, -2)
        self['barrapix_arr'] = Pixmap()
        self['barrapix_abj'] = Pixmap()
        self.imgdes = ''
        html = None
        try:
            intentos = 3
            html = None
            for iji in range(intentos):
                html = execurlext('datosg.php', 'plugin=' + self.listado[2])
                if not html == None:
                    if len(str(html)) > 2:
                        break

        except:
            html = None

        if not html == None:
            textoinfo = textoinfo + _('Category') + ': ' + devDato(html, 'categoria') + '\n'
        textoinfo = textoinfo + _('Size of file') + ': ' + Humanizer(self.listado[4], True) + '\n'
        datofecha = ''
        try:
            datofecha = time.strptime(self.listado[5], '%d-%m-%Y')
        except:
            pass

        textoinfo = textoinfo + _('Upload Date') + ': ' + formateafecha(lafecha=datofecha, corta=False, hora=False) + '\n'
        textoinfo = textoinfo + _('Number of Downloads') + ': ' + FormatWithCommas(self.listado[8]) + '\n'
        self['key_neg'] = Label('(-1) ' + FormatWithCommas(self.listado[7]) + ' ' + _('votes'))
        self['key_pos'] = Label('(+1) ' + FormatWithCommas(self.listado[6]) + ' ' + _('votes'))
        ndife = int(self.listado[6]) - int(self.listado[7])
        if int(self.listado[6]) + int(self.listado[7]) == 0:
            dife = ''
            self['key_totg'] = Label(' ')
            self['key_totr'] = Label(' ')
        elif ndife == 0:
            dife = _('TOTAL VOTES') + ': ' + FormatWithCommas(int(self.listado[6]) + int(self.listado[7])) + ' (' + '' + FormatWithCommas(ndife) + ')'
            self['key_totr'] = Label(' ')
            self['key_totg'] = Label(dife)
        elif ndife > 0:
            dife = _('TOTAL VOTES') + ': ' + FormatWithCommas(int(self.listado[6]) + int(self.listado[7])) + ' (' + '+' + FormatWithCommas(ndife) + ')'
            self['key_totr'] = Label(' ')
            self['key_totg'] = Label(dife)
        else:
            dife = _('TOTAL VOTES') + ': ' + FormatWithCommas(int(self.listado[6]) + int(self.listado[7])) + ' (' + '' + FormatWithCommas(ndife) + ')'
            self['key_totg'] = Label(' ')
            self['key_totr'] = Label(dife)
        textoinfo = textoinfo + _('File name') + ': ' + quitaextension(str(self.listado[0])) + '\n'
        if not html == None:
            lav = devDato(html, 'version')
            if len(lav) > 0:
                textoinfo = textoinfo + _('Version') + ': ' + lav + '\n'
            textoinfo = textoinfo + _('Languages') + ': ' + _(devDato(html, 'idioma')) + '\n'
            textoinfo = textoinfo + _('Models') + ': ' + devDato(html, 'modelos') + '\n'
            self.imgdes = devDato(html, 'imagen').replace(',', '')
            textoinfo = textoinfo + '-------------------------------------------------------------------------------------------\n' + devDato(html, 'descripcion')
        else:
            textoinfo = textoinfo + '-------------------------------------------------------------------------------------------\n' + _('URL Request error. Check internet conection.') + '\n' + _('It is also possible that the download server is down, or that we are performing maintenance tasks.')
        self.texto = textoinfo
        self.TimerDescarga = eTimer()
        self.TimerDescarga.callback.append(self.DescargaTimer)
        self.onLayoutFinish.append(self.cargapregunta)

    def muestrastat(self):
        if int(self.listado[6]) + int(self.listado[7]) > 0:
            votossi = int(self.listado[6])
            maxanchobarra = 300
            if votossi > 0:
                anchobarra = maxanchobarra * votossi / (votossi + int(self.listado[7]))
                if int(anchobarra) <= 1 and votossi > 0:
                    anchobarra = 2
                elif int(anchobarra) == maxanchobarra - 1:
                    anchobarra = anchobarra - 1
                temp = (int(anchobarra), self['linver'].instance.size().height())
                self['linver'].instance.resize(eSize(*temp))
            else:
                self['linver'].hide()
        else:
            self['linver'].hide()
            self['linroj'].hide()

    def ver_img(self):
        try:
            if self.imgdes != '':
                self.descargaPrevia(self.imgdes)
                return
        except:
            pass

        self['textodescarga'].setText(_('No preview image'))

    def errorIconDownload(self, error = None, item = None):
        self['textodescarga'].setText(_('Error downloading') + ':\n' + item.url + '\n' + item.filename)
        item.error = True

    def finishedIconDownload(self, result, item):
        if not item.error:
            self.showIcon(item.index, item.filename)

    def showIcon(self, nombre, filename):
        self[nombre].updateIcon(filename)
        self[nombre].show()

    def DescargaTimer(self):
        archivoipk = self.imgdes
        archivoremoto = URLXML + 'capturas/' + archivoipk
        comando1 = "cd /tmp;wget '" + archivoremoto + "';" + 'chmod 755 /tmp/' + archivoipk
        retfile = cargaosinfo(comando1, True)
        if retfile == None:
            pinfo = _('Error downloading') + ':  ' + archivoipk + '\n' + _('Press [OK] or [EXIT] key to back.')
            self['textodescarga'].setText(pinfo)
        else:
            try:
                self.showIcon('imagen', '/tmp/' + self.imgdes)
                self['imagen'].show()
                self['textodescarga'].setText(' ')
            except:
                pinfo = _('Error downloading') + '(2):  ' + archivoipk + '\n' + _('Press [OK] or [EXIT] key to back.')
                self['textodescarga'].setText(pinfo)

    def descargaPrevia(self, archivo):
        self['textodescarga'].setText(_('Downloading') + ' ' + _('Image preview') + '\n' + _('Wait...'))
        self['textodescarga'].show()
        self.TimerDescarga.start(200, True)

    def error(self, error = None):
        if error is not None:
            self['textodescarga'].setText(str(error.getErrorMessage()))
            self['imagen'].hide()

    def gexit(self):
        self.exit(1)

    def rexit(self):
        self.exit(-1)

    def exit(self, valor = 0):
        if not self.imgdes == '':
            os.system('rm /tmp/' + self.imgdes)
        self.close(valor)

    def instalar(self):
        archivoipk = formateatexto(self.listado[3])
        dei = self.session.openWithCallback(self.cbinstalar, MessageBox, _('Do you want to install?') + '\n' + archivoipk, MessageBox.TYPE_YESNO)
        dei.setTitle(_('openSPA Downloads'))

    def cbinstalar(self, respuesta):
        if respuesta:
            self.exit(2)

    def cargapregunta(self):
        self['modo'].setText('        ' + self.titulo)
        self['respuesta'].setText(self.texto)
        self['key_mode'].setText(_(' '))
        openspaSB(objectoself=self, nombrelista='barrapix', barra='barrapix', altoitem=25, imagen=True)
        self.muestrastat()
        self.ver_img()

    def key_up(self):
        self['respuesta'].pageUp()

    def key_down(self):
        self['respuesta'].pageDown()


class InfoArchivo2(Screen):
    if esHD:
        skin = '\n\t\t<screen name="InfoArchivo2" position="center,70" size="1500,915" title="%s">\n\t\t\t<widget name="respuesta" position="7,85" size="1485,763" zPosition="12" font="Regular; 19" transparent="1" backgroundColor="#00000000"/>\n\t\t\t<ePixmap name="new ePixmap" position="0,18" size="60,45" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/infoHD.png" alphatest="blend" transparent="1" zPosition="10" />\n\t\t\t<widget name="modo" position="7,16" size="1485,48" backgroundColor="#ffffff" foregroundColor="#000000" text=" " font="Regular; 22" valign="center"/>\n\t\t\t<widget name="img_yellow" position="0,876" size="52,37" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/yellowHD.png" alphatest="blend" />\n\t\t\t<widget name="key_red" position="55,876" size="744,37" transparent="1" font="Regular; 17" zPosition="20" backgroundColor="black" foregroundColor="foreground" noWrap="1" halign="left" valign="center" />\n\t\t\t<widget name="key_mode" position="1330,876" size="1027,37" transparent="1" font="Regular; 17" halign="left" valign="center"  />\n\t\t\t<widget name="barrapix_arr" position="7,85" zPosition="19" size="1485,763" alphatest="blend" transparent="1" />\n\t\t\t<widget name="barrapix_abj" position="0,0" zPosition="19" size="30,30" alphatest="blend" transparent="1" />\t\n\t\t\t<ePixmap name="new ePixmap" zPosition="-2" position="262,273" size="930,523" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/descargasSPZ/img/hdlogospafs8.png" alphatest="blend" />\t\t\n\t\t\t<ePixmap name="new ePixmap" position="1275,876" size="52,37" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/okHD.png" alphatest="blend" />\n\t\t\t<ePixmap name="new ePixmap" position="1222,876" size="52,37" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/exitHD.png" alphatest="blend" />\n\t\t\t<eLabel name="linea3" position="0,868" size="1500,1" zPosition="50" backgroundColor="#03444444" />\n\t\t</screen>' % _('openSPA Downloads')
    else:
        skin = '\n\t\t<screen name="InfoArchivo2" position="center,70" size="1000,610" title="%s">\n\t\t\t<widget name="respuesta" position="5,57" size="990,509" zPosition="12" font="Regular; 19" transparent="1" backgroundColor="#00000000"/>\n\t\t\t<ePixmap name="new ePixmap" position="0,12" size="40,30" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/descargasSPZ/img/info-fs8.png" alphatest="blend" transparent="1" zPosition="10" />\n\t\t\t<widget name="modo" position="5,11" size="990,32" backgroundColor="#ffffff" foregroundColor="#000000" text=" " font="Regular; 22" valign="center"/>\n\t\t\t<widget name="img_yellow" position="0,584" size="35,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/descargasSPZ/img/yellow.png" alphatest="blend" />\n\t\t\t<widget name="key_red" position="37,584" size="496,25" transparent="1" font="Regular; 17" zPosition="20" backgroundColor="black" foregroundColor="foreground" noWrap="1" halign="left" valign="center" />\n\t\t\t<widget name="key_mode" position="887,584" size="685,25" transparent="1" font="Regular; 17" halign="left" valign="center"  />\n\t\t\t<widget name="barrapix_arr" position="5,57" zPosition="19" size="990,509" alphatest="blend" transparent="1" />\n\t\t\t<widget name="barrapix_abj" position="0,0" zPosition="19" size="20,20" alphatest="blend" transparent="1" />\t\n\t\t\t<ePixmap name="new ePixmap" zPosition="-2" position="175,182" size="620,349" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/descargasSPZ/img/logospafs8.png" alphatest="blend" />\t\t\n\t\t\t<ePixmap name="new ePixmap" position="850,584" size="35,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/descargasSPZ/img/bok-fs8.png" alphatest="blend" />\n\t\t\t<ePixmap name="new ePixmap" position="815,584" size="35,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/descargasSPZ/img/bexit-fs8.png" alphatest="blend" />\n\t\t\t<eLabel name="linea3" position="0,579" size="1000,1" zPosition="50" backgroundColor="#03444444" />\n\t\t</screen>' % _('openSPA Downloads')

    def __init__(self, session, titulo = _('openSPA Downloads'), textoinfo = '', esds = False, textoinfo0 = ''):
        self.session = session
        Screen.__init__(self, session)
        if esds:
            addinfo = ''
            if fileExists('/usr/bin/vbinds'):
                addinfo = addinfo + '(VIP)'
            textoinfo = textoinfo0 + addinfo + '\n---------------------------------------------------------------\n\n' + textoinfo
        self.texto = textoinfo
        self.titulo = titulo
        self['respuesta'] = ScrollLabel(_(''))
        self.sids = esds
        self['modo'] = Label(_(''))
        self['key_mode'] = Label(_(''))
        self['img_yellow'] = Pixmap()
        self['key_red'] = Label(_(''))
        self['setupActions'] = ActionMap(['WizardActions',
         'DirectionActions',
         'ColorActions',
         'NumberActions',
         'MenuActions',
         'EPGSelectActions',
         'InfobarActions'], {'green': self.exit,
         'red': self.exit,
         'yellow': self.cksat,
         'back': self.exit,
         'left': self.key_up,
         'right': self.key_down,
         'up': self.key_up,
         'down': self.key_down,
         'info': self.exit,
         'ok': self.exit}, -2)
        self['barrapix_arr'] = Pixmap()
        self['barrapix_abj'] = Pixmap()
        self.onLayoutFinish.append(self.cargapregunta)

    def cksat(self):
        if self.sids:
            self.close(True)

    def exit(self):
        self.close()

    def cargapregunta(self):
        titulo = self.titulo
        if self.sids:
            try:
                titulo = titulo.decode('windows-1252').encode('utf-8')
            except:
                pass

        else:
            self['key_red'].hide()
            self['img_yellow'].hide()
        self['modo'].setText('       ' + titulo)
        self['respuesta'].setText(self.texto)
        self['key_mode'].setText(_('Close'))
        openspaSB(objectoself=self, nombrelista='barrapix', barra='barrapix', altoitem=25, imagen=True)

    def key_up(self):
        self['respuesta'].pageUp()

    def key_down(self):
        self['respuesta'].pageDown()


class descargasSPZ(Screen, HelpableScreen):
    if esHD():
        skin = '\n\t\t<screen name="descargasSPZ" position="center,70" size="1500,915" title="%s">\n\t\t<widget name="textoinfo" position="12,187" size="1455,675" valign="top" halign="left" text=" " font="Regular; 18" zPosition="2" transparent="1" />\n\t\t<eLabel name="linea1" position="12,186" size="1455,1" backgroundColor="#00555555" />\n\t\t<eLabel name="linea2" position="12,864" size="1455,1" backgroundColor="#00555555" />\n\t\t<widget name="listaA" position="12,187" size="1455,675" scrollbarMode="showOnDemand" zPosition="12" transparent="1" />\n\t\t<widget name="img_fondo" position="12,187" size="1455,675" alphatest="blend" zPosition="11" transparent="1" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/descargasSPZ/img/fondodesHD-fs8.png" />\n\t\t<widget name="modo" position="12,0" size="1455,45" backgroundColor="#ffffff" foregroundColor="#000000" text=" " font="Regular; 19" noWrap="1" valign="center"/>\n\t\t<ePixmap name="new ePixmap" position="1161,876" size="52,37" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/blueHD.png" alphatest="blend" transparent="1" />\n\t\t<widget name="key_green" position="51,877" size="300,33" transparent="1" font="Regular; 16" />\n\t\t<widget name="key_blue" position="1212,877" size="543,33" transparent="1" text="News" font="Regular; 16" />\n\t\t<widget name="img_red" position="264,876" zPosition="2" size="52,37" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/descargasSPZ/img/hdbred-fs8.png" transparent="1" alphatest="blend" />\n\t\t<widget name="key_red" position="315,877" size="300,33" transparent="1" font="Regular; 16" />\n\t\t<widget name="img_yellow" position="555,876" zPosition="2" size="52,37" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/yellowHD.png" transparent="1" alphatest="blend" />\n\t\t<widget name="key_yellow" position="606,877" size="432,33" transparent="1" font="Regular; 16" />\n\n\t\t<widget name="key_help" backgroundColor="#000000" position="12,63" size="813,105" transparent="1" font="Regular; 17" halign="left" zPosition="-10" valign="center" foregroundColor="#00999999" shadowColor="#000000" shadowOffset="-2,-2"/>\n\t\t<ePixmap name="ds" position="832,52" size="634,126" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/descargasSPZ/img/bdsHD-fs8.png" alphatest="blend" zPosition="-10" />\n\t\t<widget name="key_mode" position="12,12" size="1027,33" transparent="1" text=" " font="Regular; 15" halign="left" />\n\t\t<widget name="img_green" position="0,876" zPosition="2" size="52,37" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/descargasSPZ/img/hdbgreen-fs8.png" transparent="1" alphatest="blend" />\t\n\t\t<widget name="barrapix_arr" position="0,0" zPosition="19" size="30,30" alphatest="blend" transparent="1" />\n\t\t<widget name="barrapix_abj" position="0,0" zPosition="19" size="30,30" alphatest="blend" transparent="1" />\n\t\t<widget name="barrapix3_arr" position="12,187" zPosition="19" size="1455,675" alphatest="blend" transparent="1" />\n\t\t<widget name="barrapix3_abj" position="0,0" zPosition="19" size="30,30" alphatest="blend" transparent="1" />\n\t\t<widget name="key_ok" position="606,877" size="432,33" transparent="1" font="Regular; 16" />\n\t\t<ePixmap name="new ePixmap" position="855,876" size="52,37" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/menuHD.png" alphatest="blend" transparent="1" />\n \t\t<widget name="key_options" position="907,877" size="432,33" transparent="1" font="Regular; 16" />\n\t\t<widget name="img_ok" position="555,876" zPosition="2" size="52,37" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/okHD.png" transparent="1" alphatest="blend" />\n\t\t</screen>' % _('openSPA Downloads')
    else:
        skin = '\n\t\t<screen name="descargasSPZ" position="center,70" size="1000,610" title="%s">\n\t\t<widget name="textoinfo" position="8,125" size="970,450" valign="top" halign="left" text=" " font="Regular; 18" zPosition="2" transparent="1" />\n\t\t<eLabel name="linea1" position="8,124" size="970,1" backgroundColor="#00555555" />\n\t\t<eLabel name="linea2" position="8,576" size="970,1" backgroundColor="#00555555" />\n\t\t<widget name="listaA" position="8,125" size="970,450" scrollbarMode="showOnDemand" zPosition="12" transparent="1" />\n\t\t<widget name="img_fondo" position="8,125" size="970,450" alphatest="blend" zPosition="11" transparent="1" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/descargasSPZ/img/fondodes-fs8.png" />\n\t\t<widget name="modo" position="8,0" size="970,30" backgroundColor="#ffffff" foregroundColor="#000000" text=" " font="Regular; 19" noWrap="1" valign="center"/>\n\t\t<ePixmap name="new ePixmap" position="774,584" size="35,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/descargasSPZ/img/blue.png" alphatest="blend" transparent="1" />\n\t\t<widget name="key_green" position="34,585" size="200,22" transparent="1" font="Regular; 16" />\n\t\t<widget name="key_blue" position="808,585" size="362,22" transparent="1" text="News" font="Regular; 16" />\n\t\t<widget name="img_red" position="176,584" zPosition="2" size="35,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/descargasSPZ/img/bred-fs8.png" transparent="1" alphatest="blend" />\n\t\t<widget name="key_red" position="210,585" size="200,22" transparent="1" font="Regular; 16" />\n\t\t<widget name="key_help" backgroundColor="#000000" position="8,42" size="542,70" transparent="1" font="Regular; 17" halign="left" zPosition="-10" valign="center" foregroundColor="#00999999" shadowColor="#000000" shadowOffset="-2,-2"/>\n\t\t<ePixmap name="ds" position="555,35" size="423,84" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/descargasSPZ/img/bds-fs8.png" alphatest="blend" zPosition="-10" />\n\t\t<widget name="key_mode" position="8,8" size="685,22" transparent="1" text=" " font="Regular; 15" halign="left" />\n\t\t<widget name="img_green" position="0,584" zPosition="2" size="35,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/descargasSPZ/img/bgreen-fs8.png" transparent="1" alphatest="blend" />\t\n\t\t<widget name="barrapix_arr" position="0,0" zPosition="19" size="20,20" alphatest="blend" transparent="1" />\n\t\t<widget name="barrapix_abj" position="0,0" zPosition="19" size="20,20" alphatest="blend" transparent="1" />\n\t\t<widget name="barrapix3_arr" position="8,125" zPosition="19" size="970,450" alphatest="blend" transparent="1" />\n\t\t<widget name="barrapix3_abj" position="0,0" zPosition="19" size="20,20" alphatest="blend" transparent="1" />\n\t\t<widget name="key_ok" position="404,585" size="288,22" transparent="1" font="Regular; 16" />\n\t\t<ePixmap name="new ePixmap" position="570,584" size="35,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/descargasSPZ/img/menu.png" alphatest="blend" transparent="1" />\n\t\t<widget name="key_options" position="605,585" size="288,22" transparent="1" font="Regular; 16" />\n\t\t<widget name="img_ok" position="370,584" zPosition="2" size="35,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/descargasSPZ/img/bok-fs8.png" transparent="1" alphatest="blend" />\n\t\t</screen>' % _('openSPA Downloads')

    def __init__(self, session, categoria = None, nombrecategoria = '', instance = None, args = 0):
        global TimerMirar
        global TimerGoUpdates
        global globalsession
        global valor_ordenar
        self.session = session
        Screen.__init__(self, session)
        HelpableScreen.__init__(self)
        globalsession = self
        self.listado = []
        self.categoria_ini_nombre = _(nombrecategoria)
        self.categoria_ini = categoria
        self.categoria_ini2 = categoria
        if not fileExists('/usr/bin/OpenSPA.info'):
            try:
                from Plugins.Extensions.spazeMenu.hardinfo import creamodeloinfo
                creamodeloinfo()
            except:
                pass

        self.instalando = False
        self.TimerTemp = eTimer()
        self.TimerTemp.callback.append(self.instalarok)
        self.TimerPrivado = eTimer()
        self.TimerPrivado.callback.append(self.desactivaprivado)
        self.timerReload = eTimer()
        self.timerReload.callback.append(self.key_reload)
        self.tiempotimer = 600
        self.nprivado = 0
        self.instalados = []
        try:
            TimerGoUpdates.stop()
        except:
            pass

        try:
            TimerMirar.stop()
        except:
            pass

        booklist = None
        if fileExists('/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/descargasSPZ/updated.txt'):
            try:
                booklist = open('/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/descargasSPZ/updated.txt', 'r')
            except:
                pass

            ret = ''
            if booklist is not None:
                for oneline in booklist:
                    oneline = oneline.replace('\n', '').replace('\r', '')
                    if len(oneline) > 2:
                        self.instalados.append(oneline)

                booklist.close()
        self.infomostrado = False
        self.carpeta = '/'
        self.modoarchivo = False
        self.busqueda = ''
        self.url = 'ftp://spazeteam:ad32fG0s@www.azboxhd.es'
        self.url2 = 's221459518.mialojamiento.es'
        self.imgdes = ''
        self.usuario = 'spazeteam'
        self.container = eConsoleAppContainer()
        self.container.appClosed.append(self.runFinished)
        self.terminado = False
        self.t1 = 0
        self.t2 = 0
        self.container.dataAvail.append(self.dataAvail)
        self.pinfo_cmd = ''
        self.pwd = 'ad32fG0s'
        self.privado = False
        self.numcar = 0
        self.numarc = 0
        self.lugar = ''
        self['listaA'] = IniciaSelListArchivo([])
        self['textoinfo'] = ScrollLabel(_(''))
        self['modo'] = Label(_(''))
        self['key_help'] = Label(_(''))
        self['key_mode'] = Label(_(''))
        self['img_fondo'] = Pixmap()
        self['img_red'] = Pixmap()
        self['img_green'] = Pixmap()
        self['img_yellow'] = Pixmap()
        self['img_ok'] = Pixmap()
        self.paso = 0
        self.sisat = False
        self.pinfo = ''
        self.titulo = ''
        self.vacio = False
        self.num_archivos = 0
        valor_ordenar = ''
        self.picon = ''
        self['key_red'] = Label(_('-1') + _('(Not recommended)'))
        self['key_green'] = Label(_('+1') + _('(Recommended)'))
        self['key_yellow'] = Label(_('(Restart GUI)'))
        self['key_blue'] = Label(_('openSPA News'))
        self['key_ok'] = Label(_('View Details/Install'))
        self['key_options'] = Label(_('Options/Search') + '...')
        self['setupActions'] = ActionMap(['ColorActions'], {'yellow': self.chkprivado2}, -2)
        self['coloractions'] = HelpableActionMap(self, 'ColorActions', {'green': (self.votopositivo, _('Send for current entry') + ': ' + _('+1') + _('(Recommended)')),
         'blue': (self.chkprivado3, _('Show openSPA News')),
         'red': (self.votonegativo, _('Send for current entry') + ': ' + _('-1') + _('(Not recommended)')),
         'yellow': (self.key_reload, _('Reload screen'))}, -2)
        self['menuactions'] = HelpableActionMap(self, 'MenuActions', {'menu': (self.key_menu, _('Options menu'))}, -2)
        self['directionactions'] = HelpableActionMap(self, 'WizardActions', {'left': (self.key_left, _('Page Up')),
         'right': (self.key_right, _('Page Down')),
         'up': (self.key_up, _('Move Up')),
         'down': (self.key_down, _('Move Down')),
         'ok': (self.bkey_ok, _('View Details/Install') + ' | ' + _('Open category')),
         'back': (self.volver, _('Exit'))}, -2)
        self['numberactions'] = HelpableActionMap(self, 'NumberActions', {'0': (self.key_buscar, _('Downloads Search')),
         '1': (self.key_ayuda, _('Remote control help')),
         '2': (self.key_inicio, _('Go to') + ' ' + _('Home')),
         '3': (self.key_categorias, _('Go to') + ' ' + _('Categories'))}, -2)
        if fileExists('/tmp/resetdescargas'):
            os.system('rm /tmp/resetdescargas')
            os.system('rm /usr/bin/vbinds')
            os.system('rm /usr/bin/chkds')
        if fileExists('/usr/bin/vbinds'):
            self.privado = True
        elif not fileExists('/usr/bin/chkds'):
            chequeamaks(self.url2)
            if fileExists('/usr/bin/vbinds'):
                self.privado = True
        self.onLayoutFinish.append(self.buildList)
        self['listaA'].onSelectionChanged.append(self.muevesel)
        self.onShow.append(self.mostrar)
        self.iniciadoS = False
        self.bloqueado = False
        self['barrapix_arr'] = Pixmap()
        self['barrapix_abj'] = Pixmap()
        self['barrapix3_arr'] = Pixmap()
        self['barrapix3_abj'] = Pixmap()
        self.votados = ''
        self.pontitulo()

    def pontitulo(self):
        elmodelo = devcodmodelo()
        self.codigomodelo = elmodelo[0]
        addt = ''
        if fileExists('/usr/bin/chkds'):
            addt = '-dS'
        if fileExists('/usr/bin/vbinds'):
            addt = addt + '(VIP)'
            self.privado = True
        self.setTitle(_('openSPA Downloads') + ' :: ' + elmodelo[1] + addt)

    def key_buscar(self):
        from Plugins.Extensions.spazeMenu.spzVirtualKeyboard import spzVirtualKeyboard
        self.session.openWithCallback(self.nuevaBcb, spzVirtualKeyboard, titulo=_('Search download') + ':', texto=self.busqueda)

    def key_ayuda(self):
        self.session.openWithCallback(self.cbhelp, HelpMenu, self.helpList)

    def key_reload(self):
        self.buildList(self.carpeta, self.lugar, True)

    def key_inicio(self):
        self.buildList()

    def key_dsat(self, txtmsg = ''):
        global glenguaje
        return
        elfile = '/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/descargasSPZ/donsat_info_' + glenguaje
        txtd = ''
        if not fileExists(elfile + '.info'):
            elfile = '/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/descargasSPZ/donsat_info_en'
        if not fileExists(elfile + '.info'):
            elfile = '/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/descargasSPZ/donsat_info_es'
        try:
            txtd = open(elfile + '.info', 'r').read()
        except:
            pass

        try:
            txtd = txtd.decode('windows-1252').encode('utf-8')
        except:
            pass

        self.session.openWithCallback(self.cb_dsat, InfoArchivo2, titulo=_('DonSatelite downloads help'), textoinfo=txtd, esds=True, textoinfo0=txtmsg)

    def cb_dsat(self, resp = None):
        if resp:
            chequeamaks(self.url2)
            if not fileExists('/usr/bin/chkds'):
                msg = _('DonSatelite customer not found!!!\nUse your support website for help.')
                tipo = MessageBox.TYPE_ERROR
            else:
                msg = _('Congratulations! DonSatelite customer found.\nThe exclusive downloads are available to install.')
                tipo = MessageBox.TYPE_INFO
            self.pontitulo()
            dei = self.session.open(MessageBox, msg, tipo)
            dei.setTitle(_('openPLI downloads').replace('openPLI', 'Enigma2'))

    def key_categorias(self):
        self.buildList('-2', '<' + _('Categories') + '>')

    def dev_valorOrdenar(self, texto):
        textocur = '*'
        if self.carpeta == '' and texto == '' and valor_ordenar == 'nombre':
            return '(' + textocur + ')'
        elif texto == valor_ordenar:
            return '(' + textocur + ')'
        else:
            return ''

    def key_menu(self):
        if self.bloqueado:
            return
        if self.instalando:
            self.desins()
            return
        nkeys = []
        list = []
        list.append((_('Downloads Search') + ' ', 'search'))
        nkeys.append('0')
        list.append((_('Remote control help') + ' ', 'help'))
        nkeys.append('1')
        list.append(('------------------------------------------------------------------------------------------------------------------------------------------------------------------------', ''))
        nkeys.append('')
        list.append((_('Reload screen') + ' ', 'reload'))
        nkeys.append('yellow')
        list.append((_('Go to') + ' ' + _('Home') + ' ', '-1'))
        nkeys.append('2')
        list.append((_('Go to') + ' ' + _('Categories') + ' ', '-2'))
        nkeys.append('3')
        if not self.categoria_ini2 == None:
            list.append((_('Go to') + ' ' + self.formateatitulo('<' + _('Categories') + '>' + '/*/' + self.categoria_ini_nombre) + ' ', 'catini'))
            nkeys.append('4')
        list.append(('------------------------------------------------------------------------------------------------------------------------------------------------------------------------', ''))
        nkeys.append('')
        if self.num_archivos > 0:
            dsc1 = 'Latest Downloads'
            dsc2 = 'Top Rated'
            dsc3 = 'Top Downloads'
            dsc4 = 'Name of download'
            if self.carpeta == '':
                adds = _('Show on home') + ' '
            else:
                adds = _('Order by') + ' '
            list.append((adds + _(dsc1) + self.dev_valorOrdenar('') + ' ', 'fecha'))
            nkeys.append('5')
            list.append((adds + _(dsc2) + self.dev_valorOrdenar('votos') + ' ', 'votos'))
            nkeys.append('6')
            list.append((adds + _(dsc3) + self.dev_valorOrdenar('descargas') + ' ', 'descargas'))
            nkeys.append('7')
            if self.carpeta != '':
                list.append((adds + _(dsc4) + self.dev_valorOrdenar('nombre') + ' ', 'nombre'))
                nkeys.append('8')
            list.append(('------------------------------------------------------------------------------------------------------------------------------------------------------------------------', ''))
            nkeys.append('')
        list.append((_('openPLI downloads').replace('openPLI', 'Enigma2') + ' ', 'opdwn'))
        nkeys.append('')
        list.append(('------------------------------------------------------------------------------------------------------------------------------------------------------------------------', ''))
        nkeys.append('')
        if self.modoarchivo:
            nombrelista = 'listaA'
            numero = self[nombrelista].getSelectionIndex()
            if self.listado[numero][1][0] == 'a':
                nombre = self.listado[numero][3]
                if nombre + ',' not in self.votados:
                    list.append((_('+1') + _('(Recommended)') + ' -> ' + formateatexto(nombre) + '', 'votopos'))
                    nkeys.append('green')
                    list.append((_('-1') + _('(Not recommended)') + ' -> ' + formateatexto(nombre) + '', 'votoneg'))
                    nkeys.append('red')
                    list.append(('------------------------------------------------------------------------------------------------------------------------------------------------------------------------', ''))
                    nkeys.append('')
        list.append((_('Show openSPA News') + ' ', 'updatelog'))
        nkeys.append('blue')
        from Screens.ChoiceBox import ChoiceBox
        self.session.openWithCallback(self.cbkmenu, ChoiceBox, keys=nkeys, title=_('openSPA Downloads') + ' ' + _('Options'), list=list)

    def cbkmenu(self, answer):
        global valor_ordenar
        answer = answer and answer[1]
        if answer == 'votopos':
            self.votopositivo()
        elif answer == 'votoneg':
            self.votonegativo()
        elif answer == 'updatelog':
            self.chkprivado3()
        elif answer == 'opdwn':
            self.buildList('-3', _('openPLI downloads'))
        elif answer == 'help':
            self.key_ayuda()
        elif answer == '-1':
            self.key_inicio()
        elif answer == 'reload':
            self.key_reload()
        elif answer == '-2':
            self.key_categorias()
        elif answer == 'search':
            self.key_buscar()
        elif answer == 'dsat':
            self.key_dsat()
        elif answer == 'catini':
            self.lugar = '<' + _('Categories') + '>'
            self.buildList(self.categoria_ini2, self.categoria_ini_nombre)
        elif answer == 'fecha':
            valor_ordenar = ''
            self.key_reload()
        elif answer == 'nombre':
            valor_ordenar = 'nombre'
            self.key_reload()
        elif answer == 'descargas':
            valor_ordenar = 'descargas'
            self.key_reload()
        elif answer == 'votos':
            valor_ordenar = 'votos'
            self.key_reload()

    def nuevaBcb(self, ernombre):
        if ernombre == '' or ernombre == None:
            return
        self.busqueda = ernombre
        if len(ernombre) < 3:
            dei = self.session.open(MessageBox, _('The search term must be at least 3 characters!'), MessageBox.TYPE_INFO, timeout=8)
            dei.setTitle(_('openSPA Downloads'))
            return
        self.buildList(ernombre, _('Search of') + ' [' + ernombre + ']')

    def abreopenpli(self, cual):
        if cual == 'opman':
            try:
                from Plugins.SystemPlugins.SoftwareManager.plugin import PluginManager
                self.session.open(PluginManager)
            except:
                dei = self.session.open(MessageBox, _('Unable to find openPLI software manager!!!').replace('openPLI', 'Enigma2'), MessageBox.TYPE_ERROR)
                dei.setTitle(_('openSPA Downloads'))

        elif cual == 'opdwn':
            try:
                from Screens.PluginBrowser import PluginDownloadBrowser
                self.session.open(PluginDownloadBrowser)
            except:
                dei = self.session.open(MessageBox, _('Unable to find openPLI software manager!!!').replace('openPLI', 'Enigma2'), MessageBox.TYPE_ERROR)
                dei.setTitle(_('openSPA Downloads'))

        elif cual == 'opsu':
            dei = self.session.openWithCallback(self.actualizarOP, MessageBox, _('Do yo want launch download software openPLI manager for install new updates?').replace('openPLI', 'Enigma2'), MessageBox.TYPE_YESNO)
            dei.setTitle(_('openSPA Downloads'))

    def actualizarOP(self, resp = None):
        if resp:
            try:
                from Screens.SoftwareUpdate import UpdatePlugin
                self.session.open(UpdatePlugin)
            except:
                dei = self.session.open(MessageBox, _('Unable to find openPLI software manager!!!').replace('openPLI', 'Enigma2'), MessageBox.TYPE_ERROR)
                dei.setTitle(_('openSPA Downloads'))

    def cbnada(self, resp = None):
        pass

    def cbhelp(self, resp = None, *args):
        pass

    def votopositivo(self):
        if self.bloqueado:
            return
        if self.instalando:
            self.desins()
            return
        if self.modoarchivo and not self.instalando:
            nombrelista = 'listaA'
            numero = self[nombrelista].getSelectionIndex()
            if self.listado[numero][1][0] == 'a':
                nombre = self.listado[numero][2]
                if nombre + ',' in self.votados:
                    dei = self.session.open(MessageBox, _('Only can vote one time!'), MessageBox.TYPE_INFO, timeout=8)
                    dei.setTitle(_('openSPA Downloads'))
                else:
                    dei = self.session.openWithCallback(self.cbvotopositivo, MessageBox, _('Do you want to send +1 (positive vote) for this entry?') + '\n[' + formateatexto(self.listado[numero][3]) + ']', MessageBox.TYPE_YESNO)
                    dei.setTitle(_('openSPA Downloads'))

    def cbvotopositivo(self, respuesta = None):
        if not respuesta:
            return
        if self.modoarchivo:
            nombrelista = 'listaA'
            numero = self[nombrelista].getSelectionIndex()
            if self.listado[numero][1][0] == 'a':
                nombre = self.listado[numero][2]
                if nombre + ',' in self.votados:
                    dei = self.session.open(MessageBox, _('Only can vote one time!'), MessageBox.TYPE_INFO, timeout=8)
                    dei.setTitle(_('openSPA Downloads'))
                else:
                    lacarpeta = self.carpeta + ''
                    retvpt = votaftp(lacarpeta, nombre, 1)
                    if not retvpt:
                        dei = self.session.open(MessageBox, _('Unable to send request!\nTry again later.'), MessageBox.TYPE_ERROR)
                        dei.setTitle(_('openSPA Downloads'))
                        return
                    self.actualizadatolista('si', self.listado[numero][2])
                    self.votados = self.votados + nombre + ','
                    self[nombrelista].moveToIndex(numero)
                    archivoipk = formateatexto(self.listado[numero][3])
                    dei = self.session.open(MessageBox, '(+1) ' + archivoipk + '\n' + _('Valoration submited.\nThanks for participate!'), MessageBox.TYPE_INFO, timeout=6)
                    self['key_help'].setText('(+1) ' + archivoipk + ' ' + _('Valoration submited.\nThanks for participate!'))
                    dei.setTitle(_('openSPA Downloads'))

    def votonegativo(self):
        if self.bloqueado:
            return
        if self.instalando:
            self.desins()
            return
        if self.modoarchivo:
            nombrelista = 'listaA'
            numero = self[nombrelista].getSelectionIndex()
            if self.listado[numero][1][0] == 'a':
                nombre = self.listado[numero][2]
                if nombre + ',' in self.votados:
                    dei = self.session.open(MessageBox, _('Only can vote one time!'), MessageBox.TYPE_INFO, timeout=8)
                    dei.setTitle(_('openSPA Downloads'))
                else:
                    dei = self.session.openWithCallback(self.cbvotonegativo, MessageBox, _('Do you want to send -1 (negative vote) for this entry?') + '\n[' + formateatexto(self.listado[numero][3]) + ']', MessageBox.TYPE_YESNO)
                    dei.setTitle(_('openSPA Downloads'))

    def cbvotonegativo(self, respuesta = None):
        if not respuesta:
            return
        if self.modoarchivo:
            nombrelista = 'listaA'
            numero = self[nombrelista].getSelectionIndex()
            if self.listado[numero][1][0] == 'a':
                nombre = self.listado[numero][2]
                if nombre + ',' in self.votados:
                    dei = self.session.open(MessageBox, _('Only can vote one time!'), MessageBox.TYPE_INFO, timeout=8)
                    dei.setTitle(_('openSPA Downloads'))
                else:
                    lacarpeta = self.carpeta + ''
                    retvpt = votaftp(lacarpeta, nombre, -1)
                    if not retvpt:
                        dei = self.session.open(MessageBox, _('Unable to send request!\nTry again later.'), MessageBox.TYPE_ERROR)
                        dei.setTitle(_('openSPA Downloads'))
                        return
                    self.actualizadatolista('no', self.listado[numero][2])
                    self.votados = self.votados + nombre + ','
                    self[nombrelista].moveToIndex(numero)
                    archivoipk = formateatexto(self.listado[numero][3])
                    dei = self.session.open(MessageBox, '(-1) ' + archivoipk + '\n' + _('Valoration submited.\nThanks for participate!'), MessageBox.TYPE_INFO, timeout=6)
                    self['key_help'].setText('(-1) ' + archivoipk + ' ' + _('Valoration submited.\nThanks for participate!'))
                    dei.setTitle(_('openSPA Downloads'))

    def actualizaScrolls(self, eninfo = False):
        openspaSB(objectoself=self, nombrelista='listaA', barra='barrapix', altoitem=50, imagen=True)
        openspaSB(objectoself=self, nombrelista='barrapix3', barra='barrapix3', altoitem=50, imagen=True)
        if eninfo or self.sisat:
            self['barrapix_arr'].hide()
            self['barrapix_abj'].hide()
            if self.sisat:
                self['barrapix3_arr'].hide()
                self['barrapix3_abj'].hide()
            else:
                self['barrapix3_arr'].show()
                self['barrapix3_abj'].show()
            return
        if self.modoarchivo:
            pass
        else:
            self['barrapix_arr'].hide()
            self['barrapix_abj'].hide()
        self['barrapix3_arr'].hide()
        self['barrapix3_abj'].hide()

    def desactivaprivado(self):
        self.nprivado = 0
        self.TimerPrivado.stop()

    def chkprivado2(self):
        if self.bloqueado:
            return
        if self.instalando:
            self.session.open(TryQuitMainloop, 3)
            return
        if self.sisat:
            self.dessat()
            return
        self.buildList(self.carpeta, self.lugar, True)
        return
        self.nprivado = self.nprivado + 1
        self.TimerPrivado.stop()
        self.TimerPrivado.start(2000, True)

    def chkprivado3(self):
        if self.bloqueado:
            return
        if self.sisat:
            self.dessat()
            return
        self.info_ini(True)

    def muevesel(self):
        if len(self.listado) == 0:
            return
        if self.modoarchivo:
            nombrelista = 'listaA'
            numero = self[nombrelista].getSelectionIndex()
            if self.listado[numero][1][0] == 'a':
                ertexto = _('Select entry and press [OK] for install.')
                nombre = self.listado[numero][2]
                if nombre + ',' in self.votados:
                    self['key_red'].hide()
                    self['img_red'].hide()
                    self['key_green'].hide()
                    self['img_green'].hide()
                else:
                    self['key_red'].show()
                    self['img_red'].show()
                    self['key_green'].show()
                    self['img_green'].show()
                ertexto = _('Size of file') + ': ' + Humanizer(self.listado[numero][4], False) + ' | ' + _('Number of Downloads') + ': ' + FormatWithCommas(self.listado[numero][8]) + '\n' + ertexto
                self['img_ok'].show()
                self['key_ok'].show()
                self['key_yellow'].hide()
                self['img_yellow'].hide()
                self['key_help'].setText(ertexto)
            else:
                if self.listado[numero][2] == 'retry':
                    self['key_help'].setText(_('Press [OK] to retry'))
                elif self.listado[numero][2] == '-1':
                    self['key_help'].setText(_('Press [OK] to go Home'))
                elif self.listado[numero][2] == '-2':
                    self['key_help'].setText(_('Press [OK] to obtain the list of categories'))
                elif self.listado[numero][2] == '0':
                    self['key_help'].setText(_('Press [OK] to go back'))
                elif self.listado[numero][2] == '-3':
                    self['key_help'].setText(_('Press [OK] to go openPLI plugins/extensions download options').replace('openPLI', 'Enigma2'))
                else:
                    self['key_help'].setText(_('Press [OK] for go to selected item'))
                self['key_red'].hide()
                self['img_red'].hide()
                self['key_green'].hide()
                self['img_green'].hide()
                self['img_ok'].hide()
                self['key_ok'].hide()
        else:
            self['key_help'].setText(_('Select category and press [OK] for open.'))

    def formateatitulo(self, texto):
        cret = texto.replace('<', '').replace('>', '').replace('/*/', ' >> ')
        if len(cret) > 1:
            cret = ' :: ' + cret
        return cret

    def actualizadatolista(self, nombre, id):
        numero = 0
        if nombre == 'si':
            numero = 6
        elif nombre == 'no':
            numero = 7
        elif nombre == 'descarga':
            numero = 8
        if numero > 0:
            valor = -1
            for iji in range(0, len(self.listado)):
                if self.listado[iji][2] == str(id):
                    valor = int(self.listado[iji][numero]) + 1
                    self.listado[iji][numero] = str(valor)
                    break

            if not listaini == None:
                for iji in range(0, len(listaini[2])):
                    if listaini[2][iji][2] == str(id):
                        if valor > 0:
                            listaini[2][iji][numero] = str(valor)
                        else:
                            listaini[2][iji][numero] = str(int(listaini[2][iji][numero]) + 1)
                        break

            self.crealistado()

    def buildList(self, carpeta = '', titulo = '', forzar = False):
        global anteriorlistado
        self['img_red'].hide()
        self['img_green'].hide()
        self['key_green'].hide()
        self['key_red'].hide()
        self['img_ok'].hide()
        self['key_ok'].hide()
        self['key_yellow'].hide()
        self['img_yellow'].hide()
        if (carpeta == '' or carpeta == '1') and not self.categoria_ini == None:
            tempret = devUrlContenido('', '', privado=self.privado, siforzar=forzar)
            carpeta = self.categoria_ini
            self.lugar = '<' + _('Categories') + '>'
            if self.categoria_ini_nombre != '':
                self.lugar = '<' + _('Categories') + '>' + '/*/' + self.categoria_ini_nombre
            else:
                self.categoria_ini_nombre = self.lugar
            self.categoria_ini = None
        self.carpeta = carpeta
        list = []
        self['listaA'].setList(list)
        self['textoinfo'].hide()
        self['key_mode'].setText(_(' '))
        self['key_blue'].setText(_('openSPA News'))
        self.bloqueado = False
        self['key_help'].setText(_(' '))
        if carpeta == '' or carpeta == '1':
            self.lugar = ''
        elif carpeta == '0':
            if '/*/' in self.lugar:
                ultimo = self.lugar.split('/*/')[-1]
                self.lugar = self.lugar.replace('/*/' + ultimo, '')
            else:
                self.lugar = titulo
        elif carpeta == '-1' or carpeta == '-2' or carpeta == '-3':
            self.lugar = titulo
        elif titulo == self.lugar:
            pass
        elif _('Search of') + ' [' in titulo:
            self.lugar = _('Search of') + ' [' + self.carpeta + ']'
        elif titulo != '':
            self.lugar = self.lugar + '/*/' + titulo
        retvalor = devUrlContenido(self.carpeta, nombretit=self.lugar, privado=self.privado, siforzar=forzar)
        self.modoarchivo = True
        if retvalor == None:
            self['textoinfo'].show()
            self['textoinfo'].setText('\n\n\n\n\n\n' + _('URL Request error. Check internet conection.') + '\n' + _('It is also possible that the download server is down, or that we are performing maintenance tasks.'))
            self.actualizaScrolls(True)
            self['listaA'].show()
            self['img_fondo'].show()
            listatemp = []
            listatemp.append(['<' + _('Retry') + '>',
             'd',
             'retry',
             None,
             None,
             None,
             None,
             None,
             None])
            listatemp.append(['<' + _('openPLI downloads').replace('openPLI', 'Enigma2') + '>',
             'd',
             '-3',
             None,
             None,
             None,
             None,
             None,
             None])
            self.listado = listatemp
            self['modo'].setText(' ' + _('URL Request error. Check internet conection.'))
            self.crealistado()
            self.num_archivos = 0
        else:
            if _('Search of') + ' [' in self.lugar:
                if len(retvalor[2]) <= 1:
                    self.session.open(MessageBox, _('No matches found for:') + '\n[' + self.carpeta + ']', MessageBox.TYPE_INFO, timeout=12)
                    abus = self.carpeta
                    self['modo'].setText(' ' + _('Search download') + ' :: ' + _('No matches found for:') + '\n[' + abus + ']')
                if len(retvalor[2]) > 60:
                    self.session.open(MessageBox, _('Found more than 60 matches.\nIt shows only the first 60 results.\nUse search terms more restrictive than') + ':\n[' + self.carpeta + ']', MessageBox.TYPE_INFO, timeout=15)
            self['listaA'].show()
            self['img_fondo'].show()
            self['textoinfo'].hide()
            self.vacio = False
            if len(self.lugar.split('/*/')) <= 3 and not forzar:
                anteriorlistado = [self.numcar, self.numarc, self.listado]
                self.numcar = retvalor[0]
                self.numarc = retvalor[1]
            self.num_archivos = retvalor[1]
            self.listado = retvalor[2]
            anadido = ''
            cinicio = ''
            if retvalor[0] > 0 and not carpeta == '' and not carpeta == '1':
                anadido = anadido + ' :: ' + str(retvalor[0]) + ' ' + _('Folder(s)') + ''
            if retvalor[1] > 0 and not carpeta == '' and not carpeta == '1':
                anadido = anadido + ' :: ' + str(retvalor[1]) + ' ' + _('File(s)') + ''
                dscc = ''
                if valor_ordenar == '':
                    dscc = 'Latest Downloads'
                elif valor_ordenar == 'votos':
                    dscc = 'Top Rated'
                elif valor_ordenar == 'descargas':
                    dscc = 'Top Downloads'
                elif valor_ordenar == 'nombre':
                    dscc = 'Name of download'
                if dscc != '':
                    anadido = anadido + ' | ' + _('by') + ' ' + _(dscc)
            if carpeta == '' or carpeta == '1':
                cinicio = ' ' + _('Home')
                if valor_ordenar == '':
                    anadido = ' :: ' + _('Recent Downloads')
                elif valor_ordenar == 'votos':
                    anadido = ' :: ' + _('Top Rated')
                elif valor_ordenar == 'descargas':
                    anadido = ' :: ' + _('Top Downloads')
                else:
                    anadido = ' :: ' + _('Recent Downloads')
            ertit = ' ' + cinicio + '' + self.formateatitulo(self.lugar) + anadido
            if ertit.strip().startswith('::'):
                ertit = ertit.strip()[2:]
            self['modo'].setText(ertit)
            self.titulo = ertit
        self.crealistado()

    def crealistado(self):
        list = []
        for i in range(0, len(self.listado)):
            if self.listado[i][1] == 'd':
                if self.carpeta == '-3' and self.listado[i][2] != '-1':
                    imagen = 'a-3'
                else:
                    imagen = 'd' + self.listado[i][2]
                texto = '' + self.listado[i][0]
                sinsta = False
                list.append(IniciaSelListEntryArchivo(texto, imagen, sinsta, self.listado[i][3], None, None, None))
            else:
                texto = '' + self.listado[i][3]
                imagen = 'a' + self.listado[i][1][1:]
                sinsta = False
                if quitaextension(self.listado[i][0]) in self.instalados:
                    sinsta = True
                list.append(IniciaSelListEntryArchivo(texto, imagen, sinsta, self.listado[i][4], self.listado[i][5], self.listado[i][6], self.listado[i][7]))

        self['listaA'].show()
        self['listaA'].setList(list)
        self['listaA'].selectionEnabled(1)
        self['img_fondo'].show()
        self.actualizaScrolls()
        self.muevesel()

    def muestrasat(self, asp, sufijo):
        if self.sisat:
            self.dessat()
            return

    def dessat(self):
        self.sisat = False
        self.actualizaScrolls()

    def mostrar(self):
        if not self.infomostrado:
            self.info_ini()
        if not self.iniciadoS:
            self.actualizaScrolls()

    def desins(self):
        if not self.bloqueado:
            self.instalando = False
            self['listaA'].show()
            self['textoinfo'].hide()
            self['img_fondo'].show()
            self['key_blue'].show()
            self['key_options'].show()
            self['modo'].setText(self.titulo)
            self.actualizaScrolls()
            self.muevesel()

    def bkey_ok(self):
        global listaini
        if self.bloqueado:
            return
        if self.sisat:
            self.dessat()
            return
        if self.nprivado == 3:
            self.TimerPrivado.stop()
            self.privado = True
            listaini = None
            self.buildList()
        elif self.vacio:
            self.buildList(self.carpeta, self.lugar)
        elif self.instalando:
            self.desins()
        else:
            nombrelista = 'listaA'
            lalista = self[nombrelista].list
            idx = self[nombrelista].getSelectionIndex()
            id = str(self.listado[idx][2])
            if id == '-1':
                self.buildList()
            elif id == '-2':
                self.buildList(id, self.listado[idx][0])
            elif id == 'retry':
                self.session.open(MessageBox, _('Retring server conection...'), MessageBox.TYPE_INFO, timeout=4)
                self.timerReload.startLongTimer(1)
            elif id == '-3':
                self.buildList('-3', _('openPLI downloads').replace('openPLI', 'Enigma2'))
            elif id == 'opman':
                self.abreopenpli('opman')
            elif id == 'opdwn':
                self.abreopenpli('opdwn')
            elif id == 'opsu':
                pass
            elif id == '0':
                self.buildList(id)
            elif self.listado[idx][1][0] == 'a':
                self.key_info()
            elif self.listado[idx][1] == 'd':
                if _('Search of') + ' [' in self.lugar:
                    self.lugar = '<' + _('Categories') + '>'
                anat = ''
                self.buildList(id, self.listado[idx][0])
        self.nprivado = 0

    def instalar(self, numero):
        archivoipk = self.listado[numero][3]
        if '-donsat-' in archivoipk and not fileExists('/usr/bin/chkds'):
            chequeamaks(self.url2)
            self.pontitulo()
            if fileExists('/usr/bin/vbinds'):
                self.privado = True
        dei = self.session.openWithCallback(self.callbackInstall, MessageBox, _('Do you want to install?') + '\n' + archivoipk, MessageBox.TYPE_YESNO)
        dei.setTitle(_('openSPA Downloads'))

    def callbackInstall(self, respuesta):
        if respuesta:
            if self.modoarchivo and not self.bloqueado:
                nombrelista = 'listaA'
                numero = self[nombrelista].getSelectionIndex()
                archivoipk = self.listado[numero][3]
                catego = self.listado[numero][1][1:]
                if catego == '15':
                    from Screens.ChoiceBox import ChoiceBox
                    possible_actions = []
                    rpicon = findPicon()
                    if not rpicon == None and rpicon != '':
                        possible_actions.append((rpicon, rpicon))
                    sp = [eEnv.resolve('${datadir}/enigma2/picon/'), '/media/cf/picon/', '/media/usb/picon/']
                    for path in sp:
                        if not rpicon == sp:
                            possible_actions.append((path, path))

                    if str(config.misc.picon_path.value) not in str(possible_actions):
                        possible_actions.append((str(config.misc.picon_path.value), str(config.misc.picon_path.value)))
                    possible_actions.append(('/tmp/picon/', '/tmp/picon/'))
                    self.session.openWithCallback(self.callbackInstallPicon, ChoiceBox, _('Select picon path to install'), possible_actions)
                else:
                    self.instalando = True
                    self.bloqueado = True
                    self['textoinfo'].show()
                    self['textoinfo'].setText('\n\n' + _('Wait...'))
                    self.actualizaScrolls(True)
                    self['listaA'].hide()
                    self['img_fondo'].hide()
                    self['key_red'].hide()
                    self['key_green'].hide()
                    self['img_red'].hide()
                    self['img_green'].hide()
                    self['key_blue'].hide()
                    self['key_options'].hide()
                    self['img_ok'].hide()
                    self['key_ok'].hide()
                    self.TimerTemp.start(self.tiempotimer, True)
                    self.paso = 1
                    self.pinfo = ''

    def callbackInstallPicon(self, respuesta):
        if respuesta:
            self.picon = respuesta[1]
            if self.modoarchivo and not self.bloqueado and self.picon:
                if self.picon == '/tmp/picon/':
                    os.system('rm /tmp/picon/*')
                    os.system('mkdir /tmp/picon')
                self.instalando = True
                self.bloqueado = True
                self['textoinfo'].show()
                self['textoinfo'].setText('\n\n' + _('Wait...'))
                self.actualizaScrolls(True)
                self['listaA'].hide()
                self['img_fondo'].hide()
                self['key_red'].hide()
                self['key_green'].hide()
                self['img_red'].hide()
                self['img_green'].hide()
                self['key_blue'].hide()
                self['key_options'].hide()
                self['key_yellow'].show()
                self['img_yellow'].show()
                self['img_ok'].hide()
                self['key_ok'].hide()
                self.TimerTemp.start(self.tiempotimer, True)
                self.paso = 1
                self.pinfo = ''

    def dataAvail(self, str):
        if self.paso == 20 or self.paso == 2:
            self.pinfo_cmd = self.pinfo_cmd + str.replace('\n', '\n   ')
        else:
            max = 5500
            arexto = self['textoinfo'].getText()
            str = str.replace('tmp/post_install_openSPA.sh', '----------------------')
            try:
                open('/tmp/dwn_install_openSPA.log', 'a').write(str)
            except:
                pass

            if len(arexto) > max:
                if '...\n   ' + _('Wait') + '...\n' in arexto:
                    arexto = arexto.replace('...\n   ' + _('Wait') + '...\n', '...\n   ' + _('Wait') + '\n')
                elif '...\n   ' + _('Wait') + '..\n' in arexto:
                    arexto = arexto.replace('...\n   ' + _('Wait') + '..\n', '...\n   ' + _('Wait') + '...\n')
                elif '...\n   ' + _('Wait') + '.\n' in arexto:
                    arexto = arexto.replace('...\n   ' + _('Wait') + '.\n', '...\n   ' + _('Wait') + '..\n')
                elif '...\n   ' + _('Wait') + '\n' in arexto:
                    arexto = arexto.replace('...\n   ' + _('Wait') + '\n', '...\n   ' + _('Wait') + '.\n')
                if self.pinfo_cmd == '':
                    self['textoinfo'].setText(arexto + '...\n   ' + _('Wait') + '...\n')
                else:
                    self['textoinfo'].setText(arexto)
                self['textoinfo'].lastPage()
                self.pinfo_cmd = self.pinfo_cmd + str.replace('\n', '\n   ')
            else:
                if self.pinfo_cmd == '*':
                    self.pinfo_cmd = ''
                    arexto = arexto + '   '
                if _('Installing...') + '>>>' in arexto:
                    arexto = arexto.replace(_('Installing...') + '>>>', _('Installing...') + '>')
                elif _('Installing...') + '>>' in arexto:
                    arexto = arexto.replace(_('Installing...') + '>>', _('Installing...') + '>>>')
                elif _('Installing...') + '>' in arexto:
                    arexto = arexto.replace(_('Installing...') + '>', _('Installing...') + '>>')
                self['textoinfo'].setText(arexto + str.replace('\n', '\n   '))
                self['textoinfo'].lastPage()

    def runFinished(self, retval):
        if retval:
            if self.paso == 2 or self.paso == 20:
                os.system('rm /tmp/' + self.listado[self['listaA'].getSelectionIndex()][0])
                self.pinfo = self.pinfo + '\n' + self.pinfo_cmd
                self.paso = 21
            else:
                self.pinfo_cmd = self.pinfo_cmd + '\n' + _('Process finished with some ERRORS') + ''
        else:
            self.pinfo_cmd = self.pinfo_cmd + '\n' + _('Process finished') + ''
        self.terminado = True

    def instalarok(self):
        self.TimerTemp.stop()
        rutapost = '/nadadenada'
        nombrelista = 'listaA'
        self['key_help'].setText(_('Please wait...'))
        numero = self[nombrelista].getSelectionIndex()
        catego = self.listado[numero][1][1:]
        if catego == '15':
            rutapost = self.picon + 'tmp/post_install_openSPA.sh'
        elif catego == '6':
            rutapost = '/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/image/tmp/post_install_openSPA.sh'
        elif catego == '9':
            rutapost = '/usr/share/enigma2/skin_default/spinner/tmp/post_install_openSPA.sh'
        else:
            rutapost = '/tmp/post_install_openSPA.sh'
        archivoipk = self.listado[numero][0]
        archivoremoto = URLXML + 'descargas/' + archivoipk
        self['modo'].setText(_('Installing...').replace('...', '') + ' ' + formateatexto(self.listado[numero][3]) + ' | ' + self.formateatitulo(self.lugar))
        comando1 = "wget '" + archivoremoto + "' -P /tmp/ -T 10"
        laextension = '.' + str(archivoipk.split('.')[-1])
        anacomando = ''
        self.actualizaScrolls(True)
        if archivoipk.endswith('.tar') or laextension[:3] == '.sp':
            if laextension[:4] == '.spz':
                anacomando = 'z'
            if catego == '15':
                comando2 = 'tar -x' + anacomando + "vf '/tmp/" + archivoipk + "' -C " + self.picon
            elif catego == '6':
                comando2 = 'tar -x' + anacomando + "vf '/tmp/" + archivoipk + "' -C /usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/image/"
            elif catego == '9':
                comando2 = 'tar -x' + anacomando + "vf '/tmp/" + archivoipk + "' -C /usr/share/enigma2/skin_default/spinner/"
            else:
                comando2 = 'tar -x' + anacomando + "vf '/tmp/" + archivoipk + "' -C /"
        else:
            comando2 = "opkg install --force-overwrite '/tmp/" + archivoipk + "'"
        comando3 = 'rm /tmp/' + archivoipk
        if self.paso == 1:
            self.paso = self.paso + 1
            self.pinfo = '\n\n' + _('Downloading') + ' [' + quitaextension(archivoipk) + '] - ' + Humanizer(self.listado[numero][4], False) + ' ' + '...'
            self['textoinfo'].setText(self.pinfo)
            self.actualizaScrolls(True)
            self.TimerTemp.start(self.tiempotimer, True)
        elif self.paso == 20:
            maxtiempo = 1200
            if self.terminado or self.t1 + maxtiempo < int(time.mktime(time.localtime())):
                if self.t1 + maxtiempo < int(time.mktime(time.localtime())):
                    self['textoinfo'].setText(self['textoinfo'].getText() + '\n*************** TIMEOUT!!! *****************\n')
                    self.runFinished(-1)
                else:
                    arexto = self.pinfo
                    textodescarga = Humanizer(self.listado[numero][4], False) + ' ' + _('of') + ' ' + Humanizer(self.listado[numero][4], False) + ' (100%)'
                    caddes = '-> ' + textodescarga + ''
                    self['textoinfo'].setText(arexto + '\n   ' + caddes)
                self.paso = 21
            elif fileExists('/tmp/' + archivoipk):
                try:
                    arexto = self.pinfo
                    textodescarga = ''
                    dir_stats = os.stat('/tmp/' + archivoipk)
                    textodescarga = textodescarga + Humanizer(dir_stats.st_size, False)
                    textodescarga = textodescarga + ' ' + _('of') + ' ' + Humanizer(self.listado[numero][4], False)
                    textodescarga = textodescarga + ' (' + str(int(dir_stats.st_size * 100 / int(self.listado[numero][4]))) + '%)'
                    caddes = '-> ' + textodescarga + ''
                    self['textoinfo'].setText(arexto + '\n   ' + caddes)
                except:
                    pass

            self.TimerTemp.start(self.tiempotimer, True)
        elif self.paso == 2:
            rest = ''
            self.pinfo_cmd = '*'
            self.t1 = int(time.mktime(time.localtime()))
            self.terminado = False
            os.system('rm /tmp/' + archivoipk)
            self.paso = 20
            cret = self.container.execute(comando1)
            self.TimerTemp.start(self.tiempotimer, True)
        elif self.paso == 21:
            if fileExists('/tmp/' + archivoipk):
                rest = cargaosinfo('chmod 755 /tmp/' + archivoipk, True)
                xret = anadedescarga(self.carpeta, self.listado[numero][2])
                self.paso = 3
                self.TimerTemp.start(self.tiempotimer, True)
            else:
                self.bloqueado = False
                self.pinfo = self.pinfo + '\n\n**********************************\n' + _('Error downloading') + '!!! ' + archivoipk + '\n**********************************\n' + _('Press [OK] or [EXIT] key to back.')
                self['textoinfo'].setText(self.pinfo)
                self['key_help'].setText(_(' '))
                self.actualizaScrolls(True)
                dei = self.session.open(MessageBox, _('Error downloading') + '!!!\n ' + quitaextension(archivoipk), MessageBox.TYPE_ERROR)
                dei.setTitle(_('openSPA') + ' ' + _('Installation'))
                os.system('rm /tmp/' + archivoipk)
        elif self.paso == 3:
            self.pinfo = self.pinfo + '[' + _('COMPLETED') + ']' + '\n\n' + _('Installing...') + '>>>' + '\n*******************************************************\n'
            self['textoinfo'].setText(self.pinfo)
            self.actualizaScrolls(True)
            self.paso = self.paso + 1
            self.TimerTemp.start(self.tiempotimer, True)
        elif self.paso == 41:
            maxtiempo = 480
            if self.terminado or self.t1 + maxtiempo < int(time.mktime(time.localtime())):
                if self.t1 + maxtiempo < int(time.mktime(time.localtime())):
                    self['textoinfo'].setText(self['textoinfo'].getText() + '\n*************** TIMEOUT!!! *****************\n')
                    self.runFinished(-1)
                self.paso = 42
            self.TimerTemp.start(self.tiempotimer, True)
        elif self.paso == 4:
            if fileExists('/tmp/' + archivoipk):
                self['textoinfo'].setText(self.pinfo)
                self.paso = self.paso + 1
                rest = ''
                self.pinfo_cmd = '*'
                self.t1 = int(time.mktime(time.localtime()))
                self.terminado = False
                self.paso = 41
                if catego == '9':
                    noret = cargaosinfo('rm /usr/share/enigma2/skin_default/spinner/wait*', True)
                try:
                    open('/tmp/dwn_install_openSPA.log', 'w').write(comando2.replace(archivoipk, quitaextension(archivoipk)) + '\n')
                except:
                    pass

                if fileExists(rutapost):
                    os.system('rm -f ' + rutapost)
                cret = self.container.execute(comando2)
                if cret:
                    self.runFinished(-1)
                self.TimerTemp.start(self.tiempotimer, True)
            else:
                self.pinfo = self.pinfo + '\n\n**********************************\n' + _('Error downloading') + '!!! ' + quitaextension(archivoipk) + '\n**********************************\n' + _('Press [OK] or [EXIT] key to back.')
                dei = self.session.open(MessageBox, _('Error downloading') + '!!!\n ' + quitaextension(archivoipk), MessageBox.TYPE_ERROR)
                dei.setTitle(_('openSPA') + ' ' + _('Installation'))
                self.bloqueado = False
                self['key_help'].setText(_(' '))
                self['textoinfo'].setText(self.pinfo)
                self.actualizaScrolls(True)
                os.system('rm /tmp/' + archivoipk)
        elif self.paso == 42:
            rest = self.pinfo_cmd
            if rest != '' and rest != '*' and len(rest) > 400:
                rest = rest[len(rest) - 400:]
            self.pinfo = self['textoinfo'].getText().replace(_('Installing...') + '>>>', _('Installing...') + '[' + _('COMPLETED') + ']').replace(_('Installing...') + '>>', _('Installing...') + '[' + _('COMPLETED') + ']').replace(_('Installing...') + '>', _('Installing...') + '[' + _('COMPLETED') + ']')
            self.pinfo = self.pinfo.replace('...\n   ' + _('Wait') + '..\n', '...\n   ...\n   ...').replace('...\n   ' + _('Wait') + '..\n', '...\n   ...\n   ...').replace('...\n   ' + _('Wait') + '.\n', '...\n   ...\n   ...').replace('...\n   ' + _('Wait') + '\n', '...\n   ...\n   ...')
            self.pinfo = self.pinfo + rest + '\n*******************************************************'
            self.pinfo = self.pinfo + '\n\n' + _('Finish...')
            self['textoinfo'].setText(self.pinfo)
            self['textoinfo'].lastPage()
            self.paso = 5
            self.TimerTemp.start(self.tiempotimer, True)
            self.actualizaScrolls(True)
        elif self.paso == 5:
            self.paso = 0
            cret = ''
            if fileExists(rutapost):
                os.system('chmod 755 ' + rutapost)
                cret = '\n' + cargaosinfo('sh ' + rutapost, True) + '\n'
                os.system('rm -f ' + rutapost)
            rest = cargaosinfo(comando3, True)
            self.pinfo = self.pinfo + '[' + _('COMPLETED') + ']' + cret + '\n' + _('Finished') + ' :: ' + _('Press [OK] or [EXIT] key to back, [YELLOW] key for restart GUI now.')
            idx = self['listaA'].getSelectionIndex()
            nombreipk = self.listado[idx][0]
            sinsta = False
            if quitaextension(nombreipk) in self.instalados:
                sinsta = True
            if not sinsta:
                self.instalados.append(quitaextension(nombreipk))
                booklist = None
                try:
                    booklist = open('/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/descargasSPZ/updated.txt', 'w')
                except:
                    pass

                ret = ''
                if booklist is not None:
                    for oneline in self.instalados:
                        booklist.write(oneline + '\n')

                    booklist.close()
            self.actualizadatolista('descarga', self.listado[numero][2])
            self.actualizaScrolls(True)
            self['listaA'].moveToIndex(numero)
            self['listaA'].hide()
            self['img_fondo'].hide()
            self['key_red'].hide()
            self['key_green'].hide()
            self['img_red'].hide()
            self['img_green'].hide()
            self['img_ok'].hide()
            self['key_ok'].hide()
            self['key_yellow'].show()
            self['img_yellow'].show()
            self['textoinfo'].show()
            anad = ''
            try:
                plugins.readPluginList(resolveFilename(SCOPE_PLUGINS))
            except:
                anad = '!!'

            anaf = ''
            ilog = ''
            if _('Process finished with some ERRORS') in self['textoinfo'].getText():
                anad = anad + '\n' + _('WARNING: Some ERRORS are detected.')
                ilog = '\n' + _('Installation log created in') + ': ' + '/tmp/dwn_install_openSPA.log'
                anaf = ' ' + _('Check the installation log for more information.') + ilog
                fininfo = _('Process finished') + anad
                ertime = 40
            else:
                fininfo = _('Installation Completed') + '\n' + _('Plugins and Extensions list has been reloaded, but') + ' ' + _('you may need restart GUI!') + anad
                ertime = 10
            self['textoinfo'].setText(self.pinfo)
            self['textoinfo'].lastPage()
            self['key_help'].setText(fininfo + ilog)
            dei = self.session.open(MessageBox, fininfo + anaf, MessageBox.TYPE_INFO, timeout=ertime)
            dei.setTitle(_('openSPA') + ' ' + _('Installation'))
            self.bloqueado = False
            self.actualizaScrolls(True)
            os.system('rm /tmp/' + archivoipk)

    def cbinfo(self, respuesta = None):
        if respuesta == 0:
            pass
        elif respuesta == 2:
            self.callbackInstall(True)
        elif respuesta == 1:
            self.votopositivo()
        elif respuesta == -1:
            self.votonegativo()

    def key_info(self):
        if self.sisat:
            self.dessat()
            return
        if self.vacio:
            return
        if self.bloqueado:
            return
        if self.instalando:
            self.instalando = False
            self['listaA'].show()
            self['textoinfo'].hide()
            self['img_fondo'].show()
            self.actualizaScrolls()
            self['modo'].setText(self.titulo)
        elif self.modoarchivo:
            nombrelista = 'listaA'
            try:
                lalista = self[nombrelista].list
                idx = self[nombrelista].getSelectionIndex()
                dei = self.session.openWithCallback(self.cbinfo, InfoArchivo, self, self.listado[idx])
                return
            except:
                pass

    def info_ini(self, forzar = False):
        global actualizarTXT
        intentos = 3
        html = None
        actualizarTXT = None
        for iji in range(intentos):
            arrhtml = devupdates(False)
            html = arrhtml[0]
            if not html == None:
                if arrhtml[1]:
                    actualizarTXT = arrhtml[1]
                break

        if not html == None:
            self.infomostrado = True
            siup = hayUpdates(actualizarTXT)
            if actualizarTXT == None:
                actualizarTXT = time.strftime('%d-%m-%Y %H:%M:%S', time.localtime())
            guardatxt()
            if siup or forzar:
                dei = self.session.open(InfoArchivo2, titulo=_('openSPA News'), textoinfo=html)
        elif forzar:
            msgx = _('URL Request error. Check internet conection.') + '\n' + _('It is also possible that the download server is down, or that we are performing maintenance tasks.')
            dei = self.session.open(MessageBox, msgx, MessageBox.TYPE_ERROR)
            dei.setTitle(_('openSPA Downloads'))

    def key_left(self):
        if self.sisat:
            self.dessat()
            return
        if self.vacio:
            pass
        if self.bloqueado:
            return
        if self.instalando:
            self['textoinfo'].pageUp()
            return
        self['listaA'].pageUp()

    def key_right(self):
        if self.sisat:
            self.dessat()
            return
        if self.vacio:
            pass
        if self.bloqueado:
            return
        if self.instalando:
            self['textoinfo'].pageDown()
            return
        self['listaA'].pageDown()

    def key_up(self):
        if self.sisat:
            self.dessat()
            return
        if self.vacio:
            return
        if self.bloqueado:
            return
        if self.instalando:
            self['textoinfo'].pageUp()
        else:
            nombrelista = 'listaA'
            try:
                lonlista = len(self[nombrelista].list) - 1
                idx = self[nombrelista].getSelectionIndex()
                if idx == 0:
                    self[nombrelista].moveToIndex(lonlista)
                else:
                    self[nombrelista].up()
            except:
                pass

    def key_down(self):
        if self.sisat:
            self.dessat()
            return
        if self.vacio:
            return
        if self.bloqueado:
            return
        if self.instalando:
            self['textoinfo'].pageDown()
        else:
            nombrelista = 'listaA'
            try:
                lonlista = len(self[nombrelista].list)
                idx = self[nombrelista].getSelectionIndex()
                if idx >= lonlista - 1:
                    self[nombrelista].moveToIndex(0)
                else:
                    self[nombrelista].down()
            except:
                pass

    def volver(self):
        if self.sisat:
            self.dessat()
            return
        if self.vacio:
            pass
        if self.bloqueado:
            return
        if self.instalando:
            self.desins()
        else:
            dei = self.session.openWithCallback(self.callbackSetSalir, MessageBox, _('Do you want to exit?'), MessageBox.TYPE_YESNO)
            dei.setTitle(_('openSPA Downloads'))

    def callbackSetSalir(self, respuesta):
        if respuesta:
            self.exit()

    def exit(self):
        global listaini
        global TimerMirar
        global listacarpetas
        global anteriorlistado
        if self.instalando:
            self.desins()
            return
        if self.sisat:
            self.dessat()
            return
        if config.misc.spazeupdates.value:
            try:
                TimerMirar = eTimer()
                TimerMirar.callback.append(revisasiupdates)
                TimerMirar.startLongTimer(43200)
                os.system('date > /etc/spzbk.log')
                wlog('iniciado log. proximo chequeo en 12 horas (43200 secs.)')
            except:
                pass

        else:
            os.system('date > /etc/spzbk.log')
            wlog('Iniciado log. Chequeo de updates desactivado.')
        listaini = None
        listacarpetas = None
        anteriorlistado = None
        self.close(True)


class ImagenDescargaItem():

    def __init__(self, url = '', filename = '', index = -1, error = False):
        self.url = url
        self.filename = filename
        self.index = index
        self.error = error


class ImagenDescarga(Pixmap):

    def __init__(self):
        Pixmap.__init__(self)
        self.IconFileName = ''
        self.picload = ePicLoad()
        self.picload.PictureData.get().append(self.paintIconPixmapCB)

    def onShow(self):
        Pixmap.onShow(self)
        sc = AVSwitch().getFramebufferScale()
        self.picload.setPara((self.instance.size().width(),
         self.instance.size().height(),
         sc[0],
         sc[0],
         0,
         0,
         '#00000000'))

    def paintIconPixmapCB(self, picInfo = None):
        ptr = self.picload.getData()
        if ptr != None:
            self.instance.setPixmap(ptr.__deref__())

    def updateIcon(self, filename):
        new_IconFileName = filename
        if self.IconFileName != new_IconFileName:
            self.IconFileName = new_IconFileName
            self.picload.startDecode(self.IconFileName)


textoch = ''

class chkUpdatesTira(Screen):
    if esHD():
        skin = '\n\t\t<screen name="chkUpdatesTira" position="0,635" size="1921,142" title="openSPA updates" flags="wfNoBorder" backgroundColor="#50000000">\t\t  \n\t\t\t\t\t<widget name="content" position="198,4" size="1411,76" valign="center" font="Regular; 19" transparent="1" backgroundColor="#000000" foregroundColor="#00ffffff" shadowColor="#000000" shadowOffset="-2,-2" />\n\t\t\t\t\t<widget name="rinfo" position="1635,18" size="232,40" font="Regular; 18" transparent="1" noWrap="1" zPosition="4" backgroundColor="#000000" foregroundColor="#006cbcf0" shadowColor="#000000" shadowOffset="-2,-2" halign="center" />\n\t\t\t\t\t<eLabel position="186,7" size="3,75" backgroundColor="#05252525" zPosition="2" />\n\t\t\t\t\t<eLabel position="1620,7" size="3,75" backgroundColor="#05252525" zPosition="2" />\n\t\t\t\t\t<ePixmap name="new ePixmap" position="75,12" size="100,67" zPosition="1" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/descargasSPZ/img/fondodescarga-fs8.png" alphatest="blend" />\n\t\t\t\t\t<widget name="ico_descarga" position="52,0" size="51,51" zPosition="4" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/descargasSPZ/img/ico_up.png" alphatest="blend" />\n\t\t\t\t\t<widget name="ico_spz" position="81,13" size="81,48" zPosition="3" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/descargasSPZ/img/icologo-fs8.png" alphatest="blend" />\n\t\t\t\t\t<eLabel name="new eLabel" position="0,0" size="1921,1" backgroundColor="#50202020" />\n\t\t</screen>'
    else:
        skin = '\n\t\t<screen name="chkUpdatesTira" position="0,635" size="1281,95" title="openSPA updates" flags="wfNoBorder" backgroundColor="#50000000">\t\t  \n\t\t\t\t\t<widget name="content" position="132,3" size="941,51" valign="center" font="Regular; 19" transparent="1" backgroundColor="#000000" foregroundColor="#00ffffff" shadowColor="#000000" shadowOffset="-2,-2" />\n\t\t\t\t\t<widget name="rinfo" position="1090,12" size="155,27" font="Regular; 18" transparent="1" noWrap="1" zPosition="4" backgroundColor="#000000" foregroundColor="#006cbcf0" shadowColor="#000000" shadowOffset="-2,-2" halign="center" />\n\t\t\t\t\t<eLabel position="124,5" size="2,50" backgroundColor="#05252525" zPosition="2" />\n\t\t\t\t\t<eLabel position="1080,5" size="2,50" backgroundColor="#05252525" zPosition="2" />\n\t\t\t\t\t  <ePixmap name="new ePixmap" position="50,8" size="67,45" zPosition="1" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/descargasSPZ/img/fondodescarga-fs8.png" alphatest="blend" />\n\t\t\t\t\t  <widget name="ico_descarga" position="35,0" size="34,34" zPosition="4" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/descargasSPZ/img/ico_up.png" alphatest="blend" />\n\t\t\t\t\t  <widget name="ico_spz" position="54,9" size="54,32" zPosition="3" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/descargasSPZ/img/icologo-fs8.png" alphatest="blend" />\n\t\t\t\t\t<eLabel name="new eLabel" position="0, 0" size="1281,1" backgroundColor="#50202020" />\n\t\t</screen>'

    def __init__(self, session):
        global textoch
        Screen.__init__(self, session)
        self.lista = []
        self['ico_descarga'] = Pixmap()
        self['ico_spz'] = Pixmap()
        self['content'] = Label()
        self['rinfo'] = Label(_('Downloads'))
        self.iniciado = False
        self['actions'] = ActionMap(['DirectionActions', 'MenuActions', 'OkCancelActions'], {'left': self.klef,
         'right': self.krig,
         'up': self.krig,
         'menu': self.cerrar,
         'down': self.klef,
         'ok': self.showCurrentEntry,
         'cancel': self.cerrarfin}, -2)
        self.lista.append(_('New openSPA udpdates found!!') + ' / ' + _('Press [OK] to go download manager'))
        temptexto = textoch
        arrtexto = temptexto.split('\n')
        cana = ''
        contaele = 8
        for ele in arrtexto:
            ele = ele.replace('\n', '').strip()
            if len(ele) > 5 and '------' not in ele:
                if '*' in ele[0:5]:
                    cana = '[*' + devStrTm(ele, '*', '') + '*] '
                else:
                    anadir = cana + ele
                    self.lista.append(anadir)
                    cana = ''
                    contaele = contaele - 1
                if contaele <= 0:
                    break

        self.timerRoll = eTimer()
        self.timerClose = eTimer()
        self.timerBlink = eTimer()
        self.timerRoll.callback.append(self.timerfeeds)
        self.timerClose.callback.append(self.cerrartimer)
        self.timerBlink.callback.append(self.blinkea)
        self.tamano = 0
        self.afeed = 0
        self.blink = False
        self.contavuelta = 0
        self.onLayoutFinish.append(self.inicia)

    def inicia(self):
        self['ico_descarga'].show()
        self['ico_spz'].hide()
        self.blinkea()
        self.verfeeds()

    def blinkea(self):
        return
        if self.blink == None:
            return
        if not self.blink:
            self['ico_descarga'].hide()
        else:
            self['ico_descarga'].show()
        self.blink = not self.blink
        self.timerBlink.start(800, True)

    def showCurrentEntry(self):
        self.timerClose.stop()
        self.timerRoll.stop()
        wlog('Mostrando descargas.')
        self.finblink()
        self.session.openWithCallback(self.cbnada, descargasSPZ)

    def cbnada(self, respuesta = None):
        self.close()

    def krig(self):
        self.timerRoll.stop()
        self.timerClose.stop()
        self.finblink()
        self.afeed = self.afeed + 1
        if self.afeed >= len(self.lista):
            self.afeed = 0
        self.verfeeds()

    def klef(self):
        self.timerRoll.stop()
        self.timerClose.stop()
        self.finblink()
        self.afeed = self.afeed - 1
        if self.afeed < 0:
            self.afeed = len(self.lista) - 1
        self.verfeeds()

    def timerfeeds(self):
        self.afeed = self.afeed + 1
        if self.afeed >= len(self.lista):
            self.afeed = 0
            self.contavuelta = self.contavuelta + 1
            if self.contavuelta >= 2:
                self.timerClose.startLongTimer(3)
            self.verfeeds()
        else:
            self.verfeeds()

    def verfeeds(self, fin = False):
        if self.afeed < len(self.lista):
            try:
                contenido = self.lista[self.afeed]
            except:
                self.cerrar()
                return

            if '[*' in contenido:
                textoinfo = devStrTm(contenido, '[*', '*]')
                contenido = devStrTm(contenido, '*] ', '')
                self['rinfo'].setText(textoinfo.encode('UTF-8'))
            if self.afeed == 0:
                self['rinfo'].setText(_('Downloads'))
            self['content'].setText(contenido.encode('UTF-8'))
        if not fin:
            self.timerRoll.startLongTimer(8)

    def finblink(self):
        self.timerBlink.stop()
        self['ico_descarga'].hide()
        self['ico_spz'].show()
        self.blink = None

    def cerrarfin(self):
        self.timerClose.stop()
        if config.misc.spazeupdates.value:
            dei = self.session.openWithCallback(self.cbcerrar, MessageBox, _('Want to remember this notice later?\nIf you choose No notification will be deleted.'), MessageBox.TYPE_YESNO)
            dei.setTitle(_('openSPA Downloads'))
        self.cerrar()

    def cbcerrar(self, resp = None):
        global TimerMirar
        if resp:
            wlog('Recordar notificacion. Proximo aviso spzdwn en 2 horas')
            retardaabrir(7200)
        else:
            self.finblink()
            TimerMirar = eTimer()
            TimerMirar.callback.append(revisasiupdates)
            TimerMirar.startLongTimer(43200)
            wlog('Cancelado por usuario. Proximo chequeo spzdwn en 12 horas (43200 secs.)')
            guardatxt()
            func_updates(True)
        self.cerrar()

    def cerrartimer(self):
        wlog('Usuario no responde. Proximo aviso spzdwn en 1 hora (3600 secs.)')
        retardaabrir(3600)
        self.cerrar()

    def cerrar(self):
        self.timerBlink.stop()
        self.timerRoll.stop()
        self.timerClose.stop()
        self.close()


class chkUpdates(Screen):
    if esHD():
        skin = ' <screen position="50,70" size="600,487" title="%s" > \n\t\t<widget name="respuesta" position="0,0" size="600,450"  zPosition="12" text=" " font="Regular; 19" />\n\t\t<ePixmap name="new ePixmap" position="7,450" size="52,37" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/descargasSPZ/img/green.png" alphatest="blend" transparent="1" />\n\t\t<widget name="key_green" position="58,451" size="600,33" transparent="1" text=" " font="Regular; 16"/>\n\t\t</screen>' % _('New udpdates!')
    else:
        skin = ' <screen position="50,70" size="400,325" title="%s" > \n\t\t<widget name="respuesta" position="0,0" size="400,300"  zPosition="12" text=" " font="Regular; 19" />\n\t\t<ePixmap name="new ePixmap" position="5,300" size="35,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/descargasSPZ/img/green.png" alphatest="blend" transparent="1" />\n\t\t<widget name="key_green" position="39,301" size="400,22" transparent="1" text=" " font="Regular; 16"/>\n\t\t</screen>' % _('New udpdates!')

    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session
        self.texto = ''
        trysleep = True
        self['respuesta'] = ScrollLabel('')
        self['key_green'] = Label('')
        self.texto = textoch + ' '
        self['setupActions'] = ActionMap(['WizardActions',
         'DirectionActions',
         'ColorActions',
         'NumberActions',
         'MenuActions',
         'EPGSelectActions',
         'InfobarActions'], {'green': self.abredescargas,
         'red': self.exit,
         'back': self.exit,
         'left': self.exit,
         'right': self.exit,
         'up': self.kup,
         'down': self.kdwn,
         'info': self.exit,
         'ok': self.exit}, -2)
        self.onLayoutFinish.append(self.mostrar)

    def mostrar(self):
        self['key_green'].setText(_('Open openSPA Download Manager'))
        self['respuesta'].setText(self.texto)

    def kup(self):
        self['respuesta'].pageUp()

    def kdwn(self):
        self['respuesta'].pageDown()

    def exit(self):
        global TimerMirar
        TimerMirar = eTimer()
        TimerMirar.callback.append(revisasiupdates)
        TimerMirar.startLongTimer(43200)
        wlog('Proximo chequeo en 12 horas (43200 secs.)')
        if not actualizarTXT == None:
            guardatxt()
        self.close()

    def goUpdates(self):
        try:
            self.session.open(MessageBox, _('New openSPA udpdates found!!') + '\n' + _('Go to openSPA Downloads plugin!!'), type=MessageBox.TYPE_INFO, timeout=20)
        except:
            self.TimerGoUpdates.startLongTimer(80)

    def abredescargas(self, respuesta = True):
        if respuesta:
            self.session.open(descargasSPZ)


def main(session, **kwargs):
    if not fileExists('/usr/bin/chkvs'):
        Notifications.AddPopup(text=_('Not openSPA image found!\nMore info in www.azboxhd.es'), type=MessageBox.TYPE_ERROR, timeout=10, id='spzDwnd')
    else:
        session.open(descargasSPZ)


from Components.Sources.spaUpdates import spaUpdates

def autostart(reason, **kwargs):
    global session
    os.system('date > /etc/spzbk.log')
    wlog('iniciado log (autostart)')
    if reason == 0 and kwargs.has_key('session') and fileExists('/usr/bin/chkvs'):
        session = kwargs['session']
        session.screen['spaUpdates'] = spaUpdates(session)
        revisasiupdates()


def hayUpdates(texto):
    global actualizarTXT
    if not fileExists('/etc/updates.txt'):
        t3 = time.localtime()
        erano = int(time.strftime('%Y', t3))
        if erano >= 2012:
            actualizarTXT = time.strftime('%d-%m-%Y %H:%M:%S', time.localtime())
            guardatxt()
        return False
    if texto == None:
        return False
    if texto == '':
        return False
    hayupdates = False
    if fileExists('/etc/updates.txt'):
        try:
            udes = open('/etc/updates.txt', 'r').read()
        except:
            return False

        tguardado = udes.replace('\n', '')
        ultimoupdate = texto
        try:
            t1 = time.mktime(time.strptime(tguardado, '%d-%m-%Y %H:%M:%S'))
        except:
            t1 = 0

        try:
            t2 = time.mktime(time.strptime(ultimoupdate, '%d-%m-%Y %H:%M:%S'))
            hayupdates = t2 > t1
        except:
            pass

    return hayupdates


def revisasiupdates():
    global TimerMirar
    global textoch
    global actualizarTXT
    if not config.misc.spazeupdates.value:
        return
    if not fileExists('/usr/bin/OpenSPA.info'):
        TimerMirar = eTimer()
        TimerMirar.callback.append(revisasiupdates)
        TimerMirar.startLongTimer(14400)
        wlog('Autostart. No existe openSpa.info, Proximo chequeo en 4 horas (14400 secs.)')
        return
    html = None
    arrhtml = devupdates()
    ufecha = arrhtml[1]
    html = arrhtml[0]
    actualizarTXT = None
    siup = False
    if not html == None:
        siup = hayUpdates(ufecha)
        if ufecha == None:
            actualizarTXT = time.strftime('%d-%m-%Y %H:%M:%S', time.localtime())
        else:
            actualizarTXT = ufecha
    if siup:
        textoch = html
        wlog('Autostart. Nuevos cambios encontrados.')
        retardaabrir(180)
        func_updates(True)
    else:
        TimerMirar = eTimer()
        TimerMirar.callback.append(revisasiupdates)
        TimerMirar.startLongTimer(43200)
        wlog('Autostart. Sin cambios. Proximo chequeo en 12 horas (43200 secs.)')
        func_updates(False)


def guardatxt(valor = None):
    global actualizarTXT
    booklist = None
    if actualizarTXT == None and valor == None:
        return
    if actualizarTXT == '' and valor == None:
        return
    try:
        booklist = open('/etc/updates.txt', 'w')
    except:
        wlog('updates.txt no guardado (Error)')

    if booklist is not None:
        if not valor == None:
            booklist.write(valor)
        else:
            booklist.write(actualizarTXT)
        booklist.close()
        wlog('updates.txt actualizado OK')
        actualizarTXT = None
        func_updates(False)


def mostrarNotificacion():
    NOTIFICATIONID = 'spzchkUpdates'
    from Tools.Notifications import AddNotificationWithID, RemovePopup
    try:
        RemovePopup(NOTIFICATIONID)
    except:
        pass

    AddNotificationWithID(NOTIFICATIONID, chkUpdatesTira)


def abreinfochk():
    ok = None
    try:
        mostrarNotificacion()
        ok = 1
    except Exception as e:
        wlog('spzdwnd no mostrado (ERROR). ' + e.message)
        ok = None

    if ok == None:
        retardaabrir(3600)
        wlog('Posponiendo notificacion 1 hora (3600 secs.)')


def retardaabrir(tiempo = 400):
    global TimerGoUpdates
    TimerGoUpdates = eTimer()
    TimerGoUpdates.callback.append(abreinfochk)
    TimerGoUpdates.startLongTimer(tiempo)
    wlog('retardando mostrar notificacion ' + str(tiempo / 60 / 60) + ' hora(s) (' + str(tiempo) + ' secs.)')
