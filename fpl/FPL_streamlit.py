import os
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

# Podium function
def display_podium(title,df,column=1,value="pts"):
    st.subheader(title)
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.write("")
        st.write("")
        print("Current working directory:", os.getcwd())

        # Print the list of files in the directory
        print("Files in directory:", os.listdir())
        st.image("fpl/pictures/{}.png".format(df.loc[1, "manager"].lower()))
        st.subheader("🥈") 
        st.text("{}: {} {}".format(df.loc[1, "manager"], round(df.iloc[1][column]),value))

    with col2:
        st.image("fpl/pictures/{}.png".format(df.loc[0, "manager"].lower())) 
        st.subheader("🥇")
        st.text("{}: {} {}".format(df.loc[0, "manager"], round(df.iloc[0][column]),value))

    with col3:
        st.write("")
        st.write("")
        st.image("fpl/pictures/{}.png".format(df.loc[2, "manager"].lower()))
        st.subheader("🥉") 
        st.text("{}: {} {}".format(df.loc[2, "manager"], round(df.iloc[2][column]),value))

    with col4:
        st.write("")

    with col5:
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.image("fpl/pictures/{}.png".format(df.loc[len(df)-1, "manager"].lower()))
        st.subheader("💩",)
        st.text("{}: {} {}".format(df.loc[len(df)-1, "manager"], round(df.iloc[len(df)-1][column]),value))

def print_pic(data, num):
    st.image("https://resources.premierleague.com/premierleague/photos/players/110x140/p{}.png".format(data.loc[num,"photo"]))

def show_player(data,num, points=False, metric="gameweeks"):
    print_pic(data,num)
    if data.loc[num,"player_id"]==34:
        st.markdown("{} ✅".format(data.loc[num,"player_name"]))
    else:
        st.markdown("{}".format(data.loc[num,"player_name"]))
    
    if points=="manager":
        if data.loc[num,"player_id"]<0:
            st.warning("{} {}".format(data.loc[num,"player_id"],metric))
        else:
            st.success("{} {}".format(data.loc[num,"player_id"],metric))
    else:
        st.markdown("{} {}".format(data.loc[num,"player_id"],metric))

    if points=="total":
        st.success("{} points total".format(data.loc[num,"points"]))
    elif points=="average":
        st.success("{} points per game".format(round(data.loc[num,"points"]/data.loc[num,"player_id"],2)))
    elif points=="manager":
        st.markdown("By {}".format(data.loc[num,"manager"]))

def show_most_teams(data, num, data2):
    print_pic(data,num)
    player_name = data.loc[num,"player_name"]
    st.markdown("{}".format(player_name))
    st.markdown("in {} teams".format(data.loc[num,"0"]))    
        
    if player_name in data2["player_name"].values:
        row = data2[data2["player_name"]==data.loc[num,"player_name"]]
        st.markdown("{} GWs in your team".format(row["player_id"].values[0]))
        st.success("{} points total".format(row["points"].values[0]))
    else:
        st.markdown(" ")
        st.markdown(" ")
        st.warning("Never in your team")

