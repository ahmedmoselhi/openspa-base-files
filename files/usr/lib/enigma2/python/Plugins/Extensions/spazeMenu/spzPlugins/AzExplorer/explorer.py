from enigma import eTimer
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaBlend
from enigma import eListboxPythonMultiContent, gFont, BT_SCALE, BT_KEEP_ASPECT_RATIO
from Tools.LoadPixmap import LoadPixmap
from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Screens.InfoBar import MoviePlayer as MP_parent
from Screens.InfoBar import InfoBar
from Screens.Console import Console
from Screens.ChoiceBox import ChoiceBox
from Screens.MessageBox import MessageBox
from Screens.EventView import EventViewSimple
from Components.ActionMap import ActionMap
from Components.FileList import FileList
from Components.MenuList import MenuList
from Components.Label import Label
from Components.Button import Button
from Components.ScrollLabel import ScrollLabel
from Components.Pixmap import Pixmap, MovingPixmap
from Components.AVSwitch import AVSwitch
from Components.config import config, ConfigSubsection, ConfigYesNo, ConfigSelection, getConfigListEntry, ConfigText, ConfigDirectory
from Components.ConfigList import ConfigListScreen
from Tools.Directories import fileExists, pathExists, resolveFilename, SCOPE_LANGUAGE, SCOPE_PLUGINS
from Tools.HardwareInfo import HardwareInfo
from ServiceReference import ServiceReference
from myFileList import readlinkabs, devpermisos, formateafecha, setOrden, getOrden, FileList as myFileList
from Screens.InputBox import InputBox
from Plugins.Extensions.spazeMenu.spzVirtualKeyboard import spzVirtualKeyboard
from Plugins.Extensions.spazeMenu.plugin import esHD, fhd
if fileExists('/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/PicturePlayer/plugin.pyo') or fileExists('/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/PicturePlayer/plugin.pyc'):
    from Plugins.Extensions.PicturePlayer.plugin import Pic_Thumb, picshow
    PicPlayerAviable = True
else:
    PicPlayerAviable = False
if fileExists('/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/DVDPlayer/plugin.pyo') or fileExists('/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/DVDPlayer/plugin.pyc'):
    from Plugins.Extensions.DVDPlayer.plugin import DVDPlayer
    DVDPlayerAviable = True
else:
    DVDPlayerAviable = False
if fileExists('/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/MerlinMusicPlayer/plugin.pyo') or fileExists('/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/MerlinMusicPlayer/plugin.pyc'):
    from Plugins.Extensions.MerlinMusicPlayer.plugin import MerlinMusicPlayerScreen, Item
    MMPavaiable = True
else:
    MMPavaiable = False
from enigma import eConsoleAppContainer, eServiceReference, ePicLoad, getDesktop, eServiceCenter
from os import system as os_system
from os import stat as os_stat
from os import walk as os_walk
from os import popen as os_popen
from os import rename as os_rename
from os import mkdir as os_mkdir
from os import path as os_path
from os import listdir as os_listdir
from time import strftime as time_strftime
from time import localtime as time_localtime
from Components.Language import language
from Components.Label import Label
from os import environ
import os
import gettext
import stat
lang = language.getLanguage()
environ['LANGUAGE'] = lang[:2]
gettext.bindtextdomain('enigma2', resolveFilename(SCOPE_LANGUAGE))
gettext.textdomain('enigma2')
gettext.bindtextdomain('AzExplorer', '%s%s' % (resolveFilename(SCOPE_PLUGINS), 'Extensions/spazeMenu/spzPlugins/AzExplorer/locale/'))

def _(txt):
    t = gettext.dgettext('AzExplorer', txt)
    if t == txt:
        t = gettext.gettext(txt)
    return t


config.plugins.azExplorer = ConfigSubsection()
config.plugins.azExplorer.startDir = ConfigDirectory(default='/', visible_width=150)
config.plugins.azExplorer.ultimodir = ConfigText(default='/')
config.plugins.azExplorer.MediaFilter = ConfigText(default='off')
config.plugins.azExplorer.CopyDest = ConfigText(default='/')
config.plugins.azExplorer.showbookmarks = ConfigYesNo(default=True)
config.plugins.azExplorer.showinmenu = ConfigYesNo(default=True)
config.plugins.azExplorer.remenberpath = ConfigYesNo(default=True)
config.plugins.azExplorer.confirmexit = ConfigYesNo(default=True)
config.plugins.azExplorer.orden = ConfigSelection(default='0', choices=[('1', _('Name')),
 ('2', _('Date')),
 ('3', _('Size')),
 ('0', _('Remenber last'))])
config.plugins.azExplorer.ultimoorden = ConfigText(default='1')
explSession = None
HDSkn = False
sz_w = getDesktop(0).size().width()
if sz_w > 800:
    HDSkn = True
else:
    HDSkn = False
salirespera = False

def formateahora(lafecha = None):
    if not lafecha == None:
        t2 = lafecha
    else:
        t2 = time_localtime()
    chora = ' ' + str(time_strftime('%H:%M', t2))
    return str(chora)


def salirEspera():
    global salirespera
    return salirespera


def showExpl(dummy_self = None):
    global explSession
    explSession.open(azExplorerII)


def ejecutaOrden(self, ordenexec):
    hayError = True
    filename = '/tmp/azexplog.log'
    os_system(ordenexec + ' 2>' + filename)
    if os.path.exists(filename):
        xfile = os_stat(filename)
        if xfile.st_size > 0:
            cerror = ordenexec + '\n'
            try:
                flines = open(filename, 'r')
                for line in flines:
                    cerror = cerror + line

                flines.close()
            except:
                pass

            dei = self.session.open(MessageBox, _('Command execution error:') + '\n' + cerror, MessageBox.TYPE_ERROR)
            dei.setTitle(_('az-Explorer'))
            hayError = False
    os_system('rm ' + filename)
    return hayError


class esperaExplorer(Screen):
    if esHD():
        skin = '\n\t\t<screen position="center,center" size="390,139" title="%s" >\n\t\t\t<ePixmap name="new ePixmap" position="0,0" size="130,139" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/AzExplorer/res/hdiconofs8.png" alphatest="blend" />\n\t\t\t<widget name="texto" position="135,0" size="240,139" valign="center" halign="left" font="Regular;20" itemHeight="42" />\n\t\t</screen>' % _('az-Explorer')
    else:
        skin = '\n\t\t<screen position="center,center" size="260,93" title="%s" >\n\t\t\t<ePixmap name="new ePixmap" position="0,0" size="87,93" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/AzExplorer/res/iconofs8.png" alphatest="blend" />\n\t\t\t<widget name="texto" position="90,0" size="160,93" valign="center" halign="left" font="Regular;20" />\n \t\t</screen>' % _('az-Explorer')

    def __init__(self, session):
        self.session = session
        Screen.__init__(self, session)
        self['texto'] = Label(_('Starting'))
        self.puntos = ''
        self.TimerTemp = eTimer()
        self.TimerTemp.callback.append(self.mirar)
        self.iniciado = False
        self['actions'] = ActionMap(['DirectionActions',
         'ShortcutActions',
         'WizardActions',
         'EPGSelectActions'], {'ok': self.nada,
         'green': self.nada,
         'red': self.nada,
         'back': self.nada,
         'info': self.nada,
         'left': self.nada,
         'right': self.nada,
         'up': self.nada,
         'down': self.nada}, -1)
        self.onShow.append(self.mirar)

    def mirar(self):
        if not self.iniciado:
            self.iniciado = True
        self.TimerTemp.stop()
        if salirespera:
            self.TimerTemp.callback.append(self.exit)
            self.TimerTemp.startLongTimer(1)
        else:
            if self.puntos == '...':
                self.puntos = ''
            elif self.puntos == '':
                self.puntos = '.'
            elif self.puntos == '.':
                self.puntos = '..'
            elif self.puntos == '..':
                self.puntos = '...'
            self['texto'].setText(_('Starting') + self.puntos)
            self.TimerTemp.startLongTimer(1)

    def exit(self):
        self.TimerTemp.stop()
        self.close()

    def nada(self):
        pass


textoayuda = _('azExplorer by mpiero (azboxhd.es) 2011\nBased on Dreambox-Explorer coded 2010 by Vali') + '\n\n' + _('Special keys:') + '\n\n[EXIT] ' + _('Exit') + '\n[OK] ' + _('Action') + '\n[|<] [<<] ' + _('Parent Directory') + '\n[CH+][CH-] ' + _('Swicth sort') + '\n[<-][->] ' + _('Page up, Page down') + '\n[MENU] ' + _('Options')
textoayuda = textoayuda.replace('azboxhd.es', 'openSPA.info')
from Plugins.Extensions.spazeMenu.sbar import openspaSB

class ConfiguraAZ(ConfigListScreen, Screen):
    if esHD():
        skin = '\n\t\t\t<screen position="100,100" size="1425,615" title="%s" >\n\t\t\t<widget name="config" position="0,0" size="1425,390" scrollbarMode="showOnDemand" itemHeight="42" />\n\t\t\t<ePixmap alphatest="blend" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/yellowHD.png" position="0,420" size="52,37" zPosition="5" />\n\t\t\t<widget name="cdir" position="67,420" size="810,33" valign="left" halign="top" zPosition="4" font="Regular;18" transparent="1"/> \t\t\n\t\t\t<widget name="cdir2" position="82,453" size="810,33" valign="left" halign="top" zPosition="4" font="Regular;16" transparent="1"/> \n\t\t\t<widget name="key_red" position="0,540" size="210,60" valign="center" halign="center" zPosition="4" font="Regular;18" transparent="1"/> \n\t\t\t<widget name="key_green" position="210,540" size="210,60" valign="center" halign="center" zPosition="4" font="Regular;18" transparent="1"/> \n\t\t\t<widget name="key_blue" position="1125,540" size="210,60" valign="center" halign="center" zPosition="4" font="Regular;18" transparent="1"/> \n\t\t\t<ePixmap name="red"    position="0,540"   zPosition="2" size="210,60" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/hdred.png" transparent="1" alphatest="blend" />\n\t\t\t<ePixmap name="green"  position="210,540" zPosition="2" size="210,60" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/hdgreen.png" transparent="1" alphatest="blend" />\n\t\t\t<ePixmap name="blue"  position="1125,540" zPosition="2" size="210,60" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/hdblue.png" transparent="1" alphatest="blend" />\n\t\t\t<widget name="barrapix_arr" position="0,0" zPosition="19" size="30,30" alphatest="blend" transparent="1" />\n\t\t\t<widget name="barrapix_abj" position="0,0" zPosition="19" size="30,30" alphatest="blend" transparent="1" />\t\t\t\n\t\t</screen>' % (_('az-Explorer') + ' ' + _('Setup'))
    else:
        skin = '\n\t\t\t<screen position="100,100" size="950,410" title="%s" >\n\t\t\t<widget name="config" position="0,0" size="950,260" scrollbarMode="showOnDemand" />\n\t\t\t<ePixmap alphatest="on" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/AzExplorer/res/yellow.png" position="0,280" size="35,25" zPosition="5" />\n\t\t\t<widget name="cdir" position="45,280" size="540,22" valign="left" halign="top" zPosition="4" font="Regular;18" transparent="1"/> \t\t\n\t\t\t<widget name="cdir2" position="55,302" size="540,22" valign="left" halign="top" zPosition="4" font="Regular;16" transparent="1"/> \n\t\t\t<widget name="key_red" position="0,360" size="140,40" valign="center" halign="center" zPosition="4" font="Regular;18" transparent="1"/> \n\t\t\t<widget name="key_green" position="140,360" size="140,40" valign="center" halign="center" zPosition="4" font="Regular;18" transparent="1"/> \n\t\t\t<widget name="key_blue" position="750,360" size="140,40" valign="center" halign="center" zPosition="4" font="Regular;18" transparent="1"/> \n\t\t\t<ePixmap name="red"    position="0,360"   zPosition="2" size="140,40" pixmap="skin_default/buttons/red.png" transparent="1" alphatest="on" />\n\t\t\t<ePixmap name="green"  position="140,360" zPosition="2" size="140,40" pixmap="skin_default/buttons/green.png" transparent="1" alphatest="on" />\n\t\t\t<ePixmap name="blue"  position="750,360" zPosition="2" size="140,40" pixmap="skin_default/buttons/blue.png" transparent="1" alphatest="on" />\n\t\t\t<widget name="barrapix_arr" position="0,0" zPosition="19" size="20,20" alphatest="blend" transparent="1" />\n\t\t\t<widget name="barrapix_abj" position="0,0" zPosition="19" size="20,20" alphatest="blend" transparent="1" />\t\t\t\n\t\t</screen>' % (_('az-Explorer') + ' ' + _('Setup'))

    def __init__(self, session, curdir = '/'):
        self.session = session
        Screen.__init__(self, session)
        self.currentDir = '/'
        if curdir is not None:
            try:
                if pathExists(curdir):
                    self.currentDir = curdir
            except:
                pass

        self.list = []
        self.list.append(getConfigListEntry(_('Show Bookmarks on startup'), config.plugins.azExplorer.showbookmarks, None, None))
        self.list.append(getConfigListEntry(_('Start directory (only if last path is disabled)'), config.plugins.azExplorer.startDir, None, self.openLocationBox))
        self.list.append(getConfigListEntry(_('Start explorer in last path'), config.plugins.azExplorer.remenberpath, None, None))
        self.list.append(getConfigListEntry(_('Show Explorer in main menu (need restart)'), config.plugins.azExplorer.showinmenu, None, None))
        self.list.append(getConfigListEntry(_('Show confirm windows on exit'), config.plugins.azExplorer.confirmexit, None, None))
        self.list.append(getConfigListEntry(_('Initial file sort by'), config.plugins.azExplorer.orden, None, None))
        ConfigListScreen.__init__(self, self.list)
        self['barrapix_arr'] = Pixmap()
        self['barrapix_abj'] = Pixmap()
        self['cdir'] = Label('')
        self['cdir2'] = Label('')
        self['cdir'].setText(_('Set start directory to current directory') + ':')
        self['cdir2'].setText('-->[' + self.currentDir + ']')
        self['key_red'] = Button(_('Cancel'))
        self['key_green'] = Button(_('Save'))
        self['key_blue'] = Button(_('About'))
        self['setupActions'] = ActionMap(['SetupActions', 'ColorActions'], {'ok': self.keyOK,
         'red': self.cancel,
         'green': self.save,
         'yellow': self.ponstart,
         'blue': self.about,
         'save': self.save,
         'cancel': self.cancel}, -2)
        self.iniciadoS = False
        self.onShow.append(self.iniscroll)

    def iniscroll(self):
        if not self.iniciadoS:
            self.actualizaScrolls()
            self.iniciadoS = True

    def actualizaScrolls(self):
        openspaSB(objectoself=self, nombrelista='config', barra='barrapix', altoitem=25, imagen=True)

    def about(self):
        global textoayuda
        hilfe = textoayuda
        dei = self.session.open(MessageBox, _(hilfe), MessageBox.TYPE_INFO)
        dei.setTitle(_('Info...'))

    def ponstart(self):
        config.plugins.azExplorer.startDir.setValue(self.currentDir)
        lalista = self['config'].list
        self['config'].setList(lalista)

    def dirSelected(self, res):
        if res is not None:
            self.list[self['config'].getCurrentIndex()][1].value = res

    def openLocationBox(self):
        try:
            path = self.list[self['config'].getCurrentIndex()][1].value
            from Screens.LocationBox import LocationBox
            self.session.openWithCallback(self.dirSelected, LocationBox, text=_('Choose directory'), filename='', currDir=path, minFree=0)
        except:
            pass

    def keyOK(self):
        try:
            self.list[self['config'].getCurrentIndex()][3]()
        except:
            pass

    def save(self):
        cambiado = False
        for x in self['config'].list:
            if x[1].isChanged():
                x[1].save()
                if x[2] is not None:
                    cambiado = True

        self.close()

    def cancel(self):
        for x in self['config'].list:
            x[1].cancel()

        self.close()


