import urllib.request, json 
import pandas as pd
import numpy as np

def get_data(raw_url):
    print(f"Getting data from {raw_url}")
    with urllib.request.urlopen(raw_url) as url:
        data = json.load(url)
        #print(data)
        
    print("Data got")
    return data
    
def make_players_df(data):
    print("Making players dataset...")
    #get all player ids
    players = pd.DataFrame(columns=["player_id","player_name","team_id","position","photo"])

    for i in data["elements"]:
        data_to_append = {"player_id":i["id"], "player_name":i["web_name"], "team_id":i["team"], "position":i["element_type"],"photo":i["code"]}
        new_row = pd.DataFrame([data_to_append])

        players = pd.concat([players, new_row], ignore_index=True)

    
    print("Making teams dataset...")
    #get all team ids
    teams = pd.DataFrame(columns=["team_id","team","badge"])

    for i in data["teams"]:
        data_to_append = {"team_id":i["id"],"team":i["short_name"],"badge":i["code"]}
        new_row = pd.DataFrame([data_to_append])

        teams = pd.concat([teams, new_row], ignore_index=True)
    
    #merging team names with player df
    final_players = pd.merge(players, teams, on='team_id')
    final_players = final_players.drop(columns="team_id")
    print("Full players dataset finished")
    return final_players

def make_managers_df(managers_raw):
    print("Making managers dataset...")
    #get all transfer data
    managers_df = pd.DataFrame(columns=["manager_id","manager_short_name","manager_name","manager_team_name"])

    for i in managers_raw["league_entries"]:
            data_to_append = {"manager_id": i["entry_id"],"manager_short_name": i["short_name"],"manager_name": i["player_first_name"],"manager_team_name": i["entry_name"]}
            new_row = pd.DataFrame([data_to_append])

            managers_df = pd.concat([managers_df, new_row], ignore_index=True)
            
    print("Managers dataset finished")
    return managers_df

#function to add points. It checks if player exists, if it has a double gameweek or if it has a blank gameweek
def get_points(player_stats_ser,gw,player_id):
    points = 0

    try:
        if player_stats_ser[gw]["elements"][str(player_id)]:                    #check if player exists
            if not player_stats_ser[gw]["elements"][str(player_id)]["explain"]: #checks for a blank gameweek (if his team doesn't play)
                print(f"Blank for player {player_id} in gameweek {gw}")
            else:
                for i in player_stats_ser[gw]["elements"][str(player_id)]['explain'][0][0]:
                    points += i["points"]                                       #adds points
                if len(player_stats_ser[gw]["elements"][str(player_id)]["explain"])==2:
                    for i in player_stats_ser[gw]["elements"][str(player_id)]['explain'][1][0]:
                        points += i["points"]                                   #adds points for a double gameweek
    except KeyError:
        print(f"No data for player {player_id} in gameweek {gw}")
        return 0
    
    return points


