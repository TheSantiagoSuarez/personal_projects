import os
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import matplotlib.pyplot as plt

def overview():
    st.subheader("Overviews")

def transactions():
    st.subheader("Transaction History")

    transactions_df = pd.read_csv('clean_excels/transactions_2023_09.csv')
    transactions_df["Category"] = None
    transactions_df["Category"] = transactions_df["Category"].astype("category")
    transactions_df["Category"] = transactions_df["Category"].cat.add_categories(("Groceries", "Eating Out", "Eating Alone", "Transportation", "Personal", "Other"))

    st.experimental_data_editor(transactions_df, use_container_width=True, num_rows="fixed",)

def income():
    income_df = pd.read_csv('clean_excels/transactions_2023_09.csv')
    income_df = income_df[income_df["IMPORTE EUR"]>0]

    st.subheader("Income Tracker")

    st.write(income_df)

    grouped = income_df.groupby("payment_type").mean().reset_index()
    fig, ax = plt.subplots()
    ax.pie(grouped['IMPORTE EUR'], labels=grouped['payment_type'], autopct='%1.1f%%', startangle=90)
    ax.axis('equal')

    st.pyplot(fig)

def expenses():
    expenses_df = pd.read_csv('clean_excels/transactions_2023_09.csv')
    expenses_df = expenses_df[expenses_df["IMPORTE EUR"]<0]
    expenses_df["IMPORTE EUR"] = abs(expenses_df["IMPORTE EUR"])

    st.subheader("Income Tracker")

    st.write(expenses_df)

    grouped = expenses_df.groupby("payment_type").mean().reset_index()
    fig, ax = plt.subplots()
    ax.pie(grouped['IMPORTE EUR'], labels=grouped['payment_type'], autopct='%1.1f%%', startangle=90)
    ax.axis('equal')

    st.pyplot(fig)

pages = {
    "Overview": overview,
    "Transaction History": transactions,
    "Income Tracker" : income,
    "Expenses Analysis" : expenses
}

def main():
    st.title("My budgetting")
    st.markdown("Let's look back at this season")

    st.sidebar.subheader("Navigation")
    st.sidebar.info("Please use this sidebar for page navigation and to go to points of interest in each page")
    selection = st.sidebar.radio("Go to", list(pages.keys()))

    pages[selection]()  


if __name__ == "__main__":
    main()