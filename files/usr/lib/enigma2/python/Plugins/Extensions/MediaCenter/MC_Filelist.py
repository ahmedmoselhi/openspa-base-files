from Components.MenuList import MenuList
from Components.Harddisk import harddiskmanager
from Components.MultiContent import MultiContentEntryText, MultiContentEntryProgress, MultiContentEntryPixmapAlphaBlend
from Tools.Directories import SCOPE_CURRENT_SKIN, SCOPE_SKIN_IMAGE, resolveFilename, fileExists
from ServiceReference import ServiceReference
from enigma import RT_HALIGN_LEFT, RT_VALIGN_CENTER, RT_HALIGN_RIGHT, RT_HALIGN_CENTER, BT_SCALE, BT_KEEP_ASPECT_RATIO, eListboxPythonMultiContent, eServiceReference, eServiceCenter, gFont, iServiceInformation
from Tools.LoadPixmap import LoadPixmap
from Components.config import *
from os import environ
import gettext
from Components.Language import language
from Tools.Directories import SCOPE_PLUGINS, SCOPE_LANGUAGE
from Plugins.Extensions.spazeMenu.plugin import esHD, fhd
lang = language.getLanguage()
environ['LANGUAGE'] = lang[:2]
gettext.bindtextdomain('enigma2', resolveFilename(SCOPE_LANGUAGE))
gettext.textdomain('enigma2')
gettext.bindtextdomain('AZ_MRUAvideoinfo', '%s%s' % (resolveFilename(SCOPE_PLUGINS), 'Extensions/MediaCenter/locale/'))
config.plugins.mc_fl = ConfigSubsection()
config.plugins.mc_fl.orden = ConfigText(default='2')
config.plugins.mc_fl.ordenmi = ConfigText(default='1')

def _(txt):
    t = gettext.dgettext('AZ_MRUAvideoinfo', txt)
    if t == txt:
        t = gettext.gettext(txt)
    return t


tipolista = 'novideo'
ordenmaster = '1'
EXTENSIONS = {'m4a': 'music',
 'mp2': 'music',
 'mp3': 'music',
 'wav': 'music',
 'ogg': 'music',
 'flac': 'music',
 'jpg': 'picture',
 'jpeg': 'picture',
 'png': 'picture',
 'bmp': 'picture',
 'ts': 'record',
 'avi': 'movie',
 'divx': 'movie',
 'm4v': 'movie',
 'mpg': 'movie',
 'mpeg': 'movie',
 'mkv': 'movie',
 'mp4': 'movie',
 'mov': 'movie',
 'iso': 'movie',
 'wmv': 'movie',
 'm2ts': 'movie',
 'vob': 'movie',
 'flv': 'movie',
 'm3u': 'container',
 'pls': 'container',
 'e2pls': 'container'}
import time
import stat
import os
from enigma import eEnv

def formateafecha(lafecha = None, sepa = '-', corta = False, hora = False):
    if not lafecha == None:
        t2 = lafecha
    else:
        t2 = time.localtime()
    t3 = time.localtime()
    cdia = str(time.strftime('%d', t2))
    cmes = str(time.strftime('%B', t2))
    cano = str(time.strftime('%Y', t2))
    xhoy = str(time.strftime('%d', t3)) + str(time.strftime('%B', t3)) + str(time.strftime('%Y', t3))
    xay = str(int(time.strftime('%d', t3)) - 1) + str(time.strftime('%B', t3)) + str(time.strftime('%Y', t3))
    if cdia + cmes + cano == xhoy:
        csemana = _('Today') + ' ' + _(str(time.strftime('%A', t2)))
    elif cdia + cmes + cano == xay:
        csemana = _('Yesterday') + ' ' + _(str(time.strftime('%A', t2)))
    else:
        csemana = _(str(time.strftime('%A', t2)))
    chora = ''
    if hora:
        chora = ' ' + str(time.strftime('%H:%M', t2))
    if corta:
        cmes = _(cmes)
        cmes = cmes[0:3]
        csemana = _(csemana)
        csemana = csemana[0:3]
        return cdia + sepa + cmes + sepa + cano + chora
    else:
        return _(csemana) + ', ' + cdia + sepa + _(cmes) + sepa + cano + chora


