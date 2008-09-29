# 1.6
import es,popuplib
from extendedstats import extendedstats as xs

weapons = xs.weapons
players = xs.players
scfg = xs.scfg
EE = xs.addonIsLoaded('extendedevents')

def load():
    xs.registerCommand(scfg.command_weaponstats_weaponstats,'weaponstats',cmd_weaponstats,True,True,helplist=['Detailed stats about weapons'])
    xs.registerCommand(scfg.command_weaponstats_myweaponstats,'weaponstats',cmd_myweaponstats,True,True,helplist=['Detailed stats about a players weapon usage'])
    pplchck('xs_ws_list')
    p = popuplib.easymenu('xs_ws_list','_popup_choice',weaponstats)
    pp = popuplib.easymenu('xs_ws_mylist','_popup_choice',myweaponstats)
    weapons.execute("SELECT weapon FROM xs_weapons ORDER BY weapon ASC")
    for weapon in weapons.fetchall():
        p.addoption(weapon,weapon)
        pp.addoption(weapon,weapon)
    
def cmd_weaponstats(userid,args):
    pplchck('xs_ws_%s' % userid)
    weapons.execute("SELECT weapon,kills FROM xs_weapons ORDER BY kills DESC LIMIT 1")
    top = weapons.fetchone()
    weapons.execute("SELECT weapon,damage FROM xs_weapons ORDER BY damage DESC LIMIT 1")
    pain = weapons.fetchone()
    weapons.execute("SELECT weapon,damage FROM xs_weapons ORDER BY damage ASC LIMIT 1")
    pacifist = weapons.fetchone()
    if EE:
        weapons.execute("SELECT weapon,bought FROM xs_weapons ORDER BY bought DESC LIMIT 1")
        exevents = weapons.fetchone()
    p = popuplib.easymenu('xs_ws_%s' % userid,'_popup_choice',weaponchoice)
    p.settitle('eXtended Stats - Weaponstats')
    p.addoption(top[0],'Most lethal weapon: %s with %s kills' % top)
    p.addoption(pain[0],'Most painful weapon: %s with %.1f damage done' % pain)
    p.addoption(pacifist[0],'Most pacifist weapon: %s with %.1f damage done' % pacifist)
    if EE:
        p.addoption(exevents[0],'Most popuplar weapon: %s, bought %s times' % exevents)
    p.addoption(1,'Full list of weapons')
    p.send(userid)
    
def weaponchoice(userid,choice,popupid):
    if choice == 1:
        popuplib.send('xs_ws_list',userid)
    else:
        weaponstats(userid,choice,None)

def weaponstats(userid,choice,popupid):
    pplchck('xs_ws_%s_%s' % (choice,userid))
    p = popuplib.easylist('xs_ws_%s_%s' % (choice,userid))
    p.settitle('Weaponstats - %s' % choice)
    weapons.execute("SELECT kills,damage%s FROM xs_weapons WHERE weapon='%s'" % (',bought' if EE else '',choice))
    row = weapons.fetchone()
    p.additem('Kills: %s' % row[0])
    p.additem('Damage: %s' % row[1])
    if EE:
        p.additem('Bought: %s' % row[2])
    p.send(userid)
    
def cmd_myweaponstats(userid,args):
    steamid = es.getplayersteamid(userid)
    pplchck('xs_ws_my%s' % userid)
    weapons.execute("SELECT weapon FROM xs_weapons")
    wwk = []
    wwd = []
    wwp = []
    if EE:
        wwe = []
    www = weapons.fetchall()
    for weapon in www:
        wwk.append('kill_%s' % weapon)
        wwd.append('death_%s' % weapon)
        wwp.append('damage_%s' % weapon)
        if EE:
            wwe.append('bought_%s' % weapon)
    wk = ','.join(wwk)
    wd = ','.join(wwd)
    wp = ','.join(wwp)
    if EE:
        we = ','.join(wwe)
    players.execute("SELECT %s FROM xs_main WHERE steamid='%s'" % (wk,steamid))
    kills = players.fetchone()
    top = map(lambda x: (wwk[x].split('_')[1],kills[x]),range(len(kills)))
    top.sort(reverse=True)
    top = top[0]
    players.execute("SELECT %s FROM xs_main WHERE steamid='%s'" % (wd,steamid))
    deaths = players.fetchone()
    fear = map(lambda x: (wwd[x].split('_')[1],deaths[x]),range(len(deaths)))
    fear.sort(reverse=True)
    fear = fear[0]
    players.execute("SELECT %s FROM xs_main WHERE steamid='%s'" % (wp,steamid))
    damage = players.fetchone()
    damage = map(lambda x: (wwp[x].split('_')[1],damage[x]),range(len(damage)))
    damage.sort(reverse=True)
    damage = damage[0]
    if EE:
        players.execute("SELECT %s FROM xs_main WHERE steamid='%s'" % (we,steamid))
        exevents = players.fetchone()
        exevents = map(lambda x: (wwe[x].split('_')[1],exevents[x]),range(len(exevents)))
        exevents.sort(reverse=True)
        exevents = exevents[0]
    p = popuplib.easymenu('xs_ws_my%s' % userid,'_popup_choice',myweaponchoice)
    p.settitle('eXtended Stats - Your Weaponstats')
    p.addoption(top[0],'Your most lethal weapon: %s with %s kills' % top)
    p.addoption(damage[0],'Your most damaging weapon: %s with %.1f damage done' % damage)
    p.addoption(fear[0],'Your most feared weapon: %s, killed you %s times' % fear)
    if EE:
        p.addoption(exevents[0],'Your favorite weapon: %s, bought %s times' % exevents)
    p.addoption(1,'Full list of weapons')
    p.send(userid)
    
def myweaponchoice(userid,choice,popupid):
    if choice == 1:
        popuplib.send('xs_ws_mylist',userid)
    else:
        myweaponstats(userid,choice,None)
        
def myweaponstats(userid,choice,popupid):
    pplchck('xs_ws_my%s_%s' % (choice,userid))
    steamid = es.getplayersteamid(userid)
    p = popuplib.easylist('xs_ws_my%s_%s' % (choice,userid))
    p.settitle('Weaponstats - My %s' % choice)
    weapons.execute("SELECT kill_%s,death_%s,damage_%s%s FROM xs_main WHERE steamid='%s'" % (choice,choice,choice,(',bought_%s' % choice) if EE else '',steamid))
    row = weapons.fetchone()
    p.additem('Kills: %s' % row[0])
    p.additem('Killed: %s' % row[1])
    p.additem('Damage: %s' % row[2])
    if EE:
        p.additem('Bought: %s' % row[3])
    p.send(userid)

def pplchck(name):
    if popuplib.exists(name):
        popuplib.delete(name)