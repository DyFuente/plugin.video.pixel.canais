import re
import json
import xbmc
import urllib2
import xbmcgui
import sqlite3
import xbmcaddon
import xbmcplugin
import unicodedata
import os
import shutil
import cookielib
import uuid

#log no kodi
#/storage/emulated/0/Android/data/org.xbmc.kodi/files/.kodi/userdata/addon_data/plugin.video.pixel.canais/pics_nao_encontradas.txt

#from bs4 import BeautifulSoup

__addon__ = xbmcaddon.Addon()
__addonname__ = __addon__.getAddonInfo('name')
__icon__ = __addon__.getAddonInfo('icon')
#__path__ = xbmc.translatePath(__addon__.getAddonInfo('path')).decode("utf-8")
__userdata__ = xbmc.translatePath(__addon__.getAddonInfo('profile')).decode("utf-8")
__addonid__ = __addon__.getAddonInfo('id')
__path__ = __addon__.getAddonInfo('path')
#__IconDefault__ = xbmc.translatePath(os.path.join( __path__,'resources', 'media', 'default.png'))

#Defs
__useCustomPics__ = True if __addon__.getSetting('useCustomPics').upper() == 'TRUE' else False
__formatOfCustomPic__ = __addon__.getSetting('formatOfCustomPic').upper()
__typeOfCustomPic__ = __addon__.getSetting('typeOfCustomPic').upper()
__folderCust__ = __addon__.getSetting('folderCust')
__urlCustom__ = __addon__.getSetting('urlCustom')
__verifyURL__ = True if __addon__.getSetting('verifyURL').upper() == 'TRUE' else False
__urlPicons__ = "https://hk319yfwbl.execute-api.sa-east-1.amazonaws.com/prod"

# configure repository
repodir = xbmc.translatePath("special://home/addons/repository.pixelalternative")
if not os.path.exists(repodir):
    os.makedirs(repodir)
if not os.path.isfile(os.path.join(repodir, 'addon.xml')):
    shutil.copyfile(os.path.join( __path__,'resources', 'repo', 'addon.xml'),os.path.join(repodir, "addon.xml"))
# end configure repository

#import ptvsd
#ptvsd.enable_attach(secret = 'pwd')
#ptvsd.wait_for_attach()

url_base = 'http://www.netcombo.com.br/static/html/juntinho/components/combo_cidades/%s'

def CATEGORIAS():
    addDir('Definir Picons dos Canais', '', 1, '', False)
    addDir('Criar grupos e separar canais', '', 2, '')
    # addDir('Remover Grupos', '', 7, '', False)
    addDir('Ocultar canais que iniciam com PG-', '', 3, '', False)
    addDir('Ocultar canais SD quando houver em HD', '', 4, '', False)
    addDir('Ocultar canais informativos NET', '', 5, '', False)
    addDir('Ocultar canais adultos', '', 7, '', False)
    addDir('Reexibir todos os canais', '', 6, '', False)

# def notifyLog(message, level=xbmc.LOGDEBUG):
# 	xbmc.log('[%s]: %s' % (__addonid__, message.encode('utf-8')), level)
# 	# xbmc.log('[%s]: %s' % (__addonid__, message), level)

def log(msg, label=''):
    if label:
        combined_message = 'service.pvr.audio.subtitles ::-:: ' + str( label.encode('utf-8') ) + ' = ' + str( msg.encode('utf-8') )
    else:
        combined_message = 'service.pvr.audio.subtitles ::-:: ' + str( msg.encode('utf-8') )

    xbmc.log(combined_message, xbmc.LOGNOTICE)

