from . import _
from enigma import ePythonMessagePump
from __init__ import decrypt_block
from ThreadQueue import ThreadQueue
import gdata.youtube
import gdata.youtube.service
from gdata.service import BadAuthentication
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from twisted.web import client
from twisted.internet import reactor
from urllib2 import Request, URLError, urlopen as urlopen2
from socket import gaierror, error
import os, socket, httplib
from urllib import quote, unquote_plus, unquote, urlencode
from httplib import HTTPConnection, CannotSendRequest, BadStatusLine, HTTPException
from Components.config import config
from urlparse import parse_qs, parse_qsl
from threading import Thread
import re
import json
from jsinterp import JSInterpreter
from swfinterp import SWFInterpreter
from urllib2 import urlopen, URLError
YOUTUBE_READ_WRITE_SCOPE = 'https://www.googleapis.com/auth/youtube'
DEVELOPER_KEY = 'AIzaSyDYhIXx2lmga1aJJ7T-zTozmFWw-2ZB9s0'
YOUTUBE_API_CLIENT_ID = '928352881596-msmi2f4uje1mt556ug6hueuiersm9l60.apps.googleusercontent.com'
YOUTUBE_API_CLIENT_SECRET = 'UKnl9CYqv8AI0WTeV9iJOnBD'
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'
HTTPConnection.debuglevel = 1
if 'HTTPSConnection' not in dir(httplib):
    gdata.youtube.service.YOUTUBE_USER_FEED_URI = 'http://gdata.youtube.com/feeds/api/users'

def validate_cert(cert, key):
    buf = decrypt_block(cert[8:], key)
    if buf is None:
        return
    return buf[36:107] + cert[139:196]


def get_rnd():
    try:
        rnd = os.urandom(8)
        return rnd
    except:
        return None


std_headers = {'User-Agent': 'Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.2.6) Gecko/20100627 Firefox/3.6.6',
 'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
 'Accept-Language': 'en-us,en;q=0.5'}

class GoogleSuggestions():

    def __init__(self):
        self.hl = 'en'
        self.conn = None

    def prepareQuery(self):
        self.prepQuerry = '/complete/search?output=toolbar&client=youtube&xml=true&ds=yt&'
        if self.hl is not None:
            self.prepQuerry = self.prepQuerry + 'hl=' + self.hl + '&'
        self.prepQuerry = self.prepQuerry + 'jsonp=self.gotSuggestions&q='
        print '[MyTube - GoogleSuggestions] prepareQuery:', self.prepQuerry

    def getSuggestions(self, queryString):
        self.prepareQuery()
        if queryString is not '':
            query = self.prepQuerry + quote(queryString)
            self.conn = HTTPConnection('google.com')
            try:
                self.conn = HTTPConnection('google.com')
                self.conn.request('GET', query, '', {'Accept-Encoding': 'UTF-8'})
            except (CannotSendRequest, gaierror, error):
                self.conn.close()
                print '[MyTube - GoogleSuggestions] Can not send request for suggestions'
                return None

            try:
                response = self.conn.getresponse()
            except BadStatusLine:
                self.conn.close()
                print '[MyTube - GoogleSuggestions] Can not get a response from google'
                return None

            if response.status == 200:
                data = response.read()
                header = response.getheader('Content-Type', 'text/xml; charset=ISO-8859-1')
                charset = 'ISO-8859-1'
                try:
                    charset = header.split(';')[1].split('=')[1]
                    print '[MyTube - GoogleSuggestions] Got charset %s' % charset
                except:
                    print '[MyTube - GoogleSuggestions] No charset in Header, falling back to %s' % charset

                data = data.decode(charset).encode('utf-8')
                self.conn.close()
                return data
            else:
                self.conn.close()
                return None
        else:
            return None


