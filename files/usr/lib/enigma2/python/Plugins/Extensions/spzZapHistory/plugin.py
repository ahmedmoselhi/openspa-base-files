from Components.ActionMap import ActionMap
from Components.config import config, ConfigInteger, ConfigSelection, ConfigSubsection, getConfigListEntry, ConfigEnableDisable
from Components.ConfigList import ConfigListScreen
from Components.Label import Label
from Components.Language import language
from Components.MenuList import MenuList
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaBlend
from enigma import eListboxPythonMultiContent, eServiceCenter, gFont, eServiceReference, getDesktop, ePixmap, eEnv, RT_HALIGN_LEFT, RT_VALIGN_BOTTOM, RT_VALIGN_CENTER, RT_HALIGN_RIGHT, RT_WRAP, getBestPlayableServiceReference, BT_SCALE, BT_KEEP_ASPECT_RATIO
from os import environ
from Components.SystemInfo import SystemInfo
from Plugins.Plugin import PluginDescriptor
from Screens.ChannelSelection import ChannelSelection
from Screens.ParentalControlSetup import ProtectedScreen
from Screens.Screen import Screen
from Tools.LoadPixmap import LoadPixmap
from Tools.Directories import resolveFilename, SCOPE_LANGUAGE, SCOPE_PLUGINS, fileExists, SCOPE_SKIN_IMAGE, SCOPE_CURRENT_SKIN
from enigma import eTimer
import gettext
from Components.Renderer.Picon import getPiconName
from Plugins.Extensions.spazeMenu.plugin import esHD, fhd

def localeInit():
    lang = language.getLanguage()
    environ['LANGUAGE'] = lang[:2]
    gettext.bindtextdomain('enigma2', resolveFilename(SCOPE_LANGUAGE))
    gettext.textdomain('enigma2')
    gettext.bindtextdomain('spzZapHistory', '%s%s' % (resolveFilename(SCOPE_PLUGINS), 'Extensions/spzZapHistory/locale/'))


def _(txt):
    t = gettext.dgettext('spzZapHistory', txt)
    if t == txt:
        t = gettext.gettext(txt)
    return t


localeInit()
language.addCallback(localeInit)
config.misc.picon_path = ConfigSelection(choices={'/media/usb/picon/': _('/media/usb/picon/')}, default='/media/usb/picon/')
config.plugins.spzHistoryZapConf = ConfigSubsection()
config.plugins.spzHistoryZapConf.activate_historyZap = ConfigSelection(choices={'off': _('disabled'),
 'on': _('enabled'),
 'parental_lock': _('disabled at parental lock')}, default='on')
config.plugins.spzHistoryZapConf.maxEntries_historyZap = ConfigInteger(default=20, limits=(2, 60))
config.plugins.spzHistoryZapConf.viewMode = ConfigSelection(choices={'simple': _('Simple'),
 'menu': _('Standard'),
 'picons': _('With Picons')}, default='picons')
config.plugins.spzHistoryZapConf.autoZap = ConfigEnableDisable(default=False)

def debugtxt(mensaje = '', inicio = False):
    from os import system
    if inicio:
        system('date >texthis.log')
        system("echo '************************************************'>>/tmp/texthis.log")
    system("echo '" + str(mensaje) + "'>>/tmp/texthis.log")
    system("echo '************************************************'>>/tmp/texthis.log")


def devref(x):
    try:
        if len(x) == 2:
            ref = x[1]
        elif len(x) == 4:
            ref = x[3]
        else:
            ref = x[2]
    except:
        ref = None

    return ref


def limpiahistorico(instance):
    try:
        for i in range(len(instance.history) - 1, -1, -1):
            if instance.history[i] in instance.history[:i]:
                del instance.history[i]

    except:
        pass


