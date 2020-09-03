from Source import Source
from Components.Element import cached
from Plugins.Extensions.spazeMenu.spzPlugins.descargasSPZ.plugin import updates_event

def pondebugs(loque):
    pass


class spaUpdates(Source):

    def __init__(self, session):
        Source.__init__(self)
        self.hay = False
        self.session = session
        updates_event.append(self.gotUpdate)
        pondebugs('init')
        self.gotUpdate(False)

    def gotUpdate(self, sihay):
        pondebugs('gotUpdate: ' + str(sihay))
        self.hay = sihay
        self.changed((self.CHANGED_ALL,))

    def destroy(self):
        updates_event.remove(self.gotUpdate)
        Source.destroy(self)

    @cached
    def getBoolean(self):
        pondebugs('getBoolean: ' + str(self.hay))
        return self.hay and True or False

    boolean = property(getBoolean)

    @cached
    def getValue(self):
        pondebugs('getValue: ' + str(self.hay))
        return self.hay

    value = property(getValue)
