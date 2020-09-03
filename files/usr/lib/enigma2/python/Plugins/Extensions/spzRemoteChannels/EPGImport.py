import xml.etree.ElementTree as ET
from urllib import quote
from enigma import eEPGCache, eConsoleAppContainer, eTimer
from Screens.Screen import Screen
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.ActionMap import ActionMap
from Components.ProgressBar import ProgressBar
from Components.config import config
from Screens.MessageBox import MessageBox
from os import remove, listdir
from . import _

class DownloadComponent:
    EVENT_DOWNLOAD = 0
    EVENT_DONE = 1
    EVENT_ERROR = 2

    def __init__(self, n, ref, name, target):
        self.cmd = eConsoleAppContainer()
        self.cache = None
        self.name = None
        self.data = None
        self.number = n
        self.ref = ref
        self.name = name
        self.target = target
        self.callbackList = []

    def startCmd(self, cmd, filename = None):
        rute = 'wget'
        if filename:
            rute = rute + ' -O ' + filename
            self.filename = filename
        else:
            self.filename = cmd.split('/')[-1]
        rute = rute + ' ' + cmd
        self.runCmd(rute)

    def runCmd(self, cmd):
        print 'executing', cmd
        self.cmd.appClosed.append(self.cmdFinished)
        self.cmd.dataAvail.append(self.cmdData)
        if self.cmd.execute(cmd):
            self.cmdFinished(-1)

    def cmdFinished(self, retval):
        self.data = open(self.filename).read()
        self.callCallbacks(self.EVENT_DONE, self.number, self.data, self.ref, self.name, self.target)
        self.cmd.appClosed.remove(self.cmdFinished)
        self.cmd.dataAvail.remove(self.cmdData)
        remove(self.filename)

    def cmdData(self, data):
        if self.cache is None:
            self.cache = data
        else:
            self.cache += data
        if '\n' in data:
            splitcache = self.cache.split('\n')
            if self.cache[-1] == '\n':
                iteration = splitcache
                self.cache = None
            else:
                iteration = splitcache[:-1]
                self.cache = splitcache[-1]
            for mydata in iteration:
                if mydata != '':
                    self.parseLine(mydata)

    def parseLine(self, data):
        try:
            if data.startswith(self.name):
                self.callCallbacks(self.EVENT_DOWNLOAD, data.split(' ', 5)[1].strip())
            elif data.startswith('An error occurred'):
                self.callCallbacks(self.EVENT_ERROR, None)
            elif data.startswith('Failed to download'):
                self.callCallbacks(self.EVENT_ERROR, None)
        except Exception as ex:
            print "Failed to parse: '%s'" % data

    def callCallbacks(self, event, param = None, data = None, ref = None, name = None, target = None):
        for callback in self.callbackList:
            callback(event, param, data, ref, name, target)

    def addCallback(self, callback):
        self.callbackList.append(callback)

    def removeCallback(self, callback):
        self.callbackList.remove(callback)


