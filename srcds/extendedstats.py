##############################
###        IMPORTS        ####
##############################

# ES Imports
import es, playerlib, vecmath, popuplib, gamethread
# Python Imports
import time, path, sqlite3, sys, traceback, psyco, base64, zlib, urllib, configobj, re
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
info.version        = '0.2.1:152'
info.basename       = 'extendedstats'
info.name           = 'eXtended Stats'
info.author         = 'Ojii with loads of help by others'
info.description    = 'Stores a lot of information about players'

gamepath = path.path(str(es.ServerVar('eventscripts_gamedir')))
xspath = gamepath.joinpath('addons/eventscripts/extendedstats/')
methodspath = xspath.joinpath('methods/')
addonspath = xspath.joinpath('addons/')
eventsdir = xspath.joinpath('events')

gamedir = gamepath.replace('\\','/')
gamedir = gamedir[:-1] if gamedir[-1] == '/' else gamedir
game = gamedir.rpartition('/')[2]
methods = {}
addoncommands = {}
reggedccmd = []
reggedscmd = []
newconnected = []
pending = []
tables = {}
uniquecommands = []
saycommands = {}
addonlistpattern = re.compile('\w*[\']\s')

##############################
###     DEBUG HELPER      ####
##############################

errorlog = xspath.joinpath('log.txt')
if not errorlog.isfile():
    errorlog.touch()
    
def excepter(type1, value1, traceback1):
    mystr = traceback.format_exception(type1, value1, traceback1)
    L = ['ERROR: %s' % time.strftime("%d %b %Y %H:%M:%S"),'XS Version: %s' % info.version,'']
    L.append('Mapname: %s' % str(es.ServerVar('eventscripts_currentmap')))
    L.append('Players: %s (%s Bots)' % (len(es.getUseridList()),len(playerlib.getUseridList('#bot'))))
    for x in mystr:
        es.dbgmsg(0, x[:-1])
        L.append(x[:-1])
    L.append('')
    L += errorlog.lines(retain=False)
    errorlog.write_lines(L)
        
if scfg.debug:
    sys.excepthook = excepter
    
def dbg(text,write_to_file=False):
    if write_to_file or dcfg['debuglevel'] == '1':
        errorlog.write_lines([' ','XS: Extra debug info:',text,' '] + errorlog.lines(retain=False))
    if dcfg['debuglevel'] == '-1':
        return
    if dcfg['debuglevel'] in ('0','1'):
        es.dbgmsg(0,text)

##############################
### LOAD, HELPERS, PUBLICS ###
##############################

### Loading and Unloading ###

def load():
    dbg( '')
    dbg( 'XS: Loading...')
    if not callable(getattr(popuplib,'easylist',None)):
        es.dbgmsg(0,'XS: Popuplib version too old! Please update!')
        es.unload('extendedstats')
        return
    loadPackages()
    loadAddons()
    fillDatabase()
    loadToplist()
    saycommands[re.compile('\A%s%s' % (scfg.say_command_prefix,scfg.command_help))] = cmd_help
    es.addons.registerSayFilter(sayfilter)
    es.regclientcmd(scfg.command_help,'extendedstats/cmd_help')
    loadCVARS()
    loadMenus()
    es.regcmd('xs_resetlog','extendedstats/resetlog')
    #es.regcmd('xs_cleandb','extendedstats/cleandb')
    es.regcmd('xs_checkversion','extendedstats/checkversion')
    es.regcmd('xs_cfgsync','extendedstats/cfgsync')
    es.regcmd('xs_dbsync','extendedstats/dbsync')
    es.server.queuecmd('es_load extendedstats/events/%s' % (game))
    dbg('XS: Registered methods:')
    for method in methods:
        dbg( '    %s' % method)
    dcfg.sync()
    dbg('XS: Loaded successfully (%s)' % (info.version))
    dbg(' ')
            
def resetlog():
    errorlog.write_text('')
    
def cleandb():
    if es.getargc() == 2 and es.getargv(1) in tables:
        x = tables[es.getargv(1)].dropColumns()
    else:
        x = players.dropColumns()
    es.dbgmsg(0,'Database cleanup done. Removed %s unneccessary columns' % x)
    
