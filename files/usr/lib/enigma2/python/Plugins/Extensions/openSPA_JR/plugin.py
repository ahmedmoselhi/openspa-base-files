from Plugins.Plugin import PluginDescriptor
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Screens.ChoiceBox import ChoiceBox
from Screens.Console import Console
from Screens.Standby import TryQuitMainloop
from Components.About import about
from Components.ActionMap import ActionMap
from Components.config import config, configfile, ConfigYesNo, ConfigSubsection, getConfigListEntry, ConfigSelection, ConfigNumber, ConfigText, ConfigInteger
from Components.ConfigList import ConfigListScreen
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.AVSwitch import AVSwitch
from Tools.Directories import fileExists
import os
from enigma import ePicLoad
from Plugins.Extensions.spazeMenu.plugin import esHD
config.plugins.openspa_jr = ConfigSubsection()
if esHD():
    config.plugins.openspa_jr.SecondInfobarStyle = ConfigSelection(default='sihd', choices=[('sihd', _('Secondinfobar OpenSPA_JRLG180')), ('bitratehd', _('Secondinfobar con info bitrate')), ('siblasvegas', _('Secondinfobar Las Vegas Edition'))])
    config.plugins.openspa_jr.InfobarSelector = ConfigSelection(default='ihd', choices=[('ihd', _('InfoBar JRLG1080')), ('idark', _('Infobar fondo oscuro'))])
    config.plugins.openspa_jr.ChannSelector = ConfigSelection(default='chhd', choices=[('chhd', _('Seleccion canales OpenSPA_JRLG')), ('cbluehd', _('Seleccion de canales fondo azul'))])
    config.plugins.openspa_jr.colorido = ConfigSelection(default='hd', choices=[('hd', _('Color claro')), ('ark', _('Color oscuro'))])
    config.plugins.openspa_jr.widget = ConfigSelection(default='0', choices=[('0', _('No info tiempo')), ('1hd', _('Info meteo nubes')), ('2hd', _('Info meteo estilo JRLG'))])
else:
    config.plugins.openspa_jr.SecondInfobarStyle = ConfigSelection(default='sJRLG', choices=[('sJRLG', _('Secondinfobar OpenSPA_JRLG')), ('sbaix', _('Secondinfobar OpenSPA_JRLG abajo'))])
    config.plugins.openspa_jr.InfobarSelector = ConfigSelection(default='iJRLG', choices=[('iJRLG', _('InfoBar JRLG arriba')), ('ibaix', _('Infobar JRLG abajo')), ('ibaix2', _('Infobar JRLG abajo v2'))])
    config.plugins.openspa_jr.ChannSelector = ConfigSelection(default='cJRLG', choices=[('cJRLG', _('Seleccion canales OpenSPA_JRLG')), ('cJRLG2', _('Seleccion de canales JRLG clasica'))])
    config.plugins.openspa_jr.colorido = ConfigSelection(default='JR', choices=[('JR', _('Escala de grises'))])
    config.plugins.openspa_jr.widget = ConfigSelection(default='0', choices=[('0', _('No info tiempo')),
     ('1', _('Info meteo simple (infobar abajo)')),
     ('2', _('Info meteo v2')),
     ('3', _('Info meteo estilo android')),
     ('4', _('Info meteo simple (infobar arriba)')),
     ('5', _('Info meteo estilo JRLG'))])
    config.plugins.openspa_jr.iconos = ConfigSelection(default='1/', choices=[('1/', _('Iconos JR')), ('2/', _('Iconos pepetmv'))])

def Plugins(**kwargs):
    return PluginDescriptor(name='Configuracion OpenSPA_JR', description=_('Herramienta de personalizacion para skin OpenSPA_JR'), where=PluginDescriptor.WHERE_PLUGINMENU, icon='plugin.png', fnc=main)


def main(session, **kwargs):
    session.open(JRSetup)


