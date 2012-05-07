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
        c.execute('''create table if not exists stocks (typeID integer, count integer, value integer, unique(typeID))''')
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
        conn.commit()
    except:
        print "Unexpected error:", sys.exc_info()[0], sys.exc_info()[1]
        print "Exception on dropping daytemp"

def itemValueOverPeriod(days, typeID):
    bought = 0
    boughtCost = 0
    sold = 0
    soldCost = 0
    averageValue = 0

    now = datetime.utcnow()
    today = datetime(now.year,now.month,now.day,23,59,59)
    day = timedelta(1)
    last = today - (days * day)
    try:
        c.execute("SELECT quantity,price,transactionType FROM transactions WHERE typeID={2} AND transactionDateTime <= {0} AND transactionDateTime > {1}".format(timegm(today.utctimetuple()), timegm(last.utctimetuple()), typeID))

        rows = c.fetchall()
        for row in rows:
            if row[2] == 'buy':
                bought += row[0]
                boughtCost += (row[0] * row[1])
            elif row[2] == 'sell':
                sold += row[0]
                soldCost += (row[0] * row[1])

        if rows:
            if (sold and bought):
                averageValue = ((soldCost / sold) + (boughtCost / bought)) / 2
            elif sold:
                averageValue = (soldCost / sold)
            elif bought:
                averageValue = (boughtCost / bought)

        return averageValue

    except:
        print "Unexpected error:", sys.exc_info()[0], sys.exc_info()[1]
        print "Exception on itemValueOverPeriod"

