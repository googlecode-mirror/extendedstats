# Default eXtended Stats new_player for version 0.0.5:97
from extendedstats import extendedstats # Import eXtended Stats
import es, time, popuplib

# This dict will be used to fill new players with default keys->values to prevent key not found errors.
new_player = {
    'bomb_defused': 0,
    'bomb_dropped': 0,
    'bomb_exploded': 0,
    'bomb_pickup': 0,
    'flashbang_detonate': 0,
    'hegrenade_detonate': 0,
    'hostage_follows': 0,
    'hostage_hurt': 0,
    # 'hostage_hurt_damage': 0, moved to EE4?
    'hostage_killed': 0,
    'hostage_rescued': 0,
    'hostage_stops_following': 0,
    'weapons_picked_up':{},
    'sessions': 0,
    'sessionstart': None,
    'time': 0,
    'changename': 0,
    'kills': 0,
    'kill_weapons': {},
    'deaths': 0,
    'death_weapons': {},
    'teamkills': 0,
    'teamkilled': 0,
    'headshots': 0,
    'lastseen': 0,
    'falldamage': 0.0,
    'hurt': 0,
    'attacked': 0,
    'hurt_damage': 0,
    'attacked_damage': 0,
    'jump': 0,
    'radio': 0,
    'team_1_time': 0,
    'team_2_time': 0,
    'team_3_time': 0,
    'teamchange_time': None,
    'current_team': '0',
    'win': 0,
    'lose': 0,
    'rounds': 0,
    'ban': 0,
    'smokegrenade_detonate': 0,
    'vip_escaped': 0,
    'vip_killed': 0,
    'vip_died': 0,
    'dod_sniper': 0,
    'dod_rifleman': 0,
    'dod_assault': 0,
    'dod_support': 0,
    'dod_rocket': 0,
    'dod_mg': 0,
    'dod_blocks': 0,
    'lastname': '',
    'names': {},
    'settings':{
        'method': None,
        'name': None,
    },
}

def load():
    extendedstats.registerLiveKey('time',liveTime)
    extendedstats.registerIgnoreKey('sessionstart')
    extendedstats.registerIgnoreKey('teamchange_time')
    extendedstats.registerIgnoreKey('current_team')
    extendedstats.registerLiveKey('team_2_time',liveTeam2)
    extendedstats.registerLiveKey('team_3_time',liveTeam3)
    extendedstats.registerLiveKey('team_1_time',liveSpec)
    extendedstats.registerCommand('rank','default_commands',cmd_rank,helplist=['Usage: !rank [method]','method is optional.','To get a list of methods use !methods'])
    extendedstats.registerCommand('statsme','default_commands',cmd_statsme,helplist=['Usage: !statsme [method]',' method is optional.','To get a list of methods use !methods'])
    extendedstats.registerCommand('methods','default_commands',cmd_methods,helplist=['Usage: !methods','Will show a list of available methods'])
    extendedstats.registerCommand('settings','default_commands',cmd_settings,helplist=['Usage: !settings','Will open a menu to change personal settings'])
    extendedstats.addHelp('topx','Usage: topX [method]. X should be an integer. method is optional. To get a list of methods use !methods')
    extendedstats.addHelp('top','Usage: topX [method]. X should be an integer. method is optional. To get a list of methods use !methods')
    es.addons.registerSayFilter(xs_filter)
    
def unload():
    es.addons.unregisterSayFilter(xs_filter)
    
def cmd_rank(userid,args):
    steamid = es.getplayersteamid(userid)
    if len(args) == 1:
        method = extendedstats.getMethod(args[0].lower())
    else:
        player = extendedstats.data[steamid]
        method = extendedstats.getMethod(player['settings']['method'])
    es.tell(userid,'You are ranked %s of %s with %s points (%s)' % (extendedstats.getRank(steamid,method),len(extendedstats.data)-1,extendedstats.getScore(steamid,method),method))
    
def cmd_statsme(userid,args):
    steamid = es.getplayersteamid(userid)
    top = None
    low = None
    tr = 0
    ts = 0
    for method in extendedstats.methods:
        r,s = extendedstats.getRank(steamid,method), extendedstats.getScore(steamid,method)
        tr += r
        ts += s
        if not top or r > top:
            top = (r,s,method)
        if not low or r < low:
            low = (r,s,method)
    dr, ds = extendedstats.getRank(steamid,extendedstats.getMethod()), extendedstats.getScore(steamid,extendedstats.getMethod())
    player = extendedstats.data[steamid]
    pr, ps = None, None
    if player['settings']['method'] in extendedstats.methods.keys():
        pr = extendedstats.getRank(steamid,player['settings']['method'])
        ps = extendedstats.getScore(steamid,player['settings']['method'])
    lines = ['Your Stats']
    lines.append('Rank (default method): %s (%s)' % (dr,ds))
    if pr:
        lines.append('Rank (personal method): %s (%s)' % (pr,ps))
    lines.append('Top rank: %s (%s) using %s' % (top))
    lines.append('Low rank: %s (%s) using %s' % (low))
    statshim = popuplib.easylist('statshim',lines)
    statshim.send(userid)
    
