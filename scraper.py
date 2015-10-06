from bs4 import BeautifulSoup
from urllib2 import urlopen
from urlparse import urljoin
from openpyxl import Workbook
STATS_FIELDS={'KI':'kicks','MK':'marks','HB':'handballs','DI':'disposals','GL':'goals','BH':'behinds','HO':'hitouts','TK':'tackles','RB':'rebound_50s','IF':'inside_50s','CL':'clearances','CG':'clangers','FF':'frees_for','FA':'frees_against','BR':'brownlow_votes','CP':'contested_possessions','UP':'uncontested_possessions','CM':'contested_marks','MI':'marks_inside50','1%':'one_percenters','BO':'bounces','GA':'goal_assists','%P':'time_on_ground'}
MATCH_STATS_TEXT="Match stats" # Change if URL text changes for Match stats page
URL= 'http://afltables.com/afl/seas/2015.html' # TODO: Loop through a number of years? Simply need to change year parameter

def main:
    year_page = BeautifulSoup(urlopen(URL))
    # TODO: Smart searching required below. Should only pull those links that are found in regular season games. Currently pulls data from finals (which don't have Brownlow votes)
    links=year_page.find_all('a')
    match_links = map(lambda y: urljoin(URL,y.attrs['href']), filter(lambda x: x.text==MATCH_STATS_TEXT,links))
    for match_link in match_links:
        match_stats = BeautifulSoup(urlopen(match_link))
        # TABLE 0: scores
        # TABLE 1 & 3: Abbreviations key (TODO: infer STATS_FIELDS dictionary from this?) 
        # TABLE 2: Home team (winning team if finals)
        # TABLE 4: Away team (losing team if finals)
        # TABLE 5-6: Team bios (games played, years of age)
        # TABLE 7: Score progession
        wb = Workbook()
        scores = wb.active
        scores.title="Scores"
        tables=match_stats.find_all('table')
        parse_scores(tables[0])
        

def parse_scores(scores):
    rows=scores.find_all('tr')
    if rows.__len__() != 6:
        return 0
    else:
        score_array=list()
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
    
    
    
        
    
    