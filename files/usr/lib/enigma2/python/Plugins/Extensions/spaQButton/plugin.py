from Screens.Screen import Screen
from Screens.ChoiceBox import ChoiceBox
from Screens.MessageBox import MessageBox
from Screens.InfoBarGenerics import InfoBarPlugins
from Components.ActionMap import ActionMap
from Components.PluginComponent import plugins
from Components.config import config, ConfigSubsection, ConfigYesNo
from Plugins.Plugin import PluginDescriptor
from QuickButtonXML import QuickButtonXML
from spaQButton import spaQButton, QuickButton, chekaac3
from Components.Label import Label
import xml.sax.xmlreader
import os.path
import os
import keymapparser
from __init__ import _
from Screens.InfoBar import InfoBar
baseInfoBarPlugins__init__ = None

def InfoBarAudioSelection__init__(elself):
    texto = ''
    saltar = True
    try:
        if 'KodiVideoPlayer' in str(elself.skinName):
            saltar = False
    except:
        pass

    if saltar:
        try:
            saltar = elself.session.current_dialog == None
        except:
            pass

    try:
        from Components.ActionMap import HelpableActionMap
        if saltar:
            texto = '** DISABLED audioselection\n'
            elself['AudioSelectionAction'] = HelpableActionMap(elself, 'InfobarAudioSelectionActions', {'noaudioSelection': (elself.audioSelection, _('Audio Options...'))})
        else:
            texto = '* ENABLED audioselection\n'
            elself['AudioSelectionAction'] = HelpableActionMap(elself, 'InfobarAudioSelectionActions', {'audioSelection': (elself.audioSelection, _('Audio Options...'))})
    except Exception as ex:
        texto = texto + '*** Error 0 [' + str(ex) + ']\n'


baserunPlugin = None
StartOnlyOneTime = False
line = '------------------------------------------------------------------'
TimerTempMB = None

def autostart(reason, **kwargs):
    global baseInfoBarPlugins__init__
    global TimerTempMB
    global InfoBarAudioSelection__init__
    global baserunPlugin
    if reason == 0:
        chekaac3()
        if config.plugins.spaQButton.enable.value:
            rePatchKeymap()
            mqbkeymapfile = '/usr/lib/enigma2/python/Plugins/Extensions/spaQButton/keymap'
            bh = ''
            if not os.path.exists(mqbkeymapfile + '.xml'):
                if os.path.exists('/usr/lib/enigma2/python/Blackhole/__init__.py'):
                    os.system("cp '" + mqbkeymapfile + "_bh.xml' '" + mqbkeymapfile + ".xml'")
                    bh = 'bh'
                else:
                    os.system("cp '" + mqbkeymapfile + "_az.xml' '" + mqbkeymapfile + ".xml'")
                    bh = 'openSPA'
            if not os.path.exists('/etc/MultiQuickButton/'):
                os.system('tar -xzvf /usr/lib/enigma2/python/Plugins/Extensions/spaQButton/ini/init_etc.rar.gz -C /')
            checkMQBKeys()
            if 'session' in kwargs:
                session = kwargs['session']
                if baseInfoBarPlugins__init__ is None:
                    baseInfoBarPlugins__init__ = InfoBarPlugins.__init__
                if baserunPlugin is None:
                    baserunPlugin = InfoBarPlugins.runPlugin
                try:
                    from Screens.InfoBarGenerics import InfoBarAudioSelection
                    InfoBarAudioSelection.__init__ = InfoBarAudioSelection__init__
                except:
                    pass

                InfoBarPlugins.__init__ = InfoBarPlugins__init__
                InfoBarPlugins.runPlugin = runPlugin
                InfoBarPlugins.checkQuickSel = checkQuickSel
                InfoBarPlugins.askForQuickList = askForQuickList
                InfoBarPlugins.getQuickList = getQuickList
                InfoBarPlugins.execQuick = execQuick
                InfoBarPlugins.quickSelectGlobal = quickSelectGlobal
                if not os.path.exists('/etc/mkb.init'):
                    from enigma import eTimer
                    TimerTempMB = eTimer()
                    TimerTempMB.callback.append(muestraPresen)
                    TimerTempMB.startLongTimer(12)


def muestraPresen():
    global TimerTempMB
    from Tools.Notifications import AddNotificationWithID, RemovePopup
    notiid = 'mqbopenspa'
    RemovePopup(notiid)
    TimerTempMB = None
    AddNotificationWithID(notiid, presentacionscr)


