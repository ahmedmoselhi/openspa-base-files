from __init__ import _
from enigma import eListboxPythonMultiContent, gFont, loadPNG, eTimer, getDesktop, BT_SCALE, BT_KEEP_ASPECT_RATIO
from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.MenuList import MenuList
from Components.Label import Label
from Tools.Directories import fileExists, SCOPE_PLUGINS, resolveFilename
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaBlend
from Components.Button import Button
from Components.ProgressBar import ProgressBar
from Components.config import config, ConfigBoolean
from Components.Sources.StaticText import StaticText
from Components.Ipkg import IpkgComponent
from Plugins.Extensions.spazeMenu.plugin import esHD, fhd
import os
config.misc.firstrun = ConfigBoolean(default=True)

class listado(MenuList):

    def __init__(self, list, enableWrapAround = False):
        MenuList.__init__(self, list, enableWrapAround, eListboxPythonMultiContent)
        self.l.setItemHeight(fhd(47))
        self.l.setFont(0, gFont('Regular', 19))
        self.l.setFont(1, gFont('Regular', 16))


def listentry(name, installed, size, desc, mark):
    res = [(name,
      installed,
      size,
      desc,
      mark)]
    picture = None
    if installed:
        picture = '/usr/share/enigma2/skin_default/icons/part_unwatched.png'
    else:
        picture = '/usr/share/enigma2/skin_default/icons/part_new.png'
    res.append(MultiContentEntryText(pos=(fhd(85), fhd(3)), size=(fhd(750), fhd(23)), font=0, text=name, color=7056598))
    res.append(MultiContentEntryText(pos=(fhd(85), fhd(23)), size=(fhd(750), fhd(20)), font=1, text=desc))
    if picture != None:
        if fileExists(picture):
            res.append(MultiContentEntryPixmapAlphaBlend(pos=(fhd(55, 1.4), fhd(10)), size=(fhd(20), fhd(20)), png=loadPNG(picture), flags=BT_SCALE | BT_KEEP_ASPECT_RATIO))
    if mark:
        picture = '/usr/share/enigma2/skin_default/icons/lock_on.png'
    else:
        picture = '/usr/share/enigma2/skin_default/icons/lock_off.png'
    if picture != None:
        if fileExists(picture):
            res.append(MultiContentEntryPixmapAlphaBlend(pos=(fhd(10), fhd(10)), size=(fhd(20), fhd(19, 1.55)), png=loadPNG(picture), flags=BT_SCALE | BT_KEEP_ASPECT_RATIO))
    return res


