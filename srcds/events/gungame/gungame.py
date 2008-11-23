import es
from extendedstats import extendedstats as xs

def load():
    xs.dbg('XS: loading gungame events...')

def gg_levelup(ev):
    if not es.isbot(ev['userid']):
        xs.players.add(ev['steamid'],'gg_level',int(ev['old_level']) - int(ev['new_level']))

def gg_leveldown(ev):
    if not es.isbot(ev['userid']):
        xs.players.add(ev['steamid'],'gg_level',int(ev['old_level']) - int(ev['new_level']))    

def gg_win(ev):
    if not es.isbot(ev['userid']):
        xs.players.increment(ev['steamid'],'gg_win')