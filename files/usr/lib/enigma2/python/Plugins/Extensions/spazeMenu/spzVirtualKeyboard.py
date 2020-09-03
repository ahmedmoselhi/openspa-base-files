from Components.Label import Label
from Components.MenuList import MenuList
from Components.MultiContent import MultiContentEntryText
from enigma import eListboxPythonMultiContent, gFont, RT_HALIGN_LEFT, RT_VALIGN_CENTER
from enigma import eTimer, getPrevAsciiCode, eRCInput
from Components.Pixmap import Pixmap
from Tools.LoadPixmap import LoadPixmap
from enigma import eSize, ePoint
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap
from Screens.ChoiceBox import ChoiceBox
from Components.config import config
from Tools import Notifications
import os
from time import localtime, time, strftime
from Tools.Directories import fileExists, resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE
from Components.Language import language
from Plugins.Extensions.spazeMenu.sbar import openspaSB
from Plugins.Extensions.spazeMenu.plugin import esHD
from os import environ
import gettext
lang = language.getLanguage()
environ['LANGUAGE'] = lang[:2]
lenguaje = str(lang[:2])
gettext.bindtextdomain('enigma2', resolveFilename(SCOPE_LANGUAGE))
gettext.textdomain('enigma2')
gettext.bindtextdomain('szpVirtualKeyboard', '%s%s' % (resolveFilename(SCOPE_PLUGINS), 'Extensions/spazeMenu/locale/'))

def _(txt):
    t = gettext.dgettext('szpVirtualKeyboard', txt)
    if t == txt:
        t = gettext.gettext(txt)
    return t


def savefilerecent(lista, anadir = None):
    try:
        booklist = open('/etc/tuxbox/virtualKeyboard_recent.conf', 'w')
    except:
        pass

    if booklist is not None:
        if not anadir == None:
            booklist.write(anadir.encode('UTF-8') + '\n')
        existe = False
        conta = 1
        for elemento in lista:
            if elemento[0] == anadir:
                existe = True
            else:
                booklist.write(elemento[0] + '\n')
                conta = conta + 1
            if conta > 50:
                break

        booklist.close()


def getfilerecent():
    list = []
    booklist = None
    if not fileExists('/etc/tuxbox/virtualKeyboard_recent.conf'):
        return list
    list = []
    try:
        booklist = open('/etc/tuxbox/virtualKeyboard_recent.conf', 'r')
    except:
        pass

    if booklist is not None:
        for oneline in booklist:
            cadena = oneline.replace('\n', '')
            if not cadena == '':
                list.append(cadena)

        booklist.close()
    return list


def devpredicion(letra = None, lista1 = None):
    listapred = ['http://',
     'http://www.',
     'www.',
     'http://www.azboxhd.es',
     '/hdd/',
     '/hdd/movie/',
     '/etc/',
     'spazeTeam',
     _('Sport'),
     _('Film'),
     _('Comedy'),
     _('Series'),
     _('Terror'),
     _('Adventure'),
     _('Drama'),
     _('Documentary'),
     _('Music'),
     _('Science fiction'),
     _('Entertainment'),
     _('Cinema'),
     _('Soccer'),
     _('Basketball'),
     _('Backup'),
     _('Monday'),
     _('Tuesday'),
     _('Wednesday'),
     _('Thursday'),
     _('Friday'),
     _('Saturday'),
     _('Sunday')]
    try:
        erpat = str(config.usage.default_path.value)
        if erpat not in str(listapred):
            listapred.append(erpat)
    except:
        pass

    if letra:
        letra = letra.encode('UTF-8')
    t2 = localtime()
    cfecha = str(strftime('%d/%m/%Y', t2))
    erpat = _('Backup') + '_' + cfecha.replace('/', '-')
    listapred.append(erpat)
    listapred.append(cfecha)
    cfecha = str(strftime('%d/%m/%Y %H:%M', t2))
    erpat = _('Backup') + '_' + cfecha.replace('/', '-').replace(':', '.').replace(' ', '_')
    listapred.append(erpat)
    listapred.append(cfecha)
    cdia = str(strftime('%d', t2))
    cmes = str(strftime('%B', t2))
    cano = str(strftime('%Y', t2))
    csemana = str(strftime('%A', t2))
    hora = str(strftime('%H:%M', t2))
    cfecha = _(csemana) + ', ' + cdia + '/' + _(cmes) + '/' + cano
    erpat = _('Backup') + '_' + cfecha.replace('/', '-').replace(', ', '-')
    listapred.append(erpat)
    listapred.append(cfecha)
    listapred.append(erpat + '_' + hora.replace(':', '.'))
    listapred.append(cfecha + ' ' + hora)
    if lista1 == None:
        lista1 = []
    listaret = []
    for iji in lista1:
        if letra == None or iji[0][0:len(letra)].upper() == letra.upper():
            listaret.append(iji[0])

    for iji in listapred:
        if iji not in listaret:
            if letra == None or iji[0:len(letra)].upper() == letra.upper():
                listaret.append(iji)

    listaret.sort(key=lambda x: x.lower())
    return listaret


class vkEntryListPred(MenuList):

    def __init__(self, list, enableWrapAround = True):
        MenuList.__init__(self, list, enableWrapAround, eListboxPythonMultiContent)
        self.l.setFont(0, gFont('Regular', 17))
        self.l.setFont(1, gFont('Regular', 20))

    def postWidgetCreate(self, instance):
        MenuList.postWidgetCreate(self, instance)
        instance.setItemHeight(20)

    def getCurrentIndex(self):
        return self.instance.getCurrentIndex()

    def buildList(self, letra = None, listat = None):
        listat = devpredicion(letra, listat)
        self.list = []
        for x in listat:
            texto2 = x
            res = [x]
            if not letra == None:
                longi = len(letra)
                texto1 = x[0:longi] + '\xc2\xb7'
                texto2 = texto1
                if len(x) > 1:
                    texto2 = texto2 + x[longi:]
            res.append((eListboxPythonMultiContent.TYPE_TEXT,
             5,
             0,
             350,
             20,
             0,
             RT_HALIGN_LEFT | RT_VALIGN_CENTER,
             texto2))
            self.list.append(res)

        self.l.setList(self.list)
        self.moveToIndex(0)


class vkEntryList(MenuList):

    def __init__(self, list, enableWrapAround = True):
        MenuList.__init__(self, list, enableWrapAround, eListboxPythonMultiContent)
        self.l.setFont(0, gFont('Regular', 17))
        self.l.setFont(1, gFont('Regular', 20))

    def postWidgetCreate(self, instance):
        MenuList.postWidgetCreate(self, instance)
        if esHD():
            instance.setItemHeight(30)
        else:
            instance.setItemHeight(20)

    def getCurrentIndex(self):
        return self.instance.getCurrentIndex()

    def buildList(self):
        listat = getfilerecent()
        self.list = []
        for x in listat:
            res = [x]
            if esHD():
                res.append((eListboxPythonMultiContent.TYPE_TEXT,
                 8,
                 0,
                 525,
                 30,
                 0,
                 RT_HALIGN_LEFT | RT_VALIGN_CENTER,
                 x))
            else:
                res.append((eListboxPythonMultiContent.TYPE_TEXT,
                 5,
                 0,
                 350,
                 20,
                 0,
                 RT_HALIGN_LEFT | RT_VALIGN_CENTER,
                 x))
            self.list.append(res)

        self.l.setList(self.list)
        self.moveToIndex(0)