class OpenSPAPlug(Screen):
    if esHD():
        skin = '\n\t\t<screen name="OpenSPAPlug" position="center,center" size="1200,870" title="Plugins OpenSPA">\n\t\t<widget name="menu" position="0,195" scrollbarMode="showOnDemand" size="1200,575"/>\n\t\t<ePixmap name="logo" position="15,15" size="210,91" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/OpenSPAPlug/hdopenspa.png" zPosition="2" alphatest="on" transparent="1"/>\n\t\t<widget name="texto" position="255,22" size="900,90" font="Regular;22" valign="center" transparent="1" />\n\t\t<widget name="space" position="0,120" size="1200,45" halign="center" font="Regular;20" transparent="1" foregroundColor="#00389416"/>\n\t\t<widget name="progreso" position="0,165" size="1200,19" borderWidth="1" zPosition="3" foregroundColor="#00389416"/>\n\t\t<ePixmap position="0,795"   zPosition="1" size="225,60" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/hdredcor.png" transparent="1" alphatest="blend" />\n\t\t<ePixmap position="300,790" zPosition="1" size="225,60" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/hdgreencor.png" transparent="1" alphatest="blend" />\n\t\t<ePixmap position="600,790" zPosition="1" size="225,60" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/hdyellowcor.png" transparent="1" alphatest="blend" />\n\t\t<ePixmap position="900,790" zPosition="1" size="225,60" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/hdbluecor.png" transparent="1" alphatest="blend" />\n\t\t<widget name="key_red"    position="0,798"   zPosition="2" size="225,67" halign="center" valign="center" shadowColor="black" font="Regular;20" transparent="1"  />\n\t\t<widget name="key_green"  position="300,798" zPosition="2" size="225,67" halign="center" valign="center" shadowColor="black" font="Regular;20" transparent="1"  />\n\t\t<widget name="key_yellow" position="600,798" zPosition="2" size="225,67" halign="center" valign="center" shadowColor="black" font="Regular;20" transparent="1"  />\n\t\t<widget name="key_blue"   position="900,798" zPosition="2" size="225,67" halign="center" valign="center" shadowColor="black" font="Regular;20" transparent="1"  />\n\t\t</screen>'
    else:
        skin = '\n\t\t<screen name="OpenSPAPlug" position="center,center" size="800,580" title="Plugins OpenSPA">\n\t\t<widget name="menu" position="0,130" scrollbarMode="showOnDemand" size="800,378"/>\n\t\t<ePixmap name="logo" position="10,10" size="140,61" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/OpenSPAPlug/openspa.png" zPosition="2" alphatest="on" transparent="1"/>\n\t\t<widget name="texto" position="170,15" size="600,60" font="Regular;22" valign="center" transparent="1" />\n\t\t<widget name="space" position="0,80" size="800,30" halign="center" font="Regular;20" transparent="1" foregroundColor="#00389416"/>\n\t\t<widget name="progreso" position="0,110" size="800,13" borderWidth="1" zPosition="3" foregroundColor="#00389416"/>\n\t\t<ePixmap position="0,530"   zPosition="1" size="150,40" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/OpenSPAPlug/images/redcor.png" transparent="1" alphatest="on" />\n\t\t<ePixmap position="200,527" zPosition="1" size="150,40" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/OpenSPAPlug/images/greencor.png" transparent="1" alphatest="on" />\n\t\t<ePixmap position="400,527" zPosition="1" size="150,40" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/OpenSPAPlug/images/yellowcor.png" transparent="1" alphatest="on" />\n\t\t<ePixmap position="600,527" zPosition="1" size="150,40" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/OpenSPAPlug/images/bluecor.png" transparent="1" alphatest="on" />\n\n\t\t<widget name="key_red"    position="0,532"   zPosition="2" size="150,45" halign="center" valign="center" shadowColor="black" font="Regular;20" transparent="1"  />\n\t\t<widget name="key_green"  position="200,532" zPosition="2" size="150,45" halign="center" valign="center" shadowColor="black" font="Regular;20" transparent="1"  />\n\t\t<widget name="key_yellow" position="400,532" zPosition="2" size="150,45" halign="center" valign="center" shadowColor="black" font="Regular;20" transparent="1"  />\n\t\t<widget name="key_blue"   position="600,532" zPosition="2" size="150,45" halign="center" valign="center" shadowColor="black" font="Regular;20" transparent="1"  />\n\t\t</screen>'

    def __init__(self, session, wizard = False):
        Screen.__init__(self, session)
        self.skinName = 'OpenSPAPlug'
        self.wizard = wizard
        self['menu'] = listado(list())
        self['menu'].onSelectionChanged.append(self.selectionChanged)
        self['key_red'] = Button(_('Exit'))
        self['key_blue'] = Button(_('Switch All marks'))
        self['key_yellow'] = Button('')
        self['texto'] = Label('')
        self['space'] = Label('')
        self['progreso'] = ProgressBar()
        self['actions'] = ActionMap(['OkCancelActions', 'ColorActions'], {'ok': self.ok,
         'red': self.close,
         'green': self.go,
         'blue': self.blue,
         'cancel': self.close}, -2)
        self.allview = False
        self.list = []
        self.plug = []
        help_text = _('Use OK Key to select Plugins to Install')
        if not wizard:
            help_text = help_text + ' ' + _('or Uninstall')
            button_text = _('[Un]Install all marked')
        else:
            button_text = _('Install all marked')
        self['key_green'] = Button(button_text)
        self['texto'].setText(help_text)
        self.first = True
        self.checkTimer = eTimer()
        self.checkTimer.timeout.get().append(self.updateopkg)
        self.inst = ''
        if fileExists('/etc/OpenSPAPlug.ins'):
            self.inst = open('/etc/OpenSPAPlug.ins').read()
        self.plugfill = 0
        self.plugmarked = 0
        self.readall()
        self.spacetotal = 0
        self.spacefill = 0
        self.checkspace()
        self.onShow.append(self.updatedata)

    def updatedata(self):
        perc = int(float(self.spacefill + self.plugfill) / float(self.spacetotal) * 100)
        self['space'].setText(_('Used:') + ' ' + str(self.spacefill + self.plugfill) + 'Kb ' + _('of') + ' ' + str(self.spacetotal) + 'Kb (' + str(perc) + '%)')
        self['progreso'].setValue(perc)
        green = '#00389416'
        red = '#00ff2525'
        yellow = '#00ffe875'
        orange = '#00ff7f50'
        if perc < 30:
            color = green
        elif perc < 60:
            color = yellow
        elif perc < 80:
            color = orange
        else:
            color = red
        from skin import parseColor
        self['space'].instance.setForegroundColor(parseColor(color))
        self['progreso'].instance.setForegroundColor(parseColor(color))

    def checkspace(self):
        ustot = used = '0'
        rc = os.system('df / > /tmp/ninfo.tmp')
        if fileExists('/tmp/ninfo.tmp'):
            f = open('/tmp/ninfo.tmp', 'r')
            for line in f.readlines():
                line = line.replace('part1', ' ')
                parts = line.strip().split()
                totsp = len(parts) - 1
                if parts[totsp] == '/':
                    if totsp == 5:
                        ustot = parts[1]
                        used = parts[2]
                    break

            f.close()
            os.remove('/tmp/ninfo.tmp')
        self.spacetotal = int(ustot)
        self.spacefill = int(used)

    def readall(self):
        if fileExists('/etc/openSPAP'):
            lOPSP = open('/etc/openSPAP').read()
            info = os.popen('opkg info enigma2-*')
            if info != None:
                buff = info.read()
                info.close()
                infolist = buff.split('\n')
            else:
                infolist = ''
            i = 0
            installed = False
            size = 0
            desc = ''
            ver = ''
            while i < len(infolist):
                if 'Package: ' in infolist[i]:
                    name = infolist[i][9:].replace('enigma2-', '').replace('plugin-', '').replace('extensions-', '').replace('systemplugins-', '').replace('skins', 'skin')
                    pkg = infolist[i][9:]
                if 'Version: ' in infolist[i]:
                    ver = infolist[i][9:]
                if 'Status' in infolist[i] and ' installed' in infolist[i]:
                    installed = True
                if 'Size' in infolist[i]:
                    size = int(infolist[i][6:])
                if 'Description: ' in infolist[i]:
                    desc = infolist[i][13:].replace(pkg, '').replace('version', '').replace(ver, '').strip()
                if len(infolist[i]) > 2:
                    if infolist[i][0] == ' ' and infolist[i][1] != ' ':
                        desc = desc + infolist[i]
                if len(infolist[i]) == 0:
                    if pkg + ' ' in lOPSP:
                        if not installed and name + ' ' in self.inst:
                            mark = True
                            self.plugmarked += 1
                            self.plugfill += size / 1000
                        else:
                            mark = False
                        self.plug.append([name,
                         installed,
                         size,
                         desc,
                         mark,
                         pkg])
                    installed = False
                    size = 0
                    desc = ''
                i += 1

            if len(self.plug) == 0 and self.first:
                self.checkTimer.start(500, False)
            else:
                self.first = False
                self.plug.sort()
                self.updateLista()

    def updateopkg(self):
        self.checkTimer.stop()
        from OpenSPAPlugWizard import InstallopkgUpdater
        self.session.openWithCallback(self.endopkgupdate, InstallopkgUpdater, _('Please wait while we update the opkg database...'))

    def endopkgupdate(self):
        self.first = False
        self.readall()

    def updateLista(self):
        self.list = []
        if fileExists('/etc/OpenSPAPlug.ins'):
            os.remove('/etc/OpenSPAPlug.ins')
        for x in self.plug:
            self.list.append(listentry(x[0], x[1], x[2], x[3], x[4]))
            if x[1]:
                open('/etc/OpenSPAPlug.ins', 'a').write(x[0] + ' ')

        self['menu'].setList(self.list)

    def blue(self):
        self.plugmarked = 0
        for x in self.plug:
            x[4] = not x[4]
            if x[4]:
                self.plugmarked += 1
                if not x[1]:
                    self.plugfill += x[2] / 1000
                else:
                    self.plugfill -= x[2] / 1000
            elif not x[1]:
                self.plugfill -= x[2] / 1000
            else:
                self.plugfill += x[2] / 1000

        self.updateLista()
        self.updatedata()

    def selectionChanged(self):
        pass

    def ok(self):
        try:
            self.plug[self['menu'].getSelectedIndex()][4] = not self.plug[self['menu'].getSelectedIndex()][4]
            self.sumplugfill(self['menu'].getSelectedIndex())
        except:
            pass

        self.updateLista()

    def sumplugfill(self, index):
        if self.plug[index][4]:
            self.plugmarked += 1
            if not self.plug[index][1]:
                self.plugfill += self.plug[index][2] / 1000
            else:
                self.plugfill -= self.plug[index][2] / 1000
        else:
            self.plugmarked -= 1
            if not self.plug[index][1]:
                self.plugfill -= self.plug[index][2] / 1000
            else:
                self.plugfill += self.plug[index][2] / 1000
        self.updatedata()

    def go(self):
        self.session.openWithCallback(self.Finished, Installplugs, self.plug, self.plugmarked)

    def Finished(self):
        from Components.PluginComponent import plugins
        plugins.resetWarnings()
        plugins.clearPluginList()
        plugins.readPluginList(resolveFilename(SCOPE_PLUGINS))
        if self.wizard:
            self.close()
        else:
            self.close()


