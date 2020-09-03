from re import compile as re_compile
from os import path as os_path, listdir, stat as os_stat
from Components.MenuList import MenuList
from Components.Harddisk import harddiskmanager
from Components.config import config
from Components.MultiContent import MultiContentEntryPixmapAlphaBlend
from enigma import RT_HALIGN_RIGHT, RT_HALIGN_LEFT, BT_SCALE, BT_KEEP_ASPECT_RATIO, eListboxPythonMultiContent, eServiceReference, eServiceCenter, gFont, iServiceInformation
from Tools.LoadPixmap import LoadPixmap
from Tools.Directories import fileExists, pathExists, resolveFilename, SCOPE_LANGUAGE, SCOPE_PLUGINS
from time import strftime as time_strftime
from time import localtime as time_localtime
from Plugins.Extensions.spazeMenu.plugin import esHD, fhd
import stat
import os
from Components.Language import language
from os import environ
import gettext
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


ordenmaster = '1'

def setOrden(cualo):
    global ordenmaster
    ordenmaster = str(cualo)


def getOrden():
    return ordenmaster


EXTENSIONS = {'cfg': 'config',
 'config': 'config',
 'conf': 'config',
 'txt': 'text',
 'log': 'text',
 'info': 'text',
 'xml': 'xml',
 'py': 'py',
 'mp2': 'music',
 'mp3': 'music',
 'wav': 'music',
 'ogg': 'music',
 'flac': 'music',
 'm4a': 'music',
 'jpg': 'picture',
 'jpeg': 'picture',
 'jpe': 'picture',
 'png': 'picture',
 'bmp': 'picture',
 'mvi': 'picture',
 'ts': 'movie',
 'm2ts': 'movie',
 'avi': 'movie',
 'divx': 'movie',
 'mpg': 'movie',
 'mpeg': 'movie',
 'mkv': 'movie',
 'mp4': 'movie',
 'mov': 'movie',
 'vob': 'movie',
 'ifo': 'movie',
 'iso': 'movie',
 'flv': 'movie',
 'ipk': 'package',
 'gz': 'package',
 'bz2': 'package',
 'sh': 'script'}

def readlinkabs(l):
    p = os.readlink(l)
    if os_path.isabs(p):
        return p
    return os_path.join(os_path.dirname(l), p)


def formateafecha(lafecha = None, sepa = '-', corta = True, hora = True):
    if not lafecha == None:
        t2 = lafecha
    else:
        t2 = time_localtime()
    cdia = str(time_strftime('%d', t2))
    cmes = str(time_strftime('%B', t2))
    cano = str(time_strftime('%Y', t2))
    csemana = str(time_strftime('%A', t2))
    chora = ''
    if hora:
        chora = ' ' + str(time_strftime('%H:%M', t2))
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


def devpermisos(valorper, reducido = False):
    mode = stat.S_IMODE(valorper)
    operms = str(oct(mode))
    operms = '(' + operms[1:] + ')'
    perms = ''
    for who in ('USR', 'GRP', 'OTH'):
        for what in ('R', 'W', 'X'):
            if mode & getattr(stat, 'S_I' + what + who):
                perms = perms + what.lower()
            else:
                perms = perms + '-'

        perms = perms + ' '

    if reducido == False:
        perms = perms + operms
    return perms


