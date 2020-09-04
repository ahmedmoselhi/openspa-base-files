from Components.Label import Label
from Components.ActionMap import ActionMap
from Components.config import *
from Screens.Screen import Screen
from enigma import eListboxPythonMultiContent, eServiceCenter, gFont
from Tools.LoadPixmap import LoadPixmap
from Tools.Directories import fileExists

class IniciaSelListMC(MenuList):

    def __init__(self, list, enableWrapAround = False):
        MenuList.__init__(self, list, enableWrapAround, eListboxPythonMultiContent)
        self.l.setItemHeight(30)
        self.l.setFont(0, gFont('Regular', 19))
        self.l.setFont(1, gFont('Regular', 17))


def IniciaSelListEntryMC(texto, imagen = 'na'):
    res = [texto]
    res.append(MultiContentEntryText(pos=(42, 4), size=(1000, 30), font=0, text=texto))
    carpetaimg = '/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/images/'
    png = '' + carpetaimg + 'MC_vo' + imagen + '-fs8.png'
    if fileExists(png):
        fpng = LoadPixmap(png)
        res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND,
         2,
         2,
         35,
         25,
         fpng))
    return res


def ScalingmodeEntryComponent(text, active = 'no'):
    res = [text]
    if active == 'yes':
        png = '/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/images/checkok.png'
        if fileExists(png):
            fpng = LoadPixmap(png)
            res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHABLEND,
             4,
             0,
             35,
             25,
             fpng))
        else:
            text = text + ' (Active)'
    res.append(MultiContentEntryText(pos=(42, 0), size=(1000, 30), font=0, text=text))
    return res


def SubOptionsEntryComponent(text):
    res = [text]
    res.append(MultiContentEntryText(pos=(0, 0), size=(1000, 30), font=0, text=text))
    return res


class Scalingmode_Menu(Screen):
    skin = '\n\t<screen name="Scalingmode_Menu" position="30,55" size="350,180" title="%s" >\n\t<widget name="pathlabel" transparent="1" zPosition="2" position="0,220" size="380,20" font="Regular;16" />\n\t<widget name="list" zPosition="5" transparent="1" position="10,10" size="330,200" scrollbarMode="showOnDemand" />\n\t</screen>' % _('Scalingmode - Menu')

    def __init__(self, session):
        Screen.__init__(self, session)
        self['list'] = IniciaSelListMC([])
        self.list = []
        self.list.append(_('Full Screen'))
        self.list.append(_('Pan & Scan'))
        self.list.append(_('Letterbox'))
        self.list.append(_('Pillarbox'))
        self.list.append(_('Vertical Center'))
        self['pathlabel'] = Label(_('Select Scaling Mode'))
        self.activemode = int(config.av.scalmodemc.value)
        if fileExists('/tmp/.mcscaling'):
            try:
                f = open('/tmp/.mcscaling', 'r')
                for line in f.readlines():
                    self.activemode = int(line)

                f.close()
            except:
                pass

        self['actions'] = ActionMap(['OkCancelActions'], {'cancel': self.Exit,
         'ok': self.okbuttonClick}, -1)
        self.activemode = config.plugins.mc_scal.scalingmode.value
        self.onLayoutFinish.append(self.buildList)

    def buildList(self):
        list = []
        print 'active mode '
        print self.activemode
        for i in range(0, len(self.list)):
            text = '' + self.list[i]
            active = 'no'
            if str(i) == str(self.activemode):
                active = 'yes'
            list.append(ScalingmodeEntryComponent(text, active))

        self['list'].setList(list)

    def okbuttonClick(self):
        selection = self['list'].getSelectionIndex()
        try:
            open('/proc/scalingmode', 'w').write(str(selection))
        except IOError:
            pass

        try:
            open('/tmp/.mcscaling', 'w').write(str(selection))
        except:
            pass

        self.activemode = selection
        config.plugins.mc_scal.scalingmode.value = selection
        config.plugins.mc_scal.save()
        configfile.save()
        self.buildList()

    def Exit(self):
        self.close()
