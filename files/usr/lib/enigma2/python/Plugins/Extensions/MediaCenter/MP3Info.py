import random
import re
import urllib, urllib2, os
from Tools.Directories import fileExists

def _from_synch_safe(synchsafe):
    if isinstance(synchsafe, type(1)):
        b3, b2, b1, b0 = struct.unpack('!4b', struct.pack('!1i', synchsafe))
    else:
        while len(synchsafe) < 4:
            synchsafe = (0,) + synchsafe

        b3, b2, b1, b0 = synchsafe
    x = 128
    return ((b3 * x + b2) * x + b1) * x + b0


def _strip_zero(s):
    start = 0
    while start < len(s) and (s[start] == '\x00' or s[start] == ' '):
        start = start + 1

    end = len(s) - 1
    while end >= 0 and (s[end] == '\x00' or s[end] == ' '):
        end = end - 1

    return s[start:end + 1]


def _stringclean(s):
    start = 0
    while start < len(s) and (s[start] < ' ' or s[start] > '}'):
        start = start + 1

    end = len(s) - 1
    return s[start:end + 1].replace('\x00', '')


class Error(Exception):
    pass


_known_bad_frames = ['\x00\x00MP',
 '\x00MP3',
 ' MP3',
 'MP3e',
 '\x00MP',
 ' MP',
 'MP3']

class ID3v2Frame:

    def __init__(self, file, version):
        self.name = ''
        self.version = 0
        self.padding = 0
        self.size = 0
        self.data = ''
        self.flags = {}
        self.f_tag_alter_preservation = 0
        self.f_file_alter_preservation = 0
        self.f_read_only = 0
        self.f_compression = 0
        self.f_encryption = 0
        self.f_grouping_identity = 0
        self.f_unsynchronization = 0
        self.f_data_length_indicator = 0
        if version == 2:
            nameSize = 3
        else:
            nameSize = 4
        self.name = file.read(nameSize)
        if self.name in _known_bad_frames:
            self.padding = 1
            return
        self.version = version
        if self.name == nameSize * '\x00':
            self.padding = 1
            return
        if self.name[0] < 'A' or self.name[0] > 'Z':
            self.padding = 1
            return
        size = ()
        if version == 2:
            size = struct.unpack('!3B', file.read(3))
            self.size = (size[0] * 256 + size[1]) * 256 + size[2]
        elif version == 3:
            size = struct.unpack('!L', file.read(4))
            self.size = size[0]
        elif version == 4:
            size = struct.unpack('!4B', file.read(4))
            self.size = _from_synch_safe(size)
        if version == 3:
            flags, = struct.unpack('!1b', file.read(1))
            self.f_tag_alter_preservation = flags >> 7 & 1
            self.f_file_alter_preservation = flags >> 6 & 1
            self.f_read_only = flags >> 5 & 1
            flags, = struct.unpack('!1b', file.read(1))
            self.f_compression = flags >> 7 & 1
            self.f_encryption = flags >> 6 & 1
            self.f_grouping_identity = flags >> 5 & 1
        elif version == 4:
            flags, = struct.unpack('!1b', file.read(1))
            self.f_tag_alter_preservation = flags >> 6 & 1
            self.f_file_alter_preservation = flags >> 5 & 1
            self.f_read_only = flags >> 4 & 1
            flags, = struct.unpack('!1b', file.read(1))
            self.f_grouping_identity = flags >> 6 & 1
            self.f_compression = flags >> 3 & 1
            self.f_encryption = flags >> 2 & 1
            self.f_unsynchronization = flags >> 1 & 1
            self.f_data_length_indicator = flags >> 0 & 1
        self.data = _strip_zero(file.read(self.size))