def addToHistoryChs(instance, ref):
    if config.plugins.spzHistoryZapConf.activate_historyZap.value == 'off':
        return
    if config.ParentalControl.configured.value and config.plugins.spzHistoryZapConf.activate_historyZap.value == 'parental_lock':
        if parentalControl.getProtectionLevel(ref.toCompareString()) != -1:
            return
    if instance.servicePath is not None:
        tmp = instance.servicePath[:]
        tmp.append(ref)
        conta = 0
        borrar = -1
        for x in instance.history:
            xref = devref(x)
            if xref == ref and borrar == -1:
                borrar = conta
            conta = conta + 1

        if borrar > -1:
            del instance.history[borrar]
        if tmp not in instance.history:
            instance.history.append(tmp)
        limpiahistorico(instance)
        hlen = len(instance.history)
        if hlen > config.plugins.spzHistoryZapConf.maxEntries_historyZap.value:
            del instance.history[0]
            hlen -= 1
        instance.history_pos = hlen - 1


ChannelSelection.addToHistory = addToHistoryChs

class HistoryZapConf(ConfigListScreen, Screen):
    if esHD():
        skin = '\n\t\t<screen name="HistoryZapConf" position="80,80" size="945,381" title="%s">\n\t\t\t<widget name="config" position="15,15" size="915,300" scrollbarMode="showOnDemand" itemHeight="42" />\n\t\t\t<ePixmap name="new ePixmap" position="15,318" size="210,60" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/hdred.png" alphatest="blend" />\n\t\t\t<ePixmap name="new ePixmap" position="225,318" size="210,60" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/hdgreen.png" alphatest="blend" />\n\t\t\t<widget name="key_red" position="15,318" zPosition="5" size="210,60" valign="center" halign="center" font="Regular;16" transparent="1" shadowColor="black" shadowOffset="-1,-1" />\n\t\t\t<widget name="key_green" position="225,318" zPosition="5" size="210,60" valign="center" halign="center" font="Regular;16" transparent="1" shadowColor="black" shadowOffset="-1,-1" />\n\t\t</screen>' % _('HistoryZap Configurator')
    else:
        skin = '\n\t\t<screen name="HistoryZapConf" position="80,80" size="630,254" title="%s">\n\t\t\t<widget name="config" position="10,10" size="610,200" scrollbarMode="showOnDemand" />\n\t\t\t<ePixmap name="new ePixmap" position="10,212" size="140,40" pixmap="skin_default/buttons/red.png" alphatest="blend" />\n\t\t\t<ePixmap name="new ePixmap" position="150,212" size="140,40" pixmap="skin_default/buttons/green.png" alphatest="blend" />\n\t\t\t<widget name="key_red" position="10,212" zPosition="5" size="140,40" valign="center" halign="center" font="Regular;16" transparent="1" shadowColor="black" shadowOffset="-1,-1" />\n\t\t\t<widget name="key_green" position="150,212" zPosition="5" size="140,40" valign="center" halign="center" font="Regular;16" transparent="1" shadowColor="black" shadowOffset="-1,-1" />\n\t\t</screen>' % _('HistoryZap Configurator')

    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session
        self['key_red'] = Label('[EXIT] ' + _('Cancel'))
        self['key_green'] = Label('[OK] ' + _('Save'))
        ConfigListScreen.__init__(self, [getConfigListEntry(_('Enable zap history:'), config.plugins.spzHistoryZapConf.activate_historyZap),
         getConfigListEntry(_('Maximum zap history entries:'), config.plugins.spzHistoryZapConf.maxEntries_historyZap),
         getConfigListEntry(_('View mode:'), config.plugins.spzHistoryZapConf.viewMode),
         getConfigListEntry(_('Autozap when move in list:'), config.plugins.spzHistoryZapConf.autoZap)])
        self['actions'] = ActionMap(['OkCancelActions', 'ColorActions'], {'ok': self.save,
         'green': self.save,
         'cancel': self.exit,
         'red': self.exit}, -2)

    def save(self):
        for x in self['config'].list:
            x[1].save()

        self.close()

    def exit(self):
        for x in self['config'].list:
            x[1].cancel()

        self.close()


