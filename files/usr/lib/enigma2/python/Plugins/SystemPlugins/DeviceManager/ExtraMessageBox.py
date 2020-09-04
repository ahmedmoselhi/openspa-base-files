from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.Sources.List import List
from Tools.Directories import resolveFilename, SCOPE_CURRENT_PLUGIN
from Tools.LoadPixmap import LoadPixmap
from Components.Label import Label

def MessageBoxEntry(name, picture):
    pixmap = LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_PLUGIN, 'SystemPlugins/DeviceManager/icons/' + picture))
    if not pixmap:
        pixmap = LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_PLUGIN, 'SystemPlugins/DeviceManager/icons/empty.png'))
    return (pixmap, name)


class ExtraMessageBox(Screen):
    skin = '\n\t<screen name="ExtraMessageBox" position="center,center" size="460,430" title=" ">\n\t\t<widget name="message" position="10,10" size="440,25" font="Regular;20" />\n\t\t<widget source="menu" render="Listbox" position="20,90" size="420,360" scrollbarMode="showOnDemand">\n\t\t\t<convert type="TemplatedMultiContent">\n\t\t\t\t{"template": [\n\t\t\t\t\tMultiContentEntryPixmapAlphaTest(pos = (5, 0), size = (48, 48), png = 0),\n\t\t\t\t\tMultiContentEntryText(pos = (65, 10), size = (425, 38), font=0, flags = RT_HALIGN_LEFT|RT_VALIGN_TOP, text = 1),\n\t\t\t\t\t],\n\t\t\t\t\t"fonts": [gFont("Regular", 22)],\n\t\t\t\t\t"itemHeight": 48\n\t\t\t\t}\n\t\t\t</convert>\n\t\t</widget>\n\t\t<applet type="onLayoutFinish">\n# this should be factored out into some helper code, but currently demonstrates applets.\nfrom enigma import eSize, ePoint\n\norgwidth = self.instance.size().width()\norgheight = self.instance.size().height()\norgpos = self.instance.position()\ntextsize = self[&quot;message&quot;].getSize()\n\n# y size still must be fixed in font stuff...\nif self[&quot;message&quot;].getText() != &quot;&quot;:\n\ttextsize = (textsize[0] + 80, textsize[1] + 60)\nelse:\n\ttextsize = (textsize[0] + 80, textsize[1] + 4)\n\ncount = len(self.list)\nif count &gt; 7:\n\tcount = 7\noffset = 48 * count\nwsizex = textsize[0] + 80\nwsizey = textsize[1] + offset + 20\n\nif (460 &gt; wsizex):\n\twsizex = 460\nwsize = (wsizex, wsizey)\n\n# resize\nself.instance.resize(eSize(*wsize))\n\n# resize label\nself[&quot;message&quot;].instance.resize(eSize(*textsize))\n\n# move list\nlistsize = (wsizex - 20, 48 * count)\nself[&quot;menu&quot;].downstream_elements.downstream_elements.instance.move(ePoint(10, textsize[1] + 10))\nself[&quot;menu&quot;].downstream_elements.downstream_elements.instance.resize(eSize(*listsize))\n\n# center window\nnewwidth = wsize[0]\nnewheight = wsize[1]\nself.instance.move(ePoint(orgpos.x() + (orgwidth - newwidth)/2, orgpos.y()  + (orgheight - newheight)/2))\n\t\t</applet>\n\t</screen>'

    def __init__(self, session, message = '', title = '', menulist = [], type = 0, exitid = -1, default = 0, timeout = 0):
        Screen.__init__(self, session)
        self.session = session
        self.ctitle = title
        self.exitid = exitid
        self.default = default
        self.timeout = timeout
        self.elapsed = 0
        self.list = []
        for item in menulist:
            self.list.append(MessageBoxEntry(item[0], item[1]))

        self['menu'] = List(self.list)
        self['menu'].onSelectionChanged.append(self.selectionChanged)
        self['message'] = Label(message)
        self['actions'] = ActionMap(['SetupActions'], {'ok': self.ok,
         'cancel': self.cancel}, -2)
        self.onLayoutFinish.append(self.layoutFinished)
        self.timer = eTimer()
        self.timer.callback.append(self.timeoutStep)
        if self.timeout > 0:
            self.timer.start(1000, 1)

    def selectionChanged(self):
        self.timer.stop()
        self.setTitle(self.ctitle)

    def timeoutStep(self):
        self.elapsed += 1
        if self.elapsed == self.timeout:
            self.ok()
        else:
            self.setTitle('%s - %d' % (self.ctitle, self.timeout - self.elapsed))
            self.timer.start(1000, 1)

    def layoutFinished(self):
        if self.timeout > 0:
            self.setTitle('%s - %d' % (self.ctitle, self.timeout))
        else:
            self.setTitle(self.ctitle)
        self['menu'].setCurrentIndex(self.default)

    def ok(self):
        index = self['menu'].getIndex()
        self.close(index)

    def cancel(self):
        if self.exitid > -1:
            self.close(self.exitid)