_genres = ['Blues',
 'Classic Rock',
 'Country',
 'Dance',
 'Disco',
 'Funk',
 'Grunge',
 'Hip-Hop',
 'Jazz',
 'Metal',
 'New Age',
 'Oldies',
 'Other',
 'Pop',
 'R&B',
 'Rap',
 'Reggae',
 'Rock',
 'Techno',
 'Industrial',
 'Alternative',
 'Ska',
 'Death Metal',
 'Pranks',
 'Soundtrack',
 'Euro-Techno',
 'Ambient',
 'Trip-Hop',
 'Vocal',
 'Jazz+Funk',
 'Fusion',
 'Trance',
 'Classical',
 'Instrumental',
 'Acid',
 'House',
 'Game',
 'Sound Clip',
 'Gospel',
 'Noise',
 'AlternRock',
 'Bass',
 'Soul',
 'Punk',
 'Space',
 'Meditative',
 'Instrumental Pop',
 'Instrumental Rock',
 'Ethnic',
 'Gothic',
 'Darkwave',
 'Techno-industrial',
 'Electronic',
 'Pop-Folk',
 'Eurodance',
 'Dream',
 'Southern Rock',
 'Comedy',
 'Cult',
 'Gangsta',
 'Top 40',
 'Christian Rap',
 'Pop/Funk',
 'Jungle',
 'Native American',
 'Cabaret',
 'New Wave',
 'Psychadelic',
 'Rave',
 'Showtunes',
 'Trailer',
 'Lo-Fi',
 'Tribal',
 'Acid Punk',
 'Acid Jazz',
 'Polka',
 'Retro',
 'Musical',
 'Rock & Roll',
 'Hard Rock',
 'Folk',
 'Folk/Rock',
 'National Folk',
 'Swing',
 'Fast-Fusion',
 'Bebob',
 'Latin',
 'Revival',
 'Celtic',
 'Bluegrass',
 'Avantegarde',
 'Gothic Rock',
 'Progressive Rock',
 'Psychedelic Rock',
 'Symphonic Rock',
 'Slow Rock',
 'Big Band',
 'Chorus',
 'Easy Listening',
 'Acoustic',
 'Humour',
 'Speech',
 'Chanson',
 'Opera',
 'Chamber Music',
 'Sonata',
 'Symphony',
 'Booty Bass',
 'Primus',
 'Porn Groove',
 'Satire',
 'Slow Jam',
 'Club',
 'Tango',
 'Samba',
 'Folklore',
 'Ballad',
 'Power Ballad',
 'Rythmic Soul',
 'Freestyle',
 'Duet',
 'Punk Rock',
 'Drum Solo',
 'A capella',
 'Euro-House',
 'Dance Hall',
 'Goa',
 'Drum & Bass',
 'Club House',
 'Hardcore',
 'Terror',
 'Indie',
 'BritPop',
 'NegerPunk',
 'Polsk Punk',
 'Beat',
 'Christian Gangsta',
 'Heavy Metal',
 'Black Metal',
 'Crossover',
 'Contemporary Christian',
 'Christian Rock',
 'Merengue',
 'Salsa',
 'Thrash Metal',
 'Anime',
 'JPop',
 'SynthPop']

class ID3v1:

    def __init__(self, file):
        self.valid = 0
        self.tags = {}
        try:
            file.seek(-128, 2)
        except IOError:
            pass

        data = file.read(128)
        if data[0:3] != 'TAG':
            return
        self.valid = 1
        self.tags['TT2'] = _strip_zero(data[3:33])
        self.tags['TP1'] = _strip_zero(data[33:63])
        self.tags['TAL'] = _strip_zero(data[63:93])
        self.tags['TYE'] = _strip_zero(data[93:97])
        self.tags['COM'] = _strip_zero(data[97:125])
        if data[125] == '\x00':
            self.tags['TRK'] = ord(data[126])
        try:
            self.tags['TCO'] = _genres[ord(data[127])]
        except IndexError:
            self.tags['TCO'] = None


class ID3v2:

    def __init__(self, file):
        self.valid = 0
        self.tags = {}
        self.header_size = 0
        self.major_version = 0
        self.minor_version = 0
        self.f_unsynchronization = 0
        self.f_extended_header = 0
        self.f_experimental = 0
        self.f_footer = 0
        self.f_extended_header_zie = 0
        self.f_extended_num_flag_bytes = 0
        self.ef_update = 0
        self.ef_crc = 0
        self.ef_restrictions = 0
        self.crc = 0
        self.restrictions = 0
        self.frames = []
        self.tags = {}
        file.seek(0, 0)
        if file.read(3) != 'ID3':
            return
        self.valid = 1
        self.major_version, self.minor_version = struct.unpack('!2b', file.read(2))
        flags, = struct.unpack('!1b', file.read(1))
        self.f_unsynchronization = flags >> 7 & 1
        self.f_extended_header = flags >> 6 & 1
        self.f_experimental = flags >> 5 & 1
        self.f_footer = flags >> 4 & 1
        self.header_size = _from_synch_safe(struct.unpack('!4b', file.read(4)))
        while 1:
            if file.tell() >= self.header_size:
                break
            frame = ID3v2Frame(file, self.major_version)
            if frame.padding:
                file.seek(self.header_size)
                break
            self.frames = self.frames + [frame]
            self.tags[frame.name] = frame.data


