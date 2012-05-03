import imp, argparse
import settings
import time
import marketdb
eveapi = imp.load_source('eveapi', '../eveapi/eveapi.py')

market_transaction = 2
brokers_fee = 46
transaction_tax = 54

def taxcheck(character, auth):
    walletjournal = auth.char.WalletJournal(characterID=character.characterID)
    transactionsByRefTypeID = walletjournal.transactions.GroupedBy('refTypeID')
    transactionsByDate = walletjournal.transactions.GroupedBy('date')

    for transaction in transactionsByRefTypeID[market_transaction]:
        sourceid = transaction.refID
        print 'Finding transaction correlated to {0} for {1}'.format(sourceid, transaction.amount)
        sourcedate = transaction.date
        samedate = transactionsByDate[sourcedate]
        for trans in samedate:
            if trans.refTypeID == brokers_fee:
                if trans.refID not in matched_broker:
                    matched_broker.add(trans.refID)
                else:
                    print '{0} already matched!'.format(trans.refID)
                print 'Paid broker {0}'.format(trans.amount)
            elif trans.refTypeID == transaction_tax:
                print 'Paid transaction tax {0}'.format(trans.amount)

    for transaction in transactionsByRefTypeID[brokers_fee]:
        if transaction.refID not in matched_broker:
            print 'Unmatched broker fee {0} for {1}'.format(transaction.refID,transaction.amount)
            print transaction

if __name__ == '__main__':
    marketdb.setupdb()
    matched_broker = set()
    parser = argparse.ArgumentParser(description='Options')
    parser.add_argument('-n', '--name', dest='name', default=settings.name)
    args = parser.parse_args()

    api = eveapi.EVEAPIConnection()
    auth = api.auth(keyID=settings.keyID, vCode=settings.vCode)

    result = auth.account.Characters()

    for character in result.characters:
        if character.name==args.name:

            #taxcheck(character,auth)

            wtrans = auth.char.WalletTransactions(characterID=character.characterID)

            for row in wtrans.transactions:
                marketdb.addtransaction(row.transactionDateTime,row.transactionID,row.quantity,row.typeName,row.typeID,row.price,row.clientID,row.clientName,row.stationID,row.stationName,row.transactionType,row.transactionFor)

            #items = marketdb.itemIDList()

            #for item in items:
            #    marketdb.createSummaryForItem(item, 14)
            marketdb.createSummaryForItems(14)
            marketdb.createStocks()