# Obter Retorno/Cookie #
class abrir_url(object):
    def __init__(self, url, close=True, proxy=None, post=None, mobile=False, referer=None, cookie=None, output='',
                 timeout='10'):
        if not proxy == None:
            proxy_handler = urllib2.ProxyHandler({'http': '%s' % (proxy)})
            opener = urllib2.build_opener(proxy_handler, urllib2.HTTPHandler)
            opener = urllib2.install_opener(opener)
        if output == 'cookie' or not close == True:

            cookie_handler = urllib2.HTTPCookieProcessor(cookielib.LWPCookieJar())
            opener = urllib2.build_opener(cookie_handler, urllib2.HTTPBasicAuthHandler(), urllib2.HTTPHandler())
            opener = urllib2.install_opener(opener)
        if not post == None:
            request = urllib2.Request(url, post)
        else:
            request = urllib2.Request(url, None)
        if mobile == True:
            request.add_header('User-Agent',
                               'Mozilla/5.0 (iPhone; CPU; CPU iPhone OS 4_0 like Mac OS X; en-us) AppleWebKit/532.9 (KHTML, like Gecko) Version/4.0.5 Mobile/8A293 Safari/6531.22.7')
        else:
            request.add_header('User-Agent',
                               'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.57 Safari/537.36')
        if not referer == None:
            request.add_header('Referer', referer)
        if not cookie == None:
            request.add_header('cookie', cookie)
        response = urllib2.urlopen(request, timeout=int(timeout))
        if output == 'cookie':
            result = str(response.headers.get('Set-Cookie'))
        elif output == 'geturl':
            result = response.geturl()
        else:
            result = response.read()
        if close == True:
            response.close()
        self.result = result

# Adicionar Pasta/Link #
def addDir(name, url, mode, iconimage, pasta=True, total=1):
    u = sys.argv[0] + "?url=" + urllib2.quote(url) + "&mode=" + str(mode) + "&name=" + urllib2.quote(name)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    #liz.setProperty('fanart_image', fanart)
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=pasta, totalItems=total)
    return ok

# Obter Parametros #
def get_params():
    param = []
    paramstring = sys.argv[2]
    if len(paramstring) >= 2:
        params = sys.argv[2]
        cleanedparams = params.replace('?', '')
        if (params[len(params) - 1] == '/'):
            params = params[0:len(params) - 2]
        pairsofparams = cleanedparams.split('&')
        param = {}
        for i in range(len(pairsofparams)):
            splitparams = {}
            splitparams = pairsofparams[i].split('=')
            if (len(splitparams)) == 2:
                param[splitparams[0]] = splitparams[1]

    return param

# Executar comandos no KODI #
def executeJSONRPC(method, **kwargs):
    payload = json.dumps({
        'jsonrpc': '2.0',
        'method': method,
        'id': 1,
        "params": kwargs,
    })
    data = xbmc.executeJSONRPC(payload)
    return json.loads(data).get('result', None)

