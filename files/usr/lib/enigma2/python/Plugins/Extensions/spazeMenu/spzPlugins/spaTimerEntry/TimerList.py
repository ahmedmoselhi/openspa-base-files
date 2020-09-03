from Components.HTMLComponent import HTMLComponent
from Components.GUIComponent import GUIComponent
from skin import parseFont
from Tools.FuzzyDate import FuzzyTime
from time import localtime, strftime, time
from enigma import eListboxPythonMultiContent, eListbox, gFont, RT_HALIGN_LEFT, RT_HALIGN_RIGHT, RT_VALIGN_CENTER, RT_VALIGN_TOP, RT_VALIGN_BOTTOM
from Tools.Alternatives import GetWithAlternative
from Tools.LoadPixmap import LoadPixmap
from Tools.TextBoundary import getTextBoundarySize
from timer import TimerEntry
from Tools.Directories import resolveFilename, SCOPE_CURRENT_SKIN
from ServiceReference import ServiceReference
from . import _

class spaTimerList(HTMLComponent, GUIComponent, object):

    def buildTimerEntry(self, timer):
        width = self.l.getItemSize().width()
        name = timer.find('name').text.encode('UTF-8')
        begin = int(timer.find('StartDate').text)
        service = timer.find('Serviceref').text
        s = timer.find('Season').text
        if s == '0':
            s = _('All')
        season = _('Season') + ': ' + s
        justplay = timer.find('justplay').text
        tipo = timer.find('type').text
        res = [None]
        if service == None:
            serviceName = _('All')
        else:
            serviceName = ServiceReference(service).getServiceName()
        serviceNameWidth = getTextBoundarySize(self.instance, self.serviceNameFont, self.l.getItemSize(), serviceName).width()
        if 200 > width - serviceNameWidth - self.iconWidth - self.iconMargin:
            serviceNameWidth = width - 200 - self.iconWidth - self.iconMargin
        if justplay == 'zap':
            icon = self.iconzap
        else:
            icon = self.iconWait
        if tipo == 'by_title':
            tipo = _('By Name')
            season = ''
        else:
            tipo = _('TV Series')
        icon and res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHATEST,
         self.iconMargin / 2,
         (self.rowSplit - self.iconHeight) / 2,
         self.iconWidth,
         self.iconHeight,
         icon))
        res.append((eListboxPythonMultiContent.TYPE_TEXT,
         width - serviceNameWidth,
         0,
         serviceNameWidth,
         self.rowSplit,
         0,
         RT_HALIGN_RIGHT | RT_VALIGN_BOTTOM,
         serviceName))
        res.append((eListboxPythonMultiContent.TYPE_TEXT,
         self.iconWidth + self.iconMargin,
         0,
         width - serviceNameWidth - self.iconWidth - self.iconMargin,
         self.rowSplit,
         2,
         RT_HALIGN_LEFT | RT_VALIGN_BOTTOM,
         name))
        sbegin = strftime(_('%d.%B %Y'), localtime(begin))
        seasonWidth = getTextBoundarySize(self.instance, self.font, self.l.getItemSize(), season).width()
        res.append((eListboxPythonMultiContent.TYPE_TEXT,
         self.satPosLeft,
         self.rowSplit,
         seasonWidth,
         self.itemHeight - self.rowSplit,
         1,
         RT_HALIGN_LEFT | RT_VALIGN_TOP,
         season))
        res.append((eListboxPythonMultiContent.TYPE_TEXT,
         self.iconWidth + self.iconMargin,
         self.rowSplit,
         self.satPosLeft - self.iconWidth - self.iconMargin,
         self.itemHeight - self.rowSplit,
         1,
         RT_HALIGN_LEFT | RT_VALIGN_TOP,
         tipo))
        res.append((eListboxPythonMultiContent.TYPE_TEXT,
         self.satPosLeft + seasonWidth,
         self.rowSplit,
         width - self.satPosLeft - seasonWidth,
         self.itemHeight - self.rowSplit,
         1,
         RT_HALIGN_RIGHT | RT_VALIGN_TOP,
         _('From') + ': ' + str(sbegin)))
        return res

    def buildTimerEntry2(self, timer, xname, justplay, tipo, dirname):
        width = self.l.getItemSize().width()
        begin = int(timer.find('begin').text)
        duration = int(timer.find('duration').text)
        service = timer.find('serviceref').text
        if tipo == 'by_title':
            season = ''
            episode = ''
        else:
            season = _('Season') + ': ' + timer.find('season').text
            episode = _('Episode') + ': ' + timer.find('episode').text
        res = [None]
        serviceName = ServiceReference(service).getServiceName()
        serviceNameWidth = getTextBoundarySize(self.instance, self.serviceNameFont, self.l.getItemSize(), serviceName).width()
        if 200 > width - serviceNameWidth - self.iconWidth - self.iconMargin:
            serviceNameWidth = width - 200 - self.iconWidth - self.iconMargin
        t = time()
        if begin < t:
            if justplay == 'zap':
                icon = self.iconDone
            else:
                icon = self.iconRecording
        elif justplay == 'zap':
            icon = self.iconzap
        else:
            icon = self.iconPrepared
        icon and res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHATEST,
         self.iconMargin / 2,
         (self.rowSplit - self.iconHeight) / 2,
         self.iconWidth,
         self.iconHeight,
         icon))
        name = timer.find('name').text
        bbegin = FuzzyTime(begin)
        end = begin + duration
        sbegin = bbegin[0] + (' %s ... %s (%d ' + _('mins') + ')') % (bbegin[1], FuzzyTime(end)[1], duration / 60)
        res.append((eListboxPythonMultiContent.TYPE_TEXT,
         width - serviceNameWidth,
         0,
         serviceNameWidth,
         self.rowSplit,
         0,
         RT_HALIGN_RIGHT | RT_VALIGN_BOTTOM,
         serviceName))
        res.append((eListboxPythonMultiContent.TYPE_TEXT,
         self.iconWidth + self.iconMargin,
         0,
         width - serviceNameWidth - self.iconWidth - self.iconMargin,
         self.rowSplit,
         2,
         RT_HALIGN_LEFT | RT_VALIGN_BOTTOM,
         name))
        seasonWidth = getTextBoundarySize(self.instance, self.font, self.l.getItemSize(), season).width()
        res.append((eListboxPythonMultiContent.TYPE_TEXT,
         self.satPosLeft,
         self.rowSplit,
         seasonWidth,
         self.itemHeight - self.rowSplit,
         1,
         RT_HALIGN_LEFT | RT_VALIGN_TOP,
         season))
        res.append((eListboxPythonMultiContent.TYPE_TEXT,
         self.iconWidth + self.iconMargin,
         self.rowSplit,
         self.satPosLeft - self.iconWidth - self.iconMargin,
         self.itemHeight - self.rowSplit,
         1,
         RT_HALIGN_LEFT | RT_VALIGN_TOP,
         episode))
        res.append((eListboxPythonMultiContent.TYPE_TEXT,
         self.satPosLeft + seasonWidth,
         self.rowSplit,
         width - self.satPosLeft - seasonWidth,
         self.itemHeight - self.rowSplit,
         1,
         RT_HALIGN_RIGHT | RT_VALIGN_TOP,
         str(sbegin)))
        return res

    def __init__(self, list, Init):
        GUIComponent.__init__(self)
        self.l = eListboxPythonMultiContent()
        if Init:
            self.l.setBuildFunc(self.buildTimerEntry)
        else:
            self.l.setBuildFunc(self.buildTimerEntry2)
        self.serviceNameFont = gFont('Regular', 20)
        self.font = gFont('Regular', 18)
        self.eventNameFont = gFont('Regular', 18)
        self.l.setList(list)
        self.itemHeight = 50
        self.rowSplit = 25
        self.iconMargin = 4
        self.satPosLeft = 160
        self.iconWait = LoadPixmap(resolveFilename(SCOPE_CURRENT_SKIN, 'skin_default/icons/timer_wait.png'))
        self.iconzap = LoadPixmap(resolveFilename(SCOPE_CURRENT_SKIN, 'skin_default/icons/timer_zap.png'))
        self.iconRecording = LoadPixmap(resolveFilename(SCOPE_CURRENT_SKIN, 'skin_default/icons/record.png'))
        self.iconPrepared = LoadPixmap(resolveFilename(SCOPE_CURRENT_SKIN, 'skin_default/icons/timer_prep.png'))
        self.iconDone = LoadPixmap(resolveFilename(SCOPE_CURRENT_SKIN, 'skin_default/icons/timer_done.png'))
        self.iconWidth = self.iconWait.size().width()
        self.iconHeight = self.iconWait.size().height()

    def applySkin(self, desktop, parent):

        def itemHeight(value):
            self.itemHeight = int(value)

        def setServiceNameFont(value):
            self.serviceNameFont = parseFont(value, ((1, 1), (1, 1)))

        def setEventNameFont(value):
            self.eventNameFont = parseFont(value, ((1, 1), (1, 1)))

        def setFont(value):
            self.font = parseFont(value, ((1, 1), (1, 1)))

        def rowSplit(value):
            self.rowSplit = int(value)

        def iconMargin(value):
            self.iconMargin = int(value)

        def satPosLeft(value):
            self.satPosLeft = int(value)

        for attrib, value in list(self.skinAttributes):
            try:
                locals().get(attrib)(value)
                self.skinAttributes.remove((attrib, value))
            except:
                pass

        self.l.setItemHeight(self.itemHeight)
        self.l.setFont(0, self.serviceNameFont)
        self.l.setFont(1, self.font)
        self.l.setFont(2, self.eventNameFont)
        return GUIComponent.applySkin(self, desktop, parent)

    def getCurrent(self):
        cur = self.l.getCurrentSelection()
        return cur and cur[0]

    GUI_WIDGET = eListbox

    def postWidgetCreate(self, instance):
        instance.setContent(self.l)
        self.instance = instance
        instance.setWrapAround(True)

    def moveToIndex(self, index):
        self.instance.moveSelectionTo(index)

    def getCurrentIndex(self):
        return self.instance.getCurrentIndex()

    currentIndex = property(getCurrentIndex, moveToIndex)
    currentSelection = property(getCurrent)

    def moveDown(self):
        self.instance.moveSelection(self.instance.moveDown)

    def invalidate(self):
        self.l.invalidate()

    def entryRemoved(self, idx):
        self.l.entryRemoved(idx)
