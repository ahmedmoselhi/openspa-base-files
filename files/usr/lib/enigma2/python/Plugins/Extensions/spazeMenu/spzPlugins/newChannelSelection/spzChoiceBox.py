from Components.Label import Label
from Components.MenuList import MenuList
from enigma import eSize, ePoint
from Screens.Screen import Screen
from Components.ActionMap import ActionMap

class spzChoiceBox(Screen):
    skin = ' <screen name="spzChoiceBox" position="center,center" size="250,310" title="spzChoiceBox" flags="wfNoBorder" backgroundColor="background">\n\t\t\t<widget name="texto" position="3,3" size="244,26" valign="center" halign="center" font="Regular; 18" transparent="1" text=" " />\n\t\t\t\n\t\t<eLabel name="linea1" position="1,1" size="1,308" backgroundColor="foreground" zPosition="-1" /><eLabel name="linea2" position="248,1" size="1,308" backgroundColor="foreground" zPosition="-1" /><eLabel name="linea3" position="1,1" size="248,1" backgroundColor="foreground" zPosition="-1" /><eLabel name="linea4" position="1,308" size="248,1" backgroundColor="foreground" zPosition="-1" /><widget name="menu" position="3,39" size="245,260" transparent="1" />\n\t\t</screen>' % _('spazeTeam ChoizeBox')

    def __init__(self, session, lista, titulo = None, posx = None, posy = None):
        Screen.__init__(self, session)
        self.session = session
        if titulo == None:
            titulo = _('Select an option...')
        self.posx = posx
        self.posy = posy
        self['texto'] = Label(_(titulo))
        self['menu'] = MenuList(lista)
        self['actions'] = ActionMap(['DirectionActions',
         'ShortcutActions',
         'WizardActions',
         'EPGSelectActions'], {'ok': self.key_ok,
         'green': self.key_ok,
         'red': self.exit,
         'back': self.exit,
         'up': self.kup,
         'down': self.kdown}, -1)
        self.onLayoutFinish.append(self.actualiza)

    def kdown(self):
        lista = self['menu'].l
        if self['menu'].getSelectionIndex() == len(lista) - 1:
            self['menu'].moveToIndex(0)
        else:
            self['menu'].down()

    def kup(self):
        lista = self['menu'].l
        if self['menu'].getSelectionIndex() == 0:
            self['menu'].moveToIndex(len(lista) - 1)
        else:
            self['menu'].up()

    def key_ok(self):
        Value = self['menu'].l.getCurrentSelection()[1]
        self.close(Value)

    def actualiza(self):
        if not posx == None and not posy == None:
            self.instance.move(ePoint(self.posx, self.posy))

    def nada(self):
        pass

    def exit(self):
        self.close(None)
