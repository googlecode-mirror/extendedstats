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
import time, path, sqlite3, sys, traceback, psyco, hashlib, base64, urllib
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
info.version        = '0.1.0:122'
info.versionname    = 'Bettina'
info.basename       = 'extendedstats'
info.name           = 'eXtended stats'
info.author         = 'Ojii with loads of help by others'
info.description    = 'Stores a lot of information about players'

gamepath = path.path(str(es.ServerVar('eventscripts_gamedir')))
xspath = gamepath.joinpath('addons/eventscripts/extendedstats/')
methodspath = xspath.joinpath('methods/')
addonspath = xspath.joinpath('addons/')

game = str(es.ServerVar('eventscripts_gamedir')).replace('\\', '/').rpartition('/')[2]
methods = {}
addoncommands = {}
reggedccmd = []
reggedscmd = []
errorhashes = []
newconnected = []
tables = {}
cmdhelp = {}
uniquecommands = []
loadedAddonsList = map(lambda x: str(x),es.addons.getAddonList())

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
    
def dbg(text):
    es.dbgmsg(int(dcfg['debuglevel']),text)

##############################
### LOAD, HELPERS, PUBLICS ###
##############################

### Loading and Unloading ###

def load():
    dbg( '')
    dbg( 'XS: Loading...')
    loadPackages()
    loadAddons()
    fillDatabase()
    es.regsaycmd(scfg.say_command_prefix + scfg.command_help,'extendedstats/cmd_help')
    es.regclientcmd(scfg.command_help,'extendedstats/cmd_help')
    loadCVARS()
    loadMenus()
    es.regcmd('xs_clean','extendedstats/clean')
    es.regcmd('xs_resetlog','extendedstats/resetlog')
    es.regcmd('xs_convert','extendedstats/convert')
    dbg( 'XS: Registered methods:')
    for method in methods:
        dbg( '    %s' % method)
    dcfg.sync()
    dbg( 'XS: Loaded successfully (%s: %s)' % (info.versionname,info.version))
    dbg( '')
    
def clean():
    return
    # for reference:
    tbd = []
    for player in data:
        if not player:
            tbd.append(player)
            continue
        if player == 'info':
            continue
        if player.startswith('FAKE'):
            tbd.append(player)
            continue
        if not data[player]['sessionstart']:
            data[player]['sessionstart'] = time.time()
        for key in data[player]:
            if not key in new_player:
                del data[player][key]
    for d in tbd:
        del data[d]
            
def resetlog():
    errorlog.write_text('')
    
def convert():
    dbpath = xspath.joinpath('data.cpickle')
    if not dbpath.isfile():
        return
    backuppath = xspath.joinpath('backup')
    if not backuppath.isdir():
        backuppath.mkdir()
    import cPickle
    olddb = cPickle.load(dbpath.open('rb'))
    dbpath.move(backuppath)
    for steamid in olddb:
        if not steamid == 'info':
            if not steamid in players:
                players.newplayer(steamid)
            for key in filter(lambda x: x in map(lambda x: x[0],columns),olddb[steamid].keys()):
                players.update(steamid,key,olddb[key])
    

def unload():
    es.unregsaycmd('!help')
    for addon in addonsunloaders:
        addon()
    unloadCommands()
        
def loadAddons():
    global addonsunloaders
    addonsunloaders = []
    if scfg.allAddons:
        for addon in addonspath.files():
            if addon.endswith('.py') and not addon.namebase == '__init__':
                name = addon.namebase
                addonmodule = __import__('extendedstats.addons.%s'%name, fromlist=['addons', name])         
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
                if callable(getattr(addonmodule, 'load', None)):
                    addonmodule.load()
                else:
                    dbg( 'XS: no loader in %s' % name)
                if callable(getattr(addonmodule, 'unload', None)):
                    addonunloader = addonmodule.unload
                    addonsunloaders.append(addonunloader)
                else:
                    dbg( 'XS: no unloader in %s' % name)

