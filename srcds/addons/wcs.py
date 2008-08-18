# WCS eXtended Stats addon version 1.0 by Ojii

import path, es
from extendedstats import extendedstats as xs
wcsIsLoaded = xs.addonIsLoaded('wcs')
if wcsIsLoaded:
    columns = [
        ('wcs_ultimates_used','INTEGER DEFAULT 0'),
        ('wcs_abilities_used','INTEGER DEFAULT 0'),
    ]

def load():
    if wcsIsLoaded:
        xs.registerEvent('wcs','player_ultimate_on',player_ultimate_on)
        xs.registerEvent('wcs','player_ability_on',player_ability_on)
        xs.registerEvent('wcs','player_ability_on2',player_ability_on)

def player_ultimate_on(ev):
    steamid = xs.sid(ev)
    xs.players.increment(steamid,'wcs_ultimats_used')

def player_ability_on(ev):
    steamid = xs.sid(ev)
    xs.players.increment(steamid,'wcs_abilities_used')
