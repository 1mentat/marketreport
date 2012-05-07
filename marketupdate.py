from calendar import timegm
from datetime import datetime
from datetime import timedelta
import imp, argparse
import settings
import time
import marketdb
eveapi = imp.load_source('eveapi', '../eveapi/eveapi.py')

if __name__ == '__main__':
    marketdb.setupdb()
    parser = argparse.ArgumentParser(description='Options')
    parser.add_argument('-n', '--name', dest='name', default=settings.name)
    args = parser.parse_args()

    api = eveapi.EVEAPIConnection()
    auth = api.auth(keyID=settings.keyID, vCode=settings.vCode)

    result = auth.account.Characters()

    for character in result.characters:
        if character.name==args.name:
            wtrans = auth.char.WalletTransactions(characterID=character.characterID, rowCount=2560)

            now = datetime.utcnow()
            today = datetime(now.year,now.month,now.day,23,59,59)
            todaysec = timegm(today.utctimetuple())
            last = today - timedelta(settings.valuePeriod)
            oldest = todaysec
            oldestID = 0

            for row in wtrans.transactions:
                if row.transactionDateTime < oldest:
                    oldest = row.transactionDateTime
                    oldestID = row.transactionID

                marketdb.addtransaction(row.transactionDateTime,row.transactionID,row.quantity,row.typeName,row.typeID,row.price,row.clientID,row.clientName,row.stationID,row.stationName,row.transactionType,row.transactionFor)

            if oldest > timegm(last.utctimetuple()):
                print 'Need more transactions'
                wtrans = auth.char.WalletTransactions(characterID=character.characterID, rowCount=2560, fromID=oldestID)

                for row in wtrans.transactions:
                    if row.transactionDateTime < oldest:
                        oldest = row.transactionDateTime
                        oldestID = row.transactionID

                    marketdb.addtransaction(row.transactionDateTime,row.transactionID,row.quantity,row.typeName,row.typeID,row.price,row.clientID,row.clientName,row.stationID,row.stationName,row.transactionType,row.transactionFor)

                if oldest > timegm(last.utctimetuple()):
                    print 'Still need more transactions, to be fixed'