def checkversion():
    esam = urllib.urlopen('http://addons.eventscripts.com/addons/chklatestver/extendedstats')
    esamversion = esam.read()
    localversion = info.version.split(':')[0]
    if esamversion != localversion:
        es.dbgmsg(0,text.getTokenString('update','newversion',[('newversion',esamversion),('currentversion',localversion)]))
        es.dbgmsg(0,text.getSimple('update','please_update'))
    else:
        es.dbgmsg(0,text.getTokenString('update','no_new',[('currentversion',localversion)]))
        
def cfgsync():
    dcfg.sync()
    
def dbsync():
    db.commit()

def unload():
    es.unregsaycmd(scfg.say_command_prefix + scfg.command_help)
    for userid in pending:
        gamethread.cancelDelayed('xs_delayed_%s' % userid) 
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
    p.settitle(text.getSimple('helpmenu','title'))
    p.addoption('about',text.getSimple('helpmenu','about'))
    pattern = re.compile('__\w*__')
    doccmds = filter(lambda x: not pattern.search(x),text.strings['help'])
    for key in doccmds:
        p.addoption(key,key)
    p.addoption('nodoc',text.getSimple('helpmenu','nodoc'))
    
    nodocl = [text.getSimple('helpmenu','nodoc')] + filter(lambda x: x not in doccmds,uniquecommands)
    p = popuplib.easylist('xs_doc_nodoc', nodocl if len(nodocl) > 1 else [text.getSimple('helpmenu','no_nodoc')])
    p.settitle(text.getSimple('helpmenu','nodoc'))
        
    p = popuplib.easylist('xs_doc_about',text.getHelp('__about__'))
    p.settitle(text.getHelp('__about__title__',[('version',info.version)])[0])
    
    for command in text.strings['help']:
        p = popuplib.easylist('xs_doc_%s' % command,text.getHelp(command))
        p.settitle('eXtended Stats Help: %s' % command)
            
def loadToplist():
    global toplist
    columns = [('steamid','TEXT PRIMARY KEY')]
    for method in methods:
        columns.append((method,'REAL DEFAULT 0.0'))
    toplist = db.newTable('toplist',columns,'steamid')
    for steamid in players:
        if not steamid in toplist:
            toplist.newplayer(steamid)
            for method in methods.keys():
                toplist.update(steamid,method,methods[method](players,steamid))
    tables['toplist'] = toplist
                    
### Publics ###
        
def registerMethod(package,name,method): # string,string,method
    if scfg.allMethods or name.lower() in scfg.methodList:
        methods[name.lower()] = method
        dbg( 'XS: Registered method %s for %s' % (name,package))
    
def registerCommand(command,addonname,callback,clientcommand=True,saycommand=True):
    global addoncommands, reggedccmd, reggedscmd, cmdhelp, uniquecommands
    uniquecommands.append(command)
    if clientcommand:
        es.regclientcmd(command,'extendedstats/addonCommandListener')
        addoncommands[command] = callback
        reggedccmd.append(command)
        dbg( 'XS: Registered clientcommand %s for %s' % (command,addonname))
    if saycommand:
        command = scfg.say_command_prefix + command
        saycommands[re.compile('%s(\s|\Z)' % RESafe(command))] = callback
        reggedscmd.append(command)
        dbg( 'XS: Registered saycommand %s for %s' % (command,addonname))
        
def loadEvents(addonname):
    if eventsdir.joinpath('%s/%s.py' % (addonname,addonname)).isfile():
        es.server.queuecmd('es_load extendedstats/events/%s' % addonname)
        
def RESafe(s):
    for char in ['.', '^', '$', '*', '+', '?', '{', '[', ']', '\\', '|', '(', ')']:
        if char in s:
            s = s.replace(char,'\%s' % char)
    return s
    
def getScore(steamid,method):
    if method in players.columns:
        score = players.query(steamid,method)
        if method in scfg.negative_columns:
            return -score
        return score
    if method not in methods:
        method = dcfg['default_method'].strip()
    steamidlist = map(lambda x: es.getplayersteamid(x),playerlib.getUseridList('#human'))
    if not steamid in steamidlist:
        return toplist.query(steamid,method)
    return methods[method](players,steamid)