def ajustatam(size):
    if size < 1024:
        humansize = str(size) + ' bytes'
    elif size < 1048576:
        humansize = '%.2f Kb' % (float(size) / 1024)
    elif size < 1073741824:
        humansize = '%.2f Mb' % (float(size) / 1048576)
    else:
        humansize = '%.2f Gb' % (float(size) / 1073741824)
    return humansize


def sizeof_fmt(num):
    for x in ['B',
     'KB',
     'MB',
     'GB',
     'TB']:
        if num < 1024.0:
            return '%3.1f%s' % (num, x)
        num /= 1024.0


def setResumePoint(session, end = False):
    global resumePointCache
    ref = session.nav.getCurrentlyPlayingServiceOrGroup()
    key = ref.getName()
    lru = int(time.time())
    service = session.nav.getCurrentService()
    if service is not None:
        seek = service.seek()
    if seek:
        pos = seek.getPlayPosition()
        if not pos[0]:
            l = seek.getLength()
            if l:
                l = l[1]
            else:
                l = None
            if end:
                position = 0
            else:
                position = pos[1]
            resumePointCache[key] = [lru, position, l]
            saveResumePoints(ref)


def getResumePoint(ref):
    global resumePointCache
    resumePointCache = loadResumePoints(ref)
    if ref is not None:
        try:
            entry = resumePointCache[ref.getName()]
            entry[0] = int(time.time())
            last = entry[1]
            length = entry[2]
        except KeyError:
            last = None
            length = 0

    perc = 0
    if last is not None and float(length) > 0:
        perc = int(float(last) / 90000 / (float(length) / 90000) * 100)
        if perc > 100:
            perc = 100
        if perc < 0:
            perc = 0
    resumePointCacheLast = int(time.time())
    return (perc, last, length)


def saveResumePoints(ref):
    name = str(ref.getPath()) + '.rsp'
    import cPickle
    try:
        f = open(name, 'wb')
        cPickle.dump(resumePointCache, f, cPickle.HIGHEST_PROTOCOL)
    except Exception as ex:
        print '[InfoBar] Failed to write resumepoints:', ex


def loadResumePoints(ref):
    name = str(ref.getPath()) + '.rsp'
    import cPickle
    try:
        return cPickle.load(open(name, 'rb'))
    except Exception as ex:
        print '[InfoBar] Failed to load resumepoints:', ex
        return {}


resumePointCache = {}

