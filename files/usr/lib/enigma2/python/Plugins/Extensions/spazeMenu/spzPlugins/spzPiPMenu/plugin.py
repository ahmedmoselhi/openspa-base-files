from Plugins.Plugin import PluginDescriptor
from Screens.InfoBar import InfoBar
from Components.SystemInfo import SystemInfo
from Screens.ChoiceBox import ChoiceBox
from Tools import Notifications
from Components.config import config, ConfigSubsection
from Components.SystemInfo import SystemInfo
from os import environ
import gettext
from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE, fileExists
lang = language.getLanguage()
environ['LANGUAGE'] = lang[:2]
gettext.bindtextdomain('enigma2', resolveFilename(SCOPE_LANGUAGE))
gettext.textdomain('enigma2')
gettext.bindtextdomain('spzPiPMenu', '%s%s' % (resolveFilename(SCOPE_PLUGINS), 'Extensions/spazeMenu/spzPlugins/spzPiPMenu/locale/'))

def _(txt):
    t = gettext.dgettext('spzPiPMenu', txt)
    if t == txt:
        t = gettext.gettext(txt)
    return t


def ponlcd(cualo = '0'):
    f = open('/proc/stb/lcd/mode', 'w')
    f.write(str(cualo))
    f.close()
    if int(str(cualo)) >= 5:
        f = open('/proc/stb/vmpeg/1/dst_width', 'w')
        f.write('0')
        f.close()
        f = open('/proc/stb/vmpeg/1/dst_height', 'w')
        f.write('0')
        f.close()
        f = open('/proc/stb/vmpeg/1/dst_apply', 'w')
        f.write('1')
        f.close()
    if int(str(cualo)) == 0 and (config.misc.boxtype.value == 'gbquad' or config.misc.boxtype.value == 'gbquadplus'):
        config.lcd.modepip.value = '0'


def getlcd():
    f = open('/proc/stb/lcd/mode', 'r')
    cret = f.read()
    f.close()
    return int(cret.replace('\n', '').replace('\t', '').replace('\r', ''))


iniPiP = None

def pipmenu(session, nomenu = False, limitar = False, refPip = None):
    global iniPiP
    iniPiP = refPip
    if InfoBar and InfoBar.instance:
        nkeys = []
        list = []
        haytogle = True
        try:
            prueba = InfoBar.instance.getTogglePipzapName()
        except:
            haytogle = False

        if SystemInfo.get('NumVideoDecoders', 1) > 1:
            try:
                if InfoBar.instance.allowPiP:
                    if InfoBar.instance.pipShown():
                        list.append((_(InfoBar.instance.getShowHideName()) + ' ', 'showPiP'))
                        nkeys.append('blue')
                        if not limitar:
                            list.append((_(InfoBar.instance.getSwapName()) + ' ', 'swapPiP'))
                            nkeys.append('yellow')
                        if not limitar and haytogle:
                            list.append((_(InfoBar.instance.getTogglePipzapName()) + ' ', 'togglePipzap'))
                            nkeys.append('red')
                        list.append((_(InfoBar.instance.getMoveName()) + ' ', 'movePiP'))
                        nkeys.append('green')
                        if config.misc.boxtype.value == 'gbquad' or config.misc.boxtype.value == 'gbquadplus':
                            if getlcd() != 5:
                                list.append((_('Show Pip in LCD screen'), 'pipLcd'))
                            else:
                                list.append((_('Disable Pip in LCD screen'), 'pipLcd'))
                            nkeys.append('0')
                    else:
                        if nomenu and not (SystemInfo['Display'] and SystemInfo['LCDMiniTV']):
                            InfoBar.instance.showPiP()
                            return
                        list.append((_(InfoBar.instance.getShowHideName()) + ' ', 'showPiP'))
                        nkeys.append('blue')
                        if config.misc.boxtype.value == 'gbquad' or config.misc.boxtype.value == 'gbquadplus':
                            if getlcd() != 5:
                                list.append((_('Activate Picture in Picture in LCD screen'), 'pipLcd'))
                                nkeys.append('0')
                    if SystemInfo['Display'] and SystemInfo['LCDMiniTV']:
                        if getlcd() == 0:
                            list.append((_('Show current image in LCD screen'), 'Lcd'))
                        elif getlcd() < 5:
                            list.append((_('Disable Show current image in LCD screen'), 'Lcd'))
                        nkeys.append('1')
                    session.openWithCallback(cbselmenu, ChoiceBox, keys=nkeys, title=_('Select Pip Option:'), list=list)
            except:
                pass


def cbselmenu(answer):
    answer = answer and answer[1]
    try:
        if iniPiP:
            InfoBar.instance.lastPiPService = iniPiP
        if answer == 'showPiP':
            if InfoBar.instance.pipShown() and InfoBar.instance.allowPiP and SystemInfo['Display'] and SystemInfo['LCDMiniTV']:
                if getlcd() == 5:
                    config.lcd.modepip.value = '0'
            InfoBar.instance.showPiP()
        elif answer == 'movePiP':
            InfoBar.instance.movePiP()
        elif answer == 'swapPiP':
            InfoBar.instance.swapPiP()
        elif answer == 'togglePipzap':
            InfoBar.instance.togglePipzap()
        elif answer == 'pipLcd':
            if getlcd() != 5:
                ponlcd('5')
                oldvalue = config.lcd.modepip.value
                config.lcd.modepip.value = '5'
                if not InfoBar.instance.pipShown():
                    InfoBar.instance.showPiP()
            else:
                if InfoBar.instance.pipShown() and InfoBar.instance.allowPiP and SystemInfo['Display'] and SystemInfo['LCDMiniTV']:
                    InfoBar.instance.showPiP()
                ponlcd('0')
                config.lcd.modepip.value = '0'
        elif answer == 'Lcd':
            if getlcd() > 0:
                ponlcd('0')
                config.lcd.modeminitv.value = '0'
            else:
                ponlcd('1')
                config.lcd.modeminitv.value = '1'
    except:
        pass