def FileEntryComponent(name, absolute = None, isDir = False, ericono = None, realruta = None, realenlace = None):
    res = [(absolute, isDir)]
    if ericono == 'disk':
        name = name.replace('External', _('External')).replace('Harddisk', _('Harddisk')).replace('Hard disk', _('Harddisk')) + '     ->' + absolute + ''
    try:
        name = name.decode('utf-8').encode('utf-8')
    except:
        try:
            name = name.decode('windows-1252').encode('utf-8')
        except:
            pass

    res.append((eListboxPythonMultiContent.TYPE_TEXT,
     fhd(30),
     fhd(2),
     fhd(570),
     fhd(22),
     0,
     RT_HALIGN_LEFT,
     name))
    if ericono is None:
        if isDir:
            png = LoadPixmap('/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/AzExplorer/res/dir.png')
        else:
            extension = name.split('.')
            extension = extension[-1].lower()
            if EXTENSIONS.has_key(extension):
                png = LoadPixmap('/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/AzExplorer/res/' + EXTENSIONS[extension] + '.png')
            else:
                png = LoadPixmap('/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/AzExplorer/res/file.png')
    else:
        png = LoadPixmap('/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/AzExplorer/res/' + ericono + '.png')
    if png is not None:
        res.append(MultiContentEntryPixmapAlphaBlend(pos=(fhd(5), fhd(3)), size=(fhd(20), fhd(20)), png=png, flags=BT_SCALE | BT_KEEP_ASPECT_RATIO))
    if realenlace is not None:
        rutafin = '->' + readlinkabs(realenlace)
        maxlon = 46
        if len(rutafin) > maxlon:
            rutafin = rutafin[:maxlon / 2 - 2] + '...' + rutafin[len(rutafin) - maxlon / 2:len(rutafin)]
        res.append((eListboxPythonMultiContent.TYPE_TEXT,
         fhd(570),
         fhd(2),
         fhd(500),
         fhd(22),
         0,
         RT_HALIGN_LEFT,
         rutafin))
    elif realruta is not None:
        if os.path.exists(realruta):
            dir_stats = os_stat(realruta)
            tamano = str(ajustatam(dir_stats.st_size)) + ''
            lafecha = formateafecha(time_localtime(dir_stats.st_mtime))
            permisos = devpermisos(dir_stats.st_mode, reducido=True)
            if not os_path.isdir(realruta):
                res.append((eListboxPythonMultiContent.TYPE_TEXT,
                 fhd(615),
                 fhd(2),
                 fhd(95),
                 fhd(22),
                 0,
                 RT_HALIGN_RIGHT,
                 tamano))
            res.append((eListboxPythonMultiContent.TYPE_TEXT,
             fhd(725),
             fhd(2),
             fhd(180),
             fhd(22),
             0,
             RT_HALIGN_LEFT,
             lafecha))
            res.append((eListboxPythonMultiContent.TYPE_TEXT,
             fhd(925),
             fhd(2),
             fhd(120),
             fhd(22),
             0,
             RT_HALIGN_LEFT,
             permisos))
    elif ericono == 'disk' and os.path.exists(absolute):
        stat = os.statvfs(absolute + '/')
        total = stat.f_bsize * stat.f_blocks
        free = (stat.f_bavail if stat.f_bavail != 0 else stat.f_bfree) * stat.f_bsize
        ocupado = total - stat.f_bsize * stat.f_bfree
        porcentaje = int(ocupado * 100 / total)
        tamano = str(ajustatam(total))
        res.append((eListboxPythonMultiContent.TYPE_TEXT,
         fhd(550),
         fhd(2),
         fhd(250),
         fhd(22),
         0,
         RT_HALIGN_RIGHT,
         tamano))
        imgprogreso = 'infoprogreso0-fs8'
        png = LoadPixmap('/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/AzExplorer/res/' + imgprogreso + '.png')
        res.append(MultiContentEntryPixmapAlphaBlend(pos=(fhd(805), fhd(7)), size=(fhd(100), fhd(13)), png=png, flags=BT_SCALE | BT_KEEP_ASPECT_RATIO))
        imgprogreso = 'infoprogreso1-fs8'
        png = LoadPixmap('/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/AzExplorer/res/' + imgprogreso + '.png')
        res.append(MultiContentEntryPixmapAlphaBlend(pos=(fhd(805), fhd(7)), size=(fhd(porcentaje), fhd(13)), png=png, flags=BT_SCALE | BT_KEEP_ASPECT_RATIO))
        libre = '' + str(ajustatam(free)) + ' ' + _('free')
        res.append((eListboxPythonMultiContent.TYPE_TEXT,
         fhd(912),
         fhd(2),
         fhd(300),
         fhd(22),
         0,
         RT_HALIGN_LEFT,
         libre))
    return res


