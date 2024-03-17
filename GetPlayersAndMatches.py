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
from constants import *

data = {}

def main(id = -1):
  global data
  
  #===========================================
  # Variables and functions
  #===========================================
  try:
    with open(data_file_name, "r") as f:
      data = json.load(f)
  except FileNotFoundError:
    data = {
      'players': {},
      'matches': {},
      "last checked": 0
    }
  except json.decoder.JSONDecodeError:
    data = {
      'players': {},
      'matches': {},
      "last checked": 0
    }
  progress_bar = True
  number_of_players = 300
  player_id_start = data['last checked'] + 1
  player_id_limit = player_id_start + number_of_players
  player_id = player_id_start
  
  if id >= 0:
    progress_bar = False
    number_of_players = 1
    player_id_start = id
    player_id_limit = id + 1
    player_id = id
  
  def player_url(id: int):
    return f"https://total-waterpolo.com/tw_player/{id}"

  def player_progress(complete=False):
    if complete:
      num = player_id + 1
    else:
      num = player_id
    
    if progress_bar:
      comp_prog = int((num - player_id_start)*100 // number_of_players)
      comp_perc = (num - player_id_start)*100 / number_of_players
      print(f"Players [{player_id}]: |{'█' * comp_prog}{'-' * (100 - comp_prog)}| {comp_perc:.1f}% Complete", end="\r")


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
  player_progress()
    
  while player_id < player_id_limit:
    try:
      browser.get(player_url(player_id))
    except TimeoutException:
      # URL timed out
      data['last checked'] = player_id
      player_id += 1
      player_progress()
      continue
    
    try:
      player_progress()
      # wait for loading to dissappear
      WebDriverWait(browser, wait_time[0]).until(EC.invisibility_of_element((By.XPATH, '//*[@id="nav-stats"]/div[2]')))
      # wait a few seconds for player stats (name, position, hand, height, weight) to load
      WebDriverWait(browser, wait_time[1]).until_not(EC.text_to_be_present_in_element((By.XPATH, "//*[@id=\"Wrapper\"]/div[2]/div[2]/div[1]/div[2]/div[1]"), " - "))
      WebDriverWait(browser, wait_time[1]).until_not(EC.text_to_be_present_in_element((By.XPATH, "//*[@id=\"Wrapper\"]/div[2]/div[2]/div[2]/div[1]/div/div[2]/div[2]"), "-"))
      WebDriverWait(browser, wait_time[1]).until_not(EC.text_to_be_present_in_element((By.XPATH, "//*[@id=\"Wrapper\"]/div[2]/div[2]/div[2]/div[2]/div/div[2]/div[2]"), "-"))
      WebDriverWait(browser, wait_time[1]).until_not(EC.text_to_be_present_in_element((By.XPATH, "//*[@id=\"Wrapper\"]/div[2]/div[2]/div[3]/div[1]/div/div[2]/div[2]"), "-"))
      WebDriverWait(browser, wait_time[1]).until_not(EC.text_to_be_present_in_element((By.XPATH, "//*[@id=\"Wrapper\"]/div[2]/div[2]/div[3]/div[2]/div/div[2]/div[2]"), "-"))
    except TimeoutException:
      if id == -1:
        # player has no statistics, probably not a player
        data['last checked'] = player_id
        player_id += 1
        player_progress()
        continue
    
    try:
      num = [0, len(WebDriverWait(browser, wait_time[1]).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "tw_match_basic"))))]
      while num[1] > num[0]:
        num[0] = num[1]
        num[1] = len(WebDriverWait(browser, wait_time[1]).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "tw_match_basic"))))
    except TimeoutException:
      data['last checked'] = player_id
      player_id += 1
      player_progress()
      continue

    # get player data
    player_soup = BeautifulSoup(browser.page_source, "html.parser")
    
    try:
      player_position = player_soup.find(attrs={'tw-data': "position"}).text
    except AttributeError:
      player_position = ''
    try:
      player_hand = player_soup.find(attrs={'tw-data': "hand"}).text
    except AttributeError:
      player_hand = ''
    try:
      player_height = int(player_soup.find(attrs={'tw-data': "height"}).text)
    except ValueError:
      player_height = 0
    try:
      player_weight = int(player_soup.find(attrs={'tw-data': "weight"}).text)
    except ValueError:
      player_weight = 0
    try:
      player_birth = days(player_soup.find(attrs={'tw-data': "birthday"}).text)
    except ValueError:
      player_birth = 0
      
    
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
      data['last checked'] = player_id
      player_id += 1
      player_progress()
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
      
    player_progress(True)
    data['last checked'] = player_id
    player_id += 1

  if progress_bar:
    print(f"\n\nplayers: {len(data['players'])}\nmatches: {len(data['matches'])}")


  #===========================================
  # Save results
  #===========================================
  with open(data_file_name, "w") as f:
    json.dump(data, f, sort_keys=True, indent=4)


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
    print(f"\n\nplayers: {len(data['players'])}\nmatches: {len(data['matches'])}")
    exit(0)