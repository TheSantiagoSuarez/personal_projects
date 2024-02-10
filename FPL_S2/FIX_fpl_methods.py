import urllib.request
import json
import pandas as pd

import FIX_fpl_classes as classes

def get_data(raw_url):
    print(f"Getting data from {raw_url}")
    with urllib.request.urlopen(raw_url) as url:
        data = json.load(url)
        #print(data)
        
    print("Data got")
    return data

def get_managers(managers_raw):
    print("Getting all managers...")
    managers = []

    for entry in managers_raw:
        man = classes.FPLmanager(entry["entry_id"],entry["id"], entry["player_first_name"], entry["player_last_name"], entry["short_name"], entry["entry_name"])
        managers.append(man)
            
    print("All managers inputted")
    return managers

def get_manager(manager_id, managers, type = "ID"):
    for manager in managers:
        if (type == "ID") & (manager.id2 == manager_id):
            return manager
        elif manager.id2 == manager_id:
            return manager

def get_picks_points(manager, position):
    points = {}
    for gw, gw_squad in manager.picks.items():
        points[gw] = 0
        for squad_pos, pos_player in gw_squad.items():
            if squad_pos != "formation":
                squad_pos = int(squad_pos.replace("pos ",""))
                if (position != "bench") & (squad_pos <= 11):
                    if (pos_player.position == position) | (position == "total"):
                        points[gw] = points[gw] + pos_player.points[gw]         # add the player.points of that gw to the total
                elif  (position == "bench") & (squad_pos > 11):
                        points[gw] = points[gw] + pos_player.points[gw]         # add the player.points of that gw to the total
    return points



def get_matches(matches_raw):
    matches = []
    for match in matches_raw:
        matches.append(classes.Match(match))
    return match

def get_players(data):
    print("Getting all teams...")
    #get all team ids
    teams = [classes.FPLteam(team["id"], team["short_name"], team["code"]) for team in data["teams"]]

    print("Getting all players...")
    #get all player ids
    players = [classes.FPLplayer(player["id"], player["web_name"], player["team"], player["element_type"], player["code"]) for player in data["elements"]]

    # Assign players to teams based on team_id
    [player.assign_team(teams) for player in players]

    print("All players inputted")
    return players, teams

def get_player(player_id, players):
    for player in players:
        if player.ID == player_id:
            return player
        
def get_player_points(player_stats_ser,gw,player_id):
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

#Findings

def get_missed_points(manager, current_gw):
    missed_points = {}
    for gw in range(1, current_gw + 1):
        missed_points[gw] = optimise_bench(manager, gw)
    return missed_points

def optimise_bench(manager, gw):            #####change format so that we build the optimal team
    print("GW" + str(gw) + manager.name)
    gw_picks = manager.picks.get(gw)
    position_limits = [(2,3),(3,2),(4,1)]               #(position, limit)

    points = 0

    if gw_picks["pos 1"].points[gw] < gw_picks["pos 12"].points[gw]:
        points += gw_picks["pos 12"].points[gw] - gw_picks["pos 1"].points[gw]

    for b in range(13,16):
        print("pos " + str(b))
        bench_player_pts = gw_picks.get("pos " + str(b)).points.get(gw)
        print(gw_picks.get("pos " + str(b)).name + str(bench_player_pts))
        for f in range(2,12):
            print("pos " + str(f))
            field_player_pts = gw_picks.get("pos " + str(f)).points.get(gw)
            print(gw_picks.get("pos " + str(f)).name + str(field_player_pts))
            for pos in position_limits:
                if manager.picks[gw]["formation"][pos[0]-2] > pos[1]:
                    if field_player_pts < bench_player_pts:
                        points += bench_player_pts - field_player_pts
                        print("add points")
                        break # exit the inner loop and go to the next field_player
                    else:
                        continue  # only executed if the inner loop didn't break
                break  # exit the outer loop and go to the next bench_player
    
    print("total points" + str(points))
    return points

# returns a df in order of target (like points) for subtarget (like gk)
# basically, returns an ordered table of the highest points for [gk, def, mid, etc...]
def get_ranking(managers,target,subtarget=None): 
    df = pd.DataFrame(columns=["manager_short_name","manager",target])
    for manager in managers:
        manager_name = manager.name + " " + manager.lastname[0]
        if subtarget == None:
            df.loc[len(df.index)] = [manager.short_name,manager_name,manager.standings[target]]            
        elif type(manager.standings[target][subtarget]) == dict:
            df.loc[len(df.index)] = [manager.short_name,manager_name,sum(manager.standings[target][subtarget].values())]
        else:
            df.loc[len(df.index)] = [manager.short_name,manager_name,manager.standings[target][subtarget]]
    return df.sort_values(target,ascending=False).reset_index(drop=True)

def get_ranking_gw(managers, target, subtarget):
    df = pd.DataFrame(columns=["manager_short_name","manager", "gw", "points"])
    for manager in managers:
        manager_name = manager.name + " " + manager.lastname[0]
        for gw, value in manager.standings[target][subtarget].items():
            df.loc[len(df.index)] = [manager.short_name,manager_name, gw, value]            
    return df.sort_values("points",ascending=False).reset_index(drop=True)

def result_history(managers):
