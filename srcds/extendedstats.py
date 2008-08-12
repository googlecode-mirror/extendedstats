##############################
###    Many Thanks To     ####
##############################
#
# Saul:             __import__ and especially for the hasattr(...) and callable(getattr(...)) in loadAddons(...)
# GODJonez:         __import__(...) and especially for the dict.copy() hint
# NATO_Hunter:      __import__(...)
# Jesse:            Tester
# theresthatguy:    Tester
# lindo81:          Tester, ran the addon on his server for testing. Many many thanks!
# darkranger:       Tester, ran the addon on his server for testing. Many many thanks!
# nexitem:          Tester, ran the addon on his server for testing. Many many thanks!
#
##############################
###        IMPORTS        ####
##############################

import es, playerlib, vecmath, popuplib
import time, path, cPickle, sys, traceback, psyco, hashlib, base64, urllib
psyco.full()

##############################
###  STATIC CONFIGURATION  ###
##############################

scfg = __import__('extendedstats.staticConfiguration',fromlist=['extendedstats'],level=0)
if not 'default' in scfg.addonList:
    scfg.addonList.append('default')

##############################
###        GLOBALS        ####
##############################

info = es.AddonInfo()
info.version        = '0.1.0:117'
info.versionname    = 'Bettina'
info.basename       = 'extendedstats'
info.name           = 'eXtended stats'
info.author         = 'Ojii with loads of help by others'
info.description    = 'Stores a lot of information about players'

gamepath = path.path(str(es.ServerVar('eventscripts_gamedir')))
xspath = gamepath.joinpath('addons/eventscripts/extendedstats/')
methodspath = xspath.joinpath('methods/')
addonspath = xspath.joinpath('addons/')
databasepath = xspath.joinpath('data.cpickle')

game = str(es.ServerVar('eventscripts_gamedir')).replace('\\', '/').rpartition('/')[2]
methods = {}
addoncommands = {}
reggedccmd = []
reggedscmd = []
ignore_keys = []
live_keys = {}
data = {}
errorhashes = []
pending = {}
new_player = {}
cmdhelp = {}
new_dcfg = {}

##############################
###     DEBUG HELPER      ####
##############################

errorlog = xspath.joinpath('log.txt')
if not errorlog.isfile():
    errorlog.touch()
    
def getmd5(text):
    h = hashlib.md5()
    h.update(text)
    return h.hexdigest()
    
def excepter(type1, value1, traceback1):
    mystr = traceback.format_exception(type1, value1, traceback1)
    L = ['ERROR: %s' % time.strftime("%d %b %Y %H:%M:%S"),'XS Version: %s' % info.version,'']
    L.append('Mapname: %s' % str(es.ServerVar('eventscripts_currentmap')))
    L.append('Players: %s (%s Bots)' % (len(es.getUseridList()),len(playerlib.getUseridList('#bot'))))
    for x in mystr:
        es.dbgmsg(0, x[:-1])
        L.append(x[:-1])
    L.append('')
    hsh = getmd5(''.join(L))
    if not hsh in errorhashes:
        errorhashes.append(hsh)
        L += errorlog.lines(retain=False)
        errorlog.write_lines(L)
        
if scfg.debug:
    sys.excepthook = excepter
    
def es_map_start(ev):
    L = ['NEWMAP: %s' % time.strftime("%d %b %Y %H:%M:%S"),'XS Version: %s' % info.version,'']
    L.append('Mapname: %s' % ev['mapname'])
    L.append('Players: %s (%s Bots)' % (len(es.getUseridList()),len(playerlib.getUseridList('#bot'))))
    L.append('')
    L += errorlog.lines(retain=False)
    errorlog.write_lines(L)
    dcfg.sync()
    
def dbg(text):
    es.dbgmsg(int(dcfg['debuglevel']),text)

##############################
### LOAD, HELPERS, PUBLICS ###
##############################

### Loading and Unloading ###

