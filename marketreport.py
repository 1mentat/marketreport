import imp, argparse
import settings
import time
import marketdb
import assetdb
import evedb
eveapi = imp.load_source('eveapi', '../eveapi/eveapi.py')

market_transaction = 2
brokers_fee = 46
transaction_tax = 54

def taxcheck(character, auth):
    matched_broker = set()
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
    assetdb.setupdb()
    evedb.setupdb()
    included_items_ids = set()
    #parser = argparse.ArgumentParser(description='Options')
    #parser.add_argument('-n', '--name', dest='name', default=settings.name)
    #args = parser.parse_args()

    for name in settings.included_items:
        typeID = evedb.getTypeIDfromTypeName(name)
        if typeID == -1:
            print 'Unable to find {0} in item database'.format(name)
            pass
        else:
            included_items_ids.add(typeID)

    for typeID in included_items_ids:
        print typeID
        assetdb.assetsByTypeID(typeID)

    #marketdb.createSummaryForItems(14)
    #marketdb.createStocks()
