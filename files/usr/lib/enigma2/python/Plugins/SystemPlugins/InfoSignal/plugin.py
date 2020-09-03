from enigma import *
from Components.Label import Label
from Components.MenuList import MenuList
from Components.PluginComponent import plugins
from Screens.ChannelSelection import SimpleChannelSelection
from Components.MultiContent import MultiContentEntryText
from enigma import eListboxPythonMultiContent, eServiceCenter, gFont
from enigma import eTimer, eConsoleAppContainer
from ServiceReference import ServiceReference
from Screens.InfoBarGenerics import *
from Components.Pixmap import Pixmap
from Tools.LoadPixmap import LoadPixmap
import calendar, keymapparser
from keyids import KEYIDS
from Plugins.Plugin import PluginDescriptor
from Tools.KeyBindings import addKeyBinding
from Screens.Screen import Screen
from Components.ConfigList import ConfigListScreen
from Screens.MessageBox import MessageBox
from Screens.Console import Console
from Screens import Standby
from Screens.InfoBarGenerics import InfoBarPlugins
from Screens.Standby import TryQuitMainloop
from Components.ActionMap import ActionMap
from Components.Button import Button
from GlobalActions import globalActionMap
from Components.config import getConfigListEntry, ConfigEnableDisable, ConfigYesNo, ConfigText, ConfigClock, ConfigNumber, ConfigSelection, config, ConfigSubsection, ConfigSubList, ConfigSubDict, ConfigDirectory
from Tools import Notifications
import string
from time import localtime, asctime, time, gmtime
import os
from enigma import eSize, ePoint
from os import environ
import gettext
from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE, fileExists
from Plugins.Extensions.spazeMenu.plugin import esHD, fhd
lang = language.getLanguage()
environ['LANGUAGE'] = lang[:2]
lenguaje = str(lang[:2])
gettext.bindtextdomain('enigma2', resolveFilename(SCOPE_LANGUAGE))
gettext.textdomain('enigma2')
gettext.bindtextdomain('InfoSignal', '%s%s' % (resolveFilename(SCOPE_PLUGINS), 'SystemPlugins/InfoSignal/locale/'))

def _(txt):
    t = gettext.dgettext('InfoSignal', txt)
    if t == txt:
        t = gettext.gettext(txt)
    return t


from Components.ServiceList import ServiceList
from enigma import eSize
from Components.Pixmap import Pixmap

