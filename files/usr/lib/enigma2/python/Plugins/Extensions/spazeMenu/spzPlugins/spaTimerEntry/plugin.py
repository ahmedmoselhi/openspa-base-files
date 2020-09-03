from Components.config import config, ConfigSelection, ConfigText, ConfigSubList, ConfigDateTime, ConfigClock, ConfigYesNo, getConfigListEntry, ConfigNumber
from Screens import TimerEntry
from Components.PluginComponent import plugins
from Plugins.Plugin import PluginDescriptor
from Screens.MovieSelection import getPreferredTagEditor
from time import localtime, time, strftime
from RecordTimer import AFTEREVENT
from Components.SystemInfo import SystemInfo
from Components.UsageConfig import defaultMoviePath
from Components.ConfigList import ConfigListScreen
from enigma import eEPGCache
from ServiceReference import ServiceReference
from os import path as os_path
import xml.etree.cElementTree as ET
from datetime import datetime
from TimerList import spaTimerList
from Screens.Screen import Screen
from skin import dom_screens
from Components.Button import Button
from Components.ActionMap import ActionMap
from Screens.MessageBox import MessageBox
from . import _
from Plugins.Extensions.spazeMenu.spzVirtualKeyboard import spzVirtualKeyboard
from timertasker import tsTasker

def autostart(reason, **kwargs):
    try:
        TimerEntry.TimerEntry.createConfig = spa_createConfig
        TimerEntry.TimerEntry.createSetup = spa_createSetup
        TimerEntry.TimerEntry.keyLeft = spa_keyLeft
        TimerEntry.TimerEntry.keyGo = spa_keyGo
        TimerEntry.TimerEntry.renameEntry = spa_renameEntry
    except:
        pass

    if reason == 0 and kwargs.has_key('session'):
        session = kwargs['session']
        tsTasker.Initialize(session)


def start(session, **kwargs):
    session.open(spaTimerEditList)


def mainmenu(menuid):
    if menuid != 'timermenu':
        return []
    return [(_('TV Series Timers'),
      start,
      'startspaTimers',
      None)]


