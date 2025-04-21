import pandas as pd
import pickle
from functools import reduce

import fpl_methods as methods

def main():
    with open ('season_data.pickle','rb') as file:
        data = pickle.load(file)


    current_gw = max(data["managers"][0].picks)

    managers = data["managers"]
    players = data["players"]
    transfers = data["transfers"]
    team = data["teams"]

    findings = {}