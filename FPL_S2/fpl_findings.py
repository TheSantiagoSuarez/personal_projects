import pandas as pd
import math

import fpl_data_intake

def get_ranking(df,bench,goal,index="reset"):
    filtered = df[(df["manager_name"]!="transfer market")&(df["bench"]==bench)]
    ranked_df = filtered.groupby(["manager_short_name","manager_name"])
    ranked_df = ranked_df[goal].sum().sort_values(ascending=False).to_frame()
    if index == "index":
        return ranked_df.rename(columns={'manager_short_name': 'manager'})
    else:    
        return ranked_df.reset_index().rename(columns={'manager_short_name': 'manager'})

def get_ranking_gw(df):
    filtered = df[(df["manager_name"]!="transfer market")&(df["bench"]=="fielded")]
    ranked_df = filtered.groupby(["manager_short_name","manager_name","gameweek"])
    ranked_df = ranked_df["points"].sum().sort_values(ascending=False).to_frame()
    return ranked_df.reset_index().rename(columns={'manager_short_name': 'manager'})

def gameweek_df(data):
    grouped = data.groupby(["manager_short_name","manager_name","gameweek"])["points"].sum()
    gameweek_df = grouped.reset_index()
    return gameweek_df

def optimise(data, gw,manager):
    benched = data[(data["gameweek"] == gw)&(data["manager_short_name"] == manager)&(data["bench"] == "bench")]
    fielded = data[(data["gameweek"] == gw)&(data["manager_short_name"] == manager)&(data["bench"] == "fielded")]

    points = 0

    positions = [("DEF",3),("MID",2),("FWD",1)]

    b_gk = benched[benched["position"] == "GK"]
    f_gk = fielded[fielded["position"] == "GK"]

    if  f_gk.loc[f_gk.index.tolist()[0],"points"] < b_gk.loc[b_gk.index.tolist()[0],"points"]:
        points += b_gk["points"].item() - f_gk["points"].item()
        benched = benched.drop(index=b_gk.index)

    for indx, b_player in benched.iterrows():
        for pos in positions:
            for indx2, f_player in fielded.iterrows():
                if len(fielded[fielded["position"] == pos[0]]) > pos[1]:
                    if f_player["points"] < b_player["points"]:
                        points += b_player["points"] - f_player["points"]
                        benched = benched.drop(index=indx)
                        fielded = fielded.drop(index=indx2)
                        break  # exit the inner loop and go to the next b_player
            else:
                continue  # only executed if the inner loop didn't break
            break  # exit the outer loop and go to the next b_player

    return points

def missed_points(data, managers, gw):
    missed_points = pd.DataFrame(columns=["manager","manager_name","gameweek","missed_pts"])

    for manager in managers:
        for gw in range(1,gw+1):
            manager_name = data[data["manager_short_name"]==manager]["manager_name"].mode()[0]
            data_to_append = {"manager":manager,"manager_name":manager_name,"gameweek":gw,"missed_pts":optimise(data, gw,manager)}
            new_row = pd.DataFrame([data_to_append])
            missed_points = pd.concat([missed_points, new_row], ignore_index=True)

    missed_points_grouped = missed_points.groupby(["manager","manager_name"])
    missed_points_grouped["missed_pts"].sum().sort_values(ascending=False)
    bench_best = missed_points_grouped["missed_pts"].sum().sort_values(ascending=False).to_frame()
    bench_best = bench_best.reset_index().rename(columns={'missed_pts': 'points'})
    return bench_best
    
def podiums(gameweeks_df):
    gw_podiums = pd.DataFrame(columns=["manager","manager_name","gameweek","points"])

    gw_podiums["manager"] = gameweeks_df["manager_short_name"]
    gw_podiums["manager_name"] = gameweeks_df["manager_name"]
    gw_podiums["gameweek"] = gameweeks_df["gameweek"]
    gw_podiums["points"] = gameweeks_df["points"]
    gw_podiums["rank"] = gw_podiums.groupby("gameweek")["points"].rank(ascending=False).apply(math.floor)
    gw_podiums["podium"] = gw_podiums["rank"]<4

    total_podiums_df = pd.DataFrame(index=['1st', '2nd', '3rd'], columns=gw_podiums["manager"].unique())

    grouped = gw_podiums.groupby(["manager", 'rank']).size()

    # loop through each manager and count their 1st, 2nd, and 3rd place finishes
    for manager in total_podiums_df.columns:
        try:
            total_podiums_df.loc['1st', manager] = grouped[manager, 1]
        except KeyError:
            total_podiums_df.loc['1st', manager] = 0
        try:
            total_podiums_df.loc['2nd', manager] = grouped[manager, 2]
        except KeyError:
            total_podiums_df.loc['2nd', manager] = 0
        try:
            total_podiums_df.loc['3rd', manager] = grouped[manager, 3]
        except KeyError:
            total_podiums_df.loc['3rd', manager] = 0

    total_podiums_df.loc['Total'] = total_podiums_df.sum(axis=0)

    total_podiums_df = total_podiums_df.transpose()
    total_podiums_df = total_podiums_df.reset_index().rename(columns={"index":"manager"})
    total_podiums_df = total_podiums_df.merge(gw_podiums[["manager","manager_name"]],left_on="manager",right_on="manager")
    return total_podiums_df.drop_duplicates().reset_index(drop=True), gw_podiums

