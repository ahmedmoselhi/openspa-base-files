from Converter import Converter
from Components.Element import cached
import os
from Poll import Poll
from Components.Converter.wheaterSpz import cargaDatos, devgificono, haywheather, devtipo
from Tools.Directories import fileExists
modificando = False

def pondebug(loque, etipo = 0):
    pass


class wheaterSpzVfd(Poll, Converter, object):
    LUGARGRADOS = 10
    ICONOHOYVFD = 20
    TEMPERATURAGRADOS = 30

    def __init__(self, type):
        Converter.__init__(self, type)
        Poll.__init__(self)
        anadido = 0
        self.poll_enabled = True
        self.type = 0
        self.textohoy = ''
        self.textomanana = ''
        self.iconohoy = ''
        self.iconomanana = ''
        self.lugar = ''
        self.temperatura = ''
        self.ahora = ''
        self.png = None
        self.rutavfd = '/share/enigma2/vfd_icons/'
        self.extended = False
        if type == 'LugarGrados':
            self.type = self.LUGARGRADOS
        elif type == 'TemperaturaGrados':
            self.type = self.TEMPERATURAGRADOS
        elif type == 'IconoHoyVfd':
            self.type = self.ICONOHOYVFD
        self.intervalo = 3720000 + anadido
        self.poll_interval = 30000 + anadido
        self.anadido = anadido
        pondebug('init - tipo [' + str(type) + ']', self.type)

    @cached
    def getText(self):
        global modificando
        info = None
        pondebug('getext - tipo [' + str(self.type) + ']' + str(modificando), self.type)
        entrar = False
        try:
            info = self.source.getBoolean()
            if info and self.type == 10:
                self.poll_interval = self.intervalo
                return ''
        except:
            entrar = True

        if entrar:
            return ''
        pondebug('dentro gettext' + ' - tipo [' + str(self.type) + ']', self.type)
        text = ''
        if haywheather():
            self.poll_interval = self.intervalo
            tipo = self.type
            if tipo == 30:
                tipo = 5
            if modificando:
                if tipo == 5:
                    modificando = False
                else:
                    pondebug('getext' + ' MODIFICANDO - tipo [' + str(self.type) + ']', self.type)
                    self.poll_interval = 15000
            self.lugar, self.temperatura, self.textohoy, self.textomanana, self.iconohoy, self.iconomanana, self.ahora, actualizando = cargaDatos(tipo, self.extended)
            if actualizando:
                if tipo == 5:
                    modificando = True
                self.poll_interval = 15000
            pondebug('carga datos - tipo [' + str(self.type) + ']', self.type)
            if self.type == self.TEMPERATURAGRADOS:
                text = self.temperatura.replace('C', '').replace('F', '').replace(' ', '')
            elif self.type == self.LUGARGRADOS:
                if len(self.lugar) > 17:
                    self.lugar = self.lugar[:16] + '...'
                text = self.lugar + ' ' + self.textohoy.replace('C', '').replace('F', '').replace(' ', '')
            elif self.type == self.ICONOHOYVFD:
                if self.iconohoy == '':
                    pngname = ''
                else:
                    iconogif = self.iconohoy
                    if devtipo() == 0:
                        iconopng = devgificono(iconogif, actual=True)
                        rpng = self.rutavfd
                    else:
                        iconopng = iconogif.replace('.jpg', '-fs8.png')
                        rpng = self.rutavfd
                    if fileExists(rpng + iconopng):
                        pngname = rpng + iconopng
                    elif fileExists(self.rutavfd + iconogif):
                        pngname = self.rutavfd + iconogif
                    else:
                        pngname = self.rutapng + '0-fs8.png'
                text = pngname
        if text == '':
            self.poll_interval = 120000 + self.anadido
        pondebug('return  - tipo [' + str(self.type) + ']' + '-[' + str(text) + ']', self.type)
        return text

    text = property(getText)

    def changed(self, what):
        if what[0] != self.CHANGED_SPECIFIC or what[1] == self.type:
            pondebug('changed - tipo [' + str(self.type) + ']' + '-' + str(what), self.type)
            Converter.changed(self, what)
