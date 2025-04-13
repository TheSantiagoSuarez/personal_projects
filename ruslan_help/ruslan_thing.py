import json
import pandas as pd
import os
import openpyxl

os.fsencode("240815_174104_FP.json")

# Get the current directory
current_directory = os.getcwd()
df = pd.DataFrame(columns=["ID", "Driver", "Best Lap", "Car Model", "file"])

# Iterate through files in the current directory
for file_name in os.listdir(current_directory):
    # Check if it's a file (and not a directory)
    if file_name.endswith(".json"): 
        print(file_name)
        with open(file_name, 'r', encoding='utf-16-le') as file:
            data = json.load(file)

        for player in data["sessionResult"]["leaderBoardLines"]:
            car = player["car"]
            car_model = car["carModel"]
            best_time = player["timing"]["bestLap"]/1000
            driver = car["drivers"][0]["lastName"]
            driver_ID = car["drivers"][0]["playerId"]
            
            row = {"ID":driver_ID, "Driver":driver, "Best Lap": best_time, "Car Model": car_model, "file": file_name}
            row = pd.DataFrame([row],index=[len(df)+1])
            df = pd.concat([df,row])

final = df.groupby('ID', group_keys=False).apply(lambda x: x.loc[x["Best Lap"].idxmin()]).drop(columns=["ID"]).sort_values("Best Lap")

final.to_excel("output.xlsx")