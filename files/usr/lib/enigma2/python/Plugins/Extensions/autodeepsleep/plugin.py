from Plugins.Plugin import PluginDescriptor
from Components.config import config, getConfigListEntry
from autodeepstandby import *
from os import environ
import gettext
from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE
lang = language.getLanguage()
environ['LANGUAGE'] = lang[:2]
lenguaje = str(lang[:2])
gettext.bindtextdomain('enigma2', resolveFilename(SCOPE_LANGUAGE))
gettext.textdomain('enigma2')
gettext.bindtextdomain('autodeepsleep', '%s%s' % (resolveFilename(SCOPE_PLUGINS), 'Extensions/autodeepsleep/locale/'))

def _(txt):
    t = gettext.dgettext('autodeepsleep', txt)
    if t == txt:
        t = gettext.gettext(txt)
    return t


def Plugins(**kwargs):
    return [PluginDescriptor(name=_('AutoDeepStandby'), where=[PluginDescriptor.WHERE_AUTOSTART, PluginDescriptor.WHERE_SESSIONSTART], fnc=autostart, wakeupfnc=getNextWakeup), PluginDescriptor(name=_('AutoDeepStandby'), description=_('Put receiver automatically in deep standby a wakeup it'), where=PluginDescriptor.WHERE_MENU, fnc=autodeep_menu)]


def autodeep_menu(menuid, **kwargs):
    if menuid == 'shutdown':
        return [(_('AutoDeepStandby'),
          main,
          'openSpaAutoDeep',
          1)]
    return []


def main(session, **kwargs):
    try:
        session.open(AutoDeepStandby)
    except:
        pass


from Screens.Screen import Screen
from Components.ConfigList import ConfigListScreen
from Components.ActionMap import ActionMap
from Components.Button import Button
from Components.Label import Label

class AutoDeepStandby(ConfigListScreen, Screen):
    skin = '\n\t\t\t<screen position="center,center" size="720,420" title="%s" >\n\t\t\t\t\t\t<widget name="config" position="10,110" size="700,200" scrollbarMode="showOnDemand" transparent="1" />\n\n\t\t\t<widget name="key_red" position="0,380" size="140,40" valign="center" halign="center" zPosition="4" foregroundColor="white" font="Regular;18" transparent="1" borderColor="black" borderWidth="1"/> \n\t\t\t<widget name="key_green" position="140,380" size="140,40" valign="center" halign="center" zPosition="4" foregroundColor="white" font="Regular;18" transparent="1" borderColor="black" borderWidth="1"/> \n\t\t\t\n\t\t\t<ePixmap name="red" position="0,380" zPosition="2" size="140,40" pixmap="skin_default/buttons/red.png" transparent="1" alphatest="blend" />\n\t\t\t<ePixmap name="green" position="140,380" zPosition="2" size="140,40" pixmap="skin_default/buttons/green.png" transparent="1" alphatest="blend" />\n\t\t\t\n\t\t\t<ePixmap name="yellow" position="560,380" zPosition="2" size="140,40" pixmap="skin_default/buttons/yellow.png" transparent="1" alphatest="blend"  />\n\t\t\t<widget name="key_yellow" position="560,380" size="140,40" valign="center" halign="center" zPosition="4" foregroundColor="white" font="Regular;18" transparent="1" borderColor="black" borderWidth="1"/> \n\t\t\t<ePixmap name="logo" position="615,16" size="100,40" alphatest="blend" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/autodeepsleep/icon.png"/>\n\t\t\t<widget name="infoini" position="10,16" size="595,80" zPosition="20" transparent="0" font="Regular;17" />\n\t\t\t<widget name="info" position="0,6" size="720,370" zPosition="20" transparent="0" font="Regular;18" />\n\t\t\n\t\t</screen>' % _('AutoDeepStandby')

    def __init__(self, session, args = 0):
        self.session = session
        Screen.__init__(self, session)
        self.list = []
        self.list.append(getConfigListEntry('' + _('Enabled auto deep sleep'), config.plugins.autodeepsleep.enable))
        self.list.append(getConfigListEntry('' + _('Sleep time'), config.plugins.autodeepsleep.sleep))
        self.list.append(getConfigListEntry('' + _('Wakeup time'), config.plugins.autodeepsleep.wakeup))
        ConfigListScreen.__init__(self, self.list)
        self['key_red'] = Button(_('Cancel'))
        self['key_green'] = Button(_('Save'))
        self['key_yellow'] = Button(_('Help'))
        infotxt = ''
        infotxt = infotxt + '\n* ' + _('This utility allow put in deep standby (minimum power consumition) and wake up automaticaly, daily with programable hours')
        infotxt = infotxt + '\n\n' + '* ' + _('In deep sleep mode, the box is off, no network, no video/audio ouput')
        infotxt = infotxt + '\n\n' + '* ' + _('The timer list works. The box power on 3 minutes before timer record starts and if the timer is set with the auto option, the box is put in deep standby ant end')
        infotxt = infotxt + '\n\n' + '* ' + _('When wakeup time, the box power on 3 minutes before the time configured')
        infotxt = infotxt + '\n(' + _('For deactivate wake up put the same time of sleep time') + ')'
        self['info'] = Label(infotxt)
        self['info'].hide()
        self['infoini'] = Label(_('Put receiver automatically in deep standby a wakeup it'))
        self.ayuda = False
        self['setupActions'] = ActionMap(['SetupActions', 'ColorActions'], {'red': self.cancel,
         'green': self.save,
         'save': self.save,
         'cancel': self.cancel,
         'yellow': self.verayuda,
         'ok': self.save}, -2)

    def verayuda(self):
        if self.ayuda:
            self['key_green'].show()
            self['key_red'].show()
            self['info'].hide()
            self['infoini'].show()
            self.ayuda = False
            return
        self['infoini'].hide()
        self['key_green'].hide()
        self['key_red'].hide()
        self['info'].show()
        self.ayuda = True

    def save(self):
        if self.ayuda:
            self.verayuda()
            return
        for x in self['config'].list:
            x[1].save()

        debugtxt('init set config screen', '', True)
        ini_timer(self.session)
        info_timer(self.session)
        self.close(False, self.session)

    def cancel(self):
        if self.ayuda:
            self.verayuda()
            return
        for x in self['config'].list:
            x[1].cancel()

        self.close(False, self.session)