def definir_picons(url):
    log('canal start definir_picons')
    xbmc.executebuiltin('ActivateWindow(busydialog)')

    # Obtendo canais
    TVDB = xbmc.translatePath('special://userdata/Database/TV29.db')
    conn = sqlite3.connect(TVDB)
    cursor = conn.cursor()
    
    # lendo os dados
    cursor.execute("""
    select idChannel, bIsUserSetIcon, sIconPath, sChannelName from channels order by sChannelName;
    """)
    
    canais = cursor.fetchall()
    
    uuidOne = uuid.getnode()
    # Atualizando canais
    # alterando os dados da tabela

    addondata = xbmc.translatePath(__addon__.getAddonInfo('profile'))

    if not os.path.exists(addondata):
        os.makedirs(addondata)
    if __useCustomPics__ and __typeOfCustomPic__ == 'LOCAL':
        localpics = xbmc.translatePath(os.path.join(addondata,'picons'))
        if not os.path.exists(localpics):
            os.makedirs(localpics)

    notfoundfile = xbmc.translatePath(os.path.join(addondata,'pics_nao_encontradas.txt'))
    notfoundF = open(notfoundfile, 'w')

    listafile = xbmc.translatePath(os.path.join(addondata,'lista_de_canais.txt'))
    listaF = open(listafile, 'w')

    if __folderCust__ == '' and __useCustomPics__ and __typeOfCustomPic__ == 'LOCAL':
        xbmc.executebuiltin('Dialog.Close(busydialog)')
        xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%(__addonname__, 'Caminho das imagens invalido.', 5000, __icon__))
        quit()

    if __urlCustom__ == '' and __useCustomPics__ and __typeOfCustomPic__ == 'URL':
        xbmc.executebuiltin('Dialog.Close(busydialog)')
        xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%(__addonname__, 'URL das imagens invalido.', 5000, __icon__))
        quit()

    if not __useCustomPics__:
        listaCanais = []
        # log(str(uuidOne))
        for linha in canais:
            canal = cleanChannelName(linha[3])
            if canal.strip() != "":
                listaCanais.append(canal)
        listaCanais = list(dict.fromkeys(listaCanais))
        data = {'src': 'kodi','node': uuidOne, 'listChannel': listaCanais}
        data = json.dumps( data )

        # log(data)
        req = urllib2.Request(__urlPicons__, data, {'Content-Type': 'application/json'})
        fil = urllib2.urlopen(req)

        # log( fil )

        response = json.load(fil)
        fil.close()

        respListaPicons = json.loads(response)

        piconsList = respListaPicons['listaPicons']

        # Salvar lista de canais internos
        # log( str( respListaPicons['listaCanaisInternos'] ) )
        canaisInternos = xbmc.translatePath(os.path.join( addondata, 'canaisinternos.txt'))
        canaisI = open(canaisInternos, 'w')
        canaisI.write(json.dumps(respListaPicons['listaCanaisInternos']))
        canaisI.close()
        # Salvar lista de canais internos

        # Salvar lista de canais adultos
        canaisInternos = xbmc.translatePath(os.path.join( addondata, 'canaisadultos.txt'))
        canaisI = open(canaisInternos, 'w')
        canaisI.write(json.dumps(respListaPicons['listaCanaisAdultos']))
        canaisI.close()
        # Salvar lista de canais adultos
    
    for linha in canais:
        canalclean = cleanChannelName(linha[3])
        icone = ''
        if not __useCustomPics__:
            for chan in piconsList:
                if canalclean == chan[0]:
                    icone = chan[1]

        else:
            extF = '.'+ __formatOfCustomPic__.lower()
            if __typeOfCustomPic__ == 'URL':
                # web 
                urlFinal = __urlCustom__
                if not __urlCustom__.endswith('/'):
                    urlFinal = __urlCustom__ + "/"
                url = urlFinal + 'canal{0}' + extF
                icone = url.format(canalclean)

                if __verifyURL__:
                    try:
                        urllib2.urlopen(icone)
                    # except urllib2.HTTPError, e:
                    except (urllib2.HTTPError, e) as err:
                        # print(e.code)
                        # xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%(__addonname__, 'http error ' + str(e.code) + icone, 100, __icon__))
                        notfoundF.write(icone + '\n')
                    # end web
            else:
                if __folderCust__ != '':
                    fName = 'canal' + canalclean + extF
                    iconeSrc = xbmc.translatePath(os.path.join( __folderCust__, fName))
                    icone = xbmc.translatePath(os.path.join( localpics, fName))
                    if not os.path.exists(iconeSrc):
                        notfoundF.write(iconeSrc + '\n')
                    else:
                        shutil.copyfile(iconeSrc,icone)
                else:
                    icone = ''

        listaF.write(icone + "," + linha[3].encode('ascii', 'ignore') + '\n')
        log('Alterando picon de ' + linha[3] + ' --> ' + icone)
        cursor.execute("""UPDATE channels SET bIsUserSetIcon = 1, sIconPath = ? WHERE idChannel = ? """, (icone, linha[0]))

    notfoundF.close()
    listaF.close()

    conn.commit()
    conn.close()

    xbmc.executebuiltin('Dialog.Close(busydialog)')

def cleanChannelName(ch):
    return re.sub(re.compile('\W'), '', ''.join(c.lower() for c in unicodedata.normalize('NFKD', ch.replace("+", "mais")).encode('ascii', 'ignore') if not c.isspace()))

def remover_channels():
    # Obtendo canais
    xbmc.executebuiltin('ActivateWindow(busydialog)')
    TVDB = xbmc.translatePath('special://userdata/Database/TV29.db')
    conn = sqlite3.connect(TVDB)
    cursor = conn.cursor()
    
    cursor.execute("""
    select idChannel, bIsUserSetIcon, sIconPath, sChannelName from channels where sChannelName like "%PG-%";
    """)

    canais = cursor.fetchall()
    
    for linha in canais:
        cursor.execute("""UPDATE channels SET bIsHidden = 1 WHERE sChannelName = ? """, (linha[3],))
    # Ocultando grupo DVB-C 
    cursor.execute("""
    select idGroup, bIsRadio, sName, bIsHidden from channelgroups;
    """)
    grupoCanais = cursor.fetchall()

    for grupo in grupoCanais:
        print(grupo)
        if grupo[2] == 'DVB-C' and grupo[1] == False:
            print("ocultar grupo " + str(grupo[0]) + " " + str(grupo[2]))

            cursor.execute("""
            UPDATE channelgroups SET bIsHidden = 1 where idGroup = ?;
            """, (grupo[0],))
        
    conn.commit()
    conn.close()
    xbmc.executebuiltin('Dialog.Close(busydialog)')

