from bs4 import BeautifulSoup
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import json

#===========================================
# Open browser
#===========================================
options = Options()
options.add_argument("--headless")    # window doesn't pop up
options.add_argument("--log-level=3") # console log isn't printed
chrome_service = Service(ChromeDriverManager().install())
browser = Chrome(service=chrome_service, options=options)


#===========================================
# Find all competitions on home page
#===========================================
home_url = "https://total-waterpolo.com"
def match_url(id: int):
  return f"https://total-waterpolo.com/tw_match/{id}"
data = {"competitions": []}

# load home page
results_dropdown_id = "menu-item-99132"
browser.get(home_url)
WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.CLASS_NAME, 'section_wrapper')))
home_soup = BeautifulSoup(browser.page_source, "html.parser")

# find all links in "results" dropdown
for a in home_soup.find(attrs={'id': results_dropdown_id}).find(attrs={'class': 'section_wrapper'}).find_all('a'):
  # filter out # links
  if not a['href'] == "#":
    # none match link can be filltered out during the reading process
    try:
      data["competitions"].append({'url': a['href']})
    except AttributeError:
      # not a match link
      continue
    

#===========================================
# Find all match URLs from competition page
#===========================================
for comp in range(len(data["competitions"])):
  browser.get(data["competitions"][comp]['url'])
  try:
    #WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "match-link")))
    # because data need some tine to load, we first wait 2s to find atleast one link and then check every 0.5s to see if we find any more
    # if a match hasn't started yet, it's class will be "match-time" instead of "match-link"
    num = [0, len(WebDriverWait(browser, 2).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "match-link"))))]
    while num[1] > num[0]:
      num[0] = num[1]
      num[1] = len(WebDriverWait(browser, 0.5).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "match-link"))))
  except TimeoutException:
    # not a competition page
    #print(data['competitions'][comp]['url'])
    data['competitions'][comp] = {}
    continue
  
  match_soup = BeautifulSoup(browser.page_source, "html.parser")
  data['competitions'][comp]['matches'] = []
  for match in match_soup.find_all(attrs={'class': 'tw_match_basic'}):
    try:
      match_id = int(match.find(attrs={'class': 'match-link'})['href'].split("/")[-1])
    except TypeError:
      continue
    home_name = match.find(attrs={'tw-data': 'hometeamname'}).text
    away_name = match.find(attrs={'tw-data': 'awayteamname'}).text
    
    data['competitions'][comp]['matches'].append({
      'id': match_id,
      'teams': {
        'home': home_name,
        'away': away_name
      }
    })
  
  """data['competitions'][comp]['rounds'] = {}
  for round in match_soup.find_all(attrs={'class': 'tw_competition_round'}):
    data["competitions"][comp]['rounds'][round['tw_round_id']] = {}
    
    for match in round.find_all(attrs={'class': 'tw_match_basic'}):
      match_link = match.find(attrs={'class': 'match-link'})
      home_name = match.find(attrs={'tw-data': 'hometeamname'}).text
      away_name = match.find(attrs={'tw-data': 'awayteamname'}).text
      
      if not match_link == None:
        match_name = f"{home_name} vs {away_name}"
        data["competitions"][comp]['rounds'][round['tw_round_id']][match_name] = {'url': f"{home_url}{match_link['href']}"}"""
        
with open('test.json', 'w') as f:
  json.dump(data, f, sort_keys=True, indent=4)
  exit()


