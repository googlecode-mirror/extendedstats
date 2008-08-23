import es,popuplib
from extendedstats import extendedstats as xs

weapons = xs.weapons
scfg = xs.scfg
EE = xs.addonIsLoaded('extendedevents')

def load():
    xs.registerCommand(scfg.command_weaponstats_weaponstats,'weaponstats',cmd_weaponstats,True,True,helplist=['Detailed stats about wewapons'])
    pplchck('xs_ws_list')
    p = popuplib.easymenu('xs_ws_list','_popup_choice',weaponstats)
    weapons.execute("SELECT weapon FROM xs_weapons ORDER BY weapon ASC")
    for weapon in weapons.fetchall():
        p.addoption(weapon,weapon)
    
def cmd_weaponstats(userid,args):
    es.cexec(userid,'slot10')
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
    p = popuplib.popup('xs_ws_%s' % userid,'_popup_choice',weaponchoice)
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
    p.addline('Kills: %s' % row[0])
    p.addline('Damage: %s' % row[1])
    if EE:
        p.addline('Bought: %s' % row[2])
    p.send(userid)

def pplchck(name):
    if popuplib.exists(name):
        popuplib.delete(name)