_bitrates = [[[0,
   32,
   48,
   56,
   64,
   80,
   96,
   112,
   128,
   144,
   160,
   176,
   192,
   224,
   256,
   None], [0,
   8,
   16,
   24,
   32,
   40,
   48,
   56,
   64,
   80,
   96,
   112,
   128,
   144,
   160,
   None], [0,
   8,
   16,
   24,
   32,
   40,
   48,
   56,
   64,
   80,
   96,
   112,
   128,
   144,
   160,
   None]], [[0,
   32,
   64,
   96,
   128,
   160,
   192,
   224,
   256,
   288,
   320,
   352,
   384,
   416,
   448,
   None], [0,
   32,
   48,
   56,
   64,
   80,
   96,
   112,
   128,
   160,
   192,
   224,
   256,
   320,
   384,
   None], [0,
   32,
   40,
   48,
   56,
   64,
   80,
   96,
   112,
   128,
   160,
   192,
   224,
   256,
   320,
   None]]]
_samplerates = [[11025,
  12000,
  8000,
  None],
 [None,
  None,
  None,
  None],
 [22050,
  24000,
  16000,
  None],
 [44100,
  48000,
  32000,
  None]]
_modes = ['stereo',
 'joint stereo',
 'dual channel',
 'mono']
_mode_extensions = [['4-31',
  '8-31',
  '12-31',
  '16-31'], ['4-31',
  '8-31',
  '12-31',
  '16-31'], ['',
  'IS',
  'MS',
  'IS+MS']]
_emphases = ['none',
 '50/15 ms',
 'reserved',
 'CCIT J.17']
_MP3_HEADER_SEEK_LIMIT = 500000