class MyTubeFeedEntry():

    def __init__(self, feed, entry, favoritesFeed = False):
        self.feed = feed
        self.entry = entry
        self.favoritesFeed = favoritesFeed
        self.thumbnail = {}
        self.request = None

    def isPlaylistEntry(self):
        return False

    def getTubeId(self):
        try:
            return self.entry['id']['videoId']
        except:
            try:
                return self.entry['snippet']['resourceId']['videoId']
            except:
                try:
                    return self.entry['snippet']['resourceId']['channelId']
                except:
                    return self.entry['id']['channelId']

    def getId(self):
        try:
            return self.entry['id']
        except:
            return None

    def getType(self):
        try:
            return self.entry['id']['kind']
        except:
            try:
                return self.entry['snippet']['resourceId']['kind']
            except:
                return 'youtube#video'

    def getlive(self):
        try:
            return self.entry['snippet']['liveBroadcastContent']
        except:
            return 'none'

    def getTitle(self):
        try:
            return str(self.entry['snippet']['title']).encode('utf-8').strip()
        except KeyError:
            return ''

    def getDescription(self):
        try:
            return self.entry['snippet']['description'].encode('utf-8').strip()
        except KeyError:
            return 'not vailable'

    def getMoreDescription(self):
        try:
            return self.request['items'][0]['snippet']['description'].encode('utf-8').strip()
        except KeyError:
            return None

    def getThumbnailUrl(self, index = 0):
        try:
            return str(self.entry['snippet']['thumbnails']['default']['url'])
        except KeyError:
            return None

    def getPublishedDate(self):
        try:
            return self.entry['snippet']['publishedAt']
        except KeyError:
            return 'unknown'

    def getViews(self):
        try:
            return int(self.request['items'][0]['statistics']['viewCount'])
        except:
            return 0

    def getDuration(self):
        try:
            dur = self.request['items'][0]['contentDetails']['duration']
        except:
            return None

        dur = dur.replace('PT', '')
        h = 0
        m = 0
        s = 0
        f = dur.find('H')
        if f > 0:
            h = int(dur[:f])
            dur = dur[f + 1:]
        f = dur.find('M')
        if f > 0:
            m = int(dur[:f])
            dur = dur[f + 1:]
        f = dur.find('S')
        if f > 0:
            s = int(dur[:f])
        return h * 60 * 60 + m * 60 + s

    def getDimension(self):
        try:
            return self.request['items'][0]['contentDetails']['dimension']
        except:
            return ''

    def getDefinition(self):
        try:
            return self.request['items'][0]['contentDetails']['definition']
        except:
            return ''

    def getRatingAverage(self):
        total = self.getNumRaters() + self.getNumDeRaters()
        try:
            return self.getNumRaters() / total * 100
        except:
            return 0

    def getCategoryId(self):
        try:
            return self.request['items'][0]['snippet']['categoryId']
        except:
            return None

    def getNumRaters(self):
        try:
            return int(self.request['items'][0]['statistics']['likeCount'])
        except:
            return 0

    def getNumDeRaters(self):
        try:
            return int(self.request['items'][0]['statistics']['dislikeCount'])
        except:
            return 0

    def getTags(self):
        try:
            return str(self.request['items'][0]['snippet']['tags'])
        except:
            return ''

    def getAuthor(self):
        try:
            return self.entry['snippet']['channelTitle']
        except:
            try:
                return self.entry['snippet']['resourceId']['kind']
            except:
                return None

    def getChannelID(self):
        try:
            return self.entry['snippet']['channelId']
        except:
            try:
                return self.entry['snippet']['resourceId']['channelId']
            except KeyError:
                return None

    def getUserFeedsUrl(self):
        for author in self.entry.author:
            return author.uri.text

        return False

    def getUserId(self):
        try:
            return self.entry['snippet']['channelTitle']
        except:
            try:
                return self.entry['snippet']['title']
            except:
                return ''

    def subscribeToUser(self):
        return myTubeService.SubscribeToUser(self.getChannelID())

    def UnsubscribeToUser(self):
        return myTubeService.UnSubscribeToUser(self.getId())

    def addToFavorites(self):
        return myTubeService.addToFavorites(self.getTubeId(), self.getType())

    def deletefromFavorites(self):
        return myTubeService.deletefromFavorites(self.getId())

    def like(self):
        myTubeService.setlike(self.getTubeId())

    def dislike(self):
        myTubeService.setdislike(self.getTubeId())

    def PrintEntryDetails(self):
        self.request = youtube.videos().list(part='snippet,statistics,contentDetails', id=self.getTubeId()).execute()
        EntryDetails = {'Title': None,
         'TubeID': None,
         'Published': None,
         'Published': None,
         'Description': None,
         'Category': None,
         'Tags': None,
         'Duration': None,
         'Views': None,
         'Rating': None,
         'Thumbnails': None}
        EntryDetails['Title'] = str(self.entry['snippet']['title']).encode('utf-8').strip()
        EntryDetails['TubeID'] = self.getTubeId()
        if self.getMoreDescription():
            EntryDetails['Description'] = self.getMoreDescription()
        else:
            EntryDetails['Description'] = self.getDescription()
        EntryDetails['Category'] = self.getCategoryId()
        EntryDetails['Tags'] = self.getDimension() + ' ' + self.getDefinition() + ' ' + self.getTags()
        EntryDetails['Published'] = self.getPublishedDate()
        EntryDetails['Views'] = self.getViews()
        EntryDetails['Duration'] = self.getDuration()
        EntryDetails['Rating'] = self.getNumRaters()
        EntryDetails['DisRating'] = self.getNumDeRaters()
        EntryDetails['RatingAverage'] = self.getRatingAverage()
        EntryDetails['Author'] = self.getAuthor()
        EntryDetails['ratingaverage'] = self.getRatingAverage()
        list = []
        for thumbnail in self.entry['snippet']['thumbnails']:
            print 'Thumbnail url: %s' % self.entry['snippet']['thumbnails'][thumbnail]['url']
            list.append(str(self.entry['snippet']['thumbnails'][thumbnail]['url']))

        EntryDetails['Thumbnails'] = list
        return EntryDetails

    def getPage(self, url):
        watchvideopage = None
        watchrequest = Request(url, None, std_headers)
        try:
            print '[MyTube] trying to find out if a HD Stream is available', url
            watchvideopage = urlopen2(watchrequest).read()
        except (URLError, HTTPException, socket.error) as err:
            print '[MyTube] Error: Unable to retrieve watchpage - Error code: ', str(err)
            return

        return watchvideopage

    def getVideoUrl(self):
        VIDEO_FMT_PRIORITY_MAP = {'38': 1,
         '37': 2,
         '22': 3,
         '18': 4,
         '35': 5,
         '34': 6}
        video_url = None
        video_id = str(self.getTubeId())
        watch_url = 'http://www.youtube.com/watch?v=%s&gl=US&hl=en&has_verified=1&bpctr=9999999999' % video_id
        for x in range(0, 10):
            watchvideopage = self.getPage(watch_url)
            if watchvideopage != None:
                break

        if watchvideopage == None:
            return video_url
        age_gate = False
        if re.search('player-age-gate-content">', watchvideopage) is not None:
            age_gate = True
            if config.plugins.mytube.general.showadult.value == False:
                return 'age'
            url = 'http://www.youtube.com/embed/%s' % video_id
            embed_webpage = self.getPage(url)
            info_url = 'http://www.youtube.com/get_video_info?video_id=%s&el=embedded&gl=US&hl=en&eurl=%s&asv=3&sts=%s' % (video_id, 'https://youtube.googleapis.com/v/' + video_id, self._search_regex('"sts"\\s*:\\s*(\\d+)', embed_webpage))
            request = Request(info_url, None, std_headers)
            try:
                infopage = urlopen2(request).read()
                videoinfo = parse_qs(infopage)
            except (URLError, HTTPException, socket.error) as err:
                print '[MyTube] Error: unable to download video infopage', str(err)
                return video_url

        else:
            videoinfo = None
            for el in ['',
             '&el=detailpage',
             '&el=vevo',
             '&el=embedded']:
                info_url = 'http://www.youtube.com/get_video_info?&video_id=%s%s&ps=default&eurl=&gl=US&hl=en' % (video_id, el)
                for x in range(0, 10):
                    infopage = self.getPage(info_url)
                    if infopage != None:
                        break

                if infopage == None:
                    return video_url
                try:
                    videoinfo = parse_qs(infopage)
                    if ('url_encoded_fmt_stream_map' or 'fmt_url_map') in videoinfo:
                        break
                except:
                    pass

            if videoinfo == None:
                print '[MyTube] Error: unable to download video infopage'
                return video_url
        try:
            mobj = re.search(';ytplayer.config = ({.*?});', watchvideopage)
            info = json.loads(mobj.group(1))
            args = info['args']
            if args.get('ptk', '') == 'vevo' or '&s=' in str(args):
                print '[MyTube] %s: Vevo video detected with encrypted signature.' % video_id
                videoinfo['url_encoded_fmt_stream_map'] = [str(args['url_encoded_fmt_stream_map'])]
        except:
            pass

        if ('url_encoded_fmt_stream_map' or 'fmt_url_map') not in videoinfo:
            if 'reason' not in videoinfo:
                print '[MyTube] Error: unable to extract "fmt_url_map" or "url_encoded_fmt_stream_map" parameter for unknown reason'
            else:
                reason = unquote_plus(videoinfo['reason'][0])
                print '[MyTube] Error: YouTube said: %s' % reason.decode('utf-8')
            return video_url
        video_fmt_map = {}
        fmt_infomap = {}
        if videoinfo.has_key('url_encoded_fmt_stream_map'):
            tmp_fmtUrlDATA = videoinfo['url_encoded_fmt_stream_map'][0].split(',')
        else:
            tmp_fmtUrlDATA = videoinfo['fmt_url_map'][0].split(',')
        for fmtstring in tmp_fmtUrlDATA:
            fmturl = fmtid = fmtsig = ''
            if videoinfo.has_key('url_encoded_fmt_stream_map'):
                try:
                    for arg in fmtstring.split('&'):
                        if arg.find('=') >= 0:
                            print arg.split('=')
                            key, value = arg.split('=')
                            if key == 'itag':
                                if len(value) > 3:
                                    value = value[:2]
                                fmtid = value
                            elif key == 'url':
                                fmturl = value
                            elif key == 'sig':
                                fmtsig = value
                            elif key == 's':
                                ASSETS_RE = '"assets":.+?"js":\\s*("[^"]+")'
                                jsplayer_url_json = self._search_regex(ASSETS_RE, embed_webpage if age_gate else watchvideopage)
                                if not jsplayer_url_json and not age_gate:
                                    jsplayer_url_json = self._search_regex(ASSETS_RE, watchvideopage)
                                player_url = json.loads(jsplayer_url_json)
                                if player_url is None:
                                    player_url_json = self._search_regex('ytplayer\\.config.*?"url"\\s*:\\s*("[^"]+")', watchvideopage)
                                    player_url = json.loads(player_url_json)
                                fmtsig = self._decrypt_signature(value, player_url)

                    if fmtid != '' and fmturl != '' and VIDEO_FMT_PRIORITY_MAP.has_key(fmtid):
                        video_fmt_map[VIDEO_FMT_PRIORITY_MAP[fmtid]] = {'fmtid': fmtid,
                         'fmturl': unquote_plus(fmturl),
                         'fmtsig': fmtsig}
                        if fmtsig != '':
                            fmt_infomap[int(fmtid)] = '%s&signature=%s' % (unquote_plus(fmturl), fmtsig)
                        elif '%26signature%3D' in fmturl:
                            fmt_infomap[int(fmtid)] = unquote_plus(fmturl)
                    fmturl = fmtid = fmtsig = ''
                except:
                    print 'error parsing fmtstring:', fmtstring

            else:
                fmtid, fmturl = fmtstring.split('|')
                if VIDEO_FMT_PRIORITY_MAP.has_key(fmtid) and fmtid != '':
                    video_fmt_map[VIDEO_FMT_PRIORITY_MAP[fmtid]] = {'fmtid': fmtid,
                     'fmturl': unquote_plus(fmturl)}
                    fmt_infomap[int(fmtid)] = unquote_plus(fmturl)

        print '[MyTube] got', sorted(fmt_infomap.iterkeys())
        if video_fmt_map and len(video_fmt_map):
            print '[MyTube] found best available video format:', video_fmt_map[sorted(video_fmt_map.iterkeys())[0]]['fmtid']
            best_video = video_fmt_map[sorted(video_fmt_map.iterkeys())[0]]
            video_url = '%s&signature=%s' % (best_video['fmturl'].split(';')[0], best_video['fmtsig'])
            print '[MyTube] found best available video url:', video_url
        return str(video_url)

    def _decrypt_signature_age_gate(self, s):
        if len(s) == 86:
            return s[2:63] + s[82] + s[64:82] + s[63]
        else:
            return self._decrypt_signature2(s)

    def _download_webpage(self, url):
        """ Returns a tuple (page content as string, URL handle) """
        try:
            urlh = urlopen(url)
        except URLError as e:
            raise Exception(e.reason)

        return urlh.read()

    def _search_regex(self, pattern, string):
        """
        Perform a regex search on the given string, using a single or a list of
        patterns returning the first matching group.
        """
        mobj = re.search(pattern, string, 0)
        if mobj:
            return next((g for g in mobj.groups() if g is not None))
        raise Exception('Unable extract pattern from string!')

    def _decrypt_signature(self, s, player_url):
        """Turn the encrypted s field into a working signature"""
        if player_url is None:
            raise Exception('Cannot decrypt signature without player_url!')
        if player_url[:2] == '//':
            player_url = 'https:' + player_url
        try:
            func = self._extract_signature_function(player_url, s)
            return func(s)
        except:
            raise Exception('Signature extraction failed!')

    def _extract_signature_function(self, player_url, example_sig):
        id_m = re.match('.*?-(?P<id>[a-zA-Z0-9_-]+)(?:/watch_as3|/html5player(?:-new)?|/base)?\\.(?P<ext>[a-z]+)$', player_url)
        if not id_m:
            raise Exception('Cannot identify player %r!' % player_url)
        try:
            jsversion = re.compile('/player-([^/]+)/', re.DOTALL).search(player_url).group(1)
        except:
            jsversion = None

        if jsversion:
            import plugin
            cypher = ''
            try:
                f = open(plugin.plugin_path + '/mytube.dic2', 'r')
                for line in f:
                    if jsversion in line:
                        cypher = line.split(':')[1].split(',')
                        break

                f.close()
            except:
                pass

            if cypher != '':
                return lambda s: ''.join((s[int(i)] for i in cypher))
        player_type = id_m.group('ext')
        code = self._download_webpage(player_url)
        res = None
        if player_type == 'js':
            res = self._parse_sig_js(code)
        elif player_type == 'swf':
            res = self._parse_sig_swf(code)
        else:
            raise Exception('Invalid player type %r!' % player_type)
        test_string = ''.join(map(chr, range(len(example_sig))))
        cache_res = res(test_string)
        cache_spec = [ ord(c) for c in str(cache_res) ]
        l = ''.join((str(i) + ',' for i in cache_spec))
        import datetime
        open(plugin.plugin_path + '/mytube.dic', 'w').write('%s:%s:%s\n' % (jsversion, l[:-1], datetime.datetime.now().strftime('%d %b %Y')))
        return res

    def _parse_sig_js(self, jscode):
        funcname = self._search_regex('\\.sig\\|\\|([a-zA-Z0-9$]+)\\(', jscode)
        jsi = JSInterpreter(jscode)
        initial_function = jsi.extract_function(funcname)
        return lambda s: initial_function([s])

    def _parse_sig_swf(self, file_contents):
        swfi = SWFInterpreter(file_contents)
        TARGET_CLASSNAME = 'SignatureDecipher'
        searched_class = swfi.extract_class(TARGET_CLASSNAME)
        initial_function = swfi.extract_function(searched_class, 'decipher')
        return lambda s: initial_function([s])

    def _decrypt_signature2(self, s, js, name):
        cyphers = {'vflNzKG7n': 's3 r s2 r s1 r w67',
         'vfllMCQWM': 's2 w46 r w27 s2 w43 s2 r',
         'vflJv8FA8': 's1 w51 w52 r',
         'vflR_cX32': 's2 w64 s3',
         'vflveGye9': 'w21 w3 s1 r w44 w36 r w41 s1',
         'vflj7Fxxt': 'r s3 w3 r w17 r w41 r s2',
         'vfltM3odl': 'w60 s1 w49 r s1 w7 r s2 r',
         'vflDG7-a-': 'w52 r s3 w21 r s3 r',
         'vfl39KBj1': 'w52 r s3 w21 r s3 r',
         'vflmOfVEX': 'w52 r s3 w21 r s3 r',
         'vflJwJuHJ': 'r s3 w19 r s2',
         'vfl_ymO4Z': 'r s3 w19 r s2',
         'vfl26ng3K': 'r s2 r',
         'vflcaqGO8': 'w24 w53 s2 w31 w4',
         'vflQw-fB4': 's2 r s3 w9 s3 w43 s3 r w23',
         'vflSAFCP9': 'r s2 w17 w61 r s1 w7 s1',
         'vflART1Nf': 's3 r w63 s2 r s1',
         'vflLC8JvQ': 'w34 w29 w9 r w39 w24',
         'vflm_D8eE': 's2 r w39 w55 w49 s3 w56 w2',
         'vflTWC9KW': 'r s2 w65 r',
         'vflRFcHMl': 's3 w24 r',
         'vflM2EmfJ': 'w10 r s1 w45 s2 r s3 w50 r',
         'vflz8giW0': 's2 w18 s3',
         'vfl_wGgYV': 'w60 s1 r s1 w9 s3 r s3 r',
         'vfl1HXdPb': 'w52 r w18 r s1 w44 w51 r s1',
         'vfl2LOvBh': 'w34 w19 r s1 r s3 w24 r',
         'vflZK4ZYR': 'w19 w68 s1',
         'vflh9ybst': 'w48 s3 w37 s2',
         'vflg0g8PQ': 'w36 s3 r s2',
         'vflg0g8PQ': 'w36 s3 r s2',
         'vflHOr_nV': 'w58 r w50 s1 r s1 r w11 s3',
         'vfluy6kdb': 'r w12 w32 r w34 s3 w35 w42 s2',
         'vflkuzxcs': 'w22 w43 s3 r s1 w43',
         'vflGNjMhJ': 'w43 w2 w54 r w8 s1',
         'vfldJ8xgI': 'w11 r w29 s1 r s3'}
        if js == None:
            return ''
        if js in cyphers:
            arr = cyphers[js]
        else:
            arr = self.guessjs(js, name)
        return self.decode(s, arr)

    def decode(self, sig, arr):
        sigA = sig
        if arr == '':
            return ''
        arr2 = arr.split(' ')
        for act in arr2:
            if act[0] == 'w':
                sigA = self.swap(sigA, act[1:])
            elif act == 'r':
                sigA = sigA[::-1]
            else:
                act2 = int(act[1:])
                sigA = sigA[act2:]

        result = sigA
        if len(result) == 81:
            return result
        else:
            return ''

    def swap(self, a, b):
        al = list(a)
        b = int(b) % len(a)
        c = al[0]
        al[0] = al[int(b)]
        al[int(b)] = c
        return ''.join(al)

    def guessjs(self, ver, name):
        import plugin
        cypher = ''
        try:
            f = open(plugin.plugin_path + '/mytube.dic', 'r')
            for line in f:
                if ver in line:
                    cypher = line.split(':')[1]
                    break

            f.close()
        except:
            pass

        if cypher != '':
            return cypher
        url = 'http://s.ytimg.com/yts/jsbin/html5player-%s.js' % ver
        try:
            script = urlopen2(url).read()
        except:
            print '[myTube] unable to download javascript code'
            return ''

        if script:
            try:
                nameFunct = re.search('=.\\.sig\\|\\|(.*?)\\(', script).group(1)
            except:
                print '[myTube] unable to find decode name function'
                return ''

            try:
                Funct = re.search('function %s[^{]+{(.*?)}' % nameFunct.replace('$', '\\$'), script).group(1)
                print '[myTube] Function for decrypter is %s' % Funct
            except:
                print '[myTube] unable to find decode function %s' % nameFunct
                return ''

            try:
                for f in Funct.split(';'):
                    if 'split' not in f and 'join' not in f and 'b=' not in f and '=b' not in f:
                        if 'reverse' in f:
                            cypher = cypher + 'r '
                        elif 'a.length' in f:
                            par = f.split('%')[0].split('=')[1].split('[')[-1]
                            cypher = cypher + 'w%s ' % par
                        elif '.' in f and '=' not in f:
                            par = re.search('\\((.*?)\\)', f).group(1)
                            par = par.split(',')[1]
                            cypher = cypher + self.getfunction(f, script, par)
                        else:
                            par = re.search('\\((.*?)\\)', f).group(1)
                            if len(par.split(',')) == 2:
                                par = par.split(',')[1]
                                cypher = cypher + 'w%s ' % par
                            else:
                                cypher = cypher + 's%s ' % par

            except:
                print '[myTube] unable to make cypher string for decrypt'
                return ''

            cypher = cypher.rstrip()
            import datetime
            open(plugin.plugin_path + '/mytube.dic', 'a').write('%s:%s:%s\n' % (ver, cypher, datetime.datetime.now().strftime('%d %b %Y')))
            print '[myTube] Decode cypher is %s' % cypher
            return cypher

    def getfunction(self, func, script, par):
        cypher = ''
        nfunc = func.split('(')[0]
        nfunc = nfunc.split('.')[1]
        try:
            Funct = re.search('%s:function[^{]+{(.*?)}' % nfunc.replace('$', '\\$'), script).group(1)
            print '[myTube] SubFunction for decrypter is %s' % Funct
        except:
            print '[myTube] unable to find decode subfunction %s' % nfunc
            return ''

        try:
            if 'reverse' in Funct:
                cypher = 'r '
            elif 'a.length' in Funct:
                cypher = 'w%s ' % par
            elif 'splice' in Funct:
                cypher = 's%s ' % par
            elif len(par.split(',')) == 2:
                par = par.split(',')[1]
                cypher = 'w%s ' % par
            else:
                cypher = 's%s ' % par
        except:
            print '[myTube] unable to make cypher string for decrypt'
            return ''

        return cypher

    def getRelatedVideos(self):
        print '[MyTubeFeedEntry] getRelatedVideos()'
        for link in self.entry.link:
            if link.rel.endswith('video.related'):
                print 'Found Related: ', link.href
                return link.href

    def getResponseVideos(self):
        print '[MyTubeFeedEntry] getResponseVideos()'
        for link in self.entry.link:
            if link.rel.endswith('video.responses'):
                print 'Found Responses: ', link.href
                return link.href

    def getUserVideos(self):
        print '[MyTubeFeedEntry] getUserVideos()'
        username = self.getUserId()
        myuri = 'http://gdata.youtube.com/feeds/api/users/%s/uploads' % username
        print 'Found Uservideos: ', myuri
        return myuri