class chPermisos(ConfigListScreen, Screen):
    if esHD():
        skin = '\n\t\t<screen position="59,68" size="1183,690" title="%s">\n\t\t<widget name="information" position="4,0" size="1153,135" halign="left" valign="center" font="Regular; 18" />\n\t\t<widget name="config" position="30,142" size="477,472" scrollbarMode="showOnDemand" itemHeight="42" />\n\t\t<widget name="information2" position="90,615" size="1093,37" halign="left" valign="center" font="Regular; 18" />\n\t\t<ePixmap alphatest="blend" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/redHD.png" position="780,300" size="52,37" zPosition="5"/>\n\t\t<ePixmap alphatest="blend" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/greenHD.png" position="780,360" size="52,37" zPosition="5"/>\t\n\t\t<ePixmap alphatest="blend" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/yellowHD.png" position="780,450" size="52,37" zPosition="5"/>\n\t\t<ePixmap alphatest="blend" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/blueHD.png" position="780,510" size="52,37" zPosition="5"/>\n\t\t<eLabel font="Regular;18" halign="left" position="847,300" size="510,37" text="%s" transparent="1" valign="center" zPosition="6"/>\n\t\t<eLabel font="Regular;18" halign="left" position="847,360" size="510,37" text="%s" transparent="1" valign="center" zPosition="6"/>\t\n\t\t<eLabel font="Regular;18" halign="left" position="847,450" size="510,37" text="%s" transparent="1" valign="center" zPosition="6"/>\n\t\t<eLabel font="Regular;18" halign="left" position="847,510" size="510,37" text="%s" transparent="1" valign="center" zPosition="6"/>\t\n\t\t</screen>' % (_('Change permissions...'),
         _('Cancel (exit)'),
         _('Save (ok)'),
         _('Permission') + ' 755',
         _('Permission') + ' 644')
    else:
        skin = '\n\t\t<screen position="59,68" size="789,460" title="%s">\n\t\t<widget name="information" position="3,0" size="769,90" halign="left" valign="center" font="Regular; 18" />\n\t\t<widget name="config" position="20,95" size="318,315" scrollbarMode="showOnDemand" />\n\t\t<widget name="information2" position="60,410" size="729,25" halign="left" valign="center" font="Regular; 18" />\n\t\t<ePixmap alphatest="on" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/AzExplorer/res/red.png" position="520,200" size="35,25" zPosition="5"/>\n\t\t<ePixmap alphatest="on" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/AzExplorer/res/green.png" position="520,240" size="35,25" zPosition="5"/>\t\n\t\t<ePixmap alphatest="on" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/AzExplorer/res/yellow.png" position="520,300" size="35,25" zPosition="5"/>\n\t\t<ePixmap alphatest="on" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/AzExplorer/res/blue.png" position="520,340" size="35,25" zPosition="5"/>\n\t\t<eLabel font="Regular;18" halign="left" position="565,200" size="340,25" text="%s" transparent="1" valign="center" zPosition="6"/>\n\t\t<eLabel font="Regular;18" halign="left" position="565,240" size="340,25" text="%s" transparent="1" valign="center" zPosition="6"/>\t\n\t\t<eLabel font="Regular;18" halign="left" position="565,300" size="340,25" text="%s" transparent="1" valign="center" zPosition="6"/>\n\t\t<eLabel font="Regular;18" halign="left" position="565,340" size="340,25" text="%s" transparent="1" valign="center" zPosition="6"/>\t\n\t\t</screen>' % (_('Change permissions...'),
         _('Cancel (exit)'),
         _('Save (ok)'),
         _('Permission') + ' 755',
         _('Permission') + ' 644')

    def __init__(self, session, lainfo, peract):
        Screen.__init__(self, session)
        self.session = session
        self.propNombre = ConfigSelection(choices=[' '], default=' ')
        self.propLectura = ConfigYesNo(default=peract[0] == 'r')
        self.propEscritura = ConfigYesNo(default=peract[1] == 'w')
        self.propEjecucion = ConfigYesNo(default=peract[2] == 'x')
        self.grupNombre = ConfigSelection(choices=[' '], default=' ')
        self.grupLectura = ConfigYesNo(default=peract[4] == 'r')
        self.grupEscritura = ConfigYesNo(default=peract[5] == 'w')
        self.grupEjecucion = ConfigYesNo(default=peract[6] == 'x')
        self.todoNombre = ConfigSelection(choices=[' '], default=' ')
        self.todoLectura = ConfigYesNo(default=peract[8] == 'r')
        self.todoEscritura = ConfigYesNo(default=peract[9] == 'w')
        self.todoEjecucion = ConfigYesNo(default=peract[10] == 'x')
        ConfigListScreen.__init__(self, [getConfigListEntry('--' + _('Owner') + '--------------------------------------------------------------------------', self.propNombre),
         getConfigListEntry(_('    Read'), self.propLectura),
         getConfigListEntry(_('    Write'), self.propEscritura),
         getConfigListEntry(_('    Execution'), self.propEjecucion),
         getConfigListEntry('--' + _('Group') + '--------------------------------------------------------------------------', self.grupNombre),
         getConfigListEntry(_('    Read'), self.grupLectura),
         getConfigListEntry(_('    Write'), self.grupEscritura),
         getConfigListEntry(_('    Execution'), self.grupEjecucion),
         getConfigListEntry('--' + _('Other') + '--------------------------------------------------------------------------', self.todoNombre),
         getConfigListEntry(_('    Read'), self.todoLectura),
         getConfigListEntry(_('    Write'), self.todoEscritura),
         getConfigListEntry(_('    Execution'), self.todoEjecucion)])
        self['information'] = Label('')
        self['information'].setText(_(lainfo))
        self['information2'] = Label('')
        self['actions'] = ActionMap(['SetupActions',
         'WizardActions',
         'ColorActions',
         'MenuActions',
         'DirectionActions'], {'ok': self.save,
         'back': self.exit,
         'save': self.save,
         'green': self.save,
         'red': self.exit,
         'yellow': self.permisos755,
         'blue': self.permisos644}, -1)

    def save(self):
        valorper = 0
        valorcad = ''
        if self.propLectura.value:
            valorper = valorper + 400
            valorcad = valorcad + 'r'
        else:
            valorcad = valorcad + '-'
        if self.propEscritura.value:
            valorper = valorper + 200
            valorcad = valorcad + 'w'
        else:
            valorcad = valorcad + '-'
        if self.propEjecucion.value:
            valorper = valorper + 100
            valorcad = valorcad + 'x'
        else:
            valorcad = valorcad + '-'
        valorcad = valorcad + ' '
        if self.grupLectura.value:
            valorper = valorper + 40
            valorcad = valorcad + 'r'
        else:
            valorcad = valorcad + '-'
        if self.grupEscritura.value:
            valorper = valorper + 20
            valorcad = valorcad + 'w'
        else:
            valorcad = valorcad + '-'
        if self.grupEjecucion.value:
            valorper = valorper + 10
            valorcad = valorcad + 'x'
        else:
            valorcad = valorcad + '-'
        valorcad = valorcad + ' '
        if self.todoLectura.value:
            valorper = valorper + 4
            valorcad = valorcad + 'r'
        else:
            valorcad = valorcad + '-'
        if self.todoEscritura.value:
            valorper = valorper + 2
            valorcad = valorcad + 'w'
        else:
            valorcad = valorcad + '-'
        if self.todoEjecucion.value:
            valorper = valorper + 1
            valorcad = valorcad + 'x'
        else:
            valorcad = valorcad + '-'
        self.close(str(valorper))

    def keyOK(self):
        self.save()

    def exit(self):
        self.close(None)

    def keyLeft(self):
        ConfigListScreen.keyLeft(self)
        self.actualizaPermP()

    def permisos644(self):
        self.propLectura.setValue(True)
        self.propEscritura.setValue(True)
        self.propEjecucion.setValue(False)
        self.grupLectura.setValue(True)
        self.grupEscritura.setValue(False)
        self.grupEjecucion.setValue(False)
        self.todoLectura.setValue(True)
        self.todoEscritura.setValue(False)
        self.todoEjecucion.setValue(False)
        self['config'].setCurrentIndex(0)
        lalista = self['config'].list
        self['config'].setList(lalista)
        self.actualizaPermP()

    def permisos755(self):
        self.propLectura.setValue(True)
        self.propEscritura.setValue(True)
        self.propEjecucion.setValue(True)
        self.grupLectura.setValue(True)
        self.grupEscritura.setValue(False)
        self.grupEjecucion.setValue(True)
        self.todoLectura.setValue(True)
        self.todoEscritura.setValue(False)
        self.todoEjecucion.setValue(True)
        lalista = self['config'].list
        self['config'].setList(lalista)
        self['config'].setCurrentIndex(0)
        self.actualizaPermP()

    def actualizaPermP(self):
        valorper = 0
        valorcad = ''
        if self.propLectura.value:
            valorper = valorper + 400
            valorcad = valorcad + 'r'
        else:
            valorcad = valorcad + '-'
        if self.propEscritura.value:
            valorper = valorper + 200
            valorcad = valorcad + 'w'
        else:
            valorcad = valorcad + '-'
        if self.propEjecucion.value:
            valorper = valorper + 100
            valorcad = valorcad + 'x'
        else:
            valorcad = valorcad + '-'
        valorcad = valorcad + ' '
        if self.grupLectura.value:
            valorper = valorper + 40
            valorcad = valorcad + 'r'
        else:
            valorcad = valorcad + '-'
        if self.grupEscritura.value:
            valorper = valorper + 20
            valorcad = valorcad + 'w'
        else:
            valorcad = valorcad + '-'
        if self.grupEjecucion.value:
            valorper = valorper + 10
            valorcad = valorcad + 'x'
        else:
            valorcad = valorcad + '-'
        valorcad = valorcad + ' '
        if self.todoLectura.value:
            valorper = valorper + 4
            valorcad = valorcad + 'r'
        else:
            valorcad = valorcad + '-'
        if self.todoEscritura.value:
            valorper = valorper + 2
            valorcad = valorcad + 'w'
        else:
            valorcad = valorcad + '-'
        if self.todoEjecucion.value:
            valorper = valorper + 1
            valorcad = valorcad + 'x'
        else:
            valorcad = valorcad + '-'
        self['information2'].setText(_('New value: ') + valorcad + ' (' + str(valorper) + ')')

    def keyRight(self):
        ConfigListScreen.keyRight(self)
        self.actualizaPermP()


class IniciaSelList2(MenuList):

    def __init__(self, list, enableWrapAround = False):
        MenuList.__init__(self, list, enableWrapAround, eListboxPythonMultiContent)
        self.l.setItemHeight(fhd(66))
        self.l.setFont(0, gFont('Regular', 23))
        self.l.setFont(1, gFont('Regular', 17))


protegidos = 2
haylast = False
haystart = False

def devicono(quelugar, quenombre):
    global haylast
    global haystart
    global protegidos
    ret = ''
    if '[' + _('Last path') + ']' in quenombre and not haylast:
        haylast = True
        ret = ret + 'catlast-fs8.png'
        protegidos = protegidos + 1
    elif '[' + _('Start directory') + ']' in quenombre and not haystart:
        haystart = True
        protegidos = protegidos + 1
        ret = ret + 'cathome-fs8.png'
    elif quelugar[:-1] == '/':
        ret = ret + 'catroot-fs8.png'
    elif quelugar[0:10] == '/hdd/movie' or quelugar[0:16] == '/media/hdd/movie':
        ret = ret + 'catfoldermovie-fs8.png'
    elif quelugar[0:12] == '/hdd/picture' or quelugar[0:18] == '/media/hdd/picture':
        ret = ret + 'catphotos-fs8.png'
    elif quelugar[0:10] == '/hdd/music' or quelugar[0:16] == '/media/hdd/music':
        ret = ret + 'catfoldermusic-fs8.png'
    elif quelugar[:-1] == '/hdd/' or quelugar[:-1] == '/media/hdd/' or quelugar[:-1] == '/media/hdd' or quelugar[:-1] == '/hdd':
        ret = ret + 'catdisk-fs8.png'
    elif quenombre[0:1] == '<':
        ret = ret + 'catdisks-fs8.png'
    elif quelugar[0:4] == '/hdd' or quelugar[0:10] == '/media/hdd':
        ret = ret + 'catfolderdisk-fs8.png'
    elif quelugar[:-1] == '/autofs/sda1' or quelugar[:-1] == '/autofs/sdb1' or quelugar[:-1] == '/autofs/sda1/' or quelugar[:-1] == '/autofs/sdb1/' or quelugar[:-1] == '/autofs/sda2' or quelugar[:-1] == '/autofs/sdb2' or quelugar[:-1] == '/autofs/sda2/' or quelugar[:-1] == '/autofs/sdb2/':
        ret = ret + 'catusb-fs8.png'
    elif quelugar[0:11] == '/autofs/sda' or quelugar[0:11] == '/autofs/sdb':
        ret = ret + 'catfolderusb-fs8.png'
    else:
        ret = ret + 'catfolder-fs8.png'
    return ret


def IniciaSelListEntry2(nombre, lugar):
    nuevonombre = '' + ''.join(nombre.split('->')[:-1]) + ''
    if len(nuevonombre) <= 0:
        nuevonombre = nombre
    if len(nuevonombre) <= 0:
        nuevonombre = 'NA'
    res = [lugar]
    if nuevonombre[0] == '[':
        nuevonombre = nuevonombre.replace('[', '').replace(']', '')
    nuevolugar = lugar
    if nuevolugar == '$$&$$':
        nuevolugar = ''
    if nuevolugar == '/ ':
        nuevolugar = _('root folder')
    res.append(MultiContentEntryText(pos=(fhd(75), fhd(4, 2)), size=(fhd(700), fhd(32)), font=0, text=nuevonombre))
    res.append(MultiContentEntryText(pos=(fhd(85), fhd(32)), size=(fhd(700), fhd(50)), font=1, text=nuevolugar))
    png = '/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/AzExplorer/res/'
    png = png + devicono(lugar, nombre)
    if fileExists(png):
        fpng = LoadPixmap(png)
    else:
        png = '/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/AzExplorer/res/catfolder-fs8.png'
        fpng = LoadPixmap(png)
    res.append(MultiContentEntryPixmapAlphaBlend(pos=(1, 1), size=(fhd(63), fhd(64)), png=fpng, flags=BT_SCALE | BT_KEEP_ASPECT_RATIO))
    return res


