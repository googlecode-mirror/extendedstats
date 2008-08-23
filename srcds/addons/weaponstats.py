import es,popuplib
from extendedstats import extendedstats as xs

weapons = xs.weapons
scfg = xs.scfg
EE = xs.addonIsLoaded('extendedevents')

def load():
    xs.registerCommand(scfg.command_weaponstats_weaponstats,'weaponstats',cmd_weaponstats,True,True,helplist=['Detailed stats about wewapons'])
    
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
    p = popuplib.easylist('xs_ws_%s' % userid)
    p.settitle('eXtended Stats - Weaponstats')
    p.additem('Most lethal weapon: %s with %s kills' % top)
    p.additem('Most painful weapon: %s with %.1f damage done' % pain)
    p.additem('Most pacifist weapon: %s with %.1f damage done' % pacifist)
    if EE:
        p.additem('Most popuplar weapon: %s, bought %s times' % exevents)
    p.send(userid)

def pplchck(name):
    if popuplib.exists(name):
        popuplib.delete(name)