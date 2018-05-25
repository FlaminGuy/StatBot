import urllib2
from bs4 import BeautifulSoup

class FightStats:
    def __init__(self, id):
        self.link = 'http://www.fightmetric.com/fight-details/' + id
        self.page = urllib2.urlopen(self.link)
        self.soup = BeautifulSoup(self.page, 'html.parser')
    def fightersNames(self):
    	print self.link
        fightersBoxes = self.soup.find_all('div', attrs={'class', 'b-fight-details__person'})
        self.result = map(lambda box: box.find('i', attrs={'class', 'b-fight-details__person-status'}).text.rstrip().lstrip(), fightersBoxes)
        self.names = map(lambda box: box.find('h3', attrs={'class', 'b-fight-details__person-name'}).text.rstrip().lstrip(), fightersBoxes)
        self.nickname = map(lambda box: box.find('p', attrs={'class', 'b-fight-details__person-title'}).text.rstrip().lstrip(), fightersBoxes)
    def 