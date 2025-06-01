import os
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import pickle

import fpl_methods as methods

print("HERE IS THE VERSION",pd.__version__)
print("HERE IS THE VERSION",st.__version__)

picture_path = os.path.dirname(__file__)+"/"

file_path = os.path.join(os.path.dirname(__file__), 'season_data.pickle')
raw_data = pd.read_pickle(file_path)

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
        st.image(picture_path+"pictures/{}.png".format(df.loc[1, "manager_short"].lower()))
        st.subheader("🥈") 
        st.text("{}: {} {}".format(df.loc[1, "manager_short"], round(df.iloc[1][column]),value))

    with col2:
        st.image(picture_path+"pictures/{}.png".format(df.loc[0, "manager_short"].lower()))
        st.subheader("🥇")
        st.text("{}: {} {}".format(df.loc[0, "manager_short"], round(df.iloc[0][column]),value))

    with col3:
        st.write("")
        st.write("")
        st.image(picture_path+"pictures/{}.png".format(df.loc[2, "manager_short"].lower()))
        st.subheader("🥉") 
        st.text("{}: {} {}".format(df.loc[2, "manager_short"], round(df.iloc[2][column]),value))

    with col4:
        st.write("")

    with col5:
        st.write("")
        st.write("")
        st.write("")
        st.write("")
        st.image(picture_path+"pictures/{}.png".format(df.loc[len(df)-1, "manager_short"].lower()))
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
                st.image(picture_path+"pictures/{}.png".format(win_manager.lower()),width=80)
            with cols2:
                st.image(picture_path+"pictures/{}.png".format(tied_manager.lower()),width=80)
            st.text("{} & {}:".format(win_manager,tied_manager))        
            st.text("{} {}".format(round(df.iloc[0]),metric))
        else:
            st.image(picture_path+"pictures/{}.png".format(win_manager.lower()),width=160)
            st.text("{}:".format(win_manager))        
            st.text("{} {}".format(round(df.iloc[0]),metric))

    with tab2:
        if df.iloc[len(df)-1]==df.iloc[len(df)-2]:
            tied_manager= df.index[len(df)-2]
            cols1,cols2 = st.columns(2)
            with cols1:
                st.image(picture_path+"pictures/{}.png".format(loss_manager.lower()),width=80)
            with cols2:
                st.image(picture_path+"pictures/{}.png".format(tied_manager.lower()),width=80)
            st.text("{} & {}:".format(loss_manager,tied_manager)) 
            st.text("{} {}".format(round(df.iloc[len(df)-1]),metric))
        else: 
            st.image(picture_path+"pictures/{}.png".format(loss_manager.lower()),width=160)
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
    if data.loc[num,"metric"]==38:
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
    elif points=="draft":
        st.markdown("In {} gws".format(data.loc[num,"gws"]))

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

    st.sidebar.image(picture_path+"pictures/{}.png".format(manager.lower()), caption=manager,width=200)

    st.sidebar.markdown("Page Guide")
    st.sidebar.markdown("1. [Loyalty](#loyalty)")
    st.sidebar.markdown("2. [Disappointments](#disappointments)")
    st.sidebar.markdown("3. [Most Teams](#most-teams)")
    st.sidebar.markdown("4. [Club Mascot](#club-mascot)")
    st.sidebar.markdown("4. [Season Ticket Holder](#season-ticket-holder)")
    st.sidebar.markdown("5. [Star Players](#star-players)")

    st.markdown(" ")
    st.info("Choosing who to have in your team was hard, unless you just chose Arsenal players and called it a day")
    st.info("Let's first look at who has stuck with you through thick and thin, and ask yourself how Youssed has gotten Salah for a third year in a row. Let's look at...")
    st.header("Loyalty")
    st.markdown("The players you've owned the longest")

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
    st.header("Disappointments")
    st.markdown("Those players that you tried, but let go basically immediately")
    
    #region Disappointments
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
    st.info("Now, a final farewell to Ruslan's scouting strategy")

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