class azFavoritos(Screen):
    if esHD():
        skin = '\n\t\t<screen position="center,center" size="1050,768" title="%s">\n\t\t<widget name="img_red" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/redHD.png" position="0,723" size="60,37" transparent="1" alphatest="blend" />\n\t\t<widget name="img_green" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/greenHD.png" position="240,723" size="60,37" transparent="1" alphatest="blend" />\n\t\t<widget name="img_yellow" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/yellowHD.png" position="600,723" size="60,37" transparent="1" alphatest="blend" />\n\t\t<widget name="img_blue" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/blueHD.png" position="810,723" size="60,37" transparent="1" alphatest="blend" />\n\t\t<widget name="key_red" position="60,723" zPosition="1" size="210,45" font="Regular;16" valign="center" halign="left" backgroundColor="#1f771f" transparent="1" />\n\t\t<widget name="key_green" position="300,723" zPosition="1" size="210,45" font="Regular;16" valign="center" halign="left" backgroundColor="#1f771f" transparent="1" />\n\t\t<widget name="key_yellow" position="660,723" zPosition="1" size="210,45" font="Regular;16" valign="center" halign="left" backgroundColor="#1f771f" transparent="1" />\n\t\t<widget name="key_blue" position="870,723" zPosition="1" size="210,45" font="Regular;16" valign="center" halign="left" backgroundColor="#1f771f" transparent="1" />\n\t\t<widget name="list" position="0,0" size="1050,693" scrollbarMode="showOnDemand" zPosition="10" transparent="1" />\n\t\t<widget name="linea" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/AzExplorer/res/lineaHD-fs8.png" position="0,-694" size="1012,694" alphatest="blend" zPosition="12" backgroundColor="#33777777" transparent="0" />\n\t\t<ePixmap name="new ePixmap" position="0,0" size="1050,693" zPosition="1" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/AzExplorer/res/hdfondof-fs8.png" alphatest="blend" />\n\t\t<widget name="barrapix_arr" position="0,0" zPosition="19" size="30,30" alphatest="blend" transparent="1" />\n\t\t<widget name="barrapix_abj" position="0,0" zPosition="19" size="30,30" alphatest="blend" transparent="1" />\n\t\t</screen>' % (_('az-Explorer') + ' :: ' + _('Bookmarks'))
    else:
        skin = '\n\t\t<screen position="center,center" size="700,512" title="%s">\n\t\t<widget name="img_red" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/AzExplorer/res/red.png" position="0,482" size="40,25" transparent="1" alphatest="on" />\n\t\t<widget name="img_green" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/AzExplorer/res/green.png" position="160,482" size="40,25" transparent="1" alphatest="on" />\n\t\t<widget name="img_yellow" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/AzExplorer/res/yellow.png" position="400,482" size="40,25" transparent="1" alphatest="on" />\n\t\t<widget name="img_blue" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/AzExplorer/res/blue.png" position="540,482" size="40,25" transparent="1" alphatest="on" />\n\t\t<widget name="key_red" position="40,482" zPosition="1" size="140,30" font="Regular;16" valign="center" halign="left" backgroundColor="#1f771f" transparent="1" />\n\t\t<widget name="key_green" position="200,482" zPosition="1" size="140,30" font="Regular;16" valign="center" halign="left" backgroundColor="#1f771f" transparent="1" />\n\t\t<widget name="key_yellow" position="440,482" zPosition="1" size="140,30" font="Regular;16" valign="center" halign="left" backgroundColor="#1f771f" transparent="1" />\n\t\t<widget name="key_blue" position="580,482" zPosition="1" size="140,30" font="Regular;16" valign="center" halign="left" backgroundColor="#1f771f" transparent="1" />\n\t\t<widget name="list" position="0,0" size="700,462" scrollbarMode="showOnDemand" zPosition="10" transparent="1" />\n\t\t<widget name="linea" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/AzExplorer/res/linea-fs8.png" position="0,-463" size="675,463" alphatest="blend" zPosition="12" backgroundColor="#33777777" transparent="0" />\n\t\t<ePixmap name="new ePixmap" position="0,0" size="700,462" zPosition="1" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/AzExplorer/res/fondof-fs8.png" alphatest="blend" />\n\t\t<widget name="barrapix_arr" position="0,0" zPosition="19" size="20,20" alphatest="blend" transparent="1" />\n\t\t<widget name="barrapix_abj" position="0,0" zPosition="19" size="20,20" alphatest="blend" transparent="1" />\n\t\t</screen>' % (_('az-Explorer') + ' :: ' + _('Bookmarks'))

    def __init__(self, session, list, curpat = '/'):
        Screen.__init__(self, session)
        self.lista = list
        self.curpat = curpat
        self['list'] = IniciaSelList2([])
        self['key_red'] = Label(_('Delete'))
        self['linea'] = MovingPixmap()
        if self.curpat == None:
            self.curpat = 'None'
        if self.curpat == 'None':
            self['key_green'] = Label(_(' '))
        else:
            self['key_green'] = Label(_('Add current'))
        self.warning = False
        self['key_yellow'] = Label(_('Up'))
        self['key_blue'] = Label(_('Down'))
        self['img_red'] = Pixmap()
        self['img_green'] = Pixmap()
        self['img_yellow'] = Pixmap()
        self['img_blue'] = Pixmap()
        self.iniciadoS = False
        self['barrapix_arr'] = Pixmap()
        self['barrapix_abj'] = Pixmap()
        self.cambiado = False
        self['actions'] = ActionMap(['OkCancelActions', 'ColorActions', 'DirectionActions'], {'red': self.borrar,
         'cancel': self.cerrar,
         'green': self.anadir,
         'yellow': self.sube,
         'blue': self.baja,
         'ok': self.volver}, prio=-1)
        self.onLayoutFinish.append(self.buildList3)
        self.onShow.append(self.mostrar)

    def mostrar(self):
        posy = 66 * protegidos - 463 + 1
        self['linea'].moveTo(0, posy, 1)
        self['linea'].startMoving()
        if not self.iniciadoS:
            self.actualizaScrolls()
            self.iniciadoS = True

    def actualizaScrolls(self):
        openspaSB(objectoself=self, nombrelista='list', barra='barrapix', altoitem=66, imagen=True)

    def buildList3(self):
        global haylast
        global haystart
        global protegidos
        haystart = False
        haylast = False
        protegidos = 2
        nlista = []
        for iji in self.lista:
            nlista.append(IniciaSelListEntry2(iji[0], iji[1]))

        self['list'].setList(nlista)
        if self.curpat == 'None':
            self['img_green'].hide()
        self.muevesel()
        self['list'].onSelectionChanged.append(self.muevesel)

    def muevesel(self):
        idx = self['list'].getSelectionIndex()
        if idx >= protegidos + 1:
            self['key_yellow'].show()
            self['img_yellow'].show()
        else:
            self['key_yellow'].hide()
            self['img_yellow'].hide()
        if idx < len(self['list'].list) - 1 and idx >= protegidos:
            self['key_blue'].show()
            self['img_blue'].show()
        else:
            self['key_blue'].hide()
            self['img_blue'].hide()
        if idx >= protegidos:
            self['key_red'].show()
            self['img_red'].show()
        else:
            self['key_red'].hide()
            self['img_red'].hide()
        if idx <= 6:
            self['linea'].show()
        else:
            self['linea'].hide()

    def muevelin(self):
        idx = self['list'].getSelectionIndex()

    def key_left(self):
        self['list'].pageUp()
        self.muevelin()

    def key_right(self):
        self['list'].pageDown()
        self.muevelin()

    def key_up(self):
        self['list'].up()
        self.muevelin()

    def key_down(self):
        self['list'].down()
        self.muevelin()

    def sube(self):
        nuevalista = []
        nuevalista2 = []
        conta = 0
        idx = self['list'].getSelectionIndex()
        if idx >= protegidos + 1:
            mover = self['list'].list[idx]
            moverlista = self.lista[idx]
            for x in self['list'].list:
                if conta == idx - 1:
                    nuevalista.append(mover)
                    nuevalista2.append(moverlista)
                if not conta == idx:
                    nuevalista.append(x)
                    nuevalista2.append(self.lista[conta])
                conta = conta + 1

            self.lista = nuevalista2
            self['list'].setList(nuevalista)
            self['list'].moveToIndex(idx - 1)
            self.cambiado = True
        elif not self.warning:
            self.warning = True
            self.session.open(MessageBox, _('First elements protected, unable to move'), MessageBox.TYPE_INFO, timeout=5)

    def baja(self):
        nuevalista = []
        nuevalista2 = []
        conta = 0
        idx = self['list'].getSelectionIndex()
        if idx < len(self['list'].list) - 1 and idx >= protegidos:
            mover = self['list'].list[idx]
            moverlista = self.lista[idx]
            for x in self['list'].list:
                if not conta == idx:
                    nuevalista.append(x)
                    nuevalista2.append(self.lista[conta])
                if conta == idx + 1:
                    nuevalista2.append(moverlista)
                    nuevalista.append(mover)
                conta = conta + 1

            self.lista = nuevalista2
            self['list'].setList(nuevalista)
            self['list'].moveToIndex(idx + 1)
            self.cambiado = True
        elif idx < protegidos and not self.warning:
            self.warning = True
            self.session.open(MessageBox, _('First elements protected, unable to move'), MessageBox.TYPE_INFO, timeout=5)

    def anadir(self):
        if not self.curpat == 'None':
            yahay = False
            idx = 0
            lalista = self['list'].list
            for iji in self.lista:
                if self.curpat.strip() == iji[1][:-1].strip():
                    yahay = True
                    break
                idx = idx + 1

            if not yahay:
                RENfilename = self.curpat.split('/')[-2]
                self.session.openWithCallback(self.anadeBook, spzVirtualKeyboard, titulo=_('Add directory to Bookmarks') + ': [' + self.curpat + ']. ' + _('Set name') + ':', texto=RENfilename, caracteres='[FILE]')
            else:
                self['list'].moveToIndex(idx)

    def anadeBook(self, nombre):
        if nombre is not None:
            if not nombre == '':
                lista = self['list'].list
                lista.append(IniciaSelListEntry2(nombre, self.curpat + '\n'))
                self.lista.append((nombre, self.curpat + '\n'))
                self['list'].setList(lista)
                self['list'].moveToIndex(len(lista) - 1)
                self.actualizaScrolls()
                self.cambiado = True

    def borrar(self):
        lista = self['list'].list
        length = len(lista)
        if length > 0:
            idx = self['list'].getSelectionIndex()
            if idx >= protegidos:
                dei = self.session.openWithCallback(self.callbackborrar, MessageBox, _('Delete current bookmark from list?') + '\n' + lista[idx][0], MessageBox.TYPE_YESNO)
                dei.setTitle(_('az-Explorer...'))
            else:
                self.session.open(MessageBox, _('Protected element, unable to delete'), MessageBox.TYPE_INFO, timeout=5)

    def callbackborrar(self, answer):
        if answer is True:
            lista = self['list'].list
            idx = self['list'].getSelectionIndex()
            self.cambiado = True
            del lista[idx]
            del self.lista[idx]
            self['list'].setList(lista)
            self.actualizaScrolls()

    def cerrar(self):
        if self.cambiado:
            listaret = self.lista
        else:
            listaret = None
        self.close([('None', listaret)])

    def volver(self):
        lalista = self['list'].list
        idx = self['list'].getSelectionIndex()
        if self.cambiado:
            listaret = self.lista
        else:
            listaret = None
        ruta = str(lalista[idx][0])
        if ruta == '':
            ruta = '$$&$$'
        if ruta == _('root folder'):
            ruta = '/ '
        listaruta = [(ruta, listaret)]
        self.close(listaruta)