class MyTubePlayerService():
    cached_auth_request = {}
    current_auth_token = None
    yt_service = None

    def __init__(self):
        print '[MyTube] MyTubePlayerService - init'
        self.feedentries = []
        self.relatedToVideoId = None
        self.channelId = None
        self.feed = None
        self.order = None
        self.pageToken = None
        self.videoCategoryId = None
        self.q = None
        self.regionCode = None
        self.page = 1
        self.credentials = None
        self.safeSearch = 'moderate'
        self.myplaylist = []

    def startService(self, auth_token = None):
        global youtube
        self.current_auth_token = auth_token
        print '[MyTube] MyTubePlayerService - startService'
        if self.current_auth_token is None:
            youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)
        else:
            from oauth2client.client import AccessTokenCredentials
            import httplib2
            credentials = AccessTokenCredentials(self.current_auth_token, 'mytube-spa/1.0')
            youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, http=credentials.authorize(httplib2.Http()))

    def stopService(self):
        print '[MyTube] MyTubePlayerService - stopService'
        del self.ytService

    def getLoginTokenOnCurl(self, email, pw):
        opts = {'service': 'youtube',
         'accountType': 'HOSTED_OR_GOOGLE',
         'Email': email,
         'Passwd': pw,
         'source': self.yt_service.client_id}
        print '[MyTube] MyTubePlayerService - Starting external curl auth request'
        result = os.popen('curl -s -k -X POST "%s" -d "%s"' % (gdata.youtube.service.YOUTUBE_CLIENTLOGIN_AUTHENTICATION_URL, urlencode(opts))).read()
        return result

    def supportsSSL(self):
        return 'HTTPSConnection' in dir(httplib)

    def getFormattedTokenRequest(self, email, pw):
        return dict(parse_qsl(self.getLoginTokenOnCurl(email, pw).strip().replace('\n', '&')))

    def getAuthedUsername(self):
        if self.cached_auth_request.get('YouTubeUser') is not None:
            return self.cached_auth_request.get('YouTubeUser')
        if self.is_auth() is False:
            return ''
        return 'Logged In'

    def auth_user(self):
        print '[MyTube] MyTubePlayerService - auth_use - '
        try:
            from OAuth import OAuth
            return OAuth(YOUTUBE_API_CLIENT_ID, YOUTUBE_API_CLIENT_SECRET)
        except:
            return None

    def getuserplaylist(self):
        self.myplaylist = youtube.channels().list(part='contentDetails', mine='true').execute()['items']

    def getmyplaylist(self):
        return self.myplaylist

    def resetAuthState(self):
        print '[MyTube] MyTubePlayerService - resetting auth'
        self.cached_auth_request = {}
        self.current_auth_token = None
        if self.yt_service is None:
            return
        self.yt_service.current_token = None
        self.yt_service.token_store.remove_all_tokens()

    def is_auth(self):
        return self.current_auth_token is not None

    def auth_token(self):
        return self.yt_service.current_token.get_token_string()

    def getFeedService(self, feedname):
        if feedname == 'top_rated':
            return self.yt_service.GetTopRatedVideoFeed
        if feedname == 'most_viewed':
            return self.yt_service.GetMostViewedVideoFeed
        if feedname == 'recently_featured':
            return self.yt_service.GetRecentlyFeaturedVideoFeed
        if feedname == 'top_favorites':
            return self.yt_service.GetTopFavoritesVideoFeed
        if feedname == 'most_recent':
            return self.yt_service.GetMostRecentVideoFeed
        if feedname == 'most_discussed':
            return self.yt_service.GetMostDiscussedVideoFeed
        if feedname == 'most_linked':
            return self.yt_service.GetMostLinkedVideoFeed
        if feedname == 'most_responded':
            return self.yt_service.GetMostRespondedVideoFeed
        return self.yt_service.GetYouTubeVideoFeed

    def getFeed(self, url, feedname = '', callback = None, errorback = None):
        print '[MyTube] MyTubePlayerService - getFeed:', url, feedname
        self.feedentries = []
        if feedname != _('More video entries.'):
            self.feedname = feedname
            self.pageToken = None
        if config.plugins.mytube.general.showadult.value:
            self.safeSearch = 'none'
        self.regionCode = config.plugins.mytube.search.lr.value
        self.stype = ''
        if config.plugins.mytube.general.searchvideos.value:
            self.stype = self.stype + 'video,'
        if config.plugins.mytube.general.searchchannels.value:
            self.stype = self.stype + 'channel,'
        if len(self.stype) > 1:
            self.stype = self.stype[:-1]
        if self.feedname == _('User video entries.') or self.feedname == 'channel':
            self.stype = 'video'
        if self.feedname == 'my_subscriptions':
            if feedname == _('More video entries.'):
                self.pageToken = url
                self.page += 1
            else:
                self.page = 1
                self.pageToken = None
            request = youtube.subscriptions().list(mine=True, pageToken=self.pageToken, part='id,snippet', maxResults='25')
        elif self.feedname == 'my_favorites' or self.feedname == 'my_history' or self.feedname == 'my_watch_later' or self.feedname == 'my_uploads' or self.feedname == 'my_likes':
            if feedname == _('More video entries.'):
                self.pageToken = url
                self.page += 1
            else:
                self.page = 1
                self.pageToken = None
                channels_response = youtube.channels().list(mine=True, part='contentDetails').execute()
                for channel in channels_response['items']:
                    uploads_list_id = channel['contentDetails']['relatedPlaylists']['uploads']
                    history_list_id = channel['contentDetails']['relatedPlaylists']['watchHistory']
                    watchlater_list_id = channel['contentDetails']['relatedPlaylists']['watchLater']
                    favorites_list_id = channel['contentDetails']['relatedPlaylists']['favorites']
                    likes_id = channel['contentDetails']['relatedPlaylists']['likes']

                self.playid = None
                if self.feedname == 'my_favorites':
                    self.playid = favorites_list_id
                elif self.feedname == 'my_history':
                    self.playid = history_list_id
                elif self.feedname == 'my_watch_later':
                    self.playid = watchlater_list_id
                elif self.feedname == 'my_uploads':
                    self.playid = uploads_list_id
                elif self.feedname == 'my_likes':
                    self.playid = likes_id
            if self.playid != None:
                request = youtube.playlistItems().list(playlistId=self.playid, pageToken=self.pageToken, part='snippet', maxResults='25')
        elif feedname == 'top_rated':
            self.relatedToVideoId = None
            self.channelId = None
            self.page = 1
            self.q = None
            self.pageToken = None
            self.videoCategoryId = None
            self.order = 'rating'
        elif feedname == 'most_viewed':
            self.relatedToVideoId = None
            self.channelId = None
            self.page = 1
            self.q = None
            self.pageToken = None
            self.videoCategoryId = None
            self.order = 'viewCount'
        elif feedname == _('More video entries.'):
            self.page += 1
            self.pageToken = url
        elif feedname == _('User video entries.') or feedname == 'channel':
            self.stype = 'video'
            self.relatedToVideoId = None
            self.channelId = url
            self.page = 1
            self.q = None
            self.pageToken = None
            self.videoCategoryId = None
            self.order = config.plugins.mytube.search.orderBy.value
        elif feedname == _('Related video entries.'):
            self.relatedToVideoId = url
            self.channelId = None
            self.page = 1
            self.q = None
            self.pageToken = None
            self.videoCategoryId = None
            self.order = config.plugins.mytube.search.orderBy.value
        elif int(feedname) > 0:
            self.relatedToVideoId = None
            self.channelId = None
            self.page = 1
            self.q = None
            self.pageToken = None
            self.videoCategoryId = feedname
            self.stype = 'video'
            self.order = config.plugins.mytube.search.orderBy.value
        if self.feedname != 'my_favorites' and self.feedname != 'my_history' and self.feedname != 'my_watch_later' and self.feedname != 'my_uploads' and self.feedname != 'my_subscriptions' and self.feedname != 'my_likes':
            open('/tmp/prueba', 'w').write('self.feedname = %s\nfeedname = %s\npagetoken = %s\nchannelId = %s\nq = %s' % (self.feedname,
             feedname,
             str(self.pageToken),
             str(self.channelId),
             str(self.q)))
            request = youtube.search().list(regionCode=self.regionCode, order=self.order, videoCategoryId=self.videoCategoryId, pageToken=self.pageToken, relatedToVideoId=self.relatedToVideoId, channelId=self.channelId, safeSearch=self.safeSearch, q=self.q, part='id,snippet', maxResults='25', type=self.stype)
        queryThread = YoutubeQueryThread(request, url, self.gotFeed, self.gotFeedError, callback, errorback)
        queryThread.start()
        return queryThread

    def search(self, searchTerms, startIndex = 1, maxResults = 25, orderby = 'relevance', time = 'all_time', racy = 'include', author = '', lr = '', categories = '', sortOrder = 'ascending', callback = None, errorback = None):
        print '[MyTube] MyTubePlayerService - search()'
        self.stype = ''
        if config.plugins.mytube.general.searchvideos.value:
            self.stype = self.stype + 'video,'
        if config.plugins.mytube.general.searchchannels.value:
            self.stype = self.stype + 'channel,'
        if len(self.stype) > 1:
            self.stype = self.stype[:-1]
        self.page = 1
        self.pageToken = None
        self.channelId = None
        self.feedname = 'search'
        self.relatedToVideoId = None
        self.channelId = None
        self.feedentries = []
        self.regionCode = config.plugins.mytube.search.lr.value
        self.videoCategoryId = config.plugins.mytube.search.categories.value
        self.q = searchTerms
        self.order = 'relevance'
        if config.plugins.mytube.general.showadult.value:
            self.safeSearch = 'none'
        request = youtube.search().list(regionCode=self.regionCode, videoCategoryId=self.videoCategoryId, safeSearch=self.safeSearch, order=self.order, q=searchTerms, part='id,snippet', maxResults='25', type=self.stype)
        queryThread = YoutubeQueryThread(request, '', self.gotFeed, self.gotFeedError, callback, errorback)
        queryThread.start()
        return queryThread

    def getUserEntry(self, user = 'default'):
        channels_response = youtube.channels().list(mine=True, part='snippet,statistics').execute()
        for channel in channels_response['items']:
            username = str(channel['snippet']['title'])
            img_url = channel['snippet']['thumbnails']['default']['url']
            view_count = int(channel['statistics']['viewCount'])
            coment_count = int(channel['statistics']['commentCount'])
            subscriber_count = int(channel['statistics']['subscriberCount'])
            video_count = int(channel['statistics']['videoCount'])

        return (username,
         str(img_url),
         view_count,
         coment_count,
         subscriber_count,
         video_count)

    def gotFeed(self, feed, callback):
        if feed is not None:
            self.feed = feed
            open('/tmp/prueba2', 'w').write(str(feed))
            for entry in self.feed['items']:
                MyFeedEntry = MyTubeFeedEntry(self, entry)
                self.feedentries.append(MyFeedEntry)

        if callback is not None:
            callback(self.feed)

    def gotFeedError(self, exception, errorback):
        if errorback is not None:
            errorback(exception)

    def SubscribeToUser(self, channel_id):
        try:
            youtube.subscriptions().insert(part='snippet', body=dict(snippet=dict(resourceId=dict(channelId=channel_id)))).execute()
            return _('Subscription Succesfully')
        except:
            return _('Subscription error')

    def UnSubscribeToUser(self, kid):
        try:
            youtube.subscriptions().delete(id=kid).execute()
            return _('Remove Subscription Succesfully')
        except:
            return _('Error: No remove Subscription')

    def addToFavorites(self, video_id, kind):
        try:
            channels_response = youtube.channels().list(mine=True, part='contentDetails').execute()
            for channel in channels_response['items']:
                favorites_list_id = channel['contentDetails']['relatedPlaylists']['favorites']

            youtube.playlistItems().insert(part='snippet', body=dict(snippet=dict(playlistId=favorites_list_id, resourceId=dict(videoId=video_id, kind=kind)))).execute()
            return _('Video append to favorites')
        except:
            return _('Error: No video append')

    def deletefromFavorites(self, kid):
        try:
            youtube.playlistItems().delete(id=kid).execute()
            return _('Video remove from favorites')
        except:
            return _('Error: No remove video from favorites')

    def setlike(self, video_id):
        try:
            youtube.videos().rate(id=video_id, rating='like').execute()
        except:
            print '[mytube] Error in like action'

    def setdislike(self, video_id):
        try:
            youtube.videos().rate(id=video_id, rating='dislike').execute()
        except:
            print '[mytube] Error in dislike action'

    def getTitle(self):
        return ''

    def getEntries(self):
        return self.feedentries

    def itemCount(self):
        return ''

    def getTotalResults(self):
        if self.feed['pageInfo']['totalResults'] is None:
            return 0
        return self.feed['pageInfo']['totalResults']

    def getNextFeedEntriesURL(self):
        try:
            if self.feed['nextPageToken']:
                return self.feed['nextPageToken']
            return None
        except:
            return None

    def getCurrentPage(self):
        return self.page


class YoutubeQueryThread(Thread):

    def __init__(self, query, param, gotFeed, gotFeedError, callback, errorback):
        Thread.__init__(self)
        self.messages = ThreadQueue()
        self.gotFeed = gotFeed
        self.gotFeedError = gotFeedError
        self.callback = callback
        self.errorback = errorback
        self.query = query
        self.param = param
        self.canceled = False

    def cancel(self):
        self.canceled = True

    def run(self):
        search_response = self.query.execute()
        self.gotFeed(search_response, self.callback)

    def finished(self, val):
        if not self.canceled:
            message = self.messages.pop()
            if message[0]:
                self.gotFeed(message[1], message[2])
            else:
                self.gotFeedError(message[1], message[2])


myTubeService = MyTubePlayerService()
