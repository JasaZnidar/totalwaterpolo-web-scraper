from bs4 import BeautifulSoup
import requests
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

#=======================================
# Open browser
#=======================================
options = Options()
options.add_argument("--headless")
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
  pass


#=======================================
# Close browser
#=======================================
browser.close()