class azExplorerII(Screen):
    if esHD():
        skin = '\n\t\t<screen position="center,80" size="1770,900" title="" name="azexplorer">\n\t\t\t\t<widget name="filelist" position="127,61" scrollbarMode="showOnDemand" size="1635,702" zPosition="4" transparent="1" itemHeight="42" />\n\t\t\t\t<ePixmap alphatest="blend" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/redHD.png" position="7,856" size="60,37" zPosition="5" />\n\t\t\t\t<ePixmap alphatest="blend" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/greenHD.png" position="243,856" size="60,37" zPosition="5" />\n\t\t\t\t<ePixmap alphatest="blend" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/yellowHD.png" position="508,856" size="60,37" zPosition="5" />\n\t\t\t\t<ePixmap alphatest="blend" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/blueHD.png" position="804,856" size="60,37" zPosition="5" />\n\t\t\t\t<ePixmap alphatest="blend" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/menuHD.png" position="1062,856" size="60,37" zPosition="5" />\n\t\t\t\t<ePixmap alphatest="blend" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/infoHD.png" position="1300,856" size="60,37" zPosition="5" />\n\t\t\t\t<ePixmap alphatest="blend" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/1HD.png" position="1474,856" size="69,37" zPosition="5" />\n\t\t\t\t<eLabel font="Regular; 16" halign="left" position="66,858" size="163,37" text="Delete" transparent="1" valign="center" zPosition="6" />\n\t\t\t\t<eLabel font="Regular; 16" halign="left" position="301,858" size="193,37" text="Rename" transparent="1" valign="center" zPosition="6" />\n\t\t\t\t<eLabel font="Regular; 16" halign="left" position="567,858" size="220,37" text="%s" transparent="1" valign="center" zPosition="6" />\n\t\t\t\t<eLabel font="Regular; 16" halign="left" position="862,858" size="183,37" text="%s" transparent="1" valign="center" zPosition="6" />\n\t\t\t\t<eLabel font="Regular; 16" halign="left" position="1122,858" size="159,37" text="%s" transparent="1" valign="center" zPosition="6" />\n\t\t\t\t<eLabel font="Regular; 16" halign="left" position="1360,858" size="97,37" text="Info" transparent="1" valign="center" zPosition="6" />\n\t\t\t\t<eLabel font="Regular; 16" halign="left" position="1543,858" size="217,37" text="%s" transparent="1" valign="center" zPosition="6" />\n\t\t\t\t<widget name="status" position="127,771" size="636,45" halign="left" valign="center" font="Regular; 16" transparent="1" />\n\t\t\t\t<ePixmap name="new ePixmap" position="127,61" size="1635,702" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/AzExplorer/res/hdfondo.png" alphatest="blend" />\n\t\t\t\t<widget name="accion" position="507,771" size="1255,84" halign="right" valign="top" font="Regular; 15" transparent="1" zPosition="1" foregroundColor="#00ff771c" />\n\t\t\t\t<eLabel name="cabnom" font="Regular; 16" halign="left" position="207,22" size="159,36" text="%s" transparent="1" valign="center" zPosition="16" />\n\t\t\t\t<eLabel name="cabtam" font="Regular; 16" halign="left" position="1084,22" size="159,36" text="%s" transparent="1" valign="center" zPosition="16" />\n\t\t\t\t<eLabel name="cabfec" font="Regular; 16" halign="left" position="1249,22" size="159,36" text="%s" transparent="1" valign="center" zPosition="16" />\t\n\t\t\t\t<eLabel name="cabper" font="Regular; 16" halign="left" position="1515,22" size="159,36" text="%s" transparent="1" valign="center" zPosition="16" />\t\n\t\t\t\t<widget name="img_az" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/AzExplorer/res/hdaz-fs8.png" position="25,880" size="34,30" transparent="1" alphatest="blend" zPosition="17" />\n\t\t\t\t<ePixmap name="marcocab" position="127,60" size="1635,1" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/AzExplorer/res/hdmarco-fs8.png" alphatest="blend" zPosition="15" />\n\t\t\t\t<ePixmap name="new ePixmap" position="0,0" size="130,411" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/AzExplorer/res/hdiconofs8.png" alphatest="blend" />\n\t\t\t\t<ePixmap name="marcopie" position="127,766" size="1635,1" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/AzExplorer/res/hdmarco-fs8.png" alphatest="blend" zPosition="15" />\n\t\t\t\t<widget name="barrapix_arr" position="0,0" zPosition="19" size="30,30" alphatest="blend" transparent="1" />\n\t\t\t\t<widget name="barrapix_abj" position="0,0" zPosition="19" size="30,30" alphatest="blend" transparent="1" />\t\t\t\t\n\t\t</screen>' % (_('Move/Copy'),
         _('Bookmarks'),
         _('Options'),
         _('Change permissions'),
         _('Name'),
         _('Size'),
         _('Date'),
         _('Permission'))
    else:
        skin = '\n\t\t<screen position="center,80" size="1180,600" title="" name="azexplorer">\n\t\t\t\t<widget name="filelist" position="85,41" scrollbarMode="showOnDemand" size="1090,468" zPosition="4" transparent="1" />\n\t\t\t\t<ePixmap alphatest="on" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/AzExplorer/res/red.png" position="5,572" size="40,25" zPosition="5" />\n\t\t\t\t<ePixmap alphatest="on" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/AzExplorer/res/green.png" position="162,572" size="40,25" zPosition="5" />\n\t\t\t\t<ePixmap alphatest="on" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/AzExplorer/res/yellow.png" position="339,573" size="40,25" zPosition="5" />\n\t\t\t\t<ePixmap alphatest="on" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/AzExplorer/res/blue.png" position="536,572" size="40,25" zPosition="5" />\n\t\t\t\t<ePixmap alphatest="on" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/AzExplorer/res/menu.png" position="708,572" size="40,25" zPosition="5" />\n\t\t\t\t<ePixmap alphatest="on" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/AzExplorer/res/info.png" position="867,572" size="40,25" zPosition="5" />\n\t\t\t\t<ePixmap alphatest="on" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/AzExplorer/res/k1.png" position="983,572" size="46,25" zPosition="5" />\n\t\t\t\t<eLabel font="Regular; 16" halign="left" position="44,572" size="109,25" text="Delete" transparent="1" valign="center" zPosition="6" />\n\t\t\t\t<eLabel font="Regular; 16" halign="left" position="201,572" size="129,25" text="Rename" transparent="1" valign="center" zPosition="6" />\n\t\t\t\t<eLabel font="Regular; 16" halign="left" position="378,572" size="147,25" text="%s" transparent="1" valign="center" zPosition="6" />\n\t\t\t\t<eLabel font="Regular; 16" halign="left" position="575,572" size="122,25" text="%s" transparent="1" valign="center" zPosition="6" />\n\t\t\t\t<eLabel font="Regular; 16" halign="left" position="748,572" size="106,25" text="%s" transparent="1" valign="center" zPosition="6" />\n\t\t\t\t<eLabel font="Regular; 16" halign="left" position="907,572" size="65,25" text="Info" transparent="1" valign="center" zPosition="6" />\n\t\t\t\t<eLabel font="Regular; 16" halign="left" position="1029,572" size="145,25" text="%s" transparent="1" valign="center" zPosition="6" />\n\t\t\t\t<widget name="status" position="85,514" size="424,30" halign="left" valign="center" font="Regular; 16" transparent="1" />\n\t\t\t\t<ePixmap name="new ePixmap" position="85,41" size="1090,468" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/AzExplorer/res/fondo.png" alphatest="blend" />\n\t\t\t\t<widget name="accion" position="338,514" size="837,56" halign="right" valign="top" font="Regular; 15" transparent="1" zPosition="1" foregroundColor="#00ff771c" />\n\t\t\t\t<eLabel name="cabnom" font="Regular; 16" halign="left" position="138,15" size="106,24" text="%s" transparent="1" valign="center" zPosition="16" />\n\t\t\t\t<eLabel name="cabtam" font="Regular; 16" halign="left" position="723,15" size="106,24" text="%s" transparent="1" valign="center" zPosition="16" />\n\t\t\t\t<eLabel name="cabfec" font="Regular; 16" halign="left" position="833,15" size="106,24" text="%s" transparent="1" valign="center" zPosition="16" />\t\n\t\t\t\t<eLabel name="cabper" font="Regular; 16" halign="left" position="1010,15" size="106,24" text="%s" transparent="1" valign="center" zPosition="16" />\t\n\n\t\t\t\t<widget name="img_az" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/AzExplorer/res/az-fs8.png" position="17,587" size="23,20" transparent="1" alphatest="blend" zPosition="17" />\n\t\t\t\t<ePixmap name="marcocab" position="85, 40" size="1090,1" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/AzExplorer/res/marco-fs8.png" alphatest="blend" zPosition="15" />\n\t\t\t\t\n\t\t\t\t<ePixmap name="new ePixmap" position="0, 0" size="87,274" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/AzExplorer/res/iconofs8.png" alphatest="blend" />\n\t\t\t\t<ePixmap name="marcopie" position="85, 511" size="1090,1" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/AzExplorer/res/marco-fs8.png" alphatest="blend" zPosition="15" />\n\t\t\t\t<widget name="barrapix_arr" position="0,0" zPosition="19" size="20,20" alphatest="blend" transparent="1" />\n\t\t\t\t<widget name="barrapix_abj" position="0,0" zPosition="19" size="20,20" alphatest="blend" transparent="1" />\t\t\t\t\n\t\t</screen>' % (_('Move/Copy'),
         _('Bookmarks'),
         _('Options'),
         _('Change permissions'),
         _('Name'),
         _('Size'),
         _('Date'),
         _('Permission'))

    def __init__(self, session, rutainicial = None, args = None):
        self.skin = azExplorerII.skin
        Screen.__init__(self, session)
        self.sesion = session
        self.altservice = self.session.nav.getCurrentlyPlayingServiceOrGroup()
        self.MyBox = HardwareInfo().get_device_name()
        self.commando = ['ls']
        self.selectedDir = '/tmp/'
        self.booklines = []
        self.booklines2 = []
        self.iniciado = False
        self.iniciado2 = False
        self['status'] = Label('')
        self['accion'] = Label('')
        self['img_az'] = MovingPixmap()
        self.uinfo = ''
        self.temp = ''
        self.MediaPattern = '^.*\\.(ts|m2ts|mp3|wav|ogg|jpg|jpeg|jpe|png|bmp|mpg|mpeg|mkv|mp4|mov|divx|avi|mp2|m4a|flac|ifo|vob|iso|sh|flv)'
        self.rutainicial = rutainicial
        self.iniciadoS = False
        self['barrapix_arr'] = Pixmap()
        self['barrapix_abj'] = Pixmap()
        self.TimerBK = eTimer()
        self.TimerBK.callback.append(self.procesaBK)
        self.TimerBK.startLongTimer(3)
        if config.plugins.azExplorer.MediaFilter.value == 'off':
            self.MediaFilter = False
            self['filelist'] = myFileList(None, showDirectories=True, showFiles=True, matchingPattern=None, useServiceRef=False)
        else:
            self.MediaFilter = True
            self['filelist'] = myFileList(None, showDirectories=True, showFiles=True, matchingPattern=self.MediaPattern, useServiceRef=False)
        self['TEMPfl'] = FileList('/', matchingPattern='(?i)^.*\\.(jpeg|jpg|jpe|png|bmp)')
        self['actions'] = ActionMap(['WizardActions',
         'DirectionActions',
         'ColorActions',
         'NumberActions',
         'MenuActions',
         'EPGSelectActions',
         'InfobarActions',
         'InfobarSeekActions',
         'InfobarCueSheetActions'], {'ok': self.ok,
         'back': self.salir,
         'green': self.ExecRename,
         'red': self.ExecDelete,
         'blue': self.goToBookmark,
         'yellow': self.go2CPmaniger,
         'menu': self.explContextMenu,
         'info': self.Info,
         'left': self.left,
         'right': self.right,
         'up': self.up,
         'down': self.down,
         'nextBouquet': self.sort1,
         'prevBouquet': self.sort2,
         'showMovies': self.CloseAndPlay,
         'jumpPreviousMark': self.atras,
         'seekBack': self.atras,
         '1': self.cambiaPer}, -1)
        self.onLayoutFinish.append(self.byLayoutEnd)
        self.onShow.append(self.mostrar)
        self.fechacopia = ''
        self.origen = None
        self.destino = None

    def atras(self):
        try:
            actual = self['filelist'].getCurrentDirectory()
            absolute = 'NonePath'
            if pathExists(actual):
                absolute = '/'.join(actual.split('/')[:-2]) + '/'
            if pathExists(absolute):
                self['filelist'].changeDir(absolute)
                self.actualizaScrolls()
                self.updateLocationInfo()
        except:
            pass

    def ok(self):
        global DVDPlayerAviable
        if self['filelist'].canDescent():
            self['filelist'].descent()
            self.actualizaScrolls()
            self.updateLocationInfo()
        else:
            filename = self['filelist'].getCurrentDirectory() + self['filelist'].getFilename()
            testFileName = self['filelist'].getFilename()
            testFileName = testFileName.lower()
            if filename != None:
                if testFileName.endswith('.ts'):
                    fileRef = eServiceReference('1:0:0:0:0:0:0:0:0:0:' + filename)
                    self.session.open(MoviePlayer, fileRef)
                elif testFileName.endswith('.mpg') or testFileName.endswith('.mpeg') or testFileName.endswith('.mkv') or testFileName.endswith('.m2ts') or testFileName.endswith('.vob'):
                    fileRef = eServiceReference('4097:0:0:0:0:0:0:0:0:0:' + filename)
                    self.session.open(MoviePlayer, fileRef)
                elif testFileName.endswith('.avi') or testFileName.endswith('.mp4') or testFileName.endswith('.divx') or testFileName.endswith('.mov') or testFileName.endswith('.flv'):
                    if not self.MyBox == 'dm7025':
                        fileRef = eServiceReference('4097:0:0:0:0:0:0:0:0:0:' + filename)
                        self.session.open(MoviePlayer, fileRef)
                elif testFileName.endswith('.mp3') or testFileName.endswith('.wav') or testFileName.endswith('.ogg') or testFileName.endswith('.m4a') or testFileName.endswith('.mp2') or testFileName.endswith('.flac'):
                    if self.MyBox == 'dm7025' and (testFileName.endswith('.m4a') or testFileName.endswith('.mp2') or testFileName.endswith('.flac')):
                        return
                    if MMPavaiable:
                        SongList, SongIndex = self.searchMusic()
                        try:
                            self.session.open(MerlinMusicPlayerScreen, SongList, SongIndex, False, self.altservice, None)
                        except:
                            self.session.open(MessageBox, _('Incompatible MerlinMusicPlayer version!'), MessageBox.TYPE_INFO)

                    else:
                        fileRef = eServiceReference('4097:0:0:0:0:0:0:0:0:0:' + filename)
                        m_dir = self['filelist'].getCurrentDirectory()
                        self.session.open(MusicExplorer, fileRef, m_dir, testFileName)
                elif testFileName.endswith('.jpg') or testFileName.endswith('.jpeg') or testFileName.endswith('.jpe') or testFileName.endswith('.png') or testFileName.endswith('.bmp'):
                    if self['filelist'].getSelectionIndex() != 0:
                        Pdir = self['filelist'].getCurrentDirectory()
                        self.session.open(PictureExplorerII, filename, Pdir)
                elif testFileName.endswith('.mvi'):
                    self.session.nav.stopService()
                    self.session.open(MviExplorer, filename)
                elif testFileName == 'video_ts.ifo':
                    if DVDPlayerAviable:
                        if self['filelist'].getCurrentDirectory().lower().endswith('video_ts/'):
                            self.session.open(DVDPlayer, dvd_filelist=[self['filelist'].getCurrentDirectory()])
                elif testFileName.endswith('.iso'):
                    if DVDPlayerAviable:
                        self.session.open(DVDPlayer, dvd_filelist=[filename])
                elif testFileName.endswith('.tar.gz'):
                    self.commando = ['tar -xzvf ' + filename + ' -C /']
                    askList = [(_('Cancel'), 'NO'), (_('Install this package'), 'YES')]
                    dei = self.session.openWithCallback(self.SysExecution, ChoiceBox, title=_('GZ-package:\\n' + filename), list=askList)
                    dei.setTitle(_('az-Explorer : Install...'))
                elif testFileName.endswith('.tar.bz2'):
                    self.commando = ['tar -xjvf ' + filename + ' -C /']
                    askList = [(_('Cancel'), 'NO'), (_('Install this package'), 'YES')]
                    dei = self.session.openWithCallback(self.SysExecution, ChoiceBox, title=_('BZ2-package:\\n' + filename), list=askList)
                    dei.setTitle(_('az-Explorer : Install...'))
                elif testFileName.endswith('.ipk'):
                    if fileExists('/usr/bin/opkg'):
                        self.commando = ['opkg install ' + filename]
                    else:
                        self.commando = ['ipkg install ' + filename]
                    askList = [(_('Cancel'), 'NO'), (_('Install this package'), 'YES')]
                    dei = self.session.openWithCallback(self.SysExecution, ChoiceBox, title=_('IPKG-package:\\n' + filename), list=askList)
                    dei.setTitle(_('az-Explorer : Install...'))
                elif testFileName.endswith('.pyc') or testFileName.endswith('.pyo'):
                    self.commando = ['/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/AzExplorer/pyc2xml ' + filename]
                    askList = [(_('Cancel'), 'NO'), (_('Disassemble to bytecode...'), 'YES')]
                    dei = self.session.openWithCallback(self.SysExecution, ChoiceBox, title=_('Pyc-Script:\\n' + filename), list=askList)
                    dei.setTitle(_('az-Explorer : Disassemble...'))
                elif testFileName.endswith('.sh'):
                    self.commando = [filename]
                    askList = [(_('View/Edit this shell-script'), 'VIEW'), (_('Start execution'), 'YES'), (_('Cancel'), 'NO')]
                    self.session.openWithCallback(self.SysExecution, ChoiceBox, title=_('Select action for ') + '?\\n' + filename, list=askList)
                elif testFileName.endswith('.txt') or testFileName.endswith('.cfg') or testFileName.endswith('.log') or testFileName.endswith('.xml') or testFileName.endswith('.conf') or testFileName.endswith('.config') or testFileName.endswith('.info'):
                    self.verArchivo(filename)
                else:
                    self.commando = [filename]
                    askList = [(_('View/Edit this file'), 'VIEW'), (_('Run this file'), 'YES'), (_('Cancel'), 'NO')]
                    self.session.openWithCallback(self.SysExecution, ChoiceBox, title=_('Select action for ') + '?\\n' + filename, list=askList)

    def verArchivo(self, filename):
        if os.path.exists(filename):
            xfile = os_stat(filename)
            if xfile.st_size < 61440:
                self.session.open(vEditor, filename)
            else:
                self.avisotamano()

    def avisotamano(self):
        dei = self.session.open(MessageBox, _('You can only view or edit files less than') + ' 60kb (61440 bytes)!', MessageBox.TYPE_WARNING, timeout=15)
        dei.setTitle(_('az-Explorer'))

    def colocaorden(self):
        numeroorden = '1'
        try:
            carpeta = self['filelist'].getCurrentDirectory()
            numeroorden = getOrden()
            posx = 115
            if numeroorden == '3':
                posx = 700
            elif numeroorden == '2':
                posx = 810
        except:
            posx = -100

        self['img_az'].moveTo(posx, 17, 1)
        self['img_az'].startMoving()

    def mostrar(self):
        global salirespera
        salirespera = True
        self.colocaorden()
        if config.plugins.azExplorer.showbookmarks.value and self.rutainicial == None:
            if not self.iniciado:
                self.goToBookmark(inicio='None')
        if not self.iniciadoS:
            self.actualizaScrolls()
            self.iniciadoS = True

    def actualizaScrolls(self):
        openspaSB(objectoself=self, nombrelista='filelist', barra='barrapix', altoitem=26, imagen=True)

    def byLayoutEnd(self):
        self.updateLocationInfo()
        if fileExists('/etc/azBookmarks'):
            try:
                booklist = open('/etc/azBookmarks', 'r')
            except:
                dei = self.session.open(MessageBox, _('Error by reading bookmarks !!!'), MessageBox.TYPE_ERROR)
                dei.setTitle(_('az-Explorer'))

            if booklist is not None:
                for oneline in booklist:
                    self.booklines.append(oneline.split('#')[-1])
                    self.booklines2.append(oneline)

                booklist.close()
        else:
            oneline = _('Hard disk') + '#' + '/hdd/\n'
            self.booklines.append(oneline.split('#')[-1])
            self.booklines2.append(oneline)
            if pathExists('/hdd/movie/'):
                oneline = _('Movies') + '#' + '/hdd/movie/\n'
                self.booklines.append(oneline.split('#')[-1])
                self.booklines2.append(oneline)
            if pathExists('/hdd/music/'):
                oneline = _('Music') + '#' + '/hdd/music/\n'
                self.booklines.append(oneline.split('#')[-1])
                self.booklines2.append(oneline)
            if pathExists('/hdd/picture/'):
                oneline = _('Picture') + '#' + '/hdd/picture/\n'
                self.booklines.append(oneline.split('#')[-1])
                self.booklines2.append(oneline)
            oneline = _('Temp folder') + '#' + '/tmp/\n'
            self.booklines.append(oneline.split('#')[-1])
            self.booklines2.append(oneline)
        if not self.iniciado2:
            self.iniciado2 = True
            StartMeOn = '/'
            if not self.rutainicial == None:
                laruta = self.rutainicial
                if not laruta[len(laruta) - 1:] == '/':
                    laruta = laruta + '/'
                laruta = laruta.replace('//', '/')
                if pathExists(laruta):
                    StartMeOn = laruta
                else:
                    StartMeOn = '/'
            self['filelist'].changeDir(StartMeOn)
            self.updateLocationInfo()

    def infostatusP(self):
        if self['filelist'].numsto > 0:
            lainfo = str(self['filelist'].numsto)
            lainfo = lainfo + ' ' + _('Storage Device(s)') + ''
        else:
            lainfo = str(self['filelist'].numdirs)
            lainfo = lainfo + ' ' + _('Directory') + '(s)'
            lainfo = lainfo + ', ' + str(self['filelist'].numfiles)
            lainfo = lainfo + ' ' + _('File') + '(s)'
        return lainfo

    def updateLocationInfo(self):
        self.colocaorden()
        try:
            if self.MediaFilter:
                self.setTitle(_('[Media files] ') + self['filelist'].getCurrentDirectory())
            else:
                self.setTitle(_('[All files] ') + self['filelist'].getCurrentDirectory())
        except:
            self.setTitle(_('az-Explorer'))

        self['status'].setText(self.infostatusP())
        self['accion'].setText(self.uinfo)
        self.uinfo = ''

    def explContextMenu(self):
        if self.MediaFilter:
            mftext = 'Disable'
        else:
            mftext = 'Enable'
        cadir = self['filelist'].getCurrentDirectory()
        if cadir != None:
            if pathExists(cadir):
                if cadir == '/':
                    nomdir = ' [' + _('root') + ']'
                    nomdirin = ' [' + _('in') + ' ' + _('root') + ']'
                else:
                    nomdir = ' [' + cadir.split('/')[-2] + ']'
                    nomdirin = ' [' + _('in') + ' ' + cadir.split('/')[-2] + ']'
                if cadir + '\n' in self.booklines:
                    BMtext = _('Remove directory from Bookmarks') + nomdir
                    BMstring = 'DELLINK'
                else:
                    BMtext = _('Add directory to Bookmarks') + nomdir
                    BMstring = 'ADDLINK'
                norden = getOrden()
                actorden = ''
                if norden == '1':
                    actorden = '(' + _('Orded by') + ' ' + _('Name') + ')'
                elif norden == '2':
                    actorden = '(' + _('Orded by') + ' ' + _('Date') + ')'
                elif norden == '3':
                    actorden = '(' + _('Orded by') + ' ' + _('Size') + ')'
                contextDirList = [(_('Cancel'), 'NO'),
                 (_('Sort by') + '...' + actorden, 'SORT'),
                 (_(BMtext), BMstring),
                 (_('Create new file') + nomdirin, 'NEWFILE'),
                 (_('Create new directory') + nomdirin, 'NEWDIR'),
                 (_('Create softlink...') + nomdirin, 'SOFTLINK'),
                 (_('Preview all pictures'), 'PLAYDIRPICTURE'),
                 (_(mftext + ' Media-filter'), 'FILTER'),
                 (_('Set start directory') + nomdir, 'SETSTARTDIR'),
                 (_('Help') + '', 'AYUDA'),
                 (_('Setup') + '...', 'HELP')]
                dei = self.session.openWithCallback(self.menuorden, ChoiceBox, title=_('Options') + nomdir + ':', list=contextDirList)
                dei.setTitle(_('az-Explorer'))
            else:
                norden = getOrden()
                actorden = ''
                if norden == '1':
                    actorden = '(' + _('Orded by') + ' ' + _('Name') + ')'
                elif norden == '2':
                    actorden = '(' + _('Orded by') + ' ' + _('Date') + ')'
                elif norden == '3':
                    actorden = '(' + _('Orded by') + ' ' + _('Size') + ')'
                contextFileList = [(_('Cancel'), 'NO'),
                 (_(mftext + ' Media-filter'), 'FILTER'),
                 (_('Sort by') + actorden + '...', 'SORT'),
                 (_('Help') + '', 'AYUDA'),
                 (_('Setup') + '...', 'HELP')]
                dei = self.session.openWithCallback(self.menuorden, ChoiceBox, title=_('Options:'), list=contextFileList)
                dei.setTitle(_('az-Explorer'))
        else:
            contextFileList = [(_('Cancel'), 'NO'), (_(mftext + ' Media-filter'), 'FILTER'), (_('Setup') + '...', 'HELP')]
            dei = self.session.openWithCallback(self.SysExecution, ChoiceBox, title=_('Options:'), list=contextFileList)
            dei.setTitle(_('az-Explorer'))

    def menuorden(self, answer):
        if answer and answer[1] == 'SORT':
            contextFileList = [(_('Cancel'), 'NO'),
             (_('Sort by name'), 'SORTNAME'),
             (_('Sort by date'), 'SORTDATE'),
             (_('Sort by size'), 'SORTSIZE')]
            norden = getOrden()
            actorden = ''
            if norden == '1':
                actorden = '' + _('Name') + ''
            elif norden == '2':
                actorden = '' + _('Date') + ''
            elif norden == '3':
                actorden = '' + _('Size') + ''
            dei = self.session.openWithCallback(self.SysExecution, ChoiceBox, title=_('Sort by') + ' [' + _('Orded by') + ' ' + _(actorden) + ']:', list=contextFileList)
            dei.setTitle(_('az-Explorer'))
        else:
            self.SysExecution(answer)

    def SysExecution(self, answer):
        global PicPlayerAviable
        answer = answer and answer[1]
        if answer == 'YES':
            self.session.open(Console, self.commando[0], cmdlist=[self.commando[0]])
        elif answer == 'VIEW':
            self.verArchivo(self.commando[0])
        elif answer == 'PLAYDIRPICTURE':
            if PicPlayerAviable:
                self['TEMPfl'].changeDir(self['filelist'].getCurrentDirectory())
                self.session.open(Pic_Thumb, self['TEMPfl'].getFileList(), 0, self['filelist'].getCurrentDirectory())
            else:
                dei = self.session.open(MessageBox, _('Picture-Player not avaiable.'), MessageBox.TYPE_ERROR)
                dei.setTitle(_('az-Explorer'))
        elif answer == 'ADDLINK':
            seldestino = self['filelist'].getCurrentDirectory()
            if seldestino != None:
                if pathExists(seldestino):
                    RENfilename = seldestino.split('/')[-2]
                    self.session.openWithCallback(self.anadeBook, spzVirtualKeyboard, titulo=_('Add directory to Bookmarks') + ': [' + seldestino + ']. ' + _('Set name') + ':', texto=RENfilename, caracteres='[FILE]')
        elif answer == 'DELLINK':
            self.booklines2 = []
            self.booklines = []
            if fileExists('/etc/azBookmarks'):
                try:
                    booklist = open('/etc/azBookmarks', 'r')
                except:
                    dei = self.session.open(MessageBox, _('Error by reading bookmarks !!!'), MessageBox.TYPE_ERROR)
                    dei.setTitle(_('az-Explorer'))

                if booklist is not None:
                    seldestino = self['filelist'].getCurrentDirectory()
                    if seldestino != None:
                        if pathExists(seldestino):
                            for oneline in booklist:
                                if not seldestino + '\n' == oneline.split('#')[-1]:
                                    self.booklines.append(oneline.split('#')[-1])
                                    self.booklines2.append(oneline)

                    booklist.close()
                    self.uinfo = _('Deleted from bookmarks') + ': ' + seldestino
                    self.updateLocationInfo()
            try:
                newbooklist = open('/etc/azBookmarks', 'w')
            except:
                dei = self.session.open(MessageBox, _('Error by writing bookmarks !!!'), MessageBox.TYPE_ERROR)
                dei.setTitle(_('az-Explorer'))

            if newbooklist is not None:
                for one_line in self.booklines2:
                    newbooklist.write(one_line)

                newbooklist.close()
        elif answer == 'FILTER':
            if self.MediaFilter:
                self.MediaFilter = False
                config.plugins.azExplorer.MediaFilter.value = 'off'
                config.plugins.azExplorer.MediaFilter.save()
                self['filelist'].matchingPattern = None
                self['filelist'].refresh()
                self.updateLocationInfo()
            else:
                self.MediaFilter = True
                config.plugins.azExplorer.MediaFilter.value = 'on'
                config.plugins.azExplorer.MediaFilter.save()
                self['filelist'].matchingPattern = self.MediaPattern
                self['filelist'].refresh()
                self.updateLocationInfo()
        elif answer == 'NEWFILE':
            self.session.openWithCallback(self.callbackNewFile, spzVirtualKeyboard, titulo=_('Create new file in...') + self['filelist'].getCurrentDirectory() + ':', texto=_('newfile'), caracteres='[FILE]')
        elif answer == 'NEWDIR':
            self.session.openWithCallback(self.callbackNewDir, spzVirtualKeyboard, titulo=_('Create new directory in...') + self['filelist'].getCurrentDirectory() + ':', texto=_('newfolder'), caracteres='[FILE]')
        elif answer == 'SETSTARTDIR':
            newStartDir = self['filelist'].getCurrentDirectory()
            dei = self.session.openWithCallback(self.callbackSetStartDir, MessageBox, _('Do you want to set') + '\n' + newStartDir + '\n' + _('as start directory?'), MessageBox.TYPE_YESNO)
            dei.setTitle(_('az-Explorer...'))
        elif answer == 'SORTNAME':
            list = self.sortName()
        elif answer == 'SORTDATE':
            list = self.sortDate()
        elif answer == 'SORTSIZE':
            list = self.sortSize()
        elif answer == 'HELP':
            self.session.open(ConfiguraAZ, curdir=self['filelist'].getCurrentDirectory())
        elif answer == 'AYUDA':
            hilfe = textoayuda
            dei = self.session.open(MessageBox, _(hilfe), MessageBox.TYPE_INFO)
            dei.setTitle(_('About'))
        elif answer == 'SOFTLINK':
            if not self.MediaFilter:
                self.session.openWithCallback(self.callbackCPmaniger, SoftLinkScreen, self['filelist'].getCurrentDirectory())

    def anadeBook(self, answer):
        if answer is not None:
            try:
                newbooklist = open('/etc/azBookmarks', 'w')
            except:
                dei = self.session.open(MessageBox, _('Error by writing bookmarks !!!'), MessageBox.TYPE_ERROR)
                dei.setTitle(_('az-Explorer'))

            if newbooklist is not None:
                self.booklines2.append(answer + '#' + self['filelist'].getCurrentDirectory() + '\n')
                self.booklines.append(self['filelist'].getCurrentDirectory() + '\n')
                for one_line in self.booklines2:
                    newbooklist.write(one_line)

                newbooklist.close()
                self.uinfo = _('Add to bookmarks') + ': ' + answer
                self.updateLocationInfo()

    def up(self):
        self['filelist'].up()
        self.updateLocationInfo()

    def down(self):
        self['filelist'].down()
        self.updateLocationInfo()

    def left(self):
        self['filelist'].pageUp()
        self.updateLocationInfo()

    def right(self):
        self['filelist'].pageDown()
        self.updateLocationInfo()

    def oldHumanizer(self, size, mostrarbytes = False):
        if size < 1024:
            humansize = str(size) + ' bytes'
        elif size < 1048576:
            humansize = str(size / 1024) + ' Kb'
            if mostrarbytes:
                humansize = humansize + ' (' + str(size) + ' bytes)'
        else:
            humansize = str(size / 1048576) + ' Mb'
            if mostrarbytes:
                humansize = humansize + ' (' + str(size) + ' bytes)'
        return humansize

    def tamfichero(self, curSelFile = None):
        if not curSelFile:
            return ''
        cret = ''
        try:
            if os.path.exists(curSelFile):
                dir_stats = os.path.getsize(curSelFile)
                cret = str(self.Humanizer(dir_stats, mostrarbytes=False))
        except:
            pass

        return cret

    def Humanizer(self, size, mostrarbytes = False):
        if size < 1024:
            humansize = str(size) + ' bytes'
        elif size < 1048576:
            humansize = '%.2f Kb' % (float(size) / 1024)
            if mostrarbytes:
                humansize = humansize + ' (' + str(size) + ' bytes)'
        elif size < 1073741824:
            humansize = '%.2f Mb' % (float(size) / 1048576)
            if mostrarbytes:
                humansize = humansize + ' (' + str(size) + ' bytes)'
        else:
            humansize = '%.2f Gb' % (float(size) / 1073741824)
            if mostrarbytes:
                humansize = humansize + ' (' + str(size) + ' bytes)'
        return humansize

    def Info(self):
        if self['filelist'].canDescent():
            try:
                if self['filelist'].getSelectionIndex() != 0:
                    curSelDir = self['filelist'].getSelection()[0]
                else:
                    curSelDir = self['filelist'].getCurrentDirectory()
                longi = len(curSelDir) - 1
                y = curSelDir[:longi]
                if os_path.islink(y):
                    dir_stats = os_stat(y)
                    eltipo = '' + _('Simlynk') + ' --> ' + _('Folder')
                    eltipo = eltipo + '\n' + _('Target') + ': ' + readlinkabs(y)
                    dir_infos = _('Name') + ': ' + self['filelist'].getFilename() + '\n'
                    dir_infos = dir_infos + _('Path') + ': ' + self['filelist'].getCurrentDirectory() + '\n'
                    dir_infos = dir_infos + _('Type') + ': ' + eltipo + '\n'
                    dir_infos = dir_infos + _('Last-mod') + ': ' + formateafecha(time_localtime(dir_stats.st_mtime), corta=False) + '\n'
                    dir_infos = dir_infos + _('Permission') + ': ' + devpermisos(dir_stats.st_mode)
                    dei = self.session.open(MessageBox, dir_infos, MessageBox.TYPE_INFO)
                    dei.setTitle(_('Info...'))
                elif os.path.exists(curSelDir):
                    dir_stats = os_stat(curSelDir)
                    if curSelDir == '/':
                        nomsof = _('root')
                    else:
                        nomsof = curSelDir.split('/')[-2]
                    eltipo = _('Folder')
                    dir_infos = _('Name') + ': ' + nomsof + '\n'
                    dir_infos = dir_infos + _('Path') + ': ' + self['filelist'].getCurrentDirectory() + '\n'
                    dir_infos = dir_infos + _('Type') + ': ' + eltipo + '\n'
                    dir_infos = dir_infos + _('Creation date') + ': ' + formateafecha(time_localtime(dir_stats.st_ctime), corta=False) + '\n'
                    dir_infos = dir_infos + _('Last-mod') + ': ' + formateafecha(time_localtime(dir_stats.st_mtime), corta=False) + '\n'
                    dir_infos = dir_infos + _('Permission') + ': ' + devpermisos(dir_stats.st_mode)
                    dei = self.session.open(MessageBox, dir_infos, MessageBox.TYPE_INFO)
                    dei.setTitle(_('Info...'))
                else:
                    dei = self.session.open(MessageBox, _('Azbox: ' + self.MyBox + '\n\n' + ScanSysem_str()), MessageBox.TYPE_INFO)
                    dei.setTitle(_('az-Explorer'))
            except:
                print ''

        else:
            try:
                curSelFile = self['filelist'].getCurrentDirectory() + self['filelist'].getFilename()
                if os_path.islink(curSelFile):
                    eltipo = '' + _('Simlynk') + ' --> ' + _('File')
                    eltipo = eltipo + '\n' + _('Target') + ': ' + readlinkabs(curSelFile)
                    dir_infos = _('Name') + ': ' + self['filelist'].getFilename() + '\n'
                    dir_infos = dir_infos + _('Path') + ': ' + self['filelist'].getCurrentDirectory() + '\n'
                    dir_infos = dir_infos + _('Type') + ': ' + eltipo + '\n'
                    if os.path.exists(curSelFile):
                        dir_stats = os_stat(curSelFile)
                        dir_infos = dir_infos + _('Last-mod') + ': ' + formateafecha(time_localtime(dir_stats.st_mtime), corta=False) + '\n'
                        dir_infos = dir_infos + _('Permission') + ': ' + devpermisos(dir_stats.st_mode)
                    else:
                        dir_infos = dir_infos + '\n' + _('Target not found')
                    dei = self.session.open(MessageBox, dir_infos, MessageBox.TYPE_INFO)
                    dei.setTitle(_('Info...'))
                elif os.path.exists(curSelFile):
                    dir_stats = os_stat(curSelFile)
                    eltipo = _('File')
                    dir_infos = _('Name') + ': ' + self['filelist'].getFilename() + '\n'
                    dir_infos = dir_infos + _('Path') + ': ' + self['filelist'].getCurrentDirectory() + '\n'
                    dir_infos = dir_infos + _('Type') + ': ' + eltipo + '\n'
                    dir_infos = dir_infos + _('Size') + ': ' + str(self.Humanizer(dir_stats.st_size, mostrarbytes=True)) + '\n'
                    dir_infos = dir_infos + _('Creation date') + ': ' + formateafecha(time_localtime(dir_stats.st_ctime), corta=False) + '\n'
                    dir_infos = dir_infos + _('Last-mod') + ': ' + formateafecha(time_localtime(dir_stats.st_mtime), corta=False) + '\n'
                    dir_infos = dir_infos + _('Permission') + ': ' + devpermisos(dir_stats.st_mode)
                    dei = self.session.open(MessageBox, dir_infos, MessageBox.TYPE_INFO)
                    dei.setTitle(_('Info...'))
                    if curSelFile.endswith('.ts'):
                        serviceref = eServiceReference('1:0:0:0:0:0:0:0:0:0:' + curSelFile)
                        serviceHandler = eServiceCenter.getInstance()
                        info = serviceHandler.info(serviceref)
                        evt = info.getEvent(serviceref)
                        if evt:
                            self.session.open(EventViewSimple, evt, ServiceReference(serviceref))
            except:
                print ''

    def setBookmark(self, answer):
        if not answer[0][1] == None:
            try:
                newbooklist = open('/etc/azBookmarks', 'w')
            except:
                dei = self.session.open(MessageBox, _('Error by writing bookmarks !!!'), MessageBox.TYPE_ERROR)
                dei.setTitle(_('az-Explorer'))

            if newbooklist is not None:
                self.booklines2 = []
                self.booklines = []
                conta = 0
                for ele in answer[0][1]:
                    if conta >= protegidos:
                        laruta = ele[1][:-1]
                        elnombre = ele[0]
                        nuevonombre = '' + ''.join(elnombre.split('->')[:-1]) + ''
                        if len(nuevonombre) <= 0:
                            nuevonombre = elnombre
                        if nuevonombre[0] == '[':
                            nuevonombre = nuevonombre.replace('[', '').replace(']', '')
                        self.booklines2.append(str(nuevonombre.strip()) + '#' + str(laruta.strip()) + '\n')
                        self.booklines.append(str(laruta.strip()) + '\n')
                    conta = conta + 1

                for one_line in self.booklines2:
                    newbooklist.write(one_line)

                newbooklist.close()
        if not answer[0][0] == 'None':
            try:
                if answer[0][0][0] == '/':
                    self['filelist'].changeDir(answer[0][0][:-1])
                    self.actualizaScrolls()
                    self.updateLocationInfo()
                if answer[0][0] == '$$&$$':
                    self['filelist'].changeDir(None)
                    self.actualizaScrolls()
                    self.updateLocationInfo()
            except:
                pass

    def goToBookmark(self, inicio = 'si'):
        if not self.iniciado:
            self.iniciado = True
            if not config.plugins.azExplorer.ultimodir.value == '/' and not config.plugins.azExplorer.ultimodir.value == config.plugins.azExplorer.startDir.value:
                valorini = '[' + _('Last path') + '] ->' + config.plugins.azExplorer.ultimodir.value
                bml = [(valorini, config.plugins.azExplorer.ultimodir.value + ' ')]
                bml.append(('<' + _('List of Storage Devices') + '>', '$$&$$'))
                bml.append(('[' + _('root') + '] ->/', '/ '))
            else:
                bml = [('<' + _('List of Storage Devices') + '>', '$$&$$')]
                bml.append(('[' + _('root') + '] ->/', '/ '))
        else:
            bml = [('<' + _('List of Storage Devices') + '>', '$$&$$')]
            bml.append(('[' + _('root') + '] ->/', '/ '))
        if not config.plugins.azExplorer.startDir.value == '/':
            valorini = '[' + _('Start directory') + '] ->' + config.plugins.azExplorer.startDir.value
            bml.append((valorini, config.plugins.azExplorer.startDir.value + ' '))
        for onemark in self.booklines2:
            ervalor = onemark.split('#')[-1]
            ertexto = '[' + ''.join(onemark.split('#')[:-1]) + '] ->' + ervalor
            if ertexto == None:
                ertexto = onemark
            if ertexto == '':
                ertexto = onemark
            if ervalor == None:
                ertexto = onemark
            if ervalor == '':
                ertexto = onemark
            bml.append((_(ertexto), ervalor))

        if inicio == 'si':
            patcor = self['filelist'].getCurrentDirectory()
        else:
            patcor = inicio
        dei = self.session.openWithCallback(self.setBookmark, azFavoritos, list=bml, curpat=patcor)

    def ExecDelete(self):
        if self.MediaFilter:
            dei = self.session.open(MessageBox, _('Turn off the media-filter first.'), MessageBox.TYPE_INFO)
            dei.setTitle(_('az-Explorer...'))
            return
        if not self['filelist'].canDescent():
            DELfilename = self['filelist'].getCurrentDirectory() + self['filelist'].getFilename()
            dei = self.session.openWithCallback(self.callbackExecDelete, MessageBox, _('Do you realy want to DELETE:') + '\n' + DELfilename, MessageBox.TYPE_YESNO, default=False)
            dei.setTitle(_('az-Explorer - DELETE file...'))
        elif self['filelist'].getSelectionIndex() != 0 and self['filelist'].canDescent():
            DELDIR = self['filelist'].getSelection()[0]
            dei = self.session.openWithCallback(self.callbackDelDir, MessageBox, _('Do you realy want to DELETE:') + '\n' + DELDIR + '\n\n' + _('You do it at your own risk!'), MessageBox.TYPE_YESNO, default=False)
            dei.setTitle(_('az-Explorer - DELETE DIRECTORY...'))

    def callbackExecPer(self, answer):
        if answer is True:
            DELfilename = self['filelist'].getCurrentDirectory() + self['filelist'].getFilename()
            order = 'chmod 755 "' + DELfilename + '"'
            try:
                reg = ejecutaOrden(self, order)
                self['filelist'].refresh()
                self.updateLocationInfo()
            except:
                dei = self.session.open(MessageBox, _('%s \nFAILED!' % order), MessageBox.TYPE_ERROR)
                dei.setTitle(_('az-Explorer'))
                self['filelist'].refresh()

    def callbackExecDelete(self, answer):
        if answer is True:
            DELfilename = self['filelist'].getCurrentDirectory() + self['filelist'].getFilename()
            order = 'rm -f "' + DELfilename + '"'
            if ejecutaOrden(self, order):
                self['filelist'].refresh()
                self.uinfo = _('Deleted') + ': ' + DELfilename
                self.updateLocationInfo()

    def callbackDelDir(self, answer):
        if answer is True:
            DELDIR = self['filelist'].getSelection()[0]
            order = 'rm -r "' + DELDIR + '"'
            if ejecutaOrden(self, order):
                self['filelist'].refresh()
                self.uinfo = _('Deleted') + ': ' + DELDIR
                self.updateLocationInfo()

    def ExecRename(self):
        if self.MediaFilter:
            dei = self.session.open(MessageBox, _('Turn off the media-filter first.'), MessageBox.TYPE_INFO)
            dei.setTitle(_('az-Explorer...'))
            return
        if not self['filelist'].canDescent():
            RENfilename = self['filelist'].getFilename()
            self.session.openWithCallback(self.callbackExecRename, spzVirtualKeyboard, titulo=_('Rename file...') + _('old:  ') + RENfilename + ':', texto=RENfilename, caracteres='[FILE]')
        elif self['filelist'].getSelectionIndex() != 0 and self['filelist'].canDescent():
            RENDIR = self['filelist'].getSelection()[0]
            self.session.openWithCallback(self.callbackRenDir, spzVirtualKeyboard, titulo=_('Rename directory...') + _('old:  ') + RENDIR + ':', texto=RENDIR, caracteres='[FILE]')

    def cambiaPer(self):
        if self.MediaFilter:
            dei = self.session.open(MessageBox, _('Turn off the media-filter first.'), MessageBox.TYPE_INFO)
            dei.setTitle(_('az-Explorer...'))
            return
        if not self['filelist'].canDescent():
            RENfilename = self['filelist'].getFilename()
            curSelFile = self['filelist'].getCurrentDirectory() + self['filelist'].getFilename()
            if os.path.exists(curSelFile):
                dir_stats = os_stat(curSelFile)
                dir_infos = devpermisos(dir_stats.st_mode)
                self.session.openWithCallback(self.callbackcambiaPer, chPermisos, lainfo=_('File:  ') + RENfilename + ' ::' + _(' Current permissions: ') + dir_infos, peract=dir_infos)
        elif self['filelist'].getSelectionIndex() != 0 and self['filelist'].canDescent():
            RENDIR = self['filelist'].getSelection()[0]
            if os.path.exists(RENDIR):
                dir_stats = os_stat(RENDIR)
                dir_infos = devpermisos(dir_stats.st_mode)
                self.session.openWithCallback(self.callbackcambiaPer, chPermisos, lainfo=_('Folder:  ') + RENDIR + ' ::' + _(' Current permissions: ') + dir_infos, peract=dir_infos)

    def xcambiaPer(self):
        if self.MediaFilter:
            dei = self.session.open(MessageBox, _('Turn off the media-filter first.'), MessageBox.TYPE_INFO)
            dei.setTitle(_('az-Explorer...'))
            return
        if not self['filelist'].canDescent():
            RENfilename = self['filelist'].getFilename()
            curSelFile = self['filelist'].getCurrentDirectory() + self['filelist'].getFilename()
            if os.path.exists(curSelFile):
                dir_stats = os_stat(curSelFile)
                dir_infos = str(oct(stat.S_IMODE(dir_stats.st_mode)))
                self.session.openWithCallback(self.callbackcambiaPer, vcpInputBox, title=_('File:  ') + ' ::' + RENfilename + _(' Current permissions: ') + dir_infos, windowTitle=_('Change permissions...'), text='755')
                self.Info
        elif self['filelist'].getSelectionIndex() != 0 and self['filelist'].canDescent():
            RENDIR = self['filelist'].getSelection()[0]
            if os.path.exists(RENDIR):
                dir_stats = os_stat(RENDIR)
                dir_infos = str(oct(stat.S_IMODE(dir_stats.st_mode)))
            self.session.openWithCallback(self.callbackcambiaPer, vcpInputBox, title=_('Folder:  ') + RENDIR + ' ::' + _(' Current permissions: ') + dir_infos, windowTitle=_('Change permissions...'), text='666')
            self.Info

    def callbackcambiaPer(self, answer):
        if answer is not None:
            if self['filelist'].getSelectionIndex() != 0 and self['filelist'].canDescent():
                DELfilename = self['filelist'].getSelection()[0]
            else:
                DELfilename = self['filelist'].getCurrentDirectory() + self['filelist'].getFilename()
            order = 'chmod ' + answer + ' "' + DELfilename + '"'
            if ejecutaOrden(self, order):
                self['filelist'].refresh()
                dir_stats = os_stat(DELfilename)
                dir_infos = devpermisos(dir_stats.st_mode)
                self.uinfo = _('Permission changed') + ': ' + DELfilename + ' --> ' + dir_infos
                self.updateLocationInfo()

    def callbackExecRename(self, answer):
        if answer is not None:
            dest = self['filelist'].getCurrentDirectory() + answer
            self.temp = answer
            if fileExists(dest):
                dei = self.session.openWithCallback(self.okcallbackExecRename, MessageBox, _('Target exist:') + '\n' + dest + '\n' + _('Overwrite?'), MessageBox.TYPE_YESNO, default=False)
                dei.setTitle(_('az-Explorer...'))
            else:
                self.okcallbackExecRename(True)

    def okcallbackExecRename(self, answer):
        if answer:
            source = self['filelist'].getCurrentDirectory() + self['filelist'].getFilename()
            dest = self['filelist'].getCurrentDirectory() + self.temp
            try:
                os_rename(source, dest)
                self.uinfo = _('Renamed') + ': ' + source + ' --> ' + dest
                self['filelist'].refresh()
                self.updateLocationInfo()
            except:
                dei = self.session.open(MessageBox, _('Rename: %s \nFAILED!') % self.temp, MessageBox.TYPE_ERROR)
                dei.setTitle(_('az-Explorer'))
                self['filelist'].refresh()

    def callbackRenDir(self, answer):
        if answer is not None:
            source = self['filelist'].getSelection()[0]
            dest = answer
            try:
                os_rename(source, dest)
                self.uinfo = _('Renamed') + ': ' + source + ' --> ' + dest
                self['filelist'].refresh()
                self.updateLocationInfo()
            except:
                dei = self.session.open(MessageBox, _('Rename: %s \nFAILED!' % answer), MessageBox.TYPE_ERROR)
                dei.setTitle(_('az-Explorer'))
                self['filelist'].refresh()

    def callbackNewFile(self, answer):
        if answer is None:
            return
        dest = self['filelist'].getCurrentDirectory()
        if ' ' in answer or ' ' in dest or answer == '':
            dei = self.session.open(MessageBox, _('File name error !'), MessageBox.TYPE_ERROR)
            dei.setTitle(_('az-Explorer'))
            return
        order = 'touch ' + dest + answer
        if not fileExists(dest + answer):
            if ejecutaOrden(self, order):
                self.uinfo = _('File created') + ': ' + dest + answer
                self['filelist'].refresh()
                self.updateLocationInfo()
        else:
            dei = self.session.open(MessageBox, _('%s \nFAILED!' % order) + '\n' + 'File already exist!', MessageBox.TYPE_ERROR)
            dei.setTitle(_('az-Explorer'))
            self['filelist'].refresh()

    def callbackNewDir(self, answer):
        if answer is None:
            return
        dest = self['filelist'].getCurrentDirectory()
        if ' ' in answer or ' ' in dest or answer == '':
            dei = self.session.open(MessageBox, _('Directory name error !'), MessageBox.TYPE_ERROR)
            dei.setTitle(_('az-Explorer'))
            return
        order = dest + answer
        try:
            if not pathExists(dest + answer):
                os_mkdir(order)
                self['filelist'].refresh()
                self.uinfo = _('Folder created') + ': ' + order
                self.updateLocationInfo()
            else:
                dei = self.session.open(MessageBox, _('Target exist:') + order, MessageBox.TYPE_ERROR)
                dei.setTitle(_('az-Explorer'))
        except:
            dei = self.session.open(MessageBox, _('%s \nFAILED!' % order), MessageBox.TYPE_ERROR)
            dei.setTitle(_('az-Explorer'))
            self['filelist'].refresh()

    def go2CPmaniger(self):
        if self.MediaFilter:
            dei = self.session.open(MessageBox, _('Turn off the media-filter first.'), MessageBox.TYPE_INFO)
            dei.setTitle(_('az-Explorer...'))
            return
        if not self['filelist'].canDescent():
            source = self['filelist'].getCurrentDirectory() + self['filelist'].getFilename()
            self.session.openWithCallback(self.callbackCPmaniger, CPmaniger, source, nombre=self['filelist'].getFilename())
        elif self['filelist'].getSelectionIndex() != 0 and self['filelist'].canDescent():
            source = self['filelist'].getSelection()[0]
            self.session.openWithCallback(self.callbackCPmaniger, CPmaniger, source)

    def procesaBK(self):
        self.TimerBK.stop()
        os_system('ps >/tmp/procaz.txt')
        haycopia = False
        mensaje = None
        try:
            flines = open('/tmp/procaz.txt', 'r')
            psstring = ''
            for oneline in flines:
                psstring = psstring + oneline
                if 'cp -ppp' in psstring:
                    haycopia = True
                    mensaje = oneline.split('-ppp ')[1]
                    break

            flines.close()
        except:
            pass

        os_system('rm /tmp/procaz.txt')
        if not mensaje == None:
            nomsolo = ''
            try:
                xflines = open('/tmp/data_copy.txt', 'r')
                for xoneline in xflines:
                    arrmen = xoneline.split('[x*x]')
                    self.origen = arrmen[0]
                    nomsolo = os.path.split(self.origen)[1]
                    self.destino = arrmen[1] + '/' + str(nomsolo)
                    self.destino = self.destino.replace('//', '/')
                    self.fechacopia = arrmen[2]
                    break

            except:
                pass

            copiado = self.tamfichero(self.destino)
            copiado2 = self.tamfichero(self.origen)
            if copiado2 != '':
                copiado = copiado + ' / '
                copiado = copiado + copiado2
            if copiado != '':
                copiado = '- ' + copiado + ' - '
            losar = str(self.origen)
            if len(losar) > 65:
                losar = losar[0:65] + ' ...'
            losar = losar + ' -> ' + str(self.destino).replace(nomsolo, '')
            if len(losar) > 90:
                losar = losar[0:90] + ' ...'
            mensaje = _('Copy in background') + ' ' + copiado + self.fechacopia + ' -> ' + formateahora(lafecha=None) + '\n' + losar
            self['accion'].setText(mensaje)
            self.TimerBK.startLongTimer(6)
        else:
            self['accion'].setText(' ')
            if not haycopia:
                try:
                    if self.fechacopia != '':
                        self['accion'].setText(_('COPY in BACKGROUND') + ': ' + _('Copied') + ' :: ' + self.fechacopia + ' -> ' + formateahora(lafecha=None))
                except:
                    pass

                self.origen = None
                self.destino = None
                self.fechacopia = ''
                os_system('rm /tmp/data_copy.txt')

    def callbackCPmaniger(self, answer):
        if _('Copy in background') in answer:
            self.TimerBK.stop()
            self.TimerBK.startLongTimer(3)
        self.uinfo = answer
        self['filelist'].refresh()
        self.updateLocationInfo()

    def callbackSetStartDir(self, answerSD):
        if answerSD is True:
            config.plugins.azExplorer.startDir.value = self['filelist'].getCurrentDirectory()
            self.uinfo = _('Start directory') + ': ' + config.plugins.azExplorer.startDir.value
            config.plugins.azExplorer.startDir.save()
            self.updateLocationInfo()

    def sortName(self):
        list = self['filelist'].sortName()
        try:
            if self.MediaFilter:
                self.setTitle(_('[sort by Name] ') + self['filelist'].getCurrentDirectory())
            else:
                self.setTitle(_('[sort by Name] ') + self['filelist'].getCurrentDirectory())
        except:
            self.setTitle(_('az-Explorer'))

        config.plugins.azExplorer.ultimoorden.value = '1'
        config.plugins.azExplorer.ultimoorden.save()
        self.colocaorden()

    def sort1(self):
        aorden = getOrden()
        if aorden == '2':
            self.sortName()
        elif aorden == '3':
            self.sortDate()
        else:
            self.sortSize()

    def sort2(self):
        aorden = getOrden()
        if aorden == '2':
            self.sortSize()
        elif aorden == '3':
            self.sortName()
        else:
            self.sortDate()

    def sortDate(self):
        list = self['filelist'].sortDate()
        try:
            if self.MediaFilter:
                self.setTitle(_('[sort by Date] ') + self['filelist'].getCurrentDirectory())
            else:
                self.setTitle(_('[sort by Date] ') + self['filelist'].getCurrentDirectory())
        except:
            self.setTitle(_('az-Explorer'))

        config.plugins.azExplorer.ultimoorden.value = '2'
        config.plugins.azExplorer.ultimoorden.save()
        self.colocaorden()

    def sortSize(self):
        config.plugins.azExplorer.ultimoorden.value = '3'
        config.plugins.azExplorer.ultimoorden.save()
        list = self['filelist'].sortSize()
        try:
            if self.MediaFilter:
                self.setTitle(_('[sort by Size] ') + self['filelist'].getCurrentDirectory())
            else:
                self.setTitle(_('[sort by Size] ') + self['filelist'].getCurrentDirectory())
        except:
            self.setTitle(_('az-Explorer'))

        self.colocaorden()

    def searchMusic(self):
        slist = []
        foundIndex = 0
        index = 0
        files = os_listdir(self['filelist'].getCurrentDirectory())
        files.sort()
        for name in files:
            testname = name.lower()
            if testname.endswith('.mp3') or name.endswith('.m4a') or name.endswith('.ogg') or name.endswith('.flac'):
                slist.append((Item(text=name, filename=os_path.join(self['filelist'].getCurrentDirectory(), name)),))
                if self['filelist'].getFilename() == name:
                    foundIndex = index
                index = index + 1

        return (slist, foundIndex)

    def callbackSetSalir(self, resp):
        if resp:
            self.explExit()

    def salir(self):
        if config.plugins.azExplorer.confirmexit.value:
            dei = self.session.openWithCallback(self.callbackSetSalir, MessageBox, _('Do you want to exit?'), MessageBox.TYPE_YESNO)
            dei.setTitle(_('az-Explorer...'))
        else:
            self.explExit()

    def explExit(self):
        self.session.nav.playService(self.altservice)
        try:
            newStartDir = self['filelist'].getCurrentDirectory()
            if pathExists(newStartDir):
                config.plugins.azExplorer.ultimodir.value = newStartDir
                config.plugins.azExplorer.ultimodir.save()
            if self.MediaFilter:
                config.plugins.azExplorer.MediaFilter.value = 'on'
            else:
                config.plugins.azExplorer.MediaFilter.value = 'off'
            config.plugins.azExplorer.MediaFilter.save
        except:
            pass

        self.close()

    def CloseAndPlay(self):
        try:
            if self.MediaFilter:
                config.plugins.azExplorer.MediaFilter.value = 'on'
            else:
                config.plugins.azExplorer.MediaFilter.value = 'off'
            config.plugins.azExplorer.MediaFilter.save()
        except:
            pass

        self.close()


