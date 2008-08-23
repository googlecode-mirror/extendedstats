# Default eXtended Stats new_player for version 0.1.2:126
from extendedstats import extendedstats # Import eXtended Stats
import es, time, popuplib

scfg = extendedstats.scfg

# This dict will be used to fill new players with default keys->values to prevent key not found errors.

def load():
    extendedstats.registerCommand(scfg.command_rank,'default',cmd_rank,helplist=['Usage: !rank [method]','method is optional.','To get a list of methods use !methods'])
    extendedstats.registerCommand(scfg.command_statsme,'default',cmd_statsme,helplist=['Usage: !statsme [method]',' method is optional.','To get a list of methods use !methods'])
    extendedstats.registerCommand(scfg.command_methods,'default',cmd_methods,helplist=['Usage: !methods','Will show a list of available methods'])
    extendedstats.registerCommand(scfg.command_settings,'default',cmd_settings,helplist=['Usage: !settings','Will open a menu to change personal settings'])
    extendedstats.registerCommand(scfg.command_top,'default',cmd_top,True,False,['Usage: topX [method].','X should be an integer.','method is optional.','To get a list of methods use !methods'])
    extendedstats.registerCommand(scfg.command_commands,'default',cmd_commands,helplist=['Shows a list of commands'])
    extendedstats.addHelp(scfg.command_top,'Usage: topX [method]. X should be an integer. method is optional. To get a list of methods use !methods')
    es.addons.registerSayFilter(xs_filter)
    menus()
    
def menus():
    pplchck('xs_methods_list')
    methodslist = ['Methods available:']
    methodslist += extendedstats.methods.keys()
    m = popuplib.easylist('xs_methods_list')
    m.settitle('Methods List:')
    for x in methodslist:
        m.additem(x)
    
def unload():
    es.addons.unregisterSayFilter(xs_filter)

def cmd_top(userid,args):
    if str(userid) in extendedstats.pending:
        es.tell(userid,"Sorry but your Steam ID is currently pending and you may not use this command. Please try again later.")
        return
    myargs = [scfg.default_top_x,None]
    for x in range(len(args)):
        myargs[x] = args[x]
    steamid = es.getplayersteamid(userid)
    method = method if not extendedstats.players.query(steamid,'settings_method') else extendedstats.players.query(steamid,'settings_method')
    method = extendedstats.getMethod(myargs[1])
    displayTop(userid, int(myargs[0]), method)

def xs_filter(userid, message, team):
    text = message.strip('"')
    tokens = text.split(' ')
    cmd = tokens[0]
    if cmd.startswith(scfg.say_command_prefix + scfg.command_top) and len(tokens) < 3:
        if str(userid) in extendedstats.pending:
            es.tell(userid,"Sorry but your Steam ID is currently pending and you may not use this command. Please try again later.")
            return
        settings_method = extendedstats.players.query(es.getplayersteamid(userid),'settings_method')
        default_method = extendedstats.dcfg['default_method']
        token_is_given = len(tokens) == 2
        if token_is_given:
            token_is_given = tokens[1].lower() in extendedstats.methods
        if token_is_given:
            method = tokens[1].lower()
        elif settings_method:
            method = settings_method
        else:
            method = default_method 
        x = ''.join(filter(lambda x: x.isdigit(),cmd))
        displayTop(userid, int(x) if x != '' else scfg.default_top_x, method)
    return (userid,text,team)
    
def displayTop(userid,x,method):
    chckactive(userid)
    pplchck('xs_top_list_%s' % userid)
    topplayers = extendedstats.getToplist(x,method)
    toplist = popuplib.easylist('xs_top_list_%s' % userid)
    toplist.settitle('Top %s (%s):' % (x,method))
    i = 1
    for player in topplayers:
        toplist.additem('%s: %s (%s)' % (suffix(i),extendedstats.getName(player[1]),nice(player[0])))
        i += 1
    toplist.send(userid)
    
def cmd_commands(userid,args):
    chckactive(userid)
    if popuplib.exists('xs_commands_list'):
        popuplib.send('xs_commands_list',userid)
    else:
        c = popuplib.easylist('xs_commands_list')
        c.settitle('Command list:')
        for x in extendedstats.reggedccmd:
            c.additem('%s (console)' % x)
        for x in extendedstats.reggedscmd:
            c.additem('%s (chat)' % x)
        c.send(userid)
    
def cmd_rank(userid,args):
    if str(userid) in extendedstats.pending:
        es.tell(userid,"Sorry but your Steam ID is currently pending and you may not use this command. Please try again later.")
        return
    steamid = es.getplayersteamid(userid)
    if len(args) == 1:
        method = extendedstats.getMethod(args[0].lower())
    else:
        method = extendedstats.getMethod(extendedstats.players.query(steamid,'settings_method'))
    rank,allplayers = extendedstats.getRank(steamid,method)
    es.tell(userid,'You are ranked %s of %s with %s points (%s)' % (suffix(rank),allplayers,nice(extendedstats.getScore(steamid,method)),method))
    
