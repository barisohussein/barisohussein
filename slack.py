from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd

driver = webdriver.Chrome('/Users/barisohussein/Downloads/chromedriver')

prices = []
beds = []
baths = []
sizes = []
addresses = []
driver.get('https://www.realtor.com/realestateandhomes-search/New-York_NY')