def load():
    dbg( '')
    dbg( 'XS: Loading...')
    loadDatabase()
    loadAddons()
    checkUpgrade()
    loadPackages()
    fillDatabase()
    es.regsaycmd(scfg.say_command_prefix + scfg.command_help,'extendedstats/cmd_help')
    es.regclientcmd(scfg.command_help,'extendedstats/cmd_help')
    loadCVARS()
    loadMenus()
    dbg( 'XS: Registered methods:')
    for method in methods:
        dbg( '    %s' % method)
    dbg( 'XS: Standard new_player (%s keys):' % len(new_player))
    for key in new_player:
        dbg( '    %s: %s' % (key,new_player[key]))
    dcfg.sync()
    dbg( 'XS: Loaded successfully (%s: %s)' % (info.versionname,info.version))
    dbg( '')

def unload():
    es.unregsaycmd('!help')
    for addon in addonsunloaders:
        addon()
    saveDatabase()
    unloadCommands()
    
def loadDatabase():
    global data
    if databasepath.isfile():
        dbg( 'XS: Loading database')
        dbf = databasepath.open('rb')
        data = cPickle.load(dbf)
        dbf.close()
        
def saveDatabase():
    dbg( 'XS: Saving database')
    dbf = databasepath.open('wb')
    cPickle.dump(data,dbf)
    dbf.close()
        
def loadAddons():
    global new_player, addonsunloaders
    addonsunloaders = []
    if scfg.allAddons:
        for addon in addonspath.files():
            if addon.endswith('.py') and not addon.namebase == '__init__':
                name = addon.namebase
                addonmodule = __import__('extendedstats.addons.%s'%name, fromlist=['addons', name])
                if hasattr(addonmodule,'new_player'):
                    new_player.update(addonmodule.new_player)
                    dbg( 'XS: new_player scheme added for %s' % name)
                else:
                    dbg( 'XS: no new_player scheme in %s' % name)             
                if callable(getattr(addonmodule, 'load', None)):
                    addonmodule.load()
                else:
                    dbg( 'XS: no loader in %s' % name)
                if callable(getattr(addonmodule, 'unload', None)):
                    addonunloader = addonmodule.unload
                    addonsunloaders.append(addonunloader)
                else:
                    dbg( 'XS: no unloader in %s' % name)
    else:
        for name in scfg.addonList:
            af = addonspath.joinpath('%s.py' % name)
            if af.isfile():
                addonmodule = __import__('extendedstats.addons.%s' % name, fromlist=['addons', name])
                if hasattr(addonmodule,'new_player'):
                    new_player.update(addonmodule.new_player)
                    dbg( 'XS: new_player scheme added for %s' % name)
                else:
                    dbg( 'XS: no new_player scheme in %s' % name)
                if hasattr(addonmodule,'new_dcfg'):
                    new_dcfg[name] = addonmodule.newplayer
                    dbg( 'XS: new_dcfg scheme added for %s' % name)
                else:
                    dbg( 'XS: no new_dcfg scheme in %s' % name)             
                if callable(getattr(addonmodule, 'load', None)):
                    addonmodule.load()
                else:
                    dbg( 'XS: no loader in %s' % name)
                if callable(getattr(addonmodule, 'unload', None)):
                    addonunloader = addonmodule.unload
                    addonsunloaders.append(addonunloader)
                else:
                    dbg( 'XS: no unloader in %s' % name)
    
def checkUpgrade():
    global data
    if data != {}:
        for key in new_player:
            for player in data:
                if not player == 'info' and key not in data[player]:
                    if type(new_player[key]) == dict:
                        data[player][key] = new_player[key].copy()
                    else:
                        data[player][key] = new_player[key]
    if 'info' not in data:
        data['info'] = {}
    data['info']['new_player'] = new_player
    data['info']['db_version'] = info.version

