from bs4 import BeautifulSoup
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

#===========================================
# Open browser
#===========================================
options = Options()
options.add_argument("--headless")
chrome_service = Service(ChromeDriverManager().install())
browser = Chrome(service=chrome_service, options=options)


#===========================================
# Find all competition on home page
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
  for competition in nation.findAll('li'):
    matches[competition.span.text] = {'url': competition.a['href']}


#===========================================
# Find all match URLs from competition page
#===========================================
for comp in matches:
  browser.get(matches[comp]['url'])
  
  WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "tw_competition_round")))
  
  comp_soup = BeautifulSoup(browser.page_source, "html.parser")
  for round in comp_soup.find_all(attrs={'class': 'tw_competition_round'}):
    match_link = round.find(attrs={'class': 'match-link'})
    if not match_link == None:
      matches[comp][round['tw_round_id']] = f"{home_url}{match_link['href']}"


#===========================================
# Get players
#===========================================
# wait for id="nav-startlist"
# players in divs id=f"{[home, away, ref]}Players"


#===========================================
# Get plays
#===========================================
# wait for id="nav-playbyplay"
# play in div id=f"play-by-play-q{quarter}"


#===========================================
# Close browser
#===========================================
browser.close()