def ocultar_canais_sd():
    # Obtendo canais
    xbmc.executebuiltin('ActivateWindow(busydialog)')
    log("ocultar canais sd")
    TVDB = xbmc.translatePath('special://userdata/Database/TV29.db')
    conn = sqlite3.connect(TVDB)
    cursor = conn.cursor()
    
    listaCanaisTmp = []
    cursor.execute("""
    select idChannel, bIsUserSetIcon, sIconPath, sChannelName from channels where bIsRadio =? order by sChannelName ;
    """,(False,))

    canais = cursor.fetchall()

    cursor.execute("""
    select idChannel, iChannelNumber from map_channelgroups_channels;
    """)
    numeroCanais = cursor.fetchall()

    for canal in canais:
        # log("=>" + canal[3] + "<==>" + cleanChannelName(canal[3]) + "<==>" +  canal[3].lower().replace(' hd', '') + "<==" )
        addC = True
        canalNum = 0
        for n in numeroCanais:
            if canal[0] == n[0]:
                canalNum = n[1]
        for l in listaCanaisTmp:
            if canal[3].lower().replace(' hd', '') == l[1].lower().replace(' hd', ''):
                if canalNum > l[0]:
                    # log("sd " + l[1] + " " + str(l[0]) + " " + str(canal[0]))
                    listaCanaisTmp.remove(l)
                else:
                    # log("sd break " + canal[3] )
                    addC = False
                    break

        if addC == True:
            listaCanaisTmp.append( [canalNum,canal[3]] )

    for canal in canais:
        for n in numeroCanais:
            if canal[0] == n[0]:
                canalNum = n[1]
        ocultar = True
        for l in listaCanaisTmp:
            if canalNum == l[0]:
                ocultar = False

        if ocultar == True:
            log("ocultando " + str(canalNum) + " " + canal[3])
            cursor.execute("""UPDATE channels SET bIsHidden = 1 WHERE idChannel = ? """, (canal[0],))
    # Ocultando grupo DVB-C 
    cursor.execute("""
    select idGroup, bIsRadio, sName, bIsHidden from channelgroups;
    """)
    grupoCanais = cursor.fetchall()

    for grupo in grupoCanais:
        print(grupo)
        if grupo[2] == 'DVB-C' and grupo[1] == False:
            print("ocultar grupo " + str(grupo[0]) + " " + str(grupo[2]))

            cursor.execute("""
            UPDATE channelgroups SET bIsHidden = 1 where idGroup = ?;
            """, (grupo[0],))
        
    conn.commit()
    conn.close()
    xbmc.executebuiltin('Dialog.Close(busydialog)')

def exibir_todos_canais():
    # Obtendo canais
    xbmc.executebuiltin('ActivateWindow(busydialog)')
    TVDB = xbmc.translatePath('special://userdata/Database/TV29.db')
    conn = sqlite3.connect(TVDB)
    cursor = conn.cursor()
    
    cursor.execute("""UPDATE channels SET bIsHidden = 0 """)
    cursor.execute("""UPDATE channelgroups SET bIsHidden = 0 """)

    conn.commit()
    conn.close()
    xbmc.executebuiltin('Dialog.Close(busydialog)')