def loadPackages():
    if scfg.allMethods:
        for method in methodspath.files():
            if method.endswith('.py') and not method.namebase == '__init__':
                name = method.namebase
                packageloader = __import__('extendedstats.methods.%s' % name, fromlist=['methods', name]).load
                packageloader()
    else:
        for name in scfg.methodList:
            mf = methodspath.joinpath('%s.py' % name)
            if mf.isfile():
                packageloader = __import__('extendedstats.methods.%s' % name, fromlist=['methods', name]).load
                packageloader()

def fillDatabase():
    for player in playerlib.getPlayerList('#human'):
        steamid = sid(int(player))
        if steamid not in data:
            data[steamid] = new_player.copy()
        data[steamid]['sessionstart'] = player.attributes['timeconnected']
        data[steamid]['lastseen'] = time.time()
        data[steamid]['lastname'] = player.attributes['name']
        data[steamid]['teamchange_time'] = data[steamid]['sessionstart']

def unloadCommands():
    for saycmd in reggedscmd:
        es.unregsaycmd(saycmd)
    for clientcmd in reggedccmd:
        es.unregclientcmd(clientcmd)
            
def loadCVARS():
    es.ServerVar('extendedstats_version', info.version).makepublic()
    
def loadMenus():
    p = popuplib.easymenu('xs_help_menu','_popup_choice',helpCallback)
    p.settitle('Helptopics for eXtended Stats:')
    for key in cmdhelp:
        p.addoption(key,key)
    p.addoption('nodoc','Undocumented Commands')
    
    p = popuplib.easylist('xs_doc_nodoc')
    allcmds = addoncommands.keys()
    doccmds = cmdhelp.keys()
    nodocl = filter(lambda x: x not in doccmds,allcmds)
    if nodocl == []:
        nodocl = ['No undocumented Commands']
    for x in nodocl:
        p.additem(x)
    
    for command in cmdhelp:
        p = popuplib.easylist('xs_doc_%s' % command)
        for x in cmdhelp[command]:
            p.additem(x)
            
### Publics ###
        
def registerMethod(package,name,method): # string,string,method
    global methods
    methods[name.lower()] = method
    dbg( 'XS: Registered method %s for %s' % (name,package))
    
def registerEvent(name,event,callback): # string,string,method
    es.addons.registerForEvent(__import__('extendedstats.addons.%s' % name), event, callback)
    dbg( 'XS: Registered event %s for %s' % (event, name))
    
def registerCommand(command,addonname,callback,clientcommand=True,saycommand=True,helplist=['No help available for this command']):
    global addoncommands, reggedccmd, reggedscmd, cmdhelp
    if type(helplist) == str:
        helplist = makeList(helplist)
    cmdhelp[command] = helplist
    if clientcommand:
        es.regclientcmd(command,'extendedstats/addonCommandListener')
        addoncommands[command] = callback
        reggedccmd.append(command)
        dbg( 'XS: Registered clientcommand %s for %s' % (command,addonname))
    if saycommand:
        command = scfg.say_command_prefix + command
        es.regsaycmd(command,'extendedstats/addonCommandListener')
        addoncommands[command] = callback
        reggedscmd.append(command)
        dbg( 'XS: Registered saycommand %s for %s' % (command,addonname))
        
def registerLiveKey(name,callback):
    global live_keys, ignore_keys
    ignore_keys.append(name)
    live_keys[name] = callback

def registerIgnoreKey(name):
    global ignore_keys
    ignore_keys.append(name)
        
def addHelp(command,helptext):
    global cmdhelp
    if not type(helptext) == list:
        helptext = makeList(helptext)
    cmdhelp[command] = helptext
    dbg( 'XS: Added help text for %s' % command)
    
def getScore(player,method):
    if method not in methods:
        method = dcfg['default_method']
    return methods[method](getPlayer(player))

def getRank(player,method):
    method = getMethod(method)
    x = 1
    score = getScore(player,method)
    for user in data:
        if not user in [player,'info']:
            userscore = getScore(user,method)
            if userscore > score:
                x += 1
    return x