class MPEG:

    def __init__(self, file, seeklimit = _MP3_HEADER_SEEK_LIMIT, seekstart = 0):
        self.valid = 0
        file.seek(0, 2)
        self.filesize = file.tell()
        self.filesize2 = round(float(self.filesize / 1024 / 1024), 2)
        self.version = 0
        self.layer = 0
        self.protection = 0
        self.bitrate = 0
        self.is_vbr = 0
        self.samplerate = 0
        self.padding = 0
        self.private = 0
        self.mode = ''
        self.mode_extension = ''
        self.copyright = 0
        self.original = 0
        self.emphasis = ''
        self.length = 0
        self.length_minutes = 0
        self.length_seconds = 0
        self.total_time = 0
        test_pos = int(random.uniform(0.25, 0.75) * self.filesize)
        offset, header = self._find_header(file, seeklimit=4616, seekstart=test_pos, check_next_header=2)
        if offset == -1 or header is None:
            raise Error('Failed MPEG frame test.')
        offset, header = self._find_header(file, seeklimit, seekstart)
        if offset == -1 or header is None:
            raise Error('Could not find MPEG header')
        if not self.valid:
            raise Error('MPEG header not valid')
        self._parse_xing(file, seekstart, seeklimit)
        self.length_minutes = int(self.length / 60)
        self.length_seconds = int(round(self.length % 60))
        self.total_time = self.length

    def _find_header(self, file, seeklimit = _MP3_HEADER_SEEK_LIMIT, seekstart = 0, check_next_header = 1):
        amt = 5120
        curr_pos = 0
        read_more = 0
        file.seek(seekstart, 0)
        header = file.read(min(amt, seeklimit + 4))
        while curr_pos <= seeklimit:
            offset = string.find(header, chr(255), curr_pos)
            if offset == -1:
                curr_pos = len(header)
                read_more = 1
            elif offset + 4 > len(header):
                curr_pos = offset
                read_more = 1
            elif ord(header[offset + 1]) & 224 == 224:
                if check_next_header == 0:
                    return (seekstart + offset, header[offset:offset + 4])
                self._parse_header(header[offset:offset + 4])
                if self.valid:
                    file_pos = file.tell()
                    next_off, next_header = self._find_header(file, seeklimit=0, seekstart=seekstart + offset + self.framelength, check_next_header=check_next_header - 1)
                    file.seek(file_pos, 0)
                    if next_off != -1:
                        return (seekstart + offset, header[offset:offset + 4])
                    curr_pos = offset + 2
                else:
                    curr_pos = offset + 2
            else:
                curr_pos = offset + 2
            if read_more and curr_pos <= seeklimit:
                chunk = file.read(amt)
                if len(chunk) == 0:
                    return (-1, None)
                header += chunk

        return (-1, None)

    def _parse_header(self, header):
        self.valid = 0
        bytes, = struct.unpack('>i', header)
        mpeg_version = bytes >> 19 & 3
        layer = bytes >> 17 & 3
        protection_bit = bytes >> 16 & 1
        bitrate = bytes >> 12 & 15
        samplerate = bytes >> 10 & 3
        padding_bit = bytes >> 9 & 1
        private_bit = bytes >> 8 & 1
        mode = bytes >> 6 & 3
        mode_extension = bytes >> 4 & 3
        copyright = bytes >> 3 & 1
        original = bytes >> 2 & 1
        emphasis = bytes >> 0 & 3
        if mpeg_version == 0:
            self.version = 2.5
        elif mpeg_version == 2:
            self.version = 2
        elif mpeg_version == 3:
            self.version = 1
        else:
            return
        if layer > 0:
            self.layer = 4 - layer
        else:
            return
        self.protection = protection_bit
        self.bitrate = _bitrates[mpeg_version & 1][self.layer - 1][bitrate]
        self.samplerate = _samplerates[mpeg_version][samplerate]
        if self.bitrate is None or self.samplerate is None:
            return
        self.padding = padding_bit
        self.private = private_bit
        self.mode = _modes[mode]
        self.mode_extension = _mode_extensions[self.layer - 1][mode_extension]
        self.copyright = copyright
        self.original = original
        self.emphasis = _emphases[emphasis]
        try:
            if self.layer == 1:
                self.framelength = (12000 * self.bitrate / self.samplerate + padding_bit) * 4
                self.samplesperframe = 384.0
            elif self.layer == 2:
                self.framelength = 144000 * self.bitrate / self.samplerate + padding_bit
                self.samplesperframe = 1152.0
            else:
                if mpeg_version == 0 or mpeg_version == 2:
                    fake_samplerate = self.samplerate << 1
                else:
                    fake_samplerate = self.samplerate
                self.framelength = 144000 * self.bitrate / fake_samplerate + padding_bit
                self.samplesperframe = 1152.0
            self.length = int(round(self.filesize / self.framelength * (self.samplesperframe / self.samplerate)))
        except ZeroDivisionError:
            return

        if self.framelength < 0 or self.length < 0:
            return
        self.valid = 1

    def _parse_xing(self, file, seekstart = 0, seeklimit = _MP3_HEADER_SEEK_LIMIT):
        """Parse the Xing-specific header.
        
        For variable-bitrate (VBR) MPEG files, Xing includes a header which
        can be used to approximate the (average) bitrate and the duration
        of the file.
        """
        file.seek(seekstart, 0)
        header = file.read(seeklimit)
        try:
            i = string.find(header, 'Xing')
            if i > 0:
                header += file.read(128)
                flags, = struct.unpack('>i', header[i + 4:i + 8])
                if flags & 3:
                    frames, = struct.unpack('>i', header[i + 8:i + 12])
                    bytes, = struct.unpack('>i', header[i + 12:i + 16])
                    if self.samplerate:
                        length = int(round(frames * self.samplesperframe / self.samplerate))
                        bitrate = bytes * 8.0 / length / 1000
                        self.length = length
                        self.bitrate = bitrate
                        self.is_vbr = 1
                        return
        except ZeroDivisionError:
            pass
        except struct.error:
            pass

        if seekstart != 0:
            self._parse_xing(file, 0, seeklimit)


