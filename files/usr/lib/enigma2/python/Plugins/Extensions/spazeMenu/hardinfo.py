from Components.About import about
from Tools.HardwareInfo import HardwareInfo
from boxbranding import getMachineName, getMachineBrand
from Tools.Directories import fileExists

def tipoModelo(completo = False):
    creamodeloinfo()
    cret = 'azbox'
    try:
        textomodelo = getMachineBrand().lower()
        namemachine = getMachineName().lower()
        if completo:
            return textomodelo or namemachine
        if 'azbox' in textomodelo:
            cret = 'azbox'
        elif 'opticum' in textomodelo or namemachine == 'evo':
            cret = 'opticum'
        elif 'visionnet' in textomodelo:
            cret = 'vnet'
        elif 'xtrend' in textomodelo:
            cret = 'xtrend'
        elif 'gigablue' in textomodelo:
            cret = 'gigablue'
        elif 'golden media' in textomodelo:
            cret = 'golden'
        elif 'vu+' in textomodelo:
            cret = 'vuplus'
        elif namemachine == 'e3hd' or namemachine == 'e3hd-c':
            cret = 'e3hd'
        elif 'mk-digital' in textomodelo:
            cret = 'mkdigital'
        elif 'zgemma' in textomodelo:
            cret = 'zgemma'
        elif 'wetek' in textomodelo:
            cret = 'wetek'
        elif 'galaxy innovations' in textomodelo:
            cret = 'gi'
        elif 'formuler' in textomodelo:
            cret = 'formuler'
    except:
        return 'azbox'

    return cret


