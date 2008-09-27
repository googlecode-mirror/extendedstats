import sqlite3,path

xspath = path.path('/home/jonas/xstest/')

class Database(object):
    def __init__(self):
        self.con = sqlite3.connect(xspath.joinpath('database.sqlite'))
        self.con.text_factory = str
        self.cur = self.con.cursor()
        
    def newTable(self,tablename,columns,primarykey):
        table = Table(self.con,self.cur,tablename,columns,primarykey)
        return table
    
class Table(object):
    def __init__(self,con,cur,tablename,columns,primarykey):
        self.con = con
        self.cur = cur
        self.table = tablename
        coldef = ', '.join(map(lambda x: '%s %s' % x,columns))
        self.execute("CREATE TABLE xs_%s (%s)" % (self.table,coldef))
        self.columns = map(lambda x: x[0],columns)
        self.pk = primarykey
        self._numericColumns = filter(lambda x: self._numericColumn(x),self.columns)
        
    def _getColumns(self):
        return map(lambda x: x[1], self.con.execute('PRAGMA table_info(xs_%s)' % (self.table)).fetchall())
    
    def __iter__(self):
        self.execute("SELECT %s FROM xs_%s" % (self.pk,self.table))
        return iter(self.fetchall())
    
    def _numericColumn(self,key):
        self.execute('PRAGMA table_info(xs_%s)' % self.table)
        all = self.fetchall()
        column = filter(lambda x: x[1] == key,all)[0]
        return column[2] in ('INTEGER','REAL')
        
    def addColumns(self,columns):
        allcolumns = self._getColumns()
        for column in filter(lambda x: x[0] not in allcolumns,columns):
            self.execute("ALTER TABLE xs_%s ADD COLUMN %s %s" % (self.table,column[0],column[1]),1,True)
        self.columns += map(lambda x: x[0],columns)
        self._numericColumns = filter(lambda x: self.numericColumn(x),self.columns)
        
    def dropColumns(self):
        oldcolumns = filter(lambda x: x not in self.columns,self._getColumns())
        if not oldcolumns:
            return 0
        self.cur.execute("PRAGMA table_info(xs_%s)" % self.table)
        colnames = []
        coldef = []
        for row in self.cur.fetchall():
            if row[1] in oldcolumns:
                continue
            colnames.append(row[1])
            coldef.append('%s %s %s' % (row[1],row[2],'DEFAULT %s' % row[4] if not int(row[5]) == 1 else 'PRIMARY KEY'))
        coldef =  ', '.join(coldef)
        self.cur.execute("SELECT %s FROM xs_%s" % (', '.join(colnames),self.table),2)
        queries = []
        for row in self.cur.fetchall():
            values = []
            for val in row:
                if type(val) in (float,int):
                    values.append(str(val))
                elif not val:
                    values.append('NULL')
                else:
                    values.append("'%s'" % val)
            queries.append("INSERT INTO xs_%s (%s) VALUES (%s)" % (self.table,', '.join(colnames),', '.join(values)),1)
        self.cur.execute("DROP TABLE xs_%s" % self.table,1)
        self.cur.execute("CREATE TABLE xs_%s (%s)" % (self.table,coldef),1)
        for query in queries:
            self.cur.execute(query)
        self.columns = self._getColumns()
        return len(oldcolumns)
        
    def execute(self,sql):
        self.cur.execute(sql)
            
    def fetchall(self):
        trueValues = []
        for value in self.cur.fetchall():
            if len(value) > 1:
                trueValues.append(value)
            else:
                trueValues.append(value[0])
        return trueValues
       
    def fetchone(self):
        one = self.cur.fetchone()
        if len(one) == 1:
            return one[0]
        return one
    
    def __contains__(self,steamid):
        self.execute("SELECT * FROM xs_%s WHERE %s='%s'" % (self.table,self.pk,steamid))
        return bool(self.cur.fetchone()) 
    
    def query(self,steamid,key):
        self.execute("SELECT %s FROM xs_%s WHERE %s='%s'" % (key,self.table,self.pk,steamid))
        return self.fetchone()
        
    def convert(self,key,value):
        if key in self._numericColumns:
            return value
        return "'%s'" % value
        
    def update(self,steamid,key,newvalue):
        query = "UPDATE xs_%s SET %s=%s WHERE %s='%s'" % (self.table,key,self.convert(key,newvalue),self.pk,steamid)
        self.execute(query)
        
    def increment(self,steamid,key):
        old = self.query(steamid,key)
        if not old:
            old = 0
        self.execute("UPDATE xs_%s SET %s=%s WHERE %s='%s'" % (self.table,key,old + 1,self.pk,steamid))
        
    def add(self,steamid,key,amount):
        current = self.query(steamid,key)
        newamount = current + amount
        self.execute("UPDATE xs_%s SET %s=%s WHERE %s='%s'" % (self.table,key,newamount,self.pk,steamid))
        
    def name(self,steamid,newname):
        self.execute("SELECT name1,name2,name3,name4,name5 FROM xs_%s WHERE %s='%s'" % (self.table,self.pk,steamid))
        cnames = self.fetchone()
        if not cnames:
            self.update(steamid,'name1',newname)
        else:
            if not type(cnames) == tuple:
                cnames = [cnames]
            if newname in cnames:
                nnames = [newname]
                for cname in cnames:
                    if cname == newname:
                        continue
                    nnames.append(cname)
                    if len(nnames) == 5:
                        break
            else:
                nnames = [newname]
                for cname in cnames:
                    nnames.append(cname)
                    if len(nnames) == 5:
                        break
            for x in range(len(nnames)):
                self.update(steamid,'name%s' % (x + 1),nnames[x])
        self.increment(steamid,'changename') 

    def newplayer(self,steamid):
        self.execute("INSERT INTO xs_%s (%s) VALUES ('%s')" % (self.table,self.pk,steamid))
        
    def commit(self):
        self.con.commit()