def loadPackages():
    if scfg.allPackages:
        for package in methodspath.files():
            if package.endswith('.py') and not package.namebase == '__init__':
                name = package.namebase
                packageloader = __import__('extendedstats.methods.%s' % name, fromlist=['methods', name]).load
                packageloader()
    else:
        for name in scfg.packageList:
            mf = methodspath.joinpath('%s.py' % name)
            if mf.isfile():
                packageloader = __import__('extendedstats.methods.%s' % name, fromlist=['methods', name]).load
                packageloader()

def fillDatabase():
    for player in playerlib.getPlayerList('#human'):
        steamid = sid(int(player))
        if steamid not in players:
            players.newplayer(steamid)
        players.update(steamid,'sessionstart',player.attributes['timeconnected'])
        players.update(steamid,'lastseen',time.time())
        players.name(steamid,player.attributes['name'])
        players.update(steamid,'teamchange_time',player.attributes['timeconnected'])

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
    p.settitle('Undocumented Commands:')
    doccmds = cmdhelp.keys()
    nodocl = filter(lambda x: x not in doccmds,uniquecommands)
    if nodocl == []:
        nodocl = ['No undocumented Commands']
    for x in nodocl:
        p.additem(x)
    
    for command in cmdhelp:
        p = popuplib.easylist('xs_doc_%s' % command)
        p.settitle('Help: %s' % command)
        for x in cmdhelp[command]:
            p.additem(x)
            
### Publics ###
        
def registerMethod(package,name,method): # string,string,method
    global methods
    if scfg.allMethods or name.lower() in scfg.methodList:
        methods[name.lower()] = method
        dbg( 'XS: Registered method %s for %s' % (name,package))
    
def registerEvent(name,event,callback): # string,string,method
    es.addons.registerForEvent(__import__('extendedstats.addons.%s' % name), event, callback)
    dbg( 'XS: Registered event %s for %s' % (event, name))
    
def registerCommand(command,addonname,callback,clientcommand=True,saycommand=True,helplist=['No help available for this command']):
    global addoncommands, reggedccmd, reggedscmd, cmdhelp, uniquecommands
    uniquecommands.append(command)
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
        
def addHelp(command,helptext):
    global cmdhelp
    if not type(helptext) == list:
        helptext = makeList(helptext)
    cmdhelp[command] = helptext
    dbg( 'XS: Added help text for %s' % command)
    
def getScore(steamid,method):
    if method not in methods:
        method = dcfg['default_method']
    return methods[method](players,steamid)

def getRank(steamid,method):
    method = getMethod(method)
    if method in players.columns:
        players.execute("SELECT steamid FROM xs_main ORDER BY %s DESC" % (method))
        allplayers = players.fetchall()
        return allplayers.index(steamid) + 1,len(allplayers)
    x = 1
    score = getScore(steamid,method)
    allplayers = players.getPlayerList()
    for steamid in allplayers:
        if (steamid,method) > score:
            x += 1
    return x, len(allplayers)

def getToplist(x,method=None):
    method = getMethod(method)
    tlist = []
    if method in players.columns:
        players.execute("SELECT steamid,%s FROM xs_main ORDER BY %s DESC%s" % (method,method," LIMIT %s" % args[2] if args[2] else ""))
        for row in players.fetchall():
            steamid,score = row
            tlist.append(score,steamid)
    else:
        for steamid in players.getPlayerList():
            tlist.append((getScore(steamid,method),steamid))
        tlist.sort(reverse=True)
    return tlist

def getName(steamid):
    settings_name = players.query(steamid,'settings_name')
    if settings_name:
        return settings_name
    return players.query(steamid,'name1')

### Helpers ###
            
def sid(ev):
    if type(ev) == int:
        userid = ev
    else:
        userid = ev['userid']
    return es.getplayersteamid(userid)
    
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

def addonIsLoaded(addonname):
    return addonname in loadedAddonsList

