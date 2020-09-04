from Components.ConfigList import ConfigListScreen
from Components.Label import Label
from Components.Language import language
from Components.Pixmap import MovingPixmap, Pixmap
from enigma import eTimer
from os import environ
from Screens.Screen import Screen
from Tools.Directories import resolveFilename, SCOPE_LANGUAGE, SCOPE_PLUGINS
import gettext
lang = language.getLanguage()
environ['LANGUAGE'] = lang[:2]
gettext.bindtextdomain('enigma2', resolveFilename(SCOPE_LANGUAGE))
gettext.textdomain('enigma2')
gettext.bindtextdomain('TimeSleep', '%s%s' % (resolveFilename(SCOPE_PLUGINS), 'Extensions/MediaCenter/locale/'))

def _(txt):
    t = gettext.dgettext('TimeSleep', txt)
    if t == txt:
        t = gettext.gettext(txt)
    return t


listaopc = [('-180', _('-3 h.')),
 ('-150', _('-2 h. 30 ' + _('min.'))),
 ('-120', _('-2 h.')),
 ('-110', _('-1 h. 50 ' + _('min.'))),
 ('-100', _('-1 h. 40 ' + _('min.'))),
 ('-90', _('-1 h. 30 ' + _('min.'))),
 ('-85', _('-1 h. 25 ' + _('min.'))),
 ('-80', _('-1 h. 20 ' + _('min.'))),
 ('-75', _('-1 h. 15 ' + _('min.'))),
 ('-70', _('-1 h. 10 ' + _('min.'))),
 ('-65', _('-1 h. 5 ' + _('min.'))),
 ('-60', _('-1 h.')),
 ('-55', _('-55 ' + _('min.'))),
 ('-50', _('-50 ' + _('min.'))),
 ('-45', _('-45 ' + _('min.'))),
 ('-40', _('-40 ' + _('min.'))),
 ('-35', _('-35 ' + _('min.'))),
 ('-30', _('-30 ' + _('min.'))),
 ('-25', _('-25 ' + _('min.'))),
 ('-20', _('-20 ' + _('min.'))),
 ('-15', _('-15 ' + _('min.'))),
 ('-10', _('-10 ' + _('min.'))),
 ('-9', _('-9 ' + _('min.'))),
 ('-8', _('-8 ' + _('min.'))),
 ('-7', _('-7 ' + _('min.'))),
 ('-6', _('-6 ' + _('min.'))),
 ('-5', _('-5 ' + _('min.'))),
 ('-4', _('-4 ' + _('min.'))),
 ('-3', _('-3 ' + _('min.'))),
 ('-2', _('-2 ' + _('min.'))),
 ('-1', _('-1 ' + _('min.'))),
 ('-0.5', _('-30 ' + _('sec.'))),
 ('-0.25', _('-15 ' + _('sec.'))),
 ('0.25', _('+15 ' + _('sec.'))),
 ('0.5', _('+30 ' + _('sec.'))),
 ('1', _('+1 ' + _('min.'))),
 ('1.5', _('+1 ' + _('min.') + ' 30 ' + _('sec.'))),
 ('2', _('+2 ' + _('min.'))),
 ('3', _('+3 ' + _('min.'))),
 ('4', _('+4 ' + _('min.'))),
 ('5', _('+5 ' + _('min.'))),
 ('6', _('+6 ' + _('min.'))),
 ('7', _('+7 ' + _('min.'))),
 ('8', _('+8 ' + _('min.'))),
 ('9', _('+9 ' + _('min.'))),
 ('10', _('+10 ' + _('min.'))),
 ('15', _('+15 ' + _('min.'))),
 ('20', _('+20 ' + _('min.'))),
 ('25', _('+25 ' + _('min.'))),
 ('30', _('+30 ' + _('min.'))),
 ('35', _('+35 ' + _('min.'))),
 ('40', _('+40 ' + _('min.'))),
 ('45', _('+45 ' + _('min.'))),
 ('50', _('+50 ' + _('min.'))),
 ('55', _('+55 ' + _('min.'))),
 ('60', _('+1 h.')),
 ('65', _('+1 h. 5 ' + _('min.'))),
 ('70', _('+1 h. 10 ' + _('min.'))),
 ('75', _('+1 h. 15 ' + _('min.'))),
 ('80', _('+1 h. 20 ' + _('min.'))),
 ('85', _('+1 h. 25 ' + _('min.'))),
 ('90', _('+1 h. 30 ' + _('min.'))),
 ('100', _('+1 h. 40 ' + _('min.'))),
 ('110', _('+1 h. 50 ' + _('min.'))),
 ('120', _('+2 h.')),
 ('150', _('+2 h. 30 ' + _('min.'))),
 ('180', _('+3 h.'))]