def spa_createConfig(self):
    justplay = self.timer.justplay
    always_zap = self.timer.always_zap
    zap_wakeup = self.timer.zap_wakeup
    rename_repeat = self.timer.rename_repeat
    afterevent = {AFTEREVENT.NONE: 'nothing',
     AFTEREVENT.DEEPSTANDBY: 'deepstandby',
     AFTEREVENT.STANDBY: 'standby',
     AFTEREVENT.AUTO: 'auto'}[self.timer.afterEvent]
    if self.timer.record_ecm and self.timer.descramble:
        recordingtype = 'descrambled+ecm'
    elif self.timer.record_ecm:
        recordingtype = 'scrambled+ecm'
    elif self.timer.descramble:
        recordingtype = 'normal'
    weekday_table = ('mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun')
    day = []
    weekday = 0
    for x in (0, 1, 2, 3, 4, 5, 6):
        day.append(0)

    if self.timer.repeated:
        type = 'repeated'
        if self.timer.repeated == 31:
            repeated = 'weekdays'
        elif self.timer.repeated == 127:
            repeated = 'daily'
        else:
            flags = self.timer.repeated
            repeated = 'user'
            count = 0
            for x in (0, 1, 2, 3, 4, 5, 6):
                if flags == 1:
                    print 'Set to weekday ' + str(x)
                    weekday = x
                if flags & 1 == 1:
                    day[x] = 1
                    count += 1
                else:
                    day[x] = 0
                flags = flags >> 1

            if count == 1:
                repeated = 'weekly'
    else:
        type = 'once'
        repeated = None
        weekday = int(strftime('%u', localtime(self.timer.begin))) - 1
        day[weekday] = 1
    self.timerentry_justplay = ConfigSelection(choices=[('zap', _('zap')), ('record', _('record')), ('zap+record', _('zap and record'))], default={0: 'record',
     1: 'zap',
     2: 'zap+record'}[justplay + 2 * always_zap])
    if SystemInfo['DeepstandbySupport']:
        shutdownString = _('go to deep standby')
        choicelist = [('always', _('always')),
         ('from_standby', _('only from standby')),
         ('from_deep_standby', _('only from deep standby')),
         ('never', _('never'))]
    else:
        shutdownString = _('shut down')
        choicelist = [('always', _('always')), ('never', _('never'))]
    self.timerentry_zapwakeup = ConfigSelection(choices=choicelist, default=zap_wakeup)
    self.timerentry_afterevent = ConfigSelection(choices=[('nothing', _('do nothing')),
     ('standby', _('go to standby')),
     ('deepstandby', shutdownString),
     ('auto', _('auto'))], default=afterevent)
    self.timerentry_recordingtype = ConfigSelection(choices=[('normal', _('normal')), ('descrambled+ecm', _('descramble and record ecm')), ('scrambled+ecm', _("don't descramble, record ecm"))], default=recordingtype)
    self.timerentry_type = ConfigSelection(choices=[('once', _('once')), ('repeated', _('repeated'))], default=type)
    self.timerentry_name = ConfigText(default=self.timer.name, visible_width=50, fixed_size=False)
    self.timerentry_description = ConfigText(default=self.timer.description, visible_width=50, fixed_size=False)
    self.timerentry_tags = self.timer.tags[:]
    self.timerentry_tagsset = ConfigSelection(choices=[not self.timerentry_tags and 'None' or ' '.join(self.timerentry_tags)])
    season, episode = tsTasker.extractSeason(self.timer.name, self.timer.description)
    tmp = [('weekly', _('weekly')),
     ('daily', _('daily')),
     ('weekdays', _('Mon-Fri')),
     ('user', _('user defined')),
     ('by_title', _('By Name'))]
    if episode > 0:
        tmp.append(('series', _('TV Series')))
    self.timerentry_repeated = ConfigSelection(default=repeated, choices=tmp)
    self.timerentry_renamerepeat = ConfigYesNo(default=rename_repeat)
    self.timerentry_season = ConfigNumber(default=season)
    self.timerentry_date = ConfigDateTime(default=self.timer.begin, formatstring=_('%d.%B %Y'), increment=86400)
    self.timerentry_starttime = ConfigClock(default=self.timer.begin)
    self.timerentry_endtime = ConfigClock(default=self.timer.end)
    self.timerentry_showendtime = ConfigSelection(default=self.timer.end - self.timer.begin > 4, choices=[(True, _('yes')), (False, _('no'))])
    default = self.timer.dirname or defaultMoviePath()
    tmp = config.movielist.videodirs.value
    if default not in tmp:
        tmp.append(default)
    self.timerentry_dirname = ConfigSelection(default=default, choices=tmp)
    self.timerentry_repeatedbegindate = ConfigDateTime(default=self.timer.repeatedbegindate, formatstring=_('%d.%B %Y'), increment=86400)
    self.timerentry_weekday = ConfigSelection(default=weekday_table[weekday], choices=[('mon', _('Monday')),
     ('tue', _('Tuesday')),
     ('wed', _('Wednesday')),
     ('thu', _('Thursday')),
     ('fri', _('Friday')),
     ('sat', _('Saturday')),
     ('sun', _('Sunday'))])
    self.timerentry_day = ConfigSubList()
    for x in (0, 1, 2, 3, 4, 5, 6):
        self.timerentry_day.append(ConfigYesNo(default=day[x]))

    servicename = 'N/A'
    try:
        servicename = str(self.timer.service_ref.getServiceName())
    except:
        pass

    self.timerentry_service_ref = self.timer.service_ref
    self.timerentry_service = ConfigSelection([servicename])