class HistoryZapBrowserList(MenuList):

    def __init__(self, list, enableWrapAround = False):
        MenuList.__init__(self, list, enableWrapAround, eListboxPythonMultiContent)
        self.l.setFont(0, gFont('Regular', 20))
        self.l.setFont(1, gFont('Regular', 17))


def HistoryZapBrowserListEntry(ref, serviceName, eventName, siact = False):
    res = [serviceName]
    ancho = 480
    if config.plugins.spzHistoryZapConf.viewMode.value == 'picons':
        try:
            if ref.flags & eServiceReference.isGroup:
                ref = getBestPlayableServiceReference(ref, eServiceReference(), True)
        except:
            pass

        sname = ref.toString()
        pngname = ''
        pngname = getPiconName(sname)
        if pngname == '':
            tmp = resolveFilename(SCOPE_CURRENT_SKIN, 'picon_default.png')
            if fileExists(tmp):
                pngname = tmp
            else:
                pngname = resolveFilename(SCOPE_SKIN_IMAGE, 'skin_default/picon_default.png')
        try:
            png = LoadPixmap(pngname)
            res.append(MultiContentEntryPixmapAlphaBlend(pos=(0, fhd(5, 0.2)), size=(fhd(100), fhd(65)), png=png, flags=BT_SCALE | BT_KEEP_ASPECT_RATIO))
        except:
            pass

        xch = 105
        ych = 3
        xev = 105
        ancho = ancho - xev
        yev = 26
        lasflags = RT_HALIGN_LEFT | RT_WRAP
    elif config.plugins.spzHistoryZapConf.viewMode.value == 'menu':
        if siact:
            png = LoadPixmap('/usr/lib/enigma2/python/Plugins/Extensions/spzZapHistory/res/vtv.png')
        else:
            png = LoadPixmap('/usr/lib/enigma2/python/Plugins/Extensions/spzZapHistory/res/tv.png')
        if esHD():
            xch = 35
            ych = 3
            xev = 50
            yev = 25
        else:
            xch = 30
            ych = -1
            xev = 40
            yev = 20
        lasflags = RT_HALIGN_LEFT
        res.append(MultiContentEntryPixmapAlphaBlend(pos=(fhd(5), fhd(3, 3.3)), size=(fhd(20), fhd(20)), png=png, flags=BT_SCALE | BT_KEEP_ASPECT_RATIO))
    else:
        ancho = 330
        xch = 0
        ych = 0
    if config.plugins.spzHistoryZapConf.viewMode.value != 'simple':
        res.append(MultiContentEntryText(pos=(fhd(xev), fhd(yev, 1.8)), size=(fhd(ancho), fhd(40)), font=1, flags=lasflags, text=eventName, color=8947848))
    res.append(MultiContentEntryText(pos=(fhd(xch), fhd(ych)), size=(fhd(ancho), fhd(25)), font=0, text=serviceName))
    return res


def findPicon(serviceName):
    try:
        if '::' in serviceName:
            serviceName = serviceName.split('::')[0] + ':'
    except:
        pass

    serviceName = serviceName.replace(':', '_')
    serviceName = serviceName[:-1]
    from Components.Renderer import Picon
    searchPaths = Picon.searchPaths
    for path in searchPaths:
        pngname = path + serviceName + '.png'
        if fileExists(pngname):
            return pngname

    tmp = resolveFilename(SCOPE_CURRENT_SKIN, 'picon_default.png')
    if fileExists(tmp):
        return tmp
    else:
        return resolveFilename(SCOPE_SKIN_IMAGE, 'skin_default/picon_default.png')
    return ''