def display_stats(df, column, titles, metric):
    df = df[["manager_id",column]]
    df = df.sort_values(column,ascending=False).reset_index(drop=True,)
    
    win_manager = df.loc[0, "manager_id"]
    loss_manager = df.loc[len(df)-1, "manager_id"]

    st.subheader(titles)
    tab1, tab2, tab3 = st.tabs(["Most","Least","Table"])
    with tab1:
        if df.loc[0, column]==df.loc[1, column]:
            tied_manager= df.loc[1, "manager_id"]
            cols1,cols2 = st.columns(2)
            with cols1:
                st.image("fpl/pictures/{}.png".format(win_manager.lower()),width=80)
            with cols2:
                st.image("fpl/pictures/{}.png".format(tied_manager.lower()),width=80)
            st.text("{} & {}:".format(win_manager,tied_manager))        
            st.text("{} {}".format(round(df.loc[0, column]),metric))
        else:
            st.image("fpl/pictures/{}.png".format(win_manager.lower()),width=160)
            st.text("{}:".format(win_manager))        
            st.text("{} {}".format(round(df.loc[0, column]),metric))

    with tab2:
        if df.loc[len(df)-1, column]==df.loc[len(df)-2, column]:
            tied_manager= df.loc[len(df)-2, "manager_id"]
            cols1,cols2 = st.columns(2)
            with cols1:
                st.image("fpl/pictures/{}.png".format(loss_manager.lower()),width=80)
            with cols2:
                st.image("fpl/pictures/{}.png".format(tied_manager.lower()),width=80)
            st.text("{} & {}:".format(loss_manager,tied_manager)) 
            st.text("{} {}".format(round(df.loc[len(df)-1, column]),metric))
        else: 
            st.image("fpl/pictures/{}.png".format(loss_manager.lower()),width=160)
            st.text("{}:".format(loss_manager))
            st.text("{} {}".format(round(df.loc[len(df)-1, column]),metric))
    with tab3:
        st.write(df)