def updateTimes():
    for userid in playerlib.getUseridList('#human'):
        steamid = es.getplayersteamid(userid)
        players.update(steamid,'lastseen',time.time())
        players.add(steamid,'time',time.time() - players.query(steamid,'sessionstart'))
        players.update(steamid,'sessionstart',time.time())
        cteam = players.query(steamid,'current_team')
        if not cteam == '0':
            players.add(steamid,'team_%s_time' % cteam,time.time() - players.query(steamid,'teamchange_time'))
        players.update(steamid,'teamchange_time',time.time())
        
    
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
    if ev['cvarname'] in dcfg.cvars():
        dcfg[ev['cvarname'][3:]] = ev['cvarvalue']
        
def player_connect(ev):
    global newconnected
    newconnected.append(ev['userid'])

def player_spawn(ev):
    global newconnected
    print 'player_spawn'
    if not es.isbot(ev['userid']):
        steamid = es.getplayersteamid(ev['userid'])
        if not steamid:
            print 'NO STEAM ID!!!'
            return
        if not ev['userid'] in newconnected:
            return
        if not steamid in players:
            players.newplayer(steamid)
        players.increment(steamid,'sessions')
        players.update(steamid,'sessionstart',time.time())
        players.update(steamid,'lastseen',time.time())
        players.update(steamid,'teamchange_time',time.time())
        newname = es.getplayername(ev['userid'])
        players.name(steamid,newname)
        newconnected.remove(ev['userid'])
        dbg('player spawned: %s' % steamid)

def player_disconnect(ev):
    global newconnected
    if ev['userid'] in newconnected:
        newconnected.remove(ev['userid'])
        return
    if not es.isbot(ev['userid']):
        dbg( 'player disconnected: %s' % ev['userid'])
        dbg( 'finnishing player session')
        steamid = ev['networkid']
        if not steamid in players:
            return
        players.update(steamid,'lastseen',time.time())
        players.add(steamid,'time',time.time() - players.query(steamid,'sessionstart'))
        cteam = players.query(steamid,'current_team')
        if not cteam == '0':
            players.add(steamid,'team_%s_time' % cteam,time.time() - players.query(steamid,'teamchange_time'))
        players.update(steamid,'teamchange_time',time.time())
        players.update(steamid,'current_team',0)
    
def bomb_defused(ev):
    if not es.isbot(ev['userid']):
        dbg( 'bomb defused')
        players.increment(sid(ev),'bomb_defused')

def bomb_dropped(ev):
    if not es.isbot(ev['userid']):
        dbg( 'bomb dropped')
        steamid = sid(ev)
        if steamid:
            players.increment(sid(ev),'bomb_dropped')

def bomb_exploded(ev):
    if not es.isbot(ev['userid']):
        dbg( 'bomb exploded')
        players.increment(sid(ev),'bomb_exploded')

def bomb_pickup(ev):
    if not es.isbot(ev['userid']):
        dbg( 'bomb pickup')
        players.increment(sid(ev),'bomb_pickup')

def flashbang_detonate(ev):
    if not es.isbot(ev['userid']):
        dbg( 'flashbang detonate')
        players.increment(sid(ev),'flashbang_detonate')

def hegrenade_detonate(ev):
    if not es.isbot(ev['userid']):
        dbg( 'hegrenade detonate')
        players.increment(sid(ev),'hegrenade_detonate')

def hostage_follows(ev):
    if not es.isbot(ev['userid']):
        dbg( 'hostage follows')
        players.increment(sid(ev),'hostage_follows')

def hostage_hurt(ev):
    if not es.isbot(ev['userid']):
        dbg( 'hostage hurt')
        players.increment(sid(ev),'hostage_hurt')

def hostage_killed(ev):
    if not es.isbot(ev['userid']):
        dbg( 'hostage killed')
        players.increment(sid(ev),'hostage_killed')

def hostage_rescued(ev):
    if not es.isbot(ev['userid']):
        dbg( 'hostage rescued')
        players.increment(sid(ev),'hostage_rescued')

def hostage_stops_following(ev):
    if not es.isbot(ev['userid']):
        dbg( 'hostage stops following')
        players.increment(sid(ev),'hostage_stops_following')
    
def item_pickup(ev):
    if not es.isbot(ev['userid']):
        global data
        item = ev['item']
        steamid = sid(ev)
        if item.startswith('weapon'):
            dbg( 'weapon picked up: %s' % item)
            weapon = item[7:]
            weapons.increment(steamid,'pickup_%s' % weapon)

