import time
import codecs
import sqlite3
import sys

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

def createSummaryForItem(id, days):
    bought = 0
    boughtCost = 0
    today = time.time()
    last = today - (days * 24 * 60 * 60)
    try:
        c.execute("SELECT quantity,typeName,typeID,price,transactionType FROM transactions WHERE typeID={0}".format(id)) #XXX add date filter
        rows = c.fetchall()
        for row in rows:
            if row[4] == 'buy':
                print row
            else:
                print row[4]
    except:
        print "Unexpected error:", sys.exc_info()[0], sys.exc_info()[1]
        print "Exception on createSummaryForItem select"

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