def longest_streak(df,who):
    current_streak = 1
    max_streak = 1
    indx = 0
    
    df = df[df["manager"]==who]
    
    series = df["podium"]

    for i in range(1, len(series)):
        if series.iloc[i]:
            max_streak = max(max_streak, current_streak)
            current_streak = 1
        else:
            current_streak += 1
            if current_streak > max_streak:
                indx = i

    return max(max_streak, current_streak),df.iloc[indx]["manager"]

def tottenham(managers, gw_podiums):
    longest_nopodium_streak = (0,"")
    tottenham = pd.DataFrame(columns=["manager_name","streak_length"])

    for manager in managers:
        manager_name = gw_podiums[gw_podiums["manager"]==manager]["manager_name"].mode()[0]
        streak = longest_streak(gw_podiums, manager)
        
        tottenham.loc[manager,"manager_name"] = manager_name
        if longest_nopodium_streak[0] < streak[0]:
            longest_nopodium_streak = streak
        tottenham.loc[manager,"streak_length"] = streak[0]
        
    tottenham = tottenham.sort_values(by="streak_length",ascending=False)
    return tottenham.reset_index().rename(columns={'index': 'manager'})

def gw_losers(gw_podiums):
    last_df = pd.DataFrame(index=["Last"], columns=gw_podiums["manager"].unique())

    last_grouped = gw_podiums.groupby(["manager", 'rank']).size()

    # loop through each manager and count their last place finishes
    for manager in last_df.columns:
        try:
            last_df.loc['Last', manager] = last_grouped[manager, len(last_df.columns)]
        except KeyError:
            last_df.loc['Last', manager] = 0


    last_df = last_df.transpose().sort_values(by="Last",ascending=False)
    last_df = last_df.reset_index().rename(columns={'index': 'manager'})
    last_df = last_df.merge(gw_podiums[["manager","manager_name"]],left_on="manager",right_on="manager")
    return last_df.drop_duplicates().reset_index(drop=True)

def get_loyalty(data):
    grouped = data.groupby(["manager_short_name","manager_name","player_name","team","photo"]).agg({'player_id': 'size', 'points': 'sum'}).sort_values('player_id',ascending=False)
    return grouped

def loyalty_most_played(no_tm, fielded_points):
    loyalty_df = get_loyalty(no_tm)
    loyalty_df=loyalty_df.drop(columns="points")    
    loyalty = loyalty_df.reset_index().rename(columns={'manager_short_name': 'manager'})

    most_played_df = get_loyalty(fielded_points)
    most_played = most_played_df.reset_index().rename(columns={'manager_name': 'manager'})
    most_played["ppg"] = round(most_played["points"]/most_played["player_id"],2)
    
    most_teams_grouped = loyalty_df.groupby(["player_name","team","photo"]).size().sort_values(axis=0,ascending=False)
    most_teams = most_teams_grouped.to_frame().sort_values(by=[0, 'player_name'], ascending=[False, True]).reset_index()
    
    return loyalty, most_played, most_teams,most_played_df,loyalty_df

def get_clubmascot(data):
    mascot_grouped = data.groupby(["manager_short_name","manager_name","team"]).sum().sort_values(by=["player_id", 'manager_short_name'], ascending=[False, True])
    return mascot_grouped

def clubmascot(most_played_df,loyalty_df):
    #most owned club
    club_mascot = get_clubmascot(most_played_df)
    club_mascot["bench"] = get_clubmascot(loyalty_df)
    club_mascot.rename(columns={"player_id": 'fielded'}, inplace=True)
    club_mascot["ratio"] = round(club_mascot["fielded"]/club_mascot["bench"],2)
    club_mascot["ppg"] = round(club_mascot["points"]/club_mascot["fielded"],2)
    return club_mascot.reset_index().rename(columns={'manager_short_name': 'manager'})