def getRank(steamid,method):
    method = getMethod(method)
    if method in players.columns:
        direction = 'DESC'
        if method in scfg.negative_columns:
            direction = 'ASC'
        players.execute("SELECT steamid FROM xs_main ORDER BY %s %s" % (method,direction))
        allplayers = players.fetchall()
        return allplayers.index(steamid) + 1,len(allplayers)
    else:
        for userid in playerlib.getUseridList('#human'):
            steamid = es.getplayersteamid(userid)
            toplist.update(steamid,method,methods[method](players,steamid))
        toplist.execute("SELECT steamid FROM xs_toplist ORDER BY %s DESC" % method)
        allplayers = toplist.fetchall()
    return allplayers.index(steamid) + 1,len(allplayers)

def getRankScore(steamid,method,refresh=False):
    method = getMethod(method)
    if method in players.columns:
        score = players.query(steamid,method)
        direction = '>'
        if method in scfg.negative_columns:
            direction = '<'
        players.execute("SELECT steamid FROM xs_main WHERE %s%s%s" % (method,direction,score))
        rank = len(players.fetchall()) + 1
    else:
        if refresh:
            for userid in playerlib.getUseridList('#human'):
                steamid = es.getplayersteamid(userid)
                toplist.update(steamid,method,methods[method](players,steamid))
        score = toplist.query(steamid,method)
        toplist.execute("SELECT steamid FROM xs_toplist WHERE %s>%s" % (method,score))
        rank = len(toplist.fetchall()) + 1
    return rank,score,len(players)

def getToplist(x,method=None):
    method = getMethod(method)
    tlist = []
    if method in players.columns:
        players.execute("SELECT steamid,%s FROM xs_main ORDER BY %s DESC LIMIT %s" % (method,method,x))
        for row in players.fetchall():
            steamid,score = row
            tlist.append((score,steamid))
    else:
        for userid in playerlib.getUseridList('#human'):
            steamid = es.getplayersteamid(userid)
            score = methods[method](players,steamid)
            toplist.update(steamid,method,score)
        query = "SELECT %s,steamid FROM xs_toplist ORDER BY %s DESC LIMIT %s" % (method,method,x)
        toplist.execute(query)
        for row in toplist.fetchall():
            tlist.append(row)
    return tlist

def getName(steamid):
    settings_name = players.query(steamid,'settings_name')
    if settings_name:
        return settings_name
    dbname = players.query(steamid,'name1')
    if dbname:
        return dbname
    return 'unnamed'

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
    if not method and dcfg['default_method'] in keys:
        return dcfg['default_method']
    if method in keys:
        return method.strip()
    if dcfg['default_method'] in keys:
        return dcfg['default_method'].strip()
    return keys[0]

def addonIsLoaded(addonname):
    return addonname in map(lambda x: addonlistpattern.findall(str(x))[0][:-2],es.addons.getAddonList())

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
        
def suffix(rank):
    rank = str(rank)
    end = rank[-1]
    if end == '1':
        return rank + text.getSimple('suffix','one')
    if end == '2':
        return rank + text.getSimple('suffix','two')
    if end == '3':
        return rank + text.getSimple('suffix','three')
    return rank + text.getSimple('suffix','other')
        
    
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
    
def cmd_help(userid=None,args=None):
    if not userid:
        userid = es.getcmduserid()
    popuplib.send('xs_help_menu',userid)
    
def helpCallback(userid,choice,name):
    popuplib.send('xs_doc_%s' % choice,userid)
        
def pendingCheck(userid):
    steamid = es.getplayersteamid(userid)
    if steamid != 'STEAM_ID_PENDING':
        if not steamid in players:
            players.newplayer(steamid)
        if not steamid in toplist:
            toplist.newplayer(steamid)
        players.increment(steamid,'sessions')
        players.update(steamid,'sessionstart',time.time())
        players.update(steamid,'lastseen',time.time())
        players.update(steamid,'teamchange_time',time.time())
        newname = es.getplayername(ev['userid'])
        players.name(steamid,newname)
        newconnected.remove(ev['userid'])
        if ev['userid'] in pending:
            pending.remove(ev['userid'])
    else:
        gamethread.delayedname(1, 'xs_delayed_%s' % ev['userid'], pendingCheck, kw={userid:ev['userid']})

