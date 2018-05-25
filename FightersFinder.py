import urllib2
from bs4 import BeautifulSoup
from IndexFighters import getFighters
from difflib import get_close_matches
from difflib import SequenceMatcher

class NoFightFound(Exception):
    def __init__(self):
        self = self
        
class FightFinder:
    def __init__(self):
        self.fighterOneCandids = {}
        self.fighterTwoCandids = {}
        
    def addFighterOneCandids(self, poss):
        for (e,p) in poss:
            if self.fighterOneCandids.get(e,0) < p:
                self.fighterOneCandids[e] = p
                
    def addFighterTwoCandids(self, poss):
        for (e,p) in poss:
            if self.fighterTwoCandids.get(e,0) < p:
                self.fighterTwoCandids[e] = p
    
    def getFights(self, link):
        page = urllib2.urlopen(link)
        soup = BeautifulSoup(page, 'html.parser')
        fightBoxes = soup.find_all('tr', attrs={'class', 'b-fight-details__table-row b-fight-details__table-row__hover js-fight-details-click'})
        fightIDs = map(lambda fight: fight['data-link'][37:], fightBoxes)
        return fightIDs

    def intersectedFights(self, f1, f2):
        fighterPagePrefix = 'http://fightmetric.com/fighter-details/'
        f1Link = fighterPagePrefix + f1
        f2Link = fighterPagePrefix + f2
        f1Fights = self.getFights(f1Link)
        f2Fights = self.getFights(f2Link)
        intersection = set(f1Fights) & set(f2Fights)
        return intersection
    
    def findMostProbableFights(self):
        combinations = []
        for e1 in self.fighterOneCandids:
            for e2 in self.fighterTwoCandids:
                if e1 != e2:
                    prob = self.fighterOneCandids[e1] * self.fighterTwoCandids[e2]
                    combinations.append((prob, e1, e2))
        combinations.sort()
        for (_,e1,e2) in reversed(combinations):
            commonFights = self.intersectedFights(e1,e2)
            if len(commonFights) > 0: return commonFights
        raise NoFightFound
    
def findPossFighter(fighters, name):
    poss = []
    # Scenario 1: only one string in name, check that if it's a unique qualifier
    if len(name) == 1:
        lastNames = filter(lambda row: row[1] == name[0], fighters)
        nickNames = filter(lambda row: row[2] == name[0], fighters)
        firstNames = filter(lambda row: row[0] == name[0], fighters)
        if 0 < len(lastNames) < 10:
            prob = 1.0 / len(lastNames)
            poss = poss + map(lambda row: (row[3], prob), lastNames)
        elif 0 < len(nickNames) < 10:
            prob = 1.0 / len(nickNames)
            poss = poss + map(lambda row: (row[3], prob), nickNames)
        elif 0 < len(firstNames) < 10:
            prob = 1.0 / len(firstNames)
            poss = poss + map(lambda row: (row[3], prob), firstNames)
            
    # Scenario 2: if name has two strings, check if it's first name and last name
    if len(name) == 2:
        candids = filter(lambda row: row[0] == name[0] and row[1] == name[1], fighters)
        if 0 < len(candids) < 5:
            prob = 1.0 / len(candids)
            poss = poss + map(lambda row: (row[3], prob), candids)
        
    # Scenario 3: nothing has worked, use 'difflib'
    mp = dict(map(lambda row: (row[0] + u' ' + row[2] + u' ' + row[1], row), fighters)) 
    matches =  get_close_matches(u' '.join(name), list(mp.keys()), 4)
    poss = poss + map(lambda nm: (mp[nm][3], SequenceMatcher(None, u' '.join(name), nm).ratio()) , matches)
    return poss                  

# Finds two fighters that match the given fighters
def findFights(fighters, names):
    fightFinder = FightFinder()
    
    # Scenario 1: there is a seperator between the names
    seperators = set([u'with', u'against', u'vs', u'versus', u'and'])
    if(set(names) & seperators != set()):
        pre = []
        post = []
        flag = False
        
        for w in names:
            if flag:
                post.append(w)
            elif w in seperators:
                flag = True
            else:
                pre.append(w)
        fightFinder.addFighterOneCandids(findPossFighter(fighters, pre))
        fightFinder.addFighterTwoCandids(findPossFighter(fighters, post))

    # Scenario 2: only two words
    if len(names) == 2:
        fightFinder.addFighterOneCandids(findPossFighter(fighters, names[0]))
        fightFinder.addFighterTwoCandids(findPossFighter(fighters, names[1]))
        
    # Scenario 3: use first two words for first fighter
    if len(names) > 2:
        fightFinder.addFighterOneCandids(findPossFighter(fighters, names[:2]))
        fightFinder.addFighterTwoCandids(findPossFighter(fighters, names[2:]))

    # Scenario 4: use first 3 words for first fighter
    if len(names) > 3:
        fightFinder.addFighterOneCandids(findPossFighter(fighters, names[:3]))
        fightFinder.addFighterTwoCandids(findPossFighter(fighters, names[3:]))

    # Scenario 5: use the first word for first fighter
    fightFinder.addFighterOneCandids(findPossFighter(fighters, names[:1]))
    fightFinder.addFighterTwoCandids(findPossFighter(fighters, names[1:]))

    # Scenario 6: Use 4 words for first
    if len(names) > 4:
        fightFinder.addFighterOneCandids(findPossFighter(fighters, names[:4]))
        fightFinder.addFighterTwoCandids(findPossFighter(fighters, names[4:]))

    return fightFinder.findMostProbableFights()
