from bs4 import BeautifulSoup
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
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
# Find all national competition on home page
#===========================================
home_url = "https://total-waterpolo.com"
matches = {}

# load home page
home_dropdown_id = "mfn-megamenu-ul-900"
browser.get(home_url)
home_soup = BeautifulSoup(browser.page_source, "html.parser")

# find "National" column in "Result" dropdown menu
home_result_national_column = home_soup.find(attrs={'id': home_dropdown_id})
for nation in home_result_national_column.findAll('li'):
  for match in nation.findAll('li'):
    matches[match.span.text] = {'url': match.a['href']}


#===========================================
# Find all match URLs from competition page
#===========================================
for match in matches:
  browser.get(matches[match]['url'])
  WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "tw_competition_round")))
  
  match_soup = BeautifulSoup(browser.page_source, "html.parser")
  matches[match]['rounds'] = {}
  for round in match_soup.find_all(attrs={'class': 'tw_competition_round'}):
    match_link = round.find(attrs={'class': 'match-link'})
    if not match_link == None:
      matches[match]['rounds'][round['tw_round_id']] = {'url': f"{home_url}{match_link['href']}"}


#===========================================
# Get players
#===========================================
for match in matches:
  for round in matches[match]['rounds']:
    browser.get(matches[match]['rounds'][round]['url'])
    WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "tw_match_player")))
    
    round_soup = BeautifulSoup(browser.page_source, "html.parser")
    matches[match]['rounds'][round]['lineup'] = {}
    for team in ["home", "away"]:
      matches[match]['rounds'][round]['lineup'][team] = []
      for player in round_soup.find(attrs={'id': f"{team}Players"}).find_all(attrs={'class': 'tw_match_player'}):
        matches[match]['rounds'][round]['lineup'][team].append({
          'number': int(player.find(attrs={'tw-data': 'playerNum'}).text.strip()),
          'name': player.find(attrs={'tw-data': 'playerName'}).text.strip(),
          'id': int(player['tw-player-id'])
        })


#===========================================
# Get plays
#===========================================
# wait for id="nav-playbyplay"
# play in div id=f"play-by-play-q{quarter}"


#===========================================
# Close browser
#===========================================
browser.close()
print(json.dumps(matches, sort_keys=True, indent=4))