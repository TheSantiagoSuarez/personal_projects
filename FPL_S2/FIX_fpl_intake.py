import pandas as pd
import pickle

import FIX_fpl_methods as methods
import FIX_fpl_classes as classes


league = 41570
current_gw = 38

# Raw Data
data_raw = methods.get_data("https://draft.premierleague.com/api/bootstrap-static")
league_data_raw = methods.get_data(f"https://draft.premierleague.com/api/league/{league}/details")
player_stats_raw = pd.Series({gw: methods.get_data(f"https://draft.premierleague.com/api/event/{gw}/live") for gw in range(1, current_gw + 1)})
transfers_raw = methods.get_data(f"https://draft.premierleague.com/api/draft/league/{league}/transactions")
matches = [classes.Match(match) for match in league_data_raw["matches"] ]

#Usable Data
managers = methods.get_managers(league_data_raw["league_entries"])
players, teams = methods.get_players(data_raw)
transfers = []



print("Getting Transfers...")
for tran in transfers_raw["transactions"]:
    transfers.append(classes.Transfer(tran,players,managers))



for player in players:                                                      #go through every player
    id = player.ID
    points = {}
    for gw in range(1,current_gw+1):                                        #loop for every gameweek
            points[gw] = methods.get_player_points(player_stats_raw,gw,id)  #add POINTS for that gameweek

            try:
                for key,value in player_stats_raw[gw]["elements"][str(id)]["stats"].items(): #get specific player
                    player.stats[gw] = value                                #get all the STATS into for the gw
                    
            except KeyError:
                continue
    
    player.points = points    



for man in managers:
    # picks: for each manager, create a dictionary of dictionaries of the players picked each gameweek
    # manager.picks > GW(#) > Squad Position(#) > Player
    man.get_picks(current_gw, players)
    
    # fixtures: for each manager, create a dictionary of dictionaries of the opponent, both players points and who won each gw
    # manager.fixtures > GW(#) > W / points / opponent / opponent_points
    man.get_fixtures(matches, managers)

    # standings: 
    man.get_standings(league_data_raw["standings"],current_gw)



data = {"players":players,"managers":managers,"transfers":transfers,"teams":teams}


with open('season_data.pickle', 'wb') as handle:
    pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)
