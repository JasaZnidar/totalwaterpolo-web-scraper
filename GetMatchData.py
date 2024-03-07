from bs4 import BeautifulSoup
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import json
from constants import *
import GetPlayersAndMatches
import re
import zipJSON

data = {}

def main():
  global data
  
  #===========================================
  # Variables and functions
  #===========================================
  progress_bar = True
  matches = 0
  match_id = "0"
  id_to_del = []
  
  with open(data_file_name, "r") as f:
    data = json.load(f)
    
  def match_url(id: int):
    return f"https://total-waterpolo.com/tw_match/{id}"
  
  def progress():
    if progress_bar:
      comp_prog = int(matches*100 // len(data['matches']))
      comp_perc = matches*100 / len(data['matches'])
      print(f"Match [{match_id}]: |{'█' * comp_prog}{'-' * (100 - comp_prog)}| {comp_perc:.1f}% Complete", end="\r")
  

  #===========================================
  # Open browser
  #===========================================
  options = Options()
  options.add_argument("--headless")    # window doesn't pop up
  options.add_argument("--log-level=3") # console log isn't printed
  chrome_service = Service(ChromeDriverManager().install())
  browser = Chrome(service=chrome_service, options=options)
  

  #===========================================
  # Scan saved matches for data
  #===========================================
  progress()
  for match_id in data['matches']:
    
    progress()
    browser.get(match_url(match_id))
    
    # wait for player table to load
    WebDriverWait(browser, wait_time[0]).until(EC.presence_of_all_elements_located((By.ID, "table_player_stats")))
    
    # wait for all plays
    try:
      num = [0, len(WebDriverWait(browser, wait_time[0]).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "tw_play_by_play"))))]
      while num[1] > num[0]:
        num[0] = num[1]
        num[1] = len(WebDriverWait(browser, wait_time[1]).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "tw_play_by_play"))))
    except TimeoutException:
      # match has no data
      id_to_del.append(match_id)
      continue
    
    # get match soup
    match_soup = BeautifulSoup(browser.page_source, "html.parser")
    match_data = {
      'competition id': data['matches'][match_id]['competition id'],
      'result': {
        'home': 0,
        'away': 0
      },
      'name': {
        'home': "",
        'away': "",
        'short': {
          'home': "",
          'away': ""
        }
      },
      'lineup': {
        'home': {},
        'away': {}
      },
      'plays': [],
      'date': 0
    }
    
    # date
    full_date = match_soup.find(attrs={'tw-data': "matchdetails"}).text
    date = re.findall(r"\d{2}.\d{2}.\d{4}", full_date)
    match_data['date'] = days(date[0])
    
    # team result, lineups and short team names
    for team in ["home", "away"]:
      # result
      try:
        match_data['result'][team] = int(match_soup.find(attrs={'tw-data': f"{team}teamgoals"}).text)
      except ValueError:
        match_data['result'][team] = 0
      
      # full name
      try:
        first_player_id = match_soup.find(attrs={'id': f"{team}Players"}).find(attrs={'class': 'tw_match_player'}).find(attrs={'tw-data': 'playerName'})['onclick'].split("(")[1].split(")")[0]
        match_data['name'][team] = match_soup.find(attrs={'id': "table_player_stats"}).find(lambda tag: first_player_id in tag.text).find_all("td")[0].text.strip()
      except AttributeError:
        match_data['name'][team] = ""
    
      # short name
      shortName = match_soup.find(attrs={'tw-data': f"{team}teamname_short"}).text.lower()
      match_data['name']['short'][team] = shortName if not shortName == "-" else "null"
      
    # lineup
    for player in match_soup.find(attrs={'id': "table_player_stats"}).find_all("tr", recursive=False):
      player_td = [stat.text.strip() for stat in player.find_all("td")]
      id = player_td[2]
      saves = player_td[-1]
      team = 'home' if player_td[0] == match_data['name']['home'] else 'away'
      #print(team, player_td)
      match_data['lineup'][team][player_td[1]] = {
        'id': id,
        'saves': saves
      }
      
      if not id in data['players'].keys():
        print(f"Missing player with id {id}.", end="\r")
        GetPlayersAndMatches.main(int(id))
      
    #print(json.dumps(match_data, sort_keys=True, indent=4))
    
    # plays
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
      team = play.find(attrs={'tw-data': 'playerNum'})['class'][1]
      
      # players involved
      if not details_overview == None:
        try:
          player1 = int(play.find(attrs={'class': 'row'}).find(attrs={'tw-data': 'playerNum'}).text)
        except ValueError:
          player1 = 0
        for overview in details_overview:
          if overview.find(attrs={'class': 'description'}).text.lower() == "player":
            player2_name = overview.find(attrs={'class': 'label'}).text.strip()
            
            for player_num in match_data['lineup'][team]:
              if data['players'][match_data['lineup'][player_num]['id']] == player2_name:
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
      
      match_data['plays'].append({
          'time': seconds,   # time in seconds
          'action': action,  # depends on action (example: action, power play,...)
          'details': detail,
          'team': team,
          'player_1': player1,
          'player_2': player2,      # can be 0
          'location': location,     # [bottom, left] of class=tw_marker
          'target': target          # [bottom, left] of class=tw_marker
        })
  
    # save match_data to data
    data['matches'][match_id] = match_data
    
    matches += 1
    progress()
    
  #===========================================
  # Delete empty matches
  #===========================================
  for id in id_to_del:
    del data['matches'][id]
  
  
  #===========================================
  # Save results
  #===========================================
  with open(data_file_name, "w") as f:
    json.dump(data, f, sort_keys=True, indent=4)
  zipJSON.main()
  


  #===========================================
  # Close browser
  #===========================================
  browser.close()
  return
  
if __name__ == "__main__":
  try:
    main()
  except KeyboardInterrupt:
    with open(data_file_name, "w") as f:
      json.dump(data, f, sort_keys=True, indent=4)
    exit(0)