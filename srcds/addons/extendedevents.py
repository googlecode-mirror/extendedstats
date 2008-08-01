# ExtendedEvents eXtended Stats Addon version 1.5 by Ojii
# Compatible with ExtendedEvents 4

from extendedstats import extendedstats
import es, vecmath, path

EEP = path.path(es.getAddonPath('extendedevents'))
EE = EEP.isdir()
if EE:
    new_player = {
        'money': 0,
        'jump_distance': 0,
        'jump_longest': 0,
        'jump_startpos': None,
        'dod_captures': 0,   
        'weapon_bought':{},
    }
    dcfg = extendedstats.addonDynCfg('extendedevents')
    if not dcfg['notify_longestjump']:
        dcfg['notify_longestjump'] =  1
    if not dcfg['notify_longestjump_all']:
        dcfg['notify_longestjump_all'] = 0

def load():
    if EE:
        extendedstats.dbg( 'XS:EE: Registering extendedevents events')
        extendedstats.registerEvent('extendedevents','player_land',player_land)
        extendedstats.registerEvent('extendedevents','player_money',player_money)
        extendedstats.registerEvent('extendedevents','weapon_purchase',weapon_purchase)
        extendedstats.registerIgnoreKey('jump_startpos')
    else:
        extendedstats.dbg( 'XS:EE: No extendedevents files found')

def player_land(ev):
    if not es.isbot(ev['userid']):
        data = extendedstats.data
        steamid = extendedstats.sid(ev)
        extendedstats.dbg('player land')
        pos = vecmath.vector(es.getplayerlocation(ev['userid']))
        if data[steamid]['jump_startpos']:
            distance = vecmath.distance(pos, data[steamid]['jump_startpos'])
            data[steamid]['jump_distance'] += distance
            if distance > data[steamid]['jump_longest']:
                data[steamid]['jump_longest'] = distance
                if dcfg['notify_longestjump'] == '1':
                    name = extendedstats.getName(steamid)
                    rank = extendedstats.getRank(steamid,'longestjump')
                    rSteamid, rDistance = extendedstats.getToplist(1,'longestjump')[0]
                    rName = extendedstats.getName(rSteamid)
                    if dcfg['notify_longestjump_all'] == '1':
                        es.msg('%s just broke his record of his longest jump. His new record is: %.2f meters!' % (name,distance*0.01905))
                        es.msg('He is ranked %s of %s now. Longest jump overall is %.2f meters by %s' % (rank,len(data)-1,rDistance*0.01905,rName))
                    else:
                        es.tell(ev['userid'],'You just broke your record of your longest jump! Your new record is: %.2f meters!' % (name,distance*0.01905))
                        es.tell(ev['userid'],'You are now ranked %s of %s. Longest jump overall is %.2f meters by %s' % (rank,len(data)-1,rDistance*0.01905,rName))

def player_money(ev):
    if not es.isbot(ev['userid']):
        extendedstats.dbg( 'player money')
        extendedstats.data[extendedstats.sid(ev)]['money'] += int(ev['change_amount'])
        
def weapon_purchase(ev):
    if not es.isbot(ev['userid']):
        extendedstats.dbg( 'weapon purchase')
        steamid = extendedstats.sid(ev)
        weapon = ev['weapon']
        if extendedstats.data[steamid]['weapon_bought'].has_key(weapon):
            extendedstats.data[steamid]['weapon_bought'][weapon] += 1
        else:
            extendedstats.data[steamid]['weapon_bought'][weapon] = 1