class timeSleepMC(ConfigListScreen, Screen):
    skin = '\n<screen name="timeSleepMC" position="49,68" size="501,92" title="%s">\n\t\t<widget name="information2" position="5,1" size="26,26" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/images/tmfw-fs8.png" zPosition="5" alphatest="blend" />\n\t\t<widget name="information1" position="5,1" size="26,26" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/images/tmrw-fs8.png" zPosition="6" alphatest="blend" />\n\t\t\n\t\t<widget name="config" position="35,3" size="436,75" scrollbarMode="showOnDemand" transparent="1" />\n\t\t<widget name="cursor" position="115,51" size="20,21" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/images/tmcarolo-fs8.png" zPosition="5" alphatest="blend" />\n\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/images/tmbase-fs8.png" position="118,64" size="272,10" alphatest="blend" zPosition="4" />\n\n\t\t<widget name="time" position="38,56" size="76,19" font="Regular; 15" halign="center" transparent="0" text="0:00:00" zPosition="5" />\n\t\t<widget source="session.CurrentService" render="PositionGauge" position="121,64" size="266,10" zPosition="3" pointer="/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/images/position_pointersk.png:540,0" transparent="1">\n\t\t<convert type="ServicePosition">Gauge</convert>\n\t\t</widget>\t\n\t\t<widget source="session.CurrentService" render="Label" position="393,56" size="76,19" font="Regular; 15" halign="center" transparent="0" text="0:00:00" zPosition="5">\n\t\t<convert type="ServicePosition">Length,ShowHours</convert>\n\t\t</widget>\n\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/images/tmreloj-fs8.png" position="7,31" size="22,21" alphatest="blend" zPosition="4" />\n\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/images/tmfi-fs8.png" position="9,54" size="19,23" alphatest="blend" zPosition="4" />\n\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/images/tmfd-fs8.png" position="477,54" size="19,23" alphatest="blend" zPosition="4" />\n</screen>' % _('TimeSleep')

    def __init__(self, session, instance, fwd):
        global listaopc
        Screen.__init__(self, session)
        self.session = session
        self.fwd = fwd
        self.sensibility = 20
        self.defaulttime = '0.5'
        self.dvd = False
        self.seek = None
        self.percent = 0.0
        self.length = None
        service = None
        if self.fwd == False:
            deftiempo = '-' + self.defaulttime
        else:
            deftiempo = self.defaulttime
        xdeftiempo = int(float(deftiempo) * 60 * 90000)
        if self.fwd == False:
            xdeftiempo = -1 * xdeftiempo
        self.xdeftiempo = xdeftiempo
        self.minuteInput = ConfigSelection(default=deftiempo, choices=listaopc)
        position = 0
        self.positionEntry = ConfigSelection(choices=[' '], default=' ')
        service = self.session.nav.getCurrentService()
        if service:
            self.seek = service.seek()
            if self.seek:
                self.length = self.seek.getLength()
                position = self.seek.getPlayPosition()
                if self.length and position:
                    if int(position[1]) > 0:
                        longitud = float(self.length[1])
                        if longitud <= 0:
                            longitud = 1
                        self.percent = (float(position[1]) + self.xdeftiempo) * 100.0 / longitud
        self.ihora = ConfigSequence(seperator=':', default=[int(position[1] / 60 / 60 / 90000), int(position[1] / 60 / 90000 % 60), int(position[1] / 90000 % 60)], limits=[(0, 9), (0, 59), (0, 59)])
        txt = _('Skip:')
        ConfigListScreen.__init__(self, [getConfigListEntry(txt, self.minuteInput), getConfigListEntry(_('Go to position:'), self.ihora), getConfigListEntry(_(' '), self.positionEntry)])
        self['information1'] = Pixmap()
        self['information2'] = Pixmap()
        self['cursor'] = MovingPixmap()
        self['time'] = Label()
        self['actions'] = ActionMap(['WizardActions',
         'ColorActions',
         'MenuActions',
         'DirectionActions'], {'back': self.exit,
         'menu': self.keyMenu,
         'red': self.goini,
         'blue': self.gofin}, -1)
        self.cursorTimer = eTimer()
        self.cursorTimer.callback.append(self.updateCursor)
        self.cursorTimer.start(200, False)
        self.onLayoutFinish.append(self.firstStart)

    def inicia(self):
        pass

    def firstStart(self):
        self['config'].setCurrentIndex(0)
        if self.fwd:
            self['information2'].hide()
            self['information1'].show()
        else:
            self['information1'].hide()
            self['information2'].show()
        self.updateCursor()

    def keyMenu(self):
        pass

    def goini(self):
        self.percent = 0.0
        self['config'].setCurrentIndex(2)

    def gofin(self):
        self.percent = 100.0
        self['config'].setCurrentIndex(2)

    def updateCursor(self):
        if self.length:
            x = 119 + int(2.66 * self.percent)
            posy = self['cursor'].instance.position().y()
            self['cursor'].moveTo(x - 8, posy, 1)
            self['cursor'].startMoving()
            pts = int(float(self.length[1]) / 100.0 * self.percent)
            self['time'].setText('%d:%02d:%02d' % (pts / 60 / 60 / 90000, pts / 60 / 90000 % 60, pts / 90000 % 60))

    def exit(self):
        self.cursorTimer.stop()
        ConfigListScreen.saveAll(self)
        self.close()

    def keyOK(self):
        sel = self['config'].getCurrent()[1]
        if sel == self.positionEntry:
            if self.length:
                self.seek.seekTo(int(float(self.length[1]) / 100.0 * self.percent))
                self.exit()
        elif sel == self.minuteInput:
            pts = int(float(self.minuteInput.value) * 60 * 90000)
            vaor = self.seek.getPlayPosition()[1] + pts
            if self.length:
                if vaor >= self.length[1]:
                    vaor = self.length[1]
            if vaor < 0:
                vaor = 0
            self.seek.seekTo(vaor)
            self.exit()
        elif sel == self.ihora:
            if self.length:
                vaor = self.ihora.value[0] * 60 * 60 * 90000 + self.ihora.value[1] * 60 * 90000 + self.ihora.value[2] * 90000
                if self.length:
                    if vaor >= self.length[1]:
                        vaor = self.length[1]
                if vaor < 0:
                    vaor = 0
                self.seek.seekTo(vaor)
                self.exit()

    def keyLeft(self):
        sel = self['config'].getCurrent()[1]
        if sel == self.positionEntry:
            self.percent -= float(self.sensibility) / 10.0
            if self.percent < 0.0:
                self.percent = 0.0
        else:
            ConfigListScreen.keyLeft(self)
            if sel == self.minuteInput:
                pts = int(float(self.minuteInput.value) * 60 * 90000)
                longitud = float(self.length[1])
                if longitud <= 0:
                    longitud = 1
                self.percent = float(self.seek.getPlayPosition()[1] + pts) * 100.0 / longitud
                if self.percent < 0.0:
                    self.percent = 0.0
                if self.percent > 100.0:
                    self.percent = 100.0
                if float(self.minuteInput.value) > 0:
                    self['information2'].hide()
                    self['information1'].show()
                else:
                    self['information1'].hide()
                    self['information2'].show()

    def keyRight(self):
        sel = self['config'].getCurrent()[1]
        if sel == self.positionEntry:
            self.percent += float(self.sensibility) / 10.0
            if self.percent > 100.0:
                self.percent = 100.0
        else:
            ConfigListScreen.keyRight(self)
            if sel == self.minuteInput:
                pts = int(float(self.minuteInput.value) * 60 * 90000)
                longitud = float(self.length[1])
                if longitud <= 0:
                    longitud = 1
                self.percent = float(self.seek.getPlayPosition()[1] + pts) * 100.0 / longitud
                if self.percent < 0.0:
                    self.percent = 0.0
                if self.percent > 100.0:
                    self.percent = 100.0
                if float(self.minuteInput.value) > 0:
                    self['information2'].hide()
                    self['information1'].show()
                else:
                    self['information1'].hide()
                    self['information2'].show()

    def keyNumberGlobal(self, number):
        sel = self['config'].getCurrent()[1]
        if sel == self.positionEntry:
            self.percent = float(number) * 10.0
        else:
            ConfigListScreen.keyNumberGlobal(self, number)


def timesleep(instance, fwd = True):
    if instance and instance.session:
        instance.session.open(timeSleepMC, None, fwd)


def timesleepBack(instance):
    timesleep(instance, False)