def cmd_methods(userid,args):
    methodslist = ['Methods available:']
    methodslist += extendedstats.methods.keys()
    methods = popuplib.easylist('methods_list',)
    for x in methodslist:
        methods.additem(x)
    methods.send(userid)
    
def cmd_settings(userid,args):
    settingsmenu = popuplib.easymenu('settings_menu','_popup_choice',settingsCallback)
    settingsmenu.settitle('Your eXtended Stats settings: Main')
    settingsmenu.addoption('method','Choose your personal method')
    settingsmenu.addoption('name','Choose your preferred name')
    settingsmenu.send(userid)
    
def settingsCallback(userid,choice,name):
    player = extendedstats.getPlayer(es.getplayersteamid(userid))
    if choice == 'method':
        methodmenu = popuplib.easymenu('methods_menu','_popup_choice',settingsCallback2)
        methodmenu.settitle('Your eXtended Stats settings: Method')
        for method in extendedstats.methods.keys():
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
    playersettings = extendedstats.data[es.getplayersteamid(userid)]['settings']
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
    topplayers = extendedstats.getToplist(x,method)
    displist = []
    i = 1
    for player in topplayers:
        displist.append('%s: %s (%s)' % (i,extendedstats.getName(player[0]),player[1]))
        i += 1
    toplist = popuplib.easylist('top_list')
    for x in displist:
        toplist.additem(displist)
    toplist.send(userid)

def xs_filter(userid, message, team):
    text = message.strip('"')
    tokens = text.split(' ')
    cmd = tokens[0][1:] if tokens[0].startswith('!') else tokens[0]
    if cmd.startswith('top') and len(tokens) < 3:
        method = tokens[1].lower() if len(tokens) == 2 and tokens[1].lower in extendedstats.methods else extendedstats.dcfg['default_method']
        method =  method if not extendedstats.getPlayer(es.getplayersteamid(userid))['settings']['method'] else extendedstats.getPlayer(es.getplayersteamid(userid))['settings']['method']
        displayTop(userid, int(''.join(filter(lambda x: x.isdigit(),cmd))), method)
    return (userid,text,team)
        
def liveTime(player):
    if not 'sessionstart' in extendedstats.data[player]:
        return extendedstats.data[player]['time']
    return extendedstats.data[player]['time'] + time.time() - extendedstats.data[player]['sessionstart']
    
def liveTeam2(player):
    if es.getplayerteam(es.getuserid(player)) != 2:
        return extendedstats.data[player]['team_2_time']
    if not extendedstats.data[player]['teamchange_time'] and not extendedstats.data[player]['sessionstart']:
        return extendedstats.data[player]['team_2_time']
    if not extendedstats.data[player]['teamchange_time']:
        return extendedstats.data[player]['team_2_time'] + time.time() - extendedstats.data[player]['sessionstart']
    return extendedstats.data[player]['team_2_time'] + time.time() - extendedstats.data[player]['teamchange_time']

def liveTeam3(player):
    if es.getplayerteam(es.getuserid(player)) != 3:
        return extendedstats.data[player]['team_3_time']
    if not extendedstats.data[player]['teamchange_time'] and not extendedstats.data[player]['sessionstart']:
        return extendedstats.data[player]['team_3_time']
    if not extendedstats.data[player]['teamchange_time']:
        return extendedstats.data[player]['team_3_time'] + time.time() - extendedstats.data[player]['sessionstart']
    return extendedstats.data[player]['team_3_time'] + time.time() - extendedstats.data[player]['teamchange_time']

def liveSpec(player):
    if es.getplayerteam(es.getuserid(player)) not in [0,1]:
        return extendedstats.data[player]['team_1_time']
    if not extendedstats.data[player]['teamchange_time'] and not extendedstats.data[player]['sessionstart']:
        return extendedstats.data[player]['team_1_time']
    if not extendedstats.data[player]['teamchange_time']:
        return extendedstats.data[player]['team_1_time'] + time.time() - extendedstats.data[player]['sessionstart']
    return extendedstats.data[player]['team_1_time'] + time.time() - extendedstats.data[player]['teamchange_time']
