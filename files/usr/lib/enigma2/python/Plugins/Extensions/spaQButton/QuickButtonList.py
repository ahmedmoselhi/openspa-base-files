from Components.MenuList import MenuList
from Tools.Directories import SCOPE_SKIN_IMAGE, resolveFilename, fileExists
from enigma import RT_HALIGN_LEFT, eListboxPythonMultiContent, gFont, RT_HALIGN_RIGHT, BT_SCALE, BT_KEEP_ASPECT_RATIO, getDesktop
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmapAlphaBlend
from Tools.LoadPixmap import LoadPixmap
from __init__ import _
from Plugins.Extensions.spazeMenu.plugin import esHD, fhd

def QuickButtonListEntry(key, text, imagen = None, texto2 = None):
    res = [text]
    if text[0] == '--':
        png = LoadPixmap(resolveFilename(SCOPE_SKIN_IMAGE, '/usr/lib/enigma2/python/Plugins/Extensions/spaQButton/pic/op_separator.png'))
        if png is not None:
            res.append(MultiContentEntryPixmapAlphaBlend(pos=(0, fhd(12)), size=(fhd(780), fhd(25)), png=png, flags=BT_SCALE | BT_KEEP_ASPECT_RATIO))
    else:
        res.append((eListboxPythonMultiContent.TYPE_TEXT,
         fhd(45),
         0,
         fhd(780),
         fhd(25),
         0,
         RT_HALIGN_LEFT,
         text[0]))
        if texto2 is not None:
            texto2 = texto2.replace('**', ' :: ')
            if len(texto2) > 80:
                texto2 = texto2[:77] + '...'
            res.append(MultiContentEntryText(pos=(fhd(290), 0), size=(fhd(669), fhd(25)), font=1, flags=RT_HALIGN_RIGHT, text=texto2, color=10066329))
        if imagen is not None:
            if ' :: ' in texto2:
                imagen = 'na'
            elif not fileExists('/usr/lib/enigma2/python/Plugins/Extensions/spaQButton/img/key_' + imagen + '.png'):
                imagen = 'tecla'
            path = '/usr/lib/enigma2/python/Plugins/Extensions/spaQButton/img/key_' + imagen + '.png'
        elif (key == 'green' or key == 'red') and texto2 == None:
            path = '/usr/lib/enigma2/python/Plugins/Extensions/spaQButton/pic/' + key + '.png'
        else:
            path = resolveFilename(SCOPE_SKIN_IMAGE, 'skin_default/buttons/key_' + key + '.png')
        png = LoadPixmap(path)
        if png is not None:
            res.append(MultiContentEntryPixmapAlphaBlend(pos=(fhd(5), 0), size=(fhd(35), fhd(25)), png=png, flags=BT_SCALE | BT_KEEP_ASPECT_RATIO))
    return res


class QuickButtonList(MenuList):

    def __init__(self, list, selection = 0, enableWrapAround = False):
        MenuList.__init__(self, list, enableWrapAround, eListboxPythonMultiContent)
        self.l.setFont(0, gFont('Regular', 20))
        self.l.setFont(1, gFont('Regular', 18))
        self.l.setItemHeight(fhd(25))
        self.selection = selection

    def postWidgetCreate(self, instance):
        MenuList.postWidgetCreate(self, instance)
        self.moveToIndex(self.selection)
