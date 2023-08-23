
# 沒有最新數據@@
# with open("CIK0000320193__companyconcept.json") as jsonfile:
#     data = json.load(jsonfile)

#     print(type(data))

#     print(data.keys())

#     print(data['facts'].keys())
#     print(data['facts']["us-gaap"].keys())
#     print(data['facts']["us-gaap"]["Revenues"].keys())
#     print(data['facts']["us-gaap"]["Revenues"]["units"]["USD"])


# 也沒有最新數據@@
# with open("CIK0001318605__companyfacts.json") as jsonfile:
#     data = json.load(jsonfile)
#     print(data.keys())
#     print(data['facts'].keys())
#     print(data['facts']["us-gaap"].keys())
#     print(data['facts']["us-gaap"]["Revenues"].keys())
#     print(data['facts']["us-gaap"]["Revenues"]["units"]["USD"])


# 不是每家公司都會提供，沒辦法透過api去抓資料
# with open("CY2019Q1I.json", encoding="utf-8") as jsonfile:
#     data = json.load(jsonfile)
#     print(data.keys())
#     print(data["data"][20])




#====================================================================================
#====================================================================================
# 老老實實的自己下載財報，然後處理數據
# 資料來源: morningstar.com >> 公司 >> Financials >> 財報類型 >> Quarterly >> Expand Detail View >> Export Data


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from tkinter import Tk, filedialog
import re
import os
from datetime import datetime
# from matplotlib.pyplot import MultipleLocator
# import json



# Step 1: 選擇檔案並匯入
def import_files():
    root = Tk()
    root.withdraw()  # Hide small tkinter window

    income_statements = None
    cash_flow = None
    balance_sheet = None

    file_paths = filedialog.askopenfilenames(filetypes=(("xls", "*.xls"),))
    if len(file_paths) != 3:
        return None
    

    for path in file_paths:        
        if re.search("Income Statement_", path):
            income_statements = pd.ExcelFile(path)
        
        elif re.search("Cash Flow_", path):
            cash_flow = pd.ExcelFile(path)
            # print(cash_flow.sheet_names)

        elif re.search("Balance Sheet_", path):
            balance_sheet = pd.ExcelFile(path)

        else:
            print("No file name matched.")

    
    return income_statements, cash_flow, balance_sheet


# Step 2: 建立目標公司的資料夾
def build_dir(*dataframes):
    if any(dataframe is None for dataframe in dataframes):
        print("Missing one or more type of financial statements. Please re-import again.")
        return False
    
    abbr = dataframes[0].sheet_names[0]
    if all(dataframe.sheet_names[0] == abbr for dataframe in dataframes):
        print(len(dataframes))
        current_dir = os.getcwd()
        if not os.path.isdir(os.path.join(current_dir, "results")):
            os.mkdir(os.path.join(current_dir, "results"))
            print("Directory", os.path.join(current_dir, "results"), "is built successfully!")
        else:
            print("Directory 'results' has been built.")

        
        directory = datetime.now().strftime("%Y-%m-%d") + ' ' + abbr
        if not os.path.isdir(os.path.join(current_dir, "results", directory)):
            os.mkdir(os.path.join(current_dir, "results", directory))
            print("Directory", os.path.join(current_dir, "results", directory), "is built successfully!")
        else:
            print('Directory',  os.path.join(current_dir, "results", directory), 'has been built.')


        return True

    else:
        print("Please check the selected files and re-import again.")

    return False
        

# Step 3: Process data and export figures
def process(quarter_num, *results):
    income_statements = results[0].parse(index_col = 0)
    cash_flow = results[1].parse(index_col = 0)
    balance_sheet = results[2].parse(index_col = 0)

    # print(quarter_num)
    print(balance_sheet.info())

    data_columns = income_statements.columns[-(quarter_num + 1):-1]
    print(data_columns)
    
    # print(data_index)
    def find_index(name, df):
        for idx, val in enumerate(df.index):
            if re.search(name, val.strip()):
                return idx

        return None


    data_index = ["Total Assets", "Total Liabilities","Total Equity","Inventories","Total Revenue"]
    data = [
        balance_sheet.iloc[find_index(data_index[0], balance_sheet), -quarter_num :],
        balance_sheet.iloc[find_index(data_index[1], balance_sheet), -quarter_num :],
        balance_sheet.iloc[find_index(data_index[2], balance_sheet), -quarter_num :],
        balance_sheet.iloc[find_index(data_index[3], balance_sheet), -quarter_num :],
        income_statements.iloc[find_index(data_index[4], income_statements), -(quarter_num + 1):-1]
    ]

    return pd.DataFrame(data = data, index = data_index, columns = data_columns)






    



if __name__ == "__main__":
    quarter_num = 8


    results = import_files()
    go_next_step = build_dir(*results) if results is not None else print("Please check the selected files and re-import again.")
    
    if go_next_step:
        print("GoGo!")
        result = process(8, *results)
        print(result)

    else:
        print("No~~~")
    
    print("Finished!")