def getToplist(x,method=None):
    method = getMethod(method)
    tlist = []
    for player in data:
        if not player == 'info':
            tlist.append((getScore(player,method),player))
    tlist.sort()
    toplist = []
    for i in range(x) if len(tlist) >= x else range(len(tlist)):
        toplist.append((tlist[i][1],tlist[i][0]))
    return toplist

def getPlayer(player):
    live = {}
    for key in data[player]:
        if not key in ignore_keys:
            live[key] = data[player][key]
        for lkey in live_keys:
            if lkey == key:
                live[key] = live_keys[key](player)
    return live

def getName(player):
    if data[player]['settings']['name']:
        return data[player]['settings']['name']
    else:
        return data[player]['lastname']

### Helpers ###
            
def sid(ev):
    global pending, data
    if type(ev) == int:
        userid = ev
    else:
        userid = ev['userid']
    if userid in pending:
        return 'FAKEID_%s' % userid
    steamid = es.getplayersteamid(userid)
    if steamid == 'STEAM_ID_PENDING':
        steamid = 'FAKEID_%s' % userid
        pending[userid] = steamid
        data[steamid] = new_player.copy()
        data[steamid]['sessions'] += 1
        data[steamid]['sessionstart'] = time.time()
        data[steamid]['lastseen'] = time.time()
        data[steamid]['teamchange_time'] = time.time()
    elif not steamid in data:
        data[steamid] = new_player.copy()
    return steamid

def activateUser(userid, steamid):
    global data, pending
    if steamid not in data:
        data[steamid] = data[pending[userid]]
    else:
        for key in data[pending[userid]]:
            if type(data[pending[userid]][key]) == int and key in data[steamid]:
                data[steamid][key] += data[pending[userid]][key]
            elif type(data[pending[userid]][key]) == dict:
                if key not in data[steamid]:
                    data[steamid][key] = {}
                for subkey in data[pending[userid]][key]:
                    if type(data[pending[userid]][key][subkey]) == int and subkey in data[steamid][key]:
                        data[steamid][key][subkey] += data[pending[userid]][key][subkey]
                    else:
                        data[steamid][key][subkey] = data[pending[userid]][key][subkey]
            else:
                data[steamid][key] = data[pending[userid]][key]
    data[steamid]['sessions'] += 1
    data[steamid]['sessionstart'] = time.time()
    data[steamid]['lastseen'] = time.time()
    data[steamid]['teamchange_time'] = time.time()
    del data[pending[userid]]
    del pending[userid]
    
def makeList(text,maxchars=40):
    textlist = []
    while text:
        if ' ' in text and len(text) > 40:
            space = text.rfind(' ',0,maxchars)
            textlist.append(text[:space])
            text = text[space + 1:]
        else:
            textlist.append(text)
            text = False
    return textlist

def getMethod(method=None):
    keys = methods.keys()
    if method in keys:
        return method
    if dcfg['default_method'] in keys:
        return dcfg['default_method']
    return methods[keys[0]]
    
##############################
###   INGAME INTERACTION   ###
##############################
        
def addonCommandListener():
    b = 0
    c = es.getargc()
    args = []
    while b != c:
        args.append(es.getargv(b))
        b += 1
    cmd = args.pop(0)
    addoncommands[cmd](es.getcmduserid(),args)
    
def cmd_help():
    userid = es.getcmduserid()
    popuplib.send('xs_help_menu',userid)
    
def helpCallback(userid,choice,name):
    popuplib.send('xs_doc_%s' % choice,userid)
    
##############################
###         EVENTS         ###
##############################

### Builtin Events ###

def server_cvar(ev):
    dbg('XS: server_cvar')
    dbg('XS: cvar: %s' % ev['cvarname'])
    dbg('XS: value: %s' % ev['cvarvalue'])
    dbg('XS: dcfg: %s' % dcfg.cvars())
    if ev['cvarname'] in dcfg.cvars():
        dcfg[ev['cvarname'][3:]] = ev['cvarvalue']

