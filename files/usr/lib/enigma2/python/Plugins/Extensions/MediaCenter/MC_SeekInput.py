from Components.Label import Label
from Components.Pixmap import Pixmap, MovingPixmap

class SeekInput(Screen):
    skin = '\n\t\t<screen position="10,10" size="200,60" title="Seekinput" flags="wfNoBorder">\n\t\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/skins/default/images/timeseek_bg.png" position="10,10" zPosition="1" size="180,50" transparent="1" alphatest="on" />\n\t\t\t<widget name="hourspixmap" transparent="1" position="21,18" zPosition="2" size="45,36" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/skins/default/images/timeseek_none.png" alphatest="on" />\n\t\t\t<widget name="minutespixmap" transparent="1" position="77,18" zPosition="2" size="45,36" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/skins/default/images/timeseek_none.png" alphatest="on" />\n\t\t\t<widget name="secondspixmap" transparent="1" position="135,18" zPosition="2" size="45,36" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/skins/default/images/timeseek_sel.png" alphatest="on" />\n\t\t\t<widget name="hours" zPosition="3" transparent="1" halign="left" position="28,24" size="35,25" font="Regular;22" foregroundColor="#f0f0f0"/>\n\t\t\t<widget name="minutes" zPosition="3" transparent="1" halign="left" position="85,24" size="35,25" font="Regular;22" />\n\t\t\t<widget name="seconds" zPosition="3" transparent="1" halign="left" position="143,24" size="35,25" font="Regular;22" foregroundColor="#f0f0f0"/>\n\t\t</screen>'

    def __init__(self, session, command):
        self.skin = SeekInput.skin
        Screen.__init__(self, session)
        self['hours'] = Label()
        self['minutes'] = Label()
        self['seconds'] = Label()
        self['hourspixmap'] = Pixmap()
        self['minutespixmap'] = Pixmap()
        self['secondspixmap'] = Pixmap()
        self['actions'] = NumberActionMap(['MRUAPlayerActions',
         'NumberActions',
         'OkCancelActions',
         'DirectionActions'], {'1': self.keyNumberGlobal,
         '2': self.keyNumberGlobal,
         '3': self.keyNumberGlobal,
         '4': self.keyNumberGlobal,
         '5': self.keyNumberGlobal,
         '6': self.keyNumberGlobal,
         '7': self.keyNumberGlobal,
         '8': self.keyNumberGlobal,
         '9': self.keyNumberGlobal,
         '0': self.keyNumberGlobal,
         'left': self.left,
         'right': self.right,
         'seekFwdinput': self.increase,
         'seekBwdinput': self.decrease,
         'ok': self.ok,
         'cancel': self.cancel})
        self.sel = 'seconds'
        self.prevsel = None
        service = session.nav.getCurrentService()
        if service:
            self.seek = service.seek()
            if self.seek:
                self.lengthpts = self.seek.getLength()
                self.positionpts = self.seek.getPlayPosition()
                self.length = int(self.lengthpts[1]) / 90000
                self.position = int(self.positionpts[1]) / 90000
                if self.length and self.position:
                    if command == 'fwd':
                        self.increase()
                        print self.hours
                    elif command == 'bwd':
                        self.decrease()
                    elif command == 'totime':
                        self.hours = 0
                        self.minutes = 0
                        self.seconds = 0
                        self.update()
                else:
                    self.close(-1)
            else:
                self.close(-1)
        else:
            self.close(-1)

    def convert(self, inseconds):
        self.seconds = inseconds
        self.minutes, self.seconds = divmod(self.seconds, 60)
        self.hours, self.minutes = divmod(self.minutes, 60)

    def validate(self, hours, minutes, seconds):
        newlength = hours * 3600 + minutes * 60 + seconds
        if newlength < self.length:
            return 1
        else:
            return 0

    def update(self):
        self['hours'].setText('%02d' % self.hours)
        self['minutes'].setText('%02d' % self.minutes)
        self['seconds'].setText('%02d' % self.seconds)

    def keyNumberGlobal(self, number):
        if self.sel == 'hours':
            if self.prevsel == 'hours' and self.hours < 10:
                newvalue = self.hours * 10 + number
                if self.validate(newvalue, self.minutes, self.seconds) == 1:
                    self.hours = newvalue
                    self.update()
                self.prevsel = None
            elif self.validate(number, self.minutes, self.seconds) == 1:
                self.hours = number
                self.update()
                self.prevsel = 'hours'
        elif self.sel == 'minutes':
            if self.prevsel == 'minutes' and self.minutes < 6:
                newvalue = self.minutes * 10 + number
                if self.validate(self.hours, newvalue, self.seconds) == 1:
                    self.minutes = newvalue
                    self.update()
                self.prevsel = None
            elif self.validate(self.hours, number, self.seconds) == 1:
                self.minutes = number
                self.update()
                self.prevsel = 'minutes'
        elif self.sel == 'seconds':
            if self.prevsel == 'seconds' and self.hours < 6:
                newvalue = self.seconds * 10 + number
                if self.validate(self.hours, self.minutes, newvalue) == 1:
                    self.seconds = newvalue
                    self.update()
                self.prevsel = None
            elif self.validate(self.hours, self.minutes, number) == 1:
                self.seconds = number
                self.update()
                self.prevsel = 'seconds'

    def left(self):
        if self.sel == 'hours':
            self['hourspixmap'].instance.setPixmapFromFile('/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/skins/default/images/timeseek_none.png')
            self['secondspixmap'].instance.setPixmapFromFile('/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/skins/default/images/timeseek_sel.png')
            self.sel = 'seconds'
        elif self.sel == 'minutes':
            self['minutespixmap'].instance.setPixmapFromFile('/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/skins/default/images/timeseek_none.png')
            self['hourspixmap'].instance.setPixmapFromFile('/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/skins/default/images/timeseek_sel.png')
            self.sel = 'hours'
        elif self.sel == 'seconds':
            self['secondspixmap'].instance.setPixmapFromFile('/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/skins/default/images/timeseek_none.png')
            self['minutespixmap'].instance.setPixmapFromFile('/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/skins/default/images/timeseek_sel.png')
            self.sel = 'minutes'

    def right(self):
        if self.sel == 'hours':
            self['hourspixmap'].instance.setPixmapFromFile('/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/skins/default/images/timeseek_none.png')
            self['minutespixmap'].instance.setPixmapFromFile('/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/skins/default/images/timeseek_sel.png')
            self.sel = 'minutes'
        elif self.sel == 'minutes':
            self['minutespixmap'].instance.setPixmapFromFile('/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/skins/default/images/timeseek_none.png')
            self['secondspixmap'].instance.setPixmapFromFile('/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/skins/default/images/timeseek_sel.png')
            self.sel = 'seconds'
        elif self.sel == 'seconds':
            self['secondspixmap'].instance.setPixmapFromFile('/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/skins/default/images/timeseek_none.png')
            self['hourspixmap'].instance.setPixmapFromFile('/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/skins/default/images/timeseek_sel.png')
            self.sel = 'hours'

    def ok(self):
        self.close((self.hours * 3600 + self.minutes * 60 + self.seconds) * 90000)

    def cancel(self):
        self.close(-1)

    def increase(self):
        self.position += 15
        if self.position < self.length:
            self.convert(self.position)
            self.update()
        else:
            self.position = self.length - 15
            self.convert(self.position)
            self.update()

    def decrease(self):
        self.position -= 15
        if self.position >= 0:
            self.convert(self.position)
            self.update()
        elif self.position < 0:
            self.convert(0)
            self.update()