class MP3Info:
    num_regex = re.compile('\\d+')

    def __init__(self, file):
        self.valid = 0
        self.id3 = None
        self.mpeg = None
        self.title = self.artist = self.track = self.year = self.comment = self.composer = self.album = self.disc = self.genre = self.encoder = self.picformat = self.cover = None
        id3 = ID3v1(file)
        if id3.valid:
            self.id3 = id3
        for tag in self.id3.tags.keys():
            if tag == 'TT2' or tag == 'TIT2' or tag == 'v1title':
                self.title = self.id3.tags[tag].replace('\x00', '')
            elif tag == 'TP1' or tag == 'TPE1' or tag == 'v1performer' or tag == 'TOPE':
                self.artist = self.id3.tags[tag].replace('\x00', '')
            elif tag == 'TRK' or tag == 'TRCK' or tag == 'v1track':
                self.track = self.id3.tags[tag]
            elif tag == 'TYE' or tag == 'TYER' or tag == 'v1year':
                self.year = self.id3.tags[tag]
            elif tag == 'COM' or tag == 'COMM' or tag == 'v1comment':
                self.comment = self.id3.tags[tag].replace('\x00', '')
            elif tag == 'TCM':
                self.composer = self.id3.tags[tag].replace('\x00', '')
            elif tag == 'TAL' or tag == 'TALB' or tag == 'v1album' or tag == 'TOAL':
                self.album = self.id3.tags[tag].replace('\x00', '')
            elif tag == 'TCO' or tag == 'TCON' or tag == 'v1genre':
                self.genre = self.id3.tags[tag]
                if self.genre and self.genre[0] == '(' and self.genre[-1] == ')':
                    genres = self.num_regex.findall(self.genre)
                    if len(genres) > 0:
                        try:
                            self.genre = _genres[int(genres[0])]
                        except IndexError:
                            self.genre = ''

                    else:
                        self.genre = ''
                id3v2 = ID3v2(file)

        if id3v2.valid and id3v2.tags != {}:
            self.id3 = id3v2
        if id3v2.valid:
            self.mpeg = MPEG(file, seekstart=id3v2.header_size + 10)
        else:
            self.mpeg = MPEG(file)
        if self.id3 is None:
            return
        for tag in self.id3.tags.keys():
            if tag == 'TT2' or tag == 'TIT2' or tag == 'v1title':
                self.title = _stringclean(self.id3.tags[tag])
            elif tag == 'TP1' or tag == 'TPE1' or tag == 'v1performer' or tag == 'TOPE':
                self.artist = _stringclean(self.id3.tags[tag])
            elif tag == 'TRK' or tag == 'TRCK' or tag == 'v1track':
                self.track = _stringclean(self.id3.tags[tag])
            elif tag == 'TYE' or tag == 'TYER' or tag == 'v1year':
                self.year = _stringclean(self.id3.tags[tag])
            elif tag == 'COM' or tag == 'COMM' or tag == 'v1comment':
                self.comment = _stringclean(self.id3.tags[tag])
            elif tag == 'TCM':
                self.composer = _stringclean(self.id3.tags[tag])
            elif tag == 'TAL' or tag == 'TALB' or tag == 'v1album' or tag == 'TOAL':
                self.album = _stringclean(self.id3.tags[tag])
            elif tag == 'TPA':
                self.disc = _stringclean(self.id3.tags[tag])
            elif tag == 'TCO' or tag == 'TCON' or tag == 'v1genre':
                self.genre = _stringclean(self.id3.tags[tag])
                if self.genre and self.genre[0] == '(' and self.genre[-1] == ')':
                    genres = self.num_regex.findall(self.genre)
                    if len(genres) > 0:
                        try:
                            self.genre = _genres[int(genres[0])]
                        except IndexError:
                            self.genre = ''

                    else:
                        self.genre = ''
            elif tag == 'TEN' or tag == 'TENC':
                self.encoder = self.id3.tags[tag]
            elif tag == 'APIC':
                self.picformat = str(self.id3.tags[tag][6:9]).lower()
                self.cover = self.id3.tags[tag][12:]

        try:
            self.title = self.title.decode('utf-8').encode('utf-8')
        except:
            try:
                self.title = self.title.decode('windows-1252').encode('utf-8')
            except:
                pass

        try:
            self.artist = self.artist.decode('utf-8').encode('utf-8')
        except:
            try:
                self.artist = self.artist.decode('windows-1252').encode('utf-8')
            except:
                pass

        try:
            self.album = self.album.decode('utf-8').encode('utf-8')
        except:
            try:
                self.album = self.album.decode('windows-1252').encode('utf-8')
            except:
                pass

        try:
            self.comment = self.comment.decode('utf-8').encode('utf-8')
        except:
            try:
                self.comment = self.comment.decode('windows-1252').encode('utf-8')
            except:
                pass

        try:
            self.composer = self.composer.decode('utf-8').encode('utf-8')
        except:
            try:
                self.composer = self.composer.decode('windows-1252').encode('utf-8')
            except:
                pass

        try:
            self.genre = self.genre.decode('utf-8').encode('utf-8')
        except:
            try:
                self.genre = self.genre.decode('windows-1252').encode('utf-8')
            except:
                pass