def spa_createSetup(self, widget):
    self.list = []
    self.entryName = getConfigListEntry(_('Name'), self.timerentry_name)
    self.list.append(self.entryName)
    self.entryDescription = getConfigListEntry(_('Description'), self.timerentry_description)
    self.list.append(self.entryDescription)
    self.timerJustplayEntry = getConfigListEntry(_('Timer type'), self.timerentry_justplay)
    self.list.append(self.timerJustplayEntry)
    self.timerTypeEntry = getConfigListEntry(_('Repeat type'), self.timerentry_type)
    self.list.append(self.timerTypeEntry)
    if self.timerentry_type.value == 'once':
        self.frequencyEntry = None
    else:
        self.frequencyEntry = getConfigListEntry(_('Repeats'), self.timerentry_repeated)
        self.list.append(self.frequencyEntry)
        self.repeatedbegindateEntry = getConfigListEntry(_('Starting on'), self.timerentry_repeatedbegindate)
        self.list.append(self.repeatedbegindateEntry)
        if self.timerentry_repeated.value == 'series':
            self.list.append(getConfigListEntry(_('Season (0 for all seasons)'), self.timerentry_season))
        if self.timerentry_repeated.value == 'daily':
            pass
        if self.timerentry_repeated.value == 'weekdays':
            pass
        if self.timerentry_repeated.value == 'weekly':
            self.list.append(getConfigListEntry(_('Weekday'), self.timerentry_weekday))
        if self.timerentry_repeated.value == 'user':
            self.list.append(getConfigListEntry(_('Monday'), self.timerentry_day[0]))
            self.list.append(getConfigListEntry(_('Tuesday'), self.timerentry_day[1]))
            self.list.append(getConfigListEntry(_('Wednesday'), self.timerentry_day[2]))
            self.list.append(getConfigListEntry(_('Thursday'), self.timerentry_day[3]))
            self.list.append(getConfigListEntry(_('Friday'), self.timerentry_day[4]))
            self.list.append(getConfigListEntry(_('Saturday'), self.timerentry_day[5]))
            self.list.append(getConfigListEntry(_('Sunday'), self.timerentry_day[6]))
        if self.timerentry_justplay.value != 'zap':
            self.list.append(getConfigListEntry(_('Rename name and description for new events'), self.timerentry_renamerepeat))
    self.entryDate = getConfigListEntry(_('Date'), self.timerentry_date)
    if self.timerentry_type.value == 'once':
        self.list.append(self.entryDate)
    self.entryStartTime = getConfigListEntry(_('Start time'), self.timerentry_starttime)
    if self.timerentry_repeated.value != 'series' and self.timerentry_repeated.value != 'by_title':
        self.list.append(self.entryStartTime)
    self.entryShowEndTime = getConfigListEntry(_('Set end time'), self.timerentry_showendtime)
    self.entryZapWakeup = getConfigListEntry(_('Wakeup receiver for start timer'), self.timerentry_zapwakeup)
    if self.timerentry_justplay.value == 'zap':
        self.list.append(self.entryZapWakeup)
        self.list.append(self.entryShowEndTime)
        self['key_blue'].setText(_('Wakeup type'))
    else:
        self['key_blue'].setText('')
    self.entryEndTime = getConfigListEntry(_('End time'), self.timerentry_endtime)
    if (self.timerentry_justplay.value != 'zap' or self.timerentry_showendtime.value) and self.timerentry_repeated.value != 'series' and self.timerentry_repeated.value != 'by_title':
        self.list.append(self.entryEndTime)
    self.channelEntry = getConfigListEntry(_('Channel'), self.timerentry_service)
    self.list.append(self.channelEntry)
    self.dirname = getConfigListEntry(_('Location'), self.timerentry_dirname)
    self.tagsSet = getConfigListEntry(_('Tags'), self.timerentry_tagsset)
    if self.timerentry_justplay.value != 'zap':
        if config.usage.setup_level.index >= 2:
            self.list.append(self.dirname)
        if getPreferredTagEditor():
            self.list.append(self.tagsSet)
        self.list.append(getConfigListEntry(_('After event'), self.timerentry_afterevent))
        self.list.append(getConfigListEntry(_('Recording type'), self.timerentry_recordingtype))
    self[widget].list = self.list
    self[widget].l.setList(self.list)