def get_stats(data, gw):
    index = "index"

    stats = get_ranking(data,"fielded","goals_scored",index)
    bench_stats = get_ranking(data,"bench","goals_scored",index)

    assists = get_ranking(data,"fielded","assists",index)
    assists_bench = get_ranking(data,"bench","assists",index)
    stats["assists"] = assists["assists"]
    bench_stats["assists_bench"] = assists_bench["assists"]


    gk_def = data[(data["position"]=="GK")|(data["position"]=="DEF")]

    clean_sheets = get_ranking(gk_def,"fielded","clean_sheets",index)
    clean_sheets_bench = get_ranking(gk_def,"bench","clean_sheets",index)
    stats["clean_sheets"] = clean_sheets["clean_sheets"]
    bench_stats["clean_sheets_bench"] = clean_sheets_bench["clean_sheets"]
    
    print(type(get_ranking(data,"fielded","minutes")["minutes"].dtype))

    print(get_ranking(data,"fielded","minutes"))
    #stats["minutes"] = round(get_ranking(data,"fielded","minutes")/11/2)["minutes"]

    goals_conceded = get_ranking(gk_def,"fielded","goals_conceded", index)
    goals_conceded_bench = get_ranking(gk_def,"bench","goals_conceded",index)
    stats["goals_conceded"] = goals_conceded["goals_conceded"]
    bench_stats["goals_conceded_bench"] = goals_conceded_bench["goals_conceded"]
    
    penalties = get_ranking(data,"fielded","penalties_missed",index)
    saved_penalties = get_ranking(data,"fielded","penalties_saved",index)
    stats["penalties_missed"] = penalties["penalties_missed"]
    stats["penalties_saved"] = saved_penalties["penalties_saved"]

    own_goals = get_ranking(data,"fielded","own_goals",index)
    stats["own_goals"] = own_goals["own_goals"]

    red_cards = get_ranking(data,"fielded","red_cards",index)
    stats["red_cards"] = red_cards["red_cards"]

    yellow_cards = get_ranking(data,"fielded","yellow_cards",index)
    stats["yellow_cards"] = yellow_cards["yellow_cards"]

    saves = get_ranking(data,"fielded","saves",index)
    stats["saves"] = saves["saves"]

    bonus = get_ranking(data,"fielded","bonus",index)
    stats["bonus"] = bonus["bonus"]

    dreamteam = get_ranking(data,"fielded","in_dreamteam",index)
    stats["dreamteam"] = dreamteam["in_dreamteam"]

    return stats, bench_stats


def main(gw,league):
    full_data = fpl_data_intake.main(gw,league)
    data = full_data["akoya"]
    print(data)

    final_fpl_findings = {}

    managers = list(data["manager_short_name"].unique())
    managers.pop(1)

    fielded_points = data[(data["manager_name"]!="transfer market")&(data["bench"]=="fielded")]
    
    #region POINTS

    gameweeks_df = gameweek_df(fielded_points)

    points_ranking = get_ranking(data,"fielded","points")
    final_fpl_findings["points"] = points_ranking

    #GK Totals Table and per GW
    gk = data[data["position"]=="GK"]
    final_fpl_findings["gk"] = get_ranking(gk,"fielded","points")
    final_fpl_findings["gk_gw"] = get_ranking_gw(gk)

    #DEF Totals Table and per GW
    deef = data[data["position"]=="DEF"]
    final_fpl_findings["def"] = get_ranking(deef,"fielded","points")
    final_fpl_findings["def_gw"] = get_ranking_gw(deef)

    #MID Totals Table and per GW
    mid = data[data["position"]=="MID"]
    final_fpl_findings["mid"] = get_ranking(mid,"fielded","points")
    final_fpl_findings["mid_gw"] = get_ranking_gw(mid)

    #FWD Totals Table and per GW
    fwd = data[data["position"]=="FWD"]
    final_fpl_findings["fwd"] = get_ranking(fwd,"fielded","points")
    final_fpl_findings["fwd_gw"] = get_ranking_gw(fwd)


    final_fpl_findings["bench"] = get_ranking(data,"bench","points")
    final_fpl_findings["missed"] = missed_points(data, managers, gw)
    final_fpl_findings["podiums"], gw_podiums = podiums(gameweeks_df)
    final_fpl_findings["tottenham"] = tottenham(managers, gw_podiums)
    final_fpl_findings["last"] = gw_losers(gw_podiums)
    
    #endregion

    #region PLAYERS
    no_tm = data[(data["manager_name"]!="transfer market")]

    final_fpl_findings["loyalty"],      \
    final_fpl_findings["most_played"],  \
    final_fpl_findings["most_teams"],   \
    most_played_df,loyalty_df = loyalty_most_played(no_tm, fielded_points)
    final_fpl_findings["club_mascot"] = clubmascot(most_played_df,loyalty_df)
    #endregion

    #region STATS
    
    stats, bench_stats = get_stats(data, gw)

    #endregion


    print(final_fpl_findings)

    return final_fpl_findings, stats, bench_stats, full_data



if __name__ == "__main__":
    main()