def points():
    st.sidebar.markdown("Page Guide")
    st.sidebar.markdown("1. [Akoya FPL Award](#akoya-fpl-award)")
    st.sidebar.markdown("2. [Rankings per Position](#rankings-per-position)")
    st.sidebar.markdown("3. [Outside the starting 11](#outside-the-starting-11)")
    st.sidebar.markdown("4. [Gameweek Winners and Losers](#gameweek-winners-and-losers)")

    # region Final Standings
    
    st.subheader("Points to Total Average Points")
    st.video("https://www.youtube.com/watch?v=E9WhmBp80f8")
    st.markdown("See more in: https://public.flourish.studio/visualisation/13576709/")

    st.header("Akoya FPL Award")
    st.markdown("A little jacking off session to the ones that got the most points overall")
    main_ranking = pd.read_csv('fpl/findings/points/real_ranking.csv')

    tab1, tab2 = st.tabs(["Top 3", "Table"])

    # Create a tab for the pictures
    with tab1:
        display_podium("Final Standings Top 3",main_ranking)

    # Create a tab for the table
    with tab2:
        st.subheader("Table of Final Points")
        st.write(main_ranking)

    #endregion
    
    st.info("But we already knew that.")
    st.info("Let's look a bit deeper into some of the choices made in these past few months...")
    st.header("Rankings per Position")

    # region Goalkeeper Rankings
    st.subheader("Goalkeepers")
    st.markdown("A useless award for the most brain dead position in fpl. Pick a top 6 gk and inshallah.")

    data = pd.read_csv('fpl/findings/points/gk_ranking.csv')
    data_gw = pd.read_csv('fpl/findings/points/gw_gk_ranking.csv')

    tab1, tab2, tab3, tab4 = st.tabs(["Top 3", "Table", "Best Gameweek", "GW Table"])

    # Create a tab for the podium
    with tab1:
        display_podium("Goalkeeper Standings Top 3",data)

    # Create a tab for the table
    with tab2:
        st.subheader("Table of Goalkeeper Points")
        st.write(data)

    with tab3:
        display_podium("Goalkeeper Best Gameweek Top 3",data_gw,2)

    with tab4:
        st.subheader("Table of Goalkeeper Best Gameweeks")
        st.write(data_gw)
    # endregion

    # region Defender Rankings
    st.subheader("Defenders")
    st.markdown("A single goal vs Arsenal can mean 4 points for someone. But it also means Ruslan losing 16 cleansheet points")

    data = pd.read_csv('fpl/findings/points/def_ranking.csv')
    data_gw = pd.read_csv('fpl/findings/points/gw_def_ranking.csv')

    tab1, tab2, tab3, tab4 = st.tabs(["Top 3", "Table", "Best Gameweek", "GW Table"])

    # Create a tab for the podium
    with tab1:
        display_podium("Defender Standings Top 3",data)

    # Create a tab for the table
    with tab2:
        st.subheader("Table of Defender Points")
        st.write(data)

    with tab3:
        display_podium("Defender Best Gameweek Top 3",data_gw,2)

    with tab4:
        st.subheader("Table of Defender Best Gameweeks")
        st.write(data_gw)
    # endregion

    # region Midfielder Rankings
    st.subheader("Midfielders")
    st.markdown("CDMs are the cucks of Fantasy, might as well put a disabled person instead")
    data = pd.read_csv('fpl/findings/points/mid_ranking.csv')
    data_gw = pd.read_csv('fpl/findings/points/gw_mid_ranking.csv')

    tab1, tab2, tab3, tab4 = st.tabs(["Top 3", "Table", "Best Gameweek", "GW Table"])

    # Create a tab for the podium
    with tab1:
        display_podium("Midfielders Standings Top 3",data)

    # Create a tab for the table
    with tab2:
        st.subheader("Table of Midfielder Points")
        st.write(data)

    with tab3:
        display_podium("Midfielder Best Gameweek Top 3",data_gw,2)

    with tab4:
        st.subheader("Table of Midfielder Best Gameweeks")
        st.write(data_gw)
    # endregion

    # region Forward Rankings
    st.subheader("Forwards")
    st.markdown("Just happy that Haaland didn't get in the podium for best gameweeks")

    data = pd.read_csv('fpl/findings/points/fwd_ranking.csv')
    data_gw = pd.read_csv('fpl/findings/points/gw_fwd_ranking.csv')

    tab1, tab2, tab3, tab4 = st.tabs(["Top 3", "Table", "Best Gameweek", "GW Table"])

    # Create a tab for the podium
    with tab1:
        display_podium("Forwards Standings Top 3",data)

    # Create a tab for the table
    with tab2:
        st.subheader("Table of Forward Points")
        st.write(data)

    with tab3:
        display_podium("Forward Best Gameweek Top 3",data_gw,2)

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
    data = pd.read_csv('fpl/findings/points/bench.csv')

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
    data = pd.read_csv('fpl/findings/points/bench_best.csv')

    merged_df = pd.merge(data, main_ranking, on='manager')
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
        x=main_ranking["manager"],
        y=main_ranking["points"],
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
        display_podium("Optimised Bench Standings Top 3",data)

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
    data = pd.read_csv('fpl/findings/points/podiums.csv')

    first = data[["manager","1st"]].sort_values("1st",ascending=False).reset_index(drop=True)
    second = data[["manager","2nd"]].sort_values("2nd",ascending=False).reset_index(drop=True)
    third = data[["manager","3rd"]].sort_values("3rd",ascending=False).reset_index(drop=True)
    total = data[["manager","Total"]].sort_values("Total",ascending=False).reset_index(drop=True)

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
    data = pd.read_csv('fpl/findings/points/tottenham.csv')

    tab1, tab2 = st.tabs(["Top 3", "Table"])

    # Create a tab for the podium
    with tab1:
        display_podium("Longest Winless Streak Top 3",data,1,"gws")

    # Create a tab for the table
    with tab2:
        st.subheader("Table of Longest Winless Streak")
        st.write(data)
    # endregion

    # region Last Place
    st.subheader("Last Places")
    st.markdown("Pretty self explanatory... a ranking of Last Place gameweek Finishes")
    data = pd.read_csv('fpl/findings/points/last_df.csv')

    tab1, tab2 = st.tabs(["Top 3", "Table"])

    # Create a tab for the podium
    with tab1:
        display_podium("Last Places Top 3",data,1,"gws")

    # Create a tab for the table
    with tab2:
        st.subheader("Table of Last Places")
        st.write(data)
    # endregion

