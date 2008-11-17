# Default eXtended Stats new_player for version 0.1.2:126
from extendedstats import extendedstats as xs
import es, time, popuplib

scfg = xs.scfg
text = xs.text

def load():
    xs.registerCommand(scfg.command_rank,'default',cmd_rank,helplist=['Usage: !rank [method]','method is optional.','To get a list of methods use !methods'])
    xs.registerCommand(scfg.command_statsme,'default',cmd_statsme,helplist=['Usage: !statsme [method]',' method is optional.','To get a list of methods use !methods'])
    xs.registerCommand(scfg.command_methods,'default',cmd_methods,helplist=['Usage: !methods','Will show a list of available methods'])
    xs.registerCommand(scfg.command_settings,'default',cmd_settings,helplist=['Usage: !settings','Will open a menu to change personal settings'])
    xs.registerCommand(scfg.command_top,'default',cmd_top,True,False,['Usage: topX [method].','X should be an integer.','method is optional.','To get a list of methods use !methods'])
    xs.registerCommand(scfg.command_commands,'default',cmd_commands,helplist=['Shows a list of commands'])
    xs.addHelp(scfg.command_top,'Usage: topX [method]. X should be an integer. method is optional. To get a list of methods use !methods')
    es.addons.registerSayFilter(xs_filter)
    menus()
    
def menus():
    pplchck('xs_methods_list')
    methodslist = ['Methods available:']
    methodslist += xs.methods.keys()
    m = popuplib.easylist('xs_methods_list')
    m.settitle('Methods List:')
    for x in methodslist:
        m.additem(x)
    
def unload():
    es.addons.unregisterSayFilter(xs_filter)

def cmd_top(userid,args):
    if str(userid) in extendedstats.pending:
        es.tell(userid,txt.getSimple('sorry_pending'))
        return
    myargs = [scfg.default_top_x,None]
    for x in range(len(args)):
        myargs[x] = args[x]
    steamid = es.getplayersteamid(userid)
    method = method if not xs.players.query(steamid,'settings_method') else xs.players.query(steamid,'settings_method')
    method = xs.getMethod(myargs[1])
    displayTop(userid, int(myargs[0]), method)

def xs_filter(userid, message, team):
    text = message.strip('"')
    tokens = text.split(' ')
    cmd = tokens[0]
    if cmd.startswith(scfg.say_command_prefix + scfg.command_top) and len(tokens) < 3:
        if str(userid) in xs.pending:
            es.tell(userid,txt.getSimple('messages','sorry_pending'))
            return
        settings_method = xs.players.query(es.getplayersteamid(userid),'settings_method')
        default_method = xs.dcfg['default_method']
        token_is_given = len(tokens) == 2
        if token_is_given:
            token_is_given = tokens[1].lower() in xs.methods
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
    pplchck('xs_top_list_%s' % userid)
    topplayers = xs.getToplist(x,method)
    totalplayers = len(xs.players)
    toplist = popuplib.easylist('xs_top_list_%s' % userid)
    toplist.settitle('Top %s (%s):' % (x,method))
    i = 1
    for player in topplayers:
        toplist.additem(text.getCmdString(player[1],'top',method,player[0],i,totalplayers))
        i += 1
    toplist.send(userid)
    
def cmd_commands(userid,args):
    if popuplib.exists('xs_commands_list'):
        popuplib.send('xs_commands_list',userid)
    else:
        c = popuplib.easylist('xs_commands_list')
        c.settitle(text.getSimple('command list','title'))
        for x in xs.reggedccmd:
            c.additem(text.getTokenString('command list','console',[('command',x)]))
        for x in xs.reggedscmd:
            c.additem(text.getTokenString('command list','chat',[('command',x)]))
        c.send(userid)
    
def cmd_rank(userid,args):
    if str(userid) in xs.pending:
        es.tell(userid,txt.getSimple('messages','sorry_pending'))
        return
    steamid = es.getplayersteamid(userid)
    if len(args) == 1:
        method = xs.getMethod(args[0].lower())
    else:
        method = xs.getMethod(extendedstats.players.query(steamid,'settings_method'))
    rank,score,totalplayers = xs.getRankScore(steamid,method)
    es.tell(userid,text.getCmdString(steamid,'rank',method,score,rank,totalplayers))
    
