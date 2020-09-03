from Plugins.Plugin import PluginDescriptor
from Screens.MessageBox import MessageBox
from Screens.ServiceStopScreen import ServiceStopScreen
from Components.ActionMap import ActionMap
from Components.Button import Button
from Components.Sources.List import List
from enigma import eTimer, fbClass, eRCInput
import os
from Tools.Directories import resolveFilename, SCOPE_PLUGINS
from xml.dom import minidom
from xml.dom.minidom import Document
import urllib

SKINPATH = resolveFilename(SCOPE_PLUGINS)+"Extensions/SNESManager/skins/"
XMLURL = "http://cam4me.org/ROMS/main.xml"
DATAURL = "http://cam4me.org/ROMS/"
DATAPATH = "/smc/"
RUNSC = "/usr/bin/snes_run.sh"

def SNESEntryComponent(entry):
	return (entry, entry['name'])

def takeskin(what):
	fp = open(SKINPATH+what)
	skin = fp.read()
	fp.close()
	return skin

class SNESInstall(Screen):
	def __init__(self, session, list_installed):
		self.skin = takeskin("SNESInstall")
		Screen.__init__(self, session)
		self.setTitle(_('SNES Manager'))
		self.list_installed = list_installed
		self.list = []
		self["images"] = List(self.list)
		self["key_red"] = Button(_('Exit'))
		self["key_green"] = Button(_('Install'))
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
		{
			"cancel": self.keyCancel,
			"red": self.keyCancel,
			"green": self.keyInstall
		}, -2)

		self.timer = eTimer()
		self.timer.callback.append(self.start)
		self.timer.start(100) 

	def start(self):
		self.timer.stop() 
		self.messagebox = self.session.open(MessageBox, _('Please wait a moment'), MessageBox.TYPE_INFO, enable_input = False)
		self.timer = eTimer()
		self.timer.callback.append(self.updateList)
		self.timer.start(100) 

	def updateList(self):
		self.timer.stop() 
		snesxml = minidom.parse(urllib.urlopen(XMLURL))
		list = []
		for emu in snesxml.firstChild.childNodes:
			if emu.nodeType == emu.ELEMENT_NODE and emu.localName == "file":
				name = emu.getElementsByTagName("name")[0]
				stype = emu.getElementsByTagName("type")[0]
				extension = emu.getElementsByTagName("extension")[0]
				version = emu.getElementsByTagName("version")[0]
				size = emu.getElementsByTagName("size")[0]
				modified = emu.getElementsByTagName("modified")[0]
				entry = {}
				entry['filename'] = name.firstChild and str(name.firstChild.data) or None
				entry['name'] = name.firstChild and str(name.firstChild.data) or None
				if entry['name'].endswith('.smc'):
					entry['name'] = str(entry['name'][:-4])
				entry['type'] = stype.firstChild and str(stype.firstChild.data) or None
				entry['extension'] = extension.firstChild and str(extension.firstChild.data) or None
				entry['version'] = version.firstChild and str(version.firstChild.data) or None
				entry['size'] = size.firstChild and str(size.firstChild.data) or None
				entry['modified'] = modified.firstChild and str(modified.firstChild.data) or None
				entry['installed'] = False
				entry['installable'] = True
				if entry['filename'] not in self.list_installed:
					list.append(SNESEntryComponent(entry))
		self["images"].list = list
		self.messagebox.close() 

	def keyCancel(self):
		self.close()

	def keyInstall(self):
		self.messagebox = self.session.open(MessageBox, _('Installation in progress'), MessageBox.TYPE_INFO, enable_input = False)
		self.timer = eTimer()
		self.timer.callback.append(self.installBackground)
		self.timer.start(100)

	def installBackground(self):
		self.timer.stop()
		entry = self["images"].getCurrent()[0]
		url = DATAURL + entry['filename']
		tmp = urllib.urlopen(url).read()
		out_file = open(DATAPATH + entry['filename'], "w")
		out_file.write(tmp)
		out_file.close()
		self.messagebox.close()
		self.close()

def excute_cmd(cmd):
	os.system(cmd)