def FileEntryComponent(name, absolute = None, isDir = False, seleccionados = [], esvideos = ''):
    rutapng = '/usr/lib/enigma2/python/Plugins/Extensions/MediaCenter/images/'
    res = [(absolute, isDir, name)]
    png = None
    txt = None
    if name == ' ..' or name == '..':
        res.append(MultiContentEntryText(pos=(fhd(50), fhd(6)), size=(fhd(760), fhd(50)), font=0, text='' + name + ''))
        if esvideos == 'video':
            png = LoadPixmap(cached=True, path=rutapng + 'back-fs8.png')
            res.append(MultiContentEntryPixmapAlphaBlend(pos=(fhd(873), fhd(13)), size=(fhd(35), fhd(25)), png=png, flags=BT_SCALE | BT_KEEP_ASPECT_RATIO))
        png = LoadPixmap(cached=True, path=rutapng + 'mc_up-fs8.png')
    else:
        try:
            name = name.decode('utf-8').encode('utf-8')
        except:
            try:
                name = name.decode('windows-1252').encode('utf-8')
            except:
                pass

        xfont = 0
        ypos = 5
        xpos = 50
        if isDir:
            xfont = 2
            ypos = 10
        else:
            extension = name.split('.')
            extension = extension[-1].lower()
            if EXTENSIONS.has_key(extension):
                if EXTENSIONS[extension] == 'movie' or EXTENSIONS[extension] == 'record':
                    rutacompleta = absolute.getPath()
                    xpos = xpos + 60
                    top = 14
                    perc, last, length = getResumePoint(absolute)
                    if (last == None or last == 0) and length > 0:
                        perc = 100
                    l = length / 90000
                    longi = '%d:%02d:%02d' % (l / 3600, l % 3600 / 60, l % 60)
                    if length == 0:
                        longi = ''
                    if perc == 0:
                        color = 16730684
                    elif perc > 84:
                        color = 3735368
                    else:
                        color = 16763904
                    l = (length - (last or 0)) / 90000
                    if l == 0 or perc == 100:
                        queda = ''
                    else:
                        queda = '-%d:%02d' % (l / 60, l % 60)
                    res.append(MultiContentEntryText(pos=(fhd(47), fhd(top - 9)), size=(fhd(58), fhd(40)), font=3, flags=RT_HALIGN_LEFT, text=longi, color=color))
                    res.append(MultiContentEntryProgress(pos=(fhd(50), fhd(top + 11)), size=(fhd(53), fhd(5)), percent=perc, borderWidth=1, foreColor=color))
                    res.append(MultiContentEntryText(pos=(fhd(47), fhd(top + 16)), size=(fhd(58), fhd(40)), font=3, flags=RT_HALIGN_CENTER, text=queda, color=color))
        res.append(MultiContentEntryText(pos=(fhd(xpos), fhd(ypos)), size=(fhd(690), fhd(50)), font=xfont, text='' + name + ''))
        if isDir:
            png = LoadPixmap(cached=True, path=rutapng + 'mc_folder-fs8.png')
        elif EXTENSIONS.has_key(extension):
            try:
                rutacompleta = absolute.getPath()
                if rutacompleta.endswith('.ts'):
                    serviceref = eServiceReference('1:0:0:0:0:0:0:0:0:0:' + rutacompleta)
                    serviceHandler = eServiceCenter.getInstance()
                    info = serviceHandler.info(serviceref)
                    evt = info.getEvent(serviceref)
                    if evt and info:
                        cuanto = info.getLength(serviceref)
                        txt = ''
                        try:
                            service = ServiceReference(info.getInfoString(serviceref, iServiceInformation.sServiceref))
                            txt = txt + service.getServiceName()
                        except:
                            pass

                        if cuanto:
                            txt = txt + ' - ' + '%d:%02d Min.' % (cuanto / 60, cuanto % 60)
                        hora = evt.getBeginTimeString()
                        if hora:
                            try:
                                txt = txt + ' - ' + hora.split(',')[1]
                            except:
                                pass

            except:
                pass

            laext = EXTENSIONS[extension]
            if txt:
                extension = txt
            else:
                extension = '[' + _('File') + ' ' + str(extension).upper() + ']'
            res.append(MultiContentEntryText(pos=(fhd(xpos + 8), fhd(25)), size=(fhd(980), fhd(40)), font=1, flags=RT_HALIGN_LEFT, text='' + str(extension) + '', color=8947848))
            png = LoadPixmap(cached=True, path=rutapng + 'mc_' + laext + '-fs8.png')
        else:
            png = None
        fecha = ''
        if not isDir:
            try:
                size = os_path.getsize(absolute.getPath())
                humansize = ajustatam(size)
                res.append(MultiContentEntryText(pos=(fhd(785), fhd(5)), size=(fhd(120), fhd(40)), font=0, flags=RT_HALIGN_RIGHT, text='' + humansize + ' '))
            except:
                pass

            try:
                realruta = absolute.getPath()
                if os.path.exists(realruta):
                    dir_stats = os.stat(realruta)
                    lafecha = formateafecha(time.localtime(dir_stats.st_mtime))
                    res.append(MultiContentEntryText(pos=(fhd(492), fhd(25)), size=(fhd(415), fhd(40)), font=1, flags=RT_HALIGN_RIGHT, text='' + lafecha + '', color=8947848))
            except:
                pass

    if png is not None:
        xpos = 11
        if isDir:
            xpos = 8
        res.append(MultiContentEntryPixmapAlphaBlend(pos=(fhd(xpos), fhd(9, 1.5)), size=(fhd(32), fhd(32)), png=png, flags=BT_SCALE | BT_KEEP_ASPECT_RATIO))
    try:
        rutacompleta = absolute.getPath()
        if fileExists(rutacompleta) and rutacompleta in seleccionados:
            if esvideos == 'video':
                png = LoadPixmap(cached=True, path=rutapng + 'plcheck-fs8.png')
                res.append(MultiContentEntryPixmapAlphaBlend(pos=(fhd(3), fhd(3)), size=(fhd(26), fhd(25)), png=png, flags=BT_SCALE | BT_KEEP_ASPECT_RATIO))
            else:
                png = LoadPixmap(cached=True, path=rutapng + 'au_play.png')
                res.append(MultiContentEntryPixmapAlphaBlend(pos=(fhd(30), fhd(20)), size=(fhd(20), fhd(20)), png=png, flags=BT_SCALE | BT_KEEP_ASPECT_RATIO))
    except:
        pass

    return res


