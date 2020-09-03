from enigma import eSize, ePoint
from Tools.Directories import fileExists, resolveFilename, SCOPE_SKIN
from Components.config import config

def openspaSB(objectoself, nombrelista = 'lista', barra = 'barrascroll', altoitem = 25, imagen = None):
    nombrebarraArr = barra + '_arr'
    nombrebarraAbj = barra + '_abj'
    numele = 999
    if nombrelista == barra:
        nombrelista = nombrebarraArr
    elif not barra == 'servicelist':
        try:
            numele = len(objectoself[nombrelista].list)
        except:
            pass

    try:
        alto = objectoself[nombrelista].instance.size().height()
        elepag = int(alto / altoitem)
        if numele > elepag:
            pass
        else:
            objectoself[nombrebarraArr].hide()
            objectoself[nombrebarraAbj].hide()
            return
        ancho = objectoself[nombrelista].instance.size().width()
        if ancho > 20:
            if imagen:
                nomskin = str(config.skin.primary_skin.value).split('/')[0]
                rutaSkin = resolveFilename(SCOPE_SKIN) + nomskin + '/'
                if fileExists(rutaSkin + 'scroll.png'):
                    laimagen = rutaSkin + 'scroll.png'
                    objectoself[nombrebarraArr].instance.setPixmapFromFile(laimagen)
                else:
                    return
                if fileExists(rutaSkin + 'scrollb.png'):
                    laimagen = laimagen = rutaSkin + '/scrollb.png'
                    objectoself[nombrebarraAbj].instance.setPixmapFromFile(laimagen)
                else:
                    return
            posx = objectoself[nombrelista].instance.position().x()
            posy = objectoself[nombrelista].instance.position().y()
            wsize = (20, alto - 30)
            asizex = objectoself[nombrebarraArr].instance.size().width()
            asizey = objectoself[nombrebarraArr].instance.size().height()
            if not asizex == 20 or not asizey == alto - 30:
                objectoself[nombrebarraArr].instance.resize(eSize(*wsize))
            wsize = (20, 30)
            asizex = objectoself[nombrebarraAbj].instance.size().width()
            asizey = objectoself[nombrebarraAbj].instance.size().height()
            if not asizex == 20 or not asizey == 30:
                objectoself[nombrebarraAbj].instance.resize(eSize(*wsize))
            ax = objectoself[nombrebarraArr].instance.position().x()
            ay = objectoself[nombrebarraArr].instance.position().y()
            if not ax == posx + ancho - 20 or not ay == posy:
                objectoself[nombrebarraArr].instance.move(ePoint(posx + ancho - 20, posy))
            ax = objectoself[nombrebarraAbj].instance.position().x()
            ay = objectoself[nombrebarraAbj].instance.position().y()
            if not ax == posx + ancho - 20 or not ay == posy + alto - 30:
                objectoself[nombrebarraAbj].instance.move(ePoint(posx + ancho - 20, posy + alto - 30))
            objectoself[nombrebarraArr].show()
            objectoself[nombrebarraAbj].show()
    except:
        pass