class GoMain(Screen):
	def __init__(self, session, entry):
		skin = '<screen position="0,0" size="1280,720" title="" flags="wfNoBorder" backgroundColor="transparent" ></screen>' 
		self.skin = skin
		Screen.__init__(self, session) 
		self.entry = entry
		self['SnesAction'] = ActionMap(['SnesAction'],
		{
			'f4': self.keyCancel
		}, -1) 

		self.onLayoutFinish.append(self.go)

	def go(self):
		self.keyhandler = eTimer()
		self.keyhandler.callback.append(self.hkeys)
		self.keyhandler.start(100)
		excute_cmd(RUNSC + " \"" + DATAPATH + self.entry['filename']+ "\"")

	def keyCancel(self):
		self.close()

	def hkeys(self):
		self.keyhandler.stop()
		fbClass.getInstance().unlock()
		eRCInput.getInstance().unlock()
		self. keyCancel()

class SNESManager(Screen, ServiceStopScreen):
	def __init__(self, session):
		self.skin = takeskin("SNESManager")
		Screen.__init__(self, session)
		ServiceStopScreen.__init__(self)
		self.session = session
		self.setTitle(_('SNES Manager'))
		self.list_installed = []
		self["installedimages"] = List(self.list_installed)
		self["key_red"] = Button(_('Run'))
		self["key_green"] = Button(_('Remove'))
		self["key_yellow"] = Button(_('Install'))
		self["key_blue"] = Button(_('Exit'))
		self["actions"] = ActionMap(["OkCancelActions", "ColorActions"],
		{
			"cancel": self.keyCancel,
			"blue": self.keyCancel,
			"green": self.keyUninstall,
			"yellow": self.keyInstall,
			"red": self.keyRun,
			#"ok": self.keyRun
		}, -2)

		self.onLayoutFinish.append(self.updateList)

	def check_folder(self):
		if not os.path.exists(DATAPATH):
			try:
				os.mkdir(DATAPATH,0755)
			except:
				pass
		try:
			self.list_installed = os.listdir(DATAPATH)
		except:
			self.list_installed = []

	def readapp(self):
		self.check_folder()
		list = []
		for item in self.list_installed:
			entry = {}
			entry['filename'] = item
			entry['name'] = item
			if entry['name'].endswith('.smc'):
				entry['name'] = entry['name'][:-4]
			entry['type'] = None
			entry['extension'] = None
			entry['version'] = None
			entry['size'] = None
			entry['modified'] = None
			entry['installed'] = True
			entry['installable'] = False
			list.append(entry)
		list.sort()
		return list

	def updateList(self):
		self.list_installed = self.readapp()
		list = []
		for entry in self.list_installed:
			list.append(SNESEntryComponent(entry))
		self["installedimages"].list = list

	def keyCancel(self):
		self.close()

	def keyUninstall(self):
		entry = self["installedimages"].getCurrent()[0]
		self.session.openWithCallback(self.uninstallConfirm, MessageBox, _("Do you want to remove " + entry['name'] + "?"), MessageBox.TYPE_YESNO)

	def uninstallConfirm(self, confirmed):
		if confirmed:
			self.messagebox = self.session.open(MessageBox, _('Please wait a moment'), MessageBox.TYPE_INFO, enable_input = False)
			self.timer = eTimer()
			self.timer.callback.append(self.uninstallBackground)
			self.timer.start(100)

	def uninstallBackground(self):
		self.timer.stop()
		entry = self["installedimages"].getCurrent()[0]
		os.remove(DATAPATH + entry['filename'])
		self.messagebox.close()
		self.updateList()

	def keyInstall(self):
		self.session.openWithCallback(self.updateList, SNESInstall, self.list_installed)

	def keyRun(self):
		entry = self["installedimages"].getCurrent()[0]
		#if self.oldref == None:
		#	self.stopService()
		excute_cmd('snes_init') 
		excute_cmd('cp /etc/fb.snes /etc/fb.modes') 
		fbClass.getInstance().lock()
		eRCInput.getInstance().lock()
		self.session.openWithCallback(self.myback, GoMain, entry)
		excute_cmd('rm -R /etc/fb.modes')

	def myback(self):
		pass

def snestart(session, **kwargs):
	session.open(SNESManager)

def Plugins(**kwargs):
		return [PluginDescriptor(name="SNES Manager", description=_("Play with your SNES emulator!"), where=[PluginDescriptor.WHERE_PLUGINMENU], icon="plugin.png", fnc=snestart)]