class FileList(MenuList):

    def __init__(self, directory, showDirectories = True, showFiles = True, showMountpoints = True, matchingPattern = None, useServiceRef = False, inhibitDirs = False, inhibitMounts = False, isTop = False, enableWrapAround = False, additionalExtensions = None):
        MenuList.__init__(self, list, enableWrapAround, eListboxPythonMultiContent)
        self.lista = []
        self.additional_extensions = additionalExtensions
        self.mountpoints = []
        self.tipo = 'novideo'
        if matchingPattern == None:
            self.tipo = 'novideo'
        elif 'mkv' in matchingPattern:
            self.tipo = 'video'
        else:
            self.tipo = 'novideo'
        self.current_directory = None
        self.current_mountpoint = None
        self.useServiceRef = useServiceRef
        self.showDirectories = showDirectories
        self.showMountpoints = showMountpoints
        self.showFiles = showFiles
        self.isTop = isTop
        self.matchingPattern = matchingPattern
        self.inhibitDirs = inhibitDirs or []
        self.inhibitMounts = inhibitMounts or []
        self.savedisodir = None
        self.savedisoselec = None
        self.refreshMountpoints()
        self.changeDir(directory)
        self.l.setFont(0, gFont('Regular', 19))
        self.l.setFont(1, gFont('Regular', 18))
        self.l.setFont(2, gFont('Regular', 20))
        self.l.setFont(3, gFont('Regular', 15))
        self.l.setItemHeight(fhd(50))
        self.serviceHandler = eServiceCenter.getInstance()

    def limpiaRlista(self):
        self.lista = []

    def actualizarVista(self):
        num = self.l.getCurrentSelectionIndex()
        self.changeDir(self.current_directory)
        if num is not None and num >= 0:
            self.moveToIndex(num)

    def anadeSeleccion(self, cualo = None):
        self.lista = []
        num = self.l.getCurrentSelectionIndex()
        if cualo != None:
            self.lista.append(cualo)
        self.changeDir(self.current_directory)
        self.moveToIndex(num)

    def anadeRlista(self, cualo, actualizar = True):
        if actualizar:
            num = self.l.getCurrentSelectionIndex()
        self.lista.append(cualo)
        if actualizar:
            self.changeDir(self.current_directory)
            self.moveToIndex(num)

    def borraRlista(self, cualo, actualizar = True):
        if actualizar:
            num = self.l.getCurrentSelectionIndex()
        self.lista.remove(cualo)
        if actualizar:
            self.changeDir(self.current_directory)

    def devRlista(self):
        return self.lista

    def setOrden(self, cualo):
        ordenfl = str(cualo)
        if self.tipo == 'video':
            try:
                config.plugins.mc_fl.orden.value = ordenfl
                config.plugins.mc_fl.orden.save()
                config.plugins.mc_fl.save()
            except:
                pass

        else:
            try:
                config.plugins.mc_fl.ordenmi.value = ordenfl
                config.plugins.mc_fl.ordenmi.save()
                config.plugins.mc_fl.save()
            except:
                pass

    def getOrden(self):
        if self.tipo == 'video':
            return config.plugins.mc_fl.orden.value
        else:
            return config.plugins.mc_fl.ordenmi.value

    def bySizeFunc(self, a, b):
        try:
            stat1 = os.stat(self.current_directory + a[0][2])
            stat2 = os.stat(self.current_directory + b[0][2])
        except:
            return 0

        if b[0][1] or a[0][1]:
            return cmp(a[1][7], b[1][7]) + 10000
        else:
            return cmp(stat2.st_size, stat1.st_size)

    def sortSize(self, mover = True):
        self.list.sort(self.bySizeFunc)
        self.l.setList(self.list)
        if mover:
            self.moveToIndex(0)

    def byNameFunc(self, a, b):
        if b[0][1] or a[0][1]:
            return cmp(a[1][7].lower(), b[1][7].lower()) + 10000
        else:
            return cmp(a[1][7].lower(), b[1][7].lower())

    def sortName(self, mover = True):
        self.list.sort(self.byNameFunc)
        self.l.setList(self.list)
        if mover:
            self.moveToIndex(0)

    def byDateFunc(self, a, b):
        try:
            stat1 = os.stat(self.current_directory + a[0][2])
            stat2 = os.stat(self.current_directory + b[0][2])
        except:
            return 0

        if b[0][1] or a[0][1]:
            return cmp(a[1][7], b[1][7]) + 10000
        else:
            return cmp(stat2.st_ctime, stat1.st_ctime)

    def sortDate(self, mover = True):
        self.list.sort(self.byDateFunc)
        self.l.setList(self.list)
        if mover:
            self.moveToIndex(0)

    def refreshMountpoints(self):
        self.mountpoints = [ os_path.join(p.mountpoint, '') for p in harddiskmanager.getMountedPartitions() ]
        self.mountpoints.sort(reverse=True)

    def getMountpoint(self, file):
        file = os_path.join(os_path.realpath(file), '')
        for m in self.mountpoints:
            if file.startswith(m):
                return m

        return False

    def getMountpointLink(self, file):
        if os_path.realpath(file) == file:
            return self.getMountpoint(file)
        else:
            if file[-1] == '/':
                file = file[:-1]
            mp = self.getMountpoint(file)
            last = file
            file = os_path.dirname(file)
            while last != '/' and mp == self.getMountpoint(file):
                last = file
                file = os_path.dirname(file)

            return os_path.join(last, '')

    def getSelection(self):
        if self.l.getCurrentSelection() is None:
            return
        return self.l.getCurrentSelection()[0]

    def getCurrentEvent(self):
        l = self.l.getCurrentSelection()
        if not l or l[0][1] == True:
            return None
        else:
            return self.serviceHandler.info(l[0][0]).getEvent(l[0][0])

    def getFileList(self):
        return self.list

    def inParentDirs(self, dir, parents):
        dir = os_path.realpath(dir)
        for p in parents:
            if dir.startswith(p):
                return True

        return False

    def changeDir(self, directory, select = None, seleccionar = None):
        self.list = []
        if self.current_directory is None:
            if directory and self.showMountpoints:
                self.current_mountpoint = self.getMountpointLink(directory)
            else:
                self.current_mountpoint = None
        self.current_directory = directory
        directories = []
        files = []
        if directory is None and self.showMountpoints:
            for p in harddiskmanager.getMountedPartitions():
                path = os_path.join(p.mountpoint, '')
                if path not in self.inhibitMounts and not self.inParentDirs(path, self.inhibitDirs):
                    self.list.append(FileEntryComponent(name=p.description, absolute=path, isDir=True, esvideos=self.tipo))

            if fileExists('/media/MediaServers'):
                try:
                    files = listdir('/media/MediaServers/')
                except:
                    files = []

                files.sort()
                for x in files:
                    if os_path.isdir('/media/MediaServers/' + x) and x[0] != '.':
                        path = os_path.join('/media/MediaServers/', x + '/')
                        self.list.append(FileEntryComponent(name=x, absolute=path, isDir=True, esvideos=self.tipo))

            files = []
            directories = []
        elif directory is None:
            files = []
            directories = []
        elif self.useServiceRef:
            root = eServiceReference('2:0:1:0:0:0:0:0:0:0:' + directory)
            if self.additional_extensions:
                root.setName(self.additional_extensions)
            serviceHandler = eServiceCenter.getInstance()
            list = serviceHandler.list(root)
            while 1:
                s = list.getNext()
                if not s.valid():
                    del list
                    break
                if s.flags & s.mustDescent:
                    directories.append(s.getPath())
                else:
                    files.append(s)

            directories.sort()
            files.sort()
        elif fileExists(directory):
            try:
                files = listdir(directory)
            except:
                files = []

            files.sort()
            tmpfiles = files[:]
            for x in tmpfiles:
                if os_path.isdir(directory + x):
                    directories.append(directory + x + '/')
                    files.remove(x)

        if directory is not None and self.showDirectories and not self.isTop:
            if directory == self.current_mountpoint and self.showMountpoints:
                self.list.append(FileEntryComponent(name=' ..', absolute=None, isDir=True, esvideos=self.tipo))
            elif directory != '/' and not (self.inhibitMounts and self.getMountpoint(directory) in self.inhibitMounts):
                self.list.append(FileEntryComponent(name=' ..', absolute='/'.join(directory.split('/')[:-2]) + '/', isDir=True, esvideos=self.tipo))
        if self.showDirectories:
            for x in directories:
                if not (self.inhibitMounts and self.getMountpoint(x) in self.inhibitMounts) and not self.inParentDirs(x, self.inhibitDirs):
                    name = x.split('/')[-2]
                    if name[0] != '.':
                        self.list.append(FileEntryComponent(name=name, absolute=x, isDir=True, esvideos=self.tipo))

        if self.showFiles:
            for x in files:
                if self.useServiceRef:
                    path = x.getPath()
                    name = path.split('/')[-1]
                else:
                    path = directory + x
                    name = x
                    x = eServiceReference(4097, 0, path)
                if self.matchingPattern is None or path.split('.')[-1] in self.matchingPattern:
                    if seleccionar is not None:
                        try:
                            rutacompleta = x.getPath()
                            if fileExists(rutacompleta) and rutacompleta not in self.lista:
                                self.lista.append(rutacompleta)
                        except:
                            pass

                    self.list.append(FileEntryComponent(name=name, absolute=x, isDir=False, seleccionados=self.lista, esvideos=self.tipo))

        if self.showMountpoints and len(self.list) == 0:
            self.list.append(FileEntryComponent(name=_('nothing connected'), absolute=None, isDir=False, esvideos=self.tipo))
        self.l.setList(self.list)
        if select is not None:
            i = 0
            self.moveToIndex(0)
            for x in self.list:
                p = x[0][0]
                if isinstance(p, eServiceReference):
                    p = p.getPath()
                if p == select:
                    self.moveToIndex(i)
                i += 1

        elorden = self.getOrden()
        if elorden == '2':
            self.sortDate(False)
        elif elorden == '1':
            self.sortName(False)
        elif elorden == '3':
            self.sortSize(False)

    def getCurrentDirectory(self):
        return self.current_directory

    def canDescent(self):
        if self.getSelection() is None:
            return False
        return self.getSelection()[1]

    def descent(self):
        if self.getSelection() is None:
            return
        if self.current_directory == '/tmp/discmount/' and self.getSelection()[0] == '/tmp/':
            self.changeDir(self.savedisodir, select=self.savedisoselec)
        else:
            self.changeDir(self.getSelection()[0], select=self.current_directory)

    def gotoParent(self):
        if self.current_directory is not None:
            if self.current_directory == '/tmp/discmount/':
                self.changeDir(self.savedisodir, select=self.savedisoselec)
            else:
                if self.current_directory == self.current_mountpoint and self.showMountpoints:
                    absolute = None
                else:
                    absolute = '/'.join(self.current_directory.split('/')[:-2]) + '/'
                self.changeDir(absolute, select=self.current_directory)

    def getName(self):
        if self.getSelection() is None:
            return False
        return self.getSelection()[2]

    def getFilename(self):
        if self.getSelection() is None:
            return
        x = self.getSelection()[0]
        if isinstance(x, eServiceReference):
            x = x.getPath()
        return x

    def getServiceRef(self):
        if self.getSelection() is None:
            return
        x = self.getSelection()[0]
        if isinstance(x, eServiceReference):
            return x

    def execBegin(self):
        harddiskmanager.on_partition_list_change.append(self.partitionListChanged)

    def execEnd(self):
        harddiskmanager.on_partition_list_change.remove(self.partitionListChanged)

    def refresh(self):
        self.changeDir(self.current_directory, self.getFilename())

    def partitionListChanged(self, action, device):
        self.refreshMountpoints()
        if self.current_directory is None:
            self.refresh()

    def setIsoDir(self, filename, filedir):
        self.savedisodir = filedir
        self.savedisoselec = filename