class InfoSignal(Screen):
    if esHD():
        skin = '\n\t\t\t<screen name="InfoSignal" position="572,24" size="1003,573" title="Tunner signal information" flags="wfNoBorder" backgroundColor="#ff000000">\n\t\t\t<widget source="session.CurrentService" render="Label" position="201,6" size="798,34" font="Regular; 19" backgroundColor="black" transparent="1" valign="center" noWrap="1" foregroundColor="#cccccc">\n\t\t\t  <convert type="ServiceName">Name</convert>\n\t\t\t</widget>\n\t\t\t<widget source="session.CurrentService" render="Label" position="199,375" size="798,39" font="Regular; 18" backgroundColor="black" transparent="1" valign="center" noWrap="1" foregroundColor="#cccccc">\n\t\t\t  <convert type="ServiceName">Reference</convert>\n\t\t\t</widget>\n\t\t\t  <widget source="session.CurrentService" render="Label" position="199,262" size="798,36" font="Regular; 18" halign="left" foregroundColor="#ffffff" backgroundColor="black" transparent="1" zPosition="23" noWrap="1">\n\t\t\t\t<convert type="nBmExtendedServiceInfo">TunerInfo</convert>\n\t\t\t  </widget>\n\t\t\t  <widget source="session.FrontendStatus" render="Label" position="892,54" size="108,33" font="Regular; 18" foregroundColor="#33cc99" backgroundColor="black" transparent="1" halign="left">\n\t\t\t\t<convert type="FrontendInfo">AGC</convert>\n\t\t\t  </widget>\n\t\t\t  <widget position="201,54" render="Progress" size="684,33" source="session.FrontendStatus" zPosition="5" borderWidth="1" borderColor="#33cc99" backgroundColor="#33cc99" transparent="1" foregroundColor="#33cc99" pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/InfoSignal/pvhd-fs8.png">\n\t<convert type="FrontendInfo">AGC</convert>\n</widget>\n\t\t\t  <widget source="session.FrontendStatus" render="Label" position="892,102" size="108,33" font="Regular; 18" foregroundColor="#6699ff" backgroundColor="black" transparent="1">\n\t\t\t\t<convert type="FrontendInfo">SNR</convert>\n\t\t\t  </widget>\n\t\t\t  <widget source="session.FrontendStatus" render="Label" position="559,136" size="253,30" font="Regular; 17" foregroundColor="#6699ff" backgroundColor="black" transparent="1">\n\t\t\t\t<convert type="FrontendInfo">SNRdB</convert>\n\t\t\t  </widget>\n\t\t\t  <widget position="201,102" render="Progress" size="684,33" source="session.FrontendStatus" zPosition="5" borderWidth="1" borderColor="#6699ff" transparent="1" backgroundColor="#6699ff" foregroundColor="#6699ff" pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/InfoSignal/pahd-fs8.png">\n\t<convert type="FrontendInfo">SNR</convert>\n</widget>\n\t\t\t  <widget source="session.FrontendStatus" render="Label" position="892,177" size="108,33" font="Regular; 18" foregroundColor="#ff6600" backgroundColor="black" transparent="1">\n\t\t\t\t<convert type="FrontendInfo">BER</convert>\n\t\t\t  </widget>\n\t\t\t  <widget position="201,177" render="Progress" size="684,33" source="session.FrontendStatus" zPosition="5" borderWidth="1" borderColor="#ff6600" transparent="1" backgroundColor="#ff6600" foregroundColor="#ff6600" pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/InfoSignal/pn-fs8.png">\n\t\t\t\t<convert type="FrontendInfo">BER</convert>\n\t\t\t  </widget>\n\t\t\t  <eLabel name="new eLabel" position="9,54" size="172,33" text="%s" foregroundColor="#999999" transparent="1" halign="right" font="Regular; 16" backgroundColor="black" />\n\t\t\t  <eLabel name="new eLabel" position="9,102" size="172,33" text="%s" foregroundColor="#999999" transparent="1" halign="right" font="Regular; 16" backgroundColor="black" />\n\t\t\t  <eLabel name="new eLabel" position="9,177" size="169,33" text="%s" foregroundColor="#999999" transparent="1" halign="right" font="Regular; 16" backgroundColor="black" />\n\n\t\t\t<widget source="session.FrontendInfo" render="FixedLabel" text="DVB-C" position="199,426" size="97,30" font="Regular; 17" foregroundColor="#ffffff" backgroundColor="black" transparent="1">\n\t\t\t\t<convert type="FrontendInfo">TYPE</convert>\n\t\t\t\t<convert type="ValueRange">1,1</convert>\n\t\t\t\t<convert type="ConditionalShowHide" />\n\t\t\t  </widget>\n\t\t\t  <widget source="session.FrontendInfo" render="FixedLabel" text="DVB-S" position="199,426" size="97,30" font="Regular; 17" foregroundColor="#ffffff" backgroundColor="black" transparent="1">\n\t\t\t\t<convert type="FrontendInfo">TYPE</convert>\n\t\t\t\t<convert type="ValueRange">0,0</convert>\n\t\t\t\t<convert type="ConditionalShowHide" />\n\t\t\t  </widget>\n\t\t\t  <widget source="session.FrontendInfo" render="FixedLabel" text="DVB-T" position="199,426" size="90,30" font="Regular; 17" foregroundColor="#ffffff" backgroundColor="black" transparent="1">\n\t\t\t\t<convert type="FrontendInfo">TYPE</convert>\n\t\t\t\t<convert type="ValueRange">2,2</convert>\n\t\t\t\t<convert type="ConditionalShowHide" />\n\t\t\t  </widget>\n\t\t\t  <widget source="session.CurrentService" render="Label" font="Regular; 16" position="762,381" size="84,30" halign="right" foregroundColor="#ffffff" backgroundColor="black" transparent="1">\n\t\t\t\t<convert type="ServiceInfo">VideoWidth</convert>\n\t\t\t  </widget>\n\t\t\t  <eLabel text="x" font="Regular; 16" position="849,382" size="22,30" halign="center" foregroundColor="#999999" backgroundColor="black" transparent="1" />\n\t\t\t  <widget source="session.CurrentService" render="Label" font="Regular; 16" position="873,382" size="91,30" halign="left" foregroundColor="#ffffff" backgroundColor="black" transparent="1">\n\t\t\t\t<convert type="ServiceInfo">VideoHeight</convert>\n\t\t\t  </widget>\n\n\t\t\t<!-- letra canal -->\n\t\t\t  \n\t\t\t  <widget source="session.FrontendInfo" render="FixedLabel" position="289,426" size="30,30" transparent="1" zPosition="4" text="A" foregroundColor="#00aa00" backgroundColor="black" font="Regular;18" halign="center">\n\t\t\t\t<convert type="FrontendInfo">NUMBER</convert>\n\t\t\t\t<convert type="ValueRange">0,0</convert>\n\t\t\t\t<convert type="ConditionalShowHide" />\n\t\t\t  </widget>\n\t\t\t  \n\t\t\t  <widget source="session.FrontendInfo" render="FixedLabel" position="289,426" size="30,30" transparent="1" zPosition="4" text="B" foregroundColor="#00aa00" backgroundColor="black" font="Regular;18" halign="center">\n\t\t\t\t<convert type="FrontendInfo">NUMBER</convert>\n\t\t\t\t<convert type="ValueRange">1,1</convert>\n\t\t\t\t<convert type="ConditionalShowHide" />\n\t\t\t  </widget>\n\t\t\t  \n\t\t\t  <widget source="session.FrontendInfo" render="FixedLabel" position="289,426" size="30,30" transparent="1" zPosition="4" text="C" foregroundColor="#00aa00" backgroundColor="black" font="Regular;18" halign="center">\n\t\t\t\t<convert type="FrontendInfo">NUMBER</convert>\n\t\t\t\t<convert type="ValueRange">2,2</convert>\n\t\t\t\t<convert type="ConditionalShowHide" />\n\t\t\t  </widget>\n\t\t\t  \n\t\t\t  <widget source="session.FrontendInfo" render="FixedLabel" position="289,426" size="30,30" transparent="1" zPosition="4" text="D" foregroundColor="#00aa00" backgroundColor="black" font="Regular;18" halign="center">\n\t\t\t\t<convert type="FrontendInfo">NUMBER</convert>\n\t\t\t\t<convert type="ValueRange">3,3</convert>\n\t\t\t\t<convert type="ConditionalShowHide" />\n\t\t\t  </widget>\n\t\t\t  <widget source="session.FrontendInfo" render="FixedLabel" position="289,426" size="30,30" transparent="1" zPosition="4" text="E" foregroundColor="#00aa00" backgroundColor="black" font="Regular;18" halign="center">\n\t\t\t\t<convert type="FrontendInfo">NUMBER</convert>\n\t\t\t\t<convert type="ValueRange">4,4</convert>\n\t\t\t\t<convert type="ConditionalShowHide" />\n\t\t\t  </widget>\t\t\t  \n\t\t\t  <widget source="session.FrontendInfo" render="FixedLabel" position="289,426" size="30,30" transparent="1" zPosition="4" text="F" foregroundColor="#00aa00" backgroundColor="black" font="Regular;18" halign="center">\n\t\t\t\t<convert type="FrontendInfo">NUMBER</convert>\n\t\t\t\t<convert type="ValueRange">5,5</convert>\n\t\t\t\t<convert type="ConditionalShowHide" />\n\t\t\t  </widget>\n\t\t\t  <widget source="session.FrontendInfo" render="FixedLabel" position="289,426" size="30,30" transparent="1" zPosition="4" text="G" foregroundColor="#00aa00" backgroundColor="black" font="Regular;18" halign="center">\n\t\t\t\t<convert type="FrontendInfo">NUMBER</convert>\n\t\t\t\t<convert type="ValueRange">6,6</convert>\n\t\t\t\t<convert type="ConditionalShowHide" />\n\t\t\t  </widget>\t\t\t  \n\t\t\t  \n\t\t\t  <widget source="session.CurrentService" render="Label" position="43,300" size="954,64" font="Regular; 16" valign="center" halign="left" foregroundColor="#999999" backgroundColor="black" transparent="1" noWrap="0">\n\t\t\t\t<convert type="PliExtraInfo">ServiceInfo</convert>\n\t\t\t  </widget>\n\t\t\t<!-- fin info canal-->\n\t\t\t\t<widget source="session.CurrentService" render="Label" position="334,427" size="456,30" transparent="1" zPosition="1" foregroundColor="#ffffff" font="Regular; 17" valign="center" halign="left">\n\t\t\t\t  <convert type="PliExtraInfo">PIDInfo</convert>\n\t\t\t\t</widget>\t    \t\t  \n\n\t\t\t\t<widget source="session.CurrentService" render="Label" position="199,474" size="783,39" transparent="1" zPosition="1" foregroundColor="#00ffffff" font="Regular; 16" valign="center" halign="left" backgroundColor="black">\n\t\t\t\t  <convert type="PliExtraInfo">CryptoBar</convert>\n\t\t\t\t</widget>\t\n\t\t\t\t<widget source="session.CurrentService" render="Label" position="199,519" size="783,39" transparent="1" zPosition="1" foregroundColor="#00ffffff" font="Regular;18" valign="center" halign="left">\n\t\t\t\t  <convert type="PliExtraInfo">CryptoSpecial</convert>\n\t\t\t\t</widget>\t\n\t\t\t<eLabel name="new eLabel" position="373,136" size="178,30" text="SNR(dB)" foregroundColor="#999999" transparent="1" halign="right" font="Regular; 16" backgroundColor="black" />\n\t\t\t<eLabel name="new eLabel" position="9,7" size="172,33" text="Channel" foregroundColor="#999999" transparent="1" halign="right" font="Regular; 16" backgroundColor="black" valign="center" />\t\t    \n\t\t\t<eLabel name="new eLabel" position="9,375" size="172,39" text="REF" foregroundColor="#999999" transparent="1" halign="right" font="Regular; 16" backgroundColor="black" valign="center" />\t\t    \n\n\t\t\t<eLabel name="new eLabel" position="9,423" size="172,39" text="%s" foregroundColor="#999999" transparent="1" halign="right" font="Regular; 16" backgroundColor="black" />\t\t    \n\t\t\t<eLabel name="new eLabel" position="9,262" size="172,36" text="%s" foregroundColor="#999999" transparent="1" halign="right" font="Regular; 16" backgroundColor="black" noWrap="1" />\t\t       \n\t\t\t<eLabel name="new eLabel" position="9,474" size="172,39" text="%s" foregroundColor="#999999" transparent="1" halign="right" font="Regular; 16" backgroundColor="#40444444" valign="center" />\t\t    \t\t    \n\t\t\t\t\t\n\t\t\t<eLabel name="linea" position="1,219" size="1003,1" foregroundColor="#40444444" transparent="0" zPosition="20" backgroundColor="#30555555" />\n\t\t\t<eLabel name="fondolinea" position="1,220" size="1003,33" foregroundColor="#40222222" transparent="0" zPosition="-1" backgroundColor="#35222222" />\n\t\t\t<widget name="farr" position="531,225" size="37,27" zPosition="10" pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/InfoSignal/flear-fs8.png" alphatest="blend" />\n\t\t\t<widget name="fabj" position="531,225" size="37,27" zPosition="10" pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/InfoSignal/fleab-fs8.png" alphatest="blend" />\n\t\t\t<ePixmap name="chmas" position="801,223" size="40,28" pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/InfoSignal/chmashd.png" alphatest="blend" zPosition="20" />\n\t\t\t<ePixmap name="chmenos" position="846,223" size="40,28" pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/InfoSignal/chmenoshd.png" alphatest="blend" zPosition="20" />\n\t\t\t<ePixmap name="chok" position="891,223" size="40,28" pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/InfoSignal/okhd.png" alphatest="blend" zPosition="20" />\n\t\t\t<ePixmap name="chmover" position="951,223" size="40,28" pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/InfoSignal/moverhd.png" alphatest="blend" zPosition="20" />\n\t\t\t<ePixmap name="fondop1" position="201,49" size="684,39" pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/InfoSignal/fp-fs8.png" alphatest="blend" zPosition="50" />\n\t\t\t<ePixmap name="fondop2" position="201,97" size="684,39" pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/InfoSignal/fp-fs8.png" alphatest="blend" zPosition="50" />\n\t\t\t<ePixmap name="fondop3" position="201,172" size="684,39" pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/InfoSignal/fp-fs8.png" alphatest="blend" zPosition="50" />\n\t\t\t<widget name="fondosc" position="1,1" size="1000,570" zPosition="-10" backgroundColor="#40000000" />\n\t\t\t<widget name="bordesc" position="0,0" size="1003,573" zPosition="-11" backgroundColor="#40333333" />\n\t\t\t\t\t\t  <widget source="session.FrontendStatus" render="Label" position="574,475" size="408,33" font="Regular; 18" foregroundColor="#ff6600" backgroundColor="black" transparent="1" halign="right">\n\t\t\t\t<convert type="FrontendInfo">STRING</convert>\n\t\t\t  </widget>\n\t\t</screen>\n\t\t' % (_('Quality'),
         _('Signal'),
         _('BER'),
         _('Tunner'),
         _('Information'),
         _('Crypto'))
    else:
        skin = '\n\t\t<screen name="InfoSignal" position="572,24" size="669,382" title="Tunner signal information" flags="wfNoBorder" backgroundColor="#ff000000">\n\t\t\t<widget source="session.CurrentService" render="Label" position="134,4" size="532,23" font="Regular; 19" backgroundColor="black" transparent="1" valign="center" noWrap="1" foregroundColor="#cccccc">\n\t\t\t  <convert type="ServiceName">Name</convert>\n\t\t\t</widget>\n\t\t\t<widget source="session.CurrentService" render="Label" position="133,250" size="532,26" font="Regular; 18" backgroundColor="black" transparent="1" valign="center" noWrap="1" foregroundColor="#cccccc">\n\t\t\t  <convert type="ServiceName">Reference</convert>\n\t\t\t</widget>\n\t\t\t  <widget source="session.CurrentService" render="Label" position="133,175" size="532,24" font="Regular; 18" halign="left" foregroundColor="#ffffff" backgroundColor="black" transparent="1" zPosition="23" noWrap="1">\n\t\t\t\t<convert type="nBmExtendedServiceInfo">TunerInfo</convert>\n\t\t\t  </widget>\n\t\t\t  <widget source="session.FrontendStatus" render="Label" position="595,36" size="72,22" font="Regular; 18" foregroundColor="#33cc99" backgroundColor="black" transparent="1" halign="left">\n\t\t\t\t<convert type="FrontendInfo">AGC</convert>\n\t\t\t  </widget>\n\t\t\t  <widget position="134,36" render="Progress" size="456,22" source="session.FrontendStatus" zPosition="5" borderWidth="1" borderColor="#33cc99" backgroundColor="#33cc99" transparent="1" foregroundColor="#33cc99" pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/InfoSignal/pv-fs8.png">\n\t<convert type="FrontendInfo">AGC</convert>\n</widget>\n\t\t\t  <widget source="session.FrontendStatus" render="Label" position="595,68" size="72,22" font="Regular; 18" foregroundColor="#6699ff" backgroundColor="black" transparent="1">\n\t\t\t\t<convert type="FrontendInfo">SNR</convert>\n\t\t\t  </widget>\n\t\t\t  <widget source="session.FrontendStatus" render="Label" position="373,91" size="169,20" font="Regular; 17" foregroundColor="#6699ff" backgroundColor="black" transparent="1">\n\t\t\t\t<convert type="FrontendInfo">SNRdB</convert>\n\t\t\t  </widget>\n\t\t\t  <widget position="134,68" render="Progress" size="456,22" source="session.FrontendStatus" zPosition="5" borderWidth="1" borderColor="#6699ff" transparent="1" backgroundColor="#6699ff" foregroundColor="#6699ff" pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/InfoSignal/pa-fs8.png">\n\t<convert type="FrontendInfo">SNR</convert>\n</widget>\n\t\t\t  <widget source="session.FrontendStatus" render="Label" position="595,118" size="72,22" font="Regular; 18" foregroundColor="#ff6600" backgroundColor="black" transparent="1">\n\t\t\t\t<convert type="FrontendInfo">BER</convert>\n\t\t\t  </widget>\n\t\t\t  <widget position="134,118" render="Progress" size="456,22" source="session.FrontendStatus" zPosition="5" borderWidth="1" borderColor="#ff6600" transparent="1" backgroundColor="#ff6600" foregroundColor="#ff6600" pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/InfoSignal/pnhd-fs8.png">\n\t\t\t\t<convert type="FrontendInfo">BER</convert>\n\t\t\t  </widget>\n\t\t\t  <eLabel name="new eLabel" position="6,36" size="115,22" text="%s" foregroundColor="#999999" transparent="1" halign="right" font="Regular; 16" backgroundColor="black" />\n\t\t\t  <eLabel name="new eLabel" position="6,68" size="115,22" text="%s" foregroundColor="#999999" transparent="1" halign="right" font="Regular; 16" backgroundColor="black" />\n\t\t\t  <eLabel name="new eLabel" position="6,118" size="113,22" text="%s" foregroundColor="#999999" transparent="1" halign="right" font="Regular; 16" backgroundColor="black" />\n\n\t\t\t<widget source="session.FrontendInfo" render="FixedLabel" text="DVB-C" position="133,284" size="65,20" font="Regular; 17" foregroundColor="#ffffff" backgroundColor="black" transparent="1">\n\t\t\t\t<convert type="FrontendInfo">TYPE</convert>\n\t\t\t\t<convert type="ValueRange">1,1</convert>\n\t\t\t\t<convert type="ConditionalShowHide" />\n\t\t\t  </widget>\n\t\t\t  <widget source="session.FrontendInfo" render="FixedLabel" text="DVB-S" position="133,284" size="65,20" font="Regular; 17" foregroundColor="#ffffff" backgroundColor="black" transparent="1">\n\t\t\t\t<convert type="FrontendInfo">TYPE</convert>\n\t\t\t\t<convert type="ValueRange">0,0</convert>\n\t\t\t\t<convert type="ConditionalShowHide" />\n\t\t\t  </widget>\n\t\t\t  <widget source="session.FrontendInfo" render="FixedLabel" text="DVB-T" position="133,284" size="60,20" font="Regular; 17" foregroundColor="#ffffff" backgroundColor="black" transparent="1">\n\t\t\t\t<convert type="FrontendInfo">TYPE</convert>\n\t\t\t\t<convert type="ValueRange">2,2</convert>\n\t\t\t\t<convert type="ConditionalShowHide" />\n\t\t\t  </widget>\n\t\t\t  <widget source="session.CurrentService" render="Label" font="Regular; 16" position="508,254" size="56,20" halign="right" foregroundColor="#ffffff" backgroundColor="black" transparent="1">\n\t\t\t\t<convert type="ServiceInfo">VideoWidth</convert>\n\t\t\t  </widget>\n\t\t\t  <eLabel text="x" font="Regular; 16" position="566,255" size="15,20" halign="center" foregroundColor="#999999" backgroundColor="black" transparent="1" />\n\t\t\t  <widget source="session.CurrentService" render="Label" font="Regular; 16" position="582,255" size="61,20" halign="left" foregroundColor="#ffffff" backgroundColor="black" transparent="1">\n\t\t\t\t<convert type="ServiceInfo">VideoHeight</convert>\n\t\t\t  </widget>\n\n\t\t\t<!-- letra canal -->\n\t\t\t  \n\t\t\t  <widget source="session.FrontendInfo" render="FixedLabel" position="193,284" size="20,20" transparent="1" zPosition="4" text="A" foregroundColor="#00aa00" backgroundColor="black" font="Regular;18" halign="center">\n\t\t\t\t<convert type="FrontendInfo">NUMBER</convert>\n\t\t\t\t<convert type="ValueRange">0,0</convert>\n\t\t\t\t<convert type="ConditionalShowHide" />\n\t\t\t  </widget>\n\t\t\t  \n\t\t\t  <widget source="session.FrontendInfo" render="FixedLabel" position="193,284" size="20,20" transparent="1" zPosition="4" text="B" foregroundColor="#00aa00" backgroundColor="black" font="Regular;18" halign="center">\n\t\t\t\t<convert type="FrontendInfo">NUMBER</convert>\n\t\t\t\t<convert type="ValueRange">1,1</convert>\n\t\t\t\t<convert type="ConditionalShowHide" />\n\t\t\t  </widget>\n\t\t\t  \n\t\t\t  <widget source="session.FrontendInfo" render="FixedLabel" position="193,284" size="20,20" transparent="1" zPosition="4" text="C" foregroundColor="#00aa00" backgroundColor="black" font="Regular;18" halign="center">\n\t\t\t\t<convert type="FrontendInfo">NUMBER</convert>\n\t\t\t\t<convert type="ValueRange">2,2</convert>\n\t\t\t\t<convert type="ConditionalShowHide" />\n\t\t\t  </widget>\n\t\t\t  \n\t\t\t  <widget source="session.FrontendInfo" render="FixedLabel" position="193,284" size="20,20" transparent="1" zPosition="4" text="D" foregroundColor="#00aa00" backgroundColor="black" font="Regular;18" halign="center">\n\t\t\t\t<convert type="FrontendInfo">NUMBER</convert>\n\t\t\t\t<convert type="ValueRange">3,3</convert>\n\t\t\t\t<convert type="ConditionalShowHide" />\n\t\t\t  </widget>\n\t\t\t  <widget source="session.FrontendInfo" render="FixedLabel" position="193,284" size="20,20" transparent="1" zPosition="4" text="E" foregroundColor="#00aa00" backgroundColor="black" font="Regular;18" halign="center">\n\t\t\t\t<convert type="FrontendInfo">NUMBER</convert>\n\t\t\t\t<convert type="ValueRange">4,4</convert>\n\t\t\t\t<convert type="ConditionalShowHide" />\n\t\t\t  </widget>\t\t\t  \n\t\t\t  <widget source="session.FrontendInfo" render="FixedLabel" position="193,284" size="20,20" transparent="1" zPosition="4" text="F" foregroundColor="#00aa00" backgroundColor="black" font="Regular;18" halign="center">\n\t\t\t\t<convert type="FrontendInfo">NUMBER</convert>\n\t\t\t\t<convert type="ValueRange">5,5</convert>\n\t\t\t\t<convert type="ConditionalShowHide" />\n\t\t\t  </widget>\n\t\t\t  <widget source="session.FrontendInfo" render="FixedLabel" position="193,284" size="20,20" transparent="1" zPosition="4" text="G" foregroundColor="#00aa00" backgroundColor="black" font="Regular;18" halign="center">\n\t\t\t\t<convert type="FrontendInfo">NUMBER</convert>\n\t\t\t\t<convert type="ValueRange">6,6</convert>\n\t\t\t\t<convert type="ConditionalShowHide" />\n\t\t\t  </widget>\t\t\t  \n\t\t\t  \n\t\t\t  <widget source="session.CurrentService" render="Label" position="29,200" size="636,43" font="Regular; 16" valign="center" halign="left" foregroundColor="#999999" backgroundColor="black" transparent="1" noWrap="0">\n\t\t\t\t<convert type="PliExtraInfo">ServiceInfo</convert>\n\t\t\t  </widget>\n\t\t\t<!-- fin info canal-->\n\t\t\t\t<widget source="session.CurrentService" render="Label" position="223,285" size="304,20" transparent="1" zPosition="1" foregroundColor="#ffffff" font="Regular; 17" valign="center" halign="left">\n\t\t\t\t  <convert type="PliExtraInfo">PIDInfo</convert>\n\t\t\t\t</widget>\t    \t\t  \n\n\t\t\t\t<widget source="session.CurrentService" render="Label" position="133,316" size="522,26" transparent="1" zPosition="1" foregroundColor="#00ffffff" font="Regular; 16" valign="center" halign="left" backgroundColor="black">\n\t\t\t\t  <convert type="PliExtraInfo">CryptoBar</convert>\n\t\t\t\t</widget>\t\n\t\t\t\t<widget source="session.CurrentService" render="Label" position="133,346" size="522,26" transparent="1" zPosition="1" foregroundColor="#00ffffff" font="Regular;18" valign="center" halign="left">\n\t\t\t\t  <convert type="PliExtraInfo">CryptoSpecial</convert>\n\t\t\t\t</widget>\t\n\t\t\t<eLabel name="new eLabel" position="249,91" size="119,20" text="SNR(dB)" foregroundColor="#999999" transparent="1" halign="right" font="Regular; 16" backgroundColor="black" />\n\t\t\t<eLabel name="new eLabel" position="6,5" size="115,22" text="Channel" foregroundColor="#999999" transparent="1" halign="right" font="Regular; 16" backgroundColor="black" valign="center" />\t\t    \n\t\t\t<eLabel name="new eLabel" position="6,250" size="115,26" text="REF" foregroundColor="#999999" transparent="1" halign="right" font="Regular; 16" backgroundColor="black" valign="center" />\t\t    \n\n\t\t\t<eLabel name="new eLabel" position="6,282" size="115,26" text="%s" foregroundColor="#999999" transparent="1" halign="right" font="Regular; 16" backgroundColor="black" />\t\t    \n\t\t\t<eLabel name="new eLabel" position="6,175" size="115,24" text="%s" foregroundColor="#999999" transparent="1" halign="right" font="Regular; 16" backgroundColor="black" noWrap="1" />\t\t       \n\t\t\t<eLabel name="new eLabel" position="6,316" size="115,26" text="%s" foregroundColor="#999999" transparent="1" halign="right" font="Regular; 16" backgroundColor="#40444444" valign="center" />\t\t    \t\t    \n\t\t\t\t\t\n\t\t\t<eLabel name="linea" position="1,146" size="669,1" foregroundColor="#40444444" transparent="0" zPosition="20" backgroundColor="#30555555" />\n\t\t\t<eLabel name="fondolinea" position="1,147" size="669,22" foregroundColor="#40222222" transparent="0" zPosition="-1" backgroundColor="#35222222" />\n\t\t\t<widget name="farr" position="354,150" size="25,18" zPosition="10" pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/InfoSignal/flear-fs8.png" alphatest="blend" />\n\t\t\t<widget name="fabj" position="354,150" size="25,18" zPosition="10" pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/InfoSignal/fleab-fs8.png" alphatest="blend" />\n\t\t\t<ePixmap name="chmas" position="534,149" size="27,19" pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/InfoSignal/chmas.png" alphatest="blend" zPosition="20" />\n\t\t\t<ePixmap name="chmenos" position="564,149" size="27,19" pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/InfoSignal/chmenos.png" alphatest="blend" zPosition="20" />\n\t\t\t<ePixmap name="chok" position="594,149" size="27,19" pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/InfoSignal/ok.png" alphatest="blend" zPosition="20" />\n\t\t\t<ePixmap name="chmover" position="634,149" size="27,19" pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/InfoSignal/mover.png" alphatest="blend" zPosition="20" />\n\t\t\t<ePixmap name="fondop1" position="134,33" size="456,26" pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/InfoSignal/fp-fs8.png" alphatest="blend" zPosition="50" />\n\t\t\t<ePixmap name="fondop2" position="134,65" size="456,26" pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/InfoSignal/fp-fs8.png" alphatest="blend" zPosition="50" />\n\t\t\t<ePixmap name="fondop3" position="134,115" size="456,26" pixmap="/usr/lib/enigma2/python/Plugins/SystemPlugins/InfoSignal/fp-fs8.png" alphatest="blend" zPosition="50" />\n\t\t\t<widget name="fondosc" position="1,1" size="667,380" zPosition="-10" backgroundColor="#40000000" />\n\t\t\t<widget name="bordesc" position="0,0" size="669,382" zPosition="-11" backgroundColor="#40333333" />\n\t\t\t\t\t\t  <widget source="session.FrontendStatus" render="Label" position="383,317" size="272,22" font="Regular; 18" foregroundColor="#ff6600" backgroundColor="black" transparent="1" halign="right">\n\t\t\t\t<convert type="FrontendInfo">STRING</convert>\n\t\t\t  </widget>\n\t\t</screen>\n\t\t' % (_('Quality'),
         _('Signal'),
         _('BER'),
         _('Tunner'),
         _('Information'),
         _('Crypto'))

    def __init__(self, session, servicelist = None):
        Screen.__init__(self, session)
        self['actions'] = ActionMap(['OkCancelActions',
         'ColorActions',
         'DirectionActions',
         'WizardActions',
         'EPGSelectActions',
         'InfobarActions',
         'ChannelSelectBaseActions'], {'cancel': self.Exit,
         'ok': self.selcanal,
         'nextBouquet': self.zapDown,
         'prevBouquet': self.zapUp,
         'right': self.zapDown,
         'left': self.zapUp,
         'down': self.amplia,
         'up': self.amplia,
         'yellow': self.chekaplay,
         'blue': self.zapini}, -1)
        self.servicelist = servicelist
        self.viendotv = True
        self.TimerTemp = eTimer()
        self.TimerTemp.callback.append(self.zapini)
        self.onLayoutFinish.append(self.inicia)
        self.ampliado = True
        self['farr'] = Pixmap()
        self['fabj'] = Pixmap()
        self['fondosc'] = Label()
        self['bordesc'] = Label()
        self.chekaplay()

    def amplia(self):
        tamx = fhd(669)
        tamy1 = fhd(382)
        tamy2 = fhd(172)
        if self.ampliado:
            listsize = (tamx, tamy2)
            listsize2 = (tamx - 2, tamy2 - 2)
            self['farr'].hide()
            self['fabj'].show()
            self.ampliado = False
        else:
            listsize = (tamx, tamy1)
            listsize2 = (tamx - 2, tamy1 - 2)
            self['farr'].show()
            self['fabj'].hide()
            self.ampliado = True
        self.instance.resize(eSize(*listsize))
        self['bordesc'].instance.resize(eSize(*listsize))
        self['fondosc'].instance.resize(eSize(*listsize2))

    def chekaplay(self):
        ref = ''
        try:
            servicio = self.session.nav.getCurrentlyPlayingServiceOrGroup()
            ref = servicio.toString()
            if ref == '':
                self.viendotv = False
                return
        except:
            self.viendotv = False
            return

        if len(ref) <= len(':0:0:0:0:0'):
            self.viendotv = False
            return
        if ref.startswith('1:0:0:'):
            self.viendotv = False
            return
        self.viendotv = True

    def inicia(self):
        if self.servicelist:
            self.TimerTemp.start(600, True)
        self['fabj'].hide()

    def tempred(self):
        try:
            self.zapUp()
            self.zapDown()
        except:
            pass

    def zapini(self):
        if not self.viendotv:
            return
        try:
            servicio = self.session.nav.getCurrentlyPlayingServiceOrGroup()
            self.session.nav.playService(None)
            self.servicelist.zap()
        except:
            pass

    def selcanal(self):
        if not self.viendotv:
            return
        if self.servicelist:
            self.session.execDialog(self.servicelist)

    def Exit(self):
        self.close()

    def zapUp(self):
        if not self.viendotv:
            return
        if not self.servicelist:
            return
        if self.servicelist.inBouquet():
            prev = self.servicelist.getCurrentSelection()
            if prev:
                prev = prev.toString()
                while True:
                    if config.usage.quickzap_bouquet_change.value:
                        if self.servicelist.atBegin():
                            self.servicelist.prevBouquet()
                    self.servicelist.moveUp()
                    cur = self.servicelist.getCurrentSelection()
                    if not cur or not cur.flags & 64 or cur.toString() == prev:
                        break

        else:
            self.servicelist.moveUp()
        self.servicelist.zap()

    def zapDown(self):
        if not self.viendotv:
            return
        if not self.servicelist:
            return
        if self.servicelist.inBouquet():
            prev = self.servicelist.getCurrentSelection()
            if prev:
                prev = prev.toString()
                while True:
                    if config.usage.quickzap_bouquet_change.value and self.servicelist.atEnd():
                        self.servicelist.nextBouquet()
                    else:
                        self.servicelist.moveDown()
                    cur = self.servicelist.getCurrentSelection()
                    if not cur or not cur.flags & 64 or cur.toString() == prev:
                        break

        else:
            self.servicelist.moveDown()
        self.servicelist.zap()


def main(session, **kwargs):
    from Screens.InfoBar import InfoBar
    if InfoBar and InfoBar.instance:
        session.open(InfoSignal, InfoBar.instance.servicelist)
    else:
        session.open(InfoSignal)


def infoSignalMenu(menuid, **kwargs):
    if menuid == 'scan':
        return [(_('Tunner signal information'),
          main,
          'InfoSignal',
          1)]
    else:
        return []


def Plugins(path, **kwargs):
    plugin_list = [PluginDescriptor(name=_('Tunner signal information'), where=PluginDescriptor.WHERE_MENU, needsRestart=False, fnc=infoSignalMenu)]
    return plugin_list