def spa_keyLeft(self):
    cur = self['config'].getCurrent()
    if cur in (self.channelEntry, self.tagsSet):
        if self.timerentry_repeated.value == 'series' or self.timerentry_repeated.value == 'by_title':
            self.timerentry_service_ref = None
            self.timerentry_service.setCurrentText(_('All'))
            self['config'].invalidate(self.channelEntry)
        else:
            self.keySelect()
    elif cur in (self.entryName, self.entryDescription):
        self.renameEntry()
    else:
        ConfigListScreen.keyLeft(self)
        self.newConfig()


def spa_renameEntry(self):
    cur = self['config'].getCurrent()
    if cur == self.entryName:
        title_text = _('Please enter new name:')
        old_text = self.timerentry_name.value
    else:
        title_text = _('Please enter new description:')
        old_text = self.timerentry_description.value
    self.session.openWithCallback(self.renameEntryCallback, spzVirtualKeyboard, titulo=title_text, texto=old_text, ok=True)


def spa_keyGo(self, result = None):

    def exiting(ret):
        self.close((False,))

    if self.timerentry_repeated.value != 'series' and self.timerentry_repeated.value != 'by_title':
        if not self.timerentry_service_ref.isRecordable():
            self.session.openWithCallback(self.selectChannelSelector, MessageBox, _("You didn't select a channel to record from."), MessageBox.TYPE_ERROR)
            return
        self.timer.name = self.timerentry_name.value
        self.timer.description = self.timerentry_description.value
        self.timer.justplay = self.timerentry_justplay.value == 'zap'
        self.timer.always_zap = self.timerentry_justplay.value == 'zap+record'
        self.timer.zap_wakeup = self.timerentry_zapwakeup.value
        self.timer.rename_repeat = self.timerentry_renamerepeat.value
        if self.timerentry_justplay.value == 'zap':
            if not self.timerentry_showendtime.value:
                self.timerentry_endtime.value = self.timerentry_starttime.value
                self.timerentry_afterevent.value = 'nothing'
        self.timer.resetRepeated()
        self.timer.afterEvent = {'nothing': AFTEREVENT.NONE,
         'deepstandby': AFTEREVENT.DEEPSTANDBY,
         'standby': AFTEREVENT.STANDBY,
         'auto': AFTEREVENT.AUTO}[self.timerentry_afterevent.value]
        self.timer.descramble = {'normal': True,
         'descrambled+ecm': True,
         'scrambled+ecm': False}[self.timerentry_recordingtype.value]
        self.timer.record_ecm = {'normal': False,
         'descrambled+ecm': True,
         'scrambled+ecm': True}[self.timerentry_recordingtype.value]
        self.timer.service_ref = self.timerentry_service_ref
        self.timer.tags = self.timerentry_tags
        if self.timer.dirname or self.timerentry_dirname.value != defaultMoviePath():
            self.timer.dirname = self.timerentry_dirname.value
            config.movielist.last_timer_videodir.value = self.timer.dirname
            config.movielist.last_timer_videodir.save()
        if self.timerentry_type.value == 'once':
            self.timer.begin, self.timer.end = self.getBeginEnd()
        if self.timerentry_type.value == 'repeated':
            if self.timerentry_repeated.value == 'daily':
                for x in (0, 1, 2, 3, 4, 5, 6):
                    self.timer.setRepeated(x)

            if self.timerentry_repeated.value == 'weekly':
                self.timer.setRepeated(self.timerentry_weekday.index)
            if self.timerentry_repeated.value == 'weekdays':
                for x in (0, 1, 2, 3, 4):
                    self.timer.setRepeated(x)

            if self.timerentry_repeated.value == 'user':
                for x in (0, 1, 2, 3, 4, 5, 6):
                    if self.timerentry_day[x].value:
                        self.timer.setRepeated(x)

            self.timer.repeatedbegindate = self.getTimestamp(self.timerentry_repeatedbegindate.value, self.timerentry_starttime.value)
            if self.timer.repeated:
                self.timer.begin = self.getTimestamp(self.timerentry_repeatedbegindate.value, self.timerentry_starttime.value)
                self.timer.end = self.getTimestamp(self.timerentry_repeatedbegindate.value, self.timerentry_endtime.value)
            else:
                self.timer.begin = self.getTimestamp(time.time(), self.timerentry_starttime.value)
                self.timer.end = self.getTimestamp(time.time(), self.timerentry_endtime.value)
            if self.timer.end < self.timer.begin:
                self.timer.end += 86400
        if self.timer.eit is not None:
            event = eEPGCache.getInstance().lookupEventId(self.timer.service_ref.ref, self.timer.eit)
            if event:
                n = event.getNumOfLinkageServices()
                if n > 1:
                    tlist = []
                    ref = self.session.nav.getCurrentlyPlayingServiceOrGroup()
                    parent = self.timer.service_ref.ref
                    selection = 0
                    for x in range(n):
                        i = event.getLinkageService(parent, x)
                        if i.toString() == ref.toString():
                            selection = x
                        tlist.append((i.getName(), i))

                    self.session.openWithCallback(self.subserviceSelected, ChoiceBox, title=_('Please select a subservice to record...'), list=tlist, selection=selection)
                    return
                if n > 0:
                    parent = self.timer.service_ref.ref
                    self.timer.service_ref = ServiceReference(event.getLinkageService(parent, 0))
        self.saveTimer()
        self.close((True, self.timer))
    else:
        records = tsTasker.searchEPG(self.timerentry_name.value, self.timerentry_service_ref, self.timerentry_season.value, self.timerentry_repeatedbegindate.value, self.timerentry_justplay.value, self.timerentry_repeated.value, self.timerentry_dirname.value, self.timerentry_afterevent.value, self.timerentry_recordingtype.value)
        open('/tmp/spaTimerEntry.log', 'a').write(strftime('%d/%m/%y %H:%M:%S') + ' %d Records Append\n' % records)
        self.session.openWithCallback(exiting, MessageBox, self.timerentry_name.value + '\n' + _('Append %d events to Record Timers.') % records, type=1, timeout=8)