class EPGdownload(Screen):
    skin = '\n<screen name="EPGdownload" position="40,40" size="410,130" title="RemoteChannels EPG Download" flags="wfNoBorder" backgroundColor="#ff000000">\n\t<ePixmap name="background" position="0,0" size="410,130" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spzRemoteChannels/background.png" zPosition="-1" alphatest="off" />\n\t<widget name="action" halign="left" valign="center" position="9,6" size="289,20" font="Regular;17" foregroundColor="#dfdfdf" transparent="1" backgroundColor="#000000" borderColor="black" borderWidth="1" noWrap="1"/>\n\t<widget name="progress" position="20,65" size="360,8" borderWidth="0" backgroundColor="#1143495b" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spzRemoteChannels/progreso.png" zPosition="2" alphatest="blend" />\n\t<eLabel name="fondoprogreso" position="20,65" size="360,8" backgroundColor="#102a3b58" />\n\t<widget name="espera" valign="center" halign="center" position="20,42" size="360,20" font="Regular;15" foregroundColor="#dfdfdf" transparent="1" backgroundColor="#000000" borderColor="black" borderWidth="1" noWrap="1"/>\n\t<widget name="status" halign="center" valign="center" position="20,80" size="360,20" font="Regular;16" foregroundColor="#ffffff" transparent="1" backgroundColor="#000000" borderColor="black" borderWidth="1" noWrap="1"/>\n</screen>\n'

    def __init__(self, session, args = 0):
        self.session = session
        Screen.__init__(self, session)
        self.iprogress = 0
        self.total = 0
        self['progress'] = ProgressBar()
        self['progress'].setValue(0)
        self['action'] = Label(_('EPG Download: Remote Channels'))
        self['espera'] = Label('')
        self['status'] = Label(_('Wait...'))
        self['actions'] = ActionMap(['OkCancelActions'], {'cancel': self.salir}, -1)
        self.epgcache = eEPGCache.getInstance()
        self.fd = None
        self.state = 1
        self.onFirstExecBegin.append(self.download)

    def download(self):
        try:
            fd = listdir('/etc/enigma2')
        except:
            return

        self.fd = []
        for f in fd:
            if f.startswith('userbouquet.remote') and not f.endswith('.del'):
                l = open('/etc/enigma2/' + f, 'r').readlines()
                ip = port = user = password = auth = name = service = None
                for line in l:
                    if line.startswith('#SERVICE 1:576:'):
                        y = line.split(':')[-1]
                        z = y.split('|')
                        if len(z) == 5:
                            ip = z[0]
                            port = int(z[1])
                            user = z[2]
                            password = z[3]
                            auth = int(z[4])
                    elif line.startswith('#SERVICE ') and ip:
                        target = line[9:].replace('\n', '')
                        s = line.replace('#SERVICE 4097', '1').replace('#SERVICE ', '')
                        n = s.find('http')
                        service = s[:n]
                        name = s.split(':')[-1].replace('\n', '')
                        if ip and port and user and password and name and service and target:
                            self.fd.append((ip,
                             port,
                             user,
                             password,
                             auth,
                             service,
                             name,
                             target))

        self.total = len(self.fd)
        self.actualizaprogreso(event=DownloadComponent.EVENT_DONE, param=0)

    def actualizaprogreso(self, event = None, param = None, data = None, ref = None, name = None, ref_target = None):
        cont = False
        try:
            if self.state == 1:
                cont = True
        except:
            pass

        if cont:
            if data and ref and name and ref_target:
                self.parse_channel(data, ref_target)
            if event == DownloadComponent.EVENT_DONE:
                try:
                    self.iprogress = (param + 1) * 100 // self.total
                except:
                    self.iprogress = 100

                if self.iprogress > 100:
                    self.iprogress = 100
                self['progress'].setValue(self.iprogress)
                self['espera'].setText(str(self.iprogress) + ' %')
                if self.fd:
                    if param < self.total:
                        channel = self.fd[param]
                        ip = channel[0]
                        port = channel[1]
                        if port != 80:
                            ip = ip + ':' + str(port)
                        user = channel[2]
                        password = channel[3]
                        auth = channel[4]
                        if auth == 1:
                            ip = user + ':' + password + '@' + ip
                        ref = channel[5]
                        name = channel[6]
                        self['status'].setText(_('Wait for Channel: ') + name)
                        ref_target = channel[7]
                        self.down = DownloadComponent(param + 1, ref, name, ref_target)
                        self.down.addCallback(self.actualizaprogreso)
                        try:
                            last_day = int(config.epg.maxdays.value) * 24 * 60
                        except:
                            last_day = 9999999

                        self.down.startCmd('http://' + ip + '/web/epgservice?sRef=' + ref + '&endTime=' + str(last_day), '/tmp/xml')
                    else:
                        self.close()
                else:
                    self.TimerTemp = eTimer()
                    self.TimerTemp.callback.append(self.salirok)
                    self.TimerTemp.startLongTimer(1)

    def parse_channel(self, xml, ref_target):
        events = []
        print 'Load epg for service %s' % ref_target
        ch_epg = ET.fromstring(xml)
        for event in ch_epg:
            start = 0
            duration = 0
            title = ''
            description = ''
            extended = ''
            channel = ''
            name = ''
            for child in event:
                if child.tag == 'e2eventstart':
                    start = long(child.text)
                if child.tag == 'e2eventduration':
                    duration = int(child.text)
                if child.tag == 'e2eventtitle':
                    title = child.text
                    if title == None:
                        title = ''
                    title = title.encode('utf-8')
                if child.tag == 'e2eventdescription':
                    description = child.text
                    if description == None:
                        description = ''
                    description = description.encode('utf-8')
                if child.tag == 'e2eventdescriptionextended':
                    extended = child.text
                    if extended == None:
                        extended = ''
                    extended = extended.encode('utf-8')

            events.append((start,
             duration,
             title,
             description,
             extended,
             0))

        iterator = iter(events)
        events_tuple = tuple(iterator)
        self.epgcache.importEvents(ref_target, events_tuple)

    def salir(self):
        stri = _('The download is in progress. Exit now?')
        self.session.openWithCallback(self.salirok, MessageBox, stri, MessageBox.TYPE_YESNO, timeout=30)

    def salirok(self, answer = True):
        if answer:
            self.close(True)