def checkMQBKeys():
    mqbkeymapfile = '/usr/lib/enigma2/python/Plugins/Extensions/spaQButton/keymap.xml'
    mqbkeymap = open(mqbkeymapfile, 'r')
    text = mqbkeymap.read()
    mqbkeymap.close()
    ptskeys = ['<key id="KEY_PLAY" mapto="play" flags="m" />',
     '<key id="KEY_STOP" mapto="stop" flags="b" />',
     '<key id="KEY_PAUSE" mapto="pause" flags="m" />',
     '<key id="KEY_REWIND" mapto="rewind" flags="b" />',
     '<key id="KEY_FASTFORWARD" mapto="fastforward" flags="b" />',
     '<key id="KEY_PREVIOUSSONG" mapto="rewind" flags="b" />',
     '<key id="KEY_NEXTSONG" mapto="fastforward" flags="b" />']
    keys = ['<key id="KEY_OK" mapto="ok" flags="m" />']
    if os.path.exists('/usr/lib/enigma2/python/Plugins/Extensions/PermanentTimeshift'):
        for ptskey in ptskeys:
            ptskeyinactive = '<!-- ' + ptskey + ' -->'
            if ptskeyinactive not in text:
                text = text.replace(ptskey, ptskeyinactive)

    if config.plugins.spaQButton.okexitstate.value:
        for key in keys:
            okexitinactive = '<!-- ' + key + ' -->'
            if okexitinactive in text:
                text = text.replace(okexitinactive, key)

    else:
        for key in keys:
            okexitinactive = '<!-- ' + key + ' -->'
            if okexitinactive not in text:
                text = text.replace(key, okexitinactive)

    mqbkeymap = open(mqbkeymapfile, 'w')
    mqbkeymap.write(text)
    mqbkeymap.close()
    keymapparser.removeKeymap(mqbkeymapfile)
    keymapparser.readKeymap(mqbkeymapfile)


def rePatchKeymap():
    globalkeymapfile = '/usr/share/enigma2/keymap.xml'
    globalkeymap = open(globalkeymapfile, 'r')
    text = globalkeymap.read()
    globalkeymap.close()
    globalkeys = ['<key id="KEY_YELLOW" mapto="timeshiftStart" flags="m" />',
     '<key id="KEY_YELLOW" mapto="timeshiftActivateEndAndPause" flags="m" />',
     '<key id="KEY_VIDEO" mapto="showMovies" flags="m" />',
     '<key id="KEY_RADIO" mapto="showRadio" flags="m" />',
     '<key id="KEY_TEXT" mapto="startTeletext" flags="m" />',
     '<key id="KEY_PLAYPAUSE" mapto="timeshiftStart" flags="m" />',
     '<key id="KEY_PAUSE" mapto="timeshiftStart" flags="m" />',
     '<key id="KEY_RECORD" mapto="instantRecord" flags="m" />',
     '<key id="KEY_HELP" mapto="displayHelp" flags="m" />']
    cambiado = text
    for globalkey in globalkeys:
        globalkeyreplace = globalkey.replace('"m"', '"b"')
        text = text.replace(globalkey, globalkeyreplace)

    text = text.replace('id="KEY_AUDIO" mapto="audio_key"', 'id="KEY_AUDIO" mapto="audioSelection"')
    if not text == cambiado:
        globalkeymap = open(globalkeymapfile, 'w')
        globalkeymap.write(text)
        globalkeymap.close()
        keymapparser.removeKeymap(globalkeymapfile)
        keymapparser.readKeymap(globalkeymapfile)


