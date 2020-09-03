from Components.Converter.Converter import Converter
from Components.Element import cached
from Poll import Poll
import gettext
from Tools.Directories import fileExists

class ECMJR(Poll, Converter):
    ECMINFO = 0

    def __init__(self, type):
        Converter.__init__(self, type)
        Poll.__init__(self)
        self.poll_interval = 10000
        self.poll_enabled = True
        if type == 'EcmInfo':
            self.poll_interval = 3000
            self.type = 0

    @cached
    def getText(self):
        if self.type == 0:
            if fileExists('/tmp/ecm.info'):
                try:
                    cadena = []
                    f = open('/tmp/ecm.info', 'r')
                    linies = f.readlines()
                    for line in linies:
                        if not (line.startswith('cw') or line.startswith('chid') or line.startswith('pid') or line.startswith('CW') or line.startswith('share')):
                            cadena.append(line)

                    f.close()
                    g = open('/tmp/ecmJR.log', 'w')
                    for i in cadena:
                        g.writelines(i)

                    g.close()
                    h = open('/tmp/ecmJR.log', 'r')
                    content = h.read()
                    h.close()
                except:
                    content = ''

            else:
                content = 'No ECM\nCANAL FTA'
        text = content
        return text

    text = property(getText)
