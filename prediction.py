import pandas as pd
from scipy.stats import poisson
import re
import matplotlib.pyplot as plt
import os


df_historical = pd.read_csv('worldcup_historical_data.csv', index_col=False)
df_current = pd.read_csv('worldcup_current_data.csv', index_col=False)

# team strength
df_home = df_historical[['home', 'Home Goals', 'Away Goals']]
df_away = df_historical[['away', 'Home Goals', 'Away Goals']]

df_home = df_home.rename(columns={'home':'Team', 'Home Goals': 'Goals Scored', 'Away Goals': 'Goals Conceded'})
df_away = df_away.rename(columns={'away':'Team', 'Home Goals': 'Goals Conceded', 'Away Goals': 'Goals Scored'})

df_team_strength = pd.concat([df_home, df_away], ignore_index=True).groupby(['Team']).mean()

def teams_bar(df_team, savename):
    teams = list(df_team.index)
    strength = list(df_team['Goals Scored'] * df_team['Goals Conceded'])
    z = plt.figure()
    z.set_figwidth(20)
    z.set_figheight(10)
    plt.bar(teams, strength)
    plt.xticks(fontsize = 5, rotation=90)
    plt.title('World Cup Team Historical Performance Rating')
    plt.savefig(savename, dpi=800)
    plt.close()
    
savename_perf = os.path.basename('performance')
teams_bar(df_team_strength, savename_perf)

draw_percs = list()
home_percs = list()
away_percs = list()
df_prob = dict()
# predict points
def predict_points(home, away):
    if home in df_team_strength.index and away in df_team_strength.index:
        # goals_scored * goals_conceded
        lamb_home = df_team_strength.at[home,'Goals Scored'] * df_team_strength.at[away,'Goals Conceded']
        lamb_away = df_team_strength.at[away,'Goals Scored'] * df_team_strength.at[home,'Goals Conceded']
        prob_home, prob_away, prob_draw = 0, 0, 0
        for x in range(0,11): #number of goals home team
            for y in range(0, 11): #number of goals away team
                p = poisson.pmf(x, lamb_home) * poisson.pmf(y, lamb_away)
                if x == y:
                    prob_draw += p
                    perc_draw = "{:.2f}".format(prob_draw*100)
                elif x > y:
                    prob_home += p
                    perc_home = "{:.2f}".format(prob_home*100)
                else:
                    prob_away += p
                    perc_away = "{:.2f}".format(prob_away*100)
                
        points_home = 3 * prob_home + prob_draw
        points_away = 3 * prob_away + prob_draw
        return (points_home, points_away, perc_home, perc_away, perc_draw)
    else:
        return (0, 0)

df_current_semi = df_current[60:62].copy()
df_current_final = df_current[62:].copy()

def get_winner(df_current_updated):
    for index, row in df_current_updated.iterrows():
        home, away = row['home'], row['away']
        points_home, points_away, perc_home, perc_away, perc_draw = predict_points(home, away)
        if points_home > points_away:
            winner = home
            loser = away
        else:
            winner = away
            loser = home
        df_current_updated.loc[index, 'winner'] = winner
        df_current_updated.loc[index, 'loser'] = loser
        df_current_updated.loc[index, 'Home Winning'] = perc_home
        df_current_updated.loc[index, 'Away Winning'] = perc_away
        df_current_updated.loc[index, 'Draw'] = perc_draw

    return df_current_updated

df_current_semi = get_winner(df_current_semi)

def update_table(df_current_4, df_current_2):
    for index, row in df_current_4.iterrows():
        winner = df_current_4.loc[index, 'winner']
        loser = df_current_4.loc[index, 'loser']
        match = df_current_4.loc[index, 'score']
        df_current_2.replace({f'Winners {match}':winner}, inplace=True)
        df_current_2.replace({f'Losers {match}':loser}, inplace=True)
    return df_current_2

update_table(df_current_semi, df_current_final)

def final_pie(df_current,savename):
    home = df_current.loc['home']
    away = df_current.loc['away']
    labels = [f'{home}', f'{away}', 'Draw']
    colors = ['lightblue', 'darkred', 'grey']
    sizes = [df_current['Home Winning'], df_current['Away Winning'], df_current['Draw']]

    plt.figure()
    plt.pie(sizes, labels=labels, colors=colors, startangle=90, autopct='%1.1f%%')
    plt.axis('equal')
    plt.title('2022 World Cup Finals')
    plt.savefig(savename)
    plt.close()
    

df_current_final = get_winner(df_current_final)
df_champion = df_current_final.iloc[1]
savename_final = os.path.basename('finals')
final_pie(df_champion, savename_final)
print(f"The winner of the 2022 World Cup is predicted to be {df_champion['winner']}. Congratulations!")