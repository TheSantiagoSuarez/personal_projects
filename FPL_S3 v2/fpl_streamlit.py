import os
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import pickle

import fpl_methods as methods


with open ('season_data.pickle','rb') as file:
    raw_data = pickle.load(file)


# Podium function
def display_podium(title,df,column=2,value="points"):
    df = df.rename(columns={"manager_short_name":"manager_short"})
    st.subheader(title)
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.write("")
        st.write("")
        print("Current working directory:", os.getcwd())

        # Print the list of files in the directory
        print("Files in directory:", os.listdir())
        st.image("pictures/{}.png".format(df.loc[1, "manager_short"].lower()))
        st.subheader("🥈") 
        st.text("{}: {} {}".format(df.loc[1, "manager_short"], round(df.iloc[1][column]),value))

    with col2:
        st.image("pictures/{}.png".format(df.loc[0, "manager_short"].lower()))
        st.subheader("🥇")
        st.text("{}: {} {}".format(df.loc[0, "manager_short"], round(df.iloc[0][column]),value))

    with col3:
        st.write("")
        st.write("")
        st.image("pictures/{}.png".format(df.loc[2, "manager_short"].lower()))
        st.subheader("🥉") 
        st.text("{}: {} {}".format(df.loc[2, "manager_short"], round(df.iloc[2][column]),value))

    with col4:
        st.write("")

    with col5:
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.image("pictures/{}.png".format(df.loc[len(df)-1, "manager_short"].lower()))
        st.subheader("💩",)
        st.text("{}: {} {}".format(df.loc[len(df)-1, "manager_short"], round(df.iloc[len(df)-1][column]),value))

def display_stats(df, column, titles, metric):
    df.index = df["manager"]
    df = df.sort_values(column,ascending=False)
    df = df.loc[:,column]
    
    win_manager = df.index[0]
    loss_manager = df.index[len(df)-1]

    st.subheader(titles)
    tab1, tab2, tab3 = st.tabs(["Most","Least","Table"])
    with tab1:
        if df.iloc[0]==df.iloc[1]:
            tied_manager= df.index[1]
            cols1,cols2 = st.columns(2)
            with cols1:
                st.image("pictures/{}.png".format(win_manager.lower()),width=80)
            with cols2:
                st.image("pictures/{}.png".format(tied_manager.lower()),width=80)
            st.text("{} & {}:".format(win_manager,tied_manager))        
            st.text("{} {}".format(round(df.iloc[0]),metric))
        else:
            st.image("pictures/{}.png".format(win_manager.lower()),width=160)
            st.text("{}:".format(win_manager))        
            st.text("{} {}".format(round(df.iloc[0]),metric))

    with tab2:
        if df.iloc[len(df)-1]==df.iloc[len(df)-2]:
            tied_manager= df.index[len(df)-2]
            cols1,cols2 = st.columns(2)
            with cols1:
                st.image("pictures/{}.png".format(loss_manager.lower()),width=80)
            with cols2:
                st.image("pictures/{}.png".format(tied_manager.lower()),width=80)
            st.text("{} & {}:".format(loss_manager,tied_manager)) 
            st.text("{} {}".format(round(df.iloc[len(df)-1]),metric))
        else: 
            st.image("pictures/{}.png".format(loss_manager.lower()),width=160)
            st.text("{}:".format(loss_manager))
            st.text("{} {}".format(round(df.iloc[len(df)-1]),metric))
    with tab3:
        st.write(df)

def print_pic(player):
    st.image("https://resources.premierleague.com/premierleague/photos/players/110x140/p{}.png".format(player.photo))

def print_badge(team_id):
    st.image("https://resources.premierleague.com/premierleague/badges/t{}.png".format(team_id))