class spaTimerEditList(Screen):

    def __init__(self, session):
        Screen.__init__(self, session)
        self.skinName = 'TimerEditList'
        list = []
        self.list = list
        self.session = session
        self.setTitle(_('TV Series Timers'))
        self.spa_autotimers = None
        self.fillTimerList()
        self['timerlist'] = spaTimerList(list, True)
        self['key_red'] = Button(_('Exit'))
        self['key_green'] = Button(' ')
        self['key_yellow'] = Button(' ')
        self['key_blue'] = Button(' ')
        self['actions'] = ActionMap(['OkCancelActions',
         'DirectionActions',
         'ShortcutActions',
         'TimerEditActions'], {'red': self.exit,
         'cancel': self.exit,
         'left': self.left,
         'right': self.right,
         'up': self.up,
         'down': self.down}, -1)
        self.updateState()

    def fillTimerList(self):
        list = self.list
        del list[:]
        if os_path.exists('/etc/enigma2/spa_autotimers.xml'):
            self.spa_autotimers = ET.parse('/etc/enigma2/spa_autotimers.xml').getroot()
        else:
            self.spa_autotimers = ET.fromstring('<?xml version="1.0" ?>\n<spatimers>\n</spatimers>')
        if self.spa_autotimers:
            list.extend([ (timer,) for timer in self.spa_autotimers.findall('spatimer') ])

    def openEdit(self):
        self.session.openWithCallback(self.fillTimerList, spaTimerEntries, self['timerlist'].getCurrent())

    def up(self):
        self['timerlist'].instance.moveSelection(self['timerlist'].instance.moveUp)
        self.updateState()

    def down(self):
        self['timerlist'].instance.moveSelection(self['timerlist'].instance.moveDown)
        self.updateState()

    def left(self):
        self['timerlist'].instance.moveSelection(self['timerlist'].instance.pageUp)
        self.updateState()

    def right(self):
        self['timerlist'].instance.moveSelection(self['timerlist'].instance.pageDown)
        self.updateState()

    def updateState(self):
        cur = self['timerlist'].getCurrent()
        if cur:
            self['actions'].actions.update({'yellow': self.removeTimerQuestion})
            self['key_yellow'].setText(_('Delete'))
            self['actions'].actions.update({'green': self.openEdit})
            self['actions'].actions.update({'ok': self.openEdit})
            self['key_green'].setText(_('View Entries'))

    def removeTimerQuestion(self):
        cur = self['timerlist'].getCurrent()
        if not cur:
            return
        self.session.openWithCallback(self.removeTimer, MessageBox, _('Do you really want to delete %s?') % cur.find('name').text)

    def removeTimer(self, result):
        if not result:
            return
        list1 = self['timerlist']
        cur = list1.getCurrent()
        if cur and self.spa_autotimers:
            timer = cur
            self.spa_autotimers.remove(timer)
            tree = ET.ElementTree(self.spa_autotimers)
            tree.write('/etc/enigma2/spa_autotimers.xml')
            self.refill()
            self.updateState()

    def refill(self):
        oldsize = len(self.list)
        self.fillTimerList()
        lst = self['timerlist']
        newsize = len(self.list)
        if oldsize and oldsize != newsize:
            idx = lst.getCurrentIndex()
            lst.entryRemoved(idx)
        else:
            lst.invalidate()

    def exit(self):
        self.close()