def findPiconOLD(serviceName):
    path = str(config.misc.picon_path.value)
    pngname = path + serviceName + '.png'
    if fileExists(pngname):
        return pngname
    searchPaths = [eEnv.resolve('${datadir}/enigma2/picon/'), '/media/cf/picon/', '/media/usb/picon/']
    path = path + 'picon/'
    if path not in searchPaths:
        searchPaths.append(path)
    for path in searchPaths:
        pngname = path + serviceName + '.png'
        if fileExists(pngname):
            return pngname

    return ''


class spzZapHistory(Screen, ProtectedScreen):
    file = resolveFilename(SCOPE_CURRENT_SKIN, 'skin.xml')
    if esHD():
        skin = '\n\t\t<screen name="spzZapHistory" position="86,90" size="645,472" title="%s">\n\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/menuHD.png" position="435,432" size="52,37" transparent="1" alphatest="blend" />\n\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/greenHD.png" position="7,432" size="52,37" transparent="1" alphatest="blend" />\n\t\t<widget name="key_green" position="63,433" zPosition="1" size="142,37" font="Regular; 16" valign="center" halign="left" transparent="1" noWrap="1" />\n\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/redHD.png" position="210,432" size="52,37" transparent="1" alphatest="blend" />\n\t\t<widget name="key_red" position="264,433" zPosition="1" size="142,37" font="Regular; 16" valign="center" halign="left" transparent="1" noWrap="1" />\n\t\t<widget name="key_menu" position="487,433" zPosition="1" size="165,37" font="Regular; 16" valign="center" halign="left" transparent="1" noWrap="1" />\n\t\t<widget name="list" position="0,5" size="652,429" scrollbarMode="showOnDemand" itemHeight="42" />\n\t\t</screen>' % _('HistoryZap List')
    else:
        skin = '\n\t\t<screen name="spzZapHistory" position="36,80" size="430,315" title="%s">\n\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spzZapHistory/res/menu.png" position="290,288" size="35,25" transparent="1" alphatest="blend" />\n\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spzZapHistory/res/green.png" position="5,288" size="35,25" transparent="1" alphatest="blend" />\n\t\t<widget name="key_green" position="42,288" zPosition="1" size="95,25" font="Regular; 16" valign="center" halign="left" transparent="1" noWrap="1" />\n\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spzZapHistory/res/red.png" position="140,288" size="35,25" transparent="1" alphatest="blend" />\n\t\t<widget name="key_red" position="174,288" zPosition="1" size="113,25" font="Regular; 16" valign="center" halign="left" transparent="1" noWrap="1" />\n\t\t<widget name="key_menu" position="325,288" zPosition="1" size="110,25" font="Regular; 16" valign="center" halign="left" transparent="1" noWrap="1" />\n\t\t<widget name="list" position="0,0" size="435,286" scrollbarMode="showOnDemand" />\n\t\t<widget name="titol" position="25,208" zPosition="1" size="410,25" font="Regular; 16" valign="center" halign="left" transparent="1" noWrap="1" />\n\t\t</screen>' % _('HistoryZap List')

    def __init__(self, session, servicelist):
        Screen.__init__(self, session)
        ProtectedScreen.__init__(self)
        self.session = session
        self.real = []
        self.servicelist = servicelist
        self.serviceHandler = eServiceCenter.getInstance()
        self.allowChanges = True
        self['list'] = HistoryZapBrowserList([])
        self['key_green'] = Label(_('Zap'))
        from Screens.InfoBar import InfoBar
        etiqueta = ''
        if InfoBar and InfoBar.instance:
            if SystemInfo.get('NumVideoDecoders', 1) > 1:
                try:
                    etiqueta = 'PiP'
                except:
                    pass

        self['key_red'] = Label(etiqueta)
        self['key_menu'] = Label(_('Options') + '...')
        self['actions'] = ActionMap(['OkCancelActions',
         'ColorActions',
         'MenuActions',
         'DirectionActions'], {'cancel': self.cancel,
         'menu': self.menu,
         'left': self.klef,
         'right': self.krig,
         'up': self.kup,
         'down': self.kdow,
         'ok': self.zapAndClose,
         'blue': self.config,
         'green': self.zap,
         'red': self.zappip}, prio=-1)
        if config.plugins.spzHistoryZapConf.viewMode.value == 'picons':
            self['list'].l.setItemHeight(70)
        elif config.plugins.spzHistoryZapConf.viewMode.value == 'menu':
            self['list'].l.setItemHeight(40)
        else:
            self['list'].l.setItemHeight(22)
        self.onLayoutFinish.append(self.cargadapantalla)
        self.timerAutoZap = eTimer()
        self.timerAutoZap.callback.append(self.zap)

    def cancel(self):
        self.timerAutoZap.stop()
        self.close()

    def cargadapantalla(self):
        self.buildList()
        if config.plugins.spzHistoryZapConf.autoZap.value:
            self.timerAutoZap.startLongTimer(4)

    def buildList(self):
        list = []
        conta = 0
        try:
            if self.session.pipshown:
                refpip = self.session.pip.getCurrentService()
                refmain = self.session.nav.getCurrentlyPlayingServiceOrGroup()
                if refpip:
                    addToHistoryChs(self.servicelist, refpip)
                if refmain:
                    addToHistoryChs(self.servicelist, refmain)
        except:
            pass

        limpiahistorico(self.servicelist)
        for x in self.servicelist.history:
            xiact = False
            ref = devref(x)
            info = self.serviceHandler.info(ref)
            if info:
                name = info.getName(ref).replace('\xc2\x86', '').replace('\xc2\x87', '')
                event = info.getEvent(ref)
                if event is not None:
                    eventName = event.getEventName()
                    if eventName is None:
                        eventName = ''
                else:
                    eventName = ''
            else:
                name = 'N/A'
                eventName = ''
            if conta == len(self.servicelist.history) - 1:
                xiact = True
            list.append(HistoryZapBrowserListEntry(ref, name, eventName, siact=xiact))
            conta = conta + 1

        list.reverse()
        self['list'].setList(list)
        if len(list) > 1:
            self['list'].moveToIndex(1)
        else:
            self['list'].moveToIndex(0)

    def krig(self):
        self.timerAutoZap.stop()
        self['list'].pageDown()
        if config.plugins.spzHistoryZapConf.autoZap.value:
            self.timerAutoZap.startLongTimer(3)

    def klef(self):
        self.timerAutoZap.stop()
        self['list'].pageUp()
        if config.plugins.spzHistoryZapConf.autoZap.value:
            self.timerAutoZap.stop()
            self.timerAutoZap.startLongTimer(3)

    def kup(self):
        self.timerAutoZap.stop()
        pos = self['list'].getSelectionIndex()
        lon = len(self['list'].list)
        if pos == 0 and lon > 1:
            self['list'].moveToIndex(lon - 1)
        else:
            self['list'].up()
        if pos == 1:
            return
        if config.plugins.spzHistoryZapConf.autoZap.value:
            self.timerAutoZap.startLongTimer(3)

    def kdow(self):
        self.timerAutoZap.stop()
        pos = self['list'].getSelectionIndex()
        lon = len(self['list'].list)
        if pos == lon - 1 and lon > 1:
            self['list'].moveToIndex(0)
        else:
            self['list'].down()
            if config.plugins.spzHistoryZapConf.autoZap.value:
                self.timerAutoZap.startLongTimer(3)

    def menu(self):
        self.timerAutoZap.stop()
        from Screens.ChoiceBox import ChoiceBox
        nkeys = ['green']
        possible_actions = [(_('Zap to selected channel'), 'zap')]
        from Screens.InfoBar import InfoBar
        if InfoBar and InfoBar.instance:
            if SystemInfo.get('NumVideoDecoders', 1) > 1:
                try:
                    possible_actions.append((_('View in PiP'), 'zappip'))
                    nkeys.append('red')
                except:
                    pass

        possible_actions.append((_('Clear all history channels'), 'clear'))
        nkeys.append('1')
        possible_actions.append((_('Delete Selected channel from history'), 'delete'))
        nkeys.append('2')
        possible_actions.append((_('Config'), 'config'))
        nkeys.append('3')
        self.session.openWithCallback(self.cbmenu, ChoiceBox, keys=nkeys, title=_('HistoryZap List') + ' - ' + _('Options'), list=possible_actions)

    def cbmenu(self, result):
        if result:
            if result[1] == 'zap':
                self.zap()
            elif result[1] == 'zappip':
                self.zappip()
            elif result[1] == 'delete':
                self.delete()
            elif result[1] == 'clear':
                self.clear()
            elif result[1] == 'config':
                self.config()
            return

    def zappip(self):
        self.timerAutoZap.stop()
        ref = None
        length = len(self.servicelist.history)
        if length > 0:
            idx = length - self['list'].getSelectionIndex() - 1
            x = self.servicelist.history[idx]
            if len(x) == 2:
                ref = x[1]
            elif len(x) == 4:
                ref = x[3]
            else:
                ref = x[2]
        if not ref:
            return
        from Screens.InfoBar import InfoBar
        if InfoBar and InfoBar.instance:
            if SystemInfo.get('NumVideoDecoders', 1) > 1:
                try:
                    if InfoBar.instance.allowPiP:
                        InfoBar.instance.showPiP()
                        self.showPiPj(ref, idx)
                except:
                    pass

    def showPiPj(self, ref = None, idx = None):
        if not ref:
            return
        from Screens.PictureInPicture import PictureInPicture
        self.session.pip = self.session.instantiateDialog(PictureInPicture)
        self.session.pip.show()
        self.session.pipshown = True
        self.session.pip.playService(ref)
        self.session.pip.servicePath = self.servicelist.history[idx]

    def zap(self):
        refmain = None
        try:
            refmain = self.session.nav.getCurrentlyPlayingServiceOrGroup()
        except:
            pass

        self.timerAutoZap.stop()
        length = len(self.servicelist.history)
        if length > 0:
            self.servicelist.history_pos = length - self['list'].getSelectionIndex() - 1
            self.servicelist.setHistoryPath()
            idx = length - self['list'].getSelectionIndex() - 1
            valor = self.servicelist.history[idx]
            try:
                if self.session.pipshown:
                    laref = devref(valor)
                    refpip = self.session.pip.getCurrentService()
                    if refpip.toString() == laref.toString() and refmain.toString() != refpip.toString():
                        self.showPiPj(refmain, 0)
            except:
                pass

            del self.servicelist.history[idx]
            self.servicelist.history.append(valor)
            self.buildList()

    def clear(self):
        self.timerAutoZap.stop()
        if self.allowChanges:
            for i in range(0, len(self.servicelist.history)):
                del self.servicelist.history[0]

            self.buildList()
            self.servicelist.history_pos = 0

    def delete(self):
        self.timerAutoZap.stop()
        if self.allowChanges:
            length = len(self.servicelist.history)
            if length > 0:
                idx = length - self['list'].getSelectionIndex() - 1
                del self.servicelist.history[idx]
                self.buildList()
                currRef = self.session.nav.getCurrentlyPlayingServiceOrGroup()
                idx = 0
                for x in self.servicelist.history:
                    if len(x) == 2:
                        ref = x[1]
                    else:
                        ref = x[2]
                    if ref == currRef:
                        self.servicelist.history_pos = idx
                        break
                    else:
                        idx += 1

    def zapAndClose(self):
        self.timerAutoZap.stop()
        self.zap()
        self.close()

    def config(self):
        self.timerAutoZap.stop()
        if self.allowChanges:
            self.aconf = config.plugins.spzHistoryZapConf.viewMode.value
            self.session.openWithCallback(self.endconf, HistoryZapConf)

    def endconf(self):
        if config.plugins.spzHistoryZapConf.viewMode.value != self.aconf:
            if config.plugins.spzHistoryZapConf.viewMode.value == 'picons':
                self['list'].l.setItemHeight(70)
            elif config.plugins.spzHistoryZapConf.viewMode.value == 'menu':
                self['list'].l.setItemHeight(40)
            else:
                self['list'].l.setItemHeight(22)
            from Tools import Notifications
            from Screens.MessageBox import MessageBox
            Notifications.AddPopup(text=_('Change will be visible the next time you run this window'), type=MessageBox.TYPE_INFO, timeout=3, id='zapHistory')
            self.close()

    def isProtected(self):
        return config.ParentalControl.setuppinactive.value and config.ParentalControl.configured.value

    def pinEntered(self, result):
        if result is None:
            self.allowChanges = False
        elif not result:
            self.allowChanges = False
        else:
            self.allowChanges = True


