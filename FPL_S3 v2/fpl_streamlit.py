import os
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import pickle

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



def points(findings, data):
    st.sidebar.markdown("Page Guide")
    st.sidebar.markdown("1. [Akoya FPL Award](#akoya-fpl-award)")
    st.sidebar.markdown("2. [Rankings per Position](#rankings-per-position)")
    st.sidebar.markdown("3. [Outside the starting 11](#outside-the-starting-11)")
    st.sidebar.markdown("4. [Gameweek Winners and Losers](#gameweek-winners-and-losers)")
    
def players(findings):
    st.subheader("Players Page")
    st.markdown("Some individual and group facts about players in the AKOYA league. Please choose a manager in the sidebar")

    manager = st.sidebar.selectbox("Choose Manager", ("YE","WN","SL","RK","ST","SS","AA","YA1","SB","YA","ES","AC"))

    st.sidebar.image("pictures/{}.png".format(manager.lower()), caption=manager,width=200)

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
    manager = st.sidebar.selectbox("Choose Manager",[man.short_name for man in data["managers"]])
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