def player_connect(ev):
    global pending, data
    if not es.isbot(ev['userid']):
        steamid = 'FAKEID_%s' % ev['userid']
        pending[ev['userid']] = steamid
        data[steamid] = new_player.copy()
        data[steamid]['sessions'] += 1
        data[steamid]['sessionstart'] = time.time()
        data[steamid]['lastseen'] = time.time()
        data[steamid]['teamchange_time'] = time.time()
        data[steamid]['changename'] += 1
        newname = ev['name']
        data[steamid]['names'][newname] = 1
        data[steamid]['lastname'] = newname
        dbg( 'player connected: %s' % steamid)

def player_disconnect(ev):
    global pending, data
    if not es.isbot(ev['userid']):
        dbg( 'player disconnected: %s' % ev['userid'])
        if ev['userid'] in pending:
            dbg( 'player was pending')
            del data[pending[ev['userid']]]
            del pending[ev['userid']]
        elif not es.isbot(ev['userid']):
            dbg( 'finnishing player session')
            steamid = ev['networkid']
            if steamid in data:
                data[steamid]['lastseen'] = time.time()
                data[steamid]['time'] += time.time() - data[steamid]['sessionstart']
                if not data[steamid]['current_team'] == '0':
                    data[steamid]['team_%s_time' % data[steamid]['current_team']] += time.time() - data[steamid]['teamchange_time']
                    data[steamid]['teamchange_time'] = time.time()
                data[steamid]['current_team'] = '0'
    
def es_player_validated(ev):
    dbg( 'player validated')
    userid = str(es.getuserid(ev['networkid']))
    if userid in pending:
        dbg( 'activating player FAKEID_%s to %s' % (userid, ev['networkid']))
        activateUser(userid,ev['networkid'])
    
def bomb_defused(ev):
    if not es.isbot(ev['userid']):
        dbg( 'bomb defused')
        data[sid(ev)]['bomb_defused'] += 1

def bomb_dropped(ev):
    if not es.isbot(ev['userid']):
        dbg( 'bomb dropped')
        steamid = sid(ev)
        if steamid:
            data[steamid]['bomb_dropped'] += 1

def bomb_exploded(ev):
    if not es.isbot(ev['userid']):
        dbg( 'bomb exploded')
        data[sid(ev)]['bomb_exploded'] += 1

def bomb_pickup(ev):
    if not es.isbot(ev['userid']):
        dbg( 'bomb pickup')
        data[sid(ev)]['bomb_pickup'] += 1

def flashbang_detonate(ev):
    if not es.isbot(ev['userid']):
        dbg( 'flashbang detonate')
        data[sid(ev)]['flashbang_detonate'] += 1

def hegrenade_detonate(ev):
    if not es.isbot(ev['userid']):
        dbg( 'hegrenade detonate')
        data[sid(ev)]['hegrenade_detonate'] += 1

def hostage_follows(ev):
    if not es.isbot(ev['userid']):
        dbg( 'hostage follows')
        data[sid(ev)]['hostage_follows'] += 1

def hostage_hurt(ev):
    if not es.isbot(ev['userid']):
        dbg( 'hostage hurt')
        data[sid(ev)]['hostage_hurt'] += 1
        # data[sid(ev)]['hostage_hurt_damage'] += ???

def hostage_killed(ev):
    if not es.isbot(ev['userid']):
        dbg( 'hostage killed')
        data[sid(ev)]['hostage_killed'] += 1

def hostage_rescued(ev):
    if not es.isbot(ev['userid']):
        dbg( 'hostage rescued')
        data[sid(ev)]['hostages_rescued'] += 1

def hostage_stops_following(ev):
    if not es.isbot(ev['userid']):
        dbg( 'hostage stops following')
        data[sid(ev)]['hostage_stops_following'] += 1
    
def item_pickup(ev):
    if not es.isbot(ev['userid']):
        global data
        item = ev['item']
        steamid = sid(ev)
        if item.startswith('weapon'):
            dbg( 'weapon picked up: %s' % item)
            weapon = item[7:]
            if weapon in data[steamid]['weapons_picked_up']:
                data[steamid]['weapons_picked_up'][weapon] += 1
            else:
                data[steamid]['weapons_picked_up'][weapon] = 1

