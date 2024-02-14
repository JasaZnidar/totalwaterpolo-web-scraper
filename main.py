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
import time
import datetime

#===========================================
# Variables and functions
#===========================================
home_url = "https://total-waterpolo.com"
def match_url(id: int):
  return f"https://total-waterpolo.com/tw_match/{id}"
data_file_name = "test.json"
try:
  with open(data_file_name, "r") as f:
    data = json.load(f)
except FileNotFoundError:
  data = {
    'players': {},
    'matches': {}
  }
results_dropdown_id = "menu-item-99132"
wait_time = [7.0, 0.5]
progress_bar = True
none_players = 0
number_of_players = 130
try:
  player_id_start = max([int(key) for key in data['players']]) + 1
except ValueError:
  player_id_start = 1
player_id_limit = player_id_start + number_of_players
player_id = player_id_start
player_url = "https://total-waterpolo.com/tw_player"

def progress():
  comp_prog = int((player_id - player_id_start)*100 // number_of_players)
  comp_perc = (player_id - player_id_start)*100 / number_of_players
  if progress_bar:
    print(f"Players [{player_id+1}]: |{'█' * comp_prog}{'-' * (100 - comp_prog)}| {comp_perc:.1f}% Complete", end="\r")


#===========================================
# Open browser
#===========================================
options = Options()
options.add_argument("--headless")    # window doesn't pop up
options.add_argument("--log-level=3") # console log isn't printed
chrome_service = Service(ChromeDriverManager().install())
browser = Chrome(service=chrome_service, options=options)


#===========================================
# Find all players and their matches
#===========================================
progress()
  
for player_id in range(player_id_start, player_id_limit + 1):
  try:
    browser.get(f"{player_url}/{player_id}")
  except TimeoutException:
    # URL timed out
    none_players += 1
    progress()
    continue
  
  try:
    progress()
    # wait a few seconds for player stats (position, hand, height, weight) to load
    WebDriverWait(browser, wait_time[0]).until_not(EC.text_to_be_present_in_element((By.XPATH, '//*[@id="Wrapper"]/div[2]/div[2]/div[2]/div[1]/div/div[2]/div[2]'), "-"))
    WebDriverWait(browser, wait_time[1]).until_not(EC.text_to_be_present_in_element((By.XPATH, '//*[@id="Wrapper"]/div[2]/div[2]/div[2]/div[2]/div/div[2]/div[2]'), "-"))
    WebDriverWait(browser, wait_time[1]).until_not(EC.text_to_be_present_in_element((By.XPATH, '//*[@id="Wrapper"]/div[2]/div[2]/div[3]/div[1]/div/div[2]/div[2]'), "-"))
    WebDriverWait(browser, wait_time[1]).until_not(EC.text_to_be_present_in_element((By.XPATH, '//*[@id="Wrapper"]/div[2]/div[2]/div[3]/div[2]/div/div[2]/div[2]'), "-"))
  except TimeoutException:
    # player has no statistics, probably not a player
    none_players += 1
    progress()
    continue
  
  try:
    num = [0, len(WebDriverWait(browser, wait_time[1]).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "tw_match_basic"))))]
    while num[1] > num[0]:
      num[0] = num[1]
      num[1] = len(WebDriverWait(browser, wait_time[1]).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "tw_match_basic"))))
  except TimeoutException:
    # no recorded matches, check if player exists by finding player name
    if BeautifulSoup(browser.page_source, "html.parser").find(attrs={'tw-data': 'name'}).text == "-":
      # player doesn't exist
      none_players += 1
      progress()
      continue

  # get player data
  player_soup = BeautifulSoup(browser.page_source, "html.parser")
  
  try:
    player_position = player_soup.find(attrs={'tw-data': 'position'}).text
  except AttributeError:
    player_position = ''
  try:
    player_hand = player_soup.find(attrs={'tw-data': 'hand'}).text
  except AttributeError:
    player_hand = ''
  try:
    player_height = int(player_soup.find(attrs={'tw-data': 'height'}).text)
  except ValueError:
    player_height = None
  try:
    player_weight = int(player_soup.find(attrs={'tw-data': 'weight'}).text)
  except ValueError:
    player_weight = None
  try:
    player_birth = datetime.datetime.strptime(player_soup.find(attrs={'tw-data': 'birthday'}).text, "%d.%m.%Y")
  except ValueError:
    player_birth = None
  except OverflowError:
    print(f"Overflow error: {player_soup.find(attrs={'tw-data': 'birthday'}).text}")
    player_birth = None
    
  
  data['players'][str(player_id)] = {
    'position': player_position,
    'hand': player_hand,
    'height': player_height,
    'weight': player_weight,
    'birth': player_birth
  }
  
  # get matches id
  try:
    matches_soup = player_soup.find(attrs={'id': 'playerMatchesContainer'}).findChildren('div', recursive=False)
  except AttributeError:
    print("error finding matches")
    progress()
    continue
  for match in matches_soup:
    try:
      if str(match['tw-match-id']) in data['matches']:
        continue
      
      data['matches'][str(match['tw-match-id'])] = {
        'competition id': match['tw-competition-id']
      }
    except KeyError:
      print("match:", match.attrs)
      break
    
  progress()

print(f"\n\nplayers: {len(data['players'])}\nmatches: {len(data['matches'])}")

with open(data_file_name, "w") as f:
  json.dump(data, f, sort_keys=True, indent=4)

browser.close()
exit(0)

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
    print(f"Players [{player_id+1:6}]: |{'█' * comp_prog}{'-' * (100 - comp_prog)}| {comp_perc:.1f}% Complete", end="\r")
  
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
    print(f"Players [{player_id+1:6}]: |{'█' * 100}| 100.0% Complete")

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
with open(data_file_name, "w") as f:
  json.dump(data, f, sort_keys=True, indent=4)


#===========================================
# Close browser
#===========================================
browser.close()