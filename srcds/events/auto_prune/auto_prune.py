from extendedstats import extendedstats as xs
import time

dcfg = xs.dcfg

def es_map_start(ev):
    if dcfg['enabled'] == '1':
        limit = parseLimit(dcfg['limit'])
        xs.players.execute("SELECT steamid FROM xs_main WHERE lastseen<%s" % limit)
        steamids = xs.players.fetchall()
        for table in xs.tables:
            xs.tables[table].execute("DELETE FROM xs_%s WHERE " % (table,' OR '.join(map(lambda x: "steamid='%s'" % x,steamids))))
        
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