def player_changename(ev):
    if not es.isbot(ev['userid']):
        dbg( 'player changed name')
        steamid = sid(ev)
        newname = ev['newname']
        players.name(steamid,newname)

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
            players.increment(victimSteamid,'teamkilled')
        if not attackerIsBot:
            players.increment(attackerSteamid,'teamkills')
    else:
        dbg( 'kill')
        if not victimIsBot:
            players.increment(victimSteamid,'deaths')
        if not attackerIsBot:
            players.increment(attackerSteamid,'kills')
    if not victimIsBot:
        dbg( 'weapon stats (death)')
        weapons.increment(victimSteamid,'death_%s' % weapon)
    if not attackerIsBot:
        dbg( 'weapon stats (kill)')
        weapons.increment(attackerSteamid,'kill_%s' % weapon)
        if isHeadshot:
            players.increment(attackerSteamid,'headshots')
    
def player_falldamage(ev):
    if not es.isbot(ev['userid']):
        dbg( 'falldamage')
        players.add(sid(ev),'falldamage',float(ev['damage']))

def player_hurt(ev):
    victim = ev['es_steamid']
    attacker = ev['es_attackersteamid']
    if game == 'cstrike':
        damage = int(ev['dmg_health']) + int(ev['dmg_armor'])
    else:
        damage = int(ev['damage'])
    if not es.isbot(ev['userid']):
        dbg( 'player hurt')
        players.increment(victim,'hurt')
        players.add(victim,'hurt_damage',damage)
        data[victim]['hurt_damage'] += damage
    if not es.isbot(ev['attacker']) and bool(int(ev['attacker'])):
        dbg( 'player hurted')
        players.increment(attacker,'attacked')
        players.add(attacker,'attacked_damage',damage)

def player_jump(ev):
    if not es.isbot(ev['userid']):
        dbg( 'player jumped')
        steamid = sid(ev)
        players.increment(steamid,'jump')
        vStartpos = vecmath.vector(es.getplayerlocation(ev['userid']))
        players.update(steamid,'jump_startpos',str(vStartpos))

def player_radio(ev):
    if not es.isbot(ev['userid']):
        dbg( 'player radiomsg')
        players.increment(sid(ev),'radio')

def player_team(ev):
    if not es.isbot(ev['userid']):
        dbg( 'player_team')
        steamid = sid(ev)
        if steamid:
            ot = ev['oldteam']
            nt = ev['team']
            if ot in ['1','0'] and nt in ['2','3']:
                dbg( 'spec to play')
                players.add(steamid,'team_1_time',time.time() - players.query(steamid,'teamchange_time'))
                players.update(steamid,'teamchange_time',time.time())
            if ot in ['2','3'] and nt in ['1','0']:
                dbg( 'play to spec')
                data[steamid]['team_%s_time' % ot] += time.time() - data[steamid]['teamchange_time']
                data[steamid]['teamchange_time'] = time.time()
            if ot in ['2','3'] and ot != nt:
                dbg( 'teamswitch')
                players.add(steamid,'team_%s_time' % ot,time.time() - players.query(steamid,'teamchange_time'))
                players.update(steamid,'teamchange_time',time.time())
            players.update(steamid,'current_team',nt)
        else:
            dbg( 'disconnected')

def round_end(ev):
    dbg( 'round end')
    wt,lt = 'ct','t'
    if ev['winner'] == '2':
        wt,lt = lt,wt
    for userid in playerlib.getUseridList('#human,#%s' % wt):
        players.increment(es.getplayersteamid(userid),'win')
    for userid in playerlib.getUseridList('#human,#%s' % lt):
        players.increment(es.getplayersteamid(userid),'lose')
    dcfg.sync()
    updateTimes()

def server_addban(ev):
    if not es.isbot(ev['userid']):
        dbg( 'addban')
        if ev['networkid'] in players:
            players.increment(ev['networkid'],'ban')