def CoverFind(filename, dir):
    artist = ''
    album = ''
    cover = None
    try:
        id3r = MP3Info(open(filename, 'rb'))
    except:
        id3r = None
        cover = None

    if id3r != None:
        artist = id3r.artist
        album = id3r.album
        cover = id3r.cover
        title = id3r.title
        if artist == None:
            artist = ''
        if album == None:
            album = ''
    filename2 = str(filename) + '.jpg'
    name = os.path.basename(filename)
    album = os.path.splitext(name)[0]
    if os.path.splitext(name)[1] == 'm3u' or os.path.splitext(name)[1] == 'pls':
        return
    if cover == None:
        coverUrls = get_img_urls([album, title, artist])
        if len(coverUrls) > 0:
            dl_cover(coverUrls, dir, filename2)
            return filename2
        else:
            return
    else:
        return


def dl_cover(urlList, directory, filename):
    """download cover images from url to given dir"""
    coverImg = os.path.join(directory, filename)
    for url in urlList:
        urlOk = True
        try:
            coverImgWeb = urllib2.urlopen(url)
        except Exception as err:
            urlOk = False

        if fileExists(coverImg):
            break
        if urlOk:
            coverImgLocal = open(os.path.join(directory, filename), 'w')
            coverImgLocal.write(coverImgWeb.read())
            coverImgWeb.close()
            coverImgLocal.close()
            break


def sanitise_for_url(input):
    """sanitise a string so that it is ok to be used in a url"""
    if input == None:
        input = ''
    words = input.split(' ')
    output = ''
    for word in words:
        try:
            word = word.encode('utf-8')
        except:
            pass

        try:
            word = urllib.quote(word)
            output += word + '+'
        except Exception as err:
            pass

    output = output[:-1]
    return output


def get_img_urls(searchWords):
    """return list of cover urls obtained by searching
    google images for searchWords"""
    googleImagesUrl = 'http://ajax.googleapis.com/ajax/services/search/images'
    imgUrls = []
    searchWords = [ sanitise_for_url(searchWord) for searchWord in searchWords ]
    url = googleImagesUrl + '?v=1.0&q='
    for searchWord in searchWords:
        url += searchWord + '+'

    url = url[:-1]
    url += '&as_filetype=jpg'
    url += '&imgsz=medium'
    print url
    request = urllib2.Request(url, None, {'Referer': 'https://www.azboxhd.es'})
    try:
        response = urllib2.urlopen(request)
    except Exception as err:
        return imgUrls

    try:
        htp = response.read()
    except Exception as err:
        return imgUrls

    for dics in htp.split('['):
        for items in dics.split(','):
            key = ''
            if items[1:4] == 'url':
                value = items[7:-1]
                imgUrls.append(value)

    return imgUrls


if __name__ == '__main__':
    import sys
    i = MP3Info(open(sys.argv[1], 'rb'))
    print 'File Info'
    print '---------'
    for key in i.__dict__.keys():
        print key, ': ', i.__dict__[key]

    print
    print 'MPEG Info'
    print '---------'
    for key in i.mpeg.__dict__.keys():
        print key, ': ', i.mpeg.__dict__[key]

    print
    print 'ID3 Info'
    print '--------'
    for key in i.id3.__dict__.keys():
        print key, ': ', i.id3.__dict__[key]
