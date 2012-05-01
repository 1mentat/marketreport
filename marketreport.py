import urllib2, urllib
import settings

def getcharacters(keyID, vCode):
    values = {}

    values['keyID'] = keyID
    values['vCode'] = vCode

    encvalues = urllib.urlencode(values)

    print urllib2.urlopen('https://api.eveonline.com/account/Characters.xml.aspx?',encvalues).read()

if __name__ == '__main__':
    getcharacters(settings.keyID,settings.vCode)
