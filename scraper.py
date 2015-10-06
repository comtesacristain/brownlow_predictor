from bs4 import BeautifulSoup
from urllib2 import urlopen
from urlparse import urljoin
from openpyxl import Workbook
import re, os

#STATS_FIELDS={'KI':'kicks','MK':'marks','HB':'handballs','DI':'disposals','GL':'goals','BH':'behinds','HO':'hitouts','TK':'tackles','RB':'rebound_50s','IF':'inside_50s','CL':'clearances','CG':'clangers','FF':'frees_for','FA':'frees_against','BR':'brownlow_votes','CP':'contested_possessions','UP':'uncontested_possessions','CM':'contested_marks','MI':'marks_inside50','1%':'one_percenters','BO':'bounces','GA':'goal_assists','%P':'time_on_ground'}
STATS_FIELDS=['KI','MK','HB','DI','GL','BH','HO','TK','RB','IF','CL','CG','FF','FA','BR','CP','UP','CM','MI','1%','BO','GA','%P']
MATCH_STATS_TEXT="Match stats" # Change if URL text changes for Match stats page


URL= 'http://afltables.com/afl/seas/{0}.html'

def main():
    years = range(2007,2016)
    for year in years:
        path=os.path.join("./",str(year))
        if not os.path.exists(path): os.makedirs(path)
        year_page = BeautifulSoup(urlopen(URL.format(year)))
        # TODO: Smart searching required below. Should only pull those links that are found in regular season games. Currently pulls data from finals (which don't have Brownlow votes)
        links=year_page.find_all('a')
        match_links = map(lambda y: urljoin(URL,y.attrs['href']), filter(lambda x: x.text==MATCH_STATS_TEXT,links))
        for match_link in match_links:
            print match_link
            match_stats = BeautifulSoup(urlopen(match_link))
            # TABLE 0: scores
            # TABLE 1 & 3: Abbreviations key (TODO: infer STATS_FIELDS dictionary from this?) 
            # TABLE 2: Home team (winning team if finals)
            # TABLE 4: Away team (losing team if finals)
            # TABLE 5-6: Team bios (games played, years of age)
            # TABLE 7: Score progession
            wb = Workbook()
            score_sheet = wb.active
            score_sheet.title="Scores"
            tables=match_stats.find_all('table')
            if re.search("Notes",tables[1].text):
                team_stats_pair=[3,5]
            else:
                team_stats_pair=[2,4]
            scores=parse_scores(tables[0])
            print scores[0][0]
            filename=re.match(r"Round: ([0-9]{1,2}|\w+ Final)",scores[0][0]).group(0).replace(': ','') + scores[1][0] + scores[2][0]
            for row in scores:
                score_sheet.append(row)
            for i in team_stats_pair:
                stats=parse_stats(tables[i])
                stats_sheet = wb.create_sheet()
                stats_sheet.title=stats['team']
                header = STATS_FIELDS[:]
                header.insert(0,"PLAYER")
                stats_sheet.append(header)
                for player in stats['players']:
                    player_stats = [player[stat] for stat in STATS_FIELDS]
                    player_stats.insert(0,player["name"])
                    stats_sheet.append(player_stats)
            
            wb.save(os.path.join(path,filename+".xlsx"))
            
        

def parse_scores(scores):
    # TODO : Parse correctly to check for unique structure to the scores table
    rows=scores.find_all('tr')
    if rows.__len__() != 6:
        return 0
    rows=scores.find_all('tr')
    # ROW 0: Round and Venue information
    # ROW 1: Home (winning) team scoreline
    # ROW 2: Away (losing) teams scoreline
    # ROW 3: Quarter margins
    # ROW 4: Quarter scores
    # ROW 5: Umpires.
    round_and_venue=[rows[0].find_all('td')[1].text]
    home_score = [x.text for x in rows[1].find_all('td')]
    away_score = [x.text for x in rows[2].find_all('td')]
    umpires = [rows[5].find_all('td')[1].text]
    return [round_and_venue,home_score,away_score,umpires]
    #x=dict()
    #x["round"] = re.match(r"Round: [0-9]{1,2}",round_and_venue).group(0)
    #x["venue"] = re.search(r"Venue: .*(?= Date)",round_and_venue[0]).group(0)
    #x["date"] = re.search(r"Date: .*(?= Attendance)",round_and_venue[0]).group(0)
    #x["attendance"] = re.search(r"Attendance: [0-9]{4,6}",round_and_venue[0]).group(0)
    #return x

def parse_stats(stats):
    team_stats=dict()
    rows=stats.find_all('tr')
    team_stats['team']=re.match(r'.*(?= Match)',rows[0].text).group(0)
    team_stats['players'] = list()
    header = [x.text for x in  rows[1].find_all('th')]
    stats_fields=dict([field,header.index(field)] for field in STATS_FIELDS)
    for row in rows[2:]:
        player=dict()
        cells=row.find_all('td')
        if cells[0].text=="Rushed":
            break
        elif cells[0].text=="Totals":
            break
        player["number"] = cells[0].text
        player["name"] = cells[1].text
        player["url"] = cells[1].find('a').attrs['href']
        for key in stats_fields.keys():
            if cells[stats_fields[key]].text == u'\xa0':
                player[key]=None
            else:
                player[key] = int(cells[stats_fields[key]].text)
        team_stats['players'].append(player)
    
    return team_stats
    
    
main()
    
    
        
    
    