class vEditor(Screen):
    if esHD():
        skin = '\n\t\t<screen position="center,center" size="1770,945" title="File-Explorer">\n\t\t<widget name="filedata" position="7,10" size="1755,862" itemHeight="37" scrollbarMode="showOnDemand" />\n\t\t<ePixmap alphatest="blend" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/redHD.png" position="7,900" size="60,37" zPosition="5" />\n\t\t<eLabel font="Regular; 16" halign="left" position="66,900" size="463,37" text="%s" transparent="1" valign="center" zPosition="6" />\n\t\t<ePixmap alphatest="blend" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/greenHD.png" position="450,900" size="60,37" zPosition="5" />\n\t\t<eLabel font="Regular; 16" halign="left" position="508,900" size="463,37" text="%s" transparent="1" valign="center" zPosition="6" />\n\t\t<widget name="lineinfo" font="Regular; 18" halign="right" position="1105,900" size="654,37" transparent="1" />\n\t\t<widget name="barrapix_arr" position="0,0" zPosition="19" size="30,30" alphatest="blend" transparent="1" />\n\t\t<widget name="barrapix_abj" position="0,0" zPosition="19" size="30,30" alphatest="blend" transparent="1" />\t\t\n\t\t</screen>' % (_('Edit line '), _('View with console '))
    else:
        skin = '\n\t\t<screen position="center,center" size="1180,630" title="File-Explorer">\n\t\t<widget name="filedata" position="5,7" size="1170,575" itemHeight="25" scrollbarMode="showOnDemand" />\n\t\t<ePixmap alphatest="on" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/AzExplorer/res/red.png" position="5,600" size="40,25" zPosition="5" />\n\t\t<eLabel font="Regular; 16" halign="left" position="44,600" size="309,25" text="%s" transparent="1" valign="center" zPosition="6" />\n\t\t<ePixmap alphatest="on" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/AzExplorer/res/green.png" position="300,600" size="40,25" zPosition="5" />\n\t\t<eLabel font="Regular; 16" halign="left" position="339,600" size="309,25" text="%s" transparent="1" valign="center" zPosition="6" />\n\t\t<widget name="lineinfo" font="Regular; 18" halign="right" position="737,600" size="436,25" transparent="1" />\n\t\t<widget name="barrapix_arr" position="0,0" zPosition="19" size="20,20" alphatest="blend" transparent="1" />\n\t\t<widget name="barrapix_abj" position="0,0" zPosition="19" size="20,20" alphatest="blend" transparent="1" />\t\t\n\t\t</screen>' % (_('Edit line '), _('View with console '))

    def __init__(self, session, file):
        self.skin = vEditor.skin
        Screen.__init__(self, session)
        self.session = session
        self.file_name = file
        self.list = []
        self['lineinfo'] = Label(' ')
        self['filedata'] = MenuList(self.list)
        self.onShow.append(self.iniscroll)
        self.iniciadoS = False
        self['barrapix_arr'] = Pixmap()
        self['barrapix_abj'] = Pixmap()
        self['actions'] = ActionMap(['WizardActions', 'ColorActions'], {'red': self.editLine,
         'green': self.verConsola,
         'ok': self.viewLine,
         'back': self.exitEditor}, -1)
        self.selLine = None
        self.oldLine = None
        self.isChanged = False
        self['filedata'].onSelectionChanged.append(self.muevesel)
        self.GetFileData(file)

    def iniscroll(self):
        if not self.iniciadoS:
            self.actualizaScrolls()
            self.iniciadoS = True

    def actualizaScrolls(self):
        openspaSB(objectoself=self, nombrelista='filedata', barra='barrapix', altoitem=25, imagen=True)

    def muevesel(self):
        try:
            self.selLine = self['filedata'].getSelectionIndex()
            self.numero = len(self.list)
            self['lineinfo'].setText(str(self.selLine + 1) + '/' + str(self.numero))
        except:
            pass

    def exitEditor(self):
        if self.isChanged:
            warningtext = _('\nhave been CHANGED! Do you want to save it?')
            dei = self.session.openWithCallback(self.SaveFile, MessageBox, _(self.file_name + warningtext), MessageBox.TYPE_YESNO, default=False)
            dei.setTitle(_('az-Explorer...'))
        else:
            self.close()

    def GetFileData(self, fx):
        try:
            flines = open(fx, 'r')
            for line in flines:
                self.list.append(line)

            flines.close()
            self.setTitle(fx)
            self.muevesel()
        except:
            pass

    def viewLine(self):
        try:
            self.selLine = self['filedata'].getSelectionIndex()
            self.oldLine = self.list[self.selLine]
            editableText = self.list[self.selLine][:-1]
            self.session.openWithCallback(self.callbackviewLine, viewInputBox, linea=self.list[self.selLine], titulo=_('View line') + ' ' + str(self.selLine + 1))
        except:
            dei = self.session.open(MessageBox, _('This line is not valid text!'), MessageBox.TYPE_ERROR)
            dei.setTitle(_('Error...'))

    def editLine(self):
        try:
            self.selLine = self['filedata'].getSelectionIndex()
            self.oldLine = self.list[self.selLine]
            editableText = self.list[self.selLine][:-1]
            self.session.openWithCallback(self.callbackEditLine, spzVirtualKeyboard, titulo=_('Edit line ') + str(self.selLine + 1) + ' [' + self.file_name + ']:', texto=editableText, guardarvalor=False)
        except:
            dei = self.session.open(MessageBox, _('This line is not editable!'), MessageBox.TYPE_ERROR)
            dei.setTitle(_('Error...'))

    def callbackviewLine(self, newline):
        if newline == 'Edit':
            self.editLine()

    def callbackEditLine(self, newline):
        if newline is not None:
            self.isChanged = True
            del self.list[self.selLine]
            self.list.insert(self.selLine, newline + '\n')
        self.selLine = None
        self.oldLine = None

    def verConsola(self):
        self.session.open(Console, self.file_name, cmdlist=['cat ' + self.file_name])
        self.close()

    def SaveFile(self, answer):
        if answer is True:
            try:
                eFile = open(self.file_name, 'w')
                for x in self.list:
                    eFile.writelines(x)

                eFile.close()
            except:
                pass

            self.close()
        else:
            self.close()