def sayfilter(userid,fulltext,teamonly):
    fulltext = fulltext.strip('"') 
    dbg('Sayfilter triggered')
    dbg(fulltext)
    for saycmd in saycommands:
        dbg('checking command...')
        if saycmd.search(fulltext):
            dbg('command found!')
            saycommands[saycmd](userid,fulltext.split(' ')[1:])
            if dcfg.as_bool('visible_saycommands'):
                dbg('visible saycommands on, show command')
                return userid,fulltext,teamonly
            dbg('visible saycommands off, eat command')
            return userid,None,None
    dbg('nothing found')
    return userid,fulltext,teamonly
    
##############################
###         EVENTS         ###
##############################

# moved to /games/

##############################
###    TEXT  CONVERSION    ###
##############################

class MissingLanguageFileError(Exception):
    def __init__(self,value):
        self.value = value
    def __str__(self):
        return repr("No language files for 'en' or '%s' could be found!" % self.value)

class TextConverter(object):
    def __init__(self,lang):
        txtfile = xspath.joinpath('strings_%s.ini' % scfg.language)
        self.strings = configobj.ConfigObj(txtfile)
        self.cpattern = re.compile('f[.]\d+')
        self.qpattern = re.compile('f[?]\d+')
        self.epattern = re.compile('f!\d+')
        self.dpattern = re.compile('f![?]\d+')
        
    def getSimple(self,section,name):
        return self.strings['general strings'][section][name]
    
    def getTokenString(self,section,name,tokens):
        s = self.strings['general strings'][section][name]
        for name,value in tokens:
            pattern = re.compile('([$]%s[$])' % name)
            s = pattern.sub(value,s)
        return s
    
    def getHelp(self,command,tokens=[]):
        l = self.strings['help'][command]
        if not type(l) == list:
            l = [l]
        if tokens:
            ll = []
            for s in l:
                for name,value in tokens:
                    pattern = re.compile('([$]%s[$])' % name)
                    s = pattern.sub(value,s)
                ll.append(s)
            return ll
        return l
        
        
    def getCmdString(self,steamid,cmd,method,score,rank,totalplayers):
        methodname = method
        s = self.strings['commands'][cmd]
        if not method in s:
            method = '__standard__'
        s = s[method]
        tokens = self.getTokens(s)
        dbg('getCmdString(%s,%s,%s,%s,%s,%s)' % (steamid,cmd,method,score,rank,totalplayers))
        for token in tokens:
            name,style,raw = token
            dbg('Tokens: name: %s (%s), style: %s (%s), raw: %s (%s)' % (name,type(name),style,type(style),raw,type(raw)))
            if name == 'rank':
                s = s.replace(raw,suffix(rank))
            elif name == 'totalplayers':
                s = s.replace(raw,str(totalplayers))
            elif name == 'score':
                scr = self.nice(score,style)
                dbg('Score: %s' % scr)
                s = s.replace(raw,scr)
            elif name == 'method':
                s = s.replace(raw,methodname)
            elif name == 'name':
                s = s.replace(raw,getName(steamid))
            else:
                tmp = getScore(steamid,name)
                dbg('Temp: %s' % tmp)
                scr = self.nice(tmp,style)
                dbg('Score: %s' % scr)
                s = s.replace(raw,scr)
        dbg('Result: %s' % s, True)
        return s
    
    def nice(self,value,style):
        dbg('Input value: %s' % value)
        if style[0] not in ('s','f','i'):
            raise ValueError, 'Invalid token type: %s' % style
        elif style == 'i':
            return str(value).split('.')[0]
        value = str(value)
        if style == 's':
            return value
        elif style == 'f':
            style = 'f.3'
        if self.cpattern.search(style):
            dbg('comma pattern found (%s)' % style)
            amount = int(style[2:])
            return value[:value.find('.') + amount + 1 if '.' in value else len(value)]
        elif self.epattern.search(style):
            dbg('exclamationmark pattern found (%s)' % style)
            amount = int(style[2:])
            value = str(value)
            if not '.' in value:
                return value
            pre,post = value.split('.')
            if len(pre) >= amount:
                return pre
            else:
                return '%s.%s' % (pre,post[:amount - len(pre)])
        elif self.qpattern.search(style):
            dbg('questionmark pattern found (%s)' % style)
            amount = int(style[2:])
            value = str(value)
            if not '.' in value:
                return value
            pre,post = value.split('.')
            if len(pre) >= amount:
                return pre
            post = post[:amount-len(pre)]
            while 1:
                if not post:
                    break
                if post[-1] == '0':
                    post = post[:-1]
                else:
                    break
            if not post:
                return pre
            return '%s.%s' % (pre,post)
        elif self.dpattern.search(style):
            dbg('double pattern found (%s)' % style)
            amount = int(style[3:])
            value = str(value)
            if not '.' in value:
                return value
            pre,post = value.split('.')
            if len(pre) >= amount:
                return pre
            post = post[:amount-len(pre)]
            while 1:
                if not post:
                    break
                if post[-1] == '0':
                    post = post[:-1]
                else:
                    break
            if not post:
                return pre
            return '%s.%s' % (pre,post)
            
        else:
            dbg('no pattern found (%s)' % style)
            raise ValueError, 'Invalid token type: %s' % style
        
    def getTokens(self,s):
        pattern = re.compile('[$][(]?\w?[.]?[!]?[?]?[!?]?\d?[)]?\w*[$]')
        return map(lambda x: (x[x.find(')') + 1 if ')' in x else 1:-1],x[2:x.find(')')] if '(' in x else 's',x),pattern.findall(s))
