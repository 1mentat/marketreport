import sqlite3
import sys
import settings

conn = None
c = None

def setupdb() :
    global conn
    global c

    conn = sqlite3.connect('asset.db')

    c = conn.cursor()

    try:
        c.execute('''create table if not exists assets (locationID integer, \
                                                            typeID integer, \
                                                            quantity integer)''')
        conn.commit()
    except:
        print "Unexpected error:", sys.exc_info()[0], sys.exc_info()[1]
        print "Exception on create assets"

def addasset(locationID, typeID, quantity):
    try:
        c.execute("insert or ignore into assets values (?, ?, ?)", (locationID, typeID, quantity))
        conn.commit()
    except:
        print "Unexpected error:", sys.exc_info()[0], sys.exc_info()[1]
        print "Exception on asset insert"

def assetsByTypeID(typeID):
    assets = []
    try:
        c.execute("SELECT * FROM assets WHERE typeID={0}".format(typeID))
        rows = c.fetchall()
        for row in rows:
            assets.append(row)
    except:
        print "Unexpected error:", sys.exc_info()[0], sys.exc_info()[1]
        print "Exception on assetsByTypeID"

    return assets

def stockByTypeID(typeID):
    stock = 0
    try:
        c.execute("SELECT quantity FROM assets WHERE typeID={0}".format(typeID))
        rows = c.fetchall()
        for row in rows:
            stock += row[0]
    except:
        print "Unexpected error:", sys.exc_info()[0], sys.exc_info()[1]
        print "Exception on stockByTypeID"

    return stock