class MviExplorer(Screen):
    skin = '\n\t\t<screen position="-300,-300" size="10,10" title="mvi-Explorer">\n\t\t</screen>'

    def __init__(self, session, file):
        self.skin = MviExplorer.skin
        Screen.__init__(self, session)
        self.file_name = file
        self['actions'] = ActionMap(['WizardActions'], {'ok': self.close,
         'back': self.close}, -1)
        self.onLayoutFinish.append(self.showMvi)

    def showMvi(self):
        os_system('/usr/bin/showiframe ' + self.file_name)


class PictureExplorerII(Screen):
    if HDSkn:
        if getDesktop(0).size().width() > 1030:
            skin = '\n\t\t\t\t<screen flags="wfNoBorder" position="0,0" size="1280,720" title="Picture-Explorer" backgroundColor="#00121214">\n\t\t\t\t\t<widget name="Picture" position="0,0" size="1280,720" zPosition="1" alphatest="blend" />\n\t\t\t\t\t<widget name="State" font="Regular;20" halign="center" position="0,650" size="1280,70" backgroundColor="#01080911" foregroundColor="#fcc000" transparent="0" zPosition="9"/>\n\t\t\t\t</screen>'
        else:
            skin = '\n\t\t\t\t<screen backgroundColor="#101214" flags="wfNoBorder" position="0,0" size="1024,576" title="Picture-Explorer">\n\t\t\t\t\t<widget alphatest="on" backgroundColor="noTransBG" name="Picture" position="0,0" size="1024,576" zPosition="1"/>\n\t\t\t\t\t<widget name="State" font="Regular;20" halign="center" position="0,506" size="1024,70" backgroundColor="#01080911" foregroundColor="#fcc000" transparent="0" zPosition="9"/>\n\t\t\t\t</screen>'
    else:
        skin = '\n\t\t\t<screen flags="wfNoBorder" position="0,0" size="720,576" title="Picture-Explorer" backgroundColor="#00121214">\n\t\t\t\t<widget name="Picture" position="0,0" size="720,576" zPosition="1" alphatest="on" />\n\t\t\t\t<widget name="State" font="Regular;20" halign="center" position="0,506" size="720,70" backgroundColor="#01080911" foregroundColor="#fcc000" transparent="0" zPosition="9"/>\n\t\t\t</screen>'

    def __init__(self, session, whatPic = None, whatDir = None):
        self.skin = PictureExplorerII.skin
        Screen.__init__(self, session)
        self.session = session
        self.whatPic = whatPic
        self.whatDir = whatDir
        self.picList = []
        self.Pindex = 0
        self.EXscale = AVSwitch().getFramebufferScale()
        self.EXpicload = ePicLoad()
        self['Picture'] = Pixmap()
        self['State'] = Label(_('loading... ') + self.whatPic)
        self['actions'] = ActionMap(['WizardActions', 'DirectionActions'], {'ok': self.info,
         'back': self.close,
         'up': self.info,
         'down': self.close,
         'left': self.Pleft,
         'right': self.Pright}, -1)
        self.EXpicload.PictureData.get().append(self.DecodeAction)
        self.onLayoutFinish.append(self.Show_Picture)

    def Show_Picture(self):
        if self.whatPic is not None:
            self.EXpicload.setPara([self['Picture'].instance.size().width(),
             self['Picture'].instance.size().height(),
             self.EXscale[0],
             self.EXscale[1],
             0,
             1,
             '#002C2C39'])
            self.EXpicload.startDecode(self.whatPic)
        if self.whatDir is not None:
            pidx = 0
            for root, dirs, files in os_walk(self.whatDir):
                for name in files:
                    if name.endswith('.jpg') or name.endswith('.jpeg') or name.endswith('.Jpg') or name.endswith('.Jpeg') or name.endswith('.JPG') or name.endswith('.JPEG'):
                        self.picList.append(name)
                        if name in self.whatPic:
                            self.Pindex = pidx
                        pidx = pidx + 1

            files.sort()

    def DecodeAction(self, pictureInfo = ''):
        if self.whatPic is not None:
            self['State'].setText(_('ready...'))
            self['State'].visible = False
            ptr = self.EXpicload.getData()
            self['Picture'].instance.setPixmap(ptr)

    def Pright(self):
        if len(self.picList) > 2:
            if self.Pindex < len(self.picList) - 1:
                self.Pindex = self.Pindex + 1
                self.whatPic = self.whatDir + str(self.picList[self.Pindex])
                self['State'].visible = True
                self['State'].setText(_('loading... ') + self.whatPic)
                self.EXpicload.startDecode(self.whatPic)
            else:
                self['State'].setText(_('wait...'))
                self['State'].visible = False
                self.session.open(MessageBox, _('No more picture-files.'), MessageBox.TYPE_INFO)

    def Pleft(self):
        if len(self.picList) > 2:
            if self.Pindex > 0:
                self.Pindex = self.Pindex - 1
                self.whatPic = self.whatDir + str(self.picList[self.Pindex])
                self['State'].visible = True
                self['State'].setText(_('loading... ') + self.whatPic)
                self.EXpicload.startDecode(self.whatPic)
            else:
                self['State'].setText(_('wait...'))
                self['State'].visible = False
                self.session.open(MessageBox, _('No more picture-files.'), MessageBox.TYPE_INFO)

    def info(self):
        if self['State'].visible:
            self['State'].setText(_('wait...'))
            self['State'].visible = False
        else:
            self['State'].visible = True
            self['State'].setText(_(self.whatPic))