text = TextConverter('en')

##############################
### DYNAMIC CONFIGURATION  ###
##############################

def server_cvar(ev):
    if ev['cvarname'] in dcfg.cvars():
        dcfg[ev['cvarname'][3:]] = ev['cvarvalue']

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
            return self.__d__[s].strip()
        L = self.__filepath__.lines(retain=False)
        for line in L:
            if not line.startswith('//'):
                var,val = line.split('=',1)
                var = var.strip()
                if val.count('//') == 1:
                    val = val.split('//')[0].strip()
                if var == s:
                    self.__d__[var] = val
                    self.__cvars__.append(self.__cvarprefix__ + var)
                self[var] = val
                return val.strip()
        return None
    
    def __contains__(self,s):
        if s in self.__d__:
            return True
        L = self.__filepath__.lines(retain=False)
        for line in L:
            if line.startswith(s):
                return True
        return False

    def __setitem__(self,key,value):
        key = str(key)
        value = str(value)
        cvar = self.__cvarprefix__ + key
        self.__d__[key] = value
        if not cvar in self.__cvars__:
            self.__cvars__.append(cvar)
        L = self.__filepath__.lines(retain=False)
        done = False
        for line in L:
            if not line.startswith('//') and line.count('=') != 0:
                if line.startswith(key):
                    if line.count('//') == 1:
                        L[L.index(line)] = '%s = %s //%s' % (key,value,line.split('//')[1])
                    else:
                        L[L.index(line)] = '%s = %s' % (key,value)
                    done = True
                    break
        if not done:
            L.append('%s = %s' % (key,value))
        self.__filepath__.write_lines(L)
        es.ServerVar(cvar,value).addFlag('notify')
            

    def sync(self):
        self.__d__ = {}
        self.__cvars__ = []
        L = self.__filepath__.lines(retain=False)
        for line in L:
            if not line.startswith('//') and line.count('=') != 0:
                var,val = line.split('=')
                var = var.strip()
                if val.count('//') == 1:
                    val = val.split('//')[0].strip()
                self.__d__[var] = val
                es.ServerVar(self.__cvarprefix__ + var,val).addFlag('notify')
                self.__cvars__.append(self.__cvarprefix__ + var)
        self.__filepath__.write_lines(L)
                
    def keys(self):
        return self.__d__.keys()
        
    def cvars(self):
        return self.__cvars__
    
    def as_bool(self,s):
        return self[s].lower() in ('1','on','true')
    
    def as_list(self,s):
        value = self[s]
        if ';' in value:
            return map(lambda x: x.strip(),value.split(';'))
        else:
            return map(lambda x: x.strip(),value.split(','))
        
    def add(self,s,v): # LIST ONLY
        current = self.as_list(s)
        current.append(v)
        self[s] = ';'.join(current)
        
    def remove(self,s,v): # LIST ONLY
        current = self.as_list(s)
        if v in current:
            current.remove(v)
        self[s] = ';'.join(current)
        
    
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
        
    def as_bool(self, var):
        return dcfg.as_bool('%s_%s' % (self.__an__,var))
    
    def as_list(self, var):
        return dcfg.as_list('%s_%s' % (self.__an__,var))
    
    def keys(self):
        return filter(lambda x: x.startswith('%s_' % self.__an__),dcfg.keys())
    
    def __contains__(self,var):
        return ('%s_%s' % (self.__an__,var)) in dcfg
    
    def add(self,var,val):
        dcfg.add('%s_%s' % (self.__an__,var),val)
        
    def remove(self,var,val):
        dcfg.remove('%s_%s' % (self.__an__,var),val)
        
