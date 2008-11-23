# ExtendedEvents eXtended Stats Addon version 2.0 by Ojii
# Compatible with ExtendedEvents 4

from extendedstats import extendedstats
import es, vecmath, path

EE = extendedstats.addonIsLoaded('extendedevents')
if EE:
    columns = [
        ('jump_distance','REAL DEFAULT 0.0'),
        ('jump_longest','INTEGER DEFAULT 0'),
    ]
    if extendedstats.game == 'cstrike':
        columns += [('money','INTEGER DEFAULT 0')]
    wcolumns = None
    if extendedstats.game == 'dod':
        columns += [('dod_captures','INTEGER DEFAULT 0')]
    elif extendedstats.game == 'cstrike':
        wcolumns = map(lambda x: ('bought_%s' % x,'INTEGER DEFAULT 0'),extendedstats.cstrike_weapons)
        extendedstats.players.addColumns(wcolumns)
        extendedstats.weapons.addColumns([('bought','INTEGER DEFAULT 0')])
    extendedstats.players.addColumns(columns)
    
def load():
    if EE:
        extendedstats.loadEvents('extendedevents')
    else:
        extendedstats.dbg('XSEE: No extendedevents found')