class MoviePlayer(MP_parent):

    def __init__(self, session, service):
        self.session = session
        self.WithoutStopClose = False
        MP_parent.__init__(self, self.session, service)

    def leavePlayer(self):
        self.is_closing = True
        self.close()

    def leavePlayerConfirmed(self, answer):
        pass

    def doEofInternal(self, playing):
        if not self.execing:
            return
        if not playing:
            return
        self.leavePlayer()

    def showMovies(self):
        self.WithoutStopClose = True
        self.close()

    def movieSelected(self, service):
        self.leavePlayer(self.de_instance)

    def __onClose(self):
        if not self.WithoutStopClose:
            self.session.nav.playService(self.lastservice)


class MusicExplorer(MoviePlayer):
    if esHD():
        skin = '\n\t\t<screen backgroundColor="#50070810" flags="wfNoBorder" name="MusicExplorer" position="center,center" size="1080,45">\n\t\t<widget font="Regular;24" halign="right" position="75,0" render="Label" size="150,45" source="session.CurrentService" transparent="1" valign="center" zPosition="1">\n\t\t\t<convert type="ServicePosition">Remaining</convert>\n\t\t</widget>\n\t\t<widget font="Regular;24" position="255,0" render="Label" size="975,45" source="session.CurrentService" transparent="1" valign="center" zPosition="1">\n\t\t\t<convert type="ServiceName">Name</convert>\n\t\t</widget>\n\t\t</screen>'
    skin = '\n\t\t<screen backgroundColor="#50070810" flags="wfNoBorder" name="MusicExplorer" position="center,center" size="720,30">\n\t\t<widget font="Regular;24" halign="right" position="50,0" render="Label" size="100,30" source="session.CurrentService" transparent="1" valign="center" zPosition="1">\n\t\t\t<convert type="ServicePosition">Remaining</convert>\n\t\t</widget>\n\t\t<widget font="Regular;24" position="170,0" render="Label" size="650,30" source="session.CurrentService" transparent="1" valign="center" zPosition="1">\n\t\t\t<convert type="ServiceName">Name</convert>\n\t\t</widget>\n\t\t</screen>'

    def __init__(self, session, service, MusicDir, theFile):
        self.session = session
        MoviePlayer.__init__(self, session, service)
        self.MusicDir = MusicDir
        self.musicList = []
        self.Mindex = 0
        self.curFile = theFile
        self.searchMusic()
        self.onLayoutFinish.append(self.showMMI)
        MoviePlayer.WithoutStopClose = False

    def showMMI(self):
        os_system('/usr/bin/showiframe /usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/AzExplorer/res/music.mvi')

    def searchMusic(self):
        midx = 0
        for root, dirs, files in os_walk(self.MusicDir):
            for name in files:
                name = name.lower()
                if name.endswith('.mp3') or name.endswith('.mp2') or name.endswith('.ogg') or name.endswith('.wav') or name.endswith('.flac') or name.endswith('.m4a'):
                    self.musicList.append(name)
                    if self.curFile in name:
                        self.Mindex = midx
                    midx = midx + 1

    def seekFwd(self):
        if len(self.musicList) > 2:
            if self.Mindex < len(self.musicList) - 1:
                self.Mindex = self.Mindex + 1
                nextfile = self.MusicDir + str(self.musicList[self.Mindex])
                nextRef = eServiceReference('4097:0:0:0:0:0:0:0:0:0:' + nextfile)
                self.session.nav.playService(nextRef)
            else:
                self.session.open(MessageBox, _('No more playable files.'), MessageBox.TYPE_INFO)

    def seekBack(self):
        if len(self.musicList) > 2:
            if self.Mindex > 0:
                self.Mindex = self.Mindex - 1
                nextfile = self.MusicDir + str(self.musicList[self.Mindex])
                nextRef = eServiceReference('4097:0:0:0:0:0:0:0:0:0:' + nextfile)
                self.session.nav.playService(nextRef)
            else:
                self.session.open(MessageBox, _('No more playable files.'), MessageBox.TYPE_INFO)

    def doEofInternal(self, playing):
        if not self.execing:
            return
        if not playing:
            return
        self.seekFwd()


def ScanSysem_str():
    try:
        ret = ''
        out_line = os_popen('uptime').readline()
        ret = ret + 'at' + out_line + '\n'
        out_lines = []
        out_lines = os_popen('cat /proc/meminfo').readlines()
        for lidx in range(len(out_lines) - 1):
            tstLine = out_lines[lidx].split()
            if 'MemTotal:' in tstLine:
                ret = ret + out_lines[lidx]
            elif 'MemFree:' in tstLine:
                ret = ret + out_lines[lidx] + '\n'

        out_lines = []
        out_lines = os_popen('cat /proc/stat').readlines()
        for lidx in range(len(out_lines) - 1):
            tstLine = out_lines[lidx].split()
            if 'procs_running' in tstLine:
                ret = ret + 'Running processes: ' + tstLine[1]

        return ret
    except:
        return 'N/A'


class viewInputBox(Screen):
    if esHD():
        skin = '\n\t\t<screen name="viewline" position="center,center" size="1650,825" title="%s">\n\t\t<widget name="texto" position="7,7" size="1590,720" font="Regular;20"/>\n\t\t<ePixmap alphatest="on" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/redHD.png" position="0,765" size="52,37" zPosition="5" />\n\t\t<eLabel font="Regular;18" halign="left" position="52,765" size="180,37" text="%s" transparent="1" valign="center" zPosition="6" />\n\t\t</screen>' % (_('View...'), _('Edit line '))
    else:
        skin = '\n\t\t<screen name="viewline" position="center,center" size="1100,550" title="%s">\n\t\t<widget name="texto" position="5,5" size="1060,480" font="Regular;20"/>\n\t\t<ePixmap alphatest="on" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/AzExplorer/res/red.png" position="0,510" size="35,25" zPosition="5" />\n\t\t<eLabel font="Regular;18" halign="left" position="35,510" size="120,25" text="%s" transparent="1" valign="center" zPosition="6" />\n\t\t</screen>' % (_('View...'), _('Edit line '))

    def __init__(self, session, titulo = _('View...'), linea = ''):
        self.skin = viewInputBox.skin
        Screen.__init__(self, session)
        self.sesion = session
        self.setTitle(titulo)
        self['texto'] = Label(linea)
        self['actions'] = ActionMap(['WizardActions', 'DirectionActions', 'ColorActions'], {'ok': self.NothingToDo,
         'back': self.NothingToDo,
         'red': self.editaLinea}, -1)

    def NothingToDo(self):
        self.close(' ')

    def editaLinea(self):
        self.close('Edit')


class xviewInputBox(InputBox):
    sknew = '<screen name="vInputBox" position="center,center" size="1100,200" title="' + _('View') + '...">\n'
    sknew = sknew + '<widget name="text" position="5,5" size="1060,180" font="Regular;20"/>\n<widget name="input" position="0,580" size="'
    sknew = sknew + '150,30" font="Regular;20"/>\n</screen>'
    skin = sknew

    def __init__(self, session, title = '', windowTitle = _('Input'), useableChars = '0123456789', **kwargs):
        InputBox.__init__(self, session, title, windowTitle, useableChars, **kwargs)


class vInputBoxEdit(InputBox):
    vibnewx = str(getDesktop(0).size().width() - 80)
    sknew = '<screen name="vInputBox" position="center,center" size="' + vibnewx + ',85" title="' + _('Edit') + '...">\n'
    sknew = sknew + '<widget name="text" position="5,0" size="1270,50" font="Regular;15"/>\n<widget name="input" position="0,40" size="'
    sknew = sknew + vibnewx + ',30" font="Regular;18"/>\n</screen>'
    skin = sknew

    def __init__(self, session, title = '', windowTitle = _('Input'), useableChars = None, **kwargs):
        InputBox.__init__(self, session, title, windowTitle, useableChars, **kwargs)


class vInputBox(InputBox):
    vibnewx = str(getDesktop(0).size().width() - 80)
    sknew = '<screen name="vInputBox" position="center,center" size="' + vibnewx + ',85" title="' + _('Input') + '...">\n'
    sknew = sknew + '<widget name="text" position="5,0" size="1270,50" font="Regular;15"/>\n<widget name="input" position="0,40" size="'
    sknew = sknew + vibnewx + ',30" font="Regular;18"/>\n</screen>'
    skin = sknew

    def __init__(self, session, title = '', windowTitle = _('Input'), useableChars = None, **kwargs):
        InputBox.__init__(self, session, title, windowTitle, useableChars, **kwargs)


class vcpInputBox(InputBox):
    sknew = '<screen name="vInputBox" position="center,center" size="600,170" title="' + _('Input') + '...">\n'
    sknew = sknew + '<widget name="text" position="5,5" size="500,50" font="Regular;16"/>\n<widget name="input" position="0,80" size="'
    sknew = sknew + '150,30" font="Regular;20"/>\n</screen>'
    skin = sknew

    def __init__(self, session, title = '', windowTitle = _('Input'), useableChars = '0123456789', **kwargs):
        InputBox.__init__(self, session, title, windowTitle, useableChars, **kwargs)


