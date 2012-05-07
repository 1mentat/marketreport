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
            wtrans = auth.char.WalletTransactions(characterID=character.characterID)

            for row in wtrans.transactions:
                marketdb.addtransaction(row.transactionDateTime,row.transactionID,row.quantity,row.typeName,row.typeID,row.price,row.clientID,row.clientName,row.stationID,row.stationName,row.transactionType,row.transactionFor)
