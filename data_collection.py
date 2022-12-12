import pandas as pd
from bs4 import BeautifulSoup
import requests

years = [1930, 1934, 1938, 1950, 1954, 1958, 1962, 1966, 1970, 1974, 1978, 1982, 1986, 1990, 1994, 1998, 2002, 2006, 2010, 2014, 2018]

def get_matches(year):
    link = f'https://en.wikipedia.org/wiki/{year}_FIFA_World_Cup'
    response = requests.get(link)
    content = response.text
    soup = BeautifulSoup(content, 'lxml')

    matches = soup.find_all('div', class_='footballbox')

    home = list()
    score = list()
    away = list()

    for match in matches:
        home.append(match.find('th', class_='fhome').get_text())
        score.append(match.find('th', class_='fscore').get_text())
        away.append(match.find('th', class_='faway').get_text())

    dict_football = {'home': home, "score":score, 'away': away}
    df_football = pd.DataFrame(dict_football)
    df_football['year'] = year
    df_football['home'] = df_football['home'].str.strip()
    df_football['away'] = df_football['away'].str.strip() 

    return df_football

historical = [get_matches(year) for year in years]
df_historical = pd.concat(historical, ignore_index=True)

# Historical Data Cleaning
df_historical.drop(index=37, inplace=True)
df_historical['score'] = df_historical['score'].str.replace('[^\d–]', '', regex=True)
df_historical[['Home Goals', 'Away Goals']] = df_historical['score'].str.split('–', expand=True)
df_historical = df_historical.astype({'Home Goals': int, 'Away Goals': int})
df_historical['Total Goals'] = df_historical['Home Goals'] + df_historical['Away Goals']

df_historical.to_csv("worldcup_historical_data.csv", index=False)

df_current = get_matches(2022)
df_current.to_csv('worldcup_current_data.csv', index=False)