from __init__ import _
from Screens.Wizard import wizardManager, WizardSummary
from Screens.WizardLanguage import WizardLanguage
from Screens.Rc import Rc
from Components.Pixmap import Pixmap
from Components.Label import Label
from Screens.Screen import Screen
from Tools.Directories import resolveFilename, SCOPE_PLUGINS
from Components.Sources.StaticText import StaticText
from os import system
from Components.Ipkg import IpkgComponent

class OpenSPAPlugWizard(WizardLanguage, Rc):

    def __init__(self, session, interface = None):
        self.xmlfile = resolveFilename(SCOPE_PLUGINS, 'Extensions/OpenSPAPlug/OpenSPAPlugWizard.xml')
        WizardLanguage.__init__(self, session, showSteps=False, showStepSlider=False)
        Rc.__init__(self)
        self.skinName = 'StartWizard'
        self.session = session
        self['wizard'] = Pixmap()

    def updateopkg(self):
        self.session.openWithCallback(self.opkgFinished, InstallopkgUpdater, _('Please wait while we update the opkg database...'))

    def opkgFinished(self):
        from plugin import OpenSPAPlug
        self.session.openWithCallback(self.Finished, OpenSPAPlug, True)

    def Finished(self):
        self.currStep = self.getStepWithID('end')
        self.afterAsyncCode()

    def markDone(self):
        pass

    def back(self):
        WizardLanguage.back(self)


class InstallopkgUpdater(Screen):
    skin = '\n\t<screen position="c-300,c-25" size="600,50" title=" ">\n\t\t<widget source="statusbar" render="Label" position="10,5" zPosition="10" size="e-10,30" halign="center" valign="center" font="Regular;22" transparent="1" shadowColor="black" shadowOffset="-1,-1" />\n\t</screen>'

    def __init__(self, session, info):
        Screen.__init__(self, session)
        self['statusbar'] = StaticText(info)
        self.ipkg = IpkgComponent()
        self.ipkg.addCallback(self.ipkgCallback)
        self.ipkg.startCmd(IpkgComponent.CMD_UPDATE)

    def ipkgCallback(self, event = None, param = None):
        if event == IpkgComponent.EVENT_DONE:
            self.close()
