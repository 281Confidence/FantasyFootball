from sys import argv
from requests import get
import pandas as pd 
from bs4 import BeautifulSoup
import numpy as np

years = [i for i in range(1999, 2020)]
weeks = [i for i in range(1,18)]
yearweek = [(a,b) for a in years for b in weeks]


urlDict = {
    
}

for year, week in yearweek:
    urlDict.update( {'Passing{year}week{week}'.format(year = year, week = week) : """https://www.pro-football-reference.com/play-index/pgl_finder.cgi?request=1&match=game&year_min={year}&year_max={year}&season_start=1&season_end=-1&age_min=0&age_max=99&game_type=A&league_id=&team_id=&opp_id=&game_num_min=0&game_num_max=99&week_num_min={week}&week_num_max={week}&game_day_of_week=&game_location=&game_result=&handedness=&is_active=&is_hof=&c1stat=pass_att&c1comp=gt&c1val=1&c2stat=&c2comp=gt&c2val=&c3stat=&c3comp=gt&c3val=&c4stat=&c4comp=gt&c4val=&order_by=pass_rating&from_link=1""".format(year = year, week = week)} )
    urlDict.update( {'Receiving{year}week{week}'.format(year = year, week = week) : """https://www.pro-football-reference.com/play-index/pgl_finder.cgi?request=1&match=game&year_min={year}&year_max={year}&season_start=1&season_end=-1&age_min=0&age_max=99&game_type=A&league_id=&team_id=&opp_id=&game_num_min=0&game_num_max=99&week_num_min={week}&week_num_max={week}&game_day_of_week=&game_location=&game_result=&handedness=&is_active=&is_hof=&c1stat=rec&c1comp=gt&c1val=1&c2stat=&c2comp=gt&c2val=&c3stat=&c3comp=gt&c3val=&c4stat=&c4comp=gt&c4val=&order_by=rec_yds&from_link=1""".format(year=year, week=week)})
    urlDict.update( {'Rushing{year}week{week}'.format(year = year, week = week) : """https://www.pro-football-reference.com/play-index/pgl_finder.cgi?request=1&match=game&year_min={year}&year_max={year}&season_start=1&season_end=-1&age_min=0&age_max=99&game_type=A&league_id=&team_id=&opp_id=&game_num_min=0&game_num_max=99&week_num_min={week}&week_num_max={week}&game_day_of_week=&game_location=&game_result=&handedness=&is_active=&is_hof=&c1stat=rush_att&c1comp=gt&c1val=1&c2stat=&c2comp=gt&c2val=&c3stat=&c3comp=gt&c3val=&c4stat=&c4comp=gt&c4val=&order_by=rush_yds&from_link=1""".format(year=year, week=week)})
 

dfs = []

defColumnSettings = {
	'axis':1,
	'inplace': True
}

for key, url in urlDict.items():
	response = get(url)

	soup = BeautifulSoup(response.content, 'html.parser')

	table = soup.find('table', {'id': 'results'})

	df = pd.read_html(str(table))[0]

	df.columns = df.columns.droplevel(level=0)


	df['Home T/F'] = np.where(df['Unnamed: 7_level_1'] == '@', 'F', 'T')

	df.drop(['Lg', 'Unnamed: 7_level_1'], **defColumnSettings)
	#df.drop(['Result', 'Week', 'G#', 'Opp', 'Unnamed: 7_level_1', 'Age', 'Rk', 'Lg', 'Day'], **defColumnSettings)

	df = df[df['Pos'] != 'Pos']

	df.set_index(['Player', 'Pos', 'Age'], inplace = True)

	if 'Passing' in key:
		#df = df[['Yds', 'TD', 'Int', 'Att', 'Cmp']]
		df.rename({'Yds': 'PassingYds', 'Att': 'PassingAtt', 'Y/A': 'Y/PassingAtt', 'TD': 'PassingTD'}, **defColumnSettings)
	elif 'Receiving' in key:
		#df = df[['Rec', 'Tgt', 'Yds', 'TD']]
		#df.drop('Ctch%', **defColumnSettings)
		df.rename({'Yds': 'ReceivingYds', 'TD': 'ReceivingTD'}, **defColumnSettings)
	elif 'Rushing' in key:
		#df.drop('Y/A', **defColumnSettings)
		df.rename({'Att': 'RushingAtt', 'Yds': 'RushingYds', 'TD': 'RushingTD'}, **defColumnSettings)
	dfs.append(df)
#Joining DataFrames


df = pd.concat(dfs, join = 'outer', ignore_index = False, sort = False)
df.fillna(0, inplace = True)


fant_stats = ['PassingYds', 'PassingTD', 'Int', 'Rec', 'ReceivingYds', 'ReceivingTD', 'RushingYds', 'RushingTD']
for stats in fant_stats:
    df[stats] = df[stats].astype(str).astype('int64')

df['FantasyPoints'] = df['PassingYds']/25 + df['PassingTD']*4 - df['Int']*2 + 0.5* df['Rec'] + df['ReceivingYds']/10 + df['ReceivingTD']*6 + df['RushingYds']/10 + df['RushingTD']*6

df.reset_index(inplace=True)

print(df.head())

try:
	if argv[1] == '--save':
		df.to_csv('datasets/allstats.csv')
except IndexError:
	pass