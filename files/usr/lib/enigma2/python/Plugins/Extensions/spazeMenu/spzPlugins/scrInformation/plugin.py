from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.ActionMap import ActionMap
from time import localtime
from enigma import eTimer
from Tools.Directories import fileExists, resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE
from Screens import Standby
from Components.Language import language
from Components.Label import Label
from os import environ
import os
import gettext
lang = language.getLanguage()
environ['LANGUAGE'] = lang[:2]
gettext.bindtextdomain('enigma2', resolveFilename(SCOPE_LANGUAGE))
gettext.textdomain('enigma2')
gettext.bindtextdomain('scrInformation', '%s%s' % (resolveFilename(SCOPE_PLUGINS), 'Extensions/spazeMenu/spzPlugins/scrInformation/locale/'))

def mostrarNotificacion(id = 'spazaeTeamNotificacion', texto = 'spazeTeam (www.azboxhd.es)', titulo = _('Information'), segundos = 3, mostrarSegundos = True, cerrable = True):
    NOTIFICATIONID = id
    from Tools.Notifications import AddNotificationWithID, RemovePopup
    try:
        RemovePopup(NOTIFICATIONID)
    except:
        pass

    AddNotificationWithID(NOTIFICATIONID, scrInformation, texto, titulo, segundos, mostrarSegundos, cerrable)


def _(txt):
    t = gettext.dgettext('scrInformation', txt)
    if t == txt:
        t = gettext.gettext(txt)
    return t


from enigma import eSize, ePoint

class scrInformation(Screen):
    skin = '<screen name="scrInformation" position="750,60" size="500,40" title="%s">\n\t\t<widget name="texto" position="40,2" size="500,40" valign="top" halign="left" font="Regular; 19" transparent="1" />\n\t\t<ePixmap name="new ePixmap" position="4,0" size="26,25" alphatest="blend" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/scrInformation/msg_infop-fs8.png" zPosition="-1" />\n\t\t</screen>' % _('Information')

    def __init__(self, session, texto = ' ', titulo = _('Information'), segundos = 3, mostrarSegundos = True, cerrable = True):
        Screen.__init__(self, session)
        self.session = session
        self.cerrable = cerrable
        self['texto'] = Label(_(texto))
        self.titulo = titulo
        self.contador = segundos + 1
        self.mostrarSegundos = mostrarSegundos
        self['actions'] = ActionMap(['DirectionActions',
         'ShortcutActions',
         'WizardActions',
         'MenuActions',
         'InfobarActions',
         'EPGSelectActions'], {'ok': self.exit,
         'green': self.exit,
         'red': self.exit,
         'blue': self.exit,
         'yellow': self.exit,
         'home': self.exit,
         'back': self.exit,
         'info': self.exit,
         'left': self.exit,
         'right': self.exit,
         'up': self.exit,
         'down': self.exit,
         'menu': self.exit}, -1)
        self.setTitle(self.titulo)
        self.TimerChequea = eTimer()
        self.TimerChequea.callback.append(self.actualiza)
        self.onLayoutFinish.append(self.actualiza)
        self.onLayoutFinish.append(self.ajusta)

    def ajusta(self):
        textsize = self['texto'].getSize()
        if textsize[0] > 500:
            textsize = (500, textsize[1] + 3)
        elif textsize[0] < 250:
            textsize = (250, textsize[1] + 3)
        else:
            textsize = (textsize[0] + 50, textsize[1] + 3)
        offset = 0
        espacio = 7
        wsizex = textsize[0] + 40
        wsizey = textsize[1] + offset + espacio
        wsize = (wsizex, wsizey)
        self.instance.resize(eSize(*wsize))
        self['texto'].instance.resize(eSize(*textsize))
        newwidth = wsize[0]
        self.instance.move(ePoint(1280 - newwidth - 60, 75))

    def actualiza(self):
        self.contador = self.contador - 1
        self.TimerChequea.stop()
        if Standby.inStandby:
            self.close(None)
        elif self.contador <= -99:
            self.close(None)
        elif self.contador < 0:
            self.close(None)
        else:
            if self.mostrarSegundos:
                mensajesec = '(' + str(self.contador) + ')'
                self.setTitle(mensajesec + ' ' + self.titulo)
            self.TimerChequea.startLongTimer(1)

    def exit(self):
        if not self.cerrable:
            return
        self.TimerChequea.stop()
        self.contador = -100
        self.setTitle(self.titulo)
        self.TimerChequea.start(400, True)
