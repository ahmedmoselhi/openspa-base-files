from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS, SCOPE_LANGUAGE
from os import environ as os_environ
import gettext

def localeInit():
    lang = language.getLanguage()[:2]
    os_environ['LANGUAGE'] = lang
    gettext.bindtextdomain('spaQButton', resolveFilename(SCOPE_PLUGINS, 'Extensions/spaQButton/locale'))


_ = lambda txt: gettext.dgettext('spaQButton', txt)
localeInit()
language.addCallback(localeInit)
