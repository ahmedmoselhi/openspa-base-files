from Components.Language import language
from Tools.Directories import resolveFilename, SCOPE_PLUGINS
import os, gettext
PluginLanguageDomain = 'OpenSPAPlug'
PluginLanguagePath = 'Extensions/OpenSPAPlug/locale'

def localeInit():
    lang = language.getLanguage()[:2]
    os.environ['LANGUAGE'] = lang
    print '[OpenSPAPlug] set language to ', lang
    gettext.bindtextdomain(PluginLanguageDomain, resolveFilename(SCOPE_PLUGINS, PluginLanguagePath))


def _(txt):
    if gettext.dgettext(PluginLanguageDomain, txt):
        return gettext.dgettext(PluginLanguageDomain, txt)
    else:
        print '[' + PluginLanguageDomain + '] fallback to default translation for ' + txt
        return gettext.gettext(txt)


language.addCallback(localeInit())