class spaTimerEntries(Screen):

    def __init__(self, session, current):
        Screen.__init__(self, session)
        self.skinName = 'TimerEditList'
        list = []
        self.list = list
        self.session = session
        self.spa_autotimer = current
        self.name = current.find('name').text.encode('UTF-8')
        self.justplay = current.find('justplay').text
        self.type = current.find('type').text
        self.dirname = current.find('path').text
        self.setTitle(self.name)
        self.fillTimerList()
        self['timerlist'] = spaTimerList(list, False)
        self['key_red'] = Button(_('Exit'))
        self['key_green'] = Button(' ')
        self['key_yellow'] = Button(' ')
        self['key_blue'] = Button(' ')
        self['actions'] = ActionMap(['OkCancelActions',
         'DirectionActions',
         'ShortcutActions',
         'TimerEditActions'], {'cancel': self.exit,
         'red': self.exit,
         'left': self.left,
         'right': self.right,
         'up': self.up,
         'down': self.down}, -1)

    def fillTimerList(self):
        list = self.list
        del list[:]
        if self.spa_autotimer:
            list.extend([ (timer,
             self.name,
             self.justplay,
             self.type,
             self.dirname) for timer in self.spa_autotimer.findall('entry') ])

    def up(self):
        self['timerlist'].instance.moveSelection(self['timerlist'].instance.moveUp)

    def down(self):
        self['timerlist'].instance.moveSelection(self['timerlist'].instance.moveDown)

    def left(self):
        self['timerlist'].instance.moveSelection(self['timerlist'].instance.pageUp)

    def right(self):
        self['timerlist'].instance.moveSelection(self['timerlist'].instance.pageDown)

    def exit(self):
        self.close()


def Plugins(**kwargs):
    list = []
    list = [PluginDescriptor(where=[PluginDescriptor.WHERE_AUTOSTART, PluginDescriptor.WHERE_SESSIONSTART], fnc=autostart)]
    list.append(PluginDescriptor(name=_('TV Series Timers'), where=PluginDescriptor.WHERE_MENU, fnc=mainmenu))
    return list