def h2h(findings, data):
    st.subheader("Head to Head")
    st.markdown("For the Akoya Cup 3rd Edition, a repeat on the head to head format. It doesn't matter how many points you get, just if you beat the dickhead you're going up against.")
    st.markdown("Let's see how you did")
    
    manager = st.sidebar.selectbox("Choose Manager",["Everyone"]+[man.short_name for man in data["managers"]])
    manager_data = next((man for man in data["managers"] if man.short_name == manager), None)

    try:    
        st.sidebar.image(picture_path+"pictures/{}.png".format(manager.lower()), caption=manager,width=200)
    except:
        print("")
        
    st.sidebar.markdown("Page Guide")
    st.sidebar.markdown("1. [Season Battles](#season-battles)")
    st.sidebar.markdown("2. [Head to Head Stats](#head-to-head-stats)")
    st.sidebar.markdown("3. [Head to Head Record](#head-to-head-record)")

    
    st.header("Season Battles")
    st.markdown("A visualisation on some rivalries throughout the season")

    # region Season Battles

    tabs = st.tabs(["Turkish Derby","Youssef Derby","Deloitte Derby","The student that became the master","Pseudo El Clásico","Gooner Derby","Debutant Derby"])

    pairs = [("AA","ES"),("YE","YA"),("WN","SB"),("KS","ST"),("SL","SS"),("RK","YA1"),("pa","AB")]

    for i in range(len(tabs)):
        with tabs[i]:
            st.image(f"graphs/{pairs[i][0]}-{pairs[i][1]}_h2h.gif")

    # endregion
    
    st.header("Head to Head Stats")
    st.markdown("Some of the biggest wipeouts, closest ties, and other interesting info")

    # region Head to Head Stats

    data = findings["h2h"]
    tabs = st.tabs(["Wins", "Losses"])
    metric = ["Win", "Loss"]

    for i in range(2):
        if manager == "Everyone":
            df = data.loc[data["result"]==metric[i][0]]
        else:
            df = data.loc[(data["manager"] == manager)&(data["result"]==metric[i][0])]
        avg_pts = df["points"].mean()
        avg_opp_pts = df["opponent_points"].mean()

        with tabs[i]:
            cols = st.columns(2)
            with cols[0]:
                st.markdown(f"In your average {metric[i]}, you had")
                st.subheader(f"{round(avg_pts,2)} points")
            
            with cols[1]:
                st.markdown(f"In your average {metric[i]}, they had")
                st.subheader(f"{round(avg_opp_pts,2)} points")
            
            biggest = df.loc[df["point_diff"].abs()==max(df["point_diff"].abs())]
            closest = df.loc[df["point_diff"].abs()==min(df["point_diff"].abs())]
                
            st.markdown("<hr>", unsafe_allow_html=True)

            # Biggest Win / Loss
            st.subheader(f"Biggest {metric[i]}")
            st.markdown(f"In gameweek {biggest['gw'].values[0]}, the point difference was {biggest['point_diff'].values[0]} points")
            #st.subheader(f"{big_diff['point_diff'].values[0]} points")

            cols = st.columns(4)
            with cols[0]:
                man = biggest['manager'].values[0]
                st.image(picture_path+"pictures/{}.png".format(man.lower()), caption=man)
            with cols[1]:
                st.subheader(f"{biggest['points'].values[0]} points")
            with cols[2]:
                opp_manager = biggest['opponent'].values[0].short_name
                st.image(picture_path+"pictures/{}.png".format(opp_manager.lower()), caption=opp_manager)
            with cols[3]:
                st.subheader(f"{biggest['opponent_points'].values[0]} points")
            
            st.markdown("<hr>", unsafe_allow_html=True)
            
            # Closest Win / Loss
            st.subheader(f"Closest {metric[i]}")
            st.markdown(f"In gameweek {closest['gw'].values[0]}, the point difference was {closest['point_diff'].values[0]} points")
            #st.subheader(f"{big_diff['point_diff'].values[0]} points")

            cols = st.columns(4)
            with cols[0]:
                man = closest['manager'].values[0]
                st.image(picture_path+"pictures/{}.png".format(man.lower()), caption=man)
            with cols[1]:
                st.subheader(f"{closest['points'].values[0]} points")
            with cols[2]:
                opp_manager = closest['opponent'].values[0].short_name
                st.image(picture_path+"pictures/{}.png".format(opp_manager.lower()), caption=opp_manager)
            with cols[3]:
                st.subheader(f"{closest['opponent_points'].values[0]} points")


    # endregion
    
    st.header("Head to Head Record")
    st.markdown("Let's look at the most one sided rivalries")

    # region H2H Record
    if manager=="Everyone":
        df = data
    else:
        df = data.loc[(data["manager"] == manager)]

    df["opponent"] = df["opponent"].apply(lambda x: x.short_name)
    h2h_df = pd.pivot_table(df, index=["manager","opponent"],columns="result",values="gw",aggfunc="count").sort_values("W",ascending=False).reset_index()

    if manager == "Everyone":
        h2h_df= h2h_df[:13] 

    cols = st.columns(3)
    with cols[1]:
        st.subheader("W - D - L")

    st.markdown("<hr>", unsafe_allow_html=True)

    for i in range(len(h2h_df)):    
        cols = st.columns(3)
        row = h2h_df.loc[i]

        with cols[0]:
            man = row['manager']
            st.image(picture_path+"pictures/{}.png".format(man.lower()), caption=man,width=100)

        with cols[1]:
            wins = 0 if pd.isna(row['W']) else int(row['W'])
            losses = 0 if pd.isna(row['L']) else int(row['L'])
            try:
                draws = 0 if pd.isna(row['D']) else int(row['D'])
                st.subheader(f"{wins} - {draws} - {losses}")
            except:
                st.subheader(f"{wins} - 0 - {losses}")

        with cols[2]:
            opp_manager = row['opponent']
            st.image(picture_path+"pictures/{}.png".format(opp_manager.lower()), caption=opp_manager,width=100)
        
        st.markdown("<hr>", unsafe_allow_html=True)



    # endregion

