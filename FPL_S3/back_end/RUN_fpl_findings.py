import pandas as pd
import pickle
from functools import reduce

import fpl_methods as methods
import fpl_data_intake

def main(data):
    managers = data["managers"]
    players = data["players"]
    transfers = data["transfers"]
    team = data["teams"]

    findings = {}
    current_gw = max(managers[0].picks)

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
    findings["standings"] = reduce(lambda left, right: pd.merge(left, right, on=['manager_short', 'manager']), data_frames)

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
        manager.podiums["Total"] = manager.podiums["1st"]+manager.podiums["2nd"]+manager.podiums["3rd"]
        manager.podiums["last"] = len(gw_points[(gw_points["manager"]==manager)&(gw_points["rank"]==14)])
        manager.podiums["tottenham"] = (tottenham,streak)

    podiums = pd.DataFrame(columns=["manager_short","1st","2nd","3rd","Total","last","tottenham","streak"])
    for manager in managers:
        podiums.loc[podiums.shape[0]] = {"manager_short":manager.short_name,"1st":manager.podiums["1st"],"2nd":manager.podiums["2nd"],"3rd":manager.podiums["3rd"],"Total":manager.podiums["Total"],"last":manager.podiums["last"],"tottenham":manager.podiums["tottenham"][0],"streak":manager.podiums["tottenham"][1]}

    findings["streaks"] = podiums

    # endregion

    # region Draft H2H

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

    # region Draft Picks

    # creating the table to rank the best and worst draft picks
    draft_picks_df = pd.DataFrame(columns=["manager_short","player","pick","points","gws"])
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
            draft_picks_df.loc[draft_picks_df.shape[0]] = {"manager_short":manager.short_name,"player":player.ID,"pick":pick,"points":points,"gws":gws}
    findings["draft_picks"] = draft_picks_df.sort_values("points",ascending=False)

    # endregion

    # region Stats

    # ranks each manager by each one of these stats, good or bad
    stats = []
    targets = ["goals_scored","assists","clean_sheets","goals_conceded","own_goals","penalties_saved","penalties_missed",
          "yellow_cards","red_cards","saves","bonus","in_dreamteam"]

    for target in targets:
        stats.append(methods.get_stat_ranking(managers, target))
    findings["stats"] = pd.concat([stats[0].iloc[:,:1]]+[df.iloc[:,-1]for df in stats],axis=1)
        

    # endregion

    # region Players
    player_findings = {}

    # Loyalty and Disappointments - Players who have stayed the most and least with each manager

    owned_df = pd.DataFrame(columns=["manager_short","player","pos","team","points","gw"])
    for manager in managers:
        for gw, squad in manager.picks.items():
            for pos in range(1,16):
                player = squad["pos "+str(pos)]
                owned_df.loc[owned_df.shape[0]] = {"manager_short":manager.short_name,"pos":pos,"player":player.ID,"team":player.team.name,"points":player.points[gw],"gw":gw}
    fielded = owned_df[owned_df["pos"]<=11]
    player_findings["loyalty"] = owned_df.groupby(["manager_short","player"]).agg(gw=("gw", "count"), points=("points", "sum")).reset_index()
    
    # Joao Felix Award - Players who have played for the most different managers

    player_findings["joao felix"] = owned_df[["player", "manager_short"]].drop_duplicates().groupby("player").agg(count=("manager_short", "count")).sort_values("count",ascending=False).reset_index()

    # Club Mascot - The team each manager has fielded the most
    
    club_mascot = fielded.groupby(["manager_short", "team"]).agg(points=("points", "sum"), count=("points", "count")).reset_index()
    player_findings["club mascot"] = club_mascot
    player_findings["season ticket"] = club_mascot.loc[club_mascot.groupby("team")["count"].idxmax()].sort_values("points", ascending=False)
    
    # Star Players - The players with most points for each manager

    star = fielded.groupby(["manager_short","player"]).agg(
        gws=('gw', 'count'),
        points=("points", 'sum')
    ).sort_values("points",ascending=False).reset_index()
    star["ppg"] = round(star["points"]/star["gws"],2)
    player_findings["star"] = star[star["gws"]>=5]

    findings["players"] = player_findings
    # endregion

    # region Transfers
    transfer_findings = {}

    # Most Transfers - ranking what manager was most active in the transfer market

    transfers_df = pd.DataFrame(columns=["manager_short","num_transfers"])
    for transfer in transfers:
        man = transfer.manager
        if transfer.result == "a":
            transfers_df.loc[transfers_df.shape[0]] = {"manager_short":man.short_name,"num_transfers": transfer.result}

    transfers_df = transfers_df.groupby(["manager_short"]).count().reset_index()
    transfer_findings["total transfers"] = transfers_df.sort_values("num_transfers", ascending=False).reset_index(drop=True)

    # Love/hate relationship - ranking what player was most transferred in repeatedly by a single manager

    love_hate = pd.DataFrame(columns=["manager_short","player","player_name","num_transfers"])
    for man in managers:
        for tran in man.transfers:
            if tran.result == "a":
                if tran.player_in.ID in love_hate["player"].values:
                    love_hate.loc[love_hate["player"] == tran.player_in.ID,"num_transfers"] += 1
                else:
                    love_hate.loc[love_hate.shape[0]] = {"manager_short":man.short_name,"player":tran.player_in.ID,"player_name":tran.player_in.name, "num_transfers": 1}

    transfer_findings["love hate"] = love_hate.loc[love_hate["num_transfers"]>1].sort_values("num_transfers",ascending=False).reset_index(drop=True)

    # Best and Worst Transfers

    best_worst = pd.DataFrame(columns=["manager_short","gameweek","player","player_name","player_out","player_out_name","gws","in_pts","out_pts","pts_gain"])
    for man in managers:                                            # for every manager
        for tran in man.transfers:                                  # for every one of their transfers
            in_pts = 0
            out_pts = 0
            gws = 0

            if tran.result == "a":                                  # for every accepted transfer
                tran_gw = tran.gameweek
                player_in = tran.player_in
                player_out = tran.player_out

                for gw in range(tran_gw,min(tran_gw+3,current_gw)): # for the next three gws after the transfer
                    position = 0
                    for pos, player in man.picks[gw].items():       # check all the players in the manager's 11
                        position += 1
                        if position <= 15:
                            if player == player_in:
                                gws += 1
                                in_pts += player.points[gw]
                                out_pts += player_out.points[gw]
                row = {"manager_short":man.short_name, "gameweek":tran_gw,"player":player_in.ID,"player_name":player_in.name, "player_out":player_out.ID,"player_out_name":player_out.name,"gws":gws,"in_pts":in_pts,"out_pts":out_pts,"pts_gain":in_pts-out_pts}
                best_worst.loc[best_worst.shape[0]] = row

    transfer_findings["best worst"] = best_worst.sort_values("pts_gain")

    findings["transfers"] = transfer_findings    
    # endregion
    
    return findings


if __name__ == "__main__":
    gw = 38
    league = 2387
    with open('season_data.pickle','rb') as file:
        data = pickle.load(file)

    data = fpl_data_intake.main(league, gw)

    findings = main(data)

    with open('season_findings.pickle', 'wb') as handle:
        pickle.dump(findings, handle, protocol=pickle.HIGHEST_PROTOCOL)