def remover_canais_internos():
    log("ocultar canais internos")
    resp = False
    addondata = xbmc.translatePath(__addon__.getAddonInfo('profile'))

    # canaisFile = xbmc.translatePath(os.path.join( __path__, 'canaisnet.txt'))
    canaisInternos = xbmc.translatePath(os.path.join( addondata, 'canaisinternos.txt'))

    if os.path.isfile(canaisInternos):
        xbmc.executebuiltin('ActivateWindow(busydialog)')
        # Obtendo canais
        TVDB = xbmc.translatePath('special://userdata/Database/TV29.db')
        conn = sqlite3.connect(TVDB)
        cursor = conn.cursor()
        resp = True
        with open(canaisInternos) as json_file:  
            data = json.load(json_file)
            # log( str(data) )
            cursor.execute("""
            select idChannel, bIsUserSetIcon, sIconPath, sChannelName from channels order by sChannelName;
            """)

            canais = cursor.fetchall()
            for canal in canais:                
                # log(canal[3] + " " + cleanChannelName(canal[3]))
                if cleanChannelName(canal[3]) in data:
                    log("ocultando " + canal[3] + " " + cleanChannelName(canal[3]))
                    cursor.execute("""UPDATE channels SET bIsHidden = 1 WHERE idChannel = ? """, (canal[0],))
        # Ocultando grupo DVB-C 
        cursor.execute("""
        select idGroup, bIsRadio, sName, bIsHidden from channelgroups;
        """)
        grupoCanais = cursor.fetchall()

        for grupo in grupoCanais:
            print(grupo)
            if grupo[2] == 'DVB-C' and grupo[1] == False:
                print("ocultar grupo " + str(grupo[0]) + " " + str(grupo[2]))

                cursor.execute("""
                UPDATE channelgroups SET bIsHidden = 1 where idGroup = ?;
                """, (grupo[0],))

        conn.commit()
        conn.close()
        xbmc.executebuiltin('Dialog.Close(busydialog)')
    else:
        xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%(__addonname__, 'Necessario definir os picons antes.', 3000, __icon__))

    # elif os.path.isfile(canaisFile):
    #     # notifyLog(canaisFile)
    #     in_file = open(canaisFile, "r") 
    #     canaislist = in_file.readlines() 
    #     in_file.close()

    #     cursor.execute("""
    #     select idChannel, bIsUserSetIcon, sIconPath, sChannelName from channels order by sChannelName;
    #     """)

    #     canais = cursor.fetchall()

    #     for canalRem in canaislist:
    #         canalRemStr = canalRem.decode('utf-8').strip()
    #         for linha in canais:
    #             if canalRemStr.lower() == linha[3].lower():
    #                 cursor.execute("""UPDATE channels SET bIsHidden = 1 WHERE idChannel = ? """, (linha[0],))
    #                 # cursor.execute("""DELETE FROM channels WHERE idChannel=?""", (linha[0],))
    return resp

def ocultar_canais_adultos():
    log("ocultar canais internos")
    resp = False
    addondata = xbmc.translatePath(__addon__.getAddonInfo('profile'))

    canaisAdultos = xbmc.translatePath(os.path.join( addondata, 'canaisadultos.txt'))
    if os.path.isfile(canaisAdultos):
        xbmc.executebuiltin('ActivateWindow(busydialog)')

        # Obtendo canais
        TVDB = xbmc.translatePath('special://userdata/Database/TV29.db')
        conn = sqlite3.connect(TVDB)
        cursor = conn.cursor()
        with open(canaisAdultos) as json_file:  
            data = json.load(json_file)
            # log( str(data) )
            cursor.execute("""
            select idChannel, bIsUserSetIcon, sIconPath, sChannelName from channels order by sChannelName;
            """)

            canais = cursor.fetchall()
            for canal in canais:                
                # log(canal[3] + " " + cleanChannelName(canal[3]))
                if cleanChannelName(canal[3]) in data:
                    log("ocultando " + canal[3] + " " + cleanChannelName(canal[3]))
                    cursor.execute("""UPDATE channels SET bIsHidden = 1 WHERE idChannel = ? """, (canal[0],))
        # Ocultando grupo DVB-C 
        cursor.execute("""
        select idGroup, bIsRadio, sName, bIsHidden from channelgroups;
        """)
        grupoCanais = cursor.fetchall()

        for grupo in grupoCanais:
            print(grupo)
            if grupo[2] == 'DVB-C' and grupo[1] == False:
                print("ocultar grupo " + str(grupo[0]) + " " + str(grupo[2]))

                cursor.execute("""
                UPDATE channelgroups SET bIsHidden = 1 where idGroup = ?;
                """, (grupo[0],))

        conn.commit()
        conn.close()
        xbmc.executebuiltin('Dialog.Close(busydialog)')
        resp = True
    else:
        xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%(__addonname__, 'Necessario definir os picons antes.', 3000, __icon__))
    return resp

def listar_cidades():
    codigo_fonte = abrir_url(url_base % 'cidades.js').result.replace('var data =', '{"data":').replace(',\n];', ']}')
    cidades = json.loads(codigo_fonte)

    for c in cidades[u'data']:
        addDir((c[u'label']).encode('utf-8'), (url_base % ('data/%s.json' % c[u'rel'])), 4, '', False)