def cmd_statsme(userid,args):
    if str(userid) in extendedstats.pending:
        es.tell(userid,"Sorry but your Steam ID is currently pending and you may not use this command. Please try again later.")
        return
    steamid = es.getplayersteamid(userid)
    methods_used = [extendedstats.dcfg['default_method']]
    top = None
    low = None
    tr = 0
    ts = 0
    for method in extendedstats.methods:
        r,s = extendedstats.getRank(steamid,method)[0], extendedstats.getScore(steamid,method)
        tr += r
        ts += s
        if not top or r > top:
            top = (r,nice(s),method)
        if not low or r < low:
            low = (r,nice(s),method)
    drtotal, ds = extendedstats.getRank(steamid,extendedstats.getMethod()), extendedstats.getScore(steamid,extendedstats.getMethod())
    dr,total = drtotal
    pr, ps = None, None
    settings_method = extendedstats.players.query(steamid,'settings_method')
    if settings_method in extendedstats.methods.keys() and settings_method not in methods_used:
        pr = extendedstats.getRank(steamid,settings_method)[0]
        ps = extendedstats.getScore(steamid,settings_method)
    chckactive(userid)
    pplchck('xs_statshim_%s' % userid)
    statshim = popuplib.easylist('xs_statshim_%s' % userid)
    statshim.settitle('Your stats:')
    statshim.additem('%s: %s of %s with %s' % (extendedstats.dcfg['default_method'],suffix(dr),total,nice(ds)))
    if pr:
        statshim.additem('%s: %s of %s with %s' % (settings_method,suffix(pr),total,nice(ps)))
    statshim.additem('Top rank: %s of %s with %s using %s' % (suffix(top[0]),total,top[1],top[2]))
    statshim.additem('Low rank: %s of %s with %s using %s' % (suffix(low[0]),total,low[1],low[2]))
    if bool(extendedstats.dcfg['statsme_methods']):
        mlist = extendedstats.dcfg.as_list('statsme_methods')
        for method in filter(lambda x: x in extendedstats.methods or x in extendedstats.players.columns,mlist):
            methods_used.append(method)
            statshim.additem('%s: %s of %s with %s' % (method,suffix(extendedstats.getRank(steamid,method)[0]),total,nice(extendedstats.getScore(steamid,method))))
    statshim.send(userid)
    
def cmd_methods(userid,args):
    chckactive(userid)
    popuplib.send('xs_methods_list',userid)
    
def cmd_settings(userid,args):
    if str(userid) in extendedstats.pending:
        es.tell(userid,"Sorry but your Steam ID is currently pending and you may not use this command. Please try again later.")
        return
    chckactive(userid)
    pplchck('xs_settings_menu_%s' % userid)
    settingsmenu = popuplib.easymenu('xs_settings_menu_%s' % userid,'_popup_choice',settingsCallback)
    settingsmenu.settitle('Your eXtended Stats settings: Main')
    settingsmenu.addoption('method','Choose your personal method')
    settingsmenu.addoption('name','Choose your preferred name')
    settingsmenu.addoption('exit','Exit')
    settingsmenu.send(userid)
    
def settingsCallback(userid,choice,name):
    steamid = es.getplayersteamid(userid)
    if choice == 'method':
        pplchck('xs_methods_menu_%s' % userid)
        methodmenu = popuplib.easymenu('xs_methods_menu_%s' % userid,'_popup_choice',settingsCallback2)
        methodmenu.settitle('Your eXtended Stats settings: Method')
        settings_method = extendedstats.players.query(steamid,'settings_method')
        for method in extendedstats.methods.keys():
            if method == settings_method:
                methodmenu.addoption(('method',method),'-> %s' % method)
            else:
                methodmenu.addoption(('method',method),method)
        methodmenu.addoption(2,'Reset setting')
        methodmenu.addoption(1,'Back to Main')
        methodmenu.send(userid)
    elif choice == 'name':
        pplchck('xs_name_menu_%s' % userid)
        namemenu = popuplib.easymenu('xs_name_menu_%s' % userid,'_popup_choice',settingsCallback2)
        namemenu.settitle('Your eXtended Stats settings: Name')
        settings_name = extendedstats.players.query(steamid,'settings_method')
        extendedstats.players.execute("SELECT name1,name2,name3,name4,name5 FROM xs_main WHERE steamid='%s'" % (steamid))
        names = extendedstats.players.fetchone()
        if not type(names) == tuple:
            names = [names]
        for name in names:
            if name == settings_name:
                namemenu.addoption(('name',name),'-> %s' % name)
            else:
                namemenu.addoption(('name',name),name)      
        namemenu.addoption(2,'Reset setting')          
        namemenu.addoption(1,'Back to main')
        namemenu.send(userid)
    elif choice == 'exit':
        return
        
def settingsCallback2(userid,choice,name):
    steamid = es.getplayersteamid(userid)
    if choice == 1:
        cmd_settings(userid,None)
    elif choice == 2:
        if name == 'methods_menu':
            extendedstats.players.update(steamid,'settings_method','NULL')
        elif name == 'name_menu':
            extendedstats.players.update(steamid,'settings_name','NULL')
    else:
        extendedstats.players.update(steamid,'settings_%s' % choice[0],choice[1])
        es.tell(userid,'Your eXtended Stats settings have been changed successfully.')
    if scfg.settings_menu_resend:
        cmd_settings(userid,None)

def pplchck(name):
    if popuplib.exists(name):
        popuplib.delete(name)
        
def chckactive(userid):
    es.cexec(userid,'slot10')
        
def nice(score):
    if type(score) == float:
        return '%.3f' % score
    return score

def suffix(rank):
    rank = str(rank)
    end = rank[-1]
    if end == '1':
        return rank + 'st'
    if end == '2':
        return rank + 'nd'
    if end == '3':
        return rank + 'rd'
    return rank + 'th'