class Installplugs(Screen):
    if esHD():
        skin = '\n\t\t<screen position="c-450,c-37" size="900,75" title=" ">\n\t\t<widget source="statusbar" render="Label" position="10,5" zPosition="10" size="e-10,45" halign="center" valign="center" font="Regular;22" transparent="1" itemHeight="40" shadowColor="black" shadowOffset="-1,-1" />\n\t\t</screen>'
    else:
        skin = '\n\t\t<screen position="c-300,c-25" size="600,50" title=" ">\n\t\t<widget source="statusbar" render="Label" position="10,5" zPosition="10" size="e-10,30" halign="center" valign="center" font="Regular;22" transparent="1" shadowColor="black" shadowOffset="-1,-1" />\n\t\t</screen>'

    def __init__(self, session, lista, number):
        Screen.__init__(self, session)
        self['statusbar'] = StaticText(_('Preparing list...'))
        self.lista = []
        if fileExists('/etc/OpenSPAPlug.ins'):
            os.remove('/etc/OpenSPAPlug.ins')
        for x in lista:
            if x[1] and not x[4] or x[4] and not x[1]:
                open('/etc/OpenSPAPlug.ins', 'a').write(x[0] + ' ')
            if x[4]:
                self.lista.append(x)

        self.number = len(self.lista)
        self.index = -1
        self.ipkg = IpkgComponent()
        self.ipkg.addCallback(self.ipkgCallback)
        self.ipkgCallback(IpkgComponent.EVENT_DONE)

    def ipkgCallback(self, event = None, param = None):
        if event == IpkgComponent.EVENT_INSTALL:
            texto = _('[%d/%d] Installing %s') % (self.index + 1, self.number, self.lista[self.index][0])
            self['statusbar'].setText(texto)
        elif event == IpkgComponent.EVENT_REMOVE:
            texto = _('[%d/%d] Uninstalling %s') % (self.index + 1, self.number, self.lista[self.index][0])
            self['statusbar'].setText(texto)
        elif event == IpkgComponent.EVENT_ERROR:
            texto = _('[%d/%d] EROR with %s') % (self.index + 1, self.number, self.lista[self.index][0])
            self['statusbar'].setText(texto)
        elif event == IpkgComponent.EVENT_DONE:
            self.index += 1
            if self.index == self.number:
                self.close()
            elif self.lista[self.index][1]:
                pkg = {'package': '--force-depends %s' % self.lista[self.index][5]}
                self.ipkg.startCmd(IpkgComponent.CMD_REMOVE, pkg)
            else:
                pkg = {'package': '--force-overwrite %s' % self.lista[self.index][5]}
                self.ipkg.startCmd(IpkgComponent.CMD_INSTALL, pkg)


def startConfig(session, **kwargs):
    session.open(OpenSPAPlug)


def mainmenu(menuid):
    if menuid != 'setup':
        return []
    return [(_('Plugins OpenSPA'),
      startConfig,
      'OSPAplug',
      None)]


def OpenSPAPlugWizard(*args, **kwargs):
    from OpenSPAPlugWizard import OpenSPAPlugWizard
    return OpenSPAPlugWizard(*args, **kwargs)


def Plugins(**kwargs):
    list = []
    if config.misc.firstrun.value:
        list.append(PluginDescriptor(name=_('OpenSPA Plugins Wizard'), where=PluginDescriptor.WHERE_WIZARD, fnc=(30, OpenSPAPlugWizard)))
    return list
