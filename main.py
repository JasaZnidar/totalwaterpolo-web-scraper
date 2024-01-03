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
import re

#===========================================
# Variables and functions
#===========================================
home_url = "https://total-waterpolo.com"
def match_url(id: int):
  return f"https://total-waterpolo.com/tw_match/{id}"
data = {"competitions": []}
results_dropdown_id = "menu-item-99132"
wait_time = [3.0, 0.5]
progress_bar = True


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
# load home page
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
      # not a competition link
      continue
    

#===========================================
# Find all match URLs from competition page
#===========================================
none_comp = []
for comp in range(len(data['competitions'])):
  if progress_bar:
    comp_prog = int(100 * comp // len(data['competitions']))
    comp_perc = comp/len(data['competitions']) * 100
    print(f"Matches in competitons: |{'█' * comp_prog}{'-' * (100 - comp_prog)}| {comp_perc:.1f}% Complete", end="\r")
  
  browser.get(data["competitions"][comp]['url'])
  try:
    # because data need some tine to load, we first wait 2s to find atleast one link and then check every 0.5s to see if we find any more
    # if a match hasn't started yet, it's class will be "match-time" instead of "match-link"
    num = [0, len(WebDriverWait(browser, wait_time[0]).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "match-link"))))]
    while num[1] > num[0]:
      num[0] = num[1]
      num[1] = len(WebDriverWait(browser, wait_time[1]).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "match-link"))))
  except TimeoutException:
    # not a competition page
    data['competitions'][comp] = {}
    none_comp.append(comp)
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
      },
      'result': {},
      'short': {},
      'lineup': {
        'home': {},
        'away': {}
      },
      'plays': []
    })

if progress_bar:
    print(f"Matches in competitons: |{'█' * 100}| 100.0% Complete")

# Clear out none competitions
none_comp.reverse()
for i in none_comp:
  del data['competitions'][i]


