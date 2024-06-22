from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

import time
from bs4 import BeautifulSoup 
import pandas as pd
import re

options = webdriver.ChromeOptions()
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")


driver = webdriver.Chrome(options=options, keep_alive=True)

starting_link_to_scrape = "http://mobile.de"
driver.get(starting_link_to_scrape)
wait = WebDriverWait(driver, 10)
time.sleep(1)
dsgvo_button = wait.until(EC.element_to_be_clickable((By.XPATH,
                                                      "//*[@id=\"mde-consent-modal-container\"]/div[2]/div[2]/div[1]/button")))

dsgvo_button.click()

Marke = wait.until(EC.presence_of_element_located((By.XPATH,
                                   "//*[@id=\"root\"]/div/div/article[1]/section/div/div[2]/div[1]/div/div/select")))

Modell = wait.until(EC.presence_of_element_located((By.XPATH,
                                   "//*[@id=\"root\"]/div/div/article[1]/section/div/div[2]/div[2]/div/div/select")))

Erstzulassung_ab = wait.until(EC.presence_of_element_located((By.XPATH,
                                   "//*[@id=\"root\"]/div/div/article[1]/section/div/div[2]/div[3]/div/div/div[2]/select")))
Kilometer_bis = wait.until(EC.presence_of_element_located((By.XPATH,
                                   "//*[@id=\"root\"]/div/div/article[1]/section/div/div[2]/div[4]/div/div/div[2]/select")))

Select(Marke).select_by_value("17200")  # Mercedes
# Select(Marke).select_by_value("4350")  # Bugatti
time.sleep(1)
# Select(Modell).select_by_value("g6")
# Select(Erstzulassung_ab).select_by_value("2024")
# Select(Kilometer_bis).select_by_value("5000")

Suche_Starten = wait.until(EC.element_to_be_clickable((By.XPATH,
                                                      "//*[@id=\"root\"]/div/div/article[1]/section/div/div[2]/button")))
Suche_Starten.click()

# Suchanfrage abgeschickt - Ab hier sind Daten geladen###############################
time.sleep(1)
links = driver.find_elements(By.CLASS_NAME, "rqEvz.FWtU1.YIC4W")
eintraege = driver.find_elements(By.TAG_NAME, "h2")
preise = driver.find_elements(By.CSS_SELECTOR, "[data-testid='price-label']")
details = driver.find_elements(By.CSS_SELECTOR, "[data-testid='listing-details-attributes']")


df = pd.DataFrame(columns=['Inserat', 'Preis', 'KM', 'Details', 'Link'])

for eintrag, preis, detail, link in zip(eintraege, preise, details, links):
    content = detail.get_attribute("outerHTML")
    soup = BeautifulSoup(content, 'html.parser')
    pattern = re.compile(r'\b\d{1,3}(\.\d{2,3})*.km\b')
    kmstand = soup.find(string=pattern)
    # pattern = re.compile(r'\d{1,3}.PS')
    # ps = soup.find(string=pattern)
    df = df._append({'Inserat': eintrag.text,
                            'Preis': preis.text,
                            'KM': kmstand.text.replace(' km', ''),
                            'Details': detail.text.replace('\n', '').replace('\r', ''),
                            'Link': link.get_attribute("href")},
                    ignore_index=True)


schleife = True
# Nächste Seite falls vorhanden############################
while schleife:
    try:
        naechste_seite = wait.until(EC.element_to_be_clickable(
            # (By.XPATH, "//*[@id=\"root\"]/div/div[7]/div[2]/article[1]/section[2]/div/div[3]/ul/li[]/button")), message='letzte Seite erreicht')
            (By.CSS_SELECTOR, "[data-testid='pagination:next']")), message='letzte Seite erreicht')
        driver.execute_script("arguments[0].scrollIntoView();", naechste_seite)
        time.sleep(1)
        naechste_seite.click()
        links = driver.find_elements(By.CLASS_NAME, "rqEvz.FWtU1.YIC4W")
        eintraege = driver.find_elements(By.TAG_NAME, "h2")
        preise = driver.find_elements(By.CSS_SELECTOR, "[data-testid='price-label']")
        details = driver.find_elements(By.CSS_SELECTOR, "[data-testid='listing-details-attributes']")

        for eintrag, preis, detail, link in zip(eintraege, preise, details, links):
            content = detail.get_attribute("outerHTML")
            soup = BeautifulSoup(content, 'html.parser')
            pattern = re.compile(r'\b\d{1,3}(\.\d{2,3})*.km\b')
            kmstand = soup.find(string=pattern)
            # pattern = re.compile(r'\d{1,3}.PS')
            # ps = soup.find(string=pattern)
            df = df._append({'Inserat': eintrag.text,
                             'Preis': preis.text,
                             'KM': kmstand.text.replace(' km', ''),
                             'Details': detail.text.replace('\n', '').replace('\r', ''),
                             'Link': link.get_attribute("href")},
                            ignore_index=True)
    except:
        df.to_csv('C:/Mobile/Bugatti_Alle.csv', index=False, sep=';', encoding='utf-16')
        schleife = False