class spzZapHistoryMenu(spzZapHistory):
    if esHD():
        skin = '\n\t\t<screen name="spzZapHistoryMenu" position="center,center" size="885,900" title="%s">\n\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/menuHD.png" position="646,850" size="52,37" transparent="1" alphatest="blend" />\n\t\t<widget name="key_menu" position="699,850" zPosition="1" size="184,37" font="Regular;16" valign="center" halign="left" transparent="1" noWrap="1" />\n\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/greenHD.png" position="7,850" size="52,37" transparent="1" alphatest="blend" />\n\t\t<widget name="key_green" position="63,850" zPosition="1" size="231,37" font="Regular; 16" valign="center" halign="left" transparent="1" noWrap="1" />\t\t\n\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/redHD.png" position="315,850" size="52,37" transparent="1" alphatest="blend" />\n\t\t<widget name="key_red" position="370,850" zPosition="1" size="264,37" font="Regular; 16" valign="center" halign="left" transparent="1" noWrap="1" />\t\t\n\t\t<widget name="list" position="7,7" size="870,840" scrollbarMode="showOnDemand" />\n\t\t</screen>' % _('HistoryZap List')
    else:
        skin = '\n\t\t<screen name="spzZapHistoryMenu" position="center,center" size="590,600" title="%s">\n\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spzZapHistory/res/menu.png" position="431,567" size="35,25" transparent="1" alphatest="blend" />\n\t\t<widget name="key_menu" position="466,567" zPosition="1" size="123,25" font="Regular;16" valign="center" halign="left" transparent="1" noWrap="1" />\n\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spzZapHistory/res/green.png" position="5,567" size="35,25" transparent="1" alphatest="blend" />\n\t\t<widget name="key_green" position="42,567" zPosition="1" size="154,25" font="Regular; 16" valign="center" halign="left" transparent="1" noWrap="1" />\t\t\n\t\t<ePixmap pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spzZapHistory/res/red.png" position="210,567" size="35,25" transparent="1" alphatest="blend" />\n\t\t<widget name="key_red" position="247,567" zPosition="1" size="176,25" font="Regular; 16" valign="center" halign="left" transparent="1" noWrap="1" />\t\t\n\t\t<widget name="list" position="5,5" size="580,560" scrollbarMode="showOnDemand" />\n\t\t</screen>' % _('HistoryZap List')

    def __init__(self, session, servicelist):
        spzZapHistory.__init__(self, session, servicelist)


def main(session, servicelist, **kwargs):
    try:
        valorconf = config.plugins.spzHistoryZapConf.viewMode.value
    except:
        valorconf = 'simple'

    if valorconf == 'simple':
        session.open(spzZapHistory, servicelist)
    else:
        session.open(spzZapHistoryMenu, servicelist)


def Plugins(**kwargs):
    return PluginDescriptor(name=_('spzZapHistory'), where=PluginDescriptor.WHERE_EXTENSIONSMENU, fnc=main)
