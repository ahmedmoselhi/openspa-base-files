from enigma import eTimer, eEPGCache
from time import localtime, mktime, time, strftime
from RecordTimer import AFTEREVENT
import xml.etree.cElementTree as ET
from RecordTimer import RecordTimerEntry
from operator import itemgetter
from os import path as os_path
import re
from ServiceReference import ServiceReference
from datetime import datetime
import NavigationInstance
from Components.config import config

class timerScriptTasker():

    def __init__(self):
        self.restartTimer = eTimer()
        self.restartTimer.timeout.get().append(self.RestartTimerStart)
        self.minutes = 0
        self.timerActive = False

    def Initialize(self, session):
        self.session = session
        from Plugins.Extensions.spazeMenu.DelayedFunction import DelayedFunction
        DelayedFunction(60000, self.RestartTimerStart, True)

    def RestartTimerStart(self, initializing = False, postponeDelay = 0):
        try:
            self.restartTimer.stop()
            self.timerActive = False
            if postponeDelay > 0:
                self.restartTimer.start(postponeDelay * 60000, False)
                self.timerActive = True
                mints = postponeDelay % 60
                hours = postponeDelay / 60
                return
            lotime = localtime()
            xtimem = lotime[3] * 60 + lotime[4]
            ytimem = 480
            minsToGo = ytimem - xtimem
            if initializing or minsToGo > 0:
                if minsToGo < 0:
                    minsToGo += 1440
                elif minsToGo == 0:
                    minsToGo = 1
                open('/tmp/spaTimerEntry.log', 'a').write(strftime('%d/%m/%y %H:%M:%S') + ' %d minutes to go\n' % minsToGo)
                self.restartTimer.start(minsToGo * 60000, False)
                self.timerActive = True
                self.minutes = minsToGo
                mints = self.minutes % 60
                hours = self.minutes / 60
            else:
                self.InitRestart()
        except Exception as e:
            print '[spatimerentry] RestartTimerStart exception:\n' + str(e)
            self.RestartTimerStart(True, 30)

    def searchEPG(self, ename, timerentry_service_ref, timerentry_season, begindate, justplay, tipo, dirname, afterevent, recordtype):
        epgcache = eEPGCache.getInstance()
        epgmatches = epgcache.search(('RITBDSE',
         1000,
         eEPGCache.PARTIAL_TITLE_SEARCH,
         ename,
         eEPGCache.NO_CASE_CHECK)) or []
        epgmatches.sort(key=itemgetter(3))
        records = 0
        spa_autotimers = None
        if os_path.exists('/etc/enigma2/spa_autotimers.xml'):
            spa_autotimers = ET.parse('/etc/enigma2/spa_autotimers.xml').getroot()
        else:
            spa_autotimers = ET.fromstring('<?xml version="1.0" ?>\n<spatimers>\n</spatimers>')
        open('/tmp/spaTimerEntry.log', 'a').write(strftime('%d/%m/%y %H:%M:%S') + ' start search in EPG for %s\n' % ename)
        print '[spatimerentry] start search in EPG for %s\n' % ename
        for idx, (serviceref, eit, name, begin, duration, shortdesc, extdesc) in enumerate(epgmatches):
            if timerentry_service_ref:
                eserviceref = timerentry_service_ref.__str__()
            else:
                eserviceref = ''
            if serviceref == eserviceref or not timerentry_service_ref:
                if tipo != 'by_title':
                    season, episode = self.extractSeason(name, shortdesc + ' ' + extdesc)
                else:
                    season = episode = 0
                if episode > 0:
                    txtextra = ' [T:%d E:%d]' % (season, episode)
                else:
                    txtextra = ''
                if tipo != 'by_title' and episode == 0:
                    continue
                find = False
                channel = ServiceReference(serviceref).getServiceName()
                open('/tmp/spaTimerEntry.log', 'a').write(strftime('%d/%m/%y %H:%M:%S') + ' Event found. [%s] - %s - [%s] ... ' % (name, channel, strftime('%d/%m/%y %H:%M:%S', localtime(begin))))
                if spa_autotimers:
                    for timer in spa_autotimers.findall('spatimer'):
                        append = True
                        if timer.find('name').text.encode('UTF-8') == ename:
                            find = True
                            for element in timer.findall('entry'):
                                if element.find('episode').text == str(episode) and element.find('season').text == str(season):
                                    open('/tmp/spaTimerEntry.log', 'a').write('No Append. Event duplicate' + txtextra + '\n')
                                    append = False
                                    break

                            break

                if not find:
                    timer = ET.SubElement(spa_autotimers, 'spatimer')
                    xname = ET.SubElement(timer, 'name')
                    xname.text = ename.encode('UTF-8')
                    xdbegin = ET.SubElement(timer, 'StartDate')
                    xdbegin.text = str(begindate)
                    xservice = ET.SubElement(timer, 'Serviceref')
                    xservice.text = str(eserviceref)
                    xseason = ET.SubElement(timer, 'Season')
                    xseason.text = str(timerentry_season)
                    xjustplay = ET.SubElement(timer, 'justplay')
                    xjustplay.text = justplay
                    xtype = ET.SubElement(timer, 'type')
                    xtype.text = tipo
                    xtype = ET.SubElement(timer, 'path')
                    xtype.text = dirname
                    xafter = ET.SubElement(timer, 'afterevent')
                    xafter.text = afterevent
                    xrecord = ET.SubElement(timer, 'recordtype')
                    xrecord.text = recordtype
                    append = True
                if timerentry_season > 0 and season != timerentry_season:
                    append = False
                d = localtime(begindate)
                dt = datetime(d.tm_year, d.tm_mon, d.tm_mday, 8, 0)
                bdate = start = int(mktime(dt.timetuple()))
                d = localtime()
                dt = datetime(d.tm_year, d.tm_mon, d.tm_mday, 8, 0)
                start = int(mktime(dt.timetuple()))
                if (begin < start or begin > start + 86400 or start < bdate) and append:
                    open('/tmp/spaTimerEntry.log', 'a').write('No Append. Time out' + txtextra + '\n')
                    append = False
                if append:
                    open('/tmp/spaTimerEntry.log', 'a').write('Event Append.' + txtextra + '\n')
                    print '[spatimerentry] Event Append.' + txtextra + '\n'
                    element = ET.SubElement(timer, 'entry')
                    xserviceref = ET.SubElement(element, 'serviceref')
                    xserviceref.text = serviceref
                    xname = ET.SubElement(element, 'name')
                    xname.text = name
                    xbegin = ET.SubElement(element, 'begin')
                    xbegin.text = str(begin)
                    xduration = ET.SubElement(element, 'duration')
                    xduration.text = str(duration)
                    xseason = ET.SubElement(element, 'season')
                    xseason.text = str(season)
                    xepisode = ET.SubElement(element, 'episode')
                    xepisode.text = str(episode)
                    try:
                        begin = begin - config.recording.margin_before.value * 60
                        duration = duration + (config.recording.margin_before.value + config.recording.margin_after.value) * 60
                    except:
                        pass

                    end = begin + duration
                    if episode > 0:
                        n = name.find('(')
                        name = name[:n] + ' (T' + str(season) + ') (E' + str(episode) + ')'
                    newEntry = RecordTimerEntry(ServiceReference(serviceref), begin, end, name, shortdesc + extdesc, eit)
                    newEntry.dirname = dirname
                    newEntry.justplay = justplay == 'zap'
                    newEntry.always_zap = justplay == 'zap+record'
                    newEntry.afterEvent = {'nothing': AFTEREVENT.NONE,
                     'deepstandby': AFTEREVENT.DEEPSTANDBY,
                     'standby': AFTEREVENT.STANDBY,
                     'auto': AFTEREVENT.AUTO}[afterevent]
                    newEntry.descramble = {'normal': True,
                     'descrambled+ecm': True,
                     'scrambled+ecm': False}[recordtype]
                    newEntry.record_ecm = {'normal': False,
                     'descrambled+ecm': True,
                     'scrambled+ecm': True}[recordtype]
                    recordHandler = NavigationInstance.instance.RecordTimer
                    conflicts = recordHandler.record(newEntry)
                    records += 1

        open('/tmp/spaTimerEntry.log', 'a').write(strftime('%d/%m/%y %H:%M:%S') + ' Search End.\n')
        if spa_autotimers:
            tree = ET.ElementTree(spa_autotimers)
            tree.write('/etc/enigma2/spa_autotimers.xml')
        return records

    def extractSeason(self, name, description):
        if len(description) > 0:
            patron = '\\(T([^\\)]+)\\)'
            matches = re.compile(patron, re.DOTALL).findall(name)
            if len(matches) > 0:
                try:
                    season = int(matches[0])
                except:
                    season = 1

            else:
                season = 1
            patron = '"Episodio ([^"]+)"'
            matches = re.compile(patron, re.DOTALL).findall(description)
            if len(matches) > 0:
                try:
                    episode = int(matches[0])
                except:
                    episode = 0

            else:
                patron = "'Episodio ([^']+)'"
                matches = re.compile(patron, re.DOTALL).findall(description)
                if len(matches) > 0:
                    try:
                        episode = int(matches[0])
                    except:
                        episode = 0

                else:
                    patron = 'Ep.([^ ]+) '
                    matches = re.compile(patron, re.DOTALL).findall(description)
                    if len(matches) > 0:
                        try:
                            episode = int(matches[0])
                        except:
                            episode = 0

                    else:
                        episode = 0
            return (season, episode)
        else:
            return (0, 0)

    def InitRestart(self):
        self.LaunchRestart(True)

    def callback(self, retval):
        self.Initialize(self.session)

    def ejecuta(self):
        open('/tmp/spaTimerEntry.log', 'a').write(strftime('%d/%m/%y %H:%M:%S') + ' Init Start\n')
        spa_autotimers = None
        if os_path.exists('/etc/enigma2/spa_autotimers.xml'):
            spa_autotimers = ET.parse('/etc/enigma2/spa_autotimers.xml').getroot()
        if spa_autotimers:
            for timer in spa_autotimers.findall('spatimer'):
                name = timer.find('name').text.encode('UTF-8')
                service = timer.find('Serviceref').text
                if service == '':
                    service = None
                season = int(timer.find('Season').text)
                begin = int(timer.find('StartDate').text)
                justplay = timer.find('justplay').text
                tipo = timer.find('type').text
                dirname = timer.find('path').text
                afterevent = timer.find('afterevent').text
                recordtype = timer.find('recordtype').text
                records = self.searchEPG(name, service, season, begin, justplay, tipo, dirname, afterevent, recordtype)
                open('/tmp/spaTimerEntry.log', 'a').write(strftime('%d/%m/%y %H:%M:%S') + ' %d Records Append\n' % records)

        self.callback(True)

    def LaunchRestart(self, confirmFlag = True):
        if confirmFlag:
            self.TimerTemp = eTimer()
            self.TimerTemp.callback.append(self.ejecuta)
            self.TimerTemp.startLongTimer(4)
        else:
            self.RestartTimerStart(True, 30)

    def RestartTimerStop(self):
        self.restartTimer.stop()
        self.timerActive = False
        self.minutes = 0


tsTasker = timerScriptTasker()
