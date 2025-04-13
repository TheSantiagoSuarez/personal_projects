import pandas as pd
import gspread
import string

def clean_text(text):
    return text.strip(string.punctuation).strip()

def get_type(transaction):
    pay_method = transaction.split(" ")[0]

    if pay_method == "Pago":
        return_type = " ".join(transaction.split(" ")[0:2])
    elif pay_method == "Transaccion":
        return_type = " ".join(transaction.split(" ")[0:2])
    else:
        return_type = transaction.split(" ")[0]
    
    return return_type

def get_detail(transaction):
    payment_split = transaction.split(" ")
    pay_method = payment_split[0]
    
    return_detail = ""

    if pay_method == "Pago":
        return_detail = " ".join(transaction.split(" ")[3:]).split(",")[0]
    elif pay_method == "Compra":
        return_detail = " ".join(transaction.split(" ")[1:]).split(",")[0]
    elif pay_method == "Transferencia":
        if payment_split[1] == "A":
            return_detail = " ".join(payment_split[4:])
        elif payment_split[1] == "De":
            return_detail = " ".join(payment_split[2:])
    elif pay_method == "Bizum":
        return_detail = " ".join(payment_split[2:])
    elif pay_method == "Transaccion":
        return_detail = " ".join(transaction.split(" ")[3:]).split(",")[0]
    elif pay_method == "Recibo":
        return_detail = " ".join(payment_split[1:3])

    return return_detail

def categorise(tag,category):
    df.loc[df['payment_concepto'].str.contains(tag, case=False, na=False), 'payment_type'] = category

year = "2025"
month = "03"

df = pd.read_excel(f"raw_excels/{year}_{month}.xls")
df.columns = df.iloc[6]
df = df.iloc[7:].reset_index(drop=True)

df["payment_type"] = df["CONCEPTO"].apply(get_type)
df["payment_detail"] = df["CONCEPTO"].apply(get_detail)
df["payment_concepto"] = df["payment_detail"].apply(lambda x : x.split("Concepto")[1] if "Concepto" in x else "")
df["payment_detail"] = df["payment_detail"].apply(lambda x : x.split("Concepto")[0])

categorise("Nomina", "Nomina")

transactions = df.drop(["CONCEPTO","FECHA VALOR","SALDO"],axis=1)
transactions['payment_detail'] = transactions['payment_detail'].apply(clean_text)
transactions['payment_concepto'] = transactions['payment_concepto'].apply(clean_text)



gc = gspread.service_account()
sh = gc.open("Personal Finances")
wks = sh.worksheet("Raw_Data")

spread_data = transactions.values.tolist()
wks.insert_rows(spread_data, 2)