def smokegrenade_detonate(ev):
    if not es.isbot(ev['userid']):
        dbg( 'smokegrenade detonate')
        players.increment(sid(ev),'smokegrenade_detonate')
        
def vip_escaped(ev):
    if not es.isbot(ev['userid']):
        dbg( 'vip escaped')
        players.increment(sid(ev),'vip_escaped')

def vip_killed(ev):
    if not es.isbot(ev['attacker']):
        dbg( 'vip killed')
        players.increment(ev['attacker'],'vip_killed')
    if not es.isbot(ev['userid']):
        dbg( 'vip died')
        players.increment(sid(ev),'vip_died')

def player_changeclass(ev):
    dbg( 'player changed class')
    dbg( ev['class'])
    pass

def dod_capture_blocked(ev):
    if not es.isbot(ev['userid']):
        dbg( 'capture blocked')
        players.increment(sid(ev),'dod_blocks')

def dod_round_win(ev):
    wt,lt = 'ct','t'
    dbg( 'round won')
    if ev['team'] == '2':
        wt,lt = lt,wt
    for userid in playerlib.getUseridList('#human,#%s' % wt):
        players.increment(es.getplayersteamid(userid),'win')
    for userid in playerlib.getUseridList('#human,#%s' % lt):
        players.increment(es.getplayersteamid(userid),'lose')
    dcfg.sync()
    updateTimes()

def dod_bomb_exploded(ev):
    if not es.isbot(ev['userid']):
        dbg( 'bomb exploded')
        players.increment(sid(ev),'bomb_exploded')

def dod_bomb_defused(ev):
    if not es.isbot(ev['userid']):
        dbg( 'bomb defused')
        players.increment(sid(ev),'bomb_defused')
    
def es_map_start(ev):
    dcfg.sync()

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
    
    def as_bool(self,s):
        return bool(self[s])
    
class addonDynCfg(dict):
    def __init__(self,addonname,default={}):
        self.__an__ = addonname
        if default:
            for key in filter(lambda x: x not in dcfg,default.keys()):
                dcfg['%s_%s' % (addonname,key)] = default[key]
    
    def __getitem__(self,var):
        return dcfg['%s_%s' % (self.__an__,var)]
    
    def __setitem__(self,var,val):
        dcfg['%s_%s' % (self.__an__,var)] = val
default = {
    'default_method': 'kdr',
    'debuglevel': '0',
    'statsme_methods': '',
}
dcfg = dyncfg(gamepath.joinpath('cfg/extendedstats.cfg'),'xs_',default)

