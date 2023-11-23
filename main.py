from bs4 import BeautifulSoup
import requests
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

#=======================================
# Open browser
#=======================================
options = Options()
#options.add_argument("--headless")
chrome_service = Service(ChromeDriverManager().install())
browser = Chrome(service=chrome_service, options=options)


#=======================================
# Find all competition on home page
#=======================================
home_url = "https://total-waterpolo.com"
competitions = {}

# load home page
home_dropdown_id = "mfn-megamenu-ul-900"
browser.get(home_url)
home_soup = BeautifulSoup(browser.page_source, "html.parser")

# find "National" column in "Result" dropdown menu
home_result_national_column = home_soup.find(attrs={'id': home_dropdown_id})
for nation in home_result_national_column.findAll('li'):
  for competition in nation.findAll('li'):
    competitions[competition.span.text] = {'url': competition.a['href']}


#=======================================
# Find all match URLs from competition page
#=======================================
for comp in competitions:
  browser.get(competitions[comp]['url'])
  
  WebDriverWait(browser, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "tw_competition_round")))
  
  comp_soup = BeautifulSoup(browser.page_source, "html.parser")
  print(comp_soup.find(attrs={'tw_round_id': 'Round 10'}).prettify())
  break
  #for a in comp_soup.find('main').find('section').find_all(attrs={'class': 'mcb-wrap-inner'}):
  #  print(a.prettify())
  # wait in id bellow for class tw_info_text to load
  print(comp_soup.find(attrs={'id': 'first_match_loader'}).prettify())
  break


#=======================================
# Close browser
#=======================================
browser.close()