def player_changename(ev):
    if not es.isbot(ev['userid']):
        dbg( 'player changed name')
        steamid = sid(ev)
        data[steamid]['changename'] += 1
        newname = ev['newname']
        if newname in data[steamid]['names']:
            data[steamid]['names'][newname] += 1
        else:
            data[steamid]['names'][newname] = 1
        data[steamid]['lastname'] = newname

def player_death(ev):
    dbg('')
    victimIsBot = bool(es.isbot(ev['userid']))
    victimSteamid = ev['es_steamid']
    victimTeam = ev['es_userteam']
    attackerIsBot = bool(es.isbot(ev['attacker']))
    attackerSteamid = ev['es_attackersteamid']
    attackerTeam = ev['es_attackerteam']
    wasTeamKill = True if attackerTeam == victimTeam else False
    isHeadshot = True if ev['headshot'] == '1' else False
    weapon = ev['weapon']
    dbg('player_death')
    dbg('victim: %s (%s)' % (victimSteamid,victimIsBot))
    dbg('attacker: %s (%s)' % (attackerSteamid,attackerIsBot))
    dbg('teamkill: %s (%s,%s)' % (wasTeamKill,victimTeam,attackerTeam))
    dbg('headshot: %s (%s)' % (isHeadshot,ev['headshot']))
    dbg('weapon: %s' % weapon)
    if wasTeamKill:
        dbg( 'teamkill')
        if not victimIsBot:
            data[victimSteamid]['teamkilled'] += 1
        if not attackerIsBot:
            data[attackerSteamid]['teamkills'] += 1
    else:
        dbg( 'kill')
        if not victimIsBot:
            data[victimSteamid]['deaths'] += 1
            dbg('increased deaths of %s by one to %s' % (victimSteamid,data[victimSteamid]['deaths']))
        if not attackerIsBot:
            data[attackerSteamid]['kills'] += 1
            dbg('increased kills of %s by one to %s' % (attackerSteamid,data[attackerSteamid]['kills']))
    if not victimIsBot:
        dbg( 'weapon stats (death)')
        if weapon in data[victimSteamid]['death_weapons']:
            data[victimSteamid]['death_weapons'][weapon] += 1
        else:
            data[victimSteamid]['death_weapons'][weapon] = 1
    if not attackerIsBot:
        dbg( 'weapon stats (kill)')
        if weapon in data[attackerSteamid]['kill_weapons']:
            data[attackerSteamid]['kill_weapons'][weapon] += 1
        else:
            data[attackerSteamid]['kill_weapons'][weapon] = 1
        if isHeadshot:
            data[attackerSteamid]['headshots'] += 1
    dbg('')
    dbg('all kills/deaths of all regged players:')
    dbg('kills:    deaths:')
    for player in data:
        if not player == 'info':
            dbg('    %s    %s' % (data[player]['kills'],data[player]['deaths']))
    dbg('')
    
def player_falldamage(ev):
    if not es.isbot(ev['userid']):
        dbg( 'falldamage')
        data[sid(ev)]['falldamage'] += float(ev['damage'])

def player_hurt(ev):
    victim = ev['es_steamid']
    attacker = ev['es_attackersteamid']
    if game == 'cstrike':
        damage = int(ev['dmg_health']) + int(ev['dmg_armor'])
    else:
        damage = int(ev['damage'])
    if not es.isbot(ev['userid']):
        dbg( 'player hurt')
        data[victim]['hurt'] += 1
        data[victim]['hurt_damage'] += damage
    if not es.isbot(ev['attacker']) and bool(int(ev['attacker'])):
        dbg( 'player hurted')
        data[attacker]['attacked'] += 1
        data[attacker]['attacked_damage'] += damage

def player_jump(ev):
    if not es.isbot(ev['userid']):
        dbg( 'player jumped')
        steamid = sid(ev)
        data[steamid]['jump'] += 1
        data[steamid]['jump_startpos'] = vecmath.vector(es.getplayerlocation(ev['userid']))