class CPmaniger(Screen):
    if esHD():
        skin = '\n\t\t<screen position="center,center" size="1650,798" title="%s" name="cpmaniger">\n\t\t<widget name="File1" font="Regular; 18" halign="left" position="7,0" size="1635,39" transparent="1" valign="center" zPosition="4" noWrap="1" />\n\t\t<widget name="File2" font="Regular; 18" halign="left" position="42,39" size="1600,39" transparent="1" valign="center" zPosition="4" noWrap="1" />\n\t\t<widget name="File3" font="Regular; 18" halign="left" position="7,78" size="1635,39" transparent="1" valign="center" zPosition="4" noWrap="1" />\n\t\t<widget name="desFile" font="Regular; 18" halign="left" position="42,117" size="1600,39" transparent="1" valign="center" zPosition="4" noWrap="1" />\n\t\t<widget name="CPto" position="7,201" scrollbarMode="showOnDemand" size="1635,546" zPosition="4" itemHeight="42" />\n\t\t<eLabel backgroundColor="#555555" position="7,753" size="1635,3" zPosition="5" />\n\t\t<ePixmap alphatest="blend" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/redHD.png" position="0,760" size="52,37" zPosition="5" />\n\t\t<ePixmap alphatest="blend" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/yellowHD.png" position="435,760" size="52,37" zPosition="5" />\n\t\t<ePixmap alphatest="blend" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/blueHD.png" position="727,760" size="52,37" zPosition="5" />\n\t\t<eLabel font="Regular;18" halign="left" position="52,760" size="180,37" text="%s" transparent="1" valign="center" zPosition="6" />\n\t\t<eLabel font="Regular;18" halign="left" position="487,760" size="120,37" text="%s" transparent="1" valign="center" zPosition="6" />\n\t\t<eLabel font="Regular;18" halign="left" position="772,760" size="525,37" text="%s" transparent="1" valign="center" zPosition="6" />\n\t\t<ePixmap name="new ePixmap" position="7,0" size="1635,156" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/AzExplorer/res/hdfondolista.png" alphatest="blend" />\n\t\t<widget name="barrapix_arr" position="0,0" zPosition="19" size="30,30" alphatest="blend" transparent="1" />\n\t\t<widget name="barrapix_abj" position="0,0" zPosition="19" size="30,30" alphatest="blend" transparent="1" />\t\t\n\t\t</screen>' % (_('Select Copy/Move location...'),
         _('MOVE'),
         _('COPY'),
         _('COPY in BACKGROUND'))
    else:
        skin = '\n\t\t<screen position="center,center" size="1100,532" title="%s" name="cpmaniger">\n\t\t<widget name="File1" font="Regular; 18" halign="left" position="5,0" size="1090,26" transparent="1" valign="center" zPosition="4" noWrap="1" />\n\t\t<widget name="File2" font="Regular; 18" halign="left" position="28,26" size="1067,26" transparent="1" valign="center" zPosition="4" noWrap="1" />\n\t\t<widget name="File3" font="Regular; 18" halign="left" position="5,52" size="1090,26" transparent="1" valign="center" zPosition="4" noWrap="1" />\n\t\t<widget name="desFile" font="Regular; 18" halign="left" position="28,78" size="1067,26" transparent="1" valign="center" zPosition="4" noWrap="1" />\n\t\t<widget name="CPto" position="5,134" scrollbarMode="showOnDemand" size="1090,364" zPosition="4" />\n\t\t<eLabel backgroundColor="#555555" position="5,502" size="1090,2" zPosition="5" />\n\t\t<ePixmap alphatest="on" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/AzExplorer/res/red.png" position="0,507" size="35,25" zPosition="5" />\n\t\t<ePixmap alphatest="on" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/AzExplorer/res/yellow.png" position="290,507" size="35,25" zPosition="5" />\n\t\t<ePixmap alphatest="on" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/AzExplorer/res/blue.png" position="485,507" size="35,25" zPosition="5" />\n\t\t<eLabel font="Regular;18" halign="left" position="35,507" size="120,25" text="%s" transparent="1" valign="center" zPosition="6" />\n\t\t<eLabel font="Regular;18" halign="left" position="325,507" size="80,25" text="%s" transparent="1" valign="center" zPosition="6" />\n\t\t<eLabel font="Regular;18" halign="left" position="515,507" size="350,25" text="%s" transparent="1" valign="center" zPosition="6" />\n\t\t<ePixmap name="new ePixmap" position="5,0" size="1090,104" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/AzExplorer/res/fondolista.png" alphatest="blend" />\n\t\t<widget name="barrapix_arr" position="0,0" zPosition="19" size="20,20" alphatest="blend" transparent="1" />\n\t\t<widget name="barrapix_abj" position="0,0" zPosition="19" size="20,20" alphatest="blend" transparent="1" />\t\t\n\t\t</screen>' % (_('Select Copy/Move location...'),
         _('MOVE'),
         _('COPY'),
         _('COPY in BACKGROUND'))

    def __init__(self, session, source = '/tmp/none', nombre = None):
        self.skin = CPmaniger.skin
        Screen.__init__(self, session)
        self.sesion = session
        self.src = source
        self.nombrefile = nombre
        self.inBk = False
        self['desFile'] = Label(config.plugins.azExplorer.CopyDest.value)
        self['File1'] = Label(_('Copy/Move') + ' ' + _('File/Folder') + ':')
        self['File2'] = Label(self.src)
        self['File3'] = Label(_('To') + ':')
        self['CPto'] = myFileList(config.plugins.azExplorer.CopyDest.value, showDirectories=True, showFiles=False, matchingPattern='^.*\\.*', useServiceRef=False)
        self.onShow.append(self.iniscroll)
        self.iniciadoS = False
        self['barrapix_arr'] = Pixmap()
        self['barrapix_abj'] = Pixmap()
        self['actions'] = ActionMap(['WizardActions', 'DirectionActions', 'ColorActions'], {'ok': self.ok,
         'back': self.NothingToDo,
         'red': self.MoveFile,
         'left': self.left,
         'right': self.right,
         'up': self.up,
         'down': self.down,
         'yellow': self.CopyFile,
         'blue': self.CopyFileBk}, -1)
        self.onLayoutFinish.append(self.OneDescent)

    def iniscroll(self):
        if not self.iniciadoS:
            self.actualizaScrolls()
            self.iniciadoS = True

    def actualizaScrolls(self):
        openspaSB(objectoself=self, nombrelista='CPto', barra='barrapix', altoitem=26, imagen=True)

    def actualizaDest(self):
        self.actualizaScrolls()
        if self['CPto'].getSelectionIndex() != 0:
            erdes = self['CPto'].getSelection()[0]
            self['desFile'].setText(erdes)
        else:
            self['desFile'].setText(_('Select Copy/Move location...'))

    def up(self):
        self['CPto'].up()
        self.actualizaDest()

    def down(self):
        self['CPto'].down()
        self.actualizaDest()

    def left(self):
        self['CPto'].pageUp()
        self.actualizaDest()

    def right(self):
        self['CPto'].pageDown()
        self.actualizaDest()

    def OneDescent(self):
        if self['CPto'].canDescent():
            self['CPto'].descent()

    def ok(self):
        if self['CPto'].canDescent():
            self['CPto'].descent()
            self.actualizaDest()

    def NothingToDo(self):
        self.close(' ')

    def processCopy(self):
        cret = ' '
        if self['CPto'].getSelectionIndex() != 0:
            dest = self['CPto'].getSelection()[0]
            if self.src[len(self.src) - 1] == '/':
                order = 'cp -af "' + self.src + '" "' + dest + '"'
            else:
                order = 'cp "' + self.src + '" "' + dest + '"'
            config.plugins.azExplorer.CopyDest.value = dest
            config.plugins.azExplorer.CopyDest.save()
            config.plugins.azExplorer.save()
            self.origen = self.src
            self.destino = dest
            if not self.inBk:
                if ejecutaOrden(self, order):
                    cret = _('Copied') + ': ' + self.src + ' --> ' + dest
            else:
                open('/tmp/data_copy.txt', 'w').write(self.src + '[x*x]' + dest + '[x*x]' + formateahora(lafecha=None))
                cadena = 'cp -ppp ' + order[2:] + ' &\n'
                os_system(cadena)
                cret = _('Copy in background') + ' :: ' + order
                dei = self.session.open(MessageBox, _('Copy in background is started.') + '\n' + _('You can close azExplorer and the copy continue'), MessageBox.TYPE_INFO, timeout=10)
                dei.setTitle(_('az-Explorer'))
        self.close(cret)

    def okCopyFile(self, answer):
        if answer:
            self.processCopy()

    def CopyFileBk(self):
        self.CopyFile(True)

    def CopyFile(self, cpBk = False):
        self.inBk = cpBk
        if self['CPto'].getSelectionIndex() != 0:
            if self.nombrefile is not None:
                dest = self['CPto'].getSelection()[0]
                dest = dest + self.nombrefile
                if fileExists(dest):
                    dei = self.session.openWithCallback(self.okCopyFile, MessageBox, _('Target exist:') + '\n' + dest + '\n' + _('Overwrite?'), MessageBox.TYPE_YESNO, default=False)
                    dei.setTitle(_('az-Explorer...'))
                else:
                    self.okCopyFile(True)
            else:
                self.okCopyFile(True)

    def MoveFile(self):
        if self['CPto'].getSelectionIndex() != 0:
            if self.nombrefile is not None:
                dest = self['CPto'].getSelection()[0]
                dest = dest + self.nombrefile
                if fileExists(dest):
                    dei = self.session.openWithCallback(self.okMoveFile, MessageBox, _('Target exist:') + '\n' + dest + '\n' + _('Overwrite?'), MessageBox.TYPE_YESNO, default=False)
                    dei.setTitle(_('az-Explorer...'))
                else:
                    self.okMoveFile(True)
            else:
                self.okMoveFile(True)

    def okMoveFile(self, answer):
        if answer:
            cret = ' '
            if self['CPto'].getSelectionIndex() != 0:
                dest = self['CPto'].getSelection()[0]
                if self.src[len(self.src) - 1] == '/':
                    order = 'cp -af "' + self.src + '" "' + dest + '"'
                    DELorder = 'rm -r "' + self.src + '"'
                else:
                    order = 'cp "' + self.src + '" "' + dest + '"'
                    DELorder = 'rm -f "' + self.src + '"'
                config.plugins.azExplorer.CopyDest.value = dest
                config.plugins.azExplorer.CopyDest.save()
                if ejecutaOrden(self, order):
                    cret = _('Copied') + ': ' + self.src + ' --> ' + dest
                    if ejecutaOrden(self, DELorder):
                        if cret == ' ':
                            cret = cret + ' ' + _('Deleted') + ': ' + self.src
                        else:
                            cret = _('Moved') + ': ' + self.src + ' --> ' + dest
            self.close(cret)


class SoftLinkScreen(Screen):
    if esHD():
        skin = '\n\t\t<screen position="center,center" size="1650,798" title="%s" name="cpmaniger">\n\t\t<widget name="File1" font="Regular; 18" halign="left" position="7,0" size="1635,39" transparent="1" valign="center" zPosition="4" noWrap="1" />\n\t\t<widget name="File2" font="Regular; 18" halign="left" position="42,39" size="1600,39" transparent="1" valign="center" zPosition="4" noWrap="1" />\n\t\t<widget name="File3" font="Regular; 18" halign="left" position="7,78" size="1635,39" transparent="1" valign="center" zPosition="4" noWrap="1" />\n\t\t<widget name="desFile" font="Regular; 18" halign="left" position="42,117" size="1600,39" transparent="1" valign="center" zPosition="4" noWrap="1" />\n\t\t<widget name="SLto" position="7,201" scrollbarMode="showOnDemand" size="1635,546" zPosition="4" />\n\t\t<eLabel backgroundColor="#555555" position="7,753" size="1635,3" zPosition="5" />\n\t\t<ePixmap alphatest="blend" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/redHD.png" position="0,760" size="52,37" zPosition="5" />\n\t\t<ePixmap alphatest="blend" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/imgvk/yellowHD.png" position="465,760" size="52,37" zPosition="5" />\n\t\t<eLabel font="Regular;18" halign="left" position="52,760" size="255,37" text="%s" transparent="1" valign="center" zPosition="6" />\n\t\t<eLabel font="Regular;18" halign="left" position="517,760" size="300,37" text="%s" transparent="1" valign="center" zPosition="6" />\n\t\t<ePixmap name="new ePixmap" position="7,0" size="1635,156" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/AzExplorer/res/hdfondolista.png" alphatest="blend" />\n\t\t<widget name="barrapix_arr" position="0,0" zPosition="19" size="30,30" alphatest="blend" transparent="1" />\n\t\t<widget name="barrapix_abj" position="0,0" zPosition="19" size="30,30" alphatest="blend" transparent="1" />\t\t\n\t\t</screen>' % (_('Make a softlink...'), _('Cancel'), _('Make a softlink'))
    else:
        skin = '\n\t\t<screen position="center,center" size="1100,532" title="%s" name="cpmaniger">\n\t\t<widget name="File1" font="Regular; 18" halign="left" position="5,0" size="1090,26" transparent="1" valign="center" zPosition="4" noWrap="1" />\n\t\t<widget name="File2" font="Regular; 18" halign="left" position="28,26" size="1067,26" transparent="1" valign="center" zPosition="4" noWrap="1" />\n\t\t<widget name="File3" font="Regular; 18" halign="left" position="5,52" size="1090,26" transparent="1" valign="center" zPosition="4" noWrap="1" />\n\t\t<widget name="desFile" font="Regular; 18" halign="left" position="28,78" size="1067,26" transparent="1" valign="center" zPosition="4" noWrap="1" />\n\t\t<widget name="SLto" position="5,134" scrollbarMode="showOnDemand" size="1090,364" zPosition="4" />\n\t\t<eLabel backgroundColor="#555555" position="5,502" size="1090,2" zPosition="5" />\n\t\t<ePixmap alphatest="on" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/AzExplorer/res/red.png" position="0,507" size="35,25" zPosition="5" />\n\t\t<ePixmap alphatest="on" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/AzExplorer/res/yellow.png" position="310,507" size="35,25" zPosition="5" />\n\t\t<eLabel font="Regular;18" halign="left" position="35,507" size="170,25" text="%s" transparent="1" valign="center" zPosition="6" />\n\t\t<eLabel font="Regular;18" halign="left" position="345,507" size="200,25" text="%s" transparent="1" valign="center" zPosition="6" />\n\t\t<ePixmap name="new ePixmap" position="5,0" size="1090,104" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/AzExplorer/res/fondolista.png" alphatest="blend" />\n\t\t<widget name="barrapix_arr" position="0,0" zPosition="19" size="20,20" alphatest="blend" transparent="1" />\n\t\t<widget name="barrapix_abj" position="0,0" zPosition="19" size="20,20" alphatest="blend" transparent="1" />\t\t\n\t\t</screen>' % (_('Make a softlink...'), _('Cancel'), _('Make a softlink'))

    def __init__(self, session, source = '/tmp/'):
        self.skin = SoftLinkScreen.skin
        Screen.__init__(self, session)
        self.sesion = session
        self.src = source
        self.newSLname = ' '
        self['desFile'] = Label('/')
        self['File1'] = Label(_('Create simlynk') + ' ' + _('in') + ':')
        self['File2'] = Label(self.src)
        self['File3'] = Label(_('To') + ':')
        self['SLto'] = myFileList('/', showDirectories=True, showFiles=True, matchingPattern=None, useServiceRef=False)
        self['actions'] = ActionMap(['WizardActions', 'DirectionActions', 'ColorActions'], {'ok': self.ok,
         'back': self.NothingToDo,
         'red': self.salir,
         'left': self.left,
         'right': self.right,
         'up': self.up,
         'down': self.down,
         'yellow': self.GetSLname}, -1)
        self.onShow.append(self.iniscroll)
        self.iniciadoS = False
        self['barrapix_arr'] = Pixmap()
        self['barrapix_abj'] = Pixmap()

    def iniscroll(self):
        if not self.iniciadoS:
            self.actualizaScrolls()
            self.iniciadoS = True

    def actualizaScrolls(self):
        openspaSB(objectoself=self, nombrelista='SLto', barra='barrapix', altoitem=25, imagen=True)

    def salir(self):
        self.close(' ')

    def actualizaDest(self):
        if self['SLto'].getSelectionIndex() != 0:
            erdes = self['SLto'].getSelection()[0]
            self['desFile'].setText(erdes)
        else:
            self['desFile'].setText(_('Select symlink target...'))

    def up(self):
        self['SLto'].up()
        self.actualizaDest()

    def down(self):
        self['SLto'].down()
        self.actualizaDest()

    def left(self):
        self['SLto'].pageUp()
        self.actualizaDest()

    def right(self):
        self['SLto'].pageDown()
        self.actualizaDest()

    def GetSLname(self):
        nomsof = _('newname')
        if self['SLto'].getSelectionIndex() != 0:
            tempnom = self['SLto'].getSelection()[0]
            if os_path.isdir(tempnom):
                if tempnom == '/':
                    nomsof = _('root')
                else:
                    nomsof = tempnom.split('/')[-2]
            else:
                nomsof = tempnom
            self.session.openWithCallback(self.callbackSetLinkName, spzVirtualKeyboard, titulo=_('Create simlynk') + ' ' + _('in') + ' ' + self.src + ':', texto=nomsof, caracteres='[FILE]')

    def callbackSetLinkName(self, answer):
        if answer is None:
            return
        if ' ' in answer or answer == '':
            dei = self.session.open(MessageBox, _('Softlink name error !'), MessageBox.TYPE_ERROR)
            dei.setTitle(_('az-Explorer'))
            return
        self.newSLname = self.src + answer
        self.MakeSLnow()

    def ok(self):
        if self['SLto'].canDescent():
            self['SLto'].descent()
            self.actualizaDest()

    def NothingToDo(self):
        self.close(' ')

    def MakeSLnow(self):
        if self.newSLname != ' ':
            if self['SLto'].getSelectionIndex() != 0:
                if self['SLto'].canDescent():
                    destino = self['SLto'].getSelection()[0]
                    order = 'ln -s "' + self['SLto'].getSelection()[0] + '" "' + self.newSLname + '"'
                else:
                    order = 'ln -s "' + (self['SLto'].getCurrentDirectory() + self['SLto'].getFilename()) + '" "' + self.newSLname + '"'
                    destino = self['SLto'].getCurrentDirectory() + self['SLto'].getFilename()
                if ejecutaOrden(self, order):
                    self.close(_('Simlink created') + ': ' + self.newSLname + ' --> ' + destino)
                else:
                    self.close(' ')
        else:
            dei = self.session.open(MessageBox, _('Softlink name error !'), MessageBox.TYPE_ERROR)
            dei.setTitle(_('az-Explorer'))


global HDSkn ## Warning: Unused global
