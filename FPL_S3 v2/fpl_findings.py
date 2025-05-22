import pandas as pd
import pickle
from functools import reduce

import fpl_methods as methods

def main():
    current_gw = max(data["managers"][0].picks)

    managers = data["managers"]
    players = data["players"]
    transfers = data["transfers"]
    team = data["teams"]

    findings = {}

    # colllapse the sections with the different regions

    # region Points Standings

    # ranks each manager by all these statistics, in the whole season, and single gameweek
    ranking_targets = ["total", "gk", "def", "mid", "fwd", "bench", "missed", "points_against", "points_difference"]
    for target in ranking_targets:
        findings[target + " gw"] = methods.get_ranking_gw(managers,"points",target)
        
        findings[target] = methods.get_ranking(managers,"points",target)

    # ranks each manager by general standings statistics
    standing_fields = ["h2h_points","wins","draws","losses"]
    for field in standing_fields:
        findings[field] = methods.get_ranking(managers,field)

    h2h_points = findings["h2h_points"]
    wins = findings["wins"]
    draws = findings["draws"]
    losses = findings["losses"]
    points = findings["total"]

    data_frames = [h2h_points, wins, draws, losses, points]
    findings["standings"] = reduce(lambda left, right: pd.merge(left, right, on=['manager_short_name', 'manager']), data_frames)

    # endregion

    # region Points Streaks

    # getting the gw points for each manager
    gw_points = pd.DataFrame(columns=["gw","manager","points"])
    for gw in range(1,current_gw+1):
        for manager in managers:
            points = manager.fixtures[gw]["points"]
            manager = manager
            gw_points.loc[gw_points.shape[0]] = {"gw":gw,"manager":manager,"points":points}
        
        gw_points.loc[gw_points["gw"]==gw,"rank"] = gw_points.loc[gw_points["gw"]==gw,"points"].rank(ascending=False,method="min")

    # calculating the longest streak without being in the top 3 of the gw for each manager
    for manager in managers:
        counter = 0
        tottenham = 0
        streak = ""
        for indx, row in gw_points[(gw_points["manager"]==manager)].iterrows():
            if row["rank"]>3:
                counter += 1
                if counter > tottenham:
                    tottenham = counter
                    start = row["gw"]-tottenham+1
                    end = row["gw"]
                    streak = f"{start} - {end}"
            else:
                counter = 0

        # calculating how many times each manager has finished 1st, 2nd, 3rd, and last in a gw
        manager.podiums["1st"] = len(gw_points[(gw_points["manager"]==manager)&(gw_points["rank"]==1)])
        manager.podiums["2nd"] = len(gw_points[(gw_points["manager"]==manager)&(gw_points["rank"]==2)])
        manager.podiums["3rd"] = len(gw_points[(gw_points["manager"]==manager)&(gw_points["rank"]==3)])
        manager.podiums["last"] = len(gw_points[(gw_points["manager"]==manager)&(gw_points["rank"]==14)])
        manager.podiums["tottenham"] = (tottenham,streak)

        podiums = pd.DataFrame(columns=["manager","1st","2nd","3rd","last","tottenham","streak"])
        for manager in managers:
            podiums.loc[podiums.shape[0]] = {"manager":manager.name + manager.lastname[0],"1st":manager.podiums["1st"],"2nd":manager.podiums["2nd"],"3rd":manager.podiums["3rd"],"last":manager.podiums["last"],"tottenham":manager.podiums["tottenham"][0],"streak":manager.podiums["tottenham"][1]}

        findings["streaks"] = podiums

    # endregion

    # region H2H

    # making the table to calculate the best and worst head to heads for each manager
    h2h_df = pd.DataFrame(columns=["gw","manager","result","points", "opponent","opponent_points"])

    for manager in managers:
        for gw, match in manager.fixtures.items():
            match["manager"] = manager.short_name
            match["gw"] = int(gw)
            h2h_df.loc[h2h_df.shape[0]] = match
            
    h2h_df["point_diff"] = h2h_df["points"] - h2h_df["opponent_points"]

    findings["h2h"] = h2h_df

    # endregion

    # region Draft

    # creating the table to rank the best and worst draft picks
    draft_picks_df = pd.DataFrame(columns=["manager_short","manager","player","pick","pts","gws"])
    for pick in range(1,16):
        for manager in managers:
            player = manager.draft_picks[pick]
            gws = 0
            points = 0
            for gw, squad in manager.picks.items():
                for pos in range(1,12):
                        if squad["pos "+str(pos)] == player:
                            gws += 1
                            points += player.points[gw]
            draft_picks_df.loc[draft_picks_df.shape[0]] = {"manager_short":manager.short_name,"manager":manager.name,"player":player.name,"pick":pick,"pts":points,"gws":gws}
    findings["draft_picks"] = draft_picks_df.sort_values("pts",ascending=False)

    # endregion

    # region Stats

    # ranks each manager by each one of these stats, good or bad
    targets = ["goals_scored","assists","clean_sheets","goals_conceded","own_goals","penalties_saved","penalties_missed",
          "yellow_cards","red_cards","saves","bonus","in_dreamteam"]

    for target in targets:
        findings[target] = methods.get_stat_ranking(managers, target)
        

    # endregion

    # region Players
    player_findings = {}

    # Loyalty and Disappointments - Players who have stayed the most and least with each manager
    
    loyalty_df = pd.DataFrame(columns=["manager_short","manager","player","pos","team","pts","gw"])
    for manager in managers:
        for gw, squad in manager.picks.items():
            for pos in range(1,16):
                player = squad["pos "+str(pos)]
                loyalty_df.loc[loyalty_df.shape[0]] = {"manager_short":manager.short_name,"manager":manager.name,"pos":pos,"player":player.ID,"team":player.team.name,"pts":player.points[gw],"gw":gw}
    fielded = loyalty_df[loyalty_df["pos"]<=11]
    player_findings["loyalty"] = loyalty_df.groupby(["manager_short","manager","player"])["gw"].count().sort_values()
    
    # Joao Felix Award - Players who have played for the most different managers
    # Club Mascot - The team each manager has fielded the most
    # Star Players - The players with most points for each manager

    # endregion

    # region Transfers

    # Most Transfers - ranking what manager was most active in the transfer market
    # Love/hate relationship - ranking what player was most transferred in repeatedly by a single manager
    # Best and Worst Transfers

    # endregion


if __name__ == "__main__":
    with open ('season_data.pickle','rb') as file:
        data = pickle.load(file)

    findings = main(data)