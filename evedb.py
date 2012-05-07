import sqlite3
import sys

conn = None
c = None

def setupdb() :
    global conn
    global c

    conn = sqlite3.connect('eve.db')

    c = conn.cursor()

def getTypeIDfromTypeName(typeName):
    try:
        c.execute("SELECT typeID from invTypes where typeName=\"{0}\"".format(typeName))
        rows = c.fetchall()
        if rows:
            for row in rows:
                return row[0]
        else:
            return -1
    except:
        print "Unexpected error:", sys.exc_info()[0], sys.exc_info()[1]
        print "Exception on tidftn"

def getTypeNamefromTypeID(typeID):
    try:
        c.execute("SELECT typeName from invTypes where typeID={0}".format(typeID))
        rows = c.fetchall()
        if rows:
            for row in rows:
                return row[0]
        else:
            return ""
    except:
        print "Unexpected error:", sys.exc_info()[0], sys.exc_info()[1]
        print "Exception on tnftid"