class spzVirtualKeyboard(Screen):
    skin = '\n\t\t<screen name="spzVirtualKeyboard" position="263,140" size="953,503" title="Virtual Keyboard" flags="wfNoBorder" backgroundColor="#ff000000" zPosition="99">\n\t\t\t<ePixmap name="imagenfondo" position="0,0" size="752,354" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/teclado-fs8.png" zPosition="-10" alphatest="off" />\n\t\t\t<widget name="imagenfondo2" position="0,354" size="577,129" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/teclado2-fs8.png" zPosition="-7" alphatest="blend" />\n\t\t\t<widget name="titulo" position="42,12" size="696,24" transparent="1" text="spzVirtualKeyboard" font="Regular; 18" foregroundColor="#dedede" backgroundColor="#000000" noWrap="1" shadowColor="#000000" shadowOffset="-2,-2" />\n\t\t\t<widget name="tapa_texto" position="10,40" size="731,3" transparent="0" backgroundColor="#ffffff" zPosition="-5" />\n\t\t\t<widget name="tapa_texto2" position="10,140" size="731,3" transparent="0" backgroundColor="#ffffff" zPosition="-5" />\n\t\t\t<widget name="key_texto" position="14,47" size="724,88" transparent="0" text=" " valign="top" halign="left" font="Console; 18" foregroundColor="#ffffff" backgroundColor="#1e1e1e" />\n\t\t\t<!--<widget name="key_texto0" position="14,47" size="724,88" transparent="1" text=" " valign="top" halign="left" font="Console; 18" foregroundColor="#ffffff" backgroundColor="#1e1e1e" zPosition="1"/>-->\n\t\t\t<!-- teclas -->\n\t\t\t<!-- fila 1 -->\n\t\t\t<widget name="key_1" position="11,147" size="55,32" transparent="1" text="1" valign="bottom" halign="center" font="Regular; 26" foregroundColor="#000000" backgroundColor="#ffffff" zPosition="22" />\n\t\t\t<widget name="key_2" position="67,147" size="55,32" transparent="1" text="2" valign="bottom" halign="center" font="Regular; 26" foregroundColor="#000000" backgroundColor="#ffffff" zPosition="22" />\n\t\t\t<widget name="key_3" position="123,147" size="55,32" transparent="1" text="3" valign="bottom" halign="center" font="Regular; 26" foregroundColor="#000000" backgroundColor="#ffffff" zPosition="22" />\n\t\t\t<widget name="key_4" position="179,147" size="55,32" transparent="1" text="4" valign="bottom" halign="center" font="Regular; 26" foregroundColor="#000000" backgroundColor="#ffffff" zPosition="22" />\n\t\t\t<widget name="key_5" position="235,147" size="55,32" transparent="1" text="5" valign="bottom" halign="center" font="Regular; 26" foregroundColor="#000000" backgroundColor="#ffffff" zPosition="22" />\n\t\t\t<widget name="key_6" position="291,147" size="55,32" transparent="1" text="6" valign="bottom" halign="center" font="Regular; 26" foregroundColor="#000000" backgroundColor="#ffffff" zPosition="22" />\n\t\t\t<widget name="key_7" position="347,147" size="55,32" transparent="1" text="7" valign="bottom" halign="center" font="Regular; 26" foregroundColor="#000000" backgroundColor="#ffffff" zPosition="22" />\n\t\t\t<widget name="key_8" position="403,147" size="55,32" transparent="1" text="8" valign="bottom" halign="center" font="Regular; 26" foregroundColor="#000000" backgroundColor="#ffffff" zPosition="22" />\n\t\t\t<widget name="key_9" position="459,147" size="55,32" transparent="1" text="9" valign="bottom" halign="center" font="Regular; 26" foregroundColor="#000000" backgroundColor="#ffffff" zPosition="22" />\n\t\t\t<widget name="key_10" position="515,147" size="55,32" transparent="1" text="0" valign="bottom" halign="center" font="Regular; 26" foregroundColor="#000000" backgroundColor="#ffffff" zPosition="22" />\n\t\t\t<!-- fila 2 -->\n\t\t\t<widget name="key_11" position="11,185" size="55,32" transparent="1" text="q" valign="bottom" halign="center" font="Regular; 26" foregroundColor="#000000" backgroundColor="#ffffff" zPosition="22" />\n\t\t\t<widget name="key_12" position="67,185" size="55,32" transparent="1" text="w" valign="bottom" halign="center" font="Regular; 26" foregroundColor="#000000" backgroundColor="#ffffff" zPosition="22" />\n\t\t\t<widget name="key_13" position="123,185" size="55,32" transparent="1" text="e" valign="bottom" halign="center" font="Regular; 26" foregroundColor="#000000" backgroundColor="#ffffff" zPosition="22" />\n\t\t\t<widget name="key_14" position="179,185" size="55,32" transparent="1" text="r" valign="bottom" halign="center" font="Regular; 26" foregroundColor="#000000" backgroundColor="#ffffff" zPosition="22" />\n\t\t\t<widget name="key_15" position="235,185" size="55,32" transparent="1" text="t" valign="bottom" halign="center" font="Regular; 26" foregroundColor="#000000" backgroundColor="#ffffff" zPosition="22" />\n\t\t\t<widget name="key_16" position="291,185" size="55,32" transparent="1" text="y" valign="bottom" halign="center" font="Regular; 26" foregroundColor="#000000" backgroundColor="#ffffff" zPosition="22" />\n\t\t\t<widget name="key_17" position="347,185" size="55,32" transparent="1" text="u" valign="bottom" halign="center" font="Regular; 26" foregroundColor="#000000" backgroundColor="#ffffff" zPosition="22" />\n\t\t\t<widget name="key_18" position="403,185" size="55,32" transparent="1" text="i" valign="bottom" halign="center" font="Regular; 26" foregroundColor="#000000" backgroundColor="#ffffff" zPosition="22" />\n\t\t\t<widget name="key_19" position="459,185" size="55,32" transparent="1" text="o" valign="bottom" halign="center" font="Regular; 26" foregroundColor="#000000" backgroundColor="#ffffff" zPosition="22" />\n\t\t\t<widget name="key_20" position="515,185" size="55,32" transparent="1" text="p" valign="bottom" halign="center" font="Regular; 26" foregroundColor="#000000" backgroundColor="#ffffff" zPosition="22" />\n\t\t\t<!-- fila 3 -->\n\t\t\t<widget name="key_21" position="11,223" size="55,32" transparent="1" text="a" valign="bottom" halign="center" font="Regular; 26" foregroundColor="#000000" backgroundColor="#ffffff" zPosition="22" />\n\t\t\t<widget name="key_22" position="67,223" size="55,32" transparent="1" text="s" valign="bottom" halign="center" font="Regular; 26" foregroundColor="#000000" backgroundColor="#ffffff" zPosition="22" />\n\t\t\t<widget name="key_23" position="123,223" size="55,32" transparent="1" text="d" valign="bottom" halign="center" font="Regular; 26" foregroundColor="#000000" backgroundColor="#ffffff" zPosition="22" />\n\t\t\t<widget name="key_24" position="179,223" size="55,32" transparent="1" text="f" valign="bottom" halign="center" font="Regular; 26" foregroundColor="#000000" backgroundColor="#ffffff" zPosition="22" />\n\t\t\t<widget name="key_25" position="235,223" size="55,32" transparent="1" text="g" valign="bottom" halign="center" font="Regular; 26" foregroundColor="#000000" backgroundColor="#ffffff" zPosition="22" />\n\t\t\t<widget name="key_26" position="291,223" size="55,32" transparent="1" text="h" valign="bottom" halign="center" font="Regular; 26" foregroundColor="#000000" backgroundColor="#ffffff" zPosition="22" />\n\t\t\t<widget name="key_27" position="347,223" size="55,32" transparent="1" text="j" valign="bottom" halign="center" font="Regular; 26" foregroundColor="#000000" backgroundColor="#ffffff" zPosition="22" />\n\t\t\t<widget name="key_28" position="403,223" size="55,32" transparent="1" text="k" valign="bottom" halign="center" font="Regular; 26" foregroundColor="#000000" backgroundColor="#ffffff" zPosition="22" />\n\t\t\t<widget name="key_29" position="459,223" size="55,32" transparent="1" text="l" valign="bottom" halign="center" font="Regular; 26" foregroundColor="#000000" backgroundColor="#ffffff" zPosition="22" />\n\t\t\t<widget name="key_30" position="515,223" size="55,32" transparent="1" text="\xc3\xb1" valign="bottom" halign="center" font="Regular; 26" foregroundColor="#000000" backgroundColor="#ffffff" zPosition="22" />\n\t\t\t<!-- fila 4 -->\n\t\t\t<widget name="key_31" position="11,261" size="55,32" transparent="1" text="z" valign="bottom" halign="center" font="Regular; 26" foregroundColor="#000000" backgroundColor="#ffffff" zPosition="22" />\n\t\t\t<widget name="key_32" position="67,261" size="55,32" transparent="1" text="x" valign="bottom" halign="center" font="Regular; 26" foregroundColor="#000000" backgroundColor="#ffffff" zPosition="22" />\n\t\t\t<widget name="key_33" position="123,261" size="55,32" transparent="1" text="c" valign="bottom" halign="center" font="Regular; 26" foregroundColor="#000000" backgroundColor="#ffffff" zPosition="22" />\n\t\t\t<widget name="key_34" position="179,261" size="55,32" transparent="1" text="v" valign="bottom" halign="center" font="Regular; 26" foregroundColor="#000000" backgroundColor="#ffffff" zPosition="22" />\n\t\t\t<widget name="key_35" position="235,261" size="55,32" transparent="1" text="b" valign="bottom" halign="center" font="Regular; 26" foregroundColor="#000000" backgroundColor="#ffffff" zPosition="22" />\n\t\t\t<widget name="key_36" position="291,261" size="55,32" transparent="1" text="n" valign="bottom" halign="center" font="Regular; 26" foregroundColor="#000000" backgroundColor="#ffffff" zPosition="22" />\n\t\t\t<widget name="key_37" position="347,261" size="55,32" transparent="1" text="m" valign="bottom" halign="center" font="Regular; 26" foregroundColor="#000000" backgroundColor="#ffffff" zPosition="22" />\n\t\t\t<widget name="key_38" position="403,261" size="55,32" transparent="1" text="," valign="bottom" halign="center" font="Regular; 26" foregroundColor="#000000" backgroundColor="#ffffff" zPosition="22" />\n\t\t\t<widget name="key_39" position="459,261" size="55,32" transparent="1" text="." valign="bottom" halign="center" font="Regular; 26" foregroundColor="#000000" backgroundColor="#ffffff" zPosition="22" />\n\t\t\t<widget name="key_40" position="515,261" size="55,32" transparent="1" text="-" valign="bottom" halign="center" font="Regular; 26" foregroundColor="#000000" backgroundColor="#ffffff" zPosition="22" />\n\t\t\t<!-- especiales -->\n\t\t\t<widget name="key_stop" position="230,320" size="65,18" transparent="1" text="espacio" font="Regular; 14" foregroundColor="#000066" backgroundColor="#ffffff" noWrap="1" halign="center" zPosition="22" />\n\t\t\t<widget name="key_play" position="286,320" size="65,18" transparent="1" text="ABC" font="Regular; 14" foregroundColor="#000066" backgroundColor="#ffffff" noWrap="1" halign="center" zPosition="22" />\n\t\t\t<widget name="key_red" position="342,320" size="65,18" transparent="1" text="Borrar" font="Regular; 14" foregroundColor="#000066" backgroundColor="#ffaaaa" noWrap="1" halign="center" zPosition="22" />\n\t\t\t<widget name="key_green" position="398,311" size="65,18" transparent="1" text="OK" font="Regular; 15" foregroundColor="#000066" backgroundColor="#aaffaa" noWrap="1" halign="center" zPosition="22" />\n\t\t\t<widget name="key_yellow" position="454,311" size="65,18" transparent="1" text="Limpiar" font="Regular; 14" foregroundColor="#000066" backgroundColor="#ffffff" noWrap="1" halign="center" zPosition="22" />\n\t\t\t<widget name="key_blue" position="510,311" size="65,18" transparent="1" text="#@&amp;:" font="Regular; 15" foregroundColor="#000066" backgroundColor="#aaaaff" noWrap="1" halign="center" zPosition="22" />\n\t\t\t<!-- teclado -->\n\t\t\t<widget name="key_teclado1" position="14,356" size="182,36" transparent="1" text="abcABC" valign="center" halign="center" font="Regular; 20" foregroundColor="#ffffff" backgroundColor="#000000" />\n\t\t\t<widget name="key_teclado2" position="200,356" size="182,36" transparent="1" text="abcABC" valign="center" halign="center" font="Regular; 20" foregroundColor="#ffffff" backgroundColor="#000000" />\n\t\t\t<widget name="key_teclado3" position="385,356" size="182,36" transparent="1" text="abcABC" valign="center" halign="center" font="Regular; 20" foregroundColor="#ffffff" backgroundColor="#000000" />\n\t\t\t<widget name="key_teclado4" position="14,395" size="182,36" transparent="1" text="abcABC" valign="center" halign="center" font="Regular; 20" foregroundColor="#ffffff" backgroundColor="#000000" />\n\t\t\t<widget name="key_teclado5" position="200,395" size="182,36" transparent="1" text="abcABC" valign="center" halign="center" font="Regular; 20" foregroundColor="#ffffff" backgroundColor="#000000" />\n\t\t\t<widget name="key_teclado6" position="385,395" size="182,36" transparent="1" text="abcABC" valign="center" halign="center" font="Regular; 19" foregroundColor="#ffffff" backgroundColor="#000000" />\n\t\t\t<widget name="key_teclado7" position="14,435" size="182,36" transparent="1" text="abcABC" valign="center" halign="center" font="Regular; 20" foregroundColor="#ffffff" backgroundColor="#000000" />\n\t\t\t<widget name="key_teclado8" position="200,435" size="182,36" transparent="1" text="abcABC" valign="center" halign="center" font="Regular; 20" foregroundColor="#ffffff" backgroundColor="#000000" />\n\t\t\t<widget name="key_teclado9" position="385,435" size="182,36" transparent="1" text="abcABC" valign="center" halign="center" font="Regular; 20" foregroundColor="#ffffff" backgroundColor="#000000" />\n\t\t\t\n\t\t\t<widget name="seleccion" position="4,141" size="67,49" transparent="1" alphatest="blend" zPosition="20" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/seleccion-fs8.png" />\n\n\t\t\t<widget name="key_record" position="567,320" size="65,18" transparent="1" text="Hist." font="Regular; 14" foregroundColor="#000066" backgroundColor="#aaaaff" noWrap="1" halign="center" zPosition="22" />\n\t\t\t<widget name="key_delete" position="622,313" size="65,18" transparent="1" text="Delete" font="Regular; 14" foregroundColor="#000066" backgroundColor="#aaffaa" noWrap="1" halign="center" zPosition="22" />\n\t\t\t<widget name="key_clear" position="679,313" size="65,18" transparent="1" text="Clear" font="Regular; 14" foregroundColor="#000066" backgroundColor="#aaffaa" noWrap="1" halign="center" zPosition="22" />\n\t\t\t\n\t\t\t<widget name="cajalista" position="573,146" size="380,333" transparent="0" backgroundColor="#ffffff" zPosition="39" />\n\t\t\t<widget name="lista" position="580,152" size="153,140" transparent="0" scrollbarMode="showOnDemand" zPosition="40" />\n\t\t\t<widget name="listapred" position="580,152" size="153,140" transparent="0" scrollbarMode="showOnDemand" zPosition="41" />\n\t\t\t\n\t\t\t<widget name="text_info" position="9,39" size="733,305" transparent="0" foregroundColor="#ffffff" backgroundColor="#000000" font="Regular; 22" zPosition="50" />\n\t\t\t\t\t\n\t\t\t<eLabel name="ayu" position="0,354" size="752,30" backgroundColor="#000000" zPosition="-9" />\n\t\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/menu.png" position="10,356" size="35,25" transparent="1" alphatest="blend" zPosition="-8" />\n\t\t\t<widget name="in_menu" position="45,356" size="185,25" font="Regular; 16" valign="center" halign="left" transparent="1" foregroundColor="#ffffff" backgroundColor="#000000" zPosition="-8" />\n\n\t\t\t<widget name="in_green" position="177,356" size="570,25" font="Regular; 16" valign="center" halign="right" transparent="1" foregroundColor="#bebebe" text="Ayuda" backgroundColor="#000000" zPosition="-8" noWrap="1"/>\n\t\t<widget name="barrapix_arr" position="0,0" zPosition="42" size="20,20" alphatest="blend" transparent="1" />\n\t\t<widget name="barrapix_abj" position="0,0" zPosition="42" size="20,20" alphatest="blend" transparent="1" />\t\t\t\n\t\t</screen>'

    def __init__(self, session, titulo = _('Type the text'), texto = '', caracteres = None, guardarvalor = True, ok = False, obj = None):
        Screen.__init__(self, session)
        self.texto = texto
        try:
            self.texto = self.texto.encode('UTF-8').decode('UTF-8')
        except:
            try:
                self.texto = self.texto.decode('windows-1252').encode('utf-8').decode('UTF-8')
            except:
                pass

        self.devolver = texto
        self.titulo = titulo
        self.novalidos = None
        self.validos = None
        if caracteres == '[FILE]':
            self.validos = '0123456789\nabcdefghijklmn\xc3\xb1opqrstuvwxyz\nABCDEFGHIJKLMN\xc3\x91OPQRSTUVWXYZ\n@#._  &-][)(}{\xc3\xa1\xc3\xa9\xc3\xad\xc3\xb3\xc3\xba\xc3\xbc'
        elif caracteres == '[FILESIMPLE]':
            self.validos = '0123456789\nabcdefghijklmnopqrstuvwxyz\nABCDEFGHIJKLMNOPQRSTUVWXYZ\n._-'
        elif caracteres:
            self.validos = caracteres.replace('(tab)', '\xc2\xac')
        if self.validos:
            try:
                if self.validos[0] == '-':
                    self.validos = None
                    self.novalidos = caracteres[1:].replace('(tab)', '\xc2\xac')
            except:
                pass

        self.guardarvalor = guardarvalor
        self['titulo'] = Label()
        self.obj = None
        self['key_texto'] = Label()
        self['key_stop'] = Label()
        self['key_play'] = Label()
        self['key_red'] = Label()
        self['key_green'] = Label()
        self['key_yellow'] = Label()
        self['key_blue'] = Label()
        self['text_info'] = Label(' ')
        self['tapa_texto'] = Label()
        self['tapa_texto2'] = Label()
        self['cajalista'] = Label()
        self['in_menu'] = Label()
        self['in_green'] = Label()
        self['key_record'] = Label()
        self['key_delete'] = Label()
        self['key_clear'] = Label()
        self['lista'] = vkEntryList([])
        self['listapred'] = vkEntryListPred([])
        self.eninfo = False
        for i in range(1, 41):
            try:
                self['key_' + str(i)] = Label()
            except:
                pass

        for i in range(1, 10):
            try:
                self['key_teclado' + str(i)] = Label()
            except:
                pass

        self['seleccion'] = Pixmap()
        self['imagenfondo2'] = Pixmap()
        self.timerCursor = eTimer()
        self.blink = True
        self.timerBlink = eTimer()
        self.timerBlink.callback.append(self.esperaletra)
        self.timerWindow = eTimer()
        self.timerWindow.callback.append(self.ocultaletras)
        self.numero = None
        self.letraespera = None
        self.oculto = False
        self.lastmarked = ''
        self.valorfuente = 19
        self.predicion = False
        self.entexto = False
        self.carsep = '\xc2\xa4'
        self.carsep2 = '|'
        self.carsep1 = '\xe2\x80\xa2'
        self.altolista = 0
        self.ancholista = 0
        self['sVKactions'] = ActionMap(['spzVirtualKeyboard'], {'green': self.keygreen,
         'blue': self.keyblue,
         'yellow': self.keyyellow,
         'cancel': self.Exit,
         'left': self.keyleft,
         'right': self.keyright,
         'up': self.keyup,
         'down': self.keydown,
         'ok': self.save,
         'info': self.muestrainfo,
         'historic': self.activalista,
         'borrared': self.keyred,
         'deleteBackward': self.keyred2,
         'deleteForward': self.keyred2,
         'home': self.keyred2,
         'space': self.espacio,
         'caps': self.mayus,
         'end': self.mayus,
         'fontd': self.difuente,
         'fontu': self.aufuente,
         'nextMarker': self.muevecursor,
         'prevMarker': self.muevecursort,
         'nextBouquet': self.muevecursorr,
         'prevBouquet': self.muevecursorl,
         'seekBack': self.muevecursorl,
         'seekFwd': self.muevecursorr,
         'menu': self.menu,
         'gotAsciiCode': self.gotAsciiCode,
         'enter': self.keyenter}, -1)
        self['actions'] = ActionMap(['NumberActions'], {'1': self.key1,
         '2': self.key2,
         '3': self.key3,
         '4': self.key4,
         '5': self.key5,
         '6': self.key6,
         '7': self.key7,
         '8': self.key8,
         '9': self.key9,
         '0': self.key0}, -2)
        if obj:
            self.obj = obj
            try:
                obj['config_actions'] = self['sVKactions']
            except:
                pass

        self.posicion = 1
        if ok and len(texto) > 0:
            self.posicion = 49
        self.teclado = 0
        self.mayusculas = 0
        self.cursor = 0
        self.nocursor = False
        self.tiempocursor = 1100
        self.onLayoutFinish.append(self.inicio)
        self.nletras = 0
        self.curasc = 0
        self.historico = False
        self.letras = ['1234567890qwertyuiopasdfghjkl\xc3\xb1zxcvbnm._-', '1234567890QWERTYUIOPASDFGHJKL\xc3\x91ZXCVBNM;:,', '@#$%&/\\*=+\xc3\xa1\xc3\xa9\xc3\xad\xc3\xb3\xc3\xba\xc3\xbc\xc2\xba\xc2\xaa\xc3\x87\xc3\xa7()\xc2\xbf?\xc2\xa1![]{}<>\xc3\xa0\xc3\xa8\xc3\xac\xc3\xb2\xc3\xb9"' + "'\xc2\xac"]
        self.ayudas = {'-1': _('Use numeric keypad or use the cursor keys and press OK'),
         '0': _('Use left/right keys to move cursor(x), also [CH-]/[CH+]'),
         '1': _('Use cursor keys to move and press OK to insert'),
         '41': _('Press OK to move cursor(x) left [CH-]'),
         '42': _('Press OK to move cursor(x) right [CH+]'),
         '43': _('Move cursor(x) to beginning of text [|<<]'),
         '44': _('Move cursor(x) to end of text [>>|]'),
         '45': _('Insert space at cursor(x) position [STOP]'),
         '46': _('Switch uppercase/lowercase [PAUSE]'),
         '47': _('Delete right char of cursor(x)/Use Back/Del(<-) to Del left char'),
         '48': _('Return value and Close'),
         '49': _('Clear text'),
         '50': _('Change to special characters'),
         '51': _('Activate the list of recent texts [REC]'),
         '52': _('Deletes the selected item from the list'),
         '53': _('Delete the entire list'),
         '60': _('Use [>>] for increase text size'),
         '61': _('Use [<<] for decrease text size')}
        self.onShow.append(self.iniscroll)
        self.onExecBegin.append(self.setKeyboardModeAscii)
        self.iniciadoS = False
        self['barrapix_arr'] = Pixmap()
        self['barrapix_abj'] = Pixmap()

    def iniscroll(self):
        if not self.iniciadoS:
            self.actualizaScrolls()
            self.iniciadoS = True

    def actualizaScrolls(self):
        if not self.predicion:
            openspaSB(objectoself=self, nombrelista='lista', barra='barrapix', altoitem=20, imagen=True)
        else:
            openspaSB(objectoself=self, nombrelista='listapred', barra='barrapix', altoitem=20, imagen=True)

    def ponayuda(self, numero = None, text = None):
        self['in_green'].setText(self.devayuda(num=numero, texto=text).replace('(x)', '(' + self.carsep1 + ')'))

    def devayuda(self, num = None, texto = None):
        if not texto == None:
            return texto
        elif num == None:
            return ' '
        if num >= 1 and num <= 40:
            num = 1
        cnum = str(num)
        if cnum in self.ayudas:
            return self.ayudas[cnum]
        else:
            return ' '

    def cambiacursor(self):
        pass

    def detencursor(self):
        pass

    def menu(self):
        if self.eninfo:
            self.muestrainfo()
            return
        nkeys = ['0',
         'green',
         'yellow',
         'blue',
         '1',
         '2',
         '3',
         '4',
         '5',
         '6']
        possible_actions = [(_('Cancel and Close') + ' [EXIT]', 'exit'),
         (_('Return value and Close'), 'save'),
         (_('Clear text'), 'clear'),
         (_('Change to special characters'), 'chr'),
         (_('Recovery initial text'), 'reco'),
         (_('Expanded text Display') + ' [INFO]', 'info'),
         (_('Increase text size') + ' [>>]', 'ch1'),
         (_('Decrease text size') + ' [<<]', 'ch2'),
         (_('Change to historic list') + ' [Rec]', 'his'),
         (_('Hotkeys help') + '', 'help')]
        if len(self.devactual()) > 0:
            possible_actions.append(('--', ''))
            nkeys.append('')
            possible_actions.append((_('Copy text to clipboard') + '', 'copy'))
            nkeys.append('7')
        tclip = self.devclip()
        if len(tclip) > 0:
            if not len(self.devactual()) > 0:
                possible_actions.append(('--', ''))
                nkeys.append('')
            if len(tclip) > 20:
                tclip = tclip[:17] + '...'
            tclip = ' (' + tclip + ')'
            possible_actions.append((_('Paste text') + tclip, 'paste'))
            nkeys.append('8')
        self.session.openWithCallback(self.cbmenu, ChoiceBox, keys=nkeys, title=_('VirtualKeyboard') + ' - ' + _('Options'), list=possible_actions)

    def devclip(self, texto = None):
        if texto == None:
            cadena = ''
            booklist = None
            try:
                booklist = open('/tmp/clipboard', 'r')
            except:
                pass

            if booklist is not None:
                for oneline in booklist:
                    cadena = oneline.replace('\n', '')
                    break

                booklist.close()
            return cadena.replace('\n', '')
        booklist = None
        try:
            booklist = open('/tmp/clipboard', 'w')
        except:
            pass

        if booklist is not None:
            booklist.write(texto)
            booklist.close()

    def cbmenu(self, result):
        if result:
            if result[1] == 'exit':
                self.Exit(True)
            elif result[1] == 'save':
                self.keygreen()
            elif result[1] == 'clear':
                self.keyyellow()
            elif result[1] == 'chr':
                self.keyblue()
            elif result[1] == 'info':
                self.muestrainfo()
            elif result[1] == 'ch1':
                self.cambiafuente(2)
                self.ponayuda(60)
            elif result[1] == 'ch2':
                self.cambiafuente(-2)
                self.ponayuda(61)
            elif result[1] == 'his':
                self.activalista()
            elif result[1] == 'help':
                self.about()
            elif result[1] == 'copy':
                self.detencursor()
                xtexto = self.devactual().encode('UTF-8')
                self.devclip(xtexto)
            elif result[1] == 'paste':
                texto = self.devclip()
                if texto and len(texto) > 0:
                    try:
                        self.pontexto(texto.decode('UTF-8'))
                    except:
                        pass

            elif result[1] == 'reco':
                self.session.openWithCallback(self.cbreco, MessageBox, _('Recovery the initial text?') + '\n' + _('All changes will be lost!'))

    def cbreco(self, resp):
        if resp:
            self['key_texto'].setText(self.texto.encode('UTF-8') + self.carsep1.encode('UTF-8'))
            self.cursor = len(self.texto)

    def aufuente(self):
        self.cambiafuente(1)

    def difuente(self):
        self.cambiafuente(-1)

    def cambiafuente(self, cuanto):
        self.valorfuente = self.valorfuente + cuanto
        try:
            self['key_texto'].instance.setFont(gFont('Console', self.valorfuente))
        except:
            self.valorfuente = self.valorfuente - cuanto

    def about(self):
        cmens = '[' + _('Red') + ']: ' + _('Backspace (delete left char)')
        cmens = cmens + '\n[' + _('Green') + ']: ' + _('Return value and Close')
        cmens = cmens + '\n[' + _('Yellow') + ']: ' + _('Clear text')
        cmens = cmens + '\n[' + _('Blue') + ']: ' + _('Change to special characters')
        cmens = cmens + '\n[' + 'CH-' + ']: ' + _('Move cursor to left')
        cmens = cmens + '\n[' + 'CH+' + ']: ' + _('Move cursor to right')
        cmens = cmens + '\n[' + _('|<') + ']: ' + _('Go top')
        cmens = cmens + '\n[' + _('>|') + ']: ' + _('Go end')
        cmens = cmens + '\n[' + 'Info' + ']: ' + _('Expanded text Display')
        cmens = cmens + '\n[' + 'Exit' + ']: ' + _('Cancel and Close')
        cmens = cmens + '\n[' + 'Rec' + ']: ' + _('Change to historic list')
        cmens = cmens + '\n[' + 'Play/Pause' + ']: ' + _('Change to upper/lower chars')
        cmens = cmens + '\n[' + 'Stop' + ']: ' + _('Insert space char')
        dei = self.session.open(MessageBox, cmens, MessageBox.TYPE_INFO)
        dei.setTitle('spazeTeam :: ' + _('VirtualKeyboard') + ' :: ' + _('Hotkeys help'))

    def nextasc(self):
        self.curasc = self.curasc + 1
        if self.curasc >= 2:
            self.curasc = 0
        try:
            if self.curasc == 0:
                self.carsep = '|'
            if self.curasc == 1:
                self.carsep = '\xc2\xa4'
        except:
            pass

    def gotAsciiCode(self):
        if self.eninfo:
            self.muestrainfo()
            return
        try:
            gprev = getPrevAsciiCode()
            unichar = unichr(gprev)
            charstr = unichar.encode('utf-8')
            if int(gprev) >= 48 and int(gprev) <= 57:
                self.ponletra(int(gprev) - 48)
                return
            if not self.entexto:
                self.activatexto()
            self.pontexto(charstr)
        except:
            self.pontexto('x')

    def blinkFunc(self):
        self.blink = not self.blink

    def devactual(self):
        actual = self['key_texto'].getText().decode('UTF-8')
        if len(actual) == 1:
            actual = ''
        else:
            tactual = actual[0:self.cursor]
            try:
                tactual = tactual + actual[self.cursor + 1:]
            except:
                pass

            actual = tactual
        actual = actual.replace(self.carsep1.decode('UTF-8'), '')
        return actual

    def activapredicion(self, letra):
        sihay = False
        self['listapred'].buildList(letra, self['lista'].list)
        if len(self['listapred'].list) > 0:
            sihay = True
        if sihay:
            self.predicion = True
            self['listapred'].show()
            self.actualizaScrolls()
        else:
            self.desactivapredicion()

    def desactivapredicion(self):
        if self.predicion:
            self['listapred'].hide()
        self.predicion = False
        self.actualizaScrolls()

    def pontexto(self, quetexto = None):
        self.detencursor()
        actual = self.devactual()
        if quetexto == None:
            try:
                quetexto = self['key_' + str(self.posicion)].getText().decode('UTF-8')
                if quetexto == '\xc2\xa0':
                    return
                if quetexto == '\xc2\xb7tab':
                    quetexto = '\xc2\xac'.decode('UTF-8')
            except:
                return

        if quetexto == '' or len(quetexto) == 0:
            return
        if not quetexto == None:
            if not self.validos == None:
                if len(quetexto) == 1 and quetexto not in self.validos:
                    cmens = _('No valid character for this context!') + '[' + quetexto.encode('UTF-8') + ']'
                    cmens = cmens + '\n' + _('Valid characters are:')
                    cmens = cmens + '\n' + self.validos
                    dei = self.session.open(MessageBox, cmens, MessageBox.TYPE_ERROR)
                    dei.setTitle(_('Character not allowed'))
                    return
            if not self.novalidos == None:
                if len(quetexto) == 1 and quetexto in self.novalidos.decode('UTF-8'):
                    cmens = _('No valid character for this context!') + '[' + quetexto.encode('UTF-8') + ']'
                    cmens = cmens + '\n' + _('Some characters are not valid:')
                    cmens = cmens + '\n' + self.novalidos
                    dei = self.session.open(MessageBox, cmens, MessageBox.TYPE_ERROR)
                    dei.setTitle(_('Character not allowed'))
                    return
            if len(actual) <= 1 and len(quetexto) == 1:
                self.activapredicion(actual + quetexto)
            else:
                self.desactivapredicion()
        else:
            self.desactivapredicion()
        if self.cursor == len(actual):
            ertexto = actual + quetexto + self.carsep1
            ertexto2 = actual + quetexto + self.carsep2
            self.cursor = len(ertexto) - 1
        elif self.cursor == 0:
            ertexto = self.carsep1 + quetexto + actual
            ertexto2 = self.carsep2 + quetexto + actual
        else:
            ertexto = actual[0:self.cursor]
            ertexto2 = ertexto + quetexto + self.carsep2
            ertexto = ertexto + quetexto + self.carsep1
            try:
                ertexto = ertexto + actual[self.cursor:]
                ertexto2 = ertexto2 + actual[self.cursor:]
            except:
                pass

            self.cursor = self.cursor + len(quetexto)
        self['key_texto'].setText(ertexto.encode('UTF-8'))

    def muestrainfo(self):
        if self.eninfo:
            self['text_info'].hide()
            self.ponayuda()
        else:
            self.ocultaletras()
            self.detencursor()
            xtexto = self.devactual()
            ertexto = xtexto
            self['text_info'].setText(ertexto.encode('UTF-8'))
            self['text_info'].show()
            self.ponayuda(text=_('Press [OK] or [INFO] to go back'))
        self.eninfo = not self.eninfo

    def inicio(self):
        self.cambiafuente(0)
        self.ancholista = self['lista'].instance.size().width()
        self.altolista = self['lista'].instance.size().height()
        self['in_green'].setText(_(' '))
        self['in_menu'].setText(_('Options') + '...')
        self['listapred'].hide()
        self['tapa_texto'].hide()
        self['tapa_texto2'].hide()
        self['text_info'].hide()
        self['key_record'].setText(_('Recent'))
        self['key_delete'].setText(_('Delete'))
        self['key_clear'].setText(_('Clear'))
        self['key_stop'].setText(_('space'))
        self['key_red'].setText(_('Del'))
        self['key_yellow'].setText(_('Clear'))
        self['key_green'].setText(_('OK'))
        self['key_teclado1'].setText('1 .:/-_@'.encode('UTF-8'))
        self['key_teclado2'].setText('2abc\xc3\xa1\xc3\xa0ABC\xc3\x81\xc3\x80'.encode('UTF-8'))
        self['key_teclado3'].setText('3de\xc3\xa9\xc3\xa8fDEF\xc3\x89\xc3\x88'.encode('UTF-8'))
        self['key_teclado4'].setText('4ghi\xc3\xad\xc3\xacGHI\xc3\x8d\xc3\x8c'.encode('UTF-8'))
        self['key_teclado5'].setText('5jklJKL'.encode('UTF-8'))
        self['key_teclado6'].setText('6mn\xc3\xb1o\xc3\xb3\xc3\xb2MN\xc3\x91O\xc3\x93\xc3\x92'.encode('UTF-8'))
        self['key_teclado7'].setText('7pqrsPQRS'.encode('UTF-8'))
        self['key_teclado8'].setText('8tuv\xc3\xba\xc3\xb9TUV\xc3\x9a\xc3\x99'.encode('UTF-8'))
        self['key_teclado9'].setText('9wxyzWXYZ'.encode('UTF-8'))
        self.ocultaletras()
        self['titulo'].setText(self.titulo)
        self.texto = self.texto.replace('\t', '\xc2\xac')
        self['key_texto'].setText(self.texto.encode('UTF-8') + self.carsep1.encode('UTF-8'))
        self['lista'].buildList()
        self['cajalista'].hide()
        self.cursor = len(self.texto)
        self.ponletras(0)
        self.ponayuda(-1)
        if not fileExists('/usr/bin/chkvs'):
            Notifications.AddPopup(text=_('Not spazeTeam image found!\nMore info in www.azboxhd.es'), type=MessageBox.TYPE_ERROR, timeout=10, id='szpVirtualKeyboard')
            self.close(None)
        self.cambiacursor()
        if self.posicion != 1:
            self.mueveimg(1)

    def ponletras(self, numero = 0):
        if self.eninfo:
            self.muestrainfo()
            return
        self.ocultaletras()
        self.nletras = numero
        cadena = self.letras[self.nletras]
        conta = 1
        for i in cadena.decode('UTF-8'):
            err = False
            elcar = i
            try:
                cvalido = True
                if self.validos:
                    if elcar not in self.validos:
                        elcar = '\xc2\xa0'
                if not self.novalidos == None:
                    if elcar in self.novalidos:
                        elcar = '\xc2\xa0'
                if elcar == '\xc2\xac':
                    self['key_' + str(conta)].setText('\xc2\xb7tab')
                else:
                    self['key_' + str(conta)].setText(elcar.encode('UTF-8'))
            except:
                err = True

            conta = conta + 1

    def keyred(self):
        if self.eninfo:
            self.muestrainfo()
            return
        self.detencursor()
        actual = self.devactual()
        quetexto1 = ''
        quetexto2 = ''
        try:
            if self.cursor > 0:
                quetexto1 = actual[0:self.cursor]
            elif self.cursor == 0:
                quetexto1 = ''
        except:
            pass

        try:
            quetexto2 = actual[self.cursor + 1:]
        except:
            pass

        if True:
            self['key_texto'].setText(quetexto1.encode('UTF-8') + self.carsep1.encode('UTF-8') + quetexto2.encode('UTF-8'))
            act = quetexto1.encode('UTF-8') + quetexto2.encode('UTF-8')
            if len(act) >= 1 and len(act) <= 2:
                self.activapredicion(act)
            else:
                self.desactivapredicion()

    def keyred2(self):
        if self.eninfo:
            self.muestrainfo()
            return
        self.detencursor()
        actual = self.devactual()
        quetexto1 = ''
        quetexto2 = ''
        try:
            if self.cursor > 1:
                quetexto1 = actual[0:self.cursor - 1]
            elif self.cursor == 1:
                quetexto1 = ''
        except:
            pass

        try:
            quetexto2 = actual[self.cursor:]
        except:
            pass

        if True:
            if quetexto1 + quetexto2 != actual:
                self.cursor = self.cursor - 1
            self['key_texto'].setText(quetexto1.encode('UTF-8') + self.carsep1.encode('UTF-8') + quetexto2.encode('UTF-8'))
            act = quetexto1.encode('UTF-8') + quetexto2.encode('UTF-8')
            if len(act) >= 1 and len(act) <= 2:
                self.activapredicion(act)
            else:
                self.desactivapredicion()

    def keygreen(self):
        if self.eninfo:
            self.muestrainfo()
            return
        self.detencursor()
        txt = self.devactual()
        if self.guardarvalor:
            savefilerecent(self['lista'].list, txt)
        txt = txt.replace('\xc2\xac', '\t')
        self.timerBlink.callback.remove(self.esperaletra)
        self.timerWindow.callback.remove(self.ocultaletras)
        self.timerCursor = None
        self.timerBlink = None
        self.timerWindow = None
        if self.obj:
            self.obj.VirtualKeyBoardCallback(txt)
        else:
            self.close(txt.encode('UTF-8'))

    def keyblue(self):
        if self.eninfo:
            self.muestrainfo()
            return
        self.ocultaletras()
        if self.nletras == 2:
            self.ponletras(0)
        else:
            self['key_play'].setText('abc')
            self.ponletras(2)

    def keyenter(self):
        if self.eninfo:
            self.muestrainfo()
            return
        self.session.openWithCallback(self.cbent, MessageBox, _('Return value and Close') + '?')

    def cbent(self, resp):
        if resp:
            self.keygreen()

    def keyyellow(self):
        if self.eninfo:
            self.muestrainfo()
            return
        self.session.openWithCallback(self.cbyel, MessageBox, _('Really clear the text?'))

    def cbyel(self, resp):
        if resp:
            self.desactivapredicion()
            self['key_texto'].setText(self.carsep1.encode('UTF-8'))
            self.cursor = 0

    def keyleft(self):
        if self.eninfo:
            self.muestrainfo()
            return
        if self.historico:
            if self.predicion:
                self['listapred'].pageUp()
            else:
                self['lista'].pageUp()
        elif self.entexto:
            self.muevecursorl()
        else:
            self.mueveimg(1)

    def keyright(self):
        if self.eninfo:
            self.muestrainfo()
            return
        if self.historico:
            if self.predicion:
                self['listapred'].pageDown()
            else:
                self['lista'].pageDown()
        elif self.entexto:
            self.muevecursorr()
        else:
            self.mueveimg(2)

    def keyup(self):
        if self.eninfo:
            self.muestrainfo()
            return
        if self.historico:
            if self.predicion:
                self['listapred'].up()
            else:
                self['lista'].up()
        elif self.posicion > 50:
            self.activalista()
        elif self.posicion <= 10 or self.entexto:
            self.activatexto(0)
        else:
            self.mueveimg(3)

    def keydown(self):
        if self.eninfo:
            self.muestrainfo()
            return
        if self.historico:
            if self.predicion:
                self['listapred'].down()
            else:
                self['lista'].down()
        elif self.posicion > 50:
            self.activalista()
        elif self.posicion > 40 or self.entexto:
            self.activatexto(1)
        else:
            self.mueveimg(4)

    def espacio(self):
        if self.eninfo:
            self.muestrainfo()
            return
        self.pontexto(' ')

    def muevecursorl(self):
        self.muevecursor(-1)

    def muevecursorr(self):
        self.muevecursor(1)

    def muevecursort(self):
        self.muevecursor(0)

    def save(self):
        if self.entexto:
            self.activatexto()
            return
        if self.eninfo:
            self.muestrainfo()
            return
        if not self.oculto:
            self.esperaletra()
            return
        if self.historico:
            if self.predicion:
                try:
                    sel = self['listapred'].l.getCurrentSelection()[0]
                    self.cbyel(True)
                    self.pontexto(sel.decode('UTF-8'))
                    self.desactivapredicion()
                    self.activalista()
                except:
                    pass

            else:
                try:
                    sel = self['lista'].l.getCurrentSelection()[0]
                    self.pontexto(sel.decode('UTF-8'))
                    self.activalista()
                except:
                    pass

            return
        if self.posicion <= 40:
            self.pontexto()
        elif self.posicion == 41:
            self.muevecursor(-1)
        elif self.posicion == 42:
            self.muevecursor(1)
        elif self.posicion == 43:
            self.muevecursor(0)
        elif self.posicion == 44:
            self.muevecursor()
        elif self.posicion == 45:
            self.espacio()
        elif self.posicion == 46:
            self.mayus()
        elif self.posicion == 47:
            self.keyred()
        elif self.posicion == 48:
            self.keygreen()
        elif self.posicion == 49:
            self.keyyellow()
        elif self.posicion == 50:
            self.keyblue()
        elif self.posicion == 51:
            self.activalista()
        elif self.posicion == 52:
            self.borra()
        elif self.posicion == 53:
            self.limpia()

    def activatexto(self, dire = None):
        if self.eninfo:
            self.muestrainfo()
            return
        self.entexto = not self.entexto
        if self.entexto:
            self['seleccion'].hide()
            self['tapa_texto'].show()
            self['tapa_texto2'].show()
            self.ponayuda(0)
        else:
            if not dire == None:
                if dire == 0:
                    if self.posicion <= 10:
                        self.mueveimg(3)
                elif self.posicion > 40:
                    self.mueveimg(4)
            self.ponayuda(self.posicion)
            self['seleccion'].show()
            self['tapa_texto'].hide()
            self['tapa_texto2'].hide()

    def activalista(self):
        if self.eninfo:
            self.muestrainfo()
            return
        self.ocultaletras()
        self.historico = not self.historico
        lalista = self['lista'].list
        if len(lalista) <= 0 and not self.predicion:
            self.historico = False
        if self.historico:
            if esHD():
                temp = (int(self.ancholista * 1.5 + 205), int(self.altolista * 1.5 + 160))
            else:
                temp = (self.ancholista + 215, self.altolista + 180)
            self['lista'].instance.resize(eSize(*temp))
            self['listapred'].instance.resize(eSize(*temp))
            self['tapa_texto'].hide()
            self['tapa_texto2'].hide()
            self.entexto = False
            self['seleccion'].hide()
            self['cajalista'].show()
            self['in_green'].hide()
        else:
            temp = (self.ancholista, self.altolista)
            self['lista'].instance.resize(eSize(*temp))
            self['listapred'].instance.resize(eSize(*temp))
            self['cajalista'].hide()
            self['seleccion'].show()
            self['in_green'].show()
        self.actualizaScrolls()

    def mayus(self):
        if self.eninfo:
            self.muestrainfo()
            return
        self.ocultaletras()
        if self.nletras > 0:
            self['key_play'].setText('ABC')
            self.ponletras(0)
        else:
            self['key_play'].setText('abc')
            self.ponletras(1)

    def limpia(self):
        if self.eninfo:
            self.muestrainfo()
            return
        if self.predicion:
            self.desactivapredicion()
            return
        lalista = self['lista'].list
        if len(lalista) <= 0:
            return
        self.session.openWithCallback(self.cblimpia, MessageBox, _('Really clear the history list?'))

    def cblimpia(self, respuesta):
        if self.eninfo:
            self.muestrainfo()
            return
        if respuesta:
            os.system('rm /etc/tuxbox/virtualKeyboard_recent.conf')
            self['lista'].buildList()

    def borra(self):
        if self.eninfo:
            self.muestrainfo()
            return
        if self.predicion:
            self.desactivapredicion()
            return
        lalista = self['lista'].list
        if len(lalista) <= 0:
            return
        lis2 = []
        actual = self['lista'].l.getCurrentSelection()[0]
        for ii in lalista:
            if ii[0] != actual:
                lis2.append(ii)

        savefilerecent(lis2, None)
        self['lista'].buildList()

    def muevecursor(self, pos = None):
        self.detencursor()
        ertexto = self.devactual()
        if pos == 0:
            self.cursor = 0
        elif pos == None:
            self.cursor = len(ertexto)
        else:
            self.cursor = self.cursor + pos
        if self.cursor < 0:
            self.cursor = len(ertexto)
        if self.cursor > len(ertexto):
            self.cursor = 0
        texto1 = ''
        texto2 = ''
        try:
            texto1 = ertexto[0:self.cursor]
        except:
            pass

        try:
            texto2 = ertexto[self.cursor:]
        except:
            pass

        self['key_texto'].setText(texto1.encode('UTF-8') + self.carsep1.encode('UTF-8') + texto2.encode('UTF-8'))

    def actualizacursor(self):
        return
        ertexto = self.devactual()
        if self.cursor < 0:
            self.cursor = 0
        if self.cursor > len(ertexto):
            self.cursor = len(ertexto)
        texto1 = ''
        texto2 = ''
        try:
            texto1 = ertexto[0:self.cursor]
        except:
            pass

        try:
            texto2 = ertexto[self.cursor:]
        except:
            pass

        self['key_texto'].setText(texto1.encode('UTF-8') + self.carsep.encode('UTF-8') + texto2.encode('UTF-8'))

    def mueveimg(self, direccion):
        if self.eninfo:
            self.muestrainfo()
            return
        self.detencursor()
        self.ocultaletras()
        objeto = 'seleccion'
        despx = 0
        despy = 0
        if direccion == 1:
            if self.posicion == 1 or self.posicion == 11 or self.posicion == 21 or self.posicion == 31 or self.posicion == 41:
                if self.posicion == 41:
                    self.posicion = self.posicion + 12
                else:
                    self.posicion = self.posicion + 9
            else:
                self.posicion = self.posicion - 1
        elif direccion == 2:
            if self.posicion == 10 or self.posicion == 20 or self.posicion == 30 or self.posicion == 40 or self.posicion == 53:
                if self.posicion == 53:
                    self.posicion = self.posicion - 12
                else:
                    self.posicion = self.posicion - 9
            else:
                self.posicion = self.posicion + 1
        elif direccion == 3:
            if self.posicion >= 1 and self.posicion <= 10:
                self.posicion = self.posicion + 40
            elif self.posicion > 50 and self.posicion <= 53:
                self.posicion = self.posicion - 13
            else:
                self.posicion = self.posicion - 10
        elif direccion == 4:
            if self.posicion >= 41 and self.posicion <= 50:
                self.posicion = self.posicion - 40
            elif self.posicion > 50 and self.posicion <= 53:
                self.posicion = self.posicion - 43
            else:
                self.posicion = self.posicion + 10
        xposicion = self.posicion - 1
        if self.posicion > 10:
            cposicion = str(xposicion)[1]
            xposicion = int(cposicion)
            if self.posicion > 50:
                xposicion = xposicion + 10
        if esHD():
            lax = xposicion * 84
        else:
            lax = xposicion * 56
        tempos = self.posicion
        if tempos > 50:
            tempos = 50
        if esHD():
            lay = int((tempos - 1) / 10) * 57
        else:
            lay = int((tempos - 1) / 10) * 38
        if self.posicion > 40:
            lay = lay + 4
        if esHD():
            self[objeto].instance.move(ePoint(5 + lax, 210 + lay))
        else:
            self[objeto].instance.move(ePoint(5 + lax, 141 + lay))
        self.ponayuda(self.posicion)

    def Exit(self, forzar = False):
        if self.eninfo:
            self.muestrainfo()
            return
        if self.historico and not forzar:
            self.activalista()
            return
        self.timerBlink.callback.remove(self.esperaletra)
        self.timerWindow.callback.remove(self.ocultaletras)
        self.timerCursor = None
        self.timerBlink = None
        self.timerWindow = None
        if self.obj:
            self.obj.VirtualKeyBoardCallback(txt)
        else:
            self.close(None)

    def key1(self, numero = None):
        self.ponletra(1)

    def key2(self, numero = None):
        self.ponletra(2)

    def key3(self, numero = None):
        self.ponletra(3)

    def key4(self, numero = None):
        self.ponletra(4)

    def key5(self, numero = None):
        self.ponletra(5)

    def key6(self, numero = None):
        self.ponletra(6)

    def key7(self, numero = None):
        self.ponletra(7)

    def key8(self, numero = None):
        self.ponletra(8)

    def key9(self, numero = None):
        self.ponletra(9)

    def key0(self, numero = None):
        self.ponletra(0)

    def ponletra(self, cual):
        if self.eninfo:
            self.muestrainfo()
            return
        self.timerWindow.stop()
        self.ocultaletras(False)
        self.timerBlink.stop()
        try:
            self[self.lastmarked].setMarkedPos(-1)
        except:
            pass

        if cual == 0:
            self.esperaletra()
            self.numero = 0
            self.pontexto('0')
            self.timerWindow.stop()
            self.timerWindow.start(5000, True)
            self.letraespera = None
            return
        if self.numero != cual:
            self.esperaletra()
            self.timerWindow.stop()
            self.letraespera = None
        if self.letraespera == None:
            self.letraespera = 0
        objeto = 'key_teclado' + str(cual)
        valor = self[objeto].getText().decode('UTF-8')
        salir = False
        conta = 0
        if self.letraespera >= len(valor):
            self.letraespera = 0
        self[objeto].setMarkedPos(self.letraespera)
        self.letraespera = self.letraespera + 1
        self.lastmarked = objeto
        self.numero = cual
        self.timerBlink.start(2000, True)

    def esperaletra(self):
        self.timerBlink.stop()
        if not self.letraespera == None:
            conta = 0
            valor = ''
            for iji in self[self.lastmarked].getText().decode('UTF-8'):
                if conta == self.letraespera - 1:
                    valor = iji
                    break
                conta = conta + 1

            self.pontexto(valor)
            self.letraespera = 0
            try:
                self[self.lastmarked].setMarkedPos(-1)
            except:
                pass

        self.timerWindow.start(5000, True)

    def ocultaletras(self, ocultar = True):
        self.timerWindow.stop()
        self.timerBlink.stop()
        if ocultar:
            if not self.oculto:
                self['in_green'].show()
                self['imagenfondo2'].hide()
                self['key_teclado1'].hide()
                self['key_teclado2'].hide()
                self['key_teclado3'].hide()
                self['key_teclado4'].hide()
                self['key_teclado5'].hide()
                self['key_teclado6'].hide()
                self['key_teclado7'].hide()
                self['key_teclado8'].hide()
                self['key_teclado9'].hide()
                if not self.entexto:
                    self['seleccion'].show()
                self.oculto = True
                self.numero = 0
                self.letraespera = None
        elif self.oculto:
            self['in_green'].hide()
            self['imagenfondo2'].show()
            self['key_teclado1'].show()
            self['key_teclado2'].show()
            self['key_teclado3'].show()
            self['key_teclado4'].show()
            self['key_teclado5'].show()
            self['key_teclado6'].show()
            self['key_teclado7'].show()
            self['key_teclado8'].show()
            self['key_teclado9'].show()
            self['seleccion'].hide()
            self.oculto = False