def players():
    st.subheader("Players Page")
    st.markdown("Some individual and group facts about players in the AKOYA league. Please choose a manager in the sidebar")

    manager = st.sidebar.selectbox("Choose Manager", ("Ali","Ruslan","Sami","Yahya","Youssef","Santi","Shrey","Dani"))

    st.sidebar.image("fpl/pictures/{}.png".format(manager.lower()), caption=manager,width=200)

    st.sidebar.markdown("Page Guide")
    st.sidebar.markdown("1. [Loyalty](#loyalty)")
    st.sidebar.markdown("2. [UnLoyalty](#unloyalty)")
    st.sidebar.markdown("3. [Most Played](#most-played)")
    st.sidebar.markdown("4. [Most Teams](#most-teams)")
    st.sidebar.markdown("5. [Club Mascot](#club-mascot)")
    st.sidebar.markdown("6. [Star Players](#star-players)")

    st.markdown(" ")
    st.info("Choosing who to have in your team was hard, unless you just chose Arsenal players and called it a day")
    st.info("Let's first look at who has stuck with you through thick and thin, and ask yourself why Ali was such a lucky bitch for getting Haaland as his first pick. Let's look at...")
    st.header("Loyalty")
    st.markdown("The players you've owned the longest")

    real_ranking = pd.read_csv("fpl/findings/points/real_ranking.csv")

    #region Loyalty
    data = pd.read_csv('fpl/findings/players/loyalty.csv')

    manager_df = data[data["manager"]==manager].sort_values("player_id",ascending=False).reset_index(drop=True).iloc[:10]
    cols = st.columns(5)

    for i in range(5):
        with cols[i]:
            show_player(manager_df,i)
            show_player(manager_df,i+5)
    #endregion
    
    st.markdown("<hr>", unsafe_allow_html=True)
    st.header("UnLoyalty")
    st.markdown("The opposite of the last one")
    
    #region Unloyalty?
    manager_df = data[data["manager"]==manager].sort_values("player_id",ascending=True).reset_index(drop=True).iloc[:10]
    cols = st.columns(5)

    for i in range(5):
        with cols[i]:
            show_player(manager_df,i)
    #endregion

    st.markdown("<hr>", unsafe_allow_html=True)
    st.header("Most Played")
    st.markdown("The players you've fielded the most")

    #region Most Played
    data = pd.read_csv('fpl/findings/players/most_played.csv')
    manager_df_full = data[data["manager"]==manager].reset_index(drop=True).sort_values("player_id",ascending=False)
    manager_df = manager_df_full[:11]
    tab1, tab2 = st.tabs(["Points Total","Points per Game"])

    with tab1:
        tab1_cols = st.columns(5)
        for i in range(5):
            with tab1_cols[i]:
                show_player(manager_df,i,"total")
                show_player(manager_df,i+5,"total")
                
    with tab2:
        tab2_cols = st.columns(5)
        for i in range(5):
            with tab2_cols[i]:
                show_player(manager_df,i,"average")
                show_player(manager_df,i+5,"average")

    #endregion

    st.markdown(" ")
    st.markdown("<hr>", unsafe_allow_html=True)
    st.info("We've seen the players that have been most in ONE team, now let's look at the players that have been in MOST teams")

    st.header("Most Teams")
    st.markdown("What I just said")

    #region Most Teams
    most_teams = pd.read_csv('fpl/findings/players/most_teams.csv')[:8]

    cols = st.columns(4)

    for i in range(4):
        with cols[i]:
            show_most_teams(most_teams,i,manager_df_full)
            show_most_teams(most_teams,i+4,manager_df_full)
    #endregion
    
    st.markdown("<hr>", unsafe_allow_html=True)
    st.info("Now, Ruslan's time to shine")

    st.header("Club Mascot")
    st.markdown("A few stats based on how many players from a single club one has fielded")

    #region Club Mascot
    mascot = pd.read_csv('fpl/findings/players/club_mascot.csv')
    fielded = mascot[mascot["manager"]==manager].sort_values("fielded",ascending=False).reset_index(drop=True)
    ppg = mascot[(mascot["manager"]==manager)&(mascot["fielded"]>15)].sort_values("ppg",ascending=False).reset_index(drop=True)

    tab1, tab2 = st.tabs(["Most Fielded","Points per Game"])
    
    with tab1:
        tab1_cols = st.columns(3)
        for i in range(3):
            with tab1_cols[i]:
                row = fielded.loc[i]
                percentage = round(row["points"]/int(real_ranking[real_ranking["manager"]==manager]["points"].values[0]),2)
                st.image("fpl/team_logos/{}.png".format(row["team"]))
                st.markdown("Fielded {} players {} times".format(row["team"],row["fielded"]))
                st.markdown("Scored {} total points".format(row["points"]))
                st.success("{}% of total points".format(percentage*100))
                
    with tab2:
        tab2_cols = st.columns(3)
        for i in range(3):
            with tab2_cols[i]:
                row = ppg.loc[i]
                percentage = round(row["points"]/int(real_ranking[real_ranking["manager"]==manager]["points"].values[0]),2)
                st.image("fpl/team_logos/{}.png".format(row["team"]))
                st.markdown("Fielded {} players {} times".format(row["team"],row["fielded"]))
                st.markdown("Scored {} total points".format(row["ppg"]))
                st.success("{}% of total points".format(percentage*100))
    #endregion
    
    st.header("Star Players")

    #region Star Players
    data = pd.read_csv('fpl/findings/players/most_played.csv')
    total_points = data[data["manager"]==manager].sort_values("points",ascending=False).reset_index(drop=True)[:3]
    ppg = data[(data["manager"]==manager)&(data["player_id"]>5)].sort_values("ppg",ascending=False).reset_index(drop=True)[:3]

    tab1, tab2 = st.tabs(["Points Total","Points per Game*"])

    with tab1:
        tab1_cols = st.columns(3)
        for i in range(3):
            with tab1_cols[i]:
                print_pic(total_points,i)
                row = total_points.loc[i]
                percentage = round(row["points"]/int(real_ranking[real_ranking["manager"]==manager]["points"].values[0]),2)
                st.markdown("{}".format(row["player_name"]))
                st.markdown("Scored {} total points".format(row["points"]))
                st.success("{}% of total points".format(percentage*100))
    
    with tab2:
        tab2_cols = st.columns(3)
        for i in range(3):
            with tab2_cols[i]:
                print_pic(ppg,i)
                row = ppg.loc[i]
                percentage = round(row["points"]/int(real_ranking[real_ranking["manager"]==manager]["points"].values[0]),2)
                st.markdown("{}".format(row["player_name"]))
                st.markdown("Scored {} points per game".format(row["ppg"]))
                st.success("{}% of total points".format(percentage*100))
        
        st.markdown("*Must have played at least 5 games")
    #endregion

