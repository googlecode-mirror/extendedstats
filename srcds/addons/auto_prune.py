from extendedstats import extendedstats as xs

default = {
    'enabled': '0',
    'limit': '30d',
}

dcfg = xs.addonDynCfg('auto_prune',default)

def load():
    xs.loadEvents('auto_prune')