class JRSetup(ConfigListScreen, Screen):
    if esHD():
        skin = '\n            <screen name="JRSetup" position="65,50" size="1725,975" title="Skin OpenSPA_JR by sergiri" >  \n            <eLabel font="Regular;20" foregroundColor="#00ff4A3C" halign="center" position="120,925" size="180,39" text="Cancelar" transparent="1"/>  \n            <eLabel font="Regular;20" foregroundColor="#0056C856" halign="center" position="337,925" size="180,39" text="Guardar" transparent="1"/>\n            <eLabel font="Regular;20" foregroundColor="#00ffff00" halign="center" position="555,925" size="180,39" text="Reiniciar" transparent="1"/>\n            <ePixmap name="Info" position="780,906" size="67,67" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/openSPA_JR/button_info.png" zPosition="11" alphatest="blend"/>\n            <widget name="config" position="10,7" scrollbarMode="showOnDemand" size="825,525" transparent="1" itemHeight="40"/>\n            <widget name="Preview" position="900,256" size="747,426" zPosition="1" alphatest="blend"/>\n            <widget name="Info" font="Regular;20" foregroundColor="orange" halign="left" position="66,844" size="741,69" zPosition="10" transparent="1"/>\n            </screen>'
    else:
        skin = '\n           <screen name="JRSetup" position="65,50" size="1150,650" title="Skin OpenSPA_JR by sergiri" backgroundColor="metrixBackground">  \n           <eLabel font="Regular;20" foregroundColor="#00ff4A3C" halign="center" position="80,617" size="120,26" text="Cancelar" transparent="1"/>  \n           <eLabel font="Regular;20" foregroundColor="#0056C856" halign="center" position="225,617" size="120,26" text="Guardar" transparent="1"/>\n           <eLabel font="Regular;20" foregroundColor="#00ffff00" halign="center" position="370,617" size="120,26" text="Reiniciar" transparent="1"/>\n           <ePixmap name="Info" position="520,604" size="45,45" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/openSPA_JR/button_info.png" zPosition="11" alphatest="blend"/>\n           <widget name="config" position="7,5" scrollbarMode="showOnDemand" size="550,350" transparent="1"/>\n           <widget name="Preview" position="600,171" size="498,284" zPosition="1" alphatest="blend"/>\n           <widget name="Info" font="Regular;20" foregroundColor="orange" halign="left" position="44,563" size="494,46" zPosition="10" transparent="1"/>\n           </screen>'

    def __init__(self, session):
        Screen.__init__(self, session)
        self.session = session
        self.skinName = 'JRSetup'
        if esHD():
            self.skinFile = '/usr/share/enigma2/openSPA_JRLG1080/skin.xml'
        else:
            self.skinFile = '/usr/share/enigma2/openSPA_JRLG/skin.xml'
        self.skinMC = '/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/skins/default/skin.xml'
        self.previewFiles = '/usr/lib/enigma2/python/Plugins/Extensions/openSPA_JR/sample/'
        self.Scale = AVSwitch().getFramebufferScale()
        self.PicLoad = ePicLoad()
        self['Preview'] = Pixmap()
        list = []
        list.append(getConfigListEntry(_('Estilo InfoBar:'), config.plugins.openspa_jr.InfobarSelector))
        list.append(getConfigListEntry(_('Estilo SecondInfobar:'), config.plugins.openspa_jr.SecondInfobarStyle))
        list.append(getConfigListEntry(_('Estilo Seleccion de canales:'), config.plugins.openspa_jr.ChannSelector))
        list.append(getConfigListEntry(_('Estilo Meteo:'), config.plugins.openspa_jr.widget))
        list.append(getConfigListEntry(_('Colores :'), config.plugins.openspa_jr.colorido))
        if not esHD():
            list.append(getConfigListEntry(_('Iconos :'), config.plugins.openspa_jr.iconos))
        ConfigListScreen.__init__(self, list)
        self['actions'] = ActionMap(['OkCancelActions',
         'DirectionActions',
         'InputActions',
         'ColorActions',
         'EPGSelectActions'], {'left': self.keyLeft,
         'down': self.keyDown,
         'up': self.keyUp,
         'right': self.keyRight,
         'red': self.keyExit,
         'green': self.keySave,
         'yellow': self.keyReboot,
         'info': self.keyinfo,
         'cancel': self.keyExit}, -1)
        self.onLayoutFinish.append(self.UpdateComponents)
        self.onLayoutFinish.append(self.Getinfo)
        self['Info'] = Label()

    def GetPicturePath(self):
        try:
            returnValue = self['config'].getCurrent()[1].value
            if returnValue == '1/':
                path = '/usr/lib/enigma2/python/Plugins/Extensions/openSPA_JR/screens/JR.jpg'
            elif returnValue == '2/':
                path = '/usr/lib/enigma2/python/Plugins/Extensions/openSPA_JR/screens/pepet.jpg'
            else:
                path = '/usr/lib/enigma2/python/Plugins/Extensions/openSPA_JR/screens/' + returnValue + '.jpg'
            return path
        except:
            return '/enigma2/python/Plugins/Extensions/openSPA_JR/screens/default.jpg'

    def Getinfo(self):
        returninfo = self['config'].getCurrent()[1].value
        if returninfo == 'iJRLG':
            self['Info'].setText('Infobar original JRLG arriba')
        elif returninfo == 'ibaix':
            self['Info'].setText('Infobar JRLG abajo (con info ECM)')
        elif returninfo == 'ibaix2':
            self['Info'].setText('Infobar JRLG abajo v2')
        elif returninfo == 'idark':
            self['Info'].setText('Infobar JRLG con fondo oscuro. Dejar la info meteo seleccionando No info tiempo')
        elif returninfo == 'sJRLG':
            self['Info'].setText('Secondinfobar original JRLG')
        elif returninfo == 'sbaix':
            self['Info'].setText('Secondinfobar JRLG simetrico al original')
        elif returninfo == 'siblasvegas':
            self['Info'].setText('Secondinfobar con fondo oscuro y nuevos iconos estilo casino')
        elif returninfo == 'bitratehd':
            self['Info'].setText('Nota: aumenta el consumo de CPU usando info bitrate. No funciona en VU+ Solo 4K')
        elif returninfo == 'cJRLG':
            self['Info'].setText('Seleccion de canales original JRLG')
        elif returninfo == 'cJRLG2':
            self['Info'].setText('Seleccion de canales JRLG v2')
        elif returninfo == 'cbluehd':
            self['Info'].setText('Seleccion de canales con fondo azul')
        elif returninfo == '0':
            self['Info'].setText('Sin informacion del tiempo en infobar')
        elif returninfo == '1':
            self['Info'].setText('Info meteo simple (usar solo con infobar abajo)')
        elif returninfo == '2':
            self['Info'].setText('Info meteo v2 (usar solo con infobar abajo)')
        elif returninfo == '3':
            self['Info'].setText('Info meteo v3 (usar solo con infobar abajo)')
        elif returninfo == '4':
            self['Info'].setText('Info meteo simple (usar solo con infobar arriba)')
        elif returninfo == '5':
            self['Info'].setText('Info meteo JRLG (usar solo con infobar abajo)')
        elif returninfo == '1/':
            self['Info'].setText('Iconos originales JRLG')
        elif returninfo == '2/':
            self['Info'].setText('Iconos pepetmv')
        elif returninfo == 'hd':
            self['Info'].setText('Estilo JRLG original con colores claros')
        elif returninfo == 'ark':
            self['Info'].setText('Estilo JRLG con colores oscuros')
        else:
            self['Info'].setText('No info')

    def UpdatePicture(self):
        self.PicLoad.PictureData.get().append(self.DecodePicture)
        self.onLayoutFinish.append(self.ShowPicture)

    def ShowPicture(self):
        self.PicLoad.setPara([self['Preview'].instance.size().width(),
         self['Preview'].instance.size().height(),
         self.Scale[0],
         self.Scale[1],
         0,
         1,
         '#002C2C39'])
        self.PicLoad.startDecode(self.GetPicturePath())

    def DecodePicture(self, PicInfo = ''):
        ptr = self.PicLoad.getData()
        self['Preview'].instance.setPixmap(ptr)

    def UpdateComponents(self):
        self.UpdatePicture()

    def Iconselect(self, cadena2):
        llista2 = []
        n = 0
        for line in cadena2:
            if '<!--Iconos-->' in line:
                m = n + 1
            else:
                n = n + 1

        for h in range(0, m):
            llista2.append(cadena2[h])

        for j in range(m, len(cadena2)):
            text = str(cadena2[j]).split(' ')
            for i in range(0, len(text)):
                if text[i].startswith('pixmap='):
                    text1 = text[i].split('pixmap="openSPA_JRLG/new/v')
                    text2 = text1[1].split('/')
                    text[i] = 'pixmap="openSPA_JRLG/new/v' + config.plugins.openspa_jr.iconos.value + text2[1]

            text2 = ''
            for x in text:
                text2 = text2 + ' ' + x

            llista2.append(text2)

        return llista2

    def anadehd(self, cadena):
        if esHD():
            cadena = cadena + 'hd'
        return cadena

    def keyLeft(self):
        ConfigListScreen.keyLeft(self)
        self.ShowPicture()
        self.Getinfo()

    def keyRight(self):
        ConfigListScreen.keyRight(self)
        self.ShowPicture()
        self.Getinfo()

    def keyDown(self):
        self['config'].instance.moveSelection(self['config'].instance.moveDown)
        self.ShowPicture()
        self.Getinfo()

    def keyUp(self):
        self['config'].instance.moveSelection(self['config'].instance.moveUp)
        self.ShowPicture()
        self.Getinfo()

    def keyinfo(self):
        keyi = self.session.open(MessageBox, _('OpenSPA_JR by sergiri\nThanks to Pingu_TM and Metrix_HD coders for show me the way\nGracias a los desarrolladores de Pingu_TM y Metrix_HD por mostrarme el camino\n\nPara mas informacion, visitar :\nMore info in :\n\nhttp://openspa.info'), MessageBox.TYPE_INFO)
        keyi.setTitle(_('Creditos'))

    def keyReboot(self):
        restartbox = self.session.openWithCallback(self.restartGUI, MessageBox, _('Quieres reiniciar GUI?'), MessageBox.TYPE_YESNO)
        restartbox.setTitle(_('Reiniciar GUI'))

    def keySave(self):
        if not fileExists('/usr/lib/enigma2/python/Screens/newChannelSelection.pyo'):
            for x in self['config'].list:
                x[1].cancel()

            self.close()
            return
        for x in self['config'].list:
            x[1].save()

        try:
            skin_lines = []
            skinMC_lines = []
            if esHD():
                head_file = self.previewFiles + 'head' + config.plugins.openspa_jr.colorido.value + '.xml'
            else:
                head_file = self.previewFiles + 'head.xml'
            skFile = open(head_file, 'r')
            head_lines = skFile.readlines()
            skFile.close()
            for x in head_lines:
                skin_lines.append(x)

            skn_file = self.previewFiles + 'secondinfobar-' + config.plugins.openspa_jr.SecondInfobarStyle.value + '.xml'
            skFile = open(skn_file, 'r')
            file_lines = skFile.readlines()
            skFile.close()
            if not esHD():
                file_lines = self.Iconselect(file_lines)
            for x in file_lines:
                skin_lines.append(x)

            skn_file = self.previewFiles + 'infobar-' + config.plugins.openspa_jr.InfobarSelector.value + '.xml'
            skFile = open(skn_file, 'r')
            file_lines = skFile.readlines()
            skFile.close()
            for x in file_lines:
                skin_lines.append(x)

            skn_file = self.previewFiles + 'widget' + config.plugins.openspa_jr.widget.value + '.xml'
            skFile = open(skn_file, 'r')
            file_lines = skFile.readlines()
            skFile.close()
            for x in file_lines:
                skin_lines.append(x)

            skn_file = self.previewFiles + 'channellist-' + config.plugins.openspa_jr.ChannSelector.value + '.xml'
            skFile = open(skn_file, 'r')
            file_lines = skFile.readlines()
            skFile.close()
            for x in file_lines:
                skin_lines.append(x)

            if esHD():
                base_file = self.previewFiles + 'basehd.xml'
            else:
                base_file = self.previewFiles + 'base.xml'
            skFile = open(base_file, 'r')
            file_lines = skFile.readlines()
            skFile.close()
            for x in file_lines:
                skin_lines.append(x)

            xFile = open(self.skinFile, 'w')
            for xx in skin_lines:
                xFile.writelines(xx)

            xFile.close()
            self.session.open(MessageBox, _('Skin creado con exito'), MessageBox.TYPE_INFO, timeout=5)
        except:
            self.session.open(MessageBox, _('Error creando skin!'), MessageBox.TYPE_ERROR, timeout=5)

    def restartGUI(self, answer):
        if answer is True:
            self.session.open(TryQuitMainloop, 3)
        else:
            self.close()

    def keyExit(self):
        for x in self['config'].list:
            x[1].cancel()

        self.close()