def main(current_gw,league):
    final_data_intake = {}

    data = get_data("https://draft.premierleague.com/api/bootstrap-static")
    managers_raw = get_data(f"https://draft.premierleague.com/api/league/{league}/details")

    players_df = make_players_df(data)
    managers_df = make_managers_df(managers_raw)


    #picks: make a series of each gameweek, and the picks made by each manager per gameweek

    all_lineups_raw = pd.Series(dtype="object")

    for gw in range(1,current_gw+1):
        ser = pd.Series(dtype="object")
        for manager in managers_df["manager_id"]:
            data_to_append1 = pd.Series({manager:get_data(f"https://draft.premierleague.com/api/entry/{manager}/event/{gw}")})
            ser = pd.concat([ser, data_to_append1])
        data_to_append2 = pd.Series({gw: ser})
        new_row = pd.DataFrame([data_to_append2]).T  # Transpose the DataFrame
        
        all_lineups_raw = pd.concat([all_lineups_raw, new_row])

    all_lineups_raw.columns = ["data"]


    #get all manager picks
    picks = pd.DataFrame(columns=["player_id","squad_position","gameweek","manager_id"])

    for gw in range(1,current_gw+1):
        for manager in managers_df["manager_id"]:
            for i in all_lineups_raw.loc[gw]["data"][manager]["picks"]:
                data_to_append = {"player_id":i["element"], "squad_position":i["position"], "gameweek":gw, "manager_id":manager}
                new_row = pd.DataFrame([data_to_append])

                picks = pd.concat([picks, new_row], ignore_index=True)
    
    
    #stats: make a series of each gameweek for every player that shows their stats

    player_stats_ser = pd.Series(dtype="object")

    for gw in range(1,current_gw+1):
        data_to_append = pd.Series({gw:get_data(f"https://draft.premierleague.com/api/event/{gw}/live")})
        player_stats_ser = pd.concat([player_stats_ser, data_to_append])
    player_stats_ser[1]

    
    #get all player stats per gameweek
    player_stats = pd.DataFrame()

    for gw in range(1,current_gw+1):                                        #loop for every gameweek
        for player_id in players_df["player_id"]:                           #go through every player_id
            next_row = len(player_stats) + 1                                #create new line
            player_stats.loc[next_row,"player_id"] = player_id              #add player_id
            player_stats.loc[next_row,"gameweek"] = gw                      #add gameweek
            player_stats.loc[next_row,"points"] = get_points(player_stats_ser,gw,player_id)  #add points for that gameweek

            try:
                for key,value in player_stats_ser[gw]["elements"][str(player_id)]["stats"].items(): #get specific player
                    player_stats.loc[next_row,key] = value                  #get all the stats into df
            except KeyError:
                continue
            
    picks_stats = pd.merge(player_stats,picks,how="left",on=["player_id","gameweek"])
    akoya_df = pd.merge(picks_stats,players_df,how="left",on=["player_id"])

    akoya_df = pd.merge(akoya_df,managers_df,how="left",on=["manager_id"])

    akoya_df["manager_name"] = akoya_df["manager_name"].fillna("transfer market")
    akoya_df["bench"] = np.where(akoya_df["squad_position"]>11, 'bench', np.where(akoya_df["squad_position"]>=1, 'fielded', 'n/a'))
    akoya_df["position"] = akoya_df["position"].replace({1:"GK",2:"DEF",3:"MID",4:"FWD"})

    akoya_df = akoya_df.reindex(columns=['player_id', 'player_name','position', 'team', 'gameweek', 
            'manager_name', 'manager_short_name', 'manager_team_name', "squad_position", 'bench', 
            'points', 'minutes', 'goals_scored', 'assists','clean_sheets', 'goals_conceded', 
            'own_goals', 'penalties_saved','penalties_missed', 'yellow_cards', 'red_cards', 'saves', 'bonus',
            'bps', 'influence', 'creativity', 'threat', 'ict_index', 'total_points','in_dreamteam','photo', 'badge'])



    print("Getting transfers...")
    transfers_raw = get_data(f"https://draft.premierleague.com/api/draft/league/{league}/transactions")

    #get all transfer data
    transfers_df = pd.DataFrame(columns=["players_id_in","players_id_out","manager_id","gameweek","type","result","transfer_id"])

    for i in transfers_raw["transactions"]:
        data_to_append = {"players_id_in":i["element_in"], "players_id_out":i["element_out"], "manager_id":i["entry"], "gameweek":i["event"], "type":i["kind"], "result":i["result"], "transfer_id":i["id"]}
        new_row = pd.DataFrame([data_to_append])

        transfers_df = pd.concat([transfers_df, new_row], ignore_index=True)

    transfers_df = pd.merge(transfers_df,managers_df[["manager_id","manager_short_name"]],how="left",on=["manager_id"])

    x = pd.merge(transfers_df,players_df,how="left",left_on="players_id_in",right_on="player_id")
    transfers = pd.merge(x,players_df,how="left",left_on="players_id_out",right_on="player_id",suffixes=("_in","_out"))
    transfers = transfers.drop(columns=["player_id_in","player_id_out","position_in","position_out"])

    final_data_intake["akoya"] = akoya_df
    final_data_intake["transfers"] = transfers

    # print(final_data_intake["akoya"])
    # print(final_data_intake["transfers"])

    return final_data_intake

if __name__ == "__main__":
    main()