def player_radio(ev):
    if not es.isbot(ev['userid']):
        dbg( 'player radiomsg')
        data[sid(ev)]['radio'] += 1

def player_team(ev):
    if not es.isbot(ev['userid']):
        dbg( 'player_team')
        steamid = sid(ev)
        if steamid:
            ot = ev['oldteam']
            nt = ev['team']
            if ot in ['1','0'] and nt in ['2','3']:
                dbg( 'spec to play')
                data[steamid]['team_1_time'] += time.time() - data[steamid]['teamchange_time']
                data[steamid]['teamchange_time'] = time.time()
            if ot in ['2','3'] and nt in ['1','0']:
                dbg( 'play to spec')
                data[steamid]['team_%s_time' % ot] += time.time() - data[steamid]['teamchange_time']
                data[steamid]['teamchange_time'] = time.time()
            if ot in ['2','3'] and ot != nt:
                dbg( 'teamswitch')
                data[steamid]['team_%s_time' % ot] += time.time() - data[steamid]['teamchange_time']
                data[steamid]['teamchange_time'] = time.time()
            data[steamid]['current_team'] = nt
        else:
            dbg( 'disconnected')

def round_end(ev):
    dbg( 'round end')
    wt,lt = 'ct','t'
    if ev['winner'] == '2':
        wt,lt = lt,wt
    for userid in playerlib.getUseridList('#human,#%s' % wt):
        data[es.getplayersteamid(userid)]['win'] += 1
    for userid in playerlib.getUseridList('#human,#%s' % lt):
        data[es.getplayersteamid(userid)]['lose'] += 1
    saveDatabase()
    dcfg.sync()

def server_addban(ev):
    if not es.isbot(ev['userid']):
        steamid = sid(ev)
        dbg( 'addban')
        if steamid:
            data[steamid]['ban'] += 1
        else:
            L = ['ADDBAN: %s' % time.strftime("%d %b %Y %H:%M:%S"),'XS Version: %s' % info.version,'']
            L.append('Mapname: %s' % ev['mapname'])
            L.append('Players: %s (%s Bots)' % (len(es.getUseridList()),len(playerlib.getUseridList('#bot'))))
            L.append('Couldn\'t add ban, no steamid found')
            for var in ('networkid','userid','ip','name','duration','by','kicked'):
                L.append('%s: %s' % (var, ev[var]))
            L.append('')
            L += errorlog.lines(retain=False)
            errorlog.write_lines(L)

def smokegrenade_detonate(ev):
    if not es.isbot(ev['userid']):
        dbg( 'smokegrenade detonate')
        data[sid(ev)]['smokegrenade_detonate'] += 1
        
def vip_escaped(ev):
    if not es.isbot(ev['userid']):
        dbg( 'vip escaped')
        data[sid(ev)]['vip_escaped'] += 1

def vip_killed(ev):
    if not es.isbot(ev['attacker']):
        dbg( 'vip killed')
        data[es.getplayersteamid(ev['attacker'])]['vip_killed'] += 1
    if not es.isbot(ev['userid']):
        dbg( 'vip died')
        data[sid(ev)]['vip_died'] += 1

def player_changeclass(ev):
    dbg( 'player changed class')
    dbg( ev['class'])
    pass

def dod_capture_blocked(ev):
    if not es.isbot(ev['userid']):
        dbg( 'capture blocked')
        data[sid(ev)]['dod_blocks'] += 1

def dod_round_win(ev):
    wt,lt = 'ct','t'
    dbg( 'round won')
    if ev['team'] == '2':
        wt,lt = lt,wt
    for userid in playerlib.getUseridList('#human,#%s' % wt):
        data[es.getplayersteamid(userid)]['win'] += 1
    for userid in playerlib.getUseridList('#human,#%s' % lt):
        data[es.getplayersteamid(userid)]['lose'] += 1
    saveDatabase()
    dcfg.sync()