def MultiFileSelectEntryComponent(name, absolute = None, isDir = False, selected = False):
    res = [(absolute,
      isDir,
      selected,
      name)]
    res.append((eListboxPythonMultiContent.TYPE_TEXT,
     55,
     1,
     470,
     20,
     0,
     RT_HALIGN_LEFT,
     name))
    if isDir:
        png = LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_SKIN, 'extensions/directory.png'))
    else:
        extension = name.split('.')
        extension = extension[-1].lower()
        if EXTENSIONS.has_key(extension):
            png = LoadPixmap(resolveFilename(SCOPE_CURRENT_SKIN, 'extensions/' + EXTENSIONS[extension] + '.png'))
        else:
            png = None
    if png is not None:
        res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHATEST,
         30,
         2,
         20,
         20,
         png))
    if not name.startswith('<'):
        if selected is False:
            icon = LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_SKIN, 'skin_default/icons/lock_off.png'))
            res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHATEST,
             2,
             0,
             25,
             25,
             icon))
        else:
            icon = LoadPixmap(cached=True, path=resolveFilename(SCOPE_CURRENT_SKIN, 'skin_default/icons/lock_on.png'))
            res.append((eListboxPythonMultiContent.TYPE_PIXMAP_ALPHATEST,
             2,
             0,
             25,
             25,
             icon))
    return res


