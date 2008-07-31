# Default commands for version 0.0.5:80
import es, popuplib
from extendedstats import extendedstats as xs

def load():
    xs.registerCommand('rank','default_commands',cmd_rank,helplist=['Usage: !rank [method]','method is optional.','To get a list of methods use !methods'])
    xs.registerCommand('statsme','default_commands',cmd_statsme,helplist=['Usage: !statsme [method]',' method is optional.','To get a list of methods use !methods'])
    xs.registerCommand('methods','default_commands',cmd_methods,helplist=['Usage: !methods','Will show a list of available methods'])
    xs.registerCommand('settings','default_commands',cmd_settings,helplist=['Usage: !settings','Will open a menu to change personal settings'])
    xs.addHelp('topx','Usage: topX [method]. X should be an integer. method is optional. To get a list of methods use !methods')
    xs.addHelp('top','Usage: topX [method]. X should be an integer. method is optional. To get a list of methods use !methods')
    es.addons.registerSayFilter(xs_filter)
    
def unload():
    es.addons.unregisterSayFilter(xs_filter)
    
def cmd_rank(userid,args):
    steamid = es.getplayersteamid(userid)
    if len(args) == 1:
        method = args[0].lower()
    else:
        player = xs.data[steamid]
        method = xs.default_method if not player['settings']['method'] else player['settings']['method']
    es.tell(userid,'You are ranked %s of %s with %s points (%s)' % (xs.getRank(steamid,method),len(xs.data)-1,xs.getScore(steamid,method),method))
    
def cmd_statsme(userid,args):
    steamid = es.getplayersteamid(userid)
    top = None
    low = None
    tr = 0
    ts = 0
    for method in xs.methods:
        r,s = xs.getRank(steamid,method), xs.getScore(steamid,method)
        tr += r
        ts += s
        if not top or r > top:
            top = (r,s,method)
        if not low or r < low:
            low = (r,s,method)
    dr, ds = xs.getRank(steamid,xs.default_method), xs.getScore(steamid,xs.default_method)
    player = xs.data[steamid]
    pr, ps = None, None
    if player['settings']['method'] in xs.methods.keys():
        pr = xs.getRank(steamid,player['settings']['method'])
        ps = xs.getScore(steamid,player['settings']['method'])
    lines = ['Your Stats']
    lines.append('Rank (default method): %s (%s)' % (dr,ds))
    if pr:
        lines.append('Rank (personal method): %s (%s)' % (pr,ps))
    lines.append('Top rank: %s (%s) using %s' % (top))
    lines.append('Low rank: %s (%s) using %s' % (low))
    statshim = popuplib.easylist('statshim',lines)
    statshim.send(userid)
    
def cmd_methods(userid,args):
    es.tell(userid,'Available methods:')
    methodslist = ['Methods available:']
    methodslist += xs.methods.keys()
    methods = popuplist.easylist('methods_list',)
    methods.send(userid)
    
def cmd_settings(userid,args):
    settingsmenu = popuplib.easymenu('settings_menu','_popup_choice',settingsCallback)
    settingsmenu.settitle('Your eXtended Stats settings: Main')
    settingsmenu.addoption('method','Choose your personal method')
    settingsmenu.addoption('name','Choose your preferred name')
    settingsmenu.send(userid)
    
def settingsCallback(userid,choice,name):
    player = xs.getPlayer(es.getplayersteamid(userid))
    if choice == 'method':
        methodmenu = popuplib.easymenu('methods_menu','_popup_choice',settingsCallback2)
        methodmenu.settitle('Your eXtended Stats settings: Method')
        for method in xs.methods.keys():
            if method == player['settings']['method']:
                methodmenu.addoption(('method',method),'-> %s' % method)
            else:
                methodmenu.addoption(('method',method),method)
        methodmenu.addoption(2,'Reset setting')
        methodmenu.addoption(1,'Back to Main')
        methodmenu.send(userid)
    elif choice == 'name':
        namemenu = popuplib.easymenu('name_menu','_popup_choice',settingsCallback2)
        namemenu.settitle('Your eXtended Stats settings: Name')
        for name in player['names']:
            if name == player['settings']['name']:
                namemenu.addoption(('name',name),'-> %s' % name)
            else:
                namemenu.addoption(('name',name),name)      
        namemenu.addoption(2,'Reset setting')          
        namemenu.addoption(1,'Back to main')
        namemenu.send(userid)
        
def settingsCallback2(userid,choice,name):
    playersettings = xs.data[es.getplayersteamid(userid)]['settings']
    if choice == 1:
        cmd_settings(userid,None)
    elif choice == 2:
        if name == 'methods_menu':
            playersettings['method'] = None
        elif name == 'name_menu':
            playersettings['name'] = None            
    else:
        playersettings[choice[0]] = choice[1]
        es.tell(userid,'Your eXtended Stats settings have been changed successfully.')
    
def displayTop(userid,x,method):
    topplayers = xs.getToplist(x,method)
    displist = []
    i = 1
    for player in topplayers:
        displist.append('%s: %s (%s)' % (i,xs.getName(player[0]),player[1]))
        i += 1
    toplist = popuplib.easylist('top_list',displist)
    toplist.send(userid)

def xs_filter(userid, message, team):
    text = message.strip('"')
    tokens = text.split(' ')
    cmd = tokens[0][1:] if tokens[0].startswith('!') else tokens[0]
    if cmd.startswith('top') and len(tokens) < 3:
        displayTop(userid, int(cmd[3:]), tokens[1].lower() if len(tokens) == 2 else xs.default_method if not xs.getPlayer(es.getplayersteamid(userid))['settings']['method'] else xs.getPlayer(es.getplayersteamid(userid))['settings']['method'] )
    return (userid,text,team)
