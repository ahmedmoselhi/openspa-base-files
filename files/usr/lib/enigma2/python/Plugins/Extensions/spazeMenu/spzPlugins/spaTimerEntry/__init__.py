from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE
from os import environ as os_environ
import gettext

def localeInit():
    gettext.bindtextdomain('spaTimerEntry', resolveFilename(SCOPE_PLUGINS, 'Extensions/spazeMenu/spzPlugins/spaTimerEntry/locale'))


def _(txt):
    t = gettext.dgettext('spaTimerEntry', txt)
    if t == txt:
        print '[spaTimerEntry] fallback to default translation for', txt
        t = gettext.gettext(txt)
    return t


localeInit()
language.addCallback(localeInit)
