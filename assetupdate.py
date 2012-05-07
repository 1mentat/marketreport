import imp, argparse
import settings
import time
import assetdb
eveapi = imp.load_source('eveapi', '../eveapi/eveapi.py')

def getContents(locationID, row):
    for crow in row.contents:
        print crow
        assetdb.addasset(locationID, crow.typeID, crow.quantity)
        #assetdb.addasset(locationID, crow.itemID, crow.quantity)
        try:
            if crow.contents:
                getContents(locationID, crow)
        except AttributeError:
            pass

if __name__ == '__main__':
    assetdb.setupdb()
    parser = argparse.ArgumentParser(description='Options')
    parser.add_argument('-n', '--name', dest='name', default=settings.name)
    args = parser.parse_args()

    api = eveapi.EVEAPIConnection()
    auth = api.auth(keyID=settings.keyID, vCode=settings.vCode)

    result = auth.account.Characters()

    for character in result.characters:
        if character.name==args.name:

            aresult = auth.char.AssetList(characterID=character.characterID)

            for row in aresult.assets:
                print row
                assetdb.addasset(row.locationID, row.typeID, row.quantity)
                try:
                    if row.contents:
                        getContents(row.locationID, row)
                except AttributeError:
                    pass
