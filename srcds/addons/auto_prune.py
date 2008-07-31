import time
from extendedstats import extendedstats as xs

dcfg = xs.addonDynCfg('auto_prune')

def load():
    if not dcfg['enable']:
        dcfg['enable'] = '0'
    if not dcfg['limit']:
        dcfg['limit'] = '30d'
    xs.registerEvent('auto_prune','es_map_start',prune)
    
def prune(ev):
    if dcfg['enable'] == '1':
        limit = parseLimit(dcfg['limit'])
        for player in xs.data:
            if not player == 'info':
                if time.time() - limit > xs.data[player]['lastseen']:
                    del xs.data[player]
        
def parseLimit(mytime):
    timeformat = mytime[-1]
    mytime = int(mytime[:-1]) * 86400
    if timeformat == 'd':
        return mytime
    mytime *= 7
    if timeformat == 'w':
        return mytime
    mytime *= 4
    if timeformat == 'm':
        return mytime
    mytime *= 12
    return mytime 
