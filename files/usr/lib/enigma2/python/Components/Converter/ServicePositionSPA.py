from Converter import Converter
from Poll import Poll
from enigma import iPlayableService
from Components.Element import cached, ElementError
from Components.config import config

class ServicePositionSPA(Poll, Converter, object):
    TYPE_LENGTH = 0
    TYPE_POSITION = 1
    TYPE_REMAINING = 2

    def __init__(self, type):
        Poll.__init__(self)
        Converter.__init__(self, type)
        args = type.split(',')
        type = args.pop(0)
        self.negate = 'Negate' in args
        self.showHours = 'ShowHours' in args
        self.showNoSeconds = 'ShowNoSeconds' in args
        self.noSigno = 'NoSign' in args
        self.noDinamico = 'Fixed' in args
        self.simbolo = 'AddSymbol' in args
        self.soloSimbolo = 'OnlySymbol' in args
        self.carsim = ''
        if type == 'Length':
            self.type = self.TYPE_LENGTH
        elif type == 'Remaining':
            self.type = self.TYPE_REMAINING
        else:
            self.type = self.TYPE_POSITION
        self.poll_interval = 500
        self.poll_enabled = True

    def getSimbolo(self):
        return '>'
        try:
            from Screens.InfoBar import InfoBar
            if InfoBar and InfoBar.instance:
                if InfoBar.instance.SEEK_STATE_PLAY == InfoBar.instance.seekstate:
                    return '>'
                if InfoBar.instance.SEEK_STATE_PAUSE == InfoBar.instance.seekstate:
                    return '||'
                return '\xe2\x80\xa2'
        except:
            return 'x'

    def getSeek(self):
        s = self.source.service
        return s and s.seek()

    @cached
    def getPosition(self):
        seek = self.getSeek()
        if seek is None:
            return
        pos = seek.getPlayPosition()
        if pos[0]:
            return 0
        return pos[1]

    @cached
    def getLength(self):
        seek = self.getSeek()
        if seek is None:
            return
        length = seek.getLength()
        if length[0]:
            return 0
        return length[1]

    @cached
    def getCutlist(self):
        service = self.source.service
        cue = service and service.cueSheet()
        return cue and cue.getCutList()

    @cached
    def getText(self):
        seek = self.getSeek()
        if seek is None:
            return ''
        l = self.length
        p = self.position
        r = self.length - self.position
        if l < 0:
            return ''
        self.carsim = ''
        if self.simbolo or self.soloSimbolo:
            self.carsim = self.getSimbolo()
            if self.soloSimbolo:
                return self.carsim
            self.carsim = '' + self.carsim + ' '
        l /= 90000
        p /= 90000
        r /= 90000
        if self.negate:
            l = -l
        if self.negate:
            p = -p
        if self.negate:
            r = -r
        if l >= 0:
            sign_l = ''
        else:
            l = -l
            sign_l = '-'
        if p >= 0:
            sign_p = ''
        else:
            p = -p
            sign_p = '-'
        if r >= 0:
            sign_r = ''
        else:
            r = -r
            sign_r = '-'
        if config.usage.elapsed_time_positive_osd.getValue():
            sign_p = '+'
            sign_r = '-'
            sign_l = ''
        else:
            sign_p = ''
            sign_r = '+'
            sign_l = ''
        if self.noSigno:
            sign_p = ''
            sign_r = ''
            sign_l = ''
        if not self.noDinamico:
            try:
                if self.type == self.TYPE_LENGTH and l / 3600 + l % 3600 / 60 < 1:
                    return self.carsim + sign_l + '%d' % (l % 60) + 's'
                if self.type == self.TYPE_POSITION and p / 3600 + p % 3600 / 60 < 1:
                    return self.carsim + sign_p + '%d' % (p % 60) + 's'
                if self.type == self.TYPE_REMAINING and r / 3600 + r % 3600 / 60 < 1:
                    return self.carsim + sign_r + '%d' % (r % 60) + 's'
            except:
                pass

        if self.showNoSeconds:
            if self.type == self.TYPE_LENGTH:
                return self.carsim + sign_l + '%d:%02d' % (l / 3600, l % 3600 / 60)
            if self.type == self.TYPE_POSITION:
                return self.carsim + sign_p + '%d:%02d' % (p / 3600, p % 3600 / 60)
            if self.type == self.TYPE_REMAINING:
                return self.carsim + sign_r + '%d:%02d' % (r / 3600, r % 3600 / 60)
        else:
            if self.type == self.TYPE_LENGTH:
                return self.carsim + sign_l + '%d:%02d:%02d' % (l / 3600, l % 3600 / 60, l % 60)
            if self.type == self.TYPE_POSITION:
                return self.carsim + sign_p + '%d:%02d:%02d' % (p / 3600, p % 3600 / 60, p % 60)
            if self.type == self.TYPE_REMAINING:
                return self.carsim + sign_r + '%d:%02d:%02d' % (r / 3600, r % 3600 / 60, r % 60)

    @cached
    def getValue(self):
        pos = self.position
        len = self.length
        if pos is None or len is None or len <= 0:
            return
        return pos * 10000 / len

    position = property(getPosition)
    length = property(getLength)
    cutlist = property(getCutlist)
    text = property(getText)
    value = property(getValue)

    def changed(self, what):
        time_refresh = what[0] == self.CHANGED_POLL or what[0] == self.CHANGED_SPECIFIC and what[1] in (iPlayableService.evCuesheetChanged,)
        if time_refresh:
            self.downstream_elements.changed(what)
