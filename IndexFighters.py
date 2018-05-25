import urllib2
from string import ascii_lowercase
from bs4 import BeautifulSoup

# Parse the information for a fighter, append it to 'fighters_list'
def parseFighter(page, fighters_list):
    fighter = []
    cols = page.find_all('td', attrs={'class', 'b-statistics__table-col'})

    # First column is first name, second is last name and thrid is nickname
    for i in range(0, 3):
        fighter.append(cols[i].find('a', attrs={'class', 'b-link b-link_style_black'}).text.lower())

    # Identifier of the fighter    
    fighter.append(cols[0].a['href'][43:])
    fighters_list.append(fighter)

# Parse fighters that their last name starts with the same alphabet    
def parseFighters(page, fighters_list):
    fighters_box = page.find_all('tr', attrs={'class', 'b-statistics__table-row'})
    for i in range(2, len(fighters_box)):
        parseFighter(fighters_box[i], fighters_list)

# Get first, last and nickname of all fighters avilable        
def getFighters():
    # Suffix and prefix of a link to list of fighters
    link_prefix = 'http://www.fightmetric.com/statistics/fighters?char='
    link_suffix = '&page=all'

    lst = []
    for c in ascii_lowercase:
        link = link_prefix + c + link_suffix
        page = urllib2.urlopen(link)
        soup = BeautifulSoup(page, 'html.parser')
        parseFighters(soup,lst)

    return lst