class Sqlite(object):
    def __init__(self,table,columns=[('steamid','TEXT PRIMARY KEY')]):
        self.con = sqlite3.connect(xspath.joinpath('database.sqlite'))
        self.cur = self.con.cursor()
        self.table = table
        self.create(columns)
        self.columns = self.getColumns()
        self.numericColumns = filter(lambda x: self.numericColumn(x),self.columns)
        
    def create(self,columns):
        if self.tableExists():
            existingColumns = self.getColumns()
            columns = filter(lambda x: x[0] not in existingColumns,columns)
            self.addColumns(columns)
        else:
            coldef = ', '.join(map(lambda x: '%s %s' % x,columns))
            self.execute("CREATE TABLE xs_%s (%s)" % (self.table,coldef),True)
        
    def tableExists(self):
        return len(self.con.execute('PRAGMA table_info(xs_%s)' % self.table).fetchall()) > 0
        
    def getColumns(self):
        return map(lambda x: x[1], self.con.execute('PRAGMA table_info(xs_%s)' % self.table).fetchall())
    
    def getPlayerList(self):
        self.execute("SELECT steamid FROM xs_%s" % self.table)
        return self.fetchall()
    
    def numericColumn(self,key):
        self.execute('PRAGMA table_info(xs_%s)' % self.table)
        all = self.fetchall()
        column = filter(lambda x: x[1] == key,all)[0]
        return column[2] in ('INTEGER','REAL')
        
    def addColumns(self,columns):
        for column in columns:
            self.execute("ALTER TABLE xs_%s ADD COLUMN %s %s" % (self.table,column[0],column[1]),True)
        self.columns = self.getColumns()
        self.numericColumns = filter(lambda x: self.numericColumn(x),self.columns)
        
    def execute(self,sql,save=False):
        self.cur.execute(sql)
        if save:
            self.con.commit()
            
    def fetchall(self):
        trueValues = []
        for value in self.cur.fetchall():
            if len(value) > 1:
                trueValues.append(value)
            else:
                trueValues.append(value[0])
        return trueValues
       
    def fetchone(self):
        one = self.cur.fetchone()
        if one:
            one = one[0]
        return one
    
    def __contains__(self,steamid):
        self.execute("SELECT kills FROM xs_%s WHERE steamid='%s'" % (self.table,steamid))
        return bool(self.cur.fetchone()) 
    
    def query(self,steamid,key):
        self.execute("SELECT %s FROM xs_%s WHERE steamid='%s'" % (key,self.table,steamid))
        return self.fetchone()
        
    def convert(self,key,value):
        if key in self.numericColumns:
            return value
        return "'%s'" % value
        
    def update(self,steamid,key,newvalue):
        self.execute("UPDATE xs_%s SET %s=%s WHERE steamid='%s'" % (self.table,key,self.convert(key,newvalue),steamid),True)
        
    def increment(self,steamid,key):
        old = self.query(steamid,key)
        if not old:
            old = 0
        self.execute("UPDATE xs_%s SET %s=%s WHERE steamid='%s'" % (self.table,key,old + 1,steamid),True)
        
    def add(self,steamid,key,amount):
        current = self.query(steamid,key)
        newamount = current + amount
        self.execute("UPDATE xs_%s SET %s=%s WHERE steamid='%s'" % (self.table,key,newamount,steamid),True)
        
    def name(self,steamid,newname):
        self.execute("SELECT name1,name2,name3,name4,name5 FROM xs_%s WHERE steamid='%s'" % (self.table,steamid))
        cnames = self.fetchone()
        if not cnames:
            self.update(steamid,'name1',newname)
        else:
            if not type(cnames) == tuple:
                cnames = [cnames]
            if newname in cnames:
                nnames = [newname]
                for cname in cnames:
                    if cname == newname:
                        continue
                    nnames.append(cname)
                    if len(nnames) == 5:
                        break
            else:
                nnames = [newname]
                for cname in cnames:
                    nnames.append(cname)
                    if len(nnames) == 5:
                        break
            for x in range(len(nnames)):
                self.update(steamid,'name%s' % (x + 1),nnames[x])
        self.increment(steamid,'changename') 

    def newplayer(self,steamid):
        self.execute("INSERT INTO xs_%s (steamid) VALUES ('%s')" % (self.table,steamid),True)
        
