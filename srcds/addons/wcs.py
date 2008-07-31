# WCS eXtended Stats addon version 1.0 by Ojii

import path, es
from extendedstats import extendedstats as xs
wcsp = path.path(es.getAddonPath('wcs'))
if wcsp.isdir():
    wcs = __import__('wcs.wcs',fromlist=['wcs'],level=0)
    new_player = {
        'wcs_level': 0,
        'wcs_totalxp': 0,
        'wcs_racexp': {},
        'wcs_currentrace': {},
        'wcs_racelevel': {},
        'wcs_ultimates_used': 0,
        'wcs_abilities_used': 0,
    }

def load():
    if wcsp.isdir():
        xs.registerLiveKey('wcs_level',wcs_level)
        xs.registerLiveKey('wcs_totalxp',wcs_totalxp)
        xs.registerLiveKey('wcs_racexp',wcs_racexp)
        xs.registerLiveKey('wcs_currentrace',wcs_currentrace)
        xs.registerLiveKey('wcs_racelevel',wcs_racelevel)
        xs.registerEvent('wcs','player_ultimate_on',player_ultimate_on)
        xs.registerEvent('wcs','player_ability_on',player_ability_on)
        xs.registerEvent('wcs','player_ability_on2',player_ability_on)
        
def wcs_level(steamid):
    if steamid in wcs._dict_WCSPlayers and 'level' in wcs._dict_WCSPlayers[steamid]:
        return wcs._dict_WCSPlayers[steamid]['level']
    return 0

def wcs_totalxp(steamid):
    xp = 0
    if steamid not in wcs._dict_WCSPlayers:
        return xp
    wcsplayer = wcs._dict_WCSPlayers[steamid]
    for race in wcs._dict_races:
        if race in wcsplayer:
            xp += wcsplayer[race]['xp']
    return xp

def wcs_racexp(steamid):
    if steamid not in wcs._dict_WCSPlayers:
        return 0
    wcsplayer = wcs._dict_WCSPlayers[steamid]
    racexp = {}
    for race in wcs._dict_races:
        if race in wcsplayer:
            racexp[race] = wcsplayer[race]['xp']
    return racexp

def wcs_currentrace(steamid):
    if steamid not in wcs._dict_WCSPlayers:
        return None
    if 'race' not in wcs._dict_WCSPlayers[steamid]:
        return None
    return wcs._dict_WCSPlayers[steamid]['race']

def wcs_racelevel(steamid):
    race = wcs_currentrace(steamid)
    if not race:
        return 0
    else:
        return wcs._dict_WCSPlayers[steamid][race]['level']

def player_ultimate_on(ev):
    steamid = xs.sid(ev)
    xs.data[steamid]['wcs_ultimats_used'] += 1

def player_ability_on(ev):
    steamid = xs.sid(ev)
    xs.data[steamid]['wcs_abilities_used'] += 1