def InfoBarPlugins__init__(self):
    global StartOnlyOneTime
    if not StartOnlyOneTime:
        StartOnlyOneTime = True
        self['QuickButtonActions'] = MQBActionMap(['QuickButtonActions', 'HelpActions'], {'red': self.quickSelectGlobal,
         'red_long': self.quickSelectGlobal,
         'green': self.quickSelectGlobal,
         'green_long': self.quickSelectGlobal,
         'yellow': self.quickSelectGlobal,
         'yellow_long': self.quickSelectGlobal,
         'blue': self.quickSelectGlobal,
         'blue_long': self.quickSelectGlobal,
         'pvr': self.quickSelectGlobal,
         'pvr_long': self.quickSelectGlobal,
         'radio': self.quickSelectGlobal,
         'radio_long': self.quickSelectGlobal,
         'tv': self.quickSelectGlobal,
         'text': self.quickSelectGlobal,
         'text_long': self.quickSelectGlobal,
         'help_long': self.quickSelectGlobal,
         'info': self.quickSelectGlobal,
         'info_long': self.quickSelectGlobal,
         'end': self.quickSelectGlobal,
         'end_long': self.quickSelectGlobal,
         'home': self.quickSelectGlobal,
         'home_long': self.quickSelectGlobal,
         'cross_up': self.quickSelectGlobal,
         'cross_down': self.quickSelectGlobal,
         'cross_left': self.quickSelectGlobal,
         'cross_right': self.quickSelectGlobal,
         'channeldown': self.quickSelectGlobal,
         'channelup': self.quickSelectGlobal,
         'next': self.quickSelectGlobal,
         'previous': self.quickSelectGlobal,
         'audio': self.quickSelectGlobal,
         'subtitle': self.quickSelectGlobal,
         'ok': self.quickSelectGlobal,
         'exit': self.quickSelectGlobal,
         'play': self.quickSelectGlobal,
         'stop': self.quickSelectGlobal,
         'pause': self.quickSelectGlobal,
         'fastforward': self.quickSelectGlobal,
         'rewind': self.quickSelectGlobal,
         'f1': self.quickSelectGlobal,
         'f2': self.quickSelectGlobal,
         'f3': self.quickSelectGlobal,
         'key0': self.quickSelectGlobal,
         'stop_long': self.quickSelectGlobal,
         'pause_long': self.quickSelectGlobal,
         'back': self.quickSelectGlobal,
         'play_long': self.quickSelectGlobal,
         'forward': self.quickSelectGlobal,
         'record': self.quickSelectGlobal,
         'record_long': self.quickSelectGlobal,
         'program': self.quickSelectGlobal,
         'program_long': self.quickSelectGlobal,
         'file': self.quickSelectGlobal,
         'file_long': self.quickSelectGlobal,
         'list': self.quickSelectGlobal,
         'list_long': self.quickSelectGlobal,
         'displayHelp': self.quickSelectGlobal}, -3)
    else:
        InfoBarPlugins.__init__ = InfoBarPlugins.__init__
        InfoBarPlugins.runPlugin = InfoBarPlugins.runPlugin
        InfoBarPlugins.quickSelectGlobal = None
    baseInfoBarPlugins__init__(self)


def runPlugin(self, plugin):
    baserunPlugin(self, plugin)


def checkQuickSel(self, path):
    list = None
    button = os.path.basename(path)[12:-4]
    try:
        menu = xml.dom.minidom.parse(path)
        db = QuickButtonXML(menu)
        list = db.getSelection()
    except Exception as e:
        self.session.open(MessageBox, 'XML ' + _('Error') + ': %s' % e, MessageBox.TYPE_ERROR)

    if list != None:
        if len(list) == 1:
            self.execQuick(list[0])
        elif len(list) > 1:
            self.session.openWithCallback(self.askForQuickList, ChoiceBox, _('Menu') + ' ' + _('Key: ') + _(button), self.getQuickList(list))
        elif os.path.exists(path):
            self.session.open(QuickButton, path, _('Quickbutton: Key ') + button)
        else:
            self.session.open(MessageBox, _('file %s not found!') % path, MessageBox.TYPE_ERROR)


def askForQuickList(self, res):
    if res is None:
        pass
    else:
        self.execQuick(res)


def getQuickList(self, list):
    quickList = []
    for e in list:
        e2 = [_(e[0]),
         e[1],
         e[2],
         e[3],
         e[4],
         e[5]]
        quickList.append(e2)

    return quickList


def execQuick(self, entry):
    if entry != None:
        if entry[3] != '':
            try:
                module_import = 'from ' + entry[3] + ' import *'
                exec module_import
                if entry[4] != '':
                    try:
                        screen = 'self.session.open(' + entry[4] + ')'
                        exec screen
                    except Exception as e:
                        self.session.open(MessageBox, 'Screen ' + _('Error') + ': %s' % e, MessageBox.TYPE_ERROR)

            except Exception as e:
                self.session.open(MessageBox, 'Module ' + _('Error') + ': %s' % e, MessageBox.TYPE_ERROR)

        if entry[5] != '':
            try:
                exec entry[5]
            except Exception as e:
                self.session.open(MessageBox, 'Code ' + _('Error') + ': %s' % e, MessageBox.TYPE_ERROR)


def quickSelectGlobal(self, key):
    if key:
        if key == 'displayHelp':
            self.session.open(spaQButton, mostrarayuda=True)
            return
        haytime = False
        try:
            haytime = InfoBar.instance.timeshift_enabled > 0
        except:
            pass

        if haytime and (key == 'pause' or key == 'play' or key == 'stop'):
            return
        path = '/etc/MultiQuickButton/quickbutton_' + key + '.xml'
        if os.path.exists(path):
            self.checkQuickSel(path)
        else:
            os.system("cp '/usr/lib/enigma2/python/Plugins/Extensions/spaQButton/quickbutton_.xml' '" + path + "'")
            if os.path.exists(path):
                self.checkQuickSel(path)
            else:
                self.session.open(MessageBox, 'file %s not found!' % path, MessageBox.TYPE_ERROR)