def stats():
    data = pd.read_csv("fpl/findings/stats/stats.csv")
    st.subheader("Genneral Statistics Page")
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

            columns = ["own_goals","saves","bonus","dreamteam"]
            titles = ["Maguire Award","The Wall Award","BPS Merchant","TOTW Merchant"]
            metrics = ["own goals","saves","bonus points","TOTW players"]

            display_stats(data,columns[i],titles[i],metrics[i])
            st.markdown("<hr>", unsafe_allow_html=True)

def transfers():
    manager = st.sidebar.selectbox("Choose Whose Trades to Show:", ("Everyone","Ali","Ruslan","Sami","Yahya","Youssef","Santi","Shrey","Dani"))
    
    if manager != "Everyone":
        st.sidebar.image("fpl/pictures/{}.png".format(manager.lower()), caption=manager,width=200)

    st.sidebar.markdown("Page Guide")
    st.sidebar.markdown("1. [Total Transfers Ranking](#total-transfers-ranking)")
    st.sidebar.markdown("2. [Most Transferred In](#most-transferred-in)")
    st.sidebar.markdown("3. [Best & Worst Transfers](#best-and-worst-transfers)")

    st.subheader("Transfers Page")
    st.markdown("Quick view of the best and worst transactions in the AKOYA league")
    
    st.markdown("<hr>", unsafe_allow_html=True)

    st.subheader("Total Transfers Ranking")
    st.markdown("Brought to you weekly by Ali Ascioglu")

    #region Transfer Ranking
    data = pd.read_csv("fpl/findings/transfers/num_transfers.csv")
    tab1, tab2 = st.tabs(["Total Transfers","Table"])
    with tab1:
        display_podium("Total Transfers",data,"transfer_id","transfers")
    with tab2:
        st.write(data)
    #endregion

    st.markdown("<hr>", unsafe_allow_html=True)
    st.info("Next up the definition of a love hate relationship, let's look at...")

    st.subheader("Most Transferred In")
    st.markdown("The players you make sleep on the couch one night and come back to bed the next")

    #region Transfer In
    data = pd.read_csv("fpl/findings/transfers/most_in.csv")

    tab1, tab2 = st.tabs(["Most Transferred","Table"])
    with tab1:
        if manager=="Everyone":
            cols = st.columns(4)
            for i in range(4):
                with cols[i]:
                    show_player(data,i,"manager","times transferred")
                    show_player(data,i+4,"manager","times transferred")
        else:
            manager_df = data[data["manager"]==manager].reset_index(drop=True)
            cols = st.columns(2)
            for i in range(2):
                with cols[i]:
                    show_player(manager_df,i,"manager","times transferred")
    with tab2:
        st.write(data[["manager","player_name","player_id"]][:20])
    #endregion
    
    st.markdown("<hr>", unsafe_allow_html=True)
    st.info("Lastly, let's try to answer a question everyone has after getting a new player. Let's look at the...")

    st.subheader("Best and Worst Transfers")
    st.markdown("Just comparison of the highest scoring players in the first three weeks transferred in compared to the one traded out")

    #region Best and Worst Transfers
    data = pd.read_csv("fpl/findings/transfers/transfers_net_points.csv")
    trades = st.selectbox("Which ones do you want to see", ("Best Trades","Worst Trades"))

    if trades == "Worst Trades":
        data = data.sort_values(by="net_points",ascending=True).reset_index()
    else:
        data = data.sort_values(by="net_points",ascending=False).reset_index()

    tab1, tab2 = st.tabs(["Total Transfers","Table"])
    with tab1:
        if manager=="Everyone":
            df = data.rename(columns={"net_points":"player_id"})
            cols = st.columns(5)
            for i in range(5):
                with cols[i]:
                    show_player(df,i,"manager","net points")
                    show_player(df,i+5,"manager","net points")
        else:
            df = data[data["manager"]==manager].reset_index(drop=True).rename(columns={"net_points":"player_id"})
            cols = st.columns(5)
            for i in range(5):
                with cols[i]:
                    show_player(df,i,"manager","net points")
    with tab2:
        st.write(df[["gameweek","manager","player_id","player_name","team_in","player_name_out","team_out","in_points","out_points"]].rename(columns={"player_id":"net:points"}))
    #endregion

pages = {
    "Points": points,
    "Players": players,
    "General Stats" : stats,
    "Transfers" : transfers
}

# Streamlit app
def main():
    st.title("AKOYA FPL Draft Wrapped")
    st.markdown("Let's look back at this season")

    # Add sidebar navigation
    st.sidebar.subheader("Navigation")
    st.sidebar.info("Please use this sidebar for page navigation and to go to points of interest in each page")
    selection = st.sidebar.radio("Go to", list(pages.keys()))

    # Call the function based on selection
    pages[selection]()  


if __name__ == "__main__":
    main()