from Components.ActionMap import NumberActionMap
from Components.config import config, ConfigSubsection, ConfigInteger
from Components.Console import Console
from Components.Label import Label
from Components.Language import language
from Components.Pixmap import Pixmap
from Components.VideoWindow import VideoWindow
from enigma import eServiceCenter, eServiceReference, eTimer, getDesktop, loadPNG
from ServiceReference import ServiceReference
from os import environ
from Plugins.Plugin import PluginDescriptor
from Screens.ChannelSelection import BouquetSelector
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Tools.Directories import resolveFilename, SCOPE_SKIN_IMAGE, SCOPE_LANGUAGE, SCOPE_PLUGINS, fileExists
from Tools.LoadPixmap import LoadPixmap
import gettext
from Tools import Notifications
from enigma import eSize, ePoint
import os
from Screens.EventView import EventViewSimple
grab_binary = '/usr/bin/grab'
grab_picture = '/tmp/mosaic.jpg'
grab_errorlog = '/tmp/mosaic.log'
config_limits = (8, 60)
config.plugins.spzMosaic = ConfigSubsection()
config.plugins.spzMosaic.countdown = ConfigInteger(default=15, limits=config_limits)
playingIcon = loadPNG('/usr/lib/enigma2/python/Plugins/Extensions/spzMosaic/img/ico_mp_play.png')
pausedIcon = loadPNG(resolveFilename(SCOPE_SKIN_IMAGE, 'skin_default/icons/ico_mp_pause.png'))
lang = language.getLanguage()
environ['LANGUAGE'] = lang[:2]
gettext.bindtextdomain('enigma2', resolveFilename(SCOPE_LANGUAGE))
gettext.textdomain('enigma2')
gettext.bindtextdomain('spzMosaic', '%s%s' % (resolveFilename(SCOPE_PLUGINS), 'Extensions/spzMosaic/locale/'))

def _(txt):
    t = gettext.dgettext('spzMosaic', txt)
    if t == txt:
        t = gettext.gettext(txt)
    return t


def chequeagrabar(sesion, notificar = True):
    recordings = len(sesion.nav.getRecordings())
    if recordings > 0:
        if notificar:
            Notifications.AddPopup(text=_('Recording in progress.\nThis plugin not work during record process'), type=MessageBox.TYPE_INFO, timeout=10, id='Mosaic')
        return True
    try:
        from Screens.InfoBar import InfoBar
        if InfoBar and InfoBar.instance:
            if InfoBar.instance.timeshift_enabled > 0:
                Notifications.AddPopup(text=_('Timeshift is enabled.\nThis plugin not work during record process'), type=MessageBox.TYPE_INFO, timeout=10, id='Mosaic')
                return True
        return False
    except:
        return False


class mosaicAmpliado(Screen):
    skin = '\n\t\t<screen name="mosaicAmpliado" position="0,0" size="1281,721" title="%s" zPosition="10" flags="wfNoBorder" backgroundColor="#ff000000">\n\t\t<widget source="session.VideoPicture" render="Pig" position="0,0" size="1280,720" zPosition="0" backgroundColor="#ff000000" transparent="0" />\n\t\t\n\t\t<eLabel name="fondoarr" position="0,3" size="1280,55" backgroundColor="#50000000" zPosition="1" />\n\t\t<widget source="session.CurrentService" render="Label" position="40,20" size="500,22" transparent="1" font="Regular;19" backgroundColor="#000000" foregroundColor="#ffffff" shadowColor="#000000" shadowOffset="-2,-2" zPosition="4">\n\t\t  <convert type="ServiceName">Name</convert>\n\t\t</widget>\n\t\t<widget source="session.Event_Now" render="Label" position="10,20" size="1220,22" transparent="1" font="Regular;18" backgroundColor="#000000" foregroundColor="#ababab" halign="right" shadowColor="#000000" shadowOffset="-2,-2" zPosition="4">\n\t\t  <convert type="EventTime">Remaining</convert>\n\t\t  <convert type="RemainingToText">InMinutes</convert>\n\t\t</widget>\n\t\t<widget source="session.Event_Now" render="Label" position="20,20" size="1100,22" transparent="1" font="Regular;18" backgroundColor="#000000" foregroundColor="#ffffff" halign="right" shadowColor="#000000" shadowOffset="-2,-2" zPosition="4" >\n\t\t  <convert type="EventName">Name</convert>\n\t\t</widget>\n\t\t</screen>' % _('Channels Mosaic')

    def __init__(self, session, parent):
        Screen.__init__(self, session)
        self.parent = parent
        self['actions'] = NumberActionMap(['MosaicActions'], {'ok': self.exit,
         'cancel': self.exit,
         'green': self.parent.playPause,
         'red': self.exit,
         'blue': self.exit,
         'yellow': self.exit,
         'channelup': self.exit,
         'channeldown': self.exit,
         'left': self.exit,
         'info': self.parent.kinfo,
         'right': self.exit,
         'up': self.exit,
         'down': self.exit,
         '1': self.exit,
         '2': self.exit,
         '3': self.exit,
         '4': self.exit,
         '5': self.exit,
         '6': self.exit,
         '7': self.exit,
         '8': self.exit,
         '9': self.exit}, prio=-1)

    def exit(self):
        self.close()