def show_player(data,num, points=False, metric="gameweeks"):
    #st.table(data.head())
    player = methods.get_player(data.loc[num,"player"],raw_data["players"])
    print_pic(player)
    if data.loc[num,"player"]==36:
        st.markdown("{} ✅".format(player.name))
    else:
        st.markdown("{}".format(player.name))
    
    if points=="manager":
        if data.loc[num,"player"]<0:
            st.warning("{} {}".format(data.loc[num,"metric"],metric))
        else:
            st.success("{} {}".format(data.loc[num,"metric"],metric))
    else:
        st.markdown("{} {}".format(data.loc[num,"metric"],metric))

    if points=="total":
        st.success("{} points total".format(data.loc[num,"points"]))
    elif points=="average":
        st.success("{} points per game".format(round(data.loc[num,"points"]/data.loc[num,"player"],2)))
    elif points=="manager":
        st.markdown("By {}".format(data.loc[num,"manager_short"]))

def show_most_teams(data, num, manager_data):
    player = methods.get_player(data.loc[num,"player"],raw_data["players"])
    print_pic(player)
    st.markdown("{}".format(player.name))
    st.markdown("in {} teams".format(data.loc[num,"count"]))
        
    if player.ID in manager_data["player"].values:
        row = manager_data[manager_data["player"]==data.loc[num,"player"]]
        st.markdown("{} GWs in your team".format(row["gw"].values[0]))
        st.success("{} points total".format(row["points"].values[0]))
    else:
        st.markdown(" ")
        st.markdown(" ")
        st.warning("Never in your team")



