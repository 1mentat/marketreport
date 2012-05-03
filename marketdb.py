from calendar import timegm
from datetime import datetime
from datetime import timedelta
import codecs
import sqlite3
import sys
import settings

conn = None
c = None

def setupdb() :
    global conn
    global c

    conn = sqlite3.connect('market.db')

    c = conn.cursor()

    try:
        c.execute('''create table if not exists transactions (transactionDateTime integer, \
                                                            transactionID integer, \
                                                            quantity integer, \
                                                            typeName varchar, \
                                                            typeID integer, \
                                                            price integer, \
                                                            clientID integer, \
                                                            clientName varchar, \
                                                            stationID integer, \
                                                            stationName varchar, \
                                                            transactionType varchar, \
                                                            transactionFor varchar, \
                                                            unique(transactionID))''')
        c.execute('''create table if not exists summary (typeID integer, dmy integer, bought integer, boughtCost integer, sold integer, soldCost integer, unique(typeID, dmy))''')
        conn.commit()
    except:
        print "Unexpected error:", sys.exc_info()[0], sys.exc_info()[1]
        print "Exception on create lastupdate"

def addtransaction(transactionDateTime,transactionID,quantity,typeName,typeID,price,clientID,clientName,stationID,stationName,transactionType,transactionFor):
    try:
        c.execute("insert or ignore into transactions values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (transactionDateTime, transactionID, quantity, typeName, typeID, price, clientID, clientName, stationID, stationName, transactionType, transactionFor))
        conn.commit()
    except:
        print "Unexpected error:", sys.exc_info()[0], sys.exc_info()[1]
        print "Exception on link insert"

def createSummaryForItemDay(id, day, daybefore):
    bought = 0
    boughtCost = 0
    sold = 0
    soldCost = 0
    try:
        c.execute("SELECT quantity,typeName,typeID,price,transactionType FROM transactions WHERE typeID={0} AND transactionDateTime <= {1} AND transactionDateTime > {2}".format(id, timegm(day.utctimetuple()), timegm(daybefore.utctimetuple())))
        rows = c.fetchall()
        for row in rows:
            if row[4] == 'buy':
                bought += row[0]
                boughtCost += row[0] * row[3]
            else:
                sold += row[0]
                soldCost += row[0] * row[3]

        if rows:
            print 'For {0}'.format(day)
            if bought:
                print 'Bought {0} of {1} for a total cost of {2}'.format(bought, rows[0][1], boughtCost)
            if sold:
                print 'Sold {0} of {1} for a total revenue of {2}'.format(sold, rows[0][1], soldCost)

        #c.execute('''create table if not exists summary (typeID integer, dmy integer, bought integer, boughtCost integer, sold integer, soldCost integer, unique(typeID, dmy))''')
    except:
        print "Unexpected error:", sys.exc_info()[0], sys.exc_info()[1]
        print "Exception on createSummaryForItem select"

def createSummaryForItem(id, days):
    now = datetime.utcnow()
    today = datetime(now.year,now.month,now.day,23,59,59)
    day = timedelta(1)
    yesterday = today - day
    last = today - (days * day)

    while yesterday >= last:
        createSummaryForItemDay(id, today, yesterday)
        today = yesterday
        yesterday = today - day

def createSummaryForItems(days):
    now = datetime.utcnow()
    today = datetime(now.year,now.month,now.day,23,59,59)
    day = timedelta(1)
    yesterday = today - day
    last = today - (days * day)

    while yesterday >= last:
        createSummaryFromDay(today, yesterday)
        today = yesterday
        yesterday = today - day

def itemIDList():
    items = set()
    try:
        c.execute("SELECT DISTINCT typeID FROM transactions")
        rows = c.fetchall()
        for row in rows:
            items.add(row[0])
    except:
        print "Unexpected error:", sys.exc_info()[0], sys.exc_info()[1]
        print "Exception on createSummaryForItem select"
    
    return items

def createSummaryFromDay(day, daybefore):
    try:
        c.execute("CREATE TABLE daytemp AS SELECT quantity,typeName,typeID,price,transactionType FROM transactions WHERE transactionDateTime <= {1} AND transactionDateTime > {2}".format(id, timegm(day.utctimetuple()), timegm(daybefore.utctimetuple())))
    except:
        print "Unexpected error:", sys.exc_info()[0], sys.exc_info()[1]
        print "Exception on createDay"
        return

    dmy = day.strftime("%Y%m%d")
    items = set()

    try:
        c.execute("SELECT DISTINCT typeID FROM daytemp")
        rows = c.fetchall()
        for row in rows:
            items.add(row[0])
    except:
        print "Unexpected error:", sys.exc_info()[0], sys.exc_info()[1]
        print "Exception on distinct items for daytemp select"

    for filtered in settings.excluded_items:
        try:
            items.remove(filtered)
        except KeyError:
            pass
    
    for item in items:
        bought = 0
        boughtCost =0
        sold = 0
        soldCost = 0
        try:
            c.execute("SELECT quantity,typeName,typeID,price,transactionType FROM daytemp WHERE typeID={0}".format(item))
            rows = c.fetchall()
            for row in rows:
                if row[4] == 'buy':
                    bought += row[0]
                    boughtCost += row[0] * row[3]
                else:
                    sold += row[0]
                    soldCost += row[0] * row[3]

            if rows:
                #print 'For {0}'.format(day)
                #if bought:
                #    print 'Bought {0} of \"{1}\" for a total cost of {2}'.format(bought, rows[0][1], boughtCost)
                #if sold:
                #    print 'Sold {0} of \"{1}\" for a total revenue of {2}'.format(sold, rows[0][1], soldCost)

                try:
                    c.execute('''INSERT or REPLACE INTO summary values (?, ?, ?, ?, ?, ?)''',(item, dmy, bought, boughtCost, sold, soldCost))
                    conn.commit()
                except:
                    print "Unexpected error:", sys.exc_info()[0], sys.exc_info()[1]
                    print "Exception on summary insert"

        except:
            print "Unexpected error:", sys.exc_info()[0], sys.exc_info()[1]
            print "Exception on price processing on daytemp select"

    try:
        c.execute("DROP TABLE daytemp")
    except:
        print "Unexpected error:", sys.exc_info()[0], sys.exc_info()[1]
        print "Exception on dropping daytemp"