def dod_bomb_exploded(ev):
    if not es.isbot(ev['userid']):
        dbg( 'bomb exploded')
        data[sid(ev)]['bomb_exploded'] += 1

def dod_bomb_defused(ev):
    if not es.isbot(ev['userid']):
        dbg( 'bomb defused')
        data[sid(ev)]['bomb_defused'] += 1

### ExtendedEvents ###
#
# ExtendedEvents events have been moved to /extendedstats/addons/extendedevents.py
#       
### Gungame Events ###
#
# Gungame Events have been moved to /extendedstats/addons/gungame.py
#
### Warcraft:Source Events ###
#
# WCS Events can be found at /extendedstats/addons/wcs.py

##############################
### DYNAMIC CONFIGURATION  ###
##############################

class dyncfg(dict):
    def __init__(self,f,cvar_prefix='',default={}):
        self.__filepath__ = path.path(f)
        self.__filepath__.touch()
        self.__cvarprefix__ = cvar_prefix
        self.__d__ = {}
        self.__cvars__ = []
        self.sync()
        if default:
            for key in filter(lambda x: not self.__contains__(x),default.keys()):
                self[key] = default[key]

    def __getitem__(self,s):
        s = str(s)
        if s in self.__d__:
            return self.__d__[s]
        L = self.__filepath__.lines(retain=False)
        for line in L:
            if not line.startswith('#'):
                var,val = line.split('=',1)
                var = var.strip()
                val = val.strip()
                if var == s:
                    self.__d__[var] = val
                    self.__cvars__.append(self.__cvarprefix__ + var)
                    return val
        return None
    
    def __contains__(self,s):
        if s in self.__d__:
            return True
        L = self.__filepath__.lines(retain=False)
        for line in L:
            if line.startswith(s):
                return True
        return False

    def __setitem__(self,s,v):
        s = str(s)
        v = str(v)
        self.__d__[s] = v
        self.__cvars__.append(self.__cvarprefix__ + s)
        L = self.__filepath__.lines(retain=False)
        done = False
        for line in L:
            if not line.startswith('#') and line.count('=') != 0:
                if line.startswith(s):
                    L[L.index(line)] = '%s = %s' % (s,v)
                    done = True
                    break
        if not done:
            L.append('%s = %s' % (s,v))
        self.__filepath__.write_lines(L)
        es.ServerVar(self.__cvarprefix__ + s,v).addFlag('notify')

    def sync(self):
        self.__d__ = {}
        self.__cvars__ = []
        L = self.__filepath__.lines(retain=False)
        for line in L:
            if not line.startswith('#') and line.count('=') != 0:
                var,val = line.split('=')
                var = var.strip()
                val = val.strip()
                self.__d__[var] = val
                es.ServerVar(self.__cvarprefix__ + var,val).addFlag('notify')
                self.__cvars__.append(self.__cvarprefix__ + var)
        self.__filepath__.write_lines(L)
                
    def keys(self):
        return self.__d__.keys()
        
    def cvars(self):
        return self.__cvars__
    
class addonDynCfg():
    def __init__(self,addonname,default={}):
        dbg('XS: addonDyncfg %s init' % addonname)
        self.__an__ = addonname
        if default:
            for key in filter(lambda x: x not in dcfg,default.keys()):
                dcfg['%s_%s' % (addonname,key)] = default[key]
    
    def __getitem__(self,var):
        dbg('XS: addonDyncfg %s getitem: %s' % (self.__an__, var))
        return dcfg['%s_%s' % (self.__an__,var)]
    
    def __setitem__(self,var,val):
        dbg('XS: addonDyncfg %s setitem: %s: %s' % (self.__an__, var, val))
        dcfg['%s_%s' % (self.__an__,var)] = val
new_dcfg = {
    'default_method': 'kdr',
    'debuglevel': '0',
}
dcfg = dyncfg(gamepath.joinpath('cfg/extendedstats.cfg'),'xs_',new_dcfg)