class MultiFileSelectList(FileList):

    def __init__(self, preselectedFiles, directory, showMountpoints = False, matchingPattern = None, showDirectories = True, showFiles = True, useServiceRef = False, inhibitDirs = False, inhibitMounts = False, isTop = False, enableWrapAround = False, additionalExtensions = None):
        self.selectedFiles = preselectedFiles
        if self.selectedFiles is None:
            self.selectedFiles = []
        FileList.__init__(self, directory, showMountpoints=showMountpoints, matchingPattern=matchingPattern, showDirectories=showDirectories, showFiles=showFiles, useServiceRef=useServiceRef, inhibitDirs=inhibitDirs, inhibitMounts=inhibitMounts, isTop=isTop, enableWrapAround=enableWrapAround, additionalExtensions=additionalExtensions)
        self.changeDir(directory)
        self.tipo = 'novideo'
        self.l.setItemHeight(25)
        self.l.setFont(0, gFont('Regular', 20))
        self.onSelectionChanged = []

    def selectionChanged(self):
        for f in self.onSelectionChanged:
            f()

    def changeSelectionState(self):
        idx = self.l.getCurrentSelectionIndex()
        count = 0
        newList = []
        for x in self.list:
            if idx == count:
                if x[0][3].startswith('<'):
                    newList.append(x)
                else:
                    if x[0][1] is True:
                        realPathname = x[0][0]
                    else:
                        realPathname = self.current_directory + x[0][0]
                    if x[0][2] == True:
                        SelectState = False
                        for entry in self.selectedFiles:
                            if entry == realPathname:
                                self.selectedFiles.remove(entry)

                    else:
                        SelectState = True
                        alreadyinList = False
                        for entry in self.selectedFiles:
                            if entry == realPathname:
                                alreadyinList = True

                        if not alreadyinList:
                            self.selectedFiles.append(realPathname)
                    newList.append(MultiFileSelectEntryComponent(name=x[0][3], absolute=x[0][0], isDir=x[0][1], selected=SelectState))
            else:
                newList.append(x)
            count += 1

        self.list = newList
        self.l.setList(self.list)

    def getSelectedList(self):
        return self.selectedFiles

    def changeDir(self, directory, select = None):
        self.list = []
        if self.current_directory is None:
            if directory and self.showMountpoints:
                self.current_mountpoint = self.getMountpointLink(directory)
            else:
                self.current_mountpoint = None
        self.current_directory = directory
        directories = []
        files = []
        if directory is None and self.showMountpoints:
            for p in harddiskmanager.getMountedPartitions():
                path = os_path.join(p.mountpoint, '')
                if path not in self.inhibitMounts and not self.inParentDirs(path, self.inhibitDirs):
                    self.list.append(MultiFileSelectEntryComponent(name=p.description, absolute=path, isDir=True))

            files = []
            directories = []
        elif directory is None:
            files = []
            directories = []
        elif self.useServiceRef:
            root = eServiceReference('2:0:1:0:0:0:0:0:0:0:' + directory)
            if self.additional_extensions:
                root.setName(self.additional_extensions)
            serviceHandler = eServiceCenter.getInstance()
            list = serviceHandler.list(root)
            while 1:
                s = list.getNext()
                if not s.valid():
                    del list
                    break
                if s.flags & s.mustDescent:
                    directories.append(s.getPath())
                else:
                    files.append(s)

            directories.sort()
            files.sort()
        elif fileExists(directory):
            try:
                files = listdir(directory)
            except:
                files = []

            files.sort()
            tmpfiles = files[:]
            for x in tmpfiles:
                if os_path.isdir(directory + x):
                    directories.append(directory + x + '/')
                    files.remove(x)

        if directory is not None and self.showDirectories and not self.isTop:
            if directory == self.current_mountpoint and self.showMountpoints:
                self.list.append(MultiFileSelectEntryComponent(name='<' + _('List of Storage Devices') + '>', absolute=None, isDir=True))
            elif directory != '/' and not (self.inhibitMounts and self.getMountpoint(directory) in self.inhibitMounts):
                self.list.append(MultiFileSelectEntryComponent(name='<' + _('Parent Directory') + '>', absolute='/'.join(directory.split('/')[:-2]) + '/', isDir=True))
        if self.showDirectories:
            for x in directories:
                if not (self.inhibitMounts and self.getMountpoint(x) in self.inhibitMounts) and not self.inParentDirs(x, self.inhibitDirs):
                    name = x.split('/')[-2]
                    alreadySelected = False
                    for entry in self.selectedFiles:
                        if entry == x:
                            alreadySelected = True

                    if alreadySelected:
                        self.list.append(MultiFileSelectEntryComponent(name=name, absolute=x, isDir=True, selected=True))
                    else:
                        self.list.append(MultiFileSelectEntryComponent(name=name, absolute=x, isDir=True, selected=False))

        if self.showFiles:
            for x in files:
                if self.useServiceRef:
                    path = x.getPath()
                    name = path.split('/')[-1]
                else:
                    path = directory + x
                    name = x
                    x = eServiceReference(4097, 0, path)
                if self.matchingPattern is None or path.split('.')[-1] in self.matchingPattern:
                    alreadySelected = False
                    for entry in self.selectedFiles:
                        if os_path.basename(entry) == x:
                            alreadySelected = True

                    if alreadySelected:
                        self.list.append(MultiFileSelectEntryComponent(name=name, absolute=x, isDir=False, selected=True))
                    else:
                        self.list.append(MultiFileSelectEntryComponent(name=name, absolute=x, isDir=False, selected=False))

        self.l.setList(self.list)
        if select is not None:
            i = 0
            self.moveToIndex(0)
            for x in self.list:
                p = x[0][0]
                if isinstance(p, eServiceReference):
                    p = p.getPath()
                if p == select:
                    self.moveToIndex(i)
                i += 1

        elorden = self.getOrden()
        if elorden == '2':
            self.sortDate(False)
        elif elorden == '1':
            self.sortName(False)
        elif elorden == '3':
            self.sortSize(False)