default = {
    'default_method': 'kdr',
    'debuglevel': '0',
    'statsme_methods': '',
    'visible_saycommands': 'on',
}
dcfg = dyncfg(gamepath.joinpath('cfg/extendedstats.cfg'),'xs_',default)
        
### EXPERIMENTAL NEW SQLITE WRAPPER CLASSES ###

class Database(object):
    def __init__(self):
        self.con = sqlite3.connect(xspath.joinpath('database.sqlite'))
        self.con.text_factory = str
        self.cur = self.con.cursor()
        
    def newTable(self,tablename,columns,primarykey):
        return Table(self.con,self.cur,tablename,columns,primarykey)
    
    def commit(self):
        self.con.commit()
    
db = Database()
    
class Table(object):
    def __init__(self,con,cur,tablename,columns,primarykey):
        self.con = con
        self.cur = cur
        self.pk = primarykey
        self.table = tablename
        self.columns = []
        self._create(columns)
        self.columns = map(lambda x: x[0],columns)
        self._numericColumns = filter(lambda x: self._numericColumn(x),self.columns)    
        
    def _create(self,columns):
        coldef = ', '.join(map(lambda x: '%s %s' % x,columns))
        if self._tableExists():
            existingColumns = self._getColumns()
            newcolumns = filter(lambda x: x[0] not in existingColumns,columns)
            self.addColumns(newcolumns,True)
        else:
            self.execute("CREATE TABLE xs_%s (%s)" % (self.table,coldef))
        self.execute("CREATE TEMP TABLE IF NOT EXISTS xst_%s (%s)" % (self.table,coldef))
            
    def _tableExists(self):
        return len(self.con.execute('PRAGMA table_info(xs_%s)' % self.table).fetchall()) > 0
        
    def _getColumns(self):
        return map(lambda x: x[1], self.con.execute('PRAGMA table_info(xs_%s)' % (self.table)).fetchall())
    
    def __iter__(self):
        self.execute("SELECT %s FROM xs_%s" % (self.pk,self.table))
        return iter(self.fetchall())
    
    def __len__(self):
        self.execute("SELECT %s FROM xs_%s" % (self.pk,self.table))
        return len(self.fetchall())
    
    def _numericColumn(self,key):
        self.execute('PRAGMA table_info(xs_%s)' % self.table)
        all = self.fetchall()
        column = filter(lambda x: x[1] == key,all)[0]
        return column[2] in ('INTEGER','REAL')
        
    def addColumns(self,columns,initial=False):
        allcolumns = self._getColumns()
        for column in filter(lambda x: x[0] not in allcolumns,columns):
            self.execute("ALTER TABLE xs_%s ADD COLUMN %s %s" % (self.table,column[0],column[1]))
            if not initial:
                self.execute("ALTER TABLE xst_%s ADD COLUMN %s %s" % (self.table,column[0],column[1]))
        self.columns += map(lambda x: x[0],columns)
        self._numericColumns = filter(lambda x: self._numericColumn(x),self.columns)
        
    def dropColumns(self):
        oldcolumns = filter(lambda x: x not in self.columns,self._getColumns())
        if not oldcolumns:
            return 0

        self.cur.execute("PRAGMA table_info(xs_%s)" % self.table)
        colnames = []
        coldef = []
        for row in self.cur.fetchall():
            if row[1] in oldcolumns:
                continue
            colnames.append(row[1])
            coldef.append('%s %s %s' % (row[1],row[2],'DEFAULT %s' % row[4] if not int(row[5]) == 1 else 'PRIMARY KEY'))
        coldef =  ', '.join(coldef)
        self.cur.execute("SELECT %s FROM xs_%s" % (', '.join(colnames),self.table))
        queries = []
        for row in self.cur.fetchall():
            values = []
            for val in row:
                if type(val) in (float,int):
                    values.append(str(val))
                elif not val:
                    values.append('NULL')
                else:
                    values.append("'%s'" % val)
            queries.append("INSERT INTO xs_%s (%s) VALUES (%s)" % (self.table,', '.join(colnames),', '.join(values)))
        self.cur.execute("DROP TABLE xs_%s" % self.table)
        self.cur.execute("CREATE TABLE xs_%s (%s)" % (self.table,coldef))
        for query in queries:
            self.cur.execute(query)
        self.columns = self._getColumns()
        return len(oldcolumns)
        
    def execute(self,sql):
        self.cur.execute(sql)
            
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
        # If fetchone(...) fails, uncomment next line
        # dbg('%s (%s)' % (one,type(one)),True)
        if len(one) == 1:
            return one[0]
        return one
    
    def __contains__(self,steamid):
        self.execute("SELECT * FROM xs_%s WHERE %s='%s'" % (self.table,self.pk,steamid))
        return bool(self.cur.fetchone()) 
    
    def query(self,steamid,key):
        query = "SELECT %s FROM xs_%s WHERE %s='%s'" % (key,self.table,self.pk,steamid)
        # If query(...) fails, uncomment next line
        # dbg(query,True)
        self.execute(query)
        return self.fetchone()
        
    def convert(self,key,value):
        if key in self._numericColumns:
            return value
        return "'%s'" % value
        
    def update(self,steamid,key,newvalue):
        query = "UPDATE xs_%s SET %s=%s WHERE %s='%s'" % (self.table,key,self.convert(key,newvalue),self.pk,steamid)
        self.execute(query)
        self._update(steamid,key,newvalue)
        
    def increment(self,steamid,key):
        old = self.query(steamid,key)
        if not old:
            old = 0
        self.execute("UPDATE xs_%s SET %s=%s WHERE %s='%s'" % (self.table,key,old + 1,self.pk,steamid))
        self._increment(steamid,key)
        
    def add(self,steamid,key,amount):
        current = self.query(steamid,key)
        newamount = current + amount
        self.execute("UPDATE xs_%s SET %s=%s WHERE %s='%s'" % (self.table,key,newamount,self.pk,steamid))
        self._add(steamid,key,amount)
        
    def name(self,steamid,newname):
        self.execute("SELECT name1,name2,name3,name4,name5 FROM xs_%s WHERE %s='%s'" % (self.table,self.pk,steamid))
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
        self._name(steamid,newname)

    def newplayer(self,steamid):
        self.execute("INSERT INTO xs_%s (%s) VALUES ('%s')" % (self.table,self.pk,steamid))
        
    def commit(self):
        self.con.commit()
        
    def _update(self,steamid,key,newvalue):
        if not self._contains(steamid):
            self._newplayer(steamid)
        self.execute("UPDATE xst_%s SET %s=%s WHERE %s='%s'"  % (self.table,key,self.convert(key,newvalue),self.pk,steamid))
        
    def _query(self,steamid,key):
        self.execute("SELECT %s FROM xst_%s WHERE %s='%s'" % (key,self.table,self.pk,steamid))
        return self.fetchone()
    
    def _increment(self,steamid,key):
        if not self._contains(steamid):
            self._newplayer(steamid)
        old = self._query(steamid,key)
        if not old:
            old = 0
        self.execute("UPDATE xst_%s SET %s=%s WHERE %s='%s'" % (self.table,key,old + 1,self.pk,steamid))
    
    def _add(self,steamid,key,amount):
        if not self._contains(steamid):
            self._newplayer(steamid)
        current = self._query(steamid,key)
        newamount = current + amount
        self.execute("UPDATE xst_%s SET %s=%s WHERE %s='%s'" % (self.table,key,newamount,self.pk,steamid))
    
    def _name(self,steamid,newname):
        if not self._contains(steamid):
            self._newplayer(steamid)
        self.execute("SELECT name1,name2,name3,name4,name5 FROM xst_%s WHERE %s='%s'" % (self.table,self.pk,steamid))
        cnames = self.fetchone()
        if not cnames:
            self._update(steamid,'name1',newname)
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
                self._update(steamid,'name%s' % (x + 1),nnames[x])
        self._increment(steamid,'changename')
    
    def _newplayer(self,steamid):
        self.execute("INSERT INTO xst_%s (%s) VALUES ('%s')" % (self.table,self.pk,steamid))
    
    def _contains(self,steamid):
        self.execute("SELECT * FROM xst_%s WHERE %s='%s'" % (self.table,self.pk,steamid))
        return bool(self.cur.fetchone())
    
    def __getColumns(self):
        return map(lambda x: x[1], self.con.execute('PRAGMA table_info(xst_%s)' % (self.table)).fetchall())
    
    def getchanges(self):
        columns = self.__getColumns()
        self.execute("SELECT * FROM xst_%s" % self.table)
        data = self.fetchall()
        self.execute("DELETE FROM xst_%s" % self.table)
        return (columns,data)
            

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
    ('hurt','INTEGER DEFAULT 0'),
    ('hurt_damage', 'REAL DEFAULT 0.0'),
    ('attacked', 'INTEGER DEFAULT 0'),
    ('attacked_damage', 'REAL DEFAULT 0.0'),
    ('jump', 'INTEGER DEFAULT 0'),
    ('jump_startpos','TEXT DEFAULT NULL'),
    ('team_1_time', 'REAL DEFAULT 0.0'),
    ('team_2_time', 'REAL DEFAULT 0.0'),
    ('team_3_time', 'REAL DEFAULT 0.0'),
    ('teamchange_time', 'REAL DEFAULT NULL'),
    ('current_team', 'INTEGER DEFAULT 0.0'),
    ('win', 'REAL DEFAULT 0.0'),
    ('lose', 'REAL DEFAULT 0.0'),
    ('rounds', 'REAL DEFAULT 0.0'),
    ('ban', 'REAL DEFAULT 0.0'),
    ('name1', "TEXT DEFAULT 'unnamed'"),
    ('name2', "TEXT DEFAULT NULL"),
    ('name3', "TEXT DEFAULT NULL"),
    ('name4', "TEXT DEFAULT NULL"),
    ('name5', "TEXT DEFAULT NULL"),
    ('settings_name','TEXT DEFAULT NULL'),
    ('settings_method','TEXT DEFAULT NULL'),
]
dod_weapons = ['world','punch','30cal', 'amerknife', 'bar', 'bazooka', 'c96', 'colt', 'frag_us','frag_ger', 'garand', 'riflegren_us', 'riflegren_ger', 'k98', 'k98_scoped', 'm1carbine', 'mg42', 'mp40', 'mp44', 'p38', 'pschreck', 'spade', 'spring', 'stick', 'thompson']
cstrike_weapons = ['world','glock', 'usp', 'p228', 'deagle', 'fiveseven', 'elite', 'm3', 'xm1014', 'tmp', 'mac10', 'mp5navy', 'ump45', 'p90', 'famas', 'galil', 'ak47', 'scout', 'm4a1', 'sg550', 'g3sg1', 'awp', 'sg552', 'aug', 'm249', 'hegrenade', 'flashbang', 'smokegrenade', 'knife', 'c4']
if game == 'cstrike':
    columns += cstrike_columns
    columns += map(lambda x: ('death_%s' % x,'INTEGER DEFAULT 0'),cstrike_weapons)
    columns += map(lambda x: ('kill_%s' % x,'INTEGER DEFAULT 0'),cstrike_weapons)
    columns += map(lambda x: ('damage_%s' % x,'REAL DEFAULT 0.0'),cstrike_weapons)
elif game == 'dod':
    columns += dod_columns
    columns += map(lambda x: ('death_%s' % x,'INTEGER DEFAULT 0'),dod_weapons)
    columns += map(lambda x: ('kill_%s' % x,'INTEGER DEFAULT 0'),dod_weapons)
    columns += map(lambda x: ('damage_%s' % x,'REAL DEFAULT 0.0'),dod_weapons)
players = db.newTable('main',columns,'steamid')
tables['main'] = players
weapons = None
wcolumns = [('weapon','TEXT PRIMARY KEY'),('kills','INTEGER DEFAULT 0'),('damage','REAL DEFAULT 0.0')]
weapons = db.newTable('weapons',wcolumns,'weapon')
if game == 'cstrike':
    for weapon in filter(lambda x: x not in weapons,cstrike_weapons):
        weapons.newplayer(weapon)
elif game == 'dod':
    for weapon in filter(lambda x: x not in weapons,dod_weapons):
        weapons.newplayer(weapon)
tables['weapons'] = weapons