def remover_grupos():
    # Obtendo canais
    TVDB = xbmc.translatePath('special://userdata/Database/TV29.db')
    conn = sqlite3.connect(TVDB)
    cursor = conn.cursor()

    # # excluindo canais dos grupos
    # cursor.execute("""
    # delete from map_channelgroups_channels where idGroup > 2;
    # """)

    # excluindo grupos
    cursor.execute("""
    delete from channelgroups where idGroup > 2;
    """)

    # cursor.execute("""
    # select iLastWatched, sName from channelgroups;
    # """)

    # canais = cursor.fetchall()
    # for canalRem in canais:
    #     notifyLog(str(canalRem[0]) + "<-->" + canalRem[1] + "<--")

    # cursor.execute("""
    # select idChannel, idGroup, iChannelNumber, iSubChannelNumber from map_channelgroups_channels;
    # """)

    # canais = cursor.fetchall()
    # for canalRem in canais:
    #     notifyLog(str(canalRem[0]) + "<-->" + str(canalRem[1]) + "<-->" + str(canalRem[2]) + "<-->" + str(canalRem[3]))


    conn.commit()
    conn.close()

def definir_grupos(url):
    # Obtendo canais
    TVDB = xbmc.translatePath('special://userdata/Database/TV29.db')
    conn = sqlite3.connect(TVDB)
    cursor = conn.cursor()

    # excluindo canais dos grupos
    cursor.execute("""
    delete from map_channelgroups_channels where idGroup > 2;
    """)

    # excluindo grupos
    cursor.execute("""
    delete from channelgroups where idGroup > 2;
    """)

    # obtendo canais dos grupos
    cursor.execute("""
    select idChannel, iChannelNumber from map_channelgroups_channels where idGroup = 2;
    """)
    
    canais = cursor.fetchall()
    grupos = json.loads(abrir_url(url).result)
    
    GP = 2
    for g in grupos[u'secoes']:
        GP += 1
        ng = (g[u'nome'][8:g[u'nome'].find('</strong>')])
        cursor.execute("""INSERT INTO channelgroups (idGroup, bIsRadio, iGroupType, sName, iLastWatched, bIsHidden, iPosition) VALUES (?, 0, 2, ?, 0, 0, 0); """, (GP, ng))
        for c in g[u'canais']:
            for n in canais:
                if int(c['novo']) == int(n[1]):
                    cursor.execute("""INSERT INTO map_channelgroups_channels (idChannel, idGroup, iChannelNumber, iSubChannelNumber) VALUES (?, ?, ?, 0); """, (n[0], GP, n[1]))
                    break

    conn.commit()
    conn.close()

params = get_params()
url = None
name = None
mode = None
iconimage = None

try:
    url = urllib2.unquote(params["url"])
except:
    pass
try:
    name = urllib2.unquote(params["name"])
except:
    pass
try:
    mode = int(params["mode"])
except:
    pass

try:
    iconimage = urllib2.unquote(params["iconimage"])
except:
    pass

print ("Mode: " + str(mode))
print ("URL: " + str(url))
print ("Name: " + str(name))
print ("Iconimage: " + str(iconimage))
print ("Parameters: " + sys.argv[2])

###############################################################################################################
#                                                   MODOS                                                     #
###############################################################################################################

if mode == None:
    CATEGORIAS()

elif mode == 2:
    listar_cidades()

elif mode == 3:
    remover_channels()
    xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%(__addonname__, 'Reinicie o KODI para aplicar as alteracoes.', 3000, __icon__))

elif mode == 1:
    definir_picons(url)
    xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%(__addonname__, 'Reinicie o KODI para aplicar as alteracoes.', 3000, __icon__))

# elif mode == 4:
#     definir_grupos(url)
#     xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%(__addonname__, 'Reinicie o KODI para aplicar as alteracoes.', 3000, __icon__))

elif mode == 4:
    ocultar_canais_sd()
    xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%(__addonname__, 'Reinicie o KODI para aplicar as alteracoes.', 3000, __icon__))

elif mode == 5:
    if ( remover_canais_internos() ):
        xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%(__addonname__, 'Reinicie o KODI para aplicar as alteracoes.', 3000, __icon__))

elif mode == 6:
    exibir_todos_canais()
    xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%(__addonname__, 'Reinicie o KODI para aplicar as alteracoes.', 3000, __icon__))

elif mode == 7:
    if ( ocultar_canais_adultos() ):
        xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%(__addonname__, 'Reinicie o KODI para aplicar as alteracoes.', 3000, __icon__))

# elif mode == 7:
#     remover_grupos();
#     xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%(__addonname__, 'Reinicie o KODI para aplicar as alteracoes.', 3000, __icon__))

xbmcplugin.endOfDirectory(int(sys.argv[1]))