#===========================================
# Get match data
#===========================================
for competition in data:
  for round in data[competition]['rounds']:
    for match in data[competition]['rounds'][round]:
      browser.get(data[competition]['rounds'][round][match]['url'])
      WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "tw_match_player")))
      WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "tw_play_by_play")))
      
      match_soup = BeautifulSoup(browser.page_source, "html.parser")
      data[competition]['rounds'][round][match]['lineup'] = {}   
      data[competition]['rounds'][round][match]['short'] = {}   
      
      for team in ["home", "away"]:
        # Get short team names
        shortName = match_soup.find(attrs={'tw-data': f"{team}teamname_short"}).text
        data[competition]['rounds'][round][match]['short'][team] = shortName if not shortName == "-" else "null"
      
        # Get players
        data[competition]['rounds'][round][match]['lineup'][team] = {}
        for player in match_soup.find(attrs={'id': f"{team}Players"}).find_all(attrs={'class': 'tw_match_player'}):
          data[competition]['rounds'][round][match]['lineup'][team][int(player.find(attrs={'tw-data': 'playerNum'}).text.strip())] = {
            'name': player.find(attrs={'tw-data': 'playerName'}).text.strip(),
            'id': int(player['tw-player-id'])
          }
          
        # Get goalkeeprs
        for goalkeeper in match_soup.find(attrs={'id': f"{team}Goalkeepers"}).find_all(attrs={'class': 'tw_match_player'}):
          shortName = player.find(attrs={'tw-data': 'playerName'}).text.strip()
          data[competition]['rounds'][round][match]['lineup'][team][int(player.find(attrs={'tw-data': 'playerNum'}).text.strip())] = {
            'name': shortName if not shortName == "-" else "null",
            'id': int(player['tw-player-id'])
          }
      
      # Get plays
      data[competition]['rounds'][round][match]['plays'] = {}
      for q in ['q1', 'q2', 'q3', 'q4', 'ot']:
        data[competition]['rounds'][round][match]['plays'][q] = []
        quarter = match_soup.find(attrs={'id': f"play-by-play-{q}"})
        for play in quarter.find_all(attrs={'class': 'tw_play_by_play'}):
          id = play['tw-event-id']
          try:
            details_overview = play.find(attrs={'id': f"pills-overview_event_{id}"}).find_all(attrs={'class': 'detailsMetaRow'})
          except AttributeError:
            details_overview = None   # play doesn't have dropdown (play is timeout or card)
          
          # time of play
          time = play.find(attrs={'class': 'row'}).find(attrs={'class': 'text-center'}).find('div').text
          seconds = 60*int(time.split(':')[0]) + int(time.split(':')[1])
          
          # which play
          action = play.find(attrs={'class': 'row'}).find(attrs={'class': 'event-label'}).find(attrs={'class': 'description'}).text.lower()
          if not details_overview == None:
            for overview in details_overview:
              if overview.find(attrs={'class': 'description'}).text == "details":
                detail = overview.find(attrs={'class': 'label'}).text.strip().lower()
                break
              else:
                detail = ""
          else:
            detail = ""
          
          # shortened team name
          teamName_short = play.find(attrs={'class': 'row'}).find(attrs={'tw-data': 'team'}).text.lower()
          team = 'home' if data[competition]['rounds'][round][match]['short']['home'] == teamName_short else 'away'
          
          # players involved
          if not details_overview == None:
            player = int(play.find(attrs={'class': 'row'}).find(attrs={'tw-data': 'playerNum'}).text)
            for overview in details_overview:
              if overview.find(attrs={'class': 'description'}).text == "PLAYER":
                player2_name = overview.find(attrs={'class': 'label'}).text.strip()
                break
              else:
                player2_name = ""
          else:
            player = 0
            player2_name = ""
          
          # location of the play
          try:
            location_style = play.find(attrs={'id': f"pills-location_event_{id}"}).find(attrs={'class': 'tw_marker'})['style']
            location = [float(location_style.split('bottom: ')[1].split('%')[0])/100, float(location_style.split('left: ')[1].split('%')[0])/100]
          except AttributeError:
            location = [0, 0]
          except TypeError:
            location = [0, 0]
          
          # target of the play (relevant to shots)
          try:
            target_style = play.find(attrs={'id': f"pills-target_event_{id}"}).find(attrs={'class': 'tw_marker'})['style']
            target = [float(target_style.split('bottom: ')[1].split('%')[0])/100, float(target_style.split('left: ')[1].split('%')[0])/100]
          except AttributeError:
            target = [0, 0]
          except TypeError:
            target = [0, 0]
          
          data[competition]['rounds'][round][match]['plays'][q].append({
            'time': seconds,   # time in seconds
            'action': action,  # depends on action (example: action, power play,...)
            'details': detail,
            'team': team,
            'player': player,
            'player2': player2_name,  # can be 0
            'location': location,     # [bottom, left] of class=tw_marker
            'target': target          # [bottom, left] of class=tw_marker
          })


#===========================================
# Get plays
#===========================================
with open('data.json', 'w') as f:
  json.dump(data, f, sort_keys=True, indent=4)


#===========================================
# Close browser
#===========================================
browser.close()