class Mosaic(Screen):
    PLAY = 0
    PAUSE = 1
    desktop = getDesktop(0)
    size = desktop.size()
    width = 1280
    height = 720
    windowWidth = 300
    windowHeight = 170
    positions = []
    x = 80
    y = 77
    margenx = 60
    margeny = 29
    for i in range(1, 10):
        positions.append([x, y])
        x += windowWidth
        x += (width - 160 - windowWidth * 3) / 2
        if i == 3 or i == 6:
            y = y + windowHeight + 30
            x = 80

    skin = ''
    skin += '<screen position="0,0" size="%d,%d" title="%s" flags="wfNoBorder" backgroundColor="#ffffff" >' % (width, height, _('Channels Mosaic'))
    skin += '<widget name="marco" position="0,0" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spzMosaic/img/marcotumb-fs8.png" zPosition="4" size="330,190" alphatest="blend" />'
    skin += '<widget name="marcog" position="0,0" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spzMosaic/img/marcotumbg-fs8.png" zPosition="10" size="390,225" alphatest="blend" />'
    skin += '<eLabel name="fondoarr" position="0,0" size="%d,55" backgroundColor="#333333" zPosition="-2" />' % width
    skin += '<widget name="infocanal" position="40,30" size="%d,22" transparent="1" font="Regular;20" backgroundColor="#000000" foregroundColor="#ffffff" />' % width
    skin += '<widget name="playState" position="25,%d" size="16,16" alphatest="blend" />' % (height - 55)
    skin += '<ePixmap position="%d,%d" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spzMosaic/img/fondo-fs8.png" alphatest="blend" size="%d,%d" />' % (positions[0][0] - 3,
     positions[0][1] - 2,
     windowWidth + 2,
     windowHeight + 1)
    skin += '<ePixmap position="%d,%d" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spzMosaic/img/fondo-fs8.png" alphatest="blend" size="%d,%d" />' % (positions[1][0] - 3,
     positions[1][1] - 2,
     windowWidth + 2,
     windowHeight + 1)
    skin += '<ePixmap position="%d,%d" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spzMosaic/img/fondo-fs8.png" alphatest="blend" size="%d,%d" />' % (positions[2][0] - 3,
     positions[2][1] - 2,
     windowWidth + 2,
     windowHeight + 1)
    skin += '<ePixmap position="%d,%d" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spzMosaic/img/fondo-fs8.png" alphatest="blend" size="%d,%d" />' % (positions[3][0] - 3,
     positions[3][1] - 2,
     windowWidth + 2,
     windowHeight + 1)
    skin += '<ePixmap position="%d,%d" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spzMosaic/img/fondo-fs8.png" alphatest="blend" size="%d,%d" />' % (positions[4][0] - 3,
     positions[4][1] - 2,
     windowWidth + 2,
     windowHeight + 1)
    skin += '<ePixmap position="%d,%d" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spzMosaic/img/fondo-fs8.png" alphatest="blend" size="%d,%d" />' % (positions[5][0] - 3,
     positions[5][1] - 2,
     windowWidth + 2,
     windowHeight + 1)
    skin += '<ePixmap position="%d,%d" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spzMosaic/img/fondo-fs8.png" alphatest="blend" size="%d,%d" />' % (positions[6][0] - 3,
     positions[6][1] - 2,
     windowWidth + 2,
     windowHeight + 1)
    skin += '<ePixmap position="%d,%d" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spzMosaic/img/fondo-fs8.png" alphatest="blend" size="%d,%d" />' % (positions[7][0] - 3,
     positions[7][1] - 2,
     windowWidth + 2,
     windowHeight + 1)
    skin += '<ePixmap position="%d,%d" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spzMosaic/img/fondo-fs8.png" alphatest="blend" size="%d,%d" />' % (positions[8][0] - 3,
     positions[8][1] - 2,
     windowWidth + 2,
     windowHeight + 1)
    skin += '<widget name="channel1" position="%d,%d" size="%d,20" transparent="1" zPosition="6" font="Regular;17" backgroundColor="#ffffff" foregroundColor="#000000" />' % (positions[0][0], positions[0][1] - 20, windowWidth - 4)
    skin += '<widget name="channel2" position="%d,%d" size="%d,20" transparent="1" zPosition="6" font="Regular;17" backgroundColor="#ffffff" foregroundColor="#000000" />' % (positions[1][0], positions[1][1] - 20, windowWidth - 4)
    skin += '<widget name="channel3" position="%d,%d" size="%d,20" transparent="1" zPosition="6" font="Regular;17" backgroundColor="#ffffff" foregroundColor="#000000" />' % (positions[2][0], positions[2][1] - 20, windowWidth - 4)
    skin += '<widget name="channel4" position="%d,%d" size="%d,20" transparent="1" zPosition="6" font="Regular;17" backgroundColor="#ffffff" foregroundColor="#000000" />' % (positions[3][0], positions[3][1] - 20, windowWidth - 4)
    skin += '<widget name="channel5" position="%d,%d" size="%d,20" transparent="1" zPosition="6" font="Regular;17" backgroundColor="#ffffff" foregroundColor="#000000" />' % (positions[4][0], positions[4][1] - 20, windowWidth - 4)
    skin += '<widget name="channel6" position="%d,%d" size="%d,20" transparent="1" zPosition="6" font="Regular;17" backgroundColor="#ffffff" foregroundColor="#000000" />' % (positions[5][0], positions[5][1] - 20, windowWidth - 4)
    skin += '<widget name="channel7" position="%d,%d" size="%d,20" transparent="1" zPosition="6" font="Regular;17" backgroundColor="#ffffff" foregroundColor="#000000" />' % (positions[6][0], positions[6][1] - 20, windowWidth - 4)
    skin += '<widget name="channel8" position="%d,%d" size="%d,20" transparent="1" zPosition="6" font="Regular;17" backgroundColor="#ffffff" foregroundColor="#000000" />' % (positions[7][0], positions[7][1] - 20, windowWidth - 4)
    skin += '<widget name="channel9" position="%d,%d" size="%d,20" transparent="1" zPosition="6" font="Regular;17" backgroundColor="#ffffff" foregroundColor="#000000" />' % (positions[8][0], positions[8][1] - 20, windowWidth - 4)
    skin += '<widget name="window1" position="%d,%d" zPosition="1" size="%d,%d" />' % (positions[0][0] - 2,
     positions[0][1] - 1,
     windowWidth,
     windowHeight)
    skin += '<widget name="window2" position="%d,%d" zPosition="1" size="%d,%d" />' % (positions[1][0] - 2,
     positions[1][1] - 1,
     windowWidth,
     windowHeight)
    skin += '<widget name="window3" position="%d,%d" zPosition="1" size="%d,%d" />' % (positions[2][0] - 2,
     positions[2][1] - 1,
     windowWidth,
     windowHeight)
    skin += '<widget name="window4" position="%d,%d" zPosition="1" size="%d,%d" />' % (positions[3][0] - 2,
     positions[3][1] - 1,
     windowWidth,
     windowHeight)
    skin += '<widget name="window5" position="%d,%d" zPosition="1" size="%d,%d" />' % (positions[4][0] - 2,
     positions[4][1] - 1,
     windowWidth,
     windowHeight)
    skin += '<widget name="window6" position="%d,%d" zPosition="1" size="%d,%d" />' % (positions[5][0] - 2,
     positions[5][1] - 1,
     windowWidth,
     windowHeight)
    skin += '<widget name="window7" position="%d,%d" zPosition="1" size="%d,%d" />' % (positions[6][0] - 2,
     positions[6][1] - 1,
     windowWidth,
     windowHeight)
    skin += '<widget name="window8" position="%d,%d" zPosition="1" size="%d,%d" />' % (positions[7][0] - 2,
     positions[7][1] - 1,
     windowWidth,
     windowHeight)
    skin += '<widget name="window9" position="%d,%d" zPosition="1" size="%d,%d" />' % (positions[8][0] - 2,
     positions[8][1] - 1,
     windowWidth,
     windowHeight)
    skin += '<widget name="video1" position="%d,%d" zPosition="8" size="%d,%d" backgroundColor="#ff000000" />' % (positions[0][0] - 2 - margenx / 2,
     positions[0][1] - 1 - margeny / 2,
     windowWidth + margenx,
     windowHeight + margeny)
    skin += '<widget name="video2" position="%d,%d" zPosition="8" size="%d,%d" backgroundColor="#ff000000" />' % (positions[1][0] - 2 - margenx / 2,
     positions[1][1] - 1 - margeny / 2,
     windowWidth + margenx,
     windowHeight + margeny)
    skin += '<widget name="video3" position="%d,%d" zPosition="8" size="%d,%d" backgroundColor="#ff000000" />' % (positions[2][0] - 2 - margenx / 2,
     positions[2][1] - 1 - margeny / 2,
     windowWidth + margenx,
     windowHeight + margeny)
    skin += '<widget name="video4" position="%d,%d" zPosition="8" size="%d,%d" backgroundColor="#ff000000" />' % (positions[3][0] - 2 - margenx / 2,
     positions[3][1] - 1 - margeny / 2,
     windowWidth + margenx,
     windowHeight + margeny)
    skin += '<widget name="video5" position="%d,%d" zPosition="8" size="%d,%d" backgroundColor="#ff000000" />' % (positions[4][0] - 2 - margenx / 2,
     positions[4][1] - 1 - margeny / 2,
     windowWidth + margenx,
     windowHeight + margeny)
    skin += '<widget name="video6" position="%d,%d" zPosition="8" size="%d,%d" backgroundColor="#ff000000" />' % (positions[5][0] - 2 - margenx / 2,
     positions[5][1] - 1 - margeny / 2,
     windowWidth + margenx,
     windowHeight + margeny)
    skin += '<widget name="video7" position="%d,%d" zPosition="8" size="%d,%d" backgroundColor="#ff000000" />' % (positions[6][0] - 2 - margenx / 2,
     positions[6][1] - 1 - margeny / 2,
     windowWidth + margenx,
     windowHeight + margeny)
    skin += '<widget name="video8" position="%d,%d" zPosition="8" size="%d,%d" backgroundColor="#ff000000" />' % (positions[7][0] - 2 - margenx / 2,
     positions[7][1] - 1 - margeny / 2,
     windowWidth + margenx,
     windowHeight + margeny)
    skin += '<widget name="video9" position="%d,%d" zPosition="8" size="%d,%d" backgroundColor="#ff000000" />' % (positions[8][0] - 2 - margenx / 2,
     positions[8][1] - 1 - margeny / 2,
     windowWidth + margenx,
     windowHeight + margeny)
    skin += '<widget name="event1" position="%d,%d" size="%d,18" zPosition="3" font="Regular;16" noWrap="1" backgroundColor="#60000000" foregroundColor="#ffffff" />' % (positions[0][0] - 2, positions[0][1] - 1, windowWidth)
    skin += '<widget name="event2" position="%d,%d" size="%d,18" zPosition="3" font="Regular;16" noWrap="1" backgroundColor="#60000000" foregroundColor="#ffffff" />' % (positions[1][0] - 2, positions[1][1] - 1, windowWidth)
    skin += '<widget name="event3" position="%d,%d" size="%d,18" zPosition="3" font="Regular;16" noWrap="1" backgroundColor="#60000000" foregroundColor="#ffffff" />' % (positions[2][0] - 2, positions[2][1] - 1, windowWidth)
    skin += '<widget name="event4" position="%d,%d" size="%d,18" zPosition="3" font="Regular;16" noWrap="1" backgroundColor="#60000000" foregroundColor="#ffffff" />' % (positions[3][0] - 2, positions[3][1] - 1, windowWidth)
    skin += '<widget name="event5" position="%d,%d" size="%d,18" zPosition="3" font="Regular;16" noWrap="1" backgroundColor="#60000000" foregroundColor="#ffffff" />' % (positions[4][0] - 2, positions[4][1] - 1, windowWidth)
    skin += '<widget name="event6" position="%d,%d" size="%d,18" zPosition="3" font="Regular;16" noWrap="1" backgroundColor="#60000000" foregroundColor="#ffffff" />' % (positions[5][0] - 2, positions[5][1] - 1, windowWidth)
    skin += '<widget name="event7" position="%d,%d" size="%d,18" zPosition="3" font="Regular;16" noWrap="1" backgroundColor="#60000000" foregroundColor="#ffffff" />' % (positions[6][0] - 2, positions[6][1] - 1, windowWidth)
    skin += '<widget name="event8" position="%d,%d" size="%d,18" zPosition="3" font="Regular;16" noWrap="1" backgroundColor="#60000000" foregroundColor="#ffffff" />' % (positions[7][0] - 2, positions[7][1] - 1, windowWidth)
    skin += '<widget name="event9" position="%d,%d" size="%d,18" zPosition="3" font="Regular;16" noWrap="1" backgroundColor="#60000000" foregroundColor="#ffffff" />' % (positions[8][0] - 2, positions[8][1] - 1, windowWidth)
    skin += '<eLabel name="fondo" position="0,%d" size="%d,60" backgroundColor="#333333" zPosition="-2" />' % (height - 50, width)
    skin += '<widget name="countdown" position="43,%d" size="%d,20" transparent="1" font="Regular;17" backgroundColor="#000000" foregroundColor="#ffffff" />' % (height - 50, 500)
    skin += '<widget name="img_green" position="268,674" size="27,19" alphatest="blend" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spzMosaic/img/green-fs8.png" />'
    skin += '<widget name="tex_green" position="297,672" size="137,18" transparent="1" font="Regular; 16" backgroundColor="#000000" foregroundColor="#ffffff" noWrap="1" />'
    skin += '<widget name="img_yellow" position="458,674" size="27,19" alphatest="blend" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spzMosaic/img/yellow-fs8.png" />'
    skin += '<widget name="tex_yellow" position="487,672" size="164,18" transparent="1" font="Regular; 16" backgroundColor="#000000" foregroundColor="#ffffff" noWrap="1" />'
    skin += '<widget name="img_blue" position="663,674" size="27,19" alphatest="blend" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spzMosaic/img/blue-fs8.png" />'
    skin += '<widget name="tex_blue" position="692,672" size="141,18" transparent="1" font="Regular; 16" backgroundColor="#000000" foregroundColor="#ffffff" noWrap="1" />'
    skin += '<widget name="img_ant" position="438,674" size="27,19" alphatest="blend" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spzMosaic/img/chmenos-fs8.png" />'
    skin += '<widget name="tex_ant" position="467,672" size="163,18" transparent="1" font="Regular; 16" backgroundColor="#000000" foregroundColor="#ffffff" noWrap="1" zPosition="4" />'
    skin += '<widget name="img_sig" position="643,674" size="27,19" alphatest="blend" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spzMosaic/img/chmas-fs8.png" />'
    skin += '<widget name="tex_sig" position="672,672" size="163,18" transparent="1" font="Regular; 16" backgroundColor="#000000" foregroundColor="#ffffff" noWrap="1" zPosition="4" />'
    skin += '<widget name="img_ok" position="33,674" size="27,19" alphatest="blend" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spzMosaic/img/ok-fs8.png" />'
    skin += '<widget name="tex_ok" position="62,672" size="204,18" transparent="1" font="Regular; 16" backgroundColor="#000000" foregroundColor="#ffffff" noWrap="1" />'
    skin += '<widget name="img_info" position="843,674" size="27,19"  alphatest="blend" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spzMosaic/img/info-fs8.png" />'
    skin += '<widget name="tex_info" position="872,672" size="204,18" transparent="1" font="Regular; 16" backgroundColor="#000000" foregroundColor="#ffffff" noWrap="1" />'
    skin += '<widget name="img_red" position="1073,674" size="27,19" alphatest="blend" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spzMosaic/img/red-fs8.png" />'
    skin += '<widget name="tex_red" position="1102,672" size="164,18" transparent="1" font="Regular; 16" backgroundColor="#000000" foregroundColor="#ffffff" noWrap="1" />'
    skin += '<widget name="count" position="%d,%d" size="%d,42" transparent="1" font="Regular;18" backgroundColor="#000000" foregroundColor="#ffffff" halign="right" />\n\t</screen>' % (positions[2][0] + 40, 30, windowWidth - 10)

    def __init__(self, session, services):
        Screen.__init__(self, session)
        self.session = session
        try:
            self.oldService = self.session.nav.getCurrentlyPlayingServiceOrGroup()
        except:
            self.oldService = None

        self.consoleCmd = ''
        self.Console = Console()
        self.serviceHandler = eServiceCenter.getInstance()
        self.ref_list = services
        self.window_refs = [None,
         None,
         None,
         None,
         None,
         None,
         None,
         None,
         None]
        self.current_refidx = 0
        self.current_window = 1
        self.max_window = 9
        self.countdown = config.plugins.spzMosaic.countdown.value
        self.working = False
        self.state = self.PAUSE
        self.countdownCreate = 4
        self.intentos = 0
        self.maxintentos = 16
        self.tiempoCrear = self.countdownCreate
        self.creando = True
        self.uref = 0
        self['playState'] = Pixmap()
        for i in range(1, 10):
            self['window' + str(i)] = Pixmap()
            self['video' + str(i)] = VideoWindow(decoder=0, fb_width=self.width, fb_height=self.height)
            self['video' + str(i)].hide()
            self['channel' + str(i)] = Label(' ')
            self['event' + str(i)] = Label(' ')
            self['event' + str(i)].hide()

        self['video1'].decoder = 0
        self['video1'].show()
        self['countdown'] = Label()
        self['infocanal'] = Label()
        self['marco'] = Pixmap()
        self['marcog'] = Pixmap()
        self.updateCountdownLabel()
        self['count'] = Label()
        self['tex_green'] = Label(_('AutoZap'))
        self['img_green'] = Pixmap()
        self['tex_yellow'] = Label(_('Decrease time'))
        self['img_yellow'] = Pixmap()
        self['tex_blue'] = Label(_('Increase time'))
        self['img_blue'] = Pixmap()
        self['tex_ant'] = Label(_('Previous Screen'))
        self['img_ant'] = Pixmap()
        self['tex_sig'] = Label(_('Next Screen'))
        self['img_sig'] = Pixmap()
        self['tex_ok'] = Label(_('Zap and Exit'))
        self['img_ok'] = Pixmap()
        self['tex_info'] = Label(_('Event Information'))
        self['img_info'] = Pixmap()
        self['tex_red'] = Label(_('Full screen'))
        self['img_red'] = Pixmap()
        try:
            f = open(grab_errorlog, 'w')
            f.write('Init grab\n*****************************************\n')
            f.close()
        except:
            pass

        self['actions'] = NumberActionMap(['MosaicActions'], {'ok': self.exit,
         'cancel': self.closeWithOldService,
         'green': self.playPause,
         'red': self.amplia,
         'blue': self.countdownPlus,
         'yellow': self.countdownMinus,
         'channelup': self.sigpantalla,
         'channeldown': self.prevpantalla,
         'left': self.kleft,
         'info': self.kinfo,
         'right': self.kright,
         'up': self.kup,
         'down': self.kdown,
         '1': self.numberPressed,
         '2': self.numberPressed,
         '3': self.numberPressed,
         '4': self.numberPressed,
         '5': self.numberPressed,
         '6': self.numberPressed,
         '7': self.numberPressed,
         '8': self.numberPressed,
         '9': self.numberPressed}, prio=-1)
        self.TimerTemp = eTimer()
        self.TimerTemp.callback.append(self.ampliarTumb)
        self.onLayoutFinish.append(self.inicio)
        self.countdown = config.plugins.spzMosaic.countdown.value
        self.updateTimer = eTimer()
        self.updateTimer.callback.append(self.updateCountdown)
        self.updateTimerCreate = eTimer()
        self.updateTimerCreate.callback.append(self.updateCountdownCreate)
        self.checkTimer = eTimer()
        self.checkTimer.callback.append(self.checkGrab)
        self.checkTimer.start(500, 1)

    def amplia(self):
        if self.sibloquear():
            return
        self.session.openWithCallback(self.cbamplia, mosaicAmpliado, parent=self)

    def cbamplia(self, respuesta = None):
        pass

    def kinfo(self):
        if self.sibloquear():
            return
        if self.current_window > self.max_window:
            return
        self.pause()
        self.TimerTemp.stop()
        serviceref = self.window_refs[self.current_window - 1]
        serviceHandler = eServiceCenter.getInstance()
        info = serviceHandler.info(serviceref)
        evt = info.getEvent(serviceref)
        if evt:
            self.session.open(EventViewSimple, evt, ServiceReference(serviceref))

    def inicio(self):
        self['tex_green'].hide()
        self['img_green'].hide()
        self['tex_yellow'].hide()
        self['img_yellow'].hide()
        self['tex_blue'].hide()
        self['img_blue'].hide()
        self['tex_ant'].hide()
        self['img_ant'].hide()
        self['tex_sig'].hide()
        self['img_sig'].hide()
        self['tex_ok'].hide()
        self['img_ok'].hide()
        self['tex_info'].hide()
        self['img_info'].hide()
        self['tex_red'].hide()
        self['img_red'].hide()
        self['marco'].hide()
        self['marcog'].hide()
        self['infocanal'].setText(_('Loading...'))

    def sibloquear(self):
        if self.creando or self.working:
            return True
        else:
            return False

    def kleft(self):
        if self.sibloquear():
            return
        self.mostrarTumb(0)

    def kright(self):
        if self.sibloquear():
            return
        self.mostrarTumb(1)

    def kup(self):
        if self.sibloquear():
            return
        self.mostrarTumb(2)

    def kdown(self):
        if self.sibloquear():
            return
        self.mostrarTumb(3)

    def sigpantalla(self):
        if self.sibloquear():
            return
        if self.uref + 1 > len(self.ref_list) - 1:
            return
        self.quitaventana()
        self.current_window = 1
        self.max_window = 9
        self.checkGrab(self.uref)

    def prevpantalla(self):
        if self.sibloquear():
            return
        self.quitaventana()
        self.current_window = 1
        mxw = self.max_window + 9
        if self.uref - mxw < 0:
            self.uref = 0
        else:
            self.uref = self.uref - mxw
        self.max_window = 9
        self.checkGrab(self.uref)

    def playPause(self):
        if self.sibloquear():
            return
        if self.state == self.PAUSE:
            self.play()
        else:
            self.pause()

    def checkGrab(self, refini = 0):
        self.intentos = 0
        self['tex_green'].hide()
        self['img_green'].hide()
        self['tex_yellow'].hide()
        self['img_yellow'].hide()
        self['tex_blue'].hide()
        self['img_blue'].hide()
        self['tex_ant'].hide()
        self['img_ant'].hide()
        self['tex_sig'].hide()
        self['img_sig'].hide()
        self['tex_ok'].hide()
        self['img_ok'].hide()
        self['tex_info'].hide()
        self['img_info'].hide()
        self['tex_red'].hide()
        self['img_red'].hide()
        self.updateTimerCreate.stop()
        self.updateTimer.stop()
        self.current_window = 1
        self.current_refidx = self.uref
        ref = self.ref_list[refini]
        self.window_refs[0] = ref
        info = self.serviceHandler.info(ref)
        name = info.getName(ref).replace('\xc2\x86', '').replace('\xc2\x87', '')
        event_name = self.getEventName(info, ref)
        if chequeagrabar(self.session):
            self.exit()
            return
        self.session.nav.playService(ref)
        self['marco'].hide()
        for iji in range(2, 10):
            self['window' + str(iji)].hide()
            self['event' + str(iji)].hide()
            self['channel' + str(iji)].setText(' ')

        self['channel1'].setText(name)
        self['event1'].setText(event_name)
        self['video1'].show()
        self['infocanal'].setText(_('Loading...'))
        self.muestramarco()
        self.countdown = config.plugins.spzMosaic.countdown.value
        self['playState'].hide()
        self.creando = True
        self['countdown'].setText(_('Creating thumbails...'))
        self.updateTimerCreate.start(1, 1)

    def hayampliado(self, cerrar = True):
        ret = False
        if 'mosaicAmpliado' in str(self.session.current_dialog):
            try:
                if cerrar:
                    self.session.current_dialog.close()
                ret = True
            except:
                pass

        return ret

    def exit(self, callback = None):
        self.checkTimer.stop()
        self.updateTimerCreate.stop()
        self.updateTimer.stop()
        self.TimerTemp.stop()
        if self.hayampliado():
            pass
        self.deleteConsoleCallbacks()
        self.close(True)

    def deleteConsoleCallbacks(self):
        if self.Console.appContainers.has_key(self.consoleCmd):
            del self.Console.appContainers[self.consoleCmd].dataAvail[:]
            del self.Console.appContainers[self.consoleCmd].appClosed[:]
            del self.Console.appContainers[self.consoleCmd]
            del self.Console.extra_args[self.consoleCmd]
            del self.Console.callbacks[self.consoleCmd]

    def closeWithOldService(self):
        self.checkTimer.stop()
        self.updateTimerCreate.stop()
        self.updateTimer.stop()
        self.TimerTemp.stop()
        if not chequeagrabar(self.session, False):
            self.session.nav.playService(self.oldService)
        self.deleteConsoleCallbacks()
        self.close()

    def numberPressed(self, number):
        return
        ref = self.window_refs[number - 1]
        if ref is not None:
            if not chequeagrabar(self.session, False):
                self.session.nav.playService(ref)
            self.deleteConsoleCallbacks()
            self.close()

    def mostrarsigprev(self):
        if self.uref + 1 > len(self.ref_list) - 1:
            self['tex_sig'].hide()
            self['img_sig'].hide()
        else:
            self['tex_sig'].show()
            self['img_sig'].show()
        if self.current_refidx < 9:
            self['tex_ant'].hide()
            self['img_ant'].hide()
        else:
            self['tex_ant'].show()
            self['img_ant'].show()

    def play(self):
        if self.working == False and self.state == self.PAUSE:
            self.state = self.PLAY
            self.countdown = 1
            self['video' + str(self.current_window)].hide()
            self.current_refidx = self.uref - self.max_window + self.current_window - 1
            self.updateTimer.start(1000, 1)
            self['playState'].instance.setPixmap(playingIcon)
            self['marco'].hide()
            self['marcog'].hide()
            self['playState'].show()
            self['tex_green'].setText(_('Stop AutoZap'))
            self['img_green'].show()
            self['tex_yellow'].show()
            self['img_yellow'].show()
            self['tex_blue'].show()
            self['img_blue'].show()
            self['tex_ant'].hide()
            self['img_ant'].hide()
            self['tex_sig'].hide()
            self['img_sig'].hide()
            self['tex_ok'].hide()
            self['img_ok'].hide()

    def pause(self):
        if self.working == False and self.state == self.PLAY:
            self.state = self.PAUSE
            self.updateTimer.stop()
            self['playState'].hide()
            self['countdown'].setText(' ')
            self['tex_green'].setText(_('AutoZap'))
            self['img_green'].show()
            self['tex_yellow'].hide()
            self['img_yellow'].hide()
            self['tex_blue'].hide()
            self['img_blue'].hide()
            self.mostrarsigprev()
            self['tex_ok'].show()
            self['img_ok'].show()
            self.mostrarsigprev()

    def countdownPlus(self):
        self.changeCountdown(1)

    def countdownMinus(self):
        self.changeCountdown(-1)

    def changeCountdown(self, direction):
        if self.working == False:
            configNow = config.plugins.spzMosaic.countdown.value
            configNow += direction
            if configNow < config_limits[0]:
                configNow = config_limits[0]
            elif configNow > config_limits[1]:
                configNow = config_limits[1]
            config.plugins.spzMosaic.countdown.value = configNow
            config.plugins.spzMosaic.countdown.save()
            self.updateCountdownLabel()

    def makeNextScreenshot(self):
        if not self.Console:
            self.Console = Console()
        os.system('rm ' + grab_picture)
        self.consoleCmd = '%s -v -r %d -j 70 %s' % (grab_binary, self.windowWidth, grab_picture)
        self.Console.ePopen(self.consoleCmd, self.showNextScreenshot)

    def mostrarTumb(self, dire):
        self.TimerTemp.stop()
        self.pause()
        if not self.Console:
            self.Console = Console()
        os.system('rm ' + grab_picture)
        self.consoleCmd = '%s -v -r %d -j 70 %s' % (grab_binary, self.windowWidth, grab_picture)
        self.Console.ePopen(self.consoleCmd, self.nada)
        if dire == 0:
            ana = self.corriente - 1
            if ana == 0:
                ana = 3
            elif ana == 3 or ana == 6:
                ana = self.corriente + 2
        elif dire == 1:
            ana = self.corriente + 1
            if ana == 10:
                ana = 7
            elif ana == 4 or ana == 7:
                ana = self.corriente - 2
        elif dire == 2:
            ana = self.corriente - 3
            if ana <= 0:
                ana = self.corriente + 6
        else:
            ana = self.corriente + 3
            if ana > 9:
                ana = self.corriente - 6
        self.corriente = ana
        if self.corriente > 9:
            self.corriente = 1
        if self.corriente == self.current_window:
            self['marco'].hide()
            self.muestramarco()
        else:
            self['marcog'].hide()
            laposx = self['window' + str(self.corriente)].instance.position().x() - 5
            laposy = self['window' + str(self.corriente)].instance.position().y() - 5
            self['marco'].instance.move(ePoint(laposx, laposy))
            self['marco'].show()
        if self.corriente <= self.max_window:
            self.TimerTemp.start(2000, True)

    def muestramarco(self):
        laposx = self['video' + str(self.current_window)].instance.position().x() - 3
        laposy = self['video' + str(self.current_window)].instance.position().y() - 7
        self['marcog'].instance.move(ePoint(laposx, laposy))
        self['marcog'].show()

    def nada(self, result = None, retval = None, extra_args = None):
        pass

    def quitaventana(self):
        self.TimerTemp.stop()
        self.pause()
        if fileExists(grab_picture):
            pic = LoadPixmap(grab_picture)
        else:
            pic = LoadPixmap('/usr/lib/enigma2/python/Plugins/Extensions/spzMosaic/img/noimage.jpg')
        self['window' + str(self.current_window)].instance.setPixmap(pic)
        self['window' + str(self.current_window)].show()
        self['video' + str(self.current_window)].hide()
        self['event' + str(self.current_window)].show()

    def ampliarTumb(self):
        self.TimerTemp.stop()
        if fileExists(grab_picture):
            pic = LoadPixmap(grab_picture)
        else:
            pic = LoadPixmap('/usr/lib/enigma2/python/Plugins/Extensions/spzMosaic/img/noimage.jpg')
        self['window' + str(self.current_window)].instance.setPixmap(pic)
        self['window' + str(self.current_window)].show()
        self['video' + str(self.current_window)].hide()
        self['event' + str(self.current_window)].show()
        self.current_window = self.corriente
        ref = self.window_refs[self.current_window - 1]
        info = self.serviceHandler.info(ref)
        name = info.getName(ref).replace('\xc2\x86', '').replace('\xc2\x87', '')
        event_name = self.getEventName(info, ref)
        if chequeagrabar(self.session):
            self.exit()
            return
        self.session.nav.playService(ref)
        self['event' + str(self.current_window)].hide()
        self['event' + str(self.current_window)].setText(event_name)
        self['video' + str(self.current_window)].show()
        self['video' + str(self.current_window)].decoder = 0
        self['channel' + str(self.current_window)].setText(name)
        self.current_refidx = self.uref - self.max_window + self.current_window - 1
        self['count'].setText(_('Channel: ') + str(self.current_refidx + 1) + ' / ' + str(len(self.ref_list)))
        self.muestramarco()
        self['infocanal'].setText(name + ' :: ' + event_name)

    def showNextScreenshot(self, result, retval, extra_args):
        try:
            self.updateTimerCreate.stop()
        except:
            return

        if not fileExists(grab_picture) and self.intentos < self.maxintentos:
            try:
                f = open(grab_errorlog, 'rw')
                f.write('retval: %d\nresult: %s\n************************************************\n' % (retval, result))
                f.close()
            except:
                pass

            self.intentos = self.intentos + 1
            ref = self.ref_list[self.current_refidx]
            if chequeagrabar(self.session):
                self.exit()
                return
            if self.intentos == 13:
                self.session.nav.stopService()
                self.session.nav.playService(ref, forceRestart=True)
            if self.creando:
                self['countdown'].setText(_('Creating thumbails...') + '(' + str(self.maxintentos - self.intentos) + ')')
                self.countdownCreate = 0
                self.updateTimerCreate.start(1000, 1)
            else:
                self.countdown = 1
                self.updateTimer.start(1000, 1)
            return
        self.intentos = 0
        if retval == 0 or True:
            self.current_refidx += 1
            if self.current_refidx > len(self.ref_list) - 1:
                self.max_window = self.current_window
            if self.current_window >= self.max_window:
                self.creando = False
                self.uref = self.current_refidx
                if self.state == self.PLAY:
                    self.current_refidx = self.current_refidx - self.max_window
                else:
                    self.current_refidx = self.uref - self.max_window
            if fileExists(grab_picture):
                pic = LoadPixmap(grab_picture)
            else:
                pic = LoadPixmap('/usr/lib/enigma2/python/Plugins/Extensions/spzMosaic/img/noimage.jpg')
            self['window' + str(self.current_window)].instance.setPixmap(pic)
            self['window' + str(self.current_window)].show()
            self['video' + str(self.current_window)].hide()
            self['event' + str(self.current_window)].show()
            ref = self.ref_list[self.current_refidx]
            info = self.serviceHandler.info(ref)
            name = info.getName(ref).replace('\xc2\x86', '').replace('\xc2\x87', '')
            event_name = self.getEventName(info, ref)
            if chequeagrabar(self.session):
                self.exit()
                return
            self.session.nav.playService(ref)
            self.current_window += 1
            if self.current_window > self.max_window:
                self.current_window = 1
            self.window_refs[self.current_window - 1] = ref
            self['event' + str(self.current_window)].hide()
            self['event' + str(self.current_window)].setText(event_name)
            self['video' + str(self.current_window)].show()
            self['video' + str(self.current_window)].decoder = 0
            self.muestramarco()
            self['channel' + str(self.current_window)].setText(name)
            self.corriente = self.current_window
            self['infocanal'].setText(name + ' :: ' + event_name)
            self.working = False
            self['count'].setText(_('Channel: ') + str(self.current_refidx + 1) + ' / ' + str(len(self.ref_list)))
            if self.creando:
                self['countdown'].setText(_('Creating thumbails...'))
                self.updateTimerCreate.start(1, 1)
            elif self.state == self.PLAY:
                self.updateTimer.start(1, 1)
            else:
                self['countdown'].setText(' ')
                self['tex_green'].setText(_('AutoZap'))
                self['img_green'].show()
                self['tex_green'].show()
                self['tex_yellow'].hide()
                self['img_yellow'].hide()
                self['tex_blue'].hide()
                self['img_blue'].hide()
                self['tex_info'].show()
                self['tex_red'].show()
                self['img_red'].show()
                self['img_info'].show()
                self.mostrarsigprev()
                self['tex_ok'].show()
                self['img_ok'].show()
        else:
            print '[Mosaic] retval: %d result: %s' % (retval, result)
            try:
                f = open(grab_errorlog, 'w')
                f.write('retval: %d\nresult: %s' % (retval, result))
                f.close()
            except:
                pass

            self.session.openWithCallback(self.exit, MessageBox, _('Error while creating screenshot. You need grab version 0.8 or higher!'), MessageBox.TYPE_ERROR, timeout=5)

    def updateCountdownCreate(self, callback = None):
        self.countdownCreate -= 1
        if self.countdownCreate <= 0:
            self.countdownCreate = self.tiempoCrear
            self.working = True
            self.makeNextScreenshot()
        else:
            self.updateTimerCreate.start(1000, 1)

    def updateCountdown(self, callback = None):
        self.countdown -= 1
        self.updateCountdownLabel()
        if self.countdown <= 0:
            self.countdown = config.plugins.spzMosaic.countdown.value
            self.working = True
            self.makeNextScreenshot()
        else:
            self.updateTimer.start(1000, 1)

    def updateCountdownLabel(self):
        anade = ''
        if self.intentos > 0:
            anade = '(' + str(self.maxintentos - self.intentos) + ')'
        self['countdown'].setText('%s %s / %s%s' % (_('Countdown:'),
         str(self.countdown),
         str(config.plugins.spzMosaic.countdown.value),
         anade))

    def getEventName(self, info, ref):
        event = info.getEvent(ref)
        if event is not None:
            eventName = event.getEventName()
            if eventName is None:
                eventName = ''
        else:
            eventName = ''
        return eventName