def draft(findings, data):
    st.subheader("Draft")
    st.markdown("Some people might say FPL isn't about skill, it's all about who gets Salah, Haaland, or every Arsenal player")
    st.markdown("Let's see how everyone else's 4th to 15th picks were better than yours")
    
    manager = st.sidebar.selectbox("Choose Manager",[man.short_name for man in data["managers"]])
    manager_data = next((man for man in data["managers"] if man.short_name == manager), None)

    st.sidebar.image(picture_path+"pictures/{}.png".format(manager.lower()), caption=manager,width=200)


    st.header("Draft Picks")
    st.markdown("The best excuse for whoever doesn't do well")

    # region draft picks

    data = findings["draft_picks"]

    tabs = st.tabs(["1st","2nd","3rd","4th","5th","6th","7th","8th","9th","10th","11th","12th","13th","14th","15th"])

    for pick_num in range(1,len(tabs)+1):
        picks = data[data["pick"]==pick_num].sort_values("points",ascending=False).reset_index(drop=True)
        
        with tabs[pick_num-1]:
            cols = st.columns(3)         
            for i in range(3):
                with cols[i]:
                    show_player(picks.rename(columns={"points":"metric"}),i,"draft","points")
                    if picks.loc[i,"manager_short"]==manager:
                        st.success(manager)
                    else:
                        st.markdown(picks.loc[i,"manager_short"])
            
            cols = st.columns(5)          
            for i in range(5):
                with cols[i]:
                    show_player(picks.rename(columns={"points":"metric"}),i+3,"draft","points")
                    if picks.loc[i+3,"manager_short"]==manager:
                        st.success(manager)
                    else:
                        st.markdown(picks.loc[i+3,"manager_short"])
            
            cols = st.columns(6)       
            for i in range(6):
                with cols[i]:
                    show_player(picks.rename(columns={"points":"metric"}),i+8,"draft","points")
                    if picks.loc[i+8,"manager_short"]==manager:
                        st.success(manager)
                    else:
                        st.markdown(picks.loc[i+8,"manager_short"])
    # endregion



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
        st.sidebar.image(picture_path+"pictures/{}.png".format(manager.lower()), caption=manager,width=200)

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
        st.write(df[["gameweek","manager_short","player_name","player_out_name","in_pts","out_pts"]])
    #endregion

pages = {
    "Total Points": points,
    "Players": players,
    "Draft": draft,
    "Head-to-head":h2h,
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

    file_path = os.path.join(os.path.dirname(__file__), 'season_findings.pickle')
    findings = pd.read_pickle(file_path)

    file_path = os.path.join(os.path.dirname(__file__), 'season_data.pickle')
    data = pd.read_pickle(file_path)

    main(findings, data)