#===========================================
# Get match data
#===========================================
for comp in range(len(data['competitions'])):
  if progress_bar:
    comp_prog = int(100 * comp // len(data['competitions']))
    comp_perc = comp/len(data['competitions']) * 100
    print(f"Competitons progress:   |{'█' * comp_prog}{'-' * (100 - comp_prog)}| {comp_perc:5.1f}% Complete")
  
  for match in range(len(data['competitions'][comp]['matches'])):
    if progress_bar:
      match_prog = int(100 * match // len(data['competitions'][comp]['matches']))
      match_perc = match/len(data['competitions'][comp]['matches']) * 100
      print(f"Matches progress:       |{'█' * match_prog}{'-' * (100 - match_prog)}| {match_perc:5.1f}% Complete ({data['competitions'][comp]['matches'][match]['id']})", end="\r")
      
    # load match page
    browser.get(match_url(data['competitions'][comp]['matches'][match]['id']))
    num = [0, len(WebDriverWait(browser, wait_time[0]).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "tw_play_by_play"))))]
    while num[1] > num[0]:
      num[0] = num[1]
      num[1] = len(WebDriverWait(browser, wait_time[1]).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "tw_play_by_play"))))
    match_soup = BeautifulSoup(browser.page_source, "html.parser")
    
    # team result, lineups and short team names
    for team in ["home", "away"]:
      # result
      data['competitions'][comp]['matches'][match]['result'][team] = int(match_soup.find(attrs={'tw-data': f"{team}teamgoals"}).text)
      
      # short name
      shortName = match_soup.find(attrs={'tw-data': f"{team}teamname_short"}).text.lower()
      data['competitions'][comp]['matches'][match]['short'][team] = shortName if not shortName == "-" else "null"
      
      # lineup
      for player in match_soup.find(attrs={'id': f"{team}Players"}).find_all(attrs={'class': 'tw_match_player'}):
        data['competitions'][comp]['matches'][match]['lineup'][team][int(player.find(attrs={'tw-data': 'playerNum'}).text.strip())] = {
          'name': player.find(attrs={'tw-data': 'playerName'}).text.strip(),
          'match_id': int(player['tw-player-id']),
          'id': re.compile(r"(\d\d\d\d\d\d)|(\d\d\d\d\d)|(\d\d\d\d)|(\d\d\d)|(\d\d)|(\d)").search(player.find(attrs={'tw-data': 'playerName'})['onclick']).group(0)
        }
      for goalkeeper in match_soup.find(attrs={'id': f"{team}Goalkeepers"}).find_all(attrs={'class': 'tw_match_player'}):
        data['competitions'][comp]['matches'][match]['lineup'][team][int(goalkeeper.find(attrs={'tw-data': 'playerNum'}).text.strip())] = {
          'name': goalkeeper.find(attrs={'tw-data': 'playerName'}).text.strip(),
          'match_id': int(player['tw-player-id'])
        }
      
    # plays
    play_cnt = -1
    for play in match_soup.find_all(attrs={'class': 'tw_play_by_play'}):
      # play id
      id = play['tw-event-id']
      
      # play details
      try:
        details_overview = play.find(attrs={'id': f"pills-overview_event_{id}"}).find_all(attrs={'class': 'detailsMetaRow'})
      except AttributeError:
        details_overview = None   # play doesn't have dropdown (play is timeout or card)
        
      # play time
      time = play.find(attrs={'class': 'row'}).find(attrs={'class': 'text-center'}).find('div').text
      quarter = f"{play['class']}"[1:-1].split('-')[-1][0:1]
      try:
        quarter = int(quarter)
      except TypeError:
        quarter = 5
      seconds = 8*60*quarter - (60*int(time.split(':')[0]) + int(time.split(':')[1]))
      
      # play action
      action = play.find(attrs={'class': 'row'}).find(attrs={'class': 'event-label'}).find(attrs={'class': 'description'}).text.lower()
      if not details_overview == None:
        for overview in details_overview:
          if overview.find(attrs={'class': 'description'}).text.lower() == "details":
            detail = overview.find(attrs={'class': 'label'}).text.strip().lower()
            break
          else:
            detail = ""
      else:
        detail = ""
      
      # shortened team name
      teamName_short = play.find(attrs={'class': 'row'}).find(attrs={'tw-data': 'team'}).text.lower()
      team = "home" if data['competitions'][comp]['matches'][match]['short']['home'] == teamName_short else "away"
      
      # players involved
      if not details_overview == None:
        try:
          player1 = int(play.find(attrs={'class': 'row'}).find(attrs={'tw-data': 'playerNum'}).text)
        except ValueError:
          player1 = 0
        for overview in details_overview:
          if overview.find(attrs={'class': 'description'}).text.lower() == "player":
            player2_name = overview.find(attrs={'class': 'label'}).text.strip()
            
            for player_num in data['competitions'][comp]['matches'][match]['lineup'][team]:
              if data['competitions'][comp]['matches'][match]['lineup'][team][player_num]['name'] == player2_name:
                player2 = player_num
                break
            break
          else:
            player2 = 0
      else:
        player1 = 0
        player2 = 0
      
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
      
      data['competitions'][comp]['matches'][match]['plays'].append({
          'time': seconds,   # time in seconds
          'action': action,  # depends on action (example: action, power play,...)
          'details': detail,
          'team': team,
          'player_1': player1,
          'player_2': player2,  # can be 0
          'location': location,     # [bottom, left] of class=tw_marker
          'target': target          # [bottom, left] of class=tw_marker
        })
  
  if progress_bar:  
    print("\u001b[2K\u001b[1A", end="")  # clear line and move cursor up
if progress_bar:
  print(f"Competitons progress:   |{'█' * 100}| {comp_perc:5.1f}% Complete")


#===========================================
# Save results
#===========================================
with open('data.json', 'w') as f:
  json.dump(data, f, sort_keys=True, indent=4)


#===========================================
# Close browser
#===========================================
browser.close()