def creamodeloinfo():
    fileinfo = '/usr/bin/OpenSPA.info'
    if not fileExists(fileinfo):
        boxime = HardwareInfo().get_device_name()
        hard = about.getHardwareTypeString()
        inihard = hard
        modelo = 'NA'
        if boxime == 'elite':
            modelo = '[100]AzboxHD Elite-mipsel'
        elif boxime == 'me':
            modelo = '[101]AzboxHD Me-mipsel'
        elif boxime == 'minime':
            modelo = '[102]AzboxHD MiniMe-mipsel'
        elif boxime == 'premium':
            modelo = '[103]AzboxHD Premium-mipsel'
        elif boxime == 'premium+':
            modelo = '[104]AzboxHD Premium Plus-mipsel'
        elif boxime == 'ultra':
            modelo = '[105]AzboxHD Ultra-mipsel'
        else:
            boxname = getMachineName().lower()
            hard = '[' + hard.lower().replace(' ', '') + ']'
            if boxname == 'duo':
                modelo = '[200]Vu+ Duo-mipsel'
            elif boxname == 'solo':
                modelo = '[201]Vu+ Solo-mipsel'
            elif boxname == 'ultimo':
                modelo = '[202]Vu+ Ultimo-mipsel'
            elif boxname == 'uno':
                modelo = '[203]Vu+ Uno-mipsel'
            elif boxname == 'solo\xc2\xb2':
                modelo = '[204]Vu+ Solo2-mipsel'
            elif boxname == 'duo\xc2\xb2':
                modelo = '[205]Vu+ Duo2-mipsel'
            elif boxname == 'solo se':
                modelo = '[206]Vu+ Solo SE-mipsel'
            elif boxname == 'zero':
                modelo = '[207]Vu+ Zero-mipsel'
            elif boxname == 'solo4k':
                modelo = '[208]Vu+ Solo 4K-ARM'
            elif 'elite' in hard:
                modelo = '[100]AzboxHD Elite-mipsel'
            elif 'me' in hard:
                modelo = '[101]AzboxHD Me-mipsel'
            elif 'minime' in hard:
                modelo = '[102]AzboxHD MiniMe-mipsel'
            elif 'premium' in hard:
                modelo = '[103]AzboxHD Premium-mipsel'
            elif 'premium+' in hard or 'premiumplus' in hard:
                modelo = '[104]AzboxHD Premium Plus-mipsel'
            elif 'ultra' in hard:
                modelo = '[105]AzboxHD Ultra-mipsel'
            elif boxname == 'spark 990 lx' or boxname == 'spark reloaded':
                modelo = '[300]Golden Media Spark 990/Reloaded-sh4'
            elif boxname == 'spark one' or boxname == 'spark triplex':
                modelo = '[301]Golden Media Spark One/Triplex-sh4'
            elif boxname == 'ax odin' or boxname == 'ax odin-c' or boxname == 'evo':
                modelo = '[400]AX-ODIN/ODINM7-mipsel'
            elif boxname == 'e3hd' or boxname == 'e3hd-c':
                modelo = '[410]E3HD-mipsel'
            elif 'et9000'.lower() in hard:
                modelo = '[500]ET9000-mipsel'
            elif 'et9200'.lower() in hard:
                modelo = '[501]ET9200-mipsel'
            elif 'et9500'.lower() in hard:
                modelo = '[502]ET9500-mipsel'
            elif 'et6500'.lower() in hard:
                modelo = '[510]ET6500-mipsel'
            elif 'et6000'.lower() in hard:
                modelo = '[511]ET6000-mipsel'
            elif 'et5000'.lower() in hard:
                modelo = '[520]ET5000-mipsel'
            elif 'et4x00'.lower() in hard:
                modelo = '[530]ET4000-mipsel'
            elif 'et8000'.lower() in hard:
                modelo = '[540]ET8000-mipsel'
            elif 'et10000'.lower() in hard:
                modelo = '[550]ET10000-mipsel'
            elif boxname == 'xp1000':
                modelo = '[600]XP1000-mipsel'
            elif boxname == 'marvel 1':
                modelo = '[700]VisionNet Marvel1-mipsel'
            elif boxname == '800 se':
                modelo = '[800]GigaBlue 800SE-mipsel'
            elif boxname == '800 se plus':
                modelo = '[801]GigaBlue 800SEPLUS-mipsel'
            elif boxname == '800 solo':
                modelo = '[802]GigaBlue 800SOLO-mipsel'
            elif boxname == '800 ue':
                modelo = '[803]GigaBlue 800UE-mipsel'
            elif boxname == '800 ue plus':
                modelo = '[804]GigaBlue 800UEPLUS-mipsel'
            elif boxname == 'ipbox':
                modelo = '[805]GigaBlue IPBOX-mipsel'
            elif boxname == 'quad':
                modelo = '[806]GigaBlue QUAD-mipsel'
            elif boxname == 'quad plus':
                modelo = '[807]GigaBlue QUADPLUS-mipsel'
            elif boxname == 'ultra se':
                modelo = '[808]GigaBlue ULTRASE-mipsel'
            elif boxname == 'ultra ue':
                modelo = '[809]GigaBlue ULTRAUE-mipsel'
            elif boxname == 'x1':
                modelo = '[810]GigaBlue X1-mipsel'
            elif boxname == 'x3':
                modelo = '[811]GigaBlue X3-mipsel'
            elif boxname == 'star h1':
                modelo = '[900]ZGemma-Star H1-mipsel'
            elif boxname == 'star h2':
                modelo = '[901]ZGemma-Star H2-mipsel'
            elif boxname == 'star s':
                modelo = '[902]ZGemma-Star S-mipsel'
            elif boxname == 'star 2s':
                modelo = '[903]ZGemma-Star 2S-mipsel'
            elif boxname == 'h.s':
                modelo = '[904]ZGemma H.S-mipsel'
            elif boxname == 'h.2s':
                modelo = '[905]ZGemma H.2S-mipsel'
            elif boxname == 'h.2h':
                modelo = '[906]ZGemma H.2H-mipsel'
            elif boxname == 'play':
                modelo = '[1000]WeTek Play-ARM'
            elif boxname == 'et-7000 mini' or boxname == 'et7000':
                modelo = '[1100]Galaxy Innovations ET7x00 Mini-mipsel'
            elif boxname == 'f1':
                modelo = '[1200]Formuler F1-mipsel'
            elif boxname == 'f3':
                modelo = '[1201]Formuler F3-mipsel'
            else:
                modelo = '[0]' + inihard + '/' + boxime
                fileinfo = fileinfo.replace('OpenSPA.info', 'OpenSPA_ERROR.info')
        try:
            open(fileinfo, 'w').write(modelo)
        except:
            pass