class MQBActionMap(ActionMap):

    def action(self, contexts, action):
        quickSelection = ('red', 'red_long', 'green', 'green_long', 'yellow', 'yellow_long', 'blue', 'blue_long', 'pvr', 'pvr_long', 'radio', 'radio_long', 'text', 'text_long', 'help_long', 'info', 'info_long', 'end', 'end_long', 'home', 'home_long', 'cross_up', 'cross_down', 'cross_left', 'cross_right', 'previous', 'next', 'channelup', 'channeldown', 'f1', 'f2', 'f3', 'audio', 'subtitle', 'exit', 'ok', 'play', 'pause', 'rewind', 'fastforward', 'stop', 'tv', 'stop_long', 'key0', 'pause_long', 'back', 'play_long', 'forward', 'record', 'record_long', 'displayHelp', 'program', 'program_long', 'list', 'list_long', 'file', 'file_long')
        if action in quickSelection and self.actions.has_key(action):
            res = self.actions[action](action)
            if res is not None:
                return res
            return 1
        else:
            return ActionMap.action(self, contexts, action)


class presentacionscr(Screen):
    skin = '\n\t\t<screen name="presentacionscr" position="center,center" size="780,400" title="openSPA. Remote control setup">\n                <ePixmap name="logo" position="0,0" size="197,86" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spaQButton/img/pingui2-fs8.png" zPosition="0" alphatest="blend" />\n\t\t<ePixmap name="tecla" position="212,11" size="48,62" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spaQButton/img/teclafs8.png" zPosition="20" alphatest="blend" />\n\t\t<ePixmap name="mando" position="0,95" size="185,310" pixmap="skin_default/rc.png" zPosition="0" alphatest="blend" />\n\t\t<widget name="key_info0" position="270,28" size="513,50" halign="left" font="Regular; 20" backgroundColor="#00000000" transparent="1" />\n\t\t<ePixmap name="punto1" position="222,92" size="25,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spaQButton/pic/button_green.png" zPosition="20" alphatest="blend" />\n\t\t<widget name="key_info1" position="260,92" size="513,75" font="Regular; 18" valign="top" halign="left" transparent="1" backgroundColor="#00000000" />\n\t\t<ePixmap name="punto2" position="222,192" size="25,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spaQButton/pic/button_green.png" zPosition="20" alphatest="blend" />\n\t\t<widget name="key_info2" position="260,192" size="501,75" font="Regular; 18" valign="top" halign="left" transparent="1" backgroundColor="#00000000" />\n\t\t<ePixmap name="punto1" position="222,292" size="25,25" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spaQButton/pic/button_green.png" zPosition="20" alphatest="blend" />\n\t\t<widget name="key_info3" position="260,292" size="530,111" font="Regular; 18" valign="top" halign="left" transparent="1" backgroundColor="#00000000" />\n\t\t<widget name="key_tecla" position="197,0" size="1,405" font="Regular; 21" halign="center" backgroundColor="#05555555" foregroundColor="#00000000" zPosition="22" />\n\t\t</screen>'

    def __init__(self, session, args = 0):
        self.session = session
        Screen.__init__(self, session)
        self.onShown.append(self.setWindowTitle)
        self['key_tecla'] = Label('')
        self['key_info0'] = Label(_('This utility will allow you to view and modify to your liking the remote control.'))
        self['key_info1'] = Label(_('Closing this window you will see a list of pre-assigned functions of command. You can customize it as you wish.'))
        self['key_info2'] = Label(_('Pressing any key will be located in that key listed. Press [OK] to view / edit actions.'))
        self['key_info3'] = Label(_('The Welcome screen does not reappear. Remember you can return to the settings from the remote:\nMenu -> Customize -> Customize the buttons on the remote.'))
        self['actions'] = ActionMap(['SetupActions', 'ColorActions'], {'green': self.exit,
         'red': self.exit,
         'blue': self.exit,
         'yellow': self.exit,
         'save': self.exit,
         'cancel': self.exit,
         'ok': self.exit}, -2)

    def exit(self):
        InfoBar.instance.session.open(spaQButton)
        os.system('date >/etc/mkb.init')
        self.close()

    def setWindowTitle(self):
        self.setTitle(_('openSPA. Remote control setup'))


def main(session, **kwargs):
    session.open(spaQButton)


def menu(menuid, **kwargs):
    if menuid == 'mainmenu':
        return [(_('Multi Quickbutton'),
          main,
          'multi_quick',
          55)]
    return []


def Plugins(**kwargs):
    return [PluginDescriptor(where=[PluginDescriptor.WHERE_SESSIONSTART, PluginDescriptor.WHERE_AUTOSTART], fnc=autostart)]
