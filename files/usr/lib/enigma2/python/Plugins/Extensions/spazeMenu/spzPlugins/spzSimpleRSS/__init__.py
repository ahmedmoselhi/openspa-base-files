from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE
from os import environ as os_environ
import gettext

def localeInit():
    lang = language.getLanguage()[:2]
    os_environ['LANGUAGE'] = lang
    print '[SimpleRSS] set language to ', lang
    gettext.bindtextdomain('SimpleRSS', resolveFilename(SCOPE_PLUGINS, 'Extensions/SimpleRSS/locale'))


def _(txt):
    t = gettext.dgettext('SimpleRSS', txt)
    if t == txt:
        print '[SimpleRSS] fallback to default translation for', txt
        t = gettext.gettext(txt)
    return t


localeInit()
language.addCallback(localeInit)