Session = None
Servicelist = None
BouquetSelectorScreen = None

def getBouquetServices(bouquet):
    services = []
    Servicelist = eServiceCenter.getInstance().list(bouquet)
    if Servicelist is not None:
        while True:
            service = Servicelist.getNext()
            if not service.valid():
                break
            if service.flags & (eServiceReference.isDirectory | eServiceReference.isMarker):
                continue
            services.append(service)

    return services


def closeBouquetSelectorScreen(ret = None):
    global BouquetSelectorScreen
    if BouquetSelectorScreen is not None:
        BouquetSelectorScreen.close()
    return ret


def openMosaic(bouquet):
    global Session
    if bouquet is not None:
        services = getBouquetServices(bouquet)
        if len(services):
            Session.openWithCallback(closeBouquetSelectorScreen, Mosaic, services)


def main(session, servicelist, **kwargs):
    global Servicelist
    global Session
    global BouquetSelectorScreen
    Session = session
    if not fileExists('/usr/bin/chkvs'):
        Notifications.AddPopup(text=_('Not spazeTeam image found!\nMore info in www.azboxhd.es').replace('spazeTeam', 'openSPA').replace('www.azboxhd.es', 'openspa.info'), type=MessageBox.TYPE_ERROR, timeout=10, id='spzMosaic')
        return
    Servicelist = servicelist
    if not chequeagrabar(session):
        bouquets = Servicelist.getBouquetList()
        if bouquets is not None:
            if len(bouquets) == 1:
                openMosaic(bouquets[0][1])
            elif len(bouquets) > 1:
                BouquetSelectorScreen = Session.open(BouquetSelector, bouquets, openMosaic, enableWrapAround=True)


def Plugins(**kwargs):
    return PluginDescriptor(name=_('Channels Mosaic'), where=PluginDescriptor.WHERE_EXTENSIONSMENU, fnc=main)