def cmd_statsme(userid,args):
    if str(userid) in xs.pending:
        es.tell(userid,txt.getSimple('messages','sorry_pending'))
        return
    steamid = es.getplayersteamid(userid)
    methods_used = [xs.dcfg['default_method']]
    toprank = None
    lowrank = None
    refresh = True
    for method in xs.methods:
        rank,score,allplayers = xs.getRankScore(steamid,method,refresh)
        refresh = False
        # if toprank is None OR rank is smaller (smaller number = higher rank) than toprank
        if not toprank or rank < toprank[0]:
            toprank = (rank,score,method)
        if not lowrank or rank > lowrank[0]:
            lowrank = (rank,score,method)
    methods_used.append(toprank[2])
    methods_used.append(lowrank[2])
    defaultmethod = xs.getMethod()
    defaultrank,defaultscore = None,None
    if defaultmethod not in methods_used:
        defaultrank,defaultscore,allplageyers = xs.getRankScore(steamid,defaultmethod)
        methods_used.append(defaultmethod)
    personalrank,personalescore = None,None
    settings_method = xs.players.query(steamid,'settings_method')
    if settings_method in xs.methods.keys() and settings_method not in methods_used:
        personalrank,personalescore,allplayers = xs.getRankScore(steamid,settings_method)
        methods_used.append(settings_method)
    pplchck('xs_statshim_%s' % userid)
    statshim = popuplib.easylist('xs_statshim_%s' % userid)
    statshim.settitle(text.getSimple('statsme','title'))
    if defaultrank:
        statshim.additem(text.getCmdString(steamid,'statsme',xs.dcfg['default_method'],defaultscore,defaultrank,allplayers))
    if personalrank:
        statshim.additem(text.getCmdString(steamid,'statsme',settings_method,personalscore,personalrank,allplayers))
    statshim.additem(text.getCmdString(steamid,'statsme_toprank',toprank[2],toprank[1],toprank[0],allplayers))
    statshim.additem(text.getCmdString(steamid,'statsme_lowrank',lowrank[2],lowrank[1],lowrank[0],allplayers))
    if bool(xs.dcfg['statsme_methods']):
        mlist = xs.dcfg.as_list('statsme_methods')
        for method in filter(lambda x: (x in xs.methods or x in xs.players.columns) and x not in methods_used,mlist):
            methods_used.append(method)
            rank,score,allplayers = xs.getRankScore(steamid,method)
            statshim.additem(text.getCmdString(steamid,'statsme',method,score,rank,allplayers))
    statshim.send(userid)
    
def cmd_methods(userid,args):
    popuplib.send('xs_methods_list',userid)
    
def cmd_settings(userid,args):
    if str(userid) in xs.pending:
        es.tell(userid,txt.getSimple('messages','sorry_pending'))
        return
    pplchck('xs_settings_menu_%s' % userid)
    settingsmenu = popuplib.easymenu('xs_settings_menu_%s' % userid,'_popup_choice',settingsCallback)
    settingsmenu.settitle(text.getSimple('settings','titel_main'))
    settingsmenu.addoption('method',text.getSimple('settings','choose_method'))
    settingsmenu.addoption('name',text.getSimple('settings','choose_name'))
    settingsmenu.addoption('exit',text.getSimple('settings','exit'))
    settingsmenu.send(userid)
    
def settingsCallback(userid,choice,name):
    steamid = es.getplayersteamid(userid)
    if choice == 'method':
        pplchck('xs_methods_menu_%s' % userid)
        methodmenu = popuplib.easymenu('xs_methods_menu_%s' % userid,'_popup_choice',settingsCallback2)
        methodmenu.settitle(text.getSimple('settings','title_method'))
        settings_method = xs.players.query(steamid,'settings_method')
        for method in xs.methods.keys():
            if method == settings_method:
                methodmenu.addoption(('method',method),'-> %s' % method)
            else:
                methodmenu.addoption(('method',method),method)
        methodmenu.addoption(2,text.getSimple('settings','reset'))
        methodmenu.addoption(1,text.getSimple('settings','back'))
        methodmenu.send(userid)
    elif choice == 'name':
        pplchck('xs_name_menu_%s' % userid)
        namemenu = popuplib.easymenu('xs_name_menu_%s' % userid,'_popup_choice',settingsCallback2)
        namemenu.settitle(text.getSimple('settings','title_name'))
        settings_name = xs.players.query(steamid,'settings_method')
        xs.players.execute("SELECT name1,name2,name3,name4,name5 FROM xs_main WHERE steamid='%s'" % (steamid))
        names = xs.players.fetchone()
        if not type(names) == tuple:
            names = [names]
        for name in names:
            if name == settings_name:
                namemenu.addoption(('name',name),'-> %s' % name)
            else:
                namemenu.addoption(('name',name),name)      
        namemenu.addoption(2,text.getSimple('settings','reset'))          
        namemenu.addoption(1,text.getSimple('settings','back'))
        namemenu.send(userid)
    elif choice == 'exit':
        return
        
def settingsCallback2(userid,choice,name):
    steamid = es.getplayersteamid(userid)
    if choice == 1:
        cmd_settings(userid,None)
    elif choice == 2:
        if name == 'methods_menu':
            xs.players.update(steamid,'settings_method','NULL')
        elif name == 'name_menu':
            xs.players.update(steamid,'settings_name','NULL')
    else:
        xs.players.update(steamid,'settings_%s' % choice[0],choice[1])
        es.tell(userid,text.getSimple('settings','success'))
    if scfg.settings_menu_resend:
        cmd_settings(userid,None)

def pplchck(name):
    if popuplib.exists(name):
        popuplib.delete(name)