class FileList(MenuList):

    def __init__(self, directory, showDirectories = True, showFiles = True, showMountpoints = True, matchingPattern = None, useServiceRef = False, inhibitDirs = False, inhibitMounts = False, isTop = False, enableWrapAround = True, additionalExtensions = None):
        global ordenmaster
        MenuList.__init__(self, list, enableWrapAround, eListboxPythonMultiContent)
        self.additional_extensions = additionalExtensions
        self.mountpoints = []
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
        self.refreshMountpoints()
        self.changeDir(directory)
        self.l.setFont(0, gFont('Regular', 18))
        self.l.setItemHeight(26)
        self.serviceHandler = eServiceCenter.getInstance()
        self.numdirs = 0
        self.numfiles = 0
        self.numsto = 0
        if config.plugins.azExplorer.orden.value == '0':
            ordenmaster = config.plugins.azExplorer.ultimoorden.value
        else:
            ordenmaster = config.plugins.azExplorer.orden.value

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

    def infostatus(self):
        if self.numsto > 0:
            lainfo = str(self.numsto)
            lainfo = lainfo + ' ' + _('Storage Device(s)') + ''
        else:
            lainfo = str(self.numdirs)
            lainfo = lainfo + ' ' + _('Directory') + '(s)'
            lainfo = lainfo + ', ' + str(self.numfiles)
            lainfo = lainfo + ' ' + _('File') + '(s)'
        return lainfo

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
        self.numsto = 0
        if directory is None and self.showMountpoints:
            for p in harddiskmanager.getMountedPartitions():
                path = os_path.join(p.mountpoint, '')
                if path not in self.inhibitMounts and not self.inParentDirs(path, self.inhibitDirs):
                    self.numsto = self.numsto + 1
                    ico = 'disk'
                    self.list.append(FileEntryComponent(name=p.description, absolute=path, isDir=True, ericono=ico))

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
        elif os_path.exists(directory):
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
                self.list.append(FileEntryComponent(name='<' + _('List of Storage Devices') + '>', absolute=None, isDir=True, ericono='disks'))
            elif directory != '/' and not (self.inhibitMounts and self.getMountpoint(directory) in self.inhibitMounts):
                self.list.append(FileEntryComponent(name='<' + _('Parent Directory') + '>', absolute='/'.join(directory.split('/')[:-2]) + '/', isDir=True, ericono='back'))
        if self.showDirectories:
            self.numdirs = 0
            for x in directories:
                if not (self.inhibitMounts and self.getMountpoint(x) in self.inhibitMounts) and not self.inParentDirs(x, self.inhibitDirs):
                    self.numdirs = self.numdirs + 1
                    name = x.split('/')[-2]
                    ico = None
                    longi = len(x) - 1
                    y = x[:longi]
                    eslink = None
                    if os_path.islink(y):
                        eslink = y
                        if os_path.exists(y):
                            ico = 'dirlink'
                        else:
                            ico = 'dirlinkb'
                    self.list.append(FileEntryComponent(name=name, absolute=x, isDir=True, ericono=ico, realruta=x, realenlace=eslink))

        if self.showFiles:
            self.numfiles = 0
            for x in files:
                if self.useServiceRef:
                    path = x.getPath()
                    name = path.split('/')[-1]
                else:
                    path = directory + x
                    name = x
                    nx = None
                    if config.plugins.azExplorer.MediaFilter.value == 'on':
                        nx = self.getTSInfo(path)
                        if nx is not None:
                            name = nx
                EXext = os_path.splitext(path)[1]
                EXext = EXext.replace('.', '')
                EXext = EXext.lower()
                if EXext == '':
                    EXext = 'nothing'
                if self.matchingPattern is None or EXext in self.matchingPattern:
                    self.numfiles = self.numfiles + 1
                    ico = None
                    eslink = None
                    if os_path.islink(path):
                        eslink = path
                        if os_path.exists(path):
                            ico = 'dirlink'
                        else:
                            ico = 'dirlinkb'
                    if nx is None:
                        self.list.append(FileEntryComponent(name=name, absolute=x, isDir=False, ericono=ico, realruta=path, realenlace=eslink))
                    else:
                        res = [(x, False)]
                        png = LoadPixmap('/usr/lib/enigma2/python/Plugins/Extensions/spazeMenu/spzPlugins/AzExplorer/res/movie.png')
                        res.append((eListboxPythonMultiContent.TYPE_TEXT,
                         fhd(40),
                         fhd(2),
                         fhd(1000),
                         fhd(22),
                         0,
                         RT_HALIGN_LEFT,
                         name + ' [' + self.getTSLength(path) + ']'))
                        res.append(MultiContentEntryPixmapAlphaBlend(pos=(fhd(12), fhd(3)), size=(fhd(20), fhd(20)), png=png, flags=BT_SCALE | BT_KEEP_ASPECT_RATIO))
                        self.list.append(res)

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

        if ordenmaster == '2':
            self.sortDate(False)
        elif ordenmaster == '1':
            self.sortName(False)
        elif ordenmaster == '3':
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
        self.changeDir(self.getSelection()[0], select=self.current_directory)

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

    def getTSInfo(self, path):
        if path.endswith('.ts'):
            serviceref = eServiceReference('1:0:0:0:0:0:0:0:0:0:' + path)
            if not serviceref.valid():
                return
            serviceHandler = eServiceCenter.getInstance()
            info = serviceHandler.info(serviceref)
            if info is not None:
                txt = info.getName(serviceref)
                description = info.getInfoString(serviceref, iServiceInformation.sDescription)
                if not txt.endswith('.ts'):
                    if description is not '':
                        return txt + ' - ' + description
                    else:
                        return txt
                else:
                    evt = info.getEvent(serviceref)
                    if evt:
                        return evt.getEventName() + ' - ' + evt.getShortDescription()
                    else:
                        return

    def getTSLength(self, path):
        tslen = ''
        if path.endswith('.ts'):
            serviceref = eServiceReference('1:0:0:0:0:0:0:0:0:0:' + path)
            serviceHandler = eServiceCenter.getInstance()
            info = serviceHandler.info(serviceref)
            tslen = info.getLength(serviceref)
            if tslen > 0:
                tslen = '%d:%02d' % (tslen / 60, tslen % 60)
            else:
                tslen = ''
        return tslen

    def byNameFunc(self, a, b):
        return cmp(b[0][1], a[0][1]) or cmp(a[1][7], b[1][7])

    def sortName(self, mover = True):
        global ordenmaster
        ordenmaster = '1'
        self.list.sort(self.byNameFunc)
        self.l.setList(self.list)
        if mover:
            self.moveToIndex(0)

    def byDateFunc(self, a, b):
        try:
            stat1 = os_stat(self.current_directory + a[0][0])
            stat2 = os_stat(self.current_directory + b[0][0])
        except:
            return 0

        return cmp(b[0][1], a[0][1]) or cmp(stat2.st_ctime, stat1.st_ctime)

    def sortDate(self, mover = True):
        global ordenmaster
        ordenmaster = '2'
        self.list.sort(self.byDateFunc)
        self.l.setList(self.list)
        if mover:
            self.moveToIndex(0)

    def bySizeFunc(self, a, b):
        try:
            stat1 = os_stat(self.current_directory + a[0][0])
            stat2 = os_stat(self.current_directory + b[0][0])
        except:
            return 0

        return cmp(b[0][1], a[0][1]) or cmp(stat2.st_size, stat1.st_size)

    def sortSize(self, mover = True):
        global ordenmaster
        ordenmaster = '3'
        self.list.sort(self.bySizeFunc)
        self.l.setList(self.list)
        if mover:
            self.moveToIndex(0)