dod_columns = [
    ('dod_sniper', 'INTEGER DEFAULT 0'),
    ('dod_rifleman', 'INTEGER DEFAULT 0'),
    ('dod_assault', 'INTEGER DEFAULT 0'),
    ('dod_support', 'INTEGER DEFAULT 0'),
    ('dod_rocket', 'INTEGER DEFAULT 0'),
    ('dod_mg', 'INTEGER DEFAULT 0'),
    ('dod_blocks', 'INTEGER DEFAULT 0'),
]
cstrike_columns = [
    ('bomb_defused', 'INTEGER DEFAULT 0'),
    ('bomb_dropped', 'INTEGER DEFAULT 0'),
    ('bomb_exploded', 'INTEGER DEFAULT 0'),
    ('bomb_pickup', 'INTEGER DEFAULT 0'),
    ('flashbang_detonate', 'INTEGER DEFAULT 0'),
    ('hegrenade_detonate', 'INTEGER DEFAULT 0'),
    ('hostage_follows', 'INTEGER DEFAULT 0'),
    ('hostage_hurt', 'INTEGER DEFAULT 0'),
    ('hostage_killed', 'INTEGER DEFAULT 0'),
    ('hostage_rescued', 'INTEGER DEFAULT 0'),
    ('hostage_stops_following', 'INTEGER DEFAULT 0'),
    ('radio', 'INTEGER DEFAULT 0'),
    ('smokegrenade_detonate', 'INTEGER DEFAULT 0'),
    ('vip_escaped', 'INTEGER DEFAULT 0'),
    ('vip_killed', 'INTEGER DEFAULT 0'),
    ('vip_died', 'INTEGER DEFAULT 0'),
]
columns = [
    ('steamid','TEXT PRIMARY KEY'),
    ('sessions', 'INTEGER DEFAULT 0'),
    ('sessionstart', 'REAL DEFAULT NULL'),
    ('time', 'REAL DEFAULT 0.0'),
    ('changename', 'INTEGER DEFAULT 0'),
    ('kills', 'INTEGER DEFAULT 0'),
    ('deaths', 'INTEGER DEFAULT 0'),
    ('teamkills', 'INTEGER DEFAULT 0'),
    ('teamkilled', 'INTEGER DEFAULT 0'),
    ('headshots', 'INTEGER DEFAULT 0'),
    ('lastseen', 'REAL DEFAULT 0.0'),
    ('falldamage', 'REAL DEFAULT 0.0'),
    ('attacked', 'INTEGER DEFAULT 0'),
    ('hurt_damage', 'REAL DEFAULT 0.0'),
    ('attacked_damage', 'REAL DEFAULT 0.0'),
    ('jump', 'INTEGER DEFAULT 0'),
    ('jump_startpos','TEXT DEFAULT NULL'),
    ('team_1_time', 'REAL DEFAULT 0.0'),
    ('team_2_time', 'REAL DEFAULT 0.0'),
    ('team_3_time', 'REAL DEFAULT 0.0'),
    ('teamchange_time', 'REAL DEFAULT NULL'),
    ('current_team', 'REAL DEFAULT 0.0'),
    ('win', 'REAL DEFAULT 0.0'),
    ('lose', 'REAL DEFAULT 0.0'),
    ('rounds', 'REAL DEFAULT 0.0'),
    ('ban', 'REAL DEFAULT 0.0'),
    ('name1', 'TEXT DEFAULT NULL'),
    ('name2', 'TEXT DEFAULT NULL'),
    ('name3', 'TEXT DEFAULT NULL'),
    ('name4', 'TEXT DEFAULT NULL'),
    ('name5', 'TEXT DEFAULT NULL'),
    ('settings_name','TEXT DEFAULT NULL'),
    ('settings_method','TEXT DEFAULT NULL'),
]
if game == 'cstrike':
    columns += cstrike_columns
elif game == 'dod':
    columns += dod_columns
players = Sqlite('main',columns)
tables['main'] = players
weapons = None
dod_weapons = ['30cal', '30calpr', '30calsr', 'amerknife', 'bar', 'bazooka', 'bazookarocket', 'basebomb', 'c96', 'colt', 'frag', 'garand', 'garandgren', 'garandrggrenade', 'k98', 'k98rg', 'k98rggrenade', 'k98s', 'm1carb', 'mg42', 'mg42bd', 'mg42bu', 'mg42pr', 'mg42sr', 'mp40', 'mp44', 'p38', 'panzerschreckrocket', 'pschreck', 'smokeger', 'smokeus', 'spade', 'spring', 'stick', 'thompson']
cstrike_weapons = ['glock', 'usp', 'p228', 'deagle', 'fiveseven', 'elite', 'm3', 'xm1014', 'tmp', 'mac10', 'mp5navy', 'ump45', 'p90', 'famas', 'galil', 'ak47', 'scout', 'm4a1', 'sg550', 'g3sg1', 'awp', 'sg552', 'aug', 'm249', 'hegrenade', 'flashbang', 'smokegrenade', 'knife', 'c4']
if game == 'cstrike':
    weapons = map(lambda x: ('pickup_%s' % x,'INTEGER DEFAULT 0'),cstrike_weapons)
elif game == 'dod':
    weapons = map(lambda x: ('pickup_%s' % x,'INTEGER DEFAULT 0'),dod_weapons)
if weapons:
    weapons = Sqlite('weapons',weapons)
    tables['weapons'] = weapons