def points(findings, data):
    st.sidebar.markdown("Page Guide")
    st.sidebar.markdown("1. [Akoya FPL Award](#akoya-fpl-award)")
    st.sidebar.markdown("2. [Rankings per Position](#rankings-per-position)")
    st.sidebar.markdown("3. [Outside the starting 11](#outside-the-starting-11)")
    st.sidebar.markdown("4. [Gameweek Winners and Losers](#gameweek-winners-and-losers)")

    # region Final Standings

    st.header("Akoya FPL Award")
    st.markdown("A little jacking off session to the ones that got the most points overall")
    
    points_standings = findings["total"]

    tab1, tab2 = st.tabs(["Top 3", "Table"])

    # Create a tab for the pictures
    with tab1:
        display_podium("Final Standings Top 3",points_standings)

    # Create a tab for the table
    with tab2:
        st.subheader("Table of Final Points")
        st.write(points_standings)

    #endregion

    
    st.info("But we already knew that.")
    st.info("Let's look a bit deeper into some of the choices made in these past few months...")
    st.header("Rankings per Position")

    # region Goalkeeper Rankings
    st.subheader("Goalkeepers")
    st.markdown("A useless award for the most brain dead position in fpl. Pick a top 6 gk and inshallah.")

    data = findings["gk"]
    data_gw = findings["gk gw"]

    tab1, tab2, tab3, tab4 = st.tabs(["Top 3", "Table", "Best Gameweek", "GW Table"])

    # Create a tab for the podium
    with tab1:
        display_podium("Goalkeeper Standings Top 3",data)

    # Create a tab for the table
    with tab2:
        st.subheader("Table of Goalkeeper Points")
        st.write(data)

    with tab3:
        display_podium("Goalkeeper Best Gameweek Top 3",data_gw,3)

    with tab4:
        st.subheader("Table of Goalkeeper Best Gameweeks")
        st.write(data_gw)
    # endregion

    # region Defender Rankings
    st.subheader("Defenders")
    st.markdown("A single goal vs Arsenal can mean 4 points for someone. But it also means Ruslan losing 16 cleansheet points")

    data = findings["def"]
    data_gw = findings["def gw"]

    tab1, tab2, tab3, tab4 = st.tabs(["Top 3", "Table", "Best Gameweek", "GW Table"])

    # Create a tab for the podium
    with tab1:
        display_podium("Defender Standings Top 3",data)

    # Create a tab for the table
    with tab2:
        st.subheader("Table of Defender Points")
        st.write(data)

    with tab3:
        display_podium("Defender Best Gameweek Top 3",data_gw,3)

    with tab4:
        st.subheader("Table of Defender Best Gameweeks")
        st.write(data_gw)
    # endregion

    # region Midfielder Rankings
    st.subheader("Midfielders")
    st.markdown("CDMs are the cucks of Fantasy, might as well put a disabled person instead")
    
    data = findings["mid"]
    data_gw = findings["mid gw"]
    
    tab1, tab2, tab3, tab4 = st.tabs(["Top 3", "Table", "Best Gameweek", "GW Table"])

    # Create a tab for the podium
    with tab1:
        display_podium("Midfielders Standings Top 3",data)

    # Create a tab for the table
    with tab2:
        st.subheader("Table of Midfielder Points")
        st.write(data)

    with tab3:
        display_podium("Midfielder Best Gameweek Top 3",data_gw,3)

    with tab4:
        st.subheader("Table of Midfielder Best Gameweeks")
        st.write(data_gw)
    # endregion

    # region Forward Rankings
    st.subheader("Forwards")
    st.markdown("Just happy that Haaland didn't get in the podium for best gameweeks")

    data = findings["fwd"]
    data_gw = findings["fwd gw"]

    tab1, tab2, tab3, tab4 = st.tabs(["Top 3", "Table", "Best Gameweek", "GW Table"])

    # Create a tab for the podium
    with tab1:
        display_podium("Forwards Standings Top 3",data)

    # Create a tab for the table
    with tab2:
        st.subheader("Table of Forward Points")
        st.write(data)

    with tab3:
        display_podium("Forward Best Gameweek Top 3",data_gw,3)

    with tab4:
        st.subheader("Table of Forward Best Gameweeks")
        st.write(data_gw)
    # endregion

    st.info("Haaland was 231 of those points btw")
    st.info("Anyways, some highs, some lows... but all our own choices, for the most part")
    st.info("Now let's look at the ones we didn't choose, let's look...")
    st.header("Outside the starting 11")

    # region Bench FC
    st.subheader("Bench FC")
    st.markdown("Ranking of teams with most points in their bench")
    data = findings["bench"]

    tab1, tab2 = st.tabs(["Top 3", "Table"])

    # Create a tab for the podium
    with tab1:
        display_podium("Bench FC Standings Top 3",data)

    # Create a tab for the table
    with tab2:
        st.subheader("Table of Bench Points")
        st.write(data)
    # endregion

    # region Optimised Bench
    st.subheader("Optimised Bench")
    st.markdown("Basically a 'What if...?' in which we look at how many points were left on the bench everyone except Yahya could have capitalised on")
    data = findings["missed"]

    merged_df = pd.merge(data, points_standings, on='manager')
    merged_df['Final Points'] = merged_df['points_x'] + merged_df['points_y']
    result_df = merged_df[['manager', 'Final Points']].sort_values(by='Final Points',ascending=False)

    trace2 = go.Bar(
        x=merged_df["manager"],
        y=merged_df["Final Points"],
        name='Optimised Points',
        marker=dict(color='blue')  # Set the color for the bars of Series 1
    )

    # Create a bar trace for the second series
    trace1 = go.Bar(
        x=points_standings["manager"],
        y=points_standings["points"],
        name='Final Ranking',
        marker=dict(color='green')  # Set the color for the bars of Series 2
    )

    # Create the data list with both traces
    data2 = [trace1, trace2]

    # Define the layout
    layout = go.Layout(
        title='Comparison of Final Ranking vs Optimised Points',
        xaxis=dict(title='Manager'),
        yaxis=dict(title='Points')
    )

    # Create the figure
    fig = go.Figure(data=data2, layout=layout)

    tab1, tab2, tab3 = st.tabs(["Top 3", "Table", "Updated Final Standings"])

    # Create a tab for the podium
    with tab1:
        display_podium("Optimised Bench Standings Top 3",data,2)

    # Create a tab for the table
    with tab2:
        st.subheader("Table of Missed Bench Points")
        st.write(data)

    with tab3:
        st.subheader("Table of Optimised Points vs Final Ranking")
        st.plotly_chart(fig)
    # endregion


    st.info("De Bruyne in the bench was a brave choice")
    st.info("Since we've looked at our points and our choices, let's look at what we saw in the end of every gameweek. Let's look at...")
    st.header("Gameweek Winners and Losers")

    
    # region Podiums
    st.subheader("Podiums")
    st.markdown("Amount of times in the top 3 each gameweek")
    data = findings["streaks"].iloc[:,:5]

    first = data[["manager_short","1st"]].sort_values("1st",ascending=False).reset_index(drop=True)
    second = data[["manager_short","2nd"]].sort_values("2nd",ascending=False).reset_index(drop=True)
    third = data[["manager_short","3rd"]].sort_values("3rd",ascending=False).reset_index(drop=True)
    total = data[["manager_short","Total"]].sort_values("Total",ascending=False).reset_index(drop=True)

    tab1, tab2, tab3, tab4, tab5= st.tabs(["First Place", "Second Place", "Third Place", "Total Podiums", "Table"])


    # Create a tab for the podium
    with tab1:
        display_podium("1st Place Gameweeks",first,1, "gws")

    with tab2:
        display_podium("2nd Place Gameweeks",second,1, "gws")
    
    with tab3:
        display_podium("3rd Place Gameweeks",third,1, "gws")
    
    with tab4:
        display_podium("Total Podiums",total,1, "gws")

    # Create a tab for the table
    with tab5:
        st.subheader("Table of Podiums")
        st.write(data)

    
    # endregion

    # region Tottenham
    st.subheader("Tottenham Award")
    st.markdown("A tribute to the chickens, a ranking of the longest streaks without winning a podium in the league")
    data = findings["streaks"][["manager_short","tottenham"]].sort_values("tottenham",ascending=False).reset_index(drop=True)
    streak_data = findings["streaks"][["manager_short","tottenham","streak"]].sort_values("tottenham",ascending=False).reset_index(drop=True)

    tab1, tab2 = st.tabs(["Top 3", "Table"])

    # Create a tab for the podium
    with tab1:
        display_podium("Longest Winless Streak Top 3",data,1,"gws")

    # Create a tab for the table
    with tab2:
        st.subheader("Table of Longest Winless Streak")
        st.write(streak_data)
    # endregion

    # region Last Place
    st.subheader("Last Places")
    st.markdown("Pretty self explanatory... a ranking of Last Place gameweek Finishes")
    data = findings["streaks"][["manager_short","last"]].sort_values("last",ascending=False).reset_index(drop=True)
    
    tab1, tab2 = st.tabs(["Top 3", "Table"])

    # Create a tab for the podium
    with tab1:
        display_podium("Last Places Top 3",data,1,"gws")

    # Create a tab for the table
    with tab2:
        st.subheader("Table of Last Places")
        st.write(data)
    # endregion
 
def players(findings, data):
    st.subheader("Players Page")
    st.markdown("Some individual and group facts about players in the AKOYA league. Please choose a manager in the sidebar")

    manager = st.sidebar.selectbox("Choose Manager",[man.short_name for man in data["managers"]])
    manager_data = next((man for man in data["managers"] if man.short_name == manager), None)
    manager_pts = int(sum(manager_data.standings["points"]["total"].values()))

    st.sidebar.image("pictures/{}.png".format(manager.lower()), caption=manager,width=200)

    st.sidebar.markdown("Page Guide")
    st.sidebar.markdown("1. [Loyalty](#loyalty)")
    st.sidebar.markdown("2. [UnLoyalty](#unloyalty)")
    st.sidebar.markdown("3. [Most Teams](#most-teams)")
    st.sidebar.markdown("4. [Club Mascot](#club-mascot)")
    st.sidebar.markdown("4. [Season Ticket Holder](#season-ticket-holder)")
    st.sidebar.markdown("5. [Star Players](#star-players)")

    st.markdown(" ")
    st.info("Choosing who to have in your team was hard, unless you just chose Arsenal players and called it a day")
    st.info("Let's first look at who has stuck with you through thick and thin, and ask yourself why Ali was such a lucky bitch for getting Haaland as his first pick. Let's look at...")
    st.header("Loyalty")
    st.markdown("The players you've owned the longest")

    
    real_ranking = findings['total']

    #region Loyalty
    loyalty = findings["players"]['loyalty']

    manager_df = loyalty[loyalty["manager_short"]==manager].sort_values("gw",ascending=False).reset_index(drop=True).iloc[:10]
    cols = st.columns(5)

    for i in range(5):
        with cols[i]:
            show_player(manager_df.rename(columns={"gw":"metric"}),i)
            show_player(manager_df.rename(columns={"gw":"metric"}),i+5)
    #endregion
            
    st.markdown("<hr>", unsafe_allow_html=True)
    st.header("UnLoyalty")
    st.markdown("The opposite of the last one")
    
    #region Unloyalty?
    manager_df = loyalty[loyalty["manager_short"]==manager].sort_values("gw",ascending=True).reset_index(drop=True).iloc[:10]
    cols = st.columns(5)

    for i in range(5):
        with cols[i]:
            show_player(manager_df.rename(columns={"gw":"metric"}),i)
    #endregion

    st.markdown(" ")
    st.markdown("<hr>", unsafe_allow_html=True)
    st.info("We've seen the players that have been most in ONE team, now let's look at the players that have been in MOST teams")

    st.header("Most Teams")
    st.markdown("What I just said")

    #region Most Teams

    data = findings["players"]["joao felix"][:8]
    manager_df = loyalty[loyalty["manager_short"]==manager].sort_values("gw",ascending=False).reset_index(drop=True)

    cols = st.columns(4)

    for i in range(4):
        with cols[i]:
            show_most_teams(data,i,manager_df)
            show_most_teams(data,i+4,manager_df)
    
    #endregion

    st.markdown("<hr>", unsafe_allow_html=True)
    st.info("Now, Ruslan's time to shine")

    st.header("Club Mascot")
    st.markdown("A few stats based on how many players from a single club one has fielded")

    #region Club Mascot
    mascot = findings["players"]["club mascot"]
    fielded = mascot[mascot["manager_short"]==manager].sort_values("count",ascending=False).reset_index(drop=True)
    fielded["ppg"] = round(fielded["points"]/fielded["count"],2)

    tab1, tab2 = st.tabs(["Most Fielded","Points per Game"])

    
    with tab1:
        tab1_cols = st.columns(3)
        for i in range(3):
            with tab1_cols[i]:
                row = fielded.loc[i]
                team = next((tm for tm in raw_data["teams"] if tm.name == row["team"]), None)
                percentage = round(row["points"]/manager_pts,2)
                print_badge(team.badge)
                st.markdown("Fielded {} players {} times".format(row["team"],row["count"]))
                st.markdown("Scored {} total points".format(row["points"]))
                st.success("{}% of total points".format(percentage*100))
                
    with tab2:
        tab2_cols = st.columns(3)
        for i in range(3):
            with tab2_cols[i]:
                row = fielded.loc[i]
                team = next((tm for tm in raw_data["teams"] if tm.name == row["team"]), None)
                percentage = round(row["points"]/manager_pts,2)
                print_badge(team.badge)
                st.markdown("Fielded {} players {} times".format(row["team"],row["count"]))
                st.markdown("Scored {} points per game".format(row["ppg"]))
                st.success("{}% of total points".format(percentage*100))
    #endregion
    
    st.markdown("<hr>", unsafe_allow_html=True)
    st.info("A slightly different view to the biggest fans of each team")

    st.header("Season Ticket Holder")
    st.markdown("Who fielded the most players from each team")

    # region Season Ticket

    data = findings["players"]["season ticket"]

    cols = st.columns(5)

    for i in range(5):
        with cols[i]:
            for row_num in range(4):
                row = data.iloc[(i+(row_num*5))]
                team = next((tm for tm in raw_data["teams"] if tm.name == row["team"]), None)
                man = next((m for m in raw_data["managers"] if m.short_name == row["manager_short"]), None)

                print_badge(team.badge)
                st.markdown(team.name)
                if row["manager_short"] == manager:
                    st.success(man.name +' ' + man.lastname[0])
                    st.markdown(f"Played {team.name} players {row['count']} times")
                else:
                    st.warning(man.name +' ' + man.lastname[0])
                    st.markdown(f"Played {team.name} players {row['count']} times")
                st.markdown("<hr>", unsafe_allow_html=True)

    # endregion

    st.header("Star Players")

    #region Star Players
    data = findings["players"]['star']
    total_points = data[data["manager_short"]==manager].sort_values("points",ascending=False).reset_index(drop=True)[:3]
    ppg = data[data["manager_short"]==manager].sort_values("ppg",ascending=False).reset_index(drop=True)[:3]

    tab1, tab2 = st.tabs(["Points Total","Points per Game*"])

    with tab1:
        tab1_cols = st.columns(3)
        for i in range(3):
            with tab1_cols[i]:
                row = total_points.loc[i]
                player = methods.get_player(total_points.loc[i,"player"],raw_data["players"])
                print_pic(player)
                percentage = round(row["points"]/manager_pts,2)
                st.markdown("{}".format(player.name))
                st.markdown("Scored {} total points".format(row["points"]))
                st.success("{}% of total points".format(percentage*100))
    
    with tab2:
        tab2_cols = st.columns(3)
        for i in range(3):
            with tab2_cols[i]:
                row = ppg.loc[i]
                player = methods.get_player(ppg.loc[i,"player"],raw_data["players"])
                print_pic(player)
                percentage = round(row["points"]/manager_pts,2)
                st.markdown("{}".format(player.name))
                st.markdown("Scored {} points per game".format(row["ppg"]))
                st.success("{}% of total points".format(percentage*100))
        
        st.markdown("*Must have played at least 5 games")
    #endregion

def draft_h2h(findings, data):
    st.subheader("Head to Head")
    st.markdown("Introducing in the Akoya Cup 3rd Edition, a new format. It doesn't matter how many points you get, just if you beat the dickhead you're going up against.")
    st.markdown("Let's see how you did")

def stats(findings, data):
    data = findings["stats"]
    st.subheader("General Statistics Page")
    st.markdown("Here we are to celebrate the best of the best in each category, giving them the award they deserve.")
    st.markdown("Let's see the winners...")
    cols = st.columns(4)

    for i in range(4):
        with cols[i]:
            columns = ["goals_scored","assists","clean_sheets","goals_conceded"]
            titles = ["Most Goals Scored","Most Assists Provided","Most Cleansheets","Most Goals Conceded"]
            metrics = ["goals","assists","clean sheets","goals conceded"]

            display_stats(data,columns[i],titles[i],metrics[i])
            st.markdown("<hr>", unsafe_allow_html=True)

            columns = ["penalties_missed","penalties_saved","red_cards","yellow_cards"]
            titles = ["2016 Pessi Award","Not De Gea Award","Sergio Ramos Award","Sergio Ramos Lite Award"]
            metrics = ["penalties missed","penalties saved","red cards","rellow cards"]

            display_stats(data,columns[i],titles[i],metrics[i])
            st.markdown("<hr>", unsafe_allow_html=True)

            columns = ["own_goals","saves","bonus","in_dreamteam"]
            titles = ["Luke Shaw Award","The Wall Award","BPS Merchant","TOTW Merchant"]
            metrics = ["own goals","saves","bonus points","TOTW players"]

            display_stats(data,columns[i],titles[i],metrics[i])
            st.markdown("<hr>", unsafe_allow_html=True)

def transfers(findings, data):
    manager = st.sidebar.selectbox("Choose Manager",["Everyone"]+[man.short_name for man in data["managers"]])
    if manager != "Everyone":
        st.sidebar.image("pictures/{}.png".format(manager.lower()), caption=manager,width=200)

    st.sidebar.markdown("Page Guide")
    st.sidebar.markdown("1. [Total Transfers Ranking](#total-transfers-ranking)")
    st.sidebar.markdown("2. [Most Transferred In](#most-transferred-in)")
    st.sidebar.markdown("3. [Best & Worst Transfers](#best-and-worst-transfers)")

    st.subheader("Transfers Page")
    st.markdown("Quick view of the best and worst transactions in the AKOYA league")
    
    st.markdown("<hr>", unsafe_allow_html=True)

    st.subheader("Total Transfers Ranking")
    st.markdown("R.I.P. Transfers Weekly by Ali Ascioglu")

    #region Transfer Ranking
    data = findings["transfers"]["total transfers"]
    tab1, tab2 = st.tabs(["Total Transfers","Table"])
    with tab1:
        display_podium("Total Transfers",data,"num_transfers","transfers")
    with tab2:
        st.write(data)
    #endregion

    st.markdown("<hr>", unsafe_allow_html=True)
    st.info("Next up the definition of a love hate relationship, let's look at...")

    st.subheader("Most Transferred In")
    st.markdown("The players you make sleep on the couch one night and come back to bed the next")

    #region Transfer In
    data = findings["transfers"]["love hate"]

    tab1, tab2 = st.tabs(["Most Transferred","Table"])
    with tab1:
        if manager=="Everyone":
            cols = st.columns(4)
            for i in range(4):
                with cols[i]:
                    show_player(data.rename(columns={"num_transfers":"metric"}),i,"manager","times transferred")
                    show_player(data.rename(columns={"num_transfers":"metric"}),i+4,"manager","times transferred")
        else:
            manager_df = data[data["manager_short"]==manager].reset_index(drop=True)
            cols = st.columns(2)

            num_repeats = manager_df.shape[0]
            if num_repeats==0:
                st.info("Bro does not believe in second chances...")
            else:
                columns = 1 if num_repeats == 1 else 2
                for i in range(columns):
                    with cols[i]:
                        show_player(manager_df.rename(columns={"num_transfers":"metric"}),i,"manager","times transferred")
    with tab2:
        st.write(data[["manager_short","player_name","num_transfers"]][:20])
    #endregion

    st.markdown("<hr>", unsafe_allow_html=True)
    st.info("Lastly, let's try to answer a question everyone has after getting a new player. Let's look at the...")

    st.subheader("Best and Worst Transfers")
    st.markdown("Just comparison of the highest scoring players in the first three weeks transferred in compared to the one traded out")

    #region Best and Worst Transfers
    data = findings["transfers"]["best worst"]
    trades = st.selectbox("Which ones do you want to see", ("Best Trades","Worst Trades"))

    if trades == "Worst Trades":
        data = data.sort_values(by="pts_gain",ascending=True).reset_index()
    else:
        data = data.sort_values(by="pts_gain",ascending=False).reset_index()

    tab1, tab2 = st.tabs(["Total Transfers","Table"])
    with tab1:
        if manager=="Everyone":
            df = data.rename(columns={"pts_gain":"metric"})
            cols = st.columns(5)
            for i in range(5):
                with cols[i]:
                    show_player(df,i,"manager","net points")
                    show_player(df,i+5,"manager","net points")
        else:
            df = data[data["manager_short"]==manager].reset_index(drop=True).rename(columns={"pts_gain":"metric"})
            cols = st.columns(5)
            for i in range(5):
                with cols[i]:
                    show_player(df,i,"manager","net points")
    with tab2:
        st.write(df[["gameweek","manager_short","player_name","player_out","player_out_name","in_pts","out_pts"]])
    #endregion

pages = {
    "Total Points": points,
    "Players": players,
    "Draft & Head-to-head": draft_h2h,
    "General Stats" : stats,
    "Transfers" : transfers
}


def main(findings, data):
    #gw = st.text_input("Please enter your current gameweek: ")
    #league = st.text_input("Enter league code (akoya = 41570): ")

    #findings, stats, bench_stats, full_data = fpl_findings.main(int(gw),league)
    st.title("AKOYA FPL Draft Wrapped")
    st.markdown("Let's look back at this season")

    # Add sidebar navigation
    st.sidebar.subheader("Navigation")
    st.sidebar.info("Please use this sidebar for page navigation and to go to points of interest in each page")
    selection = st.sidebar.radio("Go to", list(pages.keys()))

    # Call the function based on selection
    pages[selection](findings, data)  


if __name__ == "__main__": 
    #gw = st.text_input("Please enter your current gameweek: ")
    #league = st.text_input("Enter league code (akoya = 41570): ")
    #findings, stats, bench_stats, full_data = fpl_findings.main(int(gw),league)

    with open ('season_findings.pickle','rb') as file:
        findings = pickle.load(file)

    
    with open ('season_data.pickle','rb') as file:
        data = pickle.load(file)

    main(findings, data)