import imp, argparse
import settings
eveapi = imp.load_source('eveapi', '../eveapi/eveapi.py')

market_transaction = 2
brokers_fee = 46
transaction_tax = 54

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Options')
    parser.add_argument('-n', '--name', dest='name', default=settings.name)
    args = parser.parse_args()

    api = eveapi.EVEAPIConnection()
    auth = api.auth(keyID=settings.keyID, vCode=settings.vCode)

    result = auth.account.Characters()

    for character in result.characters:
        if character.name==args.name:
            accountbalance = auth.char.AccountBalance(characterID=character.characterID)
            print accountbalance.accounts[0].balance
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
                        print 'Paid broker {0}'.format(trans.amount)
                    elif trans.refTypeID == transaction_tax:
                        print 'Paid transaction tax {0}'.format(trans.amount)
                
            #marketorders = auth.char.MarketOrders(characterID=character.characterID)
            #ordersByTypeID = marketorders.orders.GroupedBy('typeID')
            #for order in ordersByTypeID[439]:
            #    print order

