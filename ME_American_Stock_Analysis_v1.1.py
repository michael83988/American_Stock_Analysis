#!/usr/bin/env python
# coding: utf-8

# In[ ]:


#!/usr/bin/env python
# coding: utf-8

# # American Stock Analysis
# This project is aimed to get a specific company's financial statements of America from [U.S. Securities And Exchange Commission (SEC)](https://www.sec.gov/), including 
# - Consolidated statements of operations (income statements)
# - Consolidated statements of comprehensive income
# - Consolidated balance sheet
# - Consolidated statement of cash flows
# 
# Besides getting information about the company's financial statements, some important indicators such as ROA, gross margin, etc, are also calculated and the visualization of them is accomplished subsequently.
# 
# Financial statements of the targeted company is obtained from 10-K and 10-Q reports, searched from [EDGAR|Company Filings](https://www.sec.gov/edgar/searchedgar/companysearch).
# 
# 
# <br><br>
# <b>Technical references:</b>
# - [Python 多執行緒 threading 模組平行化程式設計教學](https://blog.gtwang.org/programming/python-threading-multithreaded-programming-tutorial/)

# ## Package used in this module

# In[1]:
print("Importing related packages and modules ...")

# import requests
from bs4 import BeautifulSoup as BS
from bs4 import NavigableString
import time
from dateutil import parser
from datetime import datetime
import re
import os
#from lxml import etree
import numpy as np
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys



import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from matplotlib.pyplot import MultipleLocator


# Multithreading
import threading


# Encrypt and decrypt
from cryptography.fernet import Fernet

# GUI part
import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from PIL import Image, ImageTk    # Deal with images
import json


# ## Global variables

# In[2]:


# Global variables
# company_name = ""
# industry_type = ""
# target_stock = ""
msgs = []
IS_ACTIVATE = False  # To determine whether updating message or not
expiration_date = datetime.strptime("2024-06-17", "%Y-%m-%d")  # Change expiration date here!
#print(expiration_date)
# contents = tk.StringVar()


# ## Function definition: For GUI

# In[3]:

print("Defining used functions ...")

def update_msg(msg):
    global msgs
    global contents 
    global IS_ACTIVATE
    global listbox
    
    if IS_ACTIVATE:
        msgs.append(msg)
        contents.set(msgs)
    
    
    # Scroll to the end
    listbox.see("end")


# ## Function definition: Get data from sec.gov

# In[4]:


# For test
# target_stock = "APPL"
# target_stock = "TSLA"
# target_stock = "KO"
# target_stock = "JNJ"
# target_stock = "哈哈ㄏ阿"
# target_stock = "GOOGL"  # Order data have smaller fact-identifier! Special case!
# target_stock = "MSFT"  # Special case in cash flows
# target_stock = "BAC"  # title is included in table!
# target_stock = "GS"



def get_source(target_stock, quarter_num, stop_flag):
    global msgs

    #print(quarter_num)
    
    try:
        # Process 1: Get financial statements from SEC.gov
        # Visit "EDGAR | Company Filings" of SEC.gov to search for a targeted company
        #print('Start connecting ...')
        update_msg("Start connecting ..." if IS_ENGLISH else "開始連線 ...")
        
        browser = webdriver.Edge(r"msedgedriver.exe")    # Start webdriver.exe
        time.sleep(np.random.rand() + 2)    # Give 2.0 ~ 3.0 seconds for opening the webdriver.ext
       
        # Break point
        if(stop_flag.is_set()):
            return None

        
        url_search = "https://www.sec.gov/edgar/searchedgar/companysearch"

        browser.get(url_search)
        time.sleep(np.random.rand() + 2)    # Give 2.0 ~ 3.0 seconds for loading web content from server
        
        # Break point
        if(stop_flag.is_set()):
            return None

        # Find input element to enter the target stock abbreviation and press enter
        stock_input = browser.find_element(By.ID, "edgar-company-person")
        stock_input.send_keys(target_stock)
        time.sleep(np.random.rand() + 1)
        
        # Break point
        if(stop_flag.is_set()):
            return None

        stock_input.send_keys(Keys.ENTER)
        time.sleep(np.random.rand() + 2)    # Hold 2 ~ 3 seconds for loading content from server
        
        # Break point
        if(stop_flag.is_set()):
            return None



        # # Find the submit button to search for the result
        # submit = browser.find_element(By.CLASS_NAME, "collapsed-submit")

        # # Input the stock abbr. and submit
        # stock_input.send_keys(target_stock)
        # submit.click()


        # Click "View all 10-Ks and 10-Qs" button
        # If no matching companies is showed, then prompt retry message
        find_result_check = BS(browser.page_source, "html.parser").find('div', id='contentDiv')

        # if not re.search(r".*No matching companies\..*", find_result_check):
        # if not re.search(r".*No matching companies\..*", ):
        # if (not browser.find_element(By.XPATH, '//*[@id="contentDiv"]/div')):
        if not find_result_check:
            #print("Getting reports of ", target_stock, " from SEC.gov ...")
            msg = "Getting reports of " + target_stock + " from SEC.gov ..." if IS_ENGLISH else "從SEC.GOV取得" + target_stock + "的財報 ..."
            update_msg(msg)

            # Click "Selected Filings>>10-K (annual reports) and 10-Q (quarterly reports)"
            annual_quarterly_report = browser.find_element(By.XPATH, '//*[@id="filingsStart"]/div[2]/div[3]/h5')         
            if annual_quarterly_report:
                #annual_quarterly_report = browser.find_element(By.XPATH, '//*[@id="filingsStart"]/div[2]/div[3]/h5')
                annual_quarterly_report.click()
                time.sleep(np.random.rand() + 1)    # Wait for 1 ~ 2 seconds
            else:
                update_msg("No 10-K and 10-Q reports provided. Please try another company." if IS_ENGLISH else "無10-K與10-Q財報。請輸入其他公司。")
                return None
            
            
            
            # Break point
            if(stop_flag.is_set()):
                return None

            
            
            # Click "View all 10-Ks and 10-Qs"
            all_KQs = browser.find_element(By.XPATH, '//*[@id="filingsStart"]/div[2]/div[3]/div/button[1]')
            all_KQs.click()
            
                

            # Add this part will cause reports clicked lack of 1? -> OK! .clear() method will automatically press enter key!
            # Clear reports' "From Date"
            from_date = browser.find_element(By.ID, "filingDateFrom")
            from_date.clear()
            time.sleep(np.random.rand() + 1)
    #         from_date.send_keys(Keys.ENTER)
    #         time.sleep(np.random.rand() + 3)

    
            # Break point
            if(stop_flag.is_set()):
                return None


            # To get customized number of  quarterly report (including 10-K reports and 10-Q reports), first n files needs scanned
            reports = list()  # To store 8 HTMLs of financial statements
            company_name = browser.find_element(By.ID, "name").text

            # Get current window handle
            # Because when clicking the linkage of report, new tab will be created. 
            # Need to switch back to the original web page to get another report of different quarter.
            # current_window = browser.current_window_handle
            # print(current_window)

            # Parameters for requests
#             user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
#             headers = {'user-agent': user_agent}


            # Get first 8 10-K or 10-Q reports
            #try:
            # Count the amount of filed reports without duplication (Reporting date must be unique)

            # reports_count = 8 if len(browser.find_elements(By.XPATH, '//*[@id="filingsTable"]/tbody/tr')) >= 8 else len(browser.find_elements(By.XPATH, '//*[@id="filingsTable"]/tbody/tr'))
            reports_count = len(browser.find_elements(By.XPATH, '//*[@id="filingsTable"]/tbody/tr'))
            #print('reports count: ', reports_count)


            # For test
            # xpath = '//*[@id="filingsTable"]/tbody/tr[1]/td[2]/div/a[1]'
            # report_link = browser.find_element(By.XPATH, xpath)
            # time.sleep(np.random.rand() + 1)
            # report_link.click()


            # A set to store reporting date
            reporting_date = set()


            # Open financial statements of search result from SEC.gov
            for i in range(reports_count):
                # Break point
                if(stop_flag.is_set()):
                    return None
                
                
                xpath_date = '//*[@id="filingsTable"]/tbody/tr[' + str(i + 1) + ']/td[4]/a'                

                xpath = '//*[@id="filingsTable"]/tbody/tr[' + str(i + 1) + ']/td[2]/div/a[1]'

                check_amendment = re.compile(r"amendment")
                check_inability_to_timely_file = re.compile("inability to timely file")

                # APPL: //*[@id="filingsTable"]/tbody/tr[1]/td[4]/a
                # TSLA: //*[@id="filingsTable"]/tbody/tr[1]/td[4]/a
                #     # Record current window ID for switching between tabs of browser
                #     reports_window = browser.current_window_handle

                # args = (By.XPATH, xpath)

                if(len(reporting_date) < (int(quarter_num) + 1)):
                    if(not check_amendment.search(browser.find_element(By.XPATH, xpath).text) and not check_inability_to_timely_file.search(browser.find_element(By.XPATH, xpath).text)):
                        reporting_date.add(browser.find_element(By.XPATH, xpath_date).text)
                        report_link = browser.find_element(By.XPATH, xpath)
                        time.sleep(np.random.rand() + 1.5)
                        report_link.click()
                        time.sleep(np.random.rand() + 2)

                    else:
                        continue


                elif(len(reporting_date) >= (int(quarter_num) + 1)):
                    break
                else:
                    #print("Something wrong when clicking report link!")
                    update_msg("Something wrong when clicking report link!" if IS_ENGLISH else "開啟財報連結出現錯誤！")
                    break




            # Get HTMLs from web tabs
            # Record new tab of window ID, string type
            new_windows = browser.window_handles

            # Get current window handle
            current_window = browser.current_window_handle

            for window in new_windows:
                if(window != current_window):
                    browser.switch_to.window(window)
                    time.sleep(np.random.rand() + 1.5)
                    
                    # Break point
                    if(stop_flag.is_set()):
                        return None
                    
                    
                    report = BS(browser.page_source, "html.parser")
                    url = browser.current_url
                    #date_match = re.search(r"([-_]\d{8}).*\.htm$", url)

                    # (BeautifulSoup object, url, date)
    #                 date = None
    #                 if not date_match:
    #                     date = parser.parse(report.find(name = "ix:nonnumeric", attrs = {"name" : "dei:DocumentPeriodEndDate"}).text)
    #                 else:
    #                     date = parser.parse(date_match.group(1))

                    date = parser.parse(report.find(name = "ix:nonnumeric", attrs = {"name" : "dei:DocumentPeriodEndDate"}).text  if report.find(name = "ix:nonnumeric", attrs = {"name" : "dei:DocumentPeriodEndDate"}) else list(reporting_date)[new_windows.index(window) - 1])
                    reports.append((report, url, date))
            
                    if(len(reports) <= 1):
                        pass
                    elif(len(reports) == 2):
                        #print(len(reports) - 1, " report is gotten.")
                        msg = str(len(reports) - 1) + " report is gotten." if IS_ENGLISH else "取得" + str(len(reports) - 1) + "份財報"
                        update_msg(msg)
                    else:
                        #print(len(reports) - 1, " reports are gotten.")
                        msg = str(len(reports) - 1) + " reports are gotten." if IS_ENGLISH else "取得" + str(len(reports) - 1) + "份財報"
                        update_msg(msg)







            """
            # This section is bulit elsewhere. It will be replaced after the program of this part is completed.
            # Process 2: Extract financial statements from the collected HTMLs
            # Format settings of dataframe
            report_data = []
            report_index = []
            report_column = []

            for report in reports:
                print(type(report))

            # Differnt type of stocks (company and financial industry)
            # Financial industry has no inventories. It's a industry earning money by money! Different measurement needs to be implyed.
            """
            #print("All reports collected completely!")
            update_msg("All reports collected completely!" if IS_ENGLISH else "成功取得所有財報！")



        else:
            #print('Execute else statement ...') 
            #print('No matching companies. Please try again.')
            update_msg("No matching companies. Please try again." if IS_ENGLISH else "查無此公司。請輸入其他公司。")
            browser.quit()  # Close the webdriver.exe 
            return None



        # except:
            #print('Can not get 10-K or 10-Q reports from SEC.gov!')
        # finally:
        #     pass
        #     browser.close()

         
        return (reports, company_name)
    
    
    except Exception as e:
        #print("Something wrong while getting reports from SEC.gov")
        update_msg(str(e))
        
    finally:
        browser.quit()  # Close the webdriver.exe
        #print("End connecting ...")        
        update_msg("End connecting ..." if IS_ENGLISH else "中斷連線 ...")




# ## Function definition: Data processing

# In[5]:


# Check the report type (10-K or 10-Q)
def check_report_type(soup):
    # print(str(soup))
    #test_list = soup.find_all("ix:nonnumeric", {"id" : re.compile(r"fact-identifier-\d+")})
    #test_list = soup.find_all("ix:nonnumeric", {"name" : "dei:DocumentType"})
    # print(test)
    # test = etree.HTML(str(soup)).xpath('//*[@id="dynamic-xbrl-form"]/div[10]/table/tbody/tr[2]/td[2]/span')[0].text
    
    IS_QUARTERLY = soup.find("ix:nonnumeric", {"name" : "dei:DocumentQuarterlyReport"})
    REPORT_FORM = soup.find("ix:nonnumeric", {"name" : "dei:DocumentType"})
    IS_ANNUAL = soup.find("ix:nonnumeric", {"name" : "dei:DocumentAnnualReport"})
    IS_TRANSITION = soup.find("ix:nonnumeric", {"name" : "dei:DocumentTransitionReport"})
    
    # 遍立每個test才能決定是哪個報表!! -> 不需要了!
#     if(any(test.string == "10-Q" for test in test_list)):
#         return 'Q'
#     elif(any((test.string == "10-K")for test in test_list)):
#         return 'K'
#     else:
#         return "Drop"

    if((IS_QUARTERLY and re.search("[☑☒X]",IS_QUARTERLY.string)) or (IS_TRANSITION and re.search("[☑☒X]", IS_TRANSITION.string)) or (REPORT_FORM and re.search("10-Q", REPORT_FORM.string))):
        return 'Q'
    elif((IS_ANNUAL and re.search("[☑☒X]", IS_ANNUAL.string)) or (REPORT_FORM and re.search("10-K", REPORT_FORM.string))):
        return 'K'
    else:
        return "Drop"


# Different companies have different scale of industry -> Not all monetary unit is i"in million"! -> Depends on "scale"
def transform_to_number(soup):
    number = 0
    if soup:
        # print(soup.text.replace(',', ''))
        number = float(soup.text.replace(',', '')) if (soup.text != '—' and soup.text != '$') else np.nan
        #number *= np.power(10, (float(soup["scale"]) - 6)) if (soup["decimals"] != "2") else 1
        number *= np.power(10, (float(soup["scale"]))) if soup.has_attr("scale") else 1
        number = number if ((soup.has_attr("isnegativesonly") and soup["isnegativesonly"] == "false") or (not soup.has_attr("isnegativesonly") and not re.search("\(.*\)",soup.parent.parent.text))) else -number
    else:
        number = np.nan
        
    #print("transformed number: ", number)
    return number


# Get data from table
def extract_data(tables, pattern, iscalculationsonly, position):
    
    # table: The source of data
    # pattern: The pattern of "name" tag. Different data have their own patterns
    # iscalculationsonly: Feature to further focus on the targeted tag of data
    # position: The position of the targeted data
    
    temp_list = []
    for table in tables:
        if iscalculationsonly:
            temp_list.extend(table.find_all(name = "ix:nonfraction", attrs = {"name" : re.compile(pattern), "iscalculationsonly" : re.compile(iscalculationsonly)}))
        else:
            temp_list.extend(table.find_all(name = "ix:nonfraction", attrs = {"name" : re.compile(pattern)}))
    
    data_tag = sorted(temp_list, key = lambda x : int(re.search(r"\d+", x.get("id")).group(0)))[position] if len(temp_list) - 1 >= position else None
    #print(data_tag)
    data = transform_to_number(data_tag)
    temp_list.clear()
#     table.clear()
    return data
    
#     if(isinstance(position, int)):
#         data_tag = sorted(temp_list, key = lambda x : int(re.search(r"\d+", x.get("id")).group(0)))[position] if len(temp_list) - 1 >= position else None
#         data = transform_to_number(data_tag)
#         temp_list.clear()
#     #     table.clear()
#         return data
    
#     elif(isinstance(position, str)):
#         if(position == "GET_MAX"):
#             data_tags = sorted(temp_list, key = lambda x : int(re.search(r"\d+", x.get("id")).group(0))) if len(temp_list) - 1 > 0 else None
#             datas = [transform_to_number(data_tag) for data_tag in data_tags]
#             data = max(datas)
#             return data
#         else:
#             pass
#     else:
#         print("Unknown parameter")
#         return None
    

def check_industry_type(soup):
    test_list = soup.find_all("ix:nonfraction", {"name" : re.compile(r"^us-gaap:Inventory"), "iscalculationsonly" : "true"})
    
    if(len(test_list) == 0):
        return "F"
    elif(len(test_list) > 0):
        return "N"
    else:
        #print("Unknown industry type")
        return "U"

# Visualization of data


# ## Function definition: Extract data and build dataframe
# Need to update the portion of special cases.

# In[6]:


# For executing this module first time, please execute the above program first, then "reports" are obtained.
# Build program of section 2 -> OK!
# Extract data from reports
# Need to consider some special case. Like GOOGLE

def extract_from_reports(reports, industry_type, special_case = None, stop_flag = None):
    
    #Default settings
    #Filter tag functions
    def find_table_operations(tag):
        if(tag.name == "span" and title_regex.search(tag.text) and type(tag.contents[0]) is NavigableString):
            return True
        return False
    
    def find_table_comprehensive(tag):
        if(tag.name == "span" and title_regex.search(tag.text) and type(tag.contents[0]) is NavigableString):
            return True
        return False
    
    def find_table_balance(tag):
        if(tag.name == "span" and title_regex.search(tag.text) and type(tag.contents[0]) is NavigableString):
            return True
        return False
    
    def find_table_cashflow(tag):
        if(tag.name == "span" and title_regex.search(tag.text) and type(tag.contents[0]) is NavigableString):
            return True
        return False
    
    def find_table_credit(tag):
        if(tag.name == "span" and title_regex.search(tag.text) and type(tag.contents[0]) is NavigableString):
            return True
        return False
    
    
    
    def find_table_balance_nested(tag):
        #print("Overwrite success!")
        if(tag.name == "table" and any((element.name == "span" and title_regex.search(element.text)) for element in tag.descendants)):
            return True
        return False

    def find_table_operations_nested(tag):
        #print("Overwrite success!")
        if(tag.name == "table" and any((element.name == "span" and title_regex.search(element.text)) for element in tag.descendants)):
            return True
        return False

    def find_table_comprehensive_nested(tag):
        #print("Overwrite success!")
        if(tag.name == "table" and any((element.name == "span" and title_regex.search(element.text)) for element in tag.descendants)):
            return True
        return False

    def find_table_cashflow_nested(tag):
        #print("Overwrite success!")
        if(tag.name == "table" and any((element.name == "span" and title_regex.search(element.text)) for element in tag.descendants)):
            return True
        return False

    def find_table_credit_nested(tag):
        if(tag.name == "table" and any((element.name == "span" and title_regex.search(element.text)) for element in tag.descendants)):
            return True
        return False
    
    def find_table_risk_weighted_assets_nested(tag):
        if(tag.name == "table" and any((element.name == "span" and title_regex.search(element.text)) for element in tag.descendants)):
            return True
        return False
   
    def find_risk_weighted_assets(tag):
        #if(tag.name = "span" and tag.parent.)
        pass

    # Title patterns
    title_pattern_balance = "[oO][nN][sS][oO][lL][iI][dD][aA][tT][eE][dD] [bB][aA][lL][aA][nN][cC][eE] [sS][hH][eE][eE][tT][sS]?"
    title_pattern_comprehensive = "[oO][nN][sS][oO][lL][iI][dD][aA][tT][eE][dD] [sS][tT][aA][tT][eE][mM][eE][nN][tT][sS]? [oO][fF] [cC][oO][mM][pP][rR][eE][hH][eE][nN][sS][iI][vV][eE] [iI][nN][cC][oO][mM][eE]"
    title_pattern_operations = "[oO][nN][sS][oO][lL][iI][dD][aA][tT][eE][dD] [sS][tT][aA][tT][eE][mM][eE][nN][tT][sS]? [oO][fF] [oO][pP][eE][rR][aA][tT][iI][oO][nN][sS]|[oO][nN][sS][oO][lL][iI][dD][aA][tT][eE][dD] [sS][tT][aA][tT][eE][mM][eE][nN][tT][sS]? [oO][fF] [iI][nN][cC][oO][mM][eE]|[oO][nN][sS][oO][lL][iI][dD][aA][tT][eE][dD] [sS][tT][aA][tT][eE][mM][eE][nN][tT][sS]? [oO][fF] [eE][aA][rR][nN][iI][nN][gG][sS]|[cC][oO][nN][sS][oO][lL][iI][dD][aA][tT][eE][dD] [iI][nN][cC][oO][mM][eE] [sS][tT][aA][tT][eE][mM][eE][nN][tT][sS]?"
    title_pattern_cashflow = "[oO][nN][sS][oO][lL][iI][dD][aA][tT][eE][dD] [sS][tT][aA][tT][eE][mM][eE][nN][tT][sS]? [oO][fF] [cC][aA][sS][hH] [fF][lL][oO][wW][sS]?|[oO][nN][sS][oO][lL][iI][dD][aA][tT][eE][dD] [cC][aA][sS][hH] [fF][lL][oO][wW][sS]? [sS][tT][aA][tT][eE][mM][eE][nN][tT][sS]?"
    title_pattern_credit = "^[cC][rR][eE][dD][iI][tT] [qQ][uU][aA][lL][iI][tT][yY]"
    title_pattern_risk_weighted_assets = "^Risk-weighted [aA]ssets"

    
    # Datas' position
    position = (0, 2, 0)  # (current quarter, previous quarter, fiscal year)
    position_income = (0, 2, 0)
    position_comprehensive = (0, 2, 0)
    position_nonperforming_loans = 0
    position_cash_flow = (0, 0, 0)  # (current quarter, previous quarter, fiscal year)
#     iscalculationsonly_revenue = "true"
    
    
    # Flags related to financial statement's structure
    CASHFLOW_QUARTER_NEED_COUNT = True
    TITLE_NESTED_IN_TABLE = False
    DONT_FIND_TABLE = True
    RISK_WEIGHTED_ASSETS_NOT_IN_TABLE = False
    
    
    # Don't use match-case (only supported above 3.10.x)
    """ 
    match special_case:
        case "Alphabet Inc.":
            position = (1, 3, 2)
            position_cash_flow = (1, 1, 2)
            iscalculationsonly_revenue = "true|false"
        case _:
            pass
    """
    
    # Special case params
    # Special case params
    if(special_case == "Alphabet Inc."):
        position = (1, 3, 2)
        position_cash_flow = (1, 1, 2)
        iscalculationsonly_revenue = "true|false"
        
    elif(special_case == "MICROSOFT CORP"):
        title_pattern_balance = r"^BALANCE SHEETS\s?$"
        title_pattern_operations = r"^INCOME STATEMENTS\s?$"
        title_pattern_comprehensive = r"^COMPREHENSIVE INCOME STATEMENTS\s?$"
        title_pattern_cashflow = r"^CASH FLOWS STATEMENTS\s?$"
        
        position_cash_flow = (0, 2, 0)  # (current quarter, previous quarter, fiscal year)
        CASHFLOW_QUARTER_NEED_COUNT = False
        
#         def find_table_balance(tag):
#             #print("Overwrite success!")
#             if(tag.name == "p" and title_regex.search(tag.text)):
#                 return True
#             return False
        
#         def find_table_operations(tag):
#             #print("Overwrite success!")
#             if(tag.name == "p" and title_regex.search(tag.text)):
#                 return True
#             return False
        
#         def find_table_comprehensive(tag):
#             #print("Overwrite success!")
#             if(tag.name == "p" and title_regex.search(tag.text)):
#                 return True
#             return False
        
#         def find_table_cashflow(tag):
#             #print("Overwrite success!")
#             if(tag.name == "p" and title_regex.search(tag.text)):
#                 return True
#             return False
        
    elif(special_case == "BANK OF AMERICA CORP /DE/"):
        
        # Table's title is included in targeted table 
#         TITLE_NESTED_IN_TABLE = True
        
        position_nonperforming_loans = -2
        
    elif(special_case == "Monster Beverage Corp"):
        pass
#         title_pattern_balance = "CONSOLIDATED BALANCE SHEETS$"
#         def find_table_balance(tag):
#             if(tag.name == "p" and title_regex.search(tag.text)):
#                 return True
#             return False
        
#         title_pattern_operations = "CONSOLIDATED STATEMENTS OF INCOME$"
#         def find_table_operations(tag):
#             if(tag.name == "p" and title_regex.search(tag.text)):
#                 return True
#             return False
        
#         title_pattern_comprehensive = "CONSOLIDATED STATEMENTS OF COMPREHENSIVE INCOME$"
#         def find_table_comprehensive(tag):
#             if(tag.name == "p" and title_regex.search(tag.text)):
#                 return True
#             return False
        
#         title_pattern_cashflow = "CONSOLIDATED STATEMENTS OF CASH FLOWS$"
#         def find_table_cashflow(tag):
#             if(tag.name == "p" and title_regex.search(tag.text)):
#                 return True
#             return False

    elif(special_case == "KIMBERLY CLARK CORP"):
        pass
    
    elif(special_case == "CLOROX CO /DE/"):
        #print("No 10-K financial statements provided. Please try other company!")
        update_msg("No 10-K financial statements provided. Please try another company!" if IS_ENGLISH else "無提供10-K財報。請嘗試其他公司！")
        return None
    
    
    elif(special_case == "CARNIVAL CORP"):
        #print("No 10-K financial statements provided. Please try other company!")
        update_msg("No 10-K financial statements provided. Please try another company!" if IS_ENGLISH else "無提供10-K財報。請嘗試其他公司！")
        return None
    
    elif(special_case == "CHURCH & DWIGHT CO INC /DE/"):
        pass
#         title_pattern_balance = "[oO][nN][sS][oO][lL][iI][dD][aA][tT][eE][dD] [bB][aA][lL][aA][nN][cC][eE] [sS][hH][eE][eE][tT][sS]$"
#         def find_table_balance(tag):
#             if(re.search("p|span", tag.name) and title_regex.search(tag.text) and type(tag.contents[0]) is NavigableString):
#                 return True
#             return False
        
#         def find_table_operations(tag):
#             if(re.search("p|span", tag.name) and title_regex.search(tag.text) and type(tag.contents[0]) is NavigableString):
#                 return True
#             return False
        
#         def find_table_cashflow(tag):
#             if(re.search("p|span", tag.name) and title_regex.search(tag.text) and type(tag.contents[0]) is NavigableString):
#                 return True
#             return False
    
    elif(special_case == "GENERAL MILLS INC"):
        
#         title_pattern_operations = "^Consolidated Statements of Earnings\s?$"
#         def find_table_operations(tag):
#             if(re.search("div|span", tag.name) and title_regex.search(tag.text) and type(tag.contents[0]) is NavigableString):
#                 return True
#             return False
        
        # Some titles are nested in tables, some even have no tables containing data (after 2022-5-29)!
#         TITLE_NESTED_IN_TABLE = True
        pass
    
    elif(special_case == "BEYOND MEAT, INC."):
        pass
#         TITLE_NESTED_IN_TABLE = True
      
    elif(special_case == "Philip Morris International Inc."):
        position_income = (2, 0, 0)
        position_comprehensive = (2, 0, 0)
        
    elif(special_case == "CONSTELLATION BRANDS, INC."):
        position_income = (2, 0, 0)
        position_comprehensive = (2, 0, 0)
        
    elif(special_case == "AMAZON COM INC"):
        position_income = (1, 3, 2)
        position = (1, 0, 1)
        position_comprehensive = (1, 3, 2)
        position_cash_flow = (1, 3, 2)
        CASHFLOW_QUARTER_NEED_COUNT = False
        DONT_FIND_TABLE = False
        
        
    elif(special_case == "MCDONALDS CORP"):
        CASHFLOW_QUARTER_NEED_COUNT = False
        position_cash_flow = (0, 2, 0)
        
    elif(special_case == "YUM BRANDS INC"):
        DONT_FIND_TABLE = False
        TITLE_NESTED_IN_TABLE = True
    
    
#     elif(special_case == "ROYAL CARIBBEAN CRUISES LTD"):
#         DONT_FIND_TABLE = False
#         title_pattern_operations = "CONSOLIDATED STATEMENTS OF COMPREHENSIVE LOSS"
#         title_pattern_comprehensive = "CONSOLIDATED STATEMENTS OF COMPREHENSIVE LOSS"
    elif(special_case == "NETFLIX INC"):
        CASHFLOW_QUARTER_NEED_COUNT = False
        position_cash_flow = (0, 2, 0)
        
        
    elif(special_case == "NORTHROP GRUMMAN CORP /DE/"):
        #REVENUES_SPECIAL = True
        #position_income_is_false = (0, )
        update_msg("Do not support this company. Please try another company!" if IS_ENGLISH else "不支援此公司。請嘗試其他公司！")
        
    else:
        # Normal report structure
        pass
    
    
    # Break point
    if(stop_flag.is_set()):
        return None
    
    # Sort reports by its date, also filter out unwanted reports
    reports_filtered = filter(lambda report : report[2] is not None, reports)
    #print(type(reports_filtered))
    reports_sorted = sorted(reports_filtered, key = lambda report : report[2])  # Sorted by date, ascending
    #print("reports count: ", str(len(reports_sorted)))

    # for report in reports_sorted:
    #     print(report[1])  # url, string
    #     print(report[2])  # Date object
    #     print(check_report_type(report[0]))  #report[0]: BS object



   
    # In case that financial statement may be divided into two tables, all the eligible title spans need to be founded
    # Find table for "Consolidated statements of operations (incomes)"
    table_operations = []
    for report in reports_sorted:
        # Break point
        if(stop_flag.is_set()):
            return None
        
        
        title_regex = re.compile(title_pattern_operations)
        
        if not TITLE_NESTED_IN_TABLE:
            
            # title_span = report[0].find("span", text = title_regex)
            title_spans = report[0].find_all(find_table_operations)
            #title_spans = report[0].find_all(lambda tag : tag.name == "span" and title_regex.search(tag.text) and type(tag.contents[0]) is NavigableString)
            tables = [title_span.findNext("table") for title_span in title_spans] # No matter the element is nested or not, just find the conformed element sequentially
            tables = report[0] if not tables else tables
            #print("Income: ", len(tables))
            table_operations.append((title_spans, tables, report[2]))  
        else:
            tables = report[0].find_all(find_table_operations_nested)
            tables = report[0] if not tables else tables
            #print("Nested Income: ", len(tables))
            table_operations.append((None, tables, report[2])) 
            
        if DONT_FIND_TABLE:
            table_operations.pop()
            table_operations.append((None, report[0], report[2]))



    # print(table_operations[7][1])


    # Find table for "Consolidated statements of comprehensive income"
    table_comprehensive_income = []
    for report in reports_sorted:
        # Break point
        if(stop_flag.is_set()):
            return None
        
        
        title_regex = re.compile(title_pattern_comprehensive)
        
        if not TITLE_NESTED_IN_TABLE:
            # title_span = report[0].find("span", text = title_regex)
            #title_spans = report[0].find_all(lambda tag : tag.name == "span" and title_regex.search(tag.text) and type(tag.contents[0]) is NavigableString)

            title_spans = report[0].find_all(find_table_comprehensive)
            tables = [title_span.findNext("table") for title_span in title_spans] # No matter the element is nested or not, just find the conformed element sequentially
            tables = report[0] if not tables else tables
            #print("Comprehensive: ", len(tables))
            table_comprehensive_income.append((title_spans, tables, report[2])) 
        else:
            tables = report[0].find_all(find_table_comprehensive_nested)
            tables = report[0] if not tables else tables
            #print("Nested Comprehensive: ", len(tables))
            table_comprehensive_income.append((None, tables, report[2])) 
            
            
        if DONT_FIND_TABLE:
            table_comprehensive_income.pop()
            table_comprehensive_income.append((None, report[0], report[2]))



    # print(table_comprehensive_income[7][1])


    # Find table for "Consolidated balance sheets"
    table_balances = []
    for report in reports_sorted:
        # Break point
        if(stop_flag.is_set()):
            return None
        
        title_regex = re.compile(title_pattern_balance)
        
        if not TITLE_NESTED_IN_TABLE:
            # title_span = report[0].find("span", text = title_regex)
            #title_spans = report[0].find_all(lambda tag : tag.name == "span" and title_regex.search(tag.text) and type(tag.contents[0]) is NavigableString)

            title_spans = report[0].find_all(find_table_balance)

            tables = [title_span.findNext("table") for title_span in title_spans]  # No matter the element is nested or not, just find the conformed element sequentially
            tables = report[0] if not tables else tables
            #print("Balance: ", len(tables))
            table_balances.append((title_spans, tables, report[2]))  
        else:
            tables = report[0].find_all(find_table_balance_nested)
            tables = report[0] if not tables else tables
            #print("Nested Balance: ", len(tables))
            table_balances.append((None, tables, report[2]))  
            
        if DONT_FIND_TABLE:
            table_balances.pop()
            table_balances.append((None, report[0], report[2]))


    # print(table_balances[2][1])



    # Find table of "Consolidated statements of cash flows"
    table_cashflows = []
    for report in reports_sorted:
        # Break point
        if(stop_flag.is_set()):
            return None
        
        title_regex = re.compile(title_pattern_cashflow)
        
        if not TITLE_NESTED_IN_TABLE:
            # title_span = report[0].find("span", text = title_regex)
            #title_spans = report[0].find_all(lambda tag : tag.name == "span" and title_regex.search(tag.text) and type(tag.contents[0]) is NavigableString)

            title_spans = report[0].find_all(find_table_cashflow)

            tables = [title_span.findNext("table") for title_span in title_spans]  # No matter the element is nested or not, just find the conformed element sequentially
            tables = report[0] if not tables else tables
            #print("Cashflows: ", len(tables))
            table_cashflows.append((title_spans, tables, report[2]))  
        else:
            tables = report[0].find_all(find_table_cashflow_nested)
            tables = report[0] if not tables else tables
            #print("Nested Cashflows: ", len(tables))
            table_cashflows.append((None, tables, report[2]))  
            
            
        if DONT_FIND_TABLE:
            table_cashflows.pop()
            table_cashflows.append((None, report[0], report[2]))


    # print(table_cashflows[2][1])
    
    
    # Find table of "Credit quality" (for financial industry)
    table_credit_quality = []
    for report in reports_sorted:
        # Break point
        if(stop_flag.is_set()):
            return None
        
        
        title_regex = re.compile(title_pattern_credit)
        if not TITLE_NESTED_IN_TABLE:
            title_spans = report[0].find_all(find_table_credit)

            tables = [title_span.findNext("table") for title_span in title_spans]  # No matter the element is nested or not, just find the conformed element sequentially
            tables = report[0] if not tables else tables
            #print("Credit: ", len(tables))
            table_credit_quality.append((title_spans, tables, report[2])) 
        else:
            tables = report[0].find_all(find_table_credit_nested)
            tables = report[0] if not tables else tables
            #print("Nested Credit: ", len(tables))
            table_credit_quality.append((None, tables, report[2]))  
            
        if DONT_FIND_TABLE:
            table_credit_quality.pop()
            table_credit_quality.append((None, report[0], report[2]))


    # Find table of "Risk-weighted assets"
    table_risk_weighted_assets = []
    for report in reports_sorted:
        # Break point
        if(stop_flag.is_set()):
            return None
        
        
        title_regex = re.compile(title_pattern_risk_weighted_assets)
        tables = report[0].find_all(find_table_risk_weighted_assets_nested)
        tables = report[0] if not tables else tables
        #print("Nested Risk-weighted: ", len(tables))
        table_risk_weighted_assets.append((None, tables, report[2])) 
        
        
        if DONT_FIND_TABLE:
            table_risk_weighted_assets.pop()
            table_risk_weighted_assets.append((None, report[0], report[2]))

    
    # Extract the targeted data from the above tables, quarter by quarter, depends on industry type
    #print("Start processing data ...")
    update_msg("Start processing data ..." if IS_ENGLISH else "資料處理中 ...")
    if(industry_type == "N"):
        # Settings of pandas's dataframe
        
        result_columns = []  # Quarter date
        result_index = []
        if IS_ENGLISH:
            result_index = ["Assets", "Inventories", "Liabilities", "Total stockholder's equity", "Earning per share basic", "Earning per share diluted",
                         "Revenue", "Gross profit", "Earning before provision for taxes on income", "Net income", "Comprehensive income net of tax",
                         "Net cash from operating activities", "Net cash from investing activities", "Net cash from financing activities",
                         "Gross margin (%)", "Operating margin (%)", "Net income margin (%)", "Days Inventory (days)",
                         "Return on assets (%)", "Return on equity (%)"]
        else:
            result_index = ["總資產", "存貨", "總負債", "股東權益", "基本每股盈餘", "稀釋每股盈餘",
                         "營業收入", "毛利", "稅前淨利", "淨收入", "綜合收入",
                         "營業活動現金流量", "投資活動現金流量", "融資活動現金流量",
                         "毛利率 (%)", "營業利益率 (%)", "稅後淨利率 (%)", "存貨周轉天數 (天)",
                         "資產報酬率 (%)", "股東權益報酬率 (%)"]
            
        result_data = [[0] * (len(reports) - 1) for _ in range(len(result_index))]
        #print(len(reports_sorted))





        # Extract data from the above tables version 2
        # Probably no 9 reports will be gotten!
        for i in range(1, len(reports)):
            # Break point
            if(stop_flag.is_set()):
                return None
        
        
            # Add quarter date
            result_columns.append(reports_sorted[i][2].date())


            # Get assets
            result_data[0][i - 1] = extract_data(table_balances[i][1], r"^us-gaap:Assets$", None, position[0])


            # Get inventories
            result_data[1][i - 1] = extract_data(table_balances[i][1], r"^us-gaap:Inventory", None, position[0])


            # Get liabilities (May need to be calculated!)
            result_data[2][i - 1] = extract_data(table_balances[i][1], r"^us-gaap:Liabilities$", None, position[0])



            # Get total stockholder's equity (May need to be calculated!)
            if not np.isnan(extract_data(table_balances[i][1], r"^us-gaap:StockholdersEquity$", None, position[0])):
                result_data[3][i - 1] = extract_data(table_balances[i][1], r"^us-gaap:StockholdersEquity$", None, position[0])
            elif not np.isnan(extract_data(table_balances[i][1], r"^us-gaap:StockholdersEquity", None, position[0])):
                result_data[3][i - 1] = extract_data(table_balances[i][1], r"^us-gaap:StockholdersEquity", None, position[0])
            else:
                result_data[3][i - 1] = np.nan


            # Calculate liabilities or stockholder's equity

            for j in range(len(reports) - 1):
                if(not np.isnan(result_data[0][j]) and np.isnan(result_data[2][j]) and not np.isnan(result_data[3][j])):
                    result_data[2][j] = result_data[0][j] - result_data[3][j]
                elif(not np.isnan(result_data[0][j]) and not np.isnan(result_data[2][j]) and np.isnan(result_data[3][j])):
                    result_data[3][j] = result_data[0][j] - result_data[2][j]
                else:
                    pass

            # Calculate liabilities or stockholder's equity
            """
            if(not np.isnan(result_data[0][i - 1]) and np.isnan(result_data[2][i - 1]) and not np.isnan(result_data[3][i - 1])):
                result_data[2][i - 1] = result_data[0][i - 1] - result_data[3][i - 1]
            elif(not np.isnan(result_data[0][i - 1]) and not np.isnan(result_data[2][i - 1]) and np.isnan(result_data[3][i - 1])):
                result_data[3][i - 1] = result_data[0][i - 1] - result_data[2][i - 1]
            else:
                pass
            """



            # Difference between 10-K and 10-Q reports
            if(check_report_type(reports_sorted[i][0]) == "Q"):

                # Get EPS (basic)
                result_data[4][i - 1] = np.round(extract_data(table_operations[i][1], r"^us-gaap:EarningsPerShareBasic$|^us-gaap:IncomeLossFromContinuingOperationsPerBasicShare$", None, position_income[0]), 2)

                # Get EPS (diluted)
                result_data[5][i - 1] = np.round(extract_data(table_operations[i][1], r"^us-gaap:EarningsPerShareDiluted$|^us-gaap:IncomeLossFromContinuingOperationsPerDilutedShare$", None, position_income[0]), 2)

                # Get revenues
                #print("Revenue")
                if not np.isnan(extract_data(table_operations[i][1], r"^us-gaap:Revenue", "true", position_income[0])):                    
                    result_data[6][i - 1] = extract_data(table_operations[i][1], r"^us-gaap:Revenue", "true", position_income[0])
                elif not np.isnan(extract_data(table_operations[i][1], r"^us-gaap:Revenue", None, position_income[0])):
                    result_data[6][i - 1] = extract_data(table_operations[i][1], r"^us-gaap:Revenue", None, position_income[0])
                else:
                    result_data[6][i - 1] = np.nan
                



                # Get gross profit (May need to be calculated)
                cost_of_revenue = np.nan
                if not np.isnan(extract_data(table_operations[i][1], r"^us-gaap:CostOfRevenue$|^us-gaap:CostOfGoodsAndServicesSold$|^us-gaap:ProductionAndDistributionCosts$", "true", position_income[0])):
                    cost_of_revenue = extract_data(table_operations[i][1], r"^us-gaap:CostOfRevenue$|^us-gaap:CostOfGoodsAndServicesSold$|^us-gaap:ProductionAndDistributionCosts$", "true", position_income[0])  
                elif not np.isnan(extract_data(table_operations[i][1], r"^us-gaap:CostOfRevenue$|^us-gaap:CostOfGoodsAndServicesSold$|^us-gaap:ProductionAndDistributionCosts$", None, position_income[0])):
                    cost_of_revenue = extract_data(table_operations[i][1], r"^us-gaap:CostOfRevenue$|^us-gaap:CostOfGoodsAndServicesSold$|^us-gaap:ProductionAndDistributionCosts$", None, position_income[0])
                else:
                    pass
                
                
                gross_profit = np.nan
                if not np.isnan(extract_data(table_operations[i][1], r"^us-gaap:GrossProfit$", "true", position_income[0])):
                    gross_profit = extract_data(table_operations[i][1], r"^us-gaap:GrossProfit$", "true", position_income[0])
                elif not np.isnan(extract_data(table_operations[i][1], r"^us-gaap:GrossProfit$", None, position_income[0])):
                    gross_profit = extract_data(table_operations[i][1], r"^us-gaap:GrossProfit$", None, position_income[0])
                else:
                    pass
                
                if not np.isnan(gross_profit):
                    result_data[7][i - 1] = gross_profit
                elif not np.isnan(result_data[6][i - 1]) and not np.isnan(cost_of_revenue):
                    result_data[7][i - 1] = result_data[6][i - 1] - cost_of_revenue
                else:
                    result_data[7][i - 1] = np.nan
                    

                # Get Income before provision for income taxes
                if not np.isnan(extract_data(table_operations[i][1], r"^us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxes|IncomeLossFromContinuingOperationsBeforeIncomeTaxes|^us-gaap:IncomeLossIncludingPortionAttributableToNoncontrollingInterest$|^us-gaap:IncomeLossAttributableToParent$", "true", position_income[0])):
                    result_data[8][i - 1] = extract_data(table_operations[i][1], r"^us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxes|IncomeLossFromContinuingOperationsBeforeIncomeTaxes|^us-gaap:IncomeLossIncludingPortionAttributableToNoncontrollingInterest$|^us-gaap:IncomeLossAttributableToParent$", "true", position_income[0])
                elif not np.isnan(extract_data(table_operations[i][1], r"^us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxes|IncomeLossFromContinuingOperationsBeforeIncomeTaxes|^us-gaap:IncomeLossIncludingPortionAttributableToNoncontrollingInterest$|^us-gaap:IncomeLossAttributableToParent$", None, position_income[0])):
                    result_data[8][i - 1] = extract_data(table_operations[i][1], r"^us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxes|IncomeLossFromContinuingOperationsBeforeIncomeTaxes|^us-gaap:IncomeLossIncludingPortionAttributableToNoncontrollingInterest$|^us-gaap:IncomeLossAttributableToParent$", None, position_income[0])
                else:
                    result_data[8][i - 1] = np.nan
                    
                    

                # Get net income
                if not np.isnan(extract_data(table_operations[i][1], r"^us-gaap:NetIncomeLoss$|^us-gaap:NetIncomeLossAvailableToCommonStockholdersBasic$", "true", position_comprehensive[0])):
                    result_data[9][i - 1] = extract_data(table_operations[i][1], r"^us-gaap:NetIncomeLoss$|^us-gaap:NetIncomeLossAvailableToCommonStockholdersBasic$", "true", position_comprehensive[0])                
                elif not np.isnan(extract_data(table_operations[i][1], r"^us-gaap:NetIncomeLoss$|^us-gaap:NetIncomeLossAvailableToCommonStockholdersBasic$", None, position_comprehensive[0])):
                    result_data[9][i - 1] = extract_data(table_operations[i][1], r"^us-gaap:NetIncomeLoss$|^us-gaap:NetIncomeLossAvailableToCommonStockholdersBasic$", None, position_comprehensive[0])    
                else:
                    result_data[9][i - 1] = np.nan


                # Get comprehensive income net of tax
                if not np.isnan(extract_data(table_comprehensive_income[i][1], r"^us-gaap:ComprehensiveIncomeNetOfTax$|^us-gaap:ComprehensiveIncomeNetOfTaxIncludingPortionAttributableToNoncontrollingInterest$", "true", position_comprehensive[0])):
                    result_data[10][i - 1] = extract_data(table_comprehensive_income[i][1], r"^us-gaap:ComprehensiveIncomeNetOfTax$|^us-gaap:ComprehensiveIncomeNetOfTaxIncludingPortionAttributableToNoncontrollingInterest$", "true", position_comprehensive[0])
                elif not np.isnan(extract_data(table_comprehensive_income[i][1], r"^us-gaap:ComprehensiveIncomeNetOfTax$|^us-gaap:ComprehensiveIncomeNetOfTaxIncludingPortionAttributableToNoncontrollingInterest$", None, position_comprehensive[0])):
                    result_data[10][i - 1] = extract_data(table_comprehensive_income[i][1], r"^us-gaap:ComprehensiveIncomeNetOfTax$|^us-gaap:ComprehensiveIncomeNetOfTaxIncludingPortionAttributableToNoncontrollingInterest$", None, position_comprehensive[0])
                else:
                    result_data[10][i - 1] = np.nan

            elif(check_report_type(reports_sorted[i][0]) == "K"):

                # Get EPS (basic)
                result_data[4][i - 1] = np.round(extract_data(table_operations[i][1], r"^us-gaap:EarningsPerShareBasic$|^us-gaap:IncomeLossFromContinuingOperationsPerBasicShare$", None, position_income[2]), 2)

                # Get EPS (diluted)
                result_data[5][i - 1] = np.round(extract_data(table_operations[i][1], r"^us-gaap:EarningsPerShareDiluted$|^us-gaap:IncomeLossFromContinuingOperationsPerDilutedShare$", None, position_income[2]), 2)


                # Get revenues (Need to get data from the previous quarter report, then calculate it)
                # 1. Get nine months accumulated data
                previous_revenues = np.nan
                if not np.isnan(extract_data(table_operations[i - 1][1], r"^us-gaap:Revenue", "true", position_income[1])):
                    previous_revenues = extract_data(table_operations[i - 1][1], r"^us-gaap:Revenue", "true", position_income[1])
                elif not np.isnan(extract_data(table_operations[i - 1][1], r"^us-gaap:Revenue", None, position_income[1])):
                    previous_revenues = extract_data(table_operations[i - 1][1], r"^us-gaap:Revenue", None, position_income[1])
                else:
                    pass


                # 2. Get revenues of whole fiscal year
                year_revenues = np.nan
                if not np.isnan(extract_data(table_operations[i][1], r"^us-gaap:Revenue", "true", position_income[2])):
                    year_revenues = extract_data(table_operations[i][1], r"^us-gaap:Revenue", "true", position_income[2])
                elif not np.isnan(extract_data(table_operations[i][1], r"^us-gaap:Revenue", None, position_income[2])):
                    year_revenues = extract_data(table_operations[i][1], r"^us-gaap:Revenue", None, position_income[2])
                else:
                    pass

                # 3. Calculate revenue from the above values
                if not np.isnan(year_revenues) and not np.isnan(year_revenues):
                    result_data[6][i - 1] = year_revenues - previous_revenues
                else:
                    result_data[6][i - 1] = np.nan
                
                
                #print("Revenue calculated!")
                #print("year_revenues: ", year_revenues)
                #print("previous_revenues: ", previous_revenues )


                # Get gross profit (Need to get data from the previous quarter report, then calculate it)
                previous_gross_profit = np.nan
                if not np.isnan(extract_data(table_operations[i - 1][1], r"^us-gaap:GrossProfit$", "true", position_income[1])):
                    previous_gross_profit = extract_data(table_operations[i - 1][1], r"^us-gaap:GrossProfit$", "true", position_income[1])
                elif not np.isnan(extract_data(table_operations[i - 1][1], r"^us-gaap:GrossProfit$", None, position_income[1])):
                    previous_gross_profit = extract_data(table_operations[i - 1][1], r"^us-gaap:GrossProfit$", None, position_income[1])
                else:
                    pass
                
                
                year_gross_profit = np.nan
                if not np.isnan(extract_data(table_operations[i][1], r"^us-gaap:GrossProfit$", "true", position_income[2])):
                    year_gross_profit = extract_data(table_operations[i][1], r"^us-gaap:GrossProfit$", "true", position_income[2])
                elif not np.isnan(extract_data(table_operations[i][1], r"^us-gaap:GrossProfit$", None, position_income[2])):
                    year_gross_profit = extract_data(table_operations[i][1], r"^us-gaap:GrossProfit$", None, position_income[2])
                else:
                    pass
                
                gross_profit = np.nan
                if not np.isnan(year_gross_profit) and not np.isnan(previous_gross_profit):
                    gross_profit = year_gross_profit - previous_gross_profit
                else:
                    pass

                previous_cost_of_revenue = np.nan
                if not np.isnan(extract_data(table_operations[i - 1][1], r"^us-gaap:CostOfRevenue$|^us-gaap:CostOfGoodsAndServicesSold$|^us-gaap:ProductionAndDistributionCosts$", "true", position_income[1])):
                    previous_cost_of_revenue = extract_data(table_operations[i - 1][1], r"^us-gaap:CostOfRevenue$|^us-gaap:CostOfGoodsAndServicesSold$|^us-gaap:ProductionAndDistributionCosts$", "true", position_income[1])
                elif not np.isnan(extract_data(table_operations[i - 1][1], r"^us-gaap:CostOfRevenue$|^us-gaap:CostOfGoodsAndServicesSold$|^us-gaap:ProductionAndDistributionCosts$", None, position_income[1])):
                    previous_cost_of_revenue = extract_data(table_operations[i - 1][1], r"^us-gaap:CostOfRevenue$|^us-gaap:CostOfGoodsAndServicesSold$|^us-gaap:ProductionAndDistributionCosts$", None, position_income[1])
                else:
                    pass
                
                year_cost_of_revenue = np.nan
                if not np.isnan(extract_data(table_operations[i][1], r"^us-gaap:CostOfRevenue$|^us-gaap:CostOfGoodsAndServicesSold$|^us-gaap:ProductionAndDistributionCosts$", "true", position_income[2])):
                    year_cost_of_revenue = extract_data(table_operations[i][1], r"^us-gaap:CostOfRevenue$|^us-gaap:CostOfGoodsAndServicesSold$|^us-gaap:ProductionAndDistributionCosts$", "true", position_income[2])
                elif not np.isnan(extract_data(table_operations[i][1], r"^us-gaap:CostOfRevenue$|^us-gaap:CostOfGoodsAndServicesSold$|^us-gaap:ProductionAndDistributionCosts$", None, position_income[2])):
                    year_cost_of_revenue = extract_data(table_operations[i][1], r"^us-gaap:CostOfRevenue$|^us-gaap:CostOfGoodsAndServicesSold$|^us-gaap:ProductionAndDistributionCosts$", None, position_income[2])
                else:
                    pass
                
                
                cost_of_revenue = np.nan
                if not np.isnan(year_cost_of_revenue) and not np.isnan(previous_cost_of_revenue):                
                    cost_of_revenue = year_cost_of_revenue - previous_cost_of_revenue
                else:
                    pass

                if not np.isnan(gross_profit):
                    result_data[7][i - 1] = gross_profit
                elif not np.isnan(result_data[6][i - 1]) and not np.isnan(cost_of_revenue):
                    result_data[7][i - 1] = result_data[6][i - 1] - cost_of_revenue
                else:
                    result_data[7][i - 1] = np.nan



                # Get Income before provision for income taxes
                previous_income_before_tax = np.nan
                if not np.isnan(extract_data(table_operations[i - 1][1], r"^us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxes|IncomeLossFromContinuingOperationsBeforeIncomeTaxes|^us-gaap:IncomeLossIncludingPortionAttributableToNoncontrollingInterest$|^us-gaap:IncomeLossAttributableToParent$", "true", position_income[1])):
                    previous_income_before_tax = extract_data(table_operations[i - 1][1], r"^us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxes|IncomeLossFromContinuingOperationsBeforeIncomeTaxes|^us-gaap:IncomeLossIncludingPortionAttributableToNoncontrollingInterest$|^us-gaap:IncomeLossAttributableToParent$", "true", position_income[1])
                elif not np.isnan(extract_data(table_operations[i - 1][1], r"^us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxes|IncomeLossFromContinuingOperationsBeforeIncomeTaxes|^us-gaap:IncomeLossIncludingPortionAttributableToNoncontrollingInterest$|^us-gaap:IncomeLossAttributableToParent$", None, position_income[1])):
                    previous_income_before_tax = extract_data(table_operations[i - 1][1], r"^us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxes|IncomeLossFromContinuingOperationsBeforeIncomeTaxes|^us-gaap:IncomeLossIncludingPortionAttributableToNoncontrollingInterest$|^us-gaap:IncomeLossAttributableToParent$", None, position_income[1])
                else:
                    pass

                year_income_before_tax = np.nan
                if not np.isnan(extract_data(table_operations[i][1], r"^us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxes|IncomeLossFromContinuingOperationsBeforeIncomeTaxes|^us-gaap:IncomeLossIncludingPortionAttributableToNoncontrollingInterest$", "true", position_income[2])):                    
                    year_income_before_tax = extract_data(table_operations[i][1], r"^us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxes|IncomeLossFromContinuingOperationsBeforeIncomeTaxes|^us-gaap:IncomeLossIncludingPortionAttributableToNoncontrollingInterest$", "true", position_income[2])
                elif not np.isnan(extract_data(table_operations[i][1], r"^us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxes|IncomeLossFromContinuingOperationsBeforeIncomeTaxes|^us-gaap:IncomeLossIncludingPortionAttributableToNoncontrollingInterest$", None, position_income[2])):
                    year_income_before_tax = extract_data(table_operations[i][1], r"^us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxes|IncomeLossFromContinuingOperationsBeforeIncomeTaxes|^us-gaap:IncomeLossIncludingPortionAttributableToNoncontrollingInterest$", None, position_income[2])
                else:
                    pass
                
                income_before_tax = np.nan
                if not np.isnan(year_income_before_tax) and not np.isnan(previous_income_before_tax):
                    income_before_tax = year_income_before_tax - previous_income_before_tax
                else:
                    pass
                
                if not np.isnan(income_before_tax):
                    result_data[8][i - 1] = income_before_tax
                else:
                    result_data[8][i - 1] = np.nan


                # Get net income
                previous_income = np.nan
                if not np.isnan(extract_data(table_operations[i - 1][1], r"^us-gaap:NetIncomeLoss$|^us-gaap:NetIncomeLossAvailableToCommonStockholdersBasic$", "true", position_income[1])):
                    previous_income = extract_data(table_operations[i - 1][1], r"^us-gaap:NetIncomeLoss$|^us-gaap:NetIncomeLossAvailableToCommonStockholdersBasic$", "true", position_income[1])
                elif not np.isnan(extract_data(table_operations[i - 1][1], r"^us-gaap:NetIncomeLoss$|^us-gaap:NetIncomeLossAvailableToCommonStockholdersBasic$", None, position_income[1])):
                    previous_income = extract_data(table_operations[i - 1][1], r"^us-gaap:NetIncomeLoss$|^us-gaap:NetIncomeLossAvailableToCommonStockholdersBasic$", None, position_income[1])
                else:
                    pass
                
                year_income = np.nan
                if not np.isnan(extract_data(table_operations[i][1], r"^us-gaap:NetIncomeLoss$|^us-gaap:NetIncomeLossAvailableToCommonStockholdersBasic$", "true", position_income[2])):
                    year_income = extract_data(table_operations[i][1], r"^us-gaap:NetIncomeLoss$|^us-gaap:NetIncomeLossAvailableToCommonStockholdersBasic$", "true", position_income[2])
                elif not np.isnan(extract_data(table_operations[i][1], r"^us-gaap:NetIncomeLoss$|^us-gaap:NetIncomeLossAvailableToCommonStockholdersBasic$", None, position_income[2])):
                    year_income = extract_data(table_operations[i][1], r"^us-gaap:NetIncomeLoss$|^us-gaap:NetIncomeLossAvailableToCommonStockholdersBasic$", None, position_income[2])
                else:
                    pass
                
                if not np.isnan(year_income) and not np.isnan(previous_income):
                    result_data[9][i - 1] = year_income - previous_income
                else:
                    result_data[9][i - 1] = np.nan


                # Get comprehensive income net of tax
                previous_comprehensive_income = np.nan
                if not np.isnan(extract_data(table_comprehensive_income[i - 1][1], r"^us-gaap:ComprehensiveIncomeNetOfTax$|^us-gaap:ComprehensiveIncomeNetOfTaxIncludingPortionAttributableToNoncontrollingInterest$", "true", position_comprehensive[1])):
                    previous_comprehensive_income = extract_data(table_comprehensive_income[i - 1][1], r"^us-gaap:ComprehensiveIncomeNetOfTax$|^us-gaap:ComprehensiveIncomeNetOfTaxIncludingPortionAttributableToNoncontrollingInterest$", "true", position_comprehensive[1])
                elif not np.isnan(extract_data(table_comprehensive_income[i - 1][1], r"^us-gaap:ComprehensiveIncomeNetOfTax$|^us-gaap:ComprehensiveIncomeNetOfTaxIncludingPortionAttributableToNoncontrollingInterest$", None, position_comprehensive[1])):
                    previous_comprehensive_income = extract_data(table_comprehensive_income[i - 1][1], r"^us-gaap:ComprehensiveIncomeNetOfTax$|^us-gaap:ComprehensiveIncomeNetOfTaxIncludingPortionAttributableToNoncontrollingInterest$", None, position_comprehensive[1])
                else:
                    pass
                
                
                year_comprehensive_income = np.nan
                if not np.isnan(extract_data(table_comprehensive_income[i][1], r"^us-gaap:ComprehensiveIncomeNetOfTax$|^us-gaap:ComprehensiveIncomeNetOfTaxIncludingPortionAttributableToNoncontrollingInterest$", "true", position_comprehensive[2])):
                    year_comprehensive_income = extract_data(table_comprehensive_income[i][1], r"^us-gaap:ComprehensiveIncomeNetOfTax$|^us-gaap:ComprehensiveIncomeNetOfTaxIncludingPortionAttributableToNoncontrollingInterest$", "true", position_comprehensive[2])
                elif not np.isnan(extract_data(table_comprehensive_income[i][1], r"^us-gaap:ComprehensiveIncomeNetOfTax$|^us-gaap:ComprehensiveIncomeNetOfTaxIncludingPortionAttributableToNoncontrollingInterest$", None, position_comprehensive[2])):
                    year_comprehensive_income = extract_data(table_comprehensive_income[i][1], r"^us-gaap:ComprehensiveIncomeNetOfTax$|^us-gaap:ComprehensiveIncomeNetOfTaxIncludingPortionAttributableToNoncontrollingInterest$", None, position_comprehensive[2])
                else:
                    pass
                
                if not np.isnan(year_comprehensive_income) and not np.isnan(previous_comprehensive_income):
                    result_data[10][i - 1] = year_comprehensive_income - previous_comprehensive_income
                else:
                    result_data[10][i - 1] = np.nan

            else:
                #print("Something wrong after filtering and sorting")
                update_msg("Something wrong after filtering and sorting." if IS_ENGLISH else "財報過濾與排序出現問題！")



            # Get net cash provided by operating activities 
            # No information of cash flow in current quarter period! Only accululated value is provided! Have special case!
            # Need some calculation to get cash flow in the quarter period
            if(check_report_type(reports_sorted[i - 1][0]) == "K"):
                # First quarter
                result_data[11][i - 1] = extract_data(table_cashflows[i][1], r"^us-gaap:NetCashProvidedByUsedInOperatingActivities", None, position_cash_flow[0])

            elif(check_report_type(reports_sorted[i - 1][0]) == "Q"):
                if CASHFLOW_QUARTER_NEED_COUNT:
                    if(check_report_type(reports_sorted[i][0]) == "Q"):
                        current_cash_flow_operating = extract_data(table_cashflows[i][1], r"^us-gaap:NetCashProvidedByUsedInOperatingActivities", None, position_cash_flow[0])
                        previous_cash_flow_operating = extract_data(table_cashflows[i - 1][1], r"^us-gaap:NetCashProvidedByUsedInOperatingActivities", None, position_cash_flow[1])
                        cash_flow_operating = current_cash_flow_operating - previous_cash_flow_operating
                        result_data[11][i - 1] = cash_flow_operating
                    elif(check_report_type(reports_sorted[i][0]) == "K"):
                        current_cash_flow_operating = extract_data(table_cashflows[i][1], r"^us-gaap:NetCashProvidedByUsedInOperatingActivities", None, position_cash_flow[2])
                        previous_cash_flow_operating = extract_data(table_cashflows[i - 1][1], r"^us-gaap:NetCashProvidedByUsedInOperatingActivities", None, position_cash_flow[1])
                        cash_flow_operating = current_cash_flow_operating - previous_cash_flow_operating
                        result_data[11][i - 1] = cash_flow_operating
                    else:
                        update_msg("Something wrong when extracting data of cash flows from 10-K report" if IS_ENGLISH else "處理10-K財報之現金流量出現問題。")
                else:
                    if(check_report_type(reports_sorted[i][0]) == "Q"):            
                        result_data[11][i - 1] = extract_data(table_cashflows[i][1], r"^us-gaap:NetCashProvidedByUsedInOperatingActivities", None, position_cash_flow[0])
                    elif(check_report_type(reports_sorted[i][0]) == "K"):
                        current_cash_flow_operating = extract_data(table_cashflows[i][1], r"^us-gaap:NetCashProvidedByUsedInOperatingActivities", None, position_cash_flow[2])
                        previous_cash_flow_operating = extract_data(table_cashflows[i - 1][1], r"^us-gaap:NetCashProvidedByUsedInOperatingActivities", None, position_cash_flow[1])
                        cash_flow_operating = current_cash_flow_operating - previous_cash_flow_operating
                        result_data[11][i - 1] = cash_flow_operating
                    else:
                        update_msg("Something wrong when extracting data of cash flows from 10-K report" if IS_ENGLISH else "處理10-K財報之現金流量出現問題。")
            else:
                update_msg("Something wrong when extracting data of cash flows" if IS_ENGLISH else "處理財報之現金流量出現問題。")



            # Get net cash provided by investing activities 
            # No information of cash flow in current quarter period! Only accululated value is provided!
            # Need some calculation to get cash flow in the quarter period
            if(check_report_type(reports_sorted[i - 1][0]) == "K"):
                # Q1
                result_data[12][i - 1] = extract_data(table_cashflows[i][1], r"^us-gaap:NetCashProvidedByUsedInInvestingActivities", None, position_cash_flow[0])


            elif(check_report_type(reports_sorted[i - 1][0]) == "Q"):
                if CASHFLOW_QUARTER_NEED_COUNT:
                    if(check_report_type(reports_sorted[i][0]) == "Q"):
                        current_cash_flow_investing = extract_data(table_cashflows[i][1], r"^us-gaap:NetCashProvidedByUsedInInvestingActivities", None, position_cash_flow[0])
                        previous_cash_flow_investing = extract_data(table_cashflows[i - 1][1], r"^us-gaap:NetCashProvidedByUsedInInvestingActivities", None, position_cash_flow[1])
                        cash_flow_investing = current_cash_flow_investing - previous_cash_flow_investing
                        result_data[12][i - 1] = cash_flow_investing
                    elif(check_report_type(reports_sorted[i][0]) == "K"):
                        current_cash_flow_investing = extract_data(table_cashflows[i][1], r"^us-gaap:NetCashProvidedByUsedInInvestingActivities", None, position_cash_flow[2])
                        previous_cash_flow_investing = extract_data(table_cashflows[i - 1][1], r"^us-gaap:NetCashProvidedByUsedInInvestingActivities", None, position_cash_flow[1])
                        cash_flow_investing = current_cash_flow_investing - previous_cash_flow_investing
                        result_data[12][i - 1] = cash_flow_investing
                    else:
                        update_msg("Something wrong when extracting data of cash flows from 10-K report" if IS_ENGLISH else "處理10-K財報之現金流量出現問題。")
                else:
                    if(check_report_type(reports_sorted[i][0]) == "Q"):
                        result_data[12][i - 1] = extract_data(table_cashflows[i][1], r"^us-gaap:NetCashProvidedByUsedInInvestingActivities", None, position_cash_flow[0])
                    elif(check_report_type(reports_sorted[i][0]) == "K"):
                        current_cash_flow_investing = extract_data(table_cashflows[i][1], r"^us-gaap:NetCashProvidedByUsedInInvestingActivities", None, position_cash_flow[2])
                        previous_cash_flow_investing = extract_data(table_cashflows[i - 1][1], r"^us-gaap:NetCashProvidedByUsedInInvestingActivities", None, position_cash_flow[1])
                        cash_flow_investing = current_cash_flow_investing - previous_cash_flow_investing
                        result_data[12][i - 1] = cash_flow_investing
                    else:
                        update_msg("Something wrong when extracting data of cash flows from 10-K report" if IS_ENGLISH else "處理10-K財報之現金流量出現問題。")
            else:
                update_msg("Something wrong when extracting data of cash flows" if IS_ENGLISH else "處理財報之現金流量出現問題。")




            # Get net cash provided by financing activities 
            # No information of cash flow in current quarter period! Only accululated value is provided!
            # Need some calculation to get cash flow in the quarter period
            if(check_report_type(reports_sorted[i - 1][0]) == "K"):
                # First quarter
                result_data[13][i - 1] = extract_data(table_cashflows[i][1], r"^us-gaap:NetCashProvidedByUsedInFinancingActivities", None, position_cash_flow[0])

            elif(check_report_type(reports_sorted[i - 1][0]) == "Q"):
                if CASHFLOW_QUARTER_NEED_COUNT:
                    if(check_report_type(reports_sorted[i][0]) == "Q"):
                        current_cash_flow_financing = extract_data(table_cashflows[i][1], r"^us-gaap:NetCashProvidedByUsedInFinancingActivities", None, position_cash_flow[0])
                        previous_cash_flow_financing = extract_data(table_cashflows[i - 1][1], r"^us-gaap:NetCashProvidedByUsedInFinancingActivities", None, position_cash_flow[1])
                        cash_flow_financing = current_cash_flow_financing - previous_cash_flow_financing
                        result_data[13][i - 1] = cash_flow_financing
                    elif(check_report_type(reports_sorted[i][0]) == "K"):
                        current_cash_flow_financing = extract_data(table_cashflows[i][1], r"^us-gaap:NetCashProvidedByUsedInFinancingActivities", None, position_cash_flow[2])
                        previous_cash_flow_financing = extract_data(table_cashflows[i - 1][1], r"^us-gaap:NetCashProvidedByUsedInFinancingActivities", None, position_cash_flow[1])
                        cash_flow_financing = current_cash_flow_financing - previous_cash_flow_financing
                        result_data[13][i - 1] = cash_flow_financing
                    else:
                        update_msg("Something wrong when extracting data of cash flows from 10-K report" if IS_ENGLISH else "處理10-K財報之現金流量出現問題。")
                else:
                    if(check_report_type(reports_sorted[i][0]) == "Q"):
                        result_data[13][i - 1] = extract_data(table_cashflows[i][1], r"^us-gaap:NetCashProvidedByUsedInFinancingActivities", None, position_cash_flow[0])
                    elif(check_report_type(reports_sorted[i][0]) == "K"):
                        current_cash_flow_financing = extract_data(table_cashflows[i][1], r"^us-gaap:NetCashProvidedByUsedInFinancingActivities", None, position_cash_flow[2])
                        previous_cash_flow_financing = extract_data(table_cashflows[i - 1][1], r"^us-gaap:NetCashProvidedByUsedInFinancingActivities", None, position_cash_flow[1])
                        cash_flow_financing = current_cash_flow_financing - previous_cash_flow_financing
                        result_data[13][i - 1] = cash_flow_financing
                    else:
                        update_msg("Something wrong when extracting data of cash flows from 10-K report" if IS_ENGLISH else "處理10-K財報之現金流量出現問題。")
            else:
                update_msg("Something wrong when extracting data of cash flows" if IS_ENGLISH else "處理財報之現金流量出現問題。")




            # Calculate some important indicator based on the gotten data
            # Gross margin
            # Gross profit / Revenue * 100%
            gross_margin = np.round(result_data[7][i - 1] / result_data[6][i - 1] * 100, 2) if (not np.isnan(result_data[7][i - 1]) and not np.isnan(result_data[6][i - 1]) and result_data[6][i - 1] != 0) else np.nan
            result_data[14][i - 1] = gross_margin


            # Operating margin
            # Earning before provision for taxes on income / Revenue * 100%
            operating_margin = np.round(result_data[8][i - 1] / result_data[6][i - 1] * 100, 2) if (not np.isnan(result_data[8][i - 1]) and not np.isnan(result_data[6][i - 1]) and result_data[6][i - 1] != 0) else np.nan
            result_data[15][i - 1] = operating_margin


            # Net income margin
            # Comprehensive income net of tax / Revenue * 100%
            net_income_margin = np.round(result_data[9][i - 1] / result_data[6][i - 1] * 100, 2) if (not np.isnan(result_data[9][i - 1]) and not np.isnan(result_data[6][i - 1]) and result_data[6][i - 1] != 0) else np.nan
            result_data[16][i - 1] = net_income_margin


            # Days inventory
            # (Revenues - Gross profit) / inventories
            days_inventory = np.round((result_data[6][i - 1] - result_data[7][i - 1]) / result_data[1][i - 1], 2) if (not np.isnan(result_data[6][i - 1]) and not np.isnan(result_data[7][i - 1]) and not np.isnan(result_data[1][i - 1]) and result_data[1][i - 1] != 0) else np.nan
            result_data[17][i - 1] = days_inventory


            # Return on assets
            # Comprehensive income net of tax / Assets * 100%
            ROA = np.round(result_data[10][i - 1] / result_data[0][i - 1] * 100, 2) if (not np.isnan(result_data[10][i - 1]) and not np.isnan(result_data[0][i - 1]) and result_data[0][i - 1] != 0) else np.nan
            result_data[18][i - 1] = ROA

            # Return on equity
            # Comprehensive income net of tax / Total stockholder's equity * 100%
            ROE = np.round(result_data[10][i - 1] / result_data[3][i - 1] * 100, 2) if (not np.isnan(result_data[10][i - 1]) and not np.isnan(result_data[3][i - 1]) and result_data[3][i - 1] != 0) else np.nan
            result_data[19][i - 1] = ROE

        result = pd.DataFrame(data = result_data, index = result_index, columns = result_columns)
        #result = result.round(2) -> does't work
        #result = result.apply(lambda x : "%.2f" % x, axis = 1) -> TypeError: cannot convert the series to <class 'float'>
        result = result.apply(lambda x : x.apply("{0:.2f}".format))  #-> OK; df.apply: Invoke function to series, not values!  series.apply: Invoke function on values of series! 
        #print("Data process finished")
        update_msg("Data process finished." if IS_ENGLISH else "資料處理完成。")
        return result
    
    
    elif(industry_type == "F"):
        #print("Financial industry")
        # Settings of pandas's dataframe
        
        result_columns = []  # Quarter date
        result_index = []
        
        if IS_ENGLISH:
            result_index = ["Assets", "Liabilities", "Total stockholder's equity",
                            "Risk weighted assets", 
                            "Total loans", "Non-performing loans", "Allowance for loan and lease losses",
                            "Total investment","Earning per share basic", "Earning per share diluted",
                             "Revenue", "Gross Profit", "Earning before provision for taxes on income", "Net income",
                            "Comprehensive income net of tax",
                            "Net cash from operating activities", "Net cash from investing activities", "Net cash from financing activities",
                            "Gross margin (%)", "Operating margin (%)", "Net income margin (%)", "Non-performing loans ratio (%)", "Capital adequacy ratio (%)",
                            "Coverage ratio (%)", "Return on assets (%)", "Return on equity (%)"]
        else:
            result_index = ["總資產", "總負債", "股東權益",
                            "風險性資產總額", 
                            "放款總額", "逾期放款", "放款備抵呆帳",
                            "總投資","基本每股盈餘", "稀釋每股盈餘",
                             "營業收入", "毛利", "稅前淨利", "淨收入",
                            "綜合收入",
                            "營業活動現金流量", "投資活動現金流量", "融資活動現金流量",
                            "毛利率 (%)", "營業利益率 (%)", "稅後淨利率 (%)", "逾期放款比率 (%)", "資本適足率 (%)",
                            "備抵呆帳覆蓋率 (%)", "資產報酬率 (%)", "股東權益報酬率 (%)"]
            
        result_data = [[0] * (len(reports) - 1) for _ in range(len(result_index))]
        
        #print(len(reports_sorted))





        # Extract data from the above tables version 2
        # Probably no 9 reports will be gotten!
        for i in range(1, len(reports)):
            # Add quarter date
            result_columns.append(reports_sorted[i][2].date())


            # Get assets
            result_data[0][i - 1] = extract_data(table_balances[i][1], r"^us-gaap:Assets$", None, position[0])


#             # Get inventories
#             result_data[1][i - 1] = extract_data(table_balances[i][1], r"^us-gaap:InventoryNet$", "true", position[0])


            # Get liabilities (May need to be calculated!)
            result_data[1][i - 1] = extract_data(table_balances[i][1], r"^us-gaap:Liabilities$", None, position[0])



            # Get total stockholder's equity (May need to be calculated!)
            if not np.isnan(extract_data(table_balances[i][1], r"^us-gaap:StockholdersEquity$", None, position[0])):
                result_data[2][i - 1] = extract_data(table_balances[i][1], r"^us-gaap:StockholdersEquity$", None, position[0])
            elif not np.isnan(extract_data(table_balances[i][1], r"^us-gaap:StockholdersEquity", None, position[0])):
                result_data[2][i - 1] = extract_data(table_balances[i][1], r"^us-gaap:StockholdersEquity", None, position[0])
            else:
                result_data[2][i - 1] = np.nan
            
            
            # Calculate liabilities or stockholder's equity

            for j in range(len(reports) - 1):
                if(not np.isnan(result_data[0][j]) and np.isnan(result_data[1][j]) and not np.isnan(result_data[2][j])):
                    result_data[1][j] = result_data[0][j] - result_data[2][j]
                elif(not np.isnan(result_data[0][j]) and not np.isnan(result_data[1][j]) and np.isnan(result_data[2][j])):
                    result_data[2][j] = result_data[0][j] - result_data[1][j]
                else:
                    pass
            
            # Get risk-weighted assets (under Basel 3 standardized)
            result_data[3][i - 1] = extract_data(table_risk_weighted_assets[i][1], r"^us-gaap:RiskWeightedAssets$", None, position[0])
            
            
            # Get total loans
            result_data[4][i - 1] = extract_data(table_balances[i][1], r"^us-gaap:FinancingReceivableExcludingAccruedInterestAfterAllowanceForCreditLoss$|^us-gaap:NotesReceivableNet$", None, position[0])
            
            
            # Get nonperforming loans
            result_data[5][i - 1] = extract_data(table_credit_quality[i][1], r"^us-gaap:FinancingReceivableExcludingAccruedInterestNonaccrual$|^us-gaap:FinancingReceivableRecordedInvestmentNonaccrualStatus$", None, position_nonperforming_loans)            
            # If data is not in table (with ix:nonfraction tag wrapped, the data may not be referenced)
#             if RISK_WEIGHTED_ASSETS_NOT_IN_TABLE:  
#                 pass
#             else:
        
            # Get allowance for loan and lease losses
            #print("allowance for loan")
            result_data[6][i - 1] = np.absolute(extract_data(table_balances[i][1], r"^us-gaap:FinancingReceivableAllowanceForCreditLossExcludingAccruedInterest$|^us-gaap:FinancingReceivableAllowanceForCreditLosses$", None, position[0]))
            
            
            
            # Get total investment (for insurance industry)
            result_data[7][i - 1] = extract_data(table_balances[i][1], r"^us-gaap:Investments$", None, position[0])                           

#             # Get Tier 1 capital (approximately equal to total stockholder's equity)
#             # Tier 1 capital = shareholder's equity(preferred stock + common stock) + retained earnings
#             preferred_stock = extract_data(table_balances[i][1], r"^us-gaap:RetainedEarnings", None, position[0])
#             retained_earnings = extract_data(table_balances[i][1], r"^us-gaap:RetainedEarnings", None, position[0])
#             result_data[3][i - 1] = result_data[2][i - 1] + retained_earnings

#             Calculate liabilities or stockholder's equity -- version 1

#             for j in range(8):
#                 if(not np.isnan(result_data[0][j]) and np.isnan(result_data[2][j]) and not np.isnan(result_data[3][j])):
#                     result_data[2][j] = result_data[0][j] - result_data[3][j]
#                 elif(not np.isnan(result_data[0][j]) and not np.isnan(result_data[2][j]) and np.isnan(result_data[3][j])):
#                     result_data[3][j] = result_data[0][j] - result_data[2][j]
#                 else:
#                     pass

#             # Calculate liabilities or stockholder's equity -- version 2
#             """
#             if(not np.isnan(result_data[0][i - 1]) and np.isnan(result_data[2][i - 1]) and not np.isnan(result_data[3][i - 1])):
#                 result_data[2][i - 1] = result_data[0][i - 1] - result_data[3][i - 1]
#             elif(not np.isnan(result_data[0][i - 1]) and not np.isnan(result_data[2][i - 1]) and np.isnan(result_data[3][i - 1])):
#                 result_data[3][i - 1] = result_data[0][i - 1] - result_data[2][i - 1]
#             else:
#                 pass
#             """



            # Difference between 10-K and 10-Q reports
            if(check_report_type(reports_sorted[i][0]) == "Q"):

                # Get EPS (basic)
                result_data[8][i - 1] = extract_data(table_operations[i][1], r"^us-gaap:EarningsPerShareBasic$", None, position_income[0])

                # Get EPS (diluted)
                result_data[9][i - 1] = extract_data(table_operations[i][1], r"^us-gaap:EarningsPerShareDiluted$", None, position_income[0])

                # Get revenues                
                if not np.isnan(extract_data(table_operations[i][1], r"^us-gaap:Revenue", "true", position_income[0])):                    
                    result_data[10][i - 1] = extract_data(table_operations[i][1], r"^us-gaap:Revenue", "true", position_income[0])
                elif not np.isnan(extract_data(table_operations[i][1], r"^us-gaap:Revenue", None, position_income[0])):
                    result_data[10][i - 1] = extract_data(table_operations[i][1], r"^us-gaap:Revenue", None, position_income[0])
                else:
                    result_data[10][i - 1] = np.nan



                # Get gross profit (May need to be calculated)
                cost_of_revenue = np.nan
                if not np.isnan(extract_data(table_operations[i][1], r"^us-gaap:CostOfRevenue$", "true", position_income[0])):
                    cost_of_revenue = extract_data(table_operations[i][1], r"^us-gaap:CostOfRevenue$", "true", position_income[0])
                elif not np.isnan(extract_data(table_operations[i][1], r"^us-gaap:CostOfRevenue$", None, position_income[0])):
                    cost_of_revenue = extract_data(table_operations[i][1], r"^us-gaap:CostOfRevenue$", None, position_income[0])
                else:
                    pass
                
                gross_profit = np.nan
                if not np.isnan(extract_data(table_operations[i][1], r"^us-gaap:GrossProfit$", "true", position_income[0])):
                    gross_profit = extract_data(table_operations[i][1], r"^us-gaap:GrossProfit$", "true", position_income[0])
                elif not np.isnan(extract_data(table_operations[i][1], r"^us-gaap:GrossProfit$", "true", position_income[0])):
                    gross_profit = extract_data(table_operations[i][1], r"^us-gaap:GrossProfit$", "true", position_income[0])
                else:
                    pass
                
                if not np.isnan(gross_profit):
                    result_data[11][i - 1] = gross_profit 
                elif not np.isnan(result_data[10][i - 1]) and not np.isnan(cost_of_revenue):
                    result_data[11][i - 1] = result_data[10][i - 1] - cost_of_revenue
                else:
                    result_data[11][i - 1] = np.nan

                    
                # Get Income before provision for income taxes
                if not np.isnan(extract_data(table_operations[i][1], r"^us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxes|^us-gaap:IncomeLossAttributableToParent$", "true", position_income[0])):
                    result_data[12][i - 1] = extract_data(table_operations[i][1], r"^us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxes|^us-gaap:IncomeLossAttributableToParent$", "true", position_income[0])
                elif not np.isnan(extract_data(table_operations[i][1], r"^us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxes|^us-gaap:IncomeLossAttributableToParent$", None, position_income[0])):
                    result_data[12][i - 1] = extract_data(table_operations[i][1], r"^us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxes|^us-gaap:IncomeLossAttributableToParent$", None, position_income[0])
                else:
                    result_data[12][i - 1] = np.nan


                # Get net income
                if not np.isnan(extract_data(table_operations[i][1], r"^us-gaap:NetIncomeLoss$|^us-gaap:NetIncomeLossAvailableToCommonStockholdersBasic$", "true", position_income[0])):
                    result_data[13][i - 1] = extract_data(table_operations[i][1], r"^us-gaap:NetIncomeLoss$|^us-gaap:NetIncomeLossAvailableToCommonStockholdersBasic$", "true", position_income[0])
                elif not np.isnan(extract_data(table_operations[i][1], r"^us-gaap:NetIncomeLoss$|^us-gaap:NetIncomeLossAvailableToCommonStockholdersBasic$", None, position_income[0])):
                    result_data[13][i - 1] = extract_data(table_operations[i][1], r"^us-gaap:NetIncomeLoss$|^us-gaap:NetIncomeLossAvailableToCommonStockholdersBasic$", None, position_income[0])
                else:
                    result_data[13][i - 1] = np.nan


                # Get comprehensive income net of tax
                if not np.isnan(extract_data(table_comprehensive_income[i][1], r"^us-gaap:ComprehensiveIncomeNetOfTax$|^us-gaap:ComprehensiveIncomeNetOfTaxIncludingPortionAttributableToNoncontrollingInterest$", "true", position_comprehensive[0])):
                    result_data[14][i - 1] = extract_data(table_comprehensive_income[i][1], r"^us-gaap:ComprehensiveIncomeNetOfTax$|^us-gaap:ComprehensiveIncomeNetOfTaxIncludingPortionAttributableToNoncontrollingInterest$", "true", position_comprehensive[0])
                elif not np.isnan(extract_data(table_comprehensive_income[i][1], r"^us-gaap:ComprehensiveIncomeNetOfTax$|^us-gaap:ComprehensiveIncomeNetOfTaxIncludingPortionAttributableToNoncontrollingInterest$", None, position_comprehensive[0])):
                    result_data[14][i - 1] = extract_data(table_comprehensive_income[i][1], r"^us-gaap:ComprehensiveIncomeNetOfTax$|^us-gaap:ComprehensiveIncomeNetOfTaxIncludingPortionAttributableToNoncontrollingInterest$", None, position_comprehensive[0])
                else:
                    result_data[14][i - 1] = np.nan

            elif(check_report_type(reports_sorted[i][0]) == "K"):

                # Get EPS (basic)
                result_data[8][i - 1] = extract_data(table_operations[i][1], r"^us-gaap:EarningsPerShareBasic$", None, position_income[2])

                # Get EPS (diluted)
                result_data[9][i - 1] = extract_data(table_operations[i][1], r"^us-gaap:EarningsPerShareDiluted$", None, position_income[2])


                # Get revenues (Need to get data from the previous quarter report, then calculate it)
                # 1. Get nine months accumulated data
                previous_revenues = 0
                if not np.isnan(extract_data(table_operations[i - 1][1], r"^us-gaap:Revenue", "true", position_income[1])):
                    previous_revenues = extract_data(table_operations[i - 1][1], r"^us-gaap:Revenue", "true", position_income[1])
                elif not np.isnan(extract_data(table_operations[i - 1][1], r"^us-gaap:Revenue", None, position_income[1])):
                    previous_revenues = extract_data(table_operations[i - 1][1], r"^us-gaap:Revenue", None , position_income[1])
                else:
                    pass


                # 2. Get revenues of whole fiscal year
                year_revenues = 0
                if not np.isnan(extract_data(table_operations[i][1], r"^us-gaap:Revenue", "true", position_income[2])):
                    year_revenues = extract_data(table_operations[i][1], r"^us-gaap:Revenue", "true", position_income[2])
                elif not np.isnan(extract_data(table_operations[i][1], r"^us-gaap:Revenue", None , position_income[2])):
                    year_revenues = extract_data(table_operations[i][1], r"^us-gaap:Revenue", None , position_income[2])
                else:
                    pass
                

                # 3. Calculate revenue from the above values
                revenues = year_revenues - previous_revenues
                result_data[10][i - 1] = revenues


                # Get gross profit (Need to get data from the previous quarter report, then calculate it)
                previous_gross_profit = np.nan
                if not np.isnan(extract_data(table_operations[i - 1][1], r"^us-gaap:GrossProfit$", "true", position_income[1])):
                    previous_gross_profit = extract_data(table_operations[i - 1][1], r"^us-gaap:GrossProfit$", "true", position_income[1])
                elif not np.isnan(extract_data(table_operations[i - 1][1], r"^us-gaap:GrossProfit$", None, position_income[1])):
                    previous_gross_profit = extract_data(table_operations[i - 1][1], r"^us-gaap:GrossProfit$", None, position_income[1])
                else:
                    pass
                
                
                year_gross_profit = np.nan
                if not np.isnan(extract_data(table_operations[i][1], r"^us-gaap:GrossProfit$", "true", position_income[2])):
                    year_gross_profit = extract_data(table_operations[i][1], r"^us-gaap:GrossProfit$", "true", position_income[2])
                elif not np.isnan(extract_data(table_operations[i][1], r"^us-gaap:GrossProfit$", None, position_income[2])):
                    year_gross_profit = extract_data(table_operations[i][1], r"^us-gaap:GrossProfit$", None, position_income[2])
                else:
                    pass
                
                
                gross_profit = np.nan
                if not np.isnan(year_gross_profit) and not np.isnan(previous_gross_profit):
                    gross_profit = year_gross_profit - previous_gross_profit
                else:
                    pass
                
                
                previous_cost_of_revenue = np.nan
                if not np.isnan(extract_data(table_operations[i - 1][1], r"^us-gaap:CostOfRevenue$", "true", position_income[1])):
                    previous_cost_of_revenue = extract_data(table_operations[i - 1][1], r"^us-gaap:CostOfRevenue$", "true", position_income[1])
                elif not np.isnan(extract_data(table_operations[i - 1][1], r"^us-gaap:CostOfRevenue$", None, position_income[1])):
                    previous_cost_of_revenue = extract_data(table_operations[i - 1][1], r"^us-gaap:CostOfRevenue$", None, position_income[1])
                else:
                    pass
                
                
                year_cost_of_revenue = np.nan
                if not np.isnan(extract_data(table_operations[i][1], r"^us-gaap:CostOfRevenue$", "true", position_income[2])):
                    year_cost_of_revenue = extract_data(table_operations[i][1], r"^us-gaap:CostOfRevenue$", "true", position_income[2])
                elif not np.isnan(extract_data(table_operations[i][1], r"^us-gaap:CostOfRevenue$", None, position_income[2])):
                    year_cost_of_revenue = extract_data(table_operations[i][1], r"^us-gaap:CostOfRevenue$", None, position_income[2])
                else:
                    pass
                
                
                cost_of_revenue = np.nan
                if not np.isnan(year_cost_of_revenue) and not np.isnan(previous_cost_of_revenue):                    
                    cost_of_revenue = year_cost_of_revenue - previous_cost_of_revenue
                else:
                    pass

                
                if not np.isnan(gross_profit):
                    result_data[11][i - 1] = gross_profit 
                elif not np.isnan(result_data[10][i - 1]) and not np.isnan(cost_of_revenue):
                    result_data[11][i - 1] = result_data[10][i - 1] - cost_of_revenue
                else:
                    result_data[11][i - 1] = np.nan



                # Get Income before provision for income taxes
                previous_income_before_tax = np.nan
                if not np.isnan(extract_data(table_operations[i - 1][1], r"^us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxes|^us-gaap:IncomeLossAttributableToParent$", "true", position_income[1])):
                    previous_income_before_tax = extract_data(table_operations[i - 1][1], r"^us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxes|^us-gaap:IncomeLossAttributableToParent$", "true", position_income[1])
                elif not np.isnan(extract_data(table_operations[i - 1][1], r"^us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxes|^us-gaap:IncomeLossAttributableToParent$", None, position_income[1])):
                    previous_income_before_tax = extract_data(table_operations[i - 1][1], r"^us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxes|^us-gaap:IncomeLossAttributableToParent$", None, position_income[1])
                else:
                    pass
                
                year_income_before_tax = np.nan
                if not np.isnan(extract_data(table_operations[i][1], r"^us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxes|^us-gaap:IncomeLossAttributableToParent$", "true", position_income[2])):
                    year_income_before_tax = extract_data(table_operations[i][1], r"^us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxes|^us-gaap:IncomeLossAttributableToParent$", "true", position_income[2])
                elif not np.isnan(extract_data(table_operations[i][1], r"^us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxes|^us-gaap:IncomeLossAttributableToParent$", None, position_income[2])):
                    year_income_before_tax = extract_data(table_operations[i][1], r"^us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxes|^us-gaap:IncomeLossAttributableToParent$", None, position_income[2])
                else:
                    pass
                
                if not np.isnan(year_income_before_tax) and not np.isnan(previous_income_before_tax):
                    result_data[12][i - 1] = year_income_before_tax - previous_income_before_tax
                else:
                    result_data[12][i - 1] = np.nan


                # Get net income
                previous_income = np.nan
                if not np.isnan(extract_data(table_operations[i - 1][1], r"^us-gaap:NetIncomeLoss$|^us-gaap:NetIncomeLossAvailableToCommonStockholdersBasic$", "true", position_income[1])):
                    previous_income = extract_data(table_operations[i - 1][1], r"^us-gaap:NetIncomeLoss$|^us-gaap:NetIncomeLossAvailableToCommonStockholdersBasic$", "true", position_income[1])
                elif not np.isnan(extract_data(table_operations[i - 1][1], r"^us-gaap:NetIncomeLoss$|^us-gaap:NetIncomeLossAvailableToCommonStockholdersBasic$", None, position_income[1])):
                    previous_income = extract_data(table_operations[i - 1][1], r"^us-gaap:NetIncomeLoss$|^us-gaap:NetIncomeLossAvailableToCommonStockholdersBasic$", None, position_income[1])
                else:
                    pass
                
                year_income = np.nan
                if not np.isnan(extract_data(table_operations[i][1], r"^us-gaap:NetIncomeLoss$|^us-gaap:NetIncomeLossAvailableToCommonStockholdersBasic$", "true", position_income[2])):
                    year_income = extract_data(table_operations[i][1], r"^us-gaap:NetIncomeLoss$|^us-gaap:NetIncomeLossAvailableToCommonStockholdersBasic$", "true", position_income[2])
                elif not np.isnan(extract_data(table_operations[i][1], r"^us-gaap:NetIncomeLoss$|^us-gaap:NetIncomeLossAvailableToCommonStockholdersBasic$", None, position_income[2])):
                    year_income = extract_data(table_operations[i][1], r"^us-gaap:NetIncomeLoss$|^us-gaap:NetIncomeLossAvailableToCommonStockholdersBasic$", None, position_income[2])
                else:
                    pass
                
                
                if not np.isnan(year_income) and not np.isnan(previous_income):
                    result_data[13][i - 1] = year_income - previous_income
                else:
                    result_data[13][i - 1] = np.nan


                # Get comprehensive income net of tax
                previous_comprehensive_income = np.nan
                if not np.isnan(extract_data(table_comprehensive_income[i - 1][1], r"^us-gaap:ComprehensiveIncomeNetOfTax$|^us-gaap:ComprehensiveIncomeNetOfTaxIncludingPortionAttributableToNoncontrollingInterest$", "true", position_comprehensive[1])):
                    previous_comprehensive_income = extract_data(table_comprehensive_income[i - 1][1], r"^us-gaap:ComprehensiveIncomeNetOfTax$|^us-gaap:ComprehensiveIncomeNetOfTaxIncludingPortionAttributableToNoncontrollingInterest$", "true", position_comprehensive[1])
                elif not np.isnan(extract_data(table_comprehensive_income[i - 1][1], r"^us-gaap:ComprehensiveIncomeNetOfTax$|^us-gaap:ComprehensiveIncomeNetOfTaxIncludingPortionAttributableToNoncontrollingInterest$", None, position_comprehensive[1])):
                    previous_comprehensive_income = extract_data(table_comprehensive_income[i - 1][1], r"^us-gaap:ComprehensiveIncomeNetOfTax$|^us-gaap:ComprehensiveIncomeNetOfTaxIncludingPortionAttributableToNoncontrollingInterest$", None, position_comprehensive[1])
                else:
                    pass
                
                year_comprehensive_income = np.nan
                if not np.isnan(extract_data(table_comprehensive_income[i][1], r"^us-gaap:ComprehensiveIncomeNetOfTax$|^us-gaap:ComprehensiveIncomeNetOfTaxIncludingPortionAttributableToNoncontrollingInterest$", "true", position_comprehensive[2])):
                    year_comprehensive_income = extract_data(table_comprehensive_income[i][1], r"^us-gaap:ComprehensiveIncomeNetOfTax$|^us-gaap:ComprehensiveIncomeNetOfTaxIncludingPortionAttributableToNoncontrollingInterest$", "true", position_comprehensive[2])
                elif not np.isnan(extract_data(table_comprehensive_income[i][1], r"^us-gaap:ComprehensiveIncomeNetOfTax$|^us-gaap:ComprehensiveIncomeNetOfTaxIncludingPortionAttributableToNoncontrollingInterest$", None, position_comprehensive[2])):
                    year_comprehensive_income = extract_data(table_comprehensive_income[i][1], r"^us-gaap:ComprehensiveIncomeNetOfTax$|^us-gaap:ComprehensiveIncomeNetOfTaxIncludingPortionAttributableToNoncontrollingInterest$", None, position_comprehensive[2])
                else:
                    pass
                
                
                if not np.isnan(year_comprehensive_income) and not np.isnan(previous_comprehensive_income):
                    result_data[14][i - 1] = year_comprehensive_income - previous_comprehensive_income
                else:
                    result_data[14][i - 1] = np.nan

            else:
                #print("Something wrong after filtering and sorting")
                update_msg("Something wrong after filtering and sorting." if IS_ENGLISH else "財報排序與過濾出現問題。")



            # Get net cash provided by operating activities 
            # No information of cash flow in current quarter period! Only accululated value is provided! Have special case!
            # Need some calculation to get cash flow in the quarter period
            if(check_report_type(reports_sorted[i - 1][0]) == "K"):
                # First quarter
                result_data[15][i - 1] = extract_data(table_cashflows[i][1], r"^us-gaap:NetCashProvidedByUsedInOperatingActivities", None, position_cash_flow[0])
                #print("Cash flow here!")
            elif(check_report_type(reports_sorted[i - 1][0]) == "Q"):
                if CASHFLOW_QUARTER_NEED_COUNT:
                    if(check_report_type(reports_sorted[i][0]) == "Q"):
                        current_cash_flow_operating = extract_data(table_cashflows[i][1], r"^us-gaap:NetCashProvidedByUsedInOperatingActivities", None, position_cash_flow[0])
                        previous_cash_flow_operating = extract_data(table_cashflows[i - 1][1], r"^us-gaap:NetCashProvidedByUsedInOperatingActivities", None, position_cash_flow[1])
                        cash_flow_operating = current_cash_flow_operating - previous_cash_flow_operating
                        result_data[15][i - 1] = cash_flow_operating
                    elif(check_report_type(reports_sorted[i][0]) == "K"):
                        current_cash_flow_operating = extract_data(table_cashflows[i][1], r"^us-gaap:NetCashProvidedByUsedInOperatingActivities", None, position_cash_flow[2])
                        previous_cash_flow_operating = extract_data(table_cashflows[i - 1][1], r"^us-gaap:NetCashProvidedByUsedInOperatingActivities", None, position_cash_flow[1])
                        cash_flow_operating = current_cash_flow_operating - previous_cash_flow_operating
                        result_data[15][i - 1] = cash_flow_operating
                    else:
                        update_msg("Something wrong when extracting data of cash flows from 10-K report" if IS_ENGLISH else "處理10-K財報之現金流量出現問題。")
                else:
                    if(check_report_type(reports_sorted[i][0]) == "Q"):            
                        result_data[15][i - 1] = extract_data(table_cashflows[i][1], r"^us-gaap:NetCashProvidedByUsedInOperatingActivities", None, position_cash_flow[0])
                    elif(check_report_type(reports_sorted[i][0]) == "K"):
                        current_cash_flow_operating = extract_data(table_cashflows[i][1], r"^us-gaap:NetCashProvidedByUsedInOperatingActivities", None, position_cash_flow[2])
                        previous_cash_flow_operating = extract_data(table_cashflows[i - 1][1], r"^us-gaap:NetCashProvidedByUsedInOperatingActivities", None, position_cash_flow[1])
                        cash_flow_operating = current_cash_flow_operating - previous_cash_flow_operating
                        result_data[15][i - 1] = cash_flow_operating
                    else:
                        update_msg("Something wrong when extracting data of cash flows from 10-K report" if IS_ENGLISH else "處理10-K財報之現金流量出現問題。")
            else:
                update_msg("Something wrong when extracting data of cash flows" if IS_ENGLISH else "處理財報之現金流量出現問題。")
                #print(check_report_type(reports_sorted[i - 1][0]))
                #print(reports_sorted[i - 1][2])



            # Get net cash provided by investing activities 
            # No information of cash flow in current quarter period! Only accululated value is provided!
            # Need some calculation to get cash flow in the quarter period
            if(check_report_type(reports_sorted[i - 1][0]) == "K"):
                # Q1
                result_data[16][i - 1] = extract_data(table_cashflows[i][1], r"^us-gaap:NetCashProvidedByUsedInInvestingActivities", None, position_cash_flow[0])


            elif(check_report_type(reports_sorted[i - 1][0]) == "Q"):
                if CASHFLOW_QUARTER_NEED_COUNT:
                    if(check_report_type(reports_sorted[i][0]) == "Q"):
                        current_cash_flow_investing = extract_data(table_cashflows[i][1], r"^us-gaap:NetCashProvidedByUsedInInvestingActivities", None, position_cash_flow[0])
                        previous_cash_flow_investing = extract_data(table_cashflows[i - 1][1], r"^us-gaap:NetCashProvidedByUsedInInvestingActivities", None, position_cash_flow[1])
                        cash_flow_investing = current_cash_flow_investing - previous_cash_flow_investing
                        result_data[16][i - 1] = cash_flow_investing
                    elif(check_report_type(reports_sorted[i][0]) == "K"):
                        current_cash_flow_investing = extract_data(table_cashflows[i][1], r"^us-gaap:NetCashProvidedByUsedInInvestingActivities", None, position_cash_flow[2])
                        previous_cash_flow_investing = extract_data(table_cashflows[i - 1][1], r"^us-gaap:NetCashProvidedByUsedInInvestingActivities", None, position_cash_flow[1])
                        cash_flow_investing = current_cash_flow_investing - previous_cash_flow_investing
                        result_data[16][i - 1] = cash_flow_investing
                    else:
                        update_msg("Something wrong when extracting data of cash flows from 10-K report" if IS_ENGLISH else "處理10-K財報之現金流量出現問題。")
                else:
                    if(check_report_type(reports_sorted[i][0]) == "Q"):
                        result_data[16][i - 1] = extract_data(table_cashflows[i][1], r"^us-gaap:NetCashProvidedByUsedInInvestingActivities", None, position_cash_flow[0])
                    elif(check_report_type(reports_sorted[i][0]) == "K"):
                        current_cash_flow_investing = extract_data(table_cashflows[i][1], r"^us-gaap:NetCashProvidedByUsedInInvestingActivities", None, position_cash_flow[2])
                        previous_cash_flow_investing = extract_data(table_cashflows[i - 1][1], r"^us-gaap:NetCashProvidedByUsedInInvestingActivities", None, position_cash_flow[1])
                        cash_flow_investing = current_cash_flow_investing - previous_cash_flow_investing
                        result_data[16][i - 1] = cash_flow_investing
                    else:
                        update_msg("Something wrong when extracting data of cash flows from 10-K report" if IS_ENGLISH else "處理10-K財報之現金流量出現問題。")
            else:
                update_msg("Something wrong when extracting data of cash flows" if IS_ENGLISH else "處理財報之現金流量出現問題。")




            # Get net cash provided by financing activities 
            # No information of cash flow in current quarter period! Only accululated value is provided!
            # Need some calculation to get cash flow in the quarter period
            if(check_report_type(reports_sorted[i - 1][0]) == "K"):
                # First quarter
                result_data[17][i - 1] = extract_data(table_cashflows[i][1], r"^us-gaap:NetCashProvidedByUsedInFinancingActivities", None, position_cash_flow[0])

            elif(check_report_type(reports_sorted[i - 1][0]) == "Q"):
                if CASHFLOW_QUARTER_NEED_COUNT:
                    if(check_report_type(reports_sorted[i][0]) == "Q"):
                        current_cash_flow_financing = extract_data(table_cashflows[i][1], r"^us-gaap:NetCashProvidedByUsedInFinancingActivities", None, position_cash_flow[0])
                        previous_cash_flow_financing = extract_data(table_cashflows[i - 1][1], r"^us-gaap:NetCashProvidedByUsedInFinancingActivities", None, position_cash_flow[1])
                        cash_flow_financing = current_cash_flow_financing - previous_cash_flow_financing
                        result_data[17][i - 1] = cash_flow_financing
                    elif(check_report_type(reports_sorted[i][0]) == "K"):
                        current_cash_flow_financing = extract_data(table_cashflows[i][1], r"^us-gaap:NetCashProvidedByUsedInFinancingActivities", None, position_cash_flow[2])
                        previous_cash_flow_financing = extract_data(table_cashflows[i - 1][1], r"^us-gaap:NetCashProvidedByUsedInFinancingActivities", None, position_cash_flow[1])
                        cash_flow_financing = current_cash_flow_financing - previous_cash_flow_financing
                        result_data[17][i - 1] = cash_flow_financing
                    else:
                        update_msg("Something wrong when extracting data of cash flows from 10-K report" if IS_ENGLISH else "處理10-K財報之現金流量出現問題。")
                else:
                    if(check_report_type(reports_sorted[i][0]) == "Q"):
                        result_data[17][i - 1] = extract_data(table_cashflows[i][1], r"^us-gaap:NetCashProvidedByUsedInFinancingActivities", None, position_cash_flow[0])
                    elif(check_report_type(reports_sorted[i][0]) == "K"):
                        current_cash_flow_financing = extract_data(table_cashflows[i][1], r"^us-gaap:NetCashProvidedByUsedInFinancingActivities", None, position_cash_flow[2])
                        previous_cash_flow_financing = extract_data(table_cashflows[i - 1][1], r"^us-gaap:NetCashProvidedByUsedInFinancingActivities", None, position_cash_flow[1])
                        cash_flow_financing = current_cash_flow_financing - previous_cash_flow_financing
                        result_data[17][i - 1] = cash_flow_financing
                    else:
                        update_msg("Something wrong when extracting data of cash flows from 10-K report" if IS_ENGLISH else "處理10-K財報之現金流量出現問題。")
            else:
                update_msg("Something wrong when extracting data of cash flows" if IS_ENGLISH else "處理財報之現金流量出現問題。")




            # Calculate some important indicator based on the gotten data
            # Gross margin
            # Gross profit / Revenue * 100%
            gross_margin = np.round(result_data[11][i - 1] / result_data[10][i - 1] * 100, 2) if (not np.isnan(result_data[11][i - 1]) and not np.isnan(result_data[10][i - 1]) and result_data[10][i - 1] != 0) else np.nan
            result_data[18][i - 1] = gross_margin


            # Operating margin
            # Earning before provision for taxes on income / Revenue * 100%
            operating_margin = np.round(result_data[12][i - 1] / result_data[10][i - 1] * 100, 2) if (not np.isnan(result_data[12][i - 1]) and not np.isnan(result_data[10][i - 1]) and result_data[10][i - 1] != 0) else np.nan
            result_data[19][i - 1] = operating_margin


            # Net income margin
            # Comprehensive income net of tax / Revenue * 100%
            net_income_margin = np.round(result_data[13][i - 1] / result_data[10][i - 1] * 100, 2) if (not np.isnan(result_data[13][i - 1]) and not np.isnan(result_data[10][i - 1]) and result_data[10][i - 1] != 0) else np.nan
            result_data[20][i - 1] = net_income_margin
            
            
            # Non-performing lonas ratio
            # Non-performing loans / Total loans * 100%
            non_performing_loans_ratio = np.round(result_data[5][i - 1] / result_data[4][i - 1] * 100, 2) if (not np.isnan(result_data[5][i - 1]) and not np.isnan(result_data[4][i - 1]) and result_data[4][i - 1] != 0) else np.nan
            result_data[21][i - 1] = non_performing_loans_ratio
            
            
            # Capital adequacy ratio
            # (Tier 1 capital + Tier 2 capital) / Risk weighted assets * 100% = Total stockholder's equity / Risk weighted assets * 100%
            capital_adequacy_ratio = np.round(result_data[2][i - 1] / result_data[3][i - 1] * 100, 2) if (not np.isnan(result_data[2][i - 1]) and not np.isnan(result_data[3][i - 1]) and result_data[3][i - 1] != 0) else np.nan
            result_data[22][i - 1] = capital_adequacy_ratio
            
            
            # Coverage ratio
            # Allowance for loan and lease losses / Non-performing loans * 100%
            coverage_ratio = np.round(result_data[6][i - 1] / result_data[5][i - 1] * 100, 2) if (not np.isnan(result_data[6][i - 1]) and not np.isnan(result_data[5][i - 1]) and result_data[5][i - 1] != 0) else np.nan
            result_data[23][i - 1] = coverage_ratio


#             # Days inventory
#             # (Revenues - Gross profit) / inventories
#             days_inventory = np.round((result_data[6][i - 1] - result_data[7][i - 1]) / result_data[1][i - 1], 2) if (not np.isnan(result_data[6][i - 1]) and not np.isnan(result_data[7][i - 1]) and not np.isnan(result_data[1][i - 1]) and result_data[1][i - 1] != 0) else np.nan
#             result_data[17][i - 1] = days_inventory


            # Return on assets
            # Comprehensive income net of tax / Assets * 100%
            ROA = np.round(result_data[14][i - 1] / result_data[0][i - 1] * 100, 2) if (not np.isnan(result_data[14][i - 1]) and not np.isnan(result_data[0][i - 1]) and result_data[0][i - 1] != 0) else np.nan
            result_data[24][i - 1] = ROA

            # Return on equity
            # Comprehensive income net of tax / Total stockholder's equity * 100%
            ROE = np.round(result_data[14][i - 1] / result_data[2][i - 1] * 100, 2) if (not np.isnan(result_data[14][i - 1]) and not np.isnan(result_data[2][i - 1]) and result_data[2][i - 1] != 0) else np.nan
            result_data[25][i - 1] = ROE

            
        
        result = pd.DataFrame(data = result_data, index = result_index, columns = result_columns)
        result = result.apply(lambda x : x.apply("{0:.2f}".format))  #-> OK; df.apply: Invoke function to series, not values!  series.apply: Invoke function on values of series! 
        update_msg("Data process finished." if IS_ENGLISH else "資料處理完成。")
        return result
        
        
    else:
        update_msg("Unknown industry type?!" if IS_ENGLISH else "未知的產業類別？")
        return None


# result = extract_from_reports(reports, industry_type, company_name)
# display(result)



# Deprecated below!
# Read "CONDENSED CONSOLIDATED STATEMENTS OF OPERATIONS (Unaudited)"
# table_name = "CONDENSED CONSOLIDATED STATEMENTS OF OPERATIONS (Unaudited)"

# result = reports[0].find('div', string = table_name).findNext('div').findNext('div').findNext('div').findNext('table')
# print(result)
# display(pd.DataFrame(result, dtype = "object"))  # Very uglyand wrong!!


# report_df = pd.read_html(str(reports[0].find('div', string = table_name).findNext('div').findNext('div').findNext('div').findNext('table')))
# display(pd.DataFrame(report_df))

# check_report_type(reports[1])


# ## Function definition: Visualization of financial statements. Save as .png and .csv

# In[7]:


# Section 3: Plot 4 figures using seaborn package according to the above dataframe
def plot_data(result, industry_type, company_name, stop_flag = None):

    
    result = result.astype("float64", copy = True)
    #print(df.dtypes)
    
    # Create a new folder of the company's name
    current_date = datetime.now().strftime("%Y-%m-%d")
    folder_name = r"results\\" + str(current_date) + re.sub(r'[\\\/:\*\?"<>\|\.]', '', company_name)
    if not os.path.isdir(folder_name):
        os.mkdir(folder_name)
    else:
        pass
    
    
    # Setting Chinese / English font
    if not IS_ENGLISH:
        plt.rcParams['font.sans-serif'] = ['Taipei Sans TC Beta']
    
    
    if(industry_type == 'N'):
        #rint("Industry:", industry_type)
        
        # Figure 1: Liabilities and Stockholder's equity stacked barchart (summation is assets)
        fig1 = plt.subplot(111)
        fig1.yaxis.set_major_locator(MaxNLocator(10))  # Max number of labels in y axis
        #fig1.xaxis.set_major_locator(MaxNLocator(len(result.columns)))  # Max number of Labels in x axis

        
        x = list(result.columns)  # x labels (quarter date)
        x_temp = np.arange(len(x))
        #x = [1,2,3,4,5,6,7,8]

        Liabilities = result.loc['Liabilities', :] if IS_ENGLISH else result.loc['總負債', :]
        Equity = result.loc["Total stockholder's equity", :] if IS_ENGLISH else result.loc['股東權益', :]
        #print(Liabilities)
        #print(Equity)

        plt.bar(x_temp, Liabilities, color='blue', width=0.5, zorder=3, label = "Liabilities" if IS_ENGLISH else "總負債")
        #plt.ylabel("Liabilities") if IS_ENGLISH else plt.ylabel("總負債")
        
        plt.bar(x_temp,Equity,color='green',label="Total stockholder's equity" if IS_ENGLISH else "股東權益", width=0.5, bottom=Liabilities, zorder=3)
        plt.title("Company's balance\n(" + company_name + ")", fontsize=18) if IS_ENGLISH else plt.title("公司負債與股東權益\n(" + company_name + ")", fontsize=18)
        plt.xticks(rotation=45)
        plt.xticks(x_temp, x)
        plt.ylabel('USD')
        plt.legend(bbox_to_anchor=(1.02,0.7), loc='upper left')
        plt.grid(axis='y')
        #plt.show()
        file_name = folder_name + "\\" + str(current_date) + re.sub(r'[\\\/:\*\?"<>\|\.]', '', company_name) + "_Liabilities and Stockholder's equity.png"
        plt.tight_layout()
        plt.subplots_adjust(left = 0.1, right = 0.6)
        plt.savefig(file_name)
        plt.close()

        
        # Break point
        if(stop_flag.is_set()):
            return None




        # Figure 2: Cash flow stacked barchart
        fig2 = plt.subplot(111)
        fig2.yaxis.set_major_locator(MaxNLocator(10)) # Max number of labels in y axis
        #fig2.xaxis.set_major_locator(MaxNLocator(len(result.columns)))  # Max number of Labels in x axis
        
        operating =  result.loc['Net cash from operating activities', :] if IS_ENGLISH else result.loc['營業活動現金流量', :]

        investing = result.loc['Net cash from investing activities', :] if IS_ENGLISH else result.loc['投資活動現金流量', :]

        financing = result.loc['Net cash from financing activities', :] if IS_ENGLISH else result.loc['融資活動現金流量', :]

        plt.bar(x_temp, operating, color='blue', label='Net cash from\noperating activities' if IS_ENGLISH else "營業活動現金流量", width=0.5, zorder=3)

        # Stack upward or downward depends on the sign of value. Downward for negative values
        # Reference: https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.bar.html
        baseline = []



        # Setting baseline for stacking investing values
        for idx in range(len(result.columns)):
            if(investing[idx] < 0):
                if(operating[idx] < 0):
                    baseline.append(operating[idx]) 
                else:
                    baseline.append(0) 
            else:
                if(operating[idx] < 0):
                    baseline.append(0) 
                else:
                    baseline.append(operating[idx]) 


        plt.bar(x_temp, investing, color='green',label='Net cash from\ninvesting activities' if IS_ENGLISH else "投資活動現金流量", width=0.5, zorder=3, bottom=baseline)



        baseline2 = []
        for idx in range(len(result.columns)):

            # Same sign of investing value and financing value (++ or --)
            if(investing[idx]*financing[idx] >= 0):
                if(operating[idx]*investing[idx] >= 0):                    
                    baseline2.append(investing[idx] + operating[idx])
                else:
                    baseline2.append(investing[idx])

            # Different sign of investing and financing value (+- or -+)
            else:

                # Same sign of investing value and operating value (++ or --)
                if(operating[idx]*investing[idx] >= 0):
                    baseline2.append(0)
                    #print('second')

                # Different sign of investing and operating value (+- or -+)    
                else:
                    baseline2.append(operating[idx])
                    #print('third')
                    #print(operating[idx]*investing[idx])

        plt.bar(x_temp, financing, color='gray', label='Net cash from\nfinancing activities' if IS_ENGLISH else "融資活動現金流量", width=0.5, zorder=3, bottom=baseline2)

        plt.title('Cash flows\n(' + company_name + ")", fontsize=18) if IS_ENGLISH else plt.title('現金流量\n(' + company_name + ")", fontsize=18)
        plt.xticks(rotation=45)
        plt.xticks(x_temp, x)
        plt.ylabel('USD')
        plt.legend(bbox_to_anchor=(1.02, 0.7), loc='upper left')
        plt.grid(axis='y')
        #plt.show()
        file_name = folder_name + "\\" + str(current_date) + re.sub(r'[\\\/:\*\?"<>\|\.]', '', company_name) + "_Cash flows.png"
        plt.tight_layout()
        plt.subplots_adjust(left = 0.1, right = 0.6)
        plt.savefig(file_name)
        plt.close()

        
        # Break point
        if(stop_flag.is_set()):
            return None


        # Figure 3: Operating circumstance
        fig3 = plt.subplot(111)
        fig3.yaxis.set_major_locator(MaxNLocator(10)) # Max number of labels in y axis
        #fig3.xaxis.set_major_locator(MaxNLocator(len(result.columns)))  # Max number of Labels in x axis
        
        plt.xticks(rotation=45)  # Need to place this setting before plotting or interpreter will confuse

        revenue = result.loc['Revenue', :] if IS_ENGLISH else result.loc['營業收入', :]
        gross_profit = result.loc['Gross profit', :] if IS_ENGLISH else result.loc['毛利', :]
        net_income = result.loc['Net income', :] if IS_ENGLISH else result.loc['淨收入', :]
        comprehensive_income = result.loc['Comprehensive income net of tax', :] if IS_ENGLISH else result.loc['綜合收入', :]         
        other_income = comprehensive_income - net_income
        days_inventory = result.loc['Days Inventory (days)', :] if IS_ENGLISH else result.loc['存貨周轉天數 (天)', :]

        #x_temp = np.arange(len(x))

        br1 = plt.bar(x_temp - 0.2, revenue, color='blue',label='Revenues' if IS_ENGLISH else "營業收入", width=0.6, zorder=2, alpha = 0.85)
        br2 = plt.bar(x_temp - 0.2, gross_profit, color='green',label='Gross profit' if IS_ENGLISH else "毛利", width=0.6, zorder=2, alpha = 0.85)
        br3 = plt.bar(x_temp - 0.2, net_income, color='orange',label='Net income' if IS_ENGLISH else "淨收入", width=0.6, zorder=3, alpha = 0.85)
        br4 = plt.bar(x_temp + 0.2, other_income, color='brown',label='Other income' if IS_ENGLISH else "其他收入", width=0.4, zorder=1, alpha = 0.85)



        # Double y axes
        fig3_1 = fig3.twinx()
        ln1 = fig3_1.plot(x_temp, days_inventory, color='red', marker='D',label='Days inventory' if IS_ENGLISH else "其他收入")

        plt.xticks(x_temp, x)

        plt.title("Operating circumstances\n(" + company_name + ")", fontsize=18) if IS_ENGLISH else plt.title("營運狀況\n(" + company_name + ")", fontsize=18)

        #plt.ylabel('Million USD')


        fig3.set_ylabel('USD')
        fig3_1.set_ylabel('Days')

        #print(type(br1))

        #brs_lns = br1 + br2 + br3 + br4 + ln1
        #brs_lns = list(br1) + ln1
        brs_lns = [br1, br2, br3, br4] + ln1
        #labels = [bl.get_label() for bl in brs_lns]
        plt.legend(handles = brs_lns, bbox_to_anchor=(1.2,0.7), loc='upper left')
        #plt.legend(bbox_to_anchor=(1.02,0.7), loc='upper left')

        plt.grid(axis='y')

        #plt.show()
        file_name = folder_name + "\\" + str(current_date) + re.sub(r'[\\\/:\*\?"<>\|\.]', '', company_name) + "_Operating circumstances.png"
        plt.tight_layout()
        plt.subplots_adjust(left = 0.1, right = 0.6)
        plt.savefig(file_name)
        plt.close()

        
        # Break point
        if(stop_flag.is_set()):
            return None


        # Figure 4: Competitiveness
        gross_margin = result.loc['Gross margin (%)', :] if IS_ENGLISH else result.loc['毛利率 (%)', :]
        operating_margin = result.loc['Operating margin (%)', :] if IS_ENGLISH else result.loc['營業利益率 (%)', :]
        net_income_margin = result.loc['Net income margin (%)', :] if IS_ENGLISH else result.loc['稅後淨利率 (%)', :]


        fig4 = plt.subplot(111)
        fig4.yaxis.set_major_locator(MaxNLocator(10))
        #fig4.xaxis.set_major_locator(MaxNLocator(len(result.columns)))  # Max number of Labels in x axis

        fig4.plot(x_temp,gross_margin,color='blue', marker='o',label='Gross margin (%)' if IS_ENGLISH else "毛利率 (%)")
        fig4.plot(x_temp,operating_margin,color='green', marker='o',label='Operating margin (%)' if IS_ENGLISH else "營業利益率 (%)")
        fig4.plot(x_temp,net_income_margin,color='orange', marker='o',label='Net income margin (%)' if IS_ENGLISH else "稅後淨利率 (%)")

        fig4.legend(bbox_to_anchor=(1.02,0.7), loc='upper left')
        fig4.grid(axis='y')
        plt.xticks(rotation=45)
        plt.xticks(x_temp, x)
        plt.title('Competitativeness\n(' + company_name + ')', fontsize=18) if IS_ENGLISH else plt.title('競爭力\n(' + company_name + ')', fontsize=18)
        fig4.set_ylabel('%')
        #plt.show()
        file_name = folder_name + "\\" + str(current_date) + re.sub(r'[\\\/:\*\?"<>\|\.]', '', company_name) + "_Competitativeness.png"
        plt.tight_layout()
        plt.subplots_adjust(left = 0.1, right = 0.6)
        plt.savefig(file_name)
        plt.close()



        # Break point
        if(stop_flag.is_set()):
            return None
        
        

        # Figure 5: Investment return
        fig5 = plt.subplot(111)
        fig5.yaxis.set_major_locator(MaxNLocator(10))
        #fig5.xaxis.set_major_locator(MaxNLocator(len(result.columns)))  # Max number of Labels in x axis
        plt.xticks(rotation=45)

        earning_per_share_basic = result.loc['Earning per share basic', :] if IS_ENGLISH else result.loc["基本每股盈餘", :]
        earning_per_share_diluted = result.loc['Earning per share diluted', :] if IS_ENGLISH else result.loc["稀釋每股盈餘", :]
        return_on_assets = result.loc['Return on assets (%)', :] if IS_ENGLISH else result.loc["資產報酬率 (%)", :]
        return_on_equity = result.loc['Return on equity (%)', :] if IS_ENGLISH else result.loc["股東權益報酬率 (%)", :]

        ln1 = plt.plot(x_temp,earning_per_share_basic,color='blue', marker='o',label='Earning per share\n(basic)' if IS_ENGLISH else "基本每股盈餘")
        ln2 = plt.plot(x_temp,earning_per_share_diluted,color='green', marker='o',label='Earning per share\n(diluted)' if IS_ENGLISH else "稀釋每股盈餘")


        # Double y axes
        fig5_1 = fig5.twinx()
        ln3 = fig5_1.plot(x_temp, return_on_assets, color='orange', marker='D',label='Return on assets' if IS_ENGLISH else "資產報酬率 (%)")
        ln4 = fig5_1.plot(x_temp, return_on_equity, color='brown', marker='D',label='Return on equity' if IS_ENGLISH else "股東權益報酬率 (%)")

        plt.xticks(x_temp, x)

        plt.title("Investment return\n(" + company_name + ")", fontsize=18) if IS_ENGLISH else plt.title("投資回報\n(" + company_name + ")", fontsize=18)




        fig5.set_ylabel('EPS (USD)')
        fig5_1.set_ylabel('Return (%)')

        #print(type(br1))

        #brs_lns = br1 + br2 + br3 + br4 + ln1
        #brs_lns = list(br1) + ln1
        lns = ln1 + ln2 + ln3 + ln4
        #labels = [bl.get_label() for bl in brs_lns]
        plt.legend(handles = lns, bbox_to_anchor=(1.2,0.7), loc='upper left')
        #plt.legend(bbox_to_anchor=(1.02,0.7), loc='upper left')

        plt.grid(axis='y')

        #plt.show()
        file_name = folder_name + "\\" + str(current_date) + re.sub(r'[\\\/:\*\?"<>\|\.]', '', company_name) + "_Investment return.png"
        plt.tight_layout()
        plt.subplots_adjust(left = 0.1, right = 0.6)
        plt.savefig(file_name)
        plt.close()
        
        # Break point
        if(stop_flag.is_set()):
            return None
        
        
        # Save the financial statements as .csv
        result.to_csv(folder_name + "\\" + "Financial Statements.csv", encoding = "utf-8")
        
        update_msg("Financial statements and their visualization are saved successfully!" if IS_ENGLISH else "財報圖表已成功儲存完畢！")
        #print("plot_data的folder_name:", folder_name)
        return (folder_name, company_name)
    
    
        
        
        
    elif(industry_type == 'F'):
        #print("Financial industry")
        
        # Figure 1: Liabilities and Stockholder's equity stacked barchart (summation is assets)
        fig1 = plt.subplot(111)
        fig1.yaxis.set_major_locator(MaxNLocator(10))  # Max number of labels in y axis
        #fig1.xaxis.set_major_locator(MaxNLocator(len(result.columns)))  # Max number of Labels in x axis

        x = list(result.columns)  # x labels (quarter date)
        x_temp = np.arange(len(x))  # For bar chart's offset
        #x = [1,2,3,4,5,6,7,8]

        
        Liabilities = result.loc['Liabilities', :] if IS_ENGLISH else result.loc['總負債', :]
        Equity = result.loc["Total stockholder's equity", :] if IS_ENGLISH else result.loc['股東權益', :]
        Investment = result.loc["Total investment", :] if IS_ENGLISH else result.loc['總投資', :]
        #Investment = pd.Series([1000000] * 8, dtype = "float64")
        Risk_Weighted_Assets = result.loc["Risk weighted assets", :] if IS_ENGLISH else result.loc['風險性資產總額', :]
        #Risk_Weighted_Assets = pd.Series([np.nan] * 8, dtype = "float64")

        plt.bar(x_temp - 0.2, Liabilities, color='blue',label='Liabilities' if IS_ENGLISH else '總負債', width=0.5, zorder=3)
        plt.bar(x_temp - 0.2, Equity,color='green',label="Total stockholder's equity" if IS_ENGLISH else '股東權益', width=0.5, bottom=Liabilities, zorder=3)
        plt.bar(x_temp, Investment, color='orange',label="Total investment" if IS_ENGLISH else '總投資', width=0.5, zorder=3) if (not Investment.isna().all()) else None
        plt.bar(x_temp + 0.2, Risk_Weighted_Assets,color='red',label="Risk weighted assets" if IS_ENGLISH else '風險性資產總額', width=0.4, zorder=3) if (not Risk_Weighted_Assets.isna().all()) else None
        plt.xticks(x_temp, x)
        
        plt.title("Company's Balance\n(" + company_name + ")", fontsize=18) if IS_ENGLISH else plt.title("公司負債與股東權益\n(" + company_name + ")", fontsize=18)
        
        plt.xticks(rotation=45)
        plt.ylabel('USD')
        plt.legend(bbox_to_anchor=(1.02,0.7), loc='upper left')
        plt.grid(axis='y')
        #plt.show()
        file_name = folder_name + "\\" + str(current_date) + re.sub(r'[\\\/:\*\?"<>\|\.]', '', company_name) + "_Liabilities and Stockholder's equity.png"
        plt.tight_layout()
        plt.subplots_adjust(left = 0.1, right = 0.6)
        plt.savefig(file_name)
        plt.close()
        
        # Break point
        if(stop_flag.is_set()):
            return None
        
#         # Figure 2: Loans composition (if having loans)
#         Total_loans = result.loc['Total loans', :]
#         if (not Total_loans.isna().all()):
#             fig2 = plt.subplot(111)
#             fig2.yaxis.set_major_locator(MaxNLocator(10))  # Max number of labels in y axis
            
#             Allowance_for_loans_and_lease_losses = result.loc['Allowance for loan and lease losses', :]
#             Nonperforming_loans = result.loc['Non-performing loans', :]
#             Performing_loans = Total_loans + Allowance_for_loans_and_lease_losses - Nonperforming_loans
            
#             plt.bar(x, Performing_loans, color='blue',label='Performing loans', width=60, zorder=3) if (not Performing_loans.isna().all()) else None
#             plt.bar(x, Nonperforming_loans,color='green',label="Non-performing loans", width=60, bottom=Performing_loans, zorder=3) if (not Nonperforming_loans.isna().all()) else None
#             plt.bar(x, -Allowance_for_loans_and_lease_losses, color='orange',label="Allowance for loan and lease losses", width=60, zorder=3) if (not Allowance_for_loans_and_lease_losses.isna().all()) else None
            
#             plt.title("Loans' composition\n(" + company_name + ")", fontsize=18)
#             plt.xticks(rotation=45)
#             plt.ylabel('Million USD')
#             plt.legend(bbox_to_anchor=(1.02,0.7), loc='upper left')
#             plt.grid(axis='y')
#             plt.show()
            
#         else:
#             pass
        
        
        # Figure 2: Cash flow stacked barchart
        fig2 = plt.subplot(111)
        fig2.yaxis.set_major_locator(MaxNLocator(10)) # Max number of labels in y axis
        #fig2.xaxis.set_major_locator(MaxNLocator(len(result.columns)))  # Max number of Labels in x axis
        
        operating =  result.loc['Net cash from operating activities', :] if IS_ENGLISH else result.loc['營業活動現金流量', :]

        investing = result.loc['Net cash from investing activities', :] if IS_ENGLISH else result.loc['投資活動現金流量', :]

        financing = result.loc['Net cash from financing activities', :] if IS_ENGLISH else result.loc['融資活動現金流量', :]

        plt.bar(x_temp, operating, color='blue', label='Net cash from\noperating activities' if IS_ENGLISH else '營業活動現金流量', width=0.5, zorder=3)

        # Stack upward or downward depends on the sign of value. Downward for negative values
        # Reference: https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.bar.html
        baseline = []



        # Setting baseline for stacking investing values
        for idx in range(len(result.columns)):
            if(investing[idx] < 0):
                if(operating[idx] < 0):
                    baseline.append(operating[idx]) 
                else:
                    baseline.append(0) 
            else:
                if(operating[idx] < 0):
                    baseline.append(0) 
                else:
                    baseline.append(operating[idx]) 


        plt.bar(x_temp, investing, color='green',label='Net cash from\ninvesting activities' if IS_ENGLISH else '投資活動現金流量', width=0.5, zorder=3, bottom=baseline)

        baseline2 = []
        for idx in range(len(result.columns)):

            # Same sign of investing value and financing value (++ or --)
            if(investing[idx]*financing[idx] >= 0):
                if(operating[idx]*investing[idx] >= 0):                    
                    baseline2.append(investing[idx] + operating[idx])
                else:
                    baseline2.append(investing[idx])

            # Different sign of investing and financing value (+- or -+)
            else:

                # Same sign of investing value and operating value (++ or --)
                if(operating[idx]*investing[idx] >= 0):
                    baseline2.append(0)
                    #print('second')

                # Different sign of investing and operating value (+- or -+)    
                else:
                    baseline2.append(operating[idx])
                    #print('third')
                    #print(operating[idx]*investing[idx])

        plt.bar(x_temp, financing, color='gray', label='Net cash from\nfinancing activities' if IS_ENGLISH else '融資活動現金流量', width=0.5, zorder=3, bottom=baseline2)

        plt.title('Cash flows\n(' + company_name + ")", fontsize=18) if IS_ENGLISH else plt.title('現金流量\n(' + company_name + ")", fontsize=18)
        plt.xticks(rotation=45)
        plt.xticks(x_temp, x)
        plt.ylabel('USD')
        plt.legend(bbox_to_anchor=(1.02, 0.7), loc='upper left')
        plt.grid(axis='y')
        #plt.show()
        file_name = folder_name + "\\" + str(current_date) + re.sub(r'[\\\/:\*\?"<>\|\.]', '', company_name) + "_Cash flows.png"
        plt.tight_layout()
        plt.subplots_adjust(left = 0.1, right = 0.6)
        plt.savefig(file_name)
        plt.close()
        
        
        # Break point
        if(stop_flag.is_set()):
            return None
        
        
        
        # Figure 3: Operating circumstance
        fig3 = plt.subplot(111)
        fig3.yaxis.set_major_locator(MaxNLocator(10)) # Max number of labels in y axis
        plt.xticks(rotation=45)  # Need to place this setting before plotting or interpreter will confuse
        plt.grid(True, axis='y', zorder = 0)

        revenue = result.loc['Revenue', :] if IS_ENGLISH else result.loc['營業收入', :]
        gross_profit = result.loc['Gross Profit', :] if IS_ENGLISH else result.loc['毛利', :]
        net_income = result.loc['Net income', :] if IS_ENGLISH else result.loc['淨收入', :]
        comprehensive_income = result.loc['Comprehensive income net of tax', :] if IS_ENGLISH else result.loc['綜合收入', :]
        other_income = comprehensive_income - net_income
        
        nonperforming_loans_ratio = result.loc["Non-performing loans ratio (%)", :] if IS_ENGLISH else result.loc['逾期放款比率 (%)', :]
        capital_adequacy_ratio = result.loc["Capital adequacy ratio (%)", :] if IS_ENGLISH else result.loc['資本適足率 (%)', :]
        coverage_ratio = result.loc["Coverage ratio (%)", :] if IS_ENGLISH else result.loc['備抵呆帳覆蓋率 (%)', :]

        x_temp = np.arange(len(x))

        br1 = plt.bar(x_temp - 0.2, revenue, color='blue',label='Revenues' if IS_ENGLISH else '營業收入', width=0.6, zorder=3)
        br2 = plt.bar(x_temp - 0.2, gross_profit, color='green',label='Gross profit' if IS_ENGLISH else '毛利', width=0.6, zorder=3)  if (not gross_profit.isna().all()) else None
        br3 = plt.bar(x_temp - 0.2, net_income, color='orange',label='Net income' if IS_ENGLISH else '淨收入', width=0.6, zorder=3, alpha = 1)
        br4 = plt.bar(x_temp + 0.2, other_income, color='brown',label='Other income' if IS_ENGLISH else '其他收入', width=0.4, zorder=3, alpha = 1)



        # Double y axes
        fig3_1 = fig3.twinx()
        ln1 = fig3_1.plot(x_temp, nonperforming_loans_ratio, color='red', marker='D',label='Non-performing\nloans ratio' if IS_ENGLISH else '逾期放款比率') if (not nonperforming_loans_ratio.isna().all()) else None
        ln2 = fig3_1.plot(x_temp, capital_adequacy_ratio, color='purple', marker='D',label='Capital adequacy\nratio' if IS_ENGLISH else '資本適足率') if (not capital_adequacy_ratio.isna().all()) else None
        ln3 = fig3_1.plot(x_temp, coverage_ratio, color='pink', marker='D',label='Coverage ratio' if IS_ENGLISH else '備抵呆帳覆蓋率') if (not coverage_ratio.isna().all()) else None
        #ln3 = None (for test)
        
        plt.xticks(x_temp, x)

        plt.title("Operating circumstances\n(" + company_name + ")", fontsize=18) if IS_ENGLISH else plt.title("營運狀況\n(" + company_name + ")", fontsize=18)

        #plt.ylabel('Million USD')


        fig3.set_ylabel('USD')
        fig3_1.set_ylabel('%')

        #print(type(br1))

        #brs_lns = br1 + br2 + br3 + br4 + ln1
        #brs_lns = list(br1) + ln1
        brs_lns = [br1, br3, br4] + (ln1 if ln1 else []) + (ln2 if ln2 else []) + (ln3 if ln3 else [])
        if br2:
            #pass
            #print("br2 is None")
            brs_lns.append(br2) 
        else:
            pass
        
        
        #labels = [bl.get_label() for bl in brs_lns]
        plt.legend(handles = brs_lns, bbox_to_anchor=(1.2,0.7), loc='upper left')
        #plt.legend(bbox_to_anchor=(1.02,0.7), loc='upper left')

        #plt.show()
        file_name = folder_name + "\\" + str(current_date) + re.sub(r'[\\\/:\*\?"<>\|\.]', '', company_name) + "_Operating circumstances.png"
        plt.tight_layout()
        plt.subplots_adjust(left = 0.1, right = 0.6)
        plt.savefig(file_name)
        plt.close()
        
        
        # Break point
        if(stop_flag.is_set()):
            return None
        
        
        
        # Figure 4: Competitiveness
        gross_margin = result.loc["Gross margin (%)", :] if IS_ENGLISH else result.loc["毛利率 (%)", :]
        operating_margin = result.loc['Operating margin (%)', :] if IS_ENGLISH else result.loc["營業利益率 (%)", :]
        net_income_margin = result.loc['Net income margin (%)', :] if IS_ENGLISH else result.loc["稅後淨利率 (%)", :]


        fig4 = plt.subplot(111)
        fig4.yaxis.set_major_locator(MaxNLocator(10))
        #fig4.xaxis.set_major_locator(MaxNLocator(len(result.columns)))  # Max number of Labels in x axis

        fig4.plot(x_temp,gross_margin,color='blue', marker='o',label='Gross margin (%)' if IS_ENGLISH else "毛利率 (%)") if (not gross_margin.isna().all()) else None
        fig4.plot(x_temp,operating_margin,color='green', marker='o',label='Operating margin (%)' if IS_ENGLISH else "營業利益率 (%)") if (not operating_margin.isna().all()) else None
        fig4.plot(x_temp,net_income_margin,color='orange', marker='o',label='Net income margin (%)' if IS_ENGLISH else "稅後淨利率 (%)")

        fig4.legend(bbox_to_anchor=(1.02,0.7), loc='upper left')
        fig4.grid(axis='y')
        plt.xticks(rotation=45)
        plt.xticks(x_temp, x)
        plt.title('Competitativeness\n(' + company_name + ')', fontsize=18) if IS_ENGLISH else plt.title('競爭力\n(' + company_name + ')', fontsize=18)
        fig4.set_ylabel('%')
        #plt.show()
        file_name = folder_name + "\\" + str(current_date) + re.sub(r'[\\\/:\*\?"<>\|\.]', '', company_name) + "_Competitativeness.png"
        plt.tight_layout()
        plt.subplots_adjust(left = 0.1, right = 0.6)
        plt.savefig(file_name)
        plt.close()
        
        
        # Break point
        if(stop_flag.is_set()):
            return None
        
        
        
        # Figure 5: Investment return
        fig5 = plt.subplot(111)
        fig5.yaxis.set_major_locator(MaxNLocator(10))
        #fig5.xaxis.set_major_locator(MaxNLocator(len(result.columns)))  # Max number of Labels in x axis
        plt.xticks(rotation=45)

        earning_per_share_basic = result.loc['Earning per share basic', :] if IS_ENGLISH else result.loc["基本每股盈餘", :]
        earning_per_share_diluted = result.loc['Earning per share diluted', :] if IS_ENGLISH else result.loc["稀釋每股盈餘", :]
        return_on_assets = result.loc['Return on assets (%)', :] if IS_ENGLISH else result.loc["資產報酬率 (%)", :]
        return_on_equity = result.loc['Return on equity (%)', :] if IS_ENGLISH else result.loc["股東權益報酬率 (%)", :]

        ln1 = plt.plot(x_temp,earning_per_share_basic,color='blue', marker='o',label='Earning per share\n(basic)' if IS_ENGLISH else "基本每股盈餘")
        ln2 = plt.plot(x_temp,earning_per_share_diluted,color='green', marker='o',label='Earning per share\n(diluted)' if IS_ENGLISH else "稀釋每股盈餘")


        # Double y axes
        fig5_1 = fig5.twinx()
        ln3 = fig5_1.plot(x_temp, return_on_assets, color='orange', marker='D',label='Return on assets' if IS_ENGLISH else "資產報酬率 (%)")
        ln4 = fig5_1.plot(x_temp, return_on_equity, color='brown', marker='D',label='Return on equity' if IS_ENGLISH else "股東權益報酬率 (%)")

        plt.xticks(x_temp, x)

        plt.title("Investment return\n(" + company_name + ")", fontsize=18) if IS_ENGLISH else plt.title("投資回報\n(" + company_name + ")", fontsize=18)




        fig5.set_ylabel('EPS (USD)')
        fig5_1.set_ylabel('Return (%)')

        #print(type(br1))

        #brs_lns = br1 + br2 + br3 + br4 + ln1
        #brs_lns = list(br1) + ln1
        lns = ln1 + ln2 + ln3 + ln4
        #labels = [bl.get_label() for bl in brs_lns]
        plt.legend(handles = lns, bbox_to_anchor=(1.2,0.7), loc='upper left', fontsize = "8")
        #plt.legend(bbox_to_anchor=(1.02,0.7), loc='upper left')

        plt.grid(axis='y')

        #plt.show()
        file_name = folder_name + "\\" + str(current_date) + re.sub(r'[\\\/:\*\?"<>\|\.]', '', company_name) + "_Investment return.png"
        plt.tight_layout()
        plt.subplots_adjust(left = 0.1, right = 0.6)
        plt.savefig(file_name)
        plt.close()
        
        
        # Break point
        if(stop_flag.is_set()):
            return None
        
        
        
        # Save the financial statements as .csv
        result.to_csv(folder_name + "\\" + "Financial Statements.csv", encoding = "utf-8")
        
        update_msg("Financial statements and their visualization are saved successfully!" if IS_ENGLISH else "財報圖表已成功儲存完畢！")
        #print("plot_data的folder_name:", folder_name)
        return (folder_name, company_name)
        
        
    else:
        update_msg("Unknown industry type" if IS_ENGLISH else "未知的產業類別？")
        return None
    
# plot_data(result, industry_type, company_name)


# In[11]:


# !pip show matplotlib


# ## Main program execution
# Going to be wrapped in GUI.<br>
# Deprecated!

# In[8]:


# def main_exe(com_name):
# #     global target_stock
#     global msgs
#     global f
#     #target_stock = com_name
    
#     try:
#         # Clear "msgs" global variable after searching
#         msgs.clear()
        
        
#         #target_stock = input("Please enter stock name: ")
#         reports, company_name = get_source(com_name)
#         #print("Step 1 completed!")

        
# #         target_stock = ""
        

#         # Check industry type
#         industry_type = check_industry_type(reports[0][0])
#         #print(industry_type)

#         # Extract data and build dataframe
#         result = extract_from_reports(reports, industry_type, company_name)
#         #display(result)

#         # Extract data and visualize them. Fianlly save them as .png and .csv under a folder named by the search date and the company's name
#         plot_data(result, industry_type, company_name)

#     except Exception as e:
#         #print("Stop the program ...")
#         #update_msg("Stop the program ...")
#         update_msg(str(e))

#     finally:
#         #print("Program finished!")
#         #update_msg("Program finished!")
#         f.close()


# # APP's GUI
# Three basic frames: Login / Search / Result

# ## Encrypt and decrypt functions

# In[8]:


# Encrypting info file
def enc_file():
    fer = Fernet(b'jT3mTLKEvPFcaVx4bP_EKWMvnWxTga2G96x-03k8-ew=')  # Used to encryt / decrypt file
    
    
    with open("info.json", "rb") as raw_file:
        #raw_file = open("test.json", "r+", encoding = "utf-8-sig")
        file_data = raw_file.read()
        
        
        enc_data = fer.encrypt(file_data)
        
    with open("info.json", "wb") as raw_file:
        raw_file.write(enc_data)
        
        
        
# Decrypting info file
def dec_file_to_json():
    fer = Fernet(b'jT3mTLKEvPFcaVx4bP_EKWMvnWxTga2G96x-03k8-ew=')  # Used to encryt / decrypt file
    
    
    with open("info.json", "rb") as raw_file:
        file_data = raw_file.read()
        
        dec_data = fer.decrypt(file_data)
        dec_data_str = dec_data.decode('utf-8-sig')
        #print(dec_data_str)
        
        dec_data_json = json.loads(dec_data_str)
        
        return dec_data_json
    
    
    
    
def update_content(*args):
    account, pwd = args
    
    fer = Fernet(b'jT3mTLKEvPFcaVx4bP_EKWMvnWxTga2G96x-03k8-ew=')  # Used to encryt / decrypt file
    
    
    #enc_data = fer.encrypt(args[0])
    with open("info.json", "rb") as raw_file:
        #raw_file = open("test.json", "r+", encoding = "utf-8-sig")
        file_data = raw_file.read()
        #print(type(file_data))  # bytes
        
        dec_data = fer.decrypt(file_data)
        dec_data_json = json.loads(dec_data)
        #print(type(dec_data_json))  # dict
        dec_data_json[account] = {"pwd" : pwd}  #["pwd"] = pwd
        
        dec_data_str = json.dumps(dec_data_json)
        dec_data_bytes = bytes(dec_data_str, "utf-8-sig")
        
        enc_data = fer.encrypt(dec_data_bytes)
        
    
    
    with open("info.json", "wb") as raw_file:
        raw_file.write(enc_data)


# ## Basic window settings

# In[9]:


print("Initializing settings for GUI ...")

# Data of login
#f = open("info.json", "r+", encoding = "utf-8-sig")
login_data = dec_file_to_json()  #json.loads(f.read())
login_time = 3
btn_pressed_res = 0  # Determint which button in result frame is pressed. 0: None of them.
                

                
root = tk.Tk()
root.title("米美股分析 ME American Stock Analysis")
root.geometry("800x600")  # width / height
root.resizable(False, False)
root.config(bg = "#F5F4F2")
#root.tk.call('wm', 'iconphoto', root._w, tk.PhotoImage(file = "elephant_no_bg.png"))
root.iconbitmap("ME_no_bg_96.ico")





# Bar image label
bar_img = Image.open("ME_bar.png")
# tech_img.putalpha(200)
# open_img_resize = open_img.resize((30, 30))
bar_img_tk = ImageTk.PhotoImage(bar_img)
# lbl_bg = tk.Label(root, image = tech_img_resize_tk)
# lbl_bg.place(x = 0, y = 0)
bar_img.close()
lbl_bar = tk.Label(root, image = bar_img_tk, padx = 0, pady = 0)
lbl_bar.place(x = 0, y = 0)


# Login / Setting / Register pages' image
# glass_of_water_img = Image.open("a_glass_of_water.jpg")
# glass_of_water_img_resize = glass_of_water_img.resize((800, 600))
# glass_of_water_img_resize_tk = ImageTk.PhotoImage(glass_of_water_img_resize)
# lbl_bg = tk.Label(root, image = glass_of_water_img_resize_tk)
# lbl_bg.place(x = 0, y = 0)



# In[250]:


# update_content("TEST", "666")
# myjson = dec_file_to_json()
# myjson["TEST"]


# In[258]:


# f.close()


# ## Login frame
# Including elements and functions

# In[10]:


# Login frame
frame_login = tk.Frame(root, relief = "flat", bd = 2, padx = 25, pady = 20, bg = "#F5F4F2")
frame_login.place(x = 200, y = 200, width = 400, height = 400)

# Login elements
lbl_user = tk.Label(frame_login, bg = "#F5F4F2", text = "User", font = ("Arial", 14, "bold"), anchor = "center", padx = 5, pady = 10)
lbl_user.grid(row = 0, column = 0, sticky = "NSEW")

ety_user = tk.Entry(frame_login, font = ("Arial", 14, "bold"), width = 10)
ety_user.grid(row = 0, column = 2, columnspan = 3, sticky = "nsew")
ety_user.focus_set()

lbl_pwd = tk.Label(frame_login, bg = "#F5F4F2", text = "Password", font = ("Arial", 14, "bold"), anchor = "center", padx = 5, pady = 10)
lbl_pwd.grid(row = 2, column = 0, sticky = "NSEW")


ety_pwd = tk.Entry(frame_login, font = ("Arial", 14), width = 10, show = "*")
ety_pwd.grid(row = 2, column = 2, columnspan = 3, sticky = "nsew")

lbl_msg = tk.Label(frame_login, font = ("Arial", 12), bg = "#F5F4F2", justify = "left", fg = "red", anchor = "sw", padx = 5, pady = 10, height = 4)
lbl_msg.grid(row = 8, column = 0, columnspan = 5, sticky = "wes")






# Functions for login frame's buttons

def goto_search():
    lbl_msg.config(text = "")
    ety_user.delete(0, "end")
    ety_pwd.delete(0, "end")
    frame_search.place(x = 0, y = 0, width = 800, height = 600)
    frame_login.place_forget()
    
    
def close_gui():
    root.destroy()
    

IS_ENGLISH = True
def change_lang():
    global IS_ENGLISH
    IS_ENGLISH = not IS_ENGLISH
    
    if IS_ENGLISH:
        btn_change_lang.config(text = "English", font = ("Arial", 14, "bold"))
        btn_login.config(text = "Login", font = ("Arial", 14, "bold"))
        lbl_user.config(text = "User", font = ("Arial", 14, "bold"))
        lbl_pwd.config(text = "Password", font = ("Arial", 14, "bold"))
        btn_setting.config(text = "Setting", font = ("Arial", 14, "bold"))
        btn_register.config(text = "Register", font = ("Arial", 14, "bold"))
        frame_login.place(x = 200, y = 200, width = 400, height = 400)
        
        
        lbl_user_reg.config(text = "User", font = ("Arial", 14, "bold"))
        lbl_pwd_reg.config(text = "Password", font = ("Arial", 14, "bold"))
        lbl_pwd_reg2.config(text = "Password again", font = ("Arial", 11, "bold"))
        btn_cancel_reg.config(text = "Cancel", font = ("Arial", 14, "bold"))
        btn_ok_reg.config(text = "Submit", font = ("Arial", 14, "bold"))
        
        
        
        lbl_user_set.config(text = "User", font = ("Arial", 14, "bold"))
        lbl_pwd_old_set.config(text = "Old password", font = ("Arial", 11, "bold"))
        lbl_pwd_new_set.config(text = "New password", font = ("Arial", 11, "bold"))
        btn_cancel_set.config(text = "Cancel", font = ("Arial", 14, "bold"))
        btn_ok_set.config(text = "Submit", font = ("Arial", 14, "bold"))
        
        
        btn_logout.config(text = "Logout", font = ("Arial", 12, "bold"))
        btn_goto_result.config(text = "Goto result", font = ("Arial", 12, "bold"))
        btn_goto_result.place(x = 660, y = 530)
        btn_search.config(text = "Search", font = ("Arial", 14, "normal"))
        lbl_quarter.config(text = "Quarter(s)", font = ("Arial", 14, "normal"))
        lbl_quarter.place(x = 440, y = 250, height = 50)
        
        
        
        lbl_com_name.config(text = "Target stock", font = ("Arial", 14, "bold"))
        btn_cashflow.config(text = "Cash flows", font = ("Arial", 12, "normal"), width = 16)
        btn_cashflow.place(x = 610, y = 180)
        btn_operation.config(text = "Operating\ncircumstances", font = ("Arial", 12, "normal"), width = 16)
        btn_operation.place(x = 610, y = 230)
        btn_balance.config(text = "Liabilities and\nStockholder's equity", font = ("Arial", 12, "normal"), width = 16)        
        btn_competitativeness.config(text = "Competitativeness", font = ("Arial", 12, "normal"), width = 16)
        btn_competitativeness.place(x = 610, y = 300)
        btn_investment.config(text = "Investment return", font = ("Arial", 12, "normal"), width = 16)
        btn_investment.place(x = 610, y = 350)
        btn_back_to_search.config(text = "Back to search", font = ("Arial", 10, "bold"))
        btn_back_to_search.place(x = 670, y = 10)
        
        
        
    else:
        btn_change_lang.config(text = "中文", font = ("新細明體", 16, "bold"))
        btn_login.config(text = "登入", font = ("新細明體", 16, "bold"))
        lbl_user.config(text = "帳號", font = ("新細明體", 16, "bold"))
        lbl_pwd.config(text = "密碼", font = ("新細明體", 16, "bold"))
        btn_setting.config(text = "設定", font = ("新細明體", 16, "bold"))
        btn_register.config(text = "註冊", font = ("新細明體", 16, "bold"))
        frame_login.place(x = 250, y = 200, width = 400, height = 400)
        
        lbl_user_reg.config(text = "帳號", font = ("新細明體", 16, "bold"))
        lbl_pwd_reg.config(text = "密碼", font = ("新細明體", 16, "bold"))
        lbl_pwd_reg2.config(text = "確認密碼", font = ("新細明體", 13, "bold"))
        btn_cancel_reg.config(text = "取消", font = ("新細明體", 16, "bold"))
        btn_ok_reg.config(text = "送出", font = ("新細明體", 16, "bold"))
        
        
        
        lbl_user_set.config(text = "帳號", font = ("新細明體", 16, "bold"))
        lbl_pwd_old_set.config(text = "舊密碼", font = ("新細明體", 13, "bold"))
        lbl_pwd_new_set.config(text = "新密碼", font = ("新細明體", 13, "bold"))
        btn_cancel_set.config(text = "取消", font = ("新細明體", 16, "bold"))
        btn_ok_set.config(text = "送出", font = ("新細明體", 16, "bold"))
        
        
        
        btn_logout.config(text = "登出", font = ("新細明體", 14, "bold"))
        btn_goto_result.config(text = "到結果頁", font = ("新細明體", 14, "bold"))
        btn_goto_result.place(x = 670, y = 530)
        btn_search.config(text = "搜尋", font = ("新細明體", 16, "normal"))
        lbl_quarter.config(text = "季數量", font = ("新細明體", 16, "normal"))
        lbl_quarter.place(x = 460, y = 250, height = 50)
    
    
        lbl_com_name.config(text = "公司名稱", font = ("新細明體", 16, "bold"))
        btn_cashflow.config(text = "現金流量", font = ("新細明體", 14, "normal"), width = 15)
        btn_cashflow.place(x = 610, y = 160)
        btn_operation.config(text = "營運狀況", font = ("新細明體", 14, "normal"), width = 15)
        btn_operation.place(x = 610, y = 210)
        btn_balance.config(text = "負債與股東權益", font = ("新細明體", 14, "normal"), width = 15)
        btn_competitativeness.config(text = "公司競爭力", font = ("新細明體", 14, "normal"), width = 15)
        btn_competitativeness.place(x = 610, y = 260)
        btn_investment.config(text = "投資回報", font = ("新細明體", 14, "normal"), width = 15)
        btn_investment.place(x = 610, y = 310)
        btn_back_to_search.config(text = "回搜尋頁", font = ("新細明體", 12, "bold"))
        btn_back_to_search.place(x = 690, y = 10)
        
    
    
def login(*args):
    global login_time
    global msgs
    global IS_ACTIVATE
    global login_data
    global IS_ENGLISH
    
    
    #login_data = dec_file_to_json()
    login_account = ety_user.get()
    
    if(login_account not in login_data):
        #print("No this account!")
        lbl_msg.config(text = "No this account." if IS_ENGLISH else "查無此帳號。", fg = "red")
        #print(login_account)
    else:
        pwd = ety_pwd.get()
        if(login_data[login_account]["pwd"] == pwd):
            #print("Login success!")
            lbl_msg.config(text = "Login success!" if IS_ENGLISH else "登入成功！", fg = "#15213A")
            #f.close()
            msgs.clear()
            IS_ACTIVATE = True
            login_time = 3
            root.after(1000, goto_search)
            
        else:
            if(login_time >0):
                #print("Login failed! Remain " + str(login_time - 1) + " chance(s).")
                lbl_msg.config(text = "Login failed! Remain " + str(login_time) + " chance(s)." if IS_ENGLISH else "登入失敗！剩下" + str(login_time) + "次機會。", fg = "red")
                login_time -= 1
            else:
                lbl_msg.config(text = "Login failed 3 times.\nProgram close automatically." if IS_ENGLISH else "登入失敗3次。自動關閉軟體﹍", fg = "red")
                #print("Login failed 3 times. Program close automatically.")
                #time.sleep(np.random.rand() + 1)  This will lock up the GUI. Use tkinter's after
                
                #f.close()
                root.after(1000, close_gui)
                #root.destroy()
                
                
        # Change basic settings
        ety_search_str.set("請輸入公司名稱或代碼" if not IS_ENGLISH else "Please enter a stock name")
        
    
    
def setting(*args):
    lbl_msg.config(text = "")
    ety_user.delete(0, "end")
    ety_pwd.delete(0, "end")
    
    if IS_ENGLISH:
        frame_setting.place(x = 200, y = 200, width = 400, height = 400)
    else:
        frame_setting.place(x = 200, y = 200, width = 400, height = 400)
    

def register(*args):
    lbl_msg.config(text = "")
    ety_user.delete(0, "end")
    ety_pwd.delete(0, "end")
    
    if IS_ENGLISH:
        frame_register.place(x = 200, y = 200, width = 400, height = 400)
    else:
        frame_register.place(x = 200, y = 200, width = 400, height = 400)

    
    
# Change language button
btn_change_lang = tk.Button(root, relief = "flat", fg = "white", bg = "#15213A", text = "English", width = 5, font = ("Arial", 14, "bold"), command = change_lang, anchor = "center", padx = 10, pady = 8)
btn_change_lang.place(x = 700, y = 10)


# Login button
btn_login = tk.Button(frame_login, bg = "#337AB7", fg = "white", text = "Login", font = ("Arial", 14, "bold"), command = login, anchor = "center", padx = 10, pady = 8)
btn_login.grid(row = 4, column = 0, sticky = "we")
btn_login.bind("<Return>", login)


# Setting button
btn_setting = tk.Button(frame_login, bg = "#0C616E", fg = "white", text = "Setting", font = ("Arial", 14, "bold"), command = setting, anchor = "center", padx = 10, pady = 8)
btn_setting.grid(row = 4, column = 2)
btn_setting.bind("<Return>", setting)


# Register button
btn_register = tk.Button(frame_login, bg = "#0C616E", fg = "white", text = "Register", font = ("Arial", 14, "bold"), command = register, anchor = "center", padx = 10, pady = 8)
btn_register.grid(row = 4, column = 4, sticky = "e")
btn_register.bind("<Return>", register)


# frame_login grid layout settings
#frame_login.grid_columnconfigure(0, minsize = 50)  
frame_login.grid_columnconfigure(1, minsize = 10)  # as a gap
frame_login.grid_columnconfigure(3, minsize = 10)  # as a gap
frame_login.grid_rowconfigure(1, minsize = 20)  # as a gap
frame_login.grid_rowconfigure(3, minsize = 30)  # as a gap
frame_login.grid_rowconfigure(5, minsize = 20)  # as a gap
frame_login.grid_rowconfigure(7, minsize = 60)  # as a gap





# ## Register frame
# Including elements and functions

# In[11]:


#Register frame
frame_register = tk.Frame(root, relief = "flat", bg = "#F5F4F2", bd = 2, padx = 20, pady = 20)
# frame_register.place(x = 200, y = 100, width = 400, height = 400)
frame_register.place_forget()


# Elements of register
lbl_user_reg = tk.Label(frame_register, bg = "#F5F4F2", text = "User", font = ("Arial", 14, "bold"), anchor = "center", padx = 5, pady = 10)
lbl_user_reg.grid(row = 0, column = 0, sticky = "NSEW")

ety_user_reg = tk.Entry(frame_register, font = ("Arial", 14, "bold"), width = 20)
ety_user_reg.grid(row = 0, column = 2, sticky = "nsew")


lbl_pwd_reg = tk.Label(frame_register, bg = "#F5F4F2", text = "Password", font = ("Arial", 14, "bold"), anchor = "center", padx = 5, pady = 10)
lbl_pwd_reg.grid(row = 2, column = 0, sticky = "NSEW")


ety_pwd_reg = tk.Entry(frame_register, font = ("Arial", 14), width = 20, show = "*")
ety_pwd_reg.grid(row = 2, column = 2, sticky = "nsew")


lbl_pwd_reg2 = tk.Label(frame_register, bg = "#F5F4F2", text = "Password again", font = ("Arial", 11, "bold"), anchor = "center", padx = 5, pady = 10)
lbl_pwd_reg2.grid(row = 4, column = 0, sticky = "NSEW")


ety_pwd_reg2 = tk.Entry(frame_register, font = ("Arial", 14), width = 20, show = "*")
ety_pwd_reg2.grid(row = 4, column = 2, sticky = "nsew")

lbl_msg_reg = tk.Label(frame_register, bg = "#F5F4F2", font = ("Arial", 12), fg = "red", anchor = "sw", padx = 5, pady = 5, height = 4)
lbl_msg_reg.grid(row = 8, column = 0, columnspan = 3, sticky = "wes")



def close_reg_frame():
    ety_user_reg.delete(0, "end")
    ety_pwd_reg.delete(0, "end")
    ety_pwd_reg2.delete(0, "end")
    lbl_msg_reg.config(text = "")
    frame_register.place_forget()
    

def cancel_reg(*args):
    ety_user_reg.delete(0, "end")
    ety_pwd_reg.delete(0, "end")
    ety_pwd_reg2.delete(0, "end")
    lbl_msg_reg.config(text = "")
    frame_register.place_forget()
    

def submit_reg(*args):    
    #global f
    global login_data
    
    
    # Write new account and pwd into info.json
    new_account = ety_user_reg.get()
    new_account_pwd = ety_pwd_reg.get()
    new_account_pwd2 = ety_pwd_reg2.get()
    
    if((not (new_account in login_data.keys()))):
        if(new_account == ""):
            lbl_msg_reg.config(text = "User is empty." if IS_ENGLISH else "帳號不可為空白。", fg = "red")
            
        elif(new_account != "" and new_account_pwd != "" and new_account_pwd == new_account_pwd2):
            #login_data[new_account] = {"pwd" : new_account_pwd}
            lbl_msg_reg.config(text = "Register successed!" if IS_ENGLISH else "帳號註冊成功！", fg = "#15213A")

            
            
            #f.seek(0)
            #json.dump(login_data, f)
            #f.close()
            update_content(new_account, new_account_pwd)

            # Reopen info.json with new information
            #f = open("info.json", "r+", encoding = "utf-8-sig")
            login_data = dec_file_to_json()  #json.loads(f.read())


            frame_register.after(1000, close_reg_frame)
            #time.sleep(np.random.rand() + 1)
            
        else:
            lbl_msg_reg.config(text = "Password not matched." if IS_ENGLISH else "密碼不符合。", fg = "red")
    
    else:
        lbl_msg_reg.config(text = "Account existed!" if IS_ENGLISH else "帳號已存在！", fg = "red")


# Cancel button
btn_cancel_reg = tk.Button(frame_register, fg = "white", bg = "#0C616E", text = "Cancel", font = ("Arial", 14, "bold"), command = cancel_reg, anchor = "center", padx = 10, pady = 8, width = 8)
btn_cancel_reg.grid(row = 6, column = 0, sticky = "w")
btn_cancel_reg.bind("<Return>", cancel_reg)



# OK button
btn_ok_reg = tk.Button(frame_register, fg = "white", bg = "#337AB7", text = "Submit", font = ("Arial", 14, "bold"), command = submit_reg, anchor = "center", padx = 10, pady = 8, width = 8)
btn_ok_reg.grid(row = 6, column = 2, sticky = "e")
btn_ok_reg.bind("<Return>", submit_reg)


# frame_register grid layout settings
# frame_register.grid_columnconfigure(0, minsize = 50)  
frame_register.grid_columnconfigure(1, minsize = 10)  # as a gap
#frame_register.grid_columnconfigure(2, minsize = 220)  # as a gap


frame_register.grid_columnconfigure(3, minsize = 10)  # as a gap
frame_register.grid_rowconfigure(1, minsize = 20)  # as a gap
frame_register.grid_rowconfigure(3, minsize = 20)  # as a gap
frame_register.grid_rowconfigure(5, minsize = 20)  # as a gap
frame_register.grid_rowconfigure(7, minsize = 40)  # as a gap



# ## Setting frame
# Including elements and functions

# In[12]:


# Setting frame
frame_setting = tk.Frame(root, relief = "flat", bg = "#F5F4F2", bd = 2, padx = 20, pady = 20)
frame_setting.place_forget()


# Elements of setting frame
lbl_user_set = tk.Label(frame_setting, bg = "#F5F4F2", text = "User", font = ("Arial", 14, "bold"), anchor = "center", padx = 5, pady = 10)
lbl_user_set.grid(row = 0, column = 0, sticky = "NSEW")

ety_user_set = tk.Entry(frame_setting, font = ("Arial", 14, "bold"), width = 20)
ety_user_set.grid(row = 0, column = 2, sticky = "nsew")


lbl_pwd_old_set = tk.Label(frame_setting, bg = "#F5F4F2", text = "Old password", font = ("Arial", 11, "bold"), anchor = "center", padx = 5, pady = 10)
lbl_pwd_old_set.grid(row = 2, column = 0, sticky = "NSEW")


ety_pwd_old_set = tk.Entry(frame_setting, font = ("Arial", 14), width = 20, show = "*")
ety_pwd_old_set.grid(row = 2, column = 2, sticky = "nsew")


lbl_pwd_new_set = tk.Label(frame_setting, bg = "#F5F4F2", text = "New password", font = ("Arial", 11, "bold"), anchor = "center", padx = 5, pady = 10)
lbl_pwd_new_set.grid(row = 4, column = 0, sticky = "NSEW")


ety_pwd_new_set = tk.Entry(frame_setting, font = ("Arial", 14), width = 20, show = "*")
ety_pwd_new_set.grid(row = 4, column = 2, sticky = "nsew")

lbl_msg_set = tk.Label(frame_setting, bg = "#F5F4F2", font = ("Arial", 12), fg = "red", anchor = "sw", padx = 5, pady = 5, height = 4)
lbl_msg_set.grid(row = 8, column = 0, columnspan = 3, sticky = "wes")


def close_set_frame():
    ety_user_set.delete(0, "end")
    ety_pwd_old_set.delete(0, "end")
    ety_pwd_new_set.delete(0, "end")
    lbl_msg_set.config(text = "")
    frame_setting.place_forget()
    
    
def cancel_set(*args):
    ety_user_set.delete(0, "end")
    ety_pwd_old_set.delete(0, "end")
    ety_pwd_new_set.delete(0, "end")
    lbl_msg_set.config(text = "")
    frame_setting.place_forget()
    


def submit_set(*args):
    #global f
    global login_data
    
    
     # Update account and pwd of info.json
    old_account = ety_user_set.get()
    account_old_pwd = ety_pwd_old_set.get()
    account_new_pwd = ety_pwd_new_set.get()
    
    
    if(old_account in login_data.keys()):
        if(account_old_pwd == login_data[old_account]["pwd"] and account_new_pwd != ""):
            #login_data[old_account]["pwd"] = account_new_pwd
            lbl_msg_set.config(text = "Updating password succeed!" if IS_ENGLISH else "密碼更新完成！", fg = "#15213A")
            
            #f.seek(0)
            #json.dump(login_data, f)
            #f.close()
            update_content(old_account, account_new_pwd)

            # Reopen info.json with new information
            #f = open("info.json", "r+", encoding = "utf-8-sig")
            login_data = dec_file_to_json()  #json.loads(f.read())


            frame_setting.after(1000, close_set_frame)
        
        else:
            lbl_msg_set.config(text = "Wrong password." if IS_ENGLISH else "密碼錯誤。", fg = "red")
        
    else:
        lbl_msg_set.config(text = "No this account." if IS_ENGLISH else "查無此帳號。", fg = "red")


# Cancel button
btn_cancel_set = tk.Button(frame_setting, fg = "white", text = "Cancel", bg = "#0C616E", font = ("Arial", 14, "bold"), command = cancel_set, anchor = "center", padx = 10, pady = 8, width = 8)
btn_cancel_set.grid(row = 6, column = 0, sticky = "w")
btn_cancel_set.bind("<Return>", cancel_set)

# OK button
btn_ok_set = tk.Button(frame_setting, fg = "white", bg = "#337AB7", text = "Submit", font = ("Arial", 14, "bold"), command = submit_set, anchor = "center", padx = 10, pady = 8, width = 8)
btn_ok_set.grid(row = 6, column = 2, sticky = "e")
btn_ok_set.bind("<Return>", submit_set)


# frame_setting grid layout settings
# frame_register.grid_columnconfigure(0, minsize = 50)  
frame_setting.grid_columnconfigure(1, minsize = 10)  # as a gap
#frame_register.grid_columnconfigure(2, minsize = 220)  # as a gap


frame_setting.grid_columnconfigure(3, minsize = 10)  # as a gap
frame_setting.grid_rowconfigure(1, minsize = 20)  # as a gap
frame_setting.grid_rowconfigure(3, minsize = 20)  # as a gap
frame_setting.grid_rowconfigure(5, minsize = 20)  # as a gap
frame_setting.grid_rowconfigure(7, minsize = 40)  # as a gap


# ## Search frame

# In[13]:


# Search frame
frame_search = tk.Frame(root, padx = 5, pady = 3, bg = "#F5F4F2")
frame_search.place_forget()

# Global thread object (allow only 1 searching thread in the same time)
m = None
folder_name = ""
company_name = ""
# stop = threading.Event()

def for_test(stop_flag):
    if not stop_flag.is_set():
        print("Why?")
        
# Functions and classes
class SearchThread(threading.Thread):
    def __init__(self, com_name, quarter_num):
        #super().__init__(target = target, args = args)
        super().__init__()
        self.stop_flag = threading.Event()
        self.com_name = com_name
        self.quarter_num = quarter_num
        #self.target = target
        #self.args = args
        
        
    def run(self):
        #self.target(self.args[0])
        global msgs
        global f
        global company_name
        global folder_name
        global btn_pressed_res
        global lbl_cur_com_name
        #target_stock = com_name

        # Python's try-except will not create a new function scope
        try:
            # Clear "msgs" global variable after searching
            msgs.clear()


            # print("Why?") -> No looping, why the below program loop itself?
            #for_test(self.stop_flag)
            
            
            #target_stock = input("Please enter stock name: ")
            #get_source(self.com_name, self.stop_flag):
            temp_source = get_source(self.com_name, self.quarter_num, self.stop_flag)
            
            if temp_source:
                reports, company_name = temp_source
                # Check industry type
                industry_type = check_industry_type(reports[0][0])
                #print(industry_type)

                # Extract data and build dataframe
                result = extract_from_reports(reports, industry_type, company_name, self.stop_flag)
                #display(result)

                # Extract data and visualize them. Fianlly save them as .png and .csv under a folder named by the search date and the company's name
                folder_name, company_name = plot_data(result, industry_type, company_name, self.stop_flag)

                # Display the result on GUI
                load_in(folder_name, company_name, "_Liabilities and Stockholder's equity.png", 1)
                #btn_pressed_res = 1
                
                # Update company name in result frame
                lbl_cur_com_name.config(text = company_name)
                
            else:
                pass
            #print("Step 1 completed!")


    #         target_stock = ""


            

        except Exception as e:
            #print("Stop the program ...")
            #update_msg("Stop the program ...")
            update_msg(str(e))

        finally:
            #print("Program finished!")
            #update_msg("Program finished!")
            #f.close()
            pass
        
        
    def stop(self):
        update_msg("Stop searching the current stock ..." if IS_ENGLISH else "停止搜尋當前公司財報 ...")
        self.stop_flag.set()
        #raise Exception("Stop searching the current stock ...")
        
        
        
        

def logout(*args):
    #global f
    global login_data
    global company_name
    global folder_name
    global lbl_display
    global lbl_cur_com_name
    global btn_pressed_res
    global msgs
    global contents
    global IS_ACTIVATE
    
    btns = [btn_balance, btn_cashflow, btn_operation, btn_competitativeness, btn_investment]
    
    # Reopen login info
    #f = open("info.json", "r+", encoding = "utf-8-sig")
    login_data = dec_file_to_json()  #json.loads(f.read())
    
    
    IS_ACTIVATE = False
    folder_name = ""
    company_name = ""
    IS_ACTIVATE = False
    lbl_display.image = None
    btn_pressed_res = 0
    lbl_cur_com_name.config(text = "")
    frame_search.place_forget()
    msgs.clear()
    contents.set(msgs)
    ety_user.focus_set()
    
    if IS_ENGLISH:
        frame_login.place(x = 200, y = 200, width = 400, height = 400)
    else:
        frame_login.place(x = 250, y = 200, width = 400, height = 400)
    
    
    # Change button's relief and font weight
    for idx, btn in enumerate(btns):
        if(idx + 1 == btn_pressed_res):
            if IS_ENGLISH:
                btns[idx].config(relief = "flat", font = ("Arial", 12, "bold"), width = 16, bg = "#15213A", fg = "white")
            else:
                btns[idx].config(relief = "flat", font = ("新細明體", 14, "bold"), width = 15, bg = "#15213A", fg = "white")
            #btn_pressed_res = args[-1]
        else:
            if IS_ENGLISH:
                btns[idx].config(relief = "raised", font = ("Arial", 12), width = 16, bg = "#F5F4F2", fg = "black")
            else:
                btns[idx].config(relief = "raised", font = ("新細明體", 14), width = 15, bg = "#F5F4F2", fg = "black")
            
            
    
def on_focus_out(ety_search):
    global IS_ENGLISH
#     ety_search.delete(0, "end")
#     ety_search.insert(0, "Please enter a stock name" if IS_ENGLISH else "請輸入公司名稱或代碼")
    ety_search_str.set("請輸入公司名稱或代碼" if not IS_ENGLISH else "Please enter a stock name")
    ety_search.config(fg = "gray")
    
    
def on_focus_in(ety_search):
    global IS_ENGLISH
    ety_search.delete(0, "end")
    ety_search.config(fg = "black")

    
def search(*args):
#     global target_stock
    global m
    global IS_ENGLISH
    
    
    com_name = ety_search.get()
    quarter_num = cb_quarter_num.get()
    #print(quarter_num)
    if(com_name != "Please enter a stock name" and com_name != "請輸入公司名稱或代碼" and com_name != ""):  
        
        if(m and m.is_alive()):
            lbl_msg_search.config(text = "Searching is in progress. Please wait ... " if IS_ENGLISH else "搜尋中。請燒等 ...")
        elif(expiration_date < datetime.now()):
            lbl_msg_search.config(text = "Searching function has expired!" if IS_ENGLISH else "搜尋功能已過期！")
            
        else:
            ety_search.delete(0, "end")
            lbl_msg_search.config(text = "")
            target_stock = com_name

            frame_result.place(x = 0, y = 0, width = 800, height = 600)
            lbl_cur_com_name.config(text = com_name)
            frame_search.place_forget()
            on_focus_out(ety_search)

            #get_source(com_name)
            #frame_search.after(1000, lambda  : main_exe(target_stock))
            #m = threading.Thread(target = main_exe, args = (target_stock,))
            m = SearchThread(com_name, quarter_num)
            m.start()
            #m.join()
    else:
        lbl_msg_search.config(text = "No company's name entered." if IS_ENGLISH else "未輸入公司名稱或代碼。")
    
    
def goto_result(*args):
    global IS_ENGLISH
#     ety_search.delete(0, "end")
#     ety_search.insert(0, "Please enter a stock name" if IS_ENGLISH else "請輸入公司名稱或代碼")
    ety_search_str.set("請輸入公司名稱或代碼" if not IS_ENGLISH else "Please enter a stock name")
    lbl_msg_search.config(text = "")
    frame_result.place(x = 0, y = 0, width = 800, height = 600)
    on_focus_out(ety_search)
    frame_search.place_forget()
    
    
    
# Elements 

# Bar image label
bar_img_ser = Image.open("ME_bar.png")
# tech_img.putalpha(200)
# open_img_resize = open_img.resize((30, 30))
bar_img_tk_ser = ImageTk.PhotoImage(bar_img_ser)
# lbl_bg = tk.Label(root, image = tech_img_resize_tk)
# lbl_bg.place(x = 0, y = 0)
bar_img_ser.close()
lbl_bar_ser = tk.Label(frame_search, image = bar_img_tk_ser, padx = 0, pady = 0)
lbl_bar_ser.place(x = 0, y = 0)


btn_logout = tk.Button(frame_search, fg = "white", bg = "#0C616E", text = "Logout", relief = "flat", anchor = "center", font = ("Arial", 12, "bold"), padx = 5, pady = 3, command = logout)
btn_logout.place(x = 20, y = 530)
btn_logout.bind("<Return>", logout)


btn_goto_result = tk.Button(frame_search, fg = "white", bg = "#337AB7", text = "Go to result", relief = "flat", anchor = "center", font = ("Arial", 12, "bold"), padx = 5, pady = 3, command = goto_result)
btn_goto_result.place(x = 660, y = 530)

lbl_msg_search = tk.Label(frame_search, bg = "#F5F4F2", font = ("Arial", 12), fg = "red", anchor = "w", padx = 5, pady = 5, height = 4)
lbl_msg_search.place(x = 130, y = 310, width = 400, height = 50)


ety_search_str = tk.StringVar()

ety_search = tk.Entry(frame_search, font = ("Arial", 14), bg = "white", textvariable = ety_search_str)
# ety_search_str.set("請輸入公司名稱或代碼" if not IS_ENGLISH else "Please enter a stock name")
# ety_search.delete(0, "end")

ety_search.config(fg = "gray")
ety_search.bind("<FocusIn>", lambda x : on_focus_in(ety_search))
#ety_search.bind("<FocusOut>", lambda x : on_focus_out(ety_search))
ety_search.place(x = 130, y = 250, width = 300, height = 50)
# if IS_ENGLISH:
#     ety_search.insert(0, "Please enter a stock name??")
# else:
#     print("Hi??")
#     ety_search.insert(0, "請輸入公司名稱或代碼")

btn_search = tk.Button(frame_search, text = "Search", anchor = "center", bg = "#FFC107", font = ("Arial", 14), padx = 10, pady = 5, command = search)
btn_search.place(x = 610, y = 250, width = 80, height = 50)
btn_search.bind("<Return>", search)



# Choose how many numbers of quarters to be obtained (1 ~ 8)
cb_quarter_num = ttk.Combobox(frame_search, width = 3, values = [1,2,3,4,5,6,7,8], font = ("Arial", 14), state = "readonly")
cb_quarter_num.current(7)
cb_quarter_num.place(x = 550, y = 250, width = 50, height = 50)

lbl_quarter = tk.Label(frame_search, text = "Quarter(s)", bg = "#F5F4F2", font = ("Arial", 14, "normal"), anchor = "center", padx = 5, pady = 3)
lbl_quarter.place(x = 440, y = 250, height = 50)



# ## Load-in file to display function

# In[14]:


def load_in(*args):
    global lbl_display
    global btn_pressed_res
    global btn_balance  # 1
    global btn_cashflow  # 2
    global btn_operation   # 3
    global btn_competitativeness  # 4
    global btn_investment  # 5
    
    btns = [btn_balance, btn_cashflow, btn_operation, btn_competitativeness, btn_investment]
    
    
    try:
        file = ""
        
        
        
        # Get file path
        if(len(args) == 2):
            file = args[0]
            
        elif(len(args) == 4):
            
            # Unpack parameters
            folder_name, company_name, which, btn_pressed_res = args
#             print("folder name:", folder_name)
#             print("company name:", company_name)
#             print("which:", which)
#             print("btn_pressed_res:", btn_pressed_res)
            
            current_date = re.search("\d{4}-\d{2}-\d{2}", folder_name).group(0)


            #current_date = current_date_match.group(0)
            if not re.match(r"results", folder_name):
                folder_name = r"results\\" + folder_name
#                 print("自己加results:", folder_name)
            else:
#                 print("自帶results:", folder_name)
                pass
            
        
        
            file = folder_name + "\\" + str(current_date) + re.sub(r'[\\\/:\*\?"<>\|\.]', '', company_name) + which
#             print(file)
            

        #     if num == 1:
        #         #print("Type 1")
        else:
            pass
        
        
        # Open image file
        with Image.open(file) as f:
#             print("成功開啟")
            f_resize = f.resize((550, 420))
            f_resize_tk = ImageTk.PhotoImage(f_resize)
            lbl_display.configure(image = f_resize_tk)
            lbl_display.image = f_resize_tk
            
            
            # Change button's relief and font weight
            for idx, btn in enumerate(btns):
                if(idx + 1 == args[-1]):
                    if IS_ENGLISH:
                        btns[idx].config(relief = "flat", font = ("Arial", 12, "bold"), width = 16, bg = "#15213A", fg = "white")
                    else:
                        btns[idx].config(relief = "flat", font = ("新細明體", 14, "bold"), width = 15, bg = "#15213A", fg = "white")
                    #btn_pressed_res = args[-1]
                else:
                    if IS_ENGLISH:
                        btns[idx].config(relief = "raised", font = ("Arial", 12), width = 16, bg = "#F5F4F2", fg = "black")
                    else:
                        btns[idx].config(relief = "raised", font = ("新細明體", 14), width = 15, bg = "#F5F4F2", fg = "black")
                
            
    except Exception as e:
        pass
        
        
# Temporary not used
def load_in_data(*args):
    if(len(args) == 2):
        pass
    else:
        update_msg("Wrong load-in format." if IS_ENGLISH else "錯誤的資料夾名稱格式。")


# ## Result frame

# In[18]:


# Search frame
frame_result = tk.Frame(root, padx = 5, pady = 3, bg = "#F5F4F2")
frame_result.place_forget()




# Elements
lbl_com_name = tk.Label(frame_result, text = "Target stock", font = ("Arial", 14, "bold"), anchor = "center", padx = 5, pady = 3)
lbl_com_name.place(x = 20, y = 10, height = 50)

lbl_cur_com_name = tk.Label(frame_result, font = ("Arial", 14), anchor = "w", padx = 10, pady = 3, fg = "blue")
lbl_cur_com_name.place(x = 170, y = 10, height = 50)


lbl_display = tk.Label(frame_result, anchor = "center", padx = 5, pady = 3, bg = "white", relief = "sunken")
lbl_display.place(x = 20, y = 60, height = 450, width = 580)


frame_msg = tk.Frame(frame_result, padx = 1, pady = 3, bg = "white")
frame_msg.place(x = 20, y = 520, height = 70, width = 755)


scrollbar = tk.Scrollbar(frame_msg)
scrollbar.pack(side = "right", fill = "y")


contents = tk.StringVar()  # Need to be created after root is built!
# msgs = ["msg1","msg2","msg3","msg4","msg5"]
# msgs = []  # Defined in global variables

# lbl_fr1 = tk.Label(text = "Apple")
# lbl_fr2 = tk.Label(text = "Banana")
# lbl_fruits = [lbl_fr1, lbl_fr2]
# contents.set(msgs)  #無法在listbox中加label



listbox = tk.Listbox(frame_msg, listvariable = contents, height = 65, width = 700, font = ("Arial", 14), yscrollcommand = scrollbar.set)
listbox.pack(side = "left", fill = "y")

scrollbar.config(command = listbox.yview)



#btn_financial_statement = tk.Button(frame_result, text = "Financial statements", command = lambda :load_in_data(folder_name, company_name), font = ("Arial", 12), padx = 10, pady = 5, anchor = "w", width = 16)
#btn_financial_statement.place(x = 610, y = 60)


    
btn_balance = tk.Button(frame_result, text = "Liabilities and\nStockholder's equity", command = lambda :load_in(folder_name, company_name, "_Liabilities and Stockholder's equity.png", 1),font = ("Arial", 12), padx = 10, pady = 5, width = 16, anchor = "w", justify = "left")
btn_balance.place(x = 610, y = 110)


btn_cashflow = tk.Button(frame_result, text = "Cash flows", command = lambda :load_in(folder_name, company_name, "_Cash flows.png", 2), font = ("Arial", 12), padx = 10, pady = 5, width = 16, anchor = "w", justify = "left")
btn_cashflow.place(x = 610, y = 180)


btn_operation = tk.Button(frame_result, text = "Operating\ncircumstances", command = lambda :load_in(folder_name, company_name, "_Operating circumstances.png", 3), font = ("Arial", 12), padx = 10, pady = 5, width = 16, anchor = "w", justify = "left")
btn_operation.place(x = 610, y = 230)

btn_competitativeness = tk.Button(frame_result, text = "Competitativeness", command = lambda :load_in(folder_name, company_name, "_Competitativeness.png", 4), font = ("Arial", 12), padx = 10, pady = 5, width = 16, anchor = "w", justify = "left")
btn_competitativeness.place(x = 610, y = 300)

btn_investment = tk.Button(frame_result, text = "Investment return", command = lambda :load_in(folder_name, company_name, "_Investment return.png", 5), font = ("Arial", 12), padx = 10, pady = 5, width = 16, anchor = "w", justify = "left")
btn_investment.place(x = 610, y = 350)


# # Back-to-search button
# back_img = Image.open("back.png")
# # tech_img.putalpha(200)
# back_img_resize = back_img.resize((30, 30))
# back_img_resize_tk = ImageTk.PhotoImage(back_img_resize)
# # lbl_bg = tk.Label(root, image = tech_img_resize_tk)
# # lbl_bg.place(x = 0, y = 0)
# back_img.close()
# btn_back_res = tk.Button(frame_result, image = back_img_resize_tk, padx = 5, pady = 5)
# btn_back_res.place(x = 610, y = 470)


def backto_search(*args):
    global ety_search
    
    frame_search.place(x = 0, y = 0, width = 800, height = 600)
    frame_result.place_forget()
    on_focus_out(ety_search)
    frame_search.focus_set()

    
def stop_search(*args):
    #raise Exception("Stop searching the stock's financial statements.")
    global m
    global folder_name
    global company_name
    
    if m:
        m.stop()
        folder_name = ""
        company_name = ""
        m = None
    else:
        pass


def open_file(*args):
    #file_path = tk.filedialog.askopenfilename(initialdir = os.getcwd(), filetype = (("png files","*.png"),))
    global lbl_cur_com_name
    global folder_name
    global company_name
    
    
    try:
        file_path = filedialog.askdirectory(initialdir = os.getcwd() + "\\results")  # initialdir = os.getcwd()
        #file_path = tk.filedialog.Directory(initialdir = os.getcwd())
        if not file_path:
            pass
        else:
            #print(file_path)
            folder_name = re.search(r"\d{4}-\d{2}-\d{2}.*$", file_path).group(0)
            company_name = re.search(r"\d{4}-\d{2}-\d{2}(.*)$", file_path).group(1)
            #print(folder_name)
            #print(company_name)
            
            
            load_in(file_path + "\\" + folder_name + "_Liabilities and Stockholder's equity.png", 1)
            
            lbl_cur_com_name.config(text = company_name)
    
    except Exception as e:
        update_msg("Can not open this folder." if IS_ENGLISH else "無法開啟此資料夾。")


def logout_res(*args):
    #global f
    global login_data
    global msgs
    global m
    global login_time
    global contents
    global IS_ACTIVATE
    global lbl_display
    global company_name
    global folder_name
    global btn_pressed_res
    
    
    btns = [btn_balance, btn_cashflow, btn_operation, btn_competitativeness, btn_investment]
    
    # Reopen login info
    #f = open("info.json", "r+", encoding = "utf-8-sig")
    login_data = dec_file_to_json()  #json.loads(f.read())
    
    
    frame_search.place_forget()
    frame_result.place_forget()
    
    if m:
        m.stop()
        #m.join()  # Wait the thread to end -> will crash?  Thread was stopped, can not wait until it's ended!
        
        m = None
    else:
        pass
    
    
    IS_ACTIVATE = False
    msgs.clear()
    contents.set(msgs)
    lbl_cur_com_name.config(text = "")
    login_time = 3
    company_name = ""
    folder_name = ""
    btn_pressed_res = 0
    
    #lbl_display.config(bg = "white")
    lbl_display.image = None
    ety_user.focus_set()
    #lbl_display.config(image = None, bg = "white")
    
    # Change button's relief and font weight
    for idx, btn in enumerate(btns):
        if(idx + 1 == btn_pressed_res):
            if IS_ENGLISH:
                btns[idx].config(relief = "flat", font = ("Arial", 12, "bold"), width = 16, bg = "#15213A", fg = "white")
            else:
                btns[idx].config(relief = "flat", font = ("新細明體", 14, "bold"), width = 15, bg = "#15213A", fg = "white")
            #btn_pressed_res = args[-1]
        else:
            if IS_ENGLISH:
                btns[idx].config(relief = "raised", font = ("Arial", 12), width = 16, bg = "#F5F4F2", fg = "black")
            else:
                btns[idx].config(relief = "raised", font = ("新細明體", 14), width = 15, bg = "#F5F4F2", fg = "black")
            
            
    if IS_ENGLISH:
        frame_login.place(x = 200, y = 200, width = 400, height = 400)
    else:
        frame_login.place(x = 250, y = 200, width = 400, height = 400)
    
    


# Back to search button
btn_back_to_search = tk.Button(frame_result, bg = "#0C616E", fg = "white", text = "Back to search", relief = "flat", anchor = "center", font = ("Arial", 10, "bold"), padx = 5, pady = 3, command = backto_search)
btn_back_to_search.place(x = 670, y = 10)
btn_back_to_search.bind("<Return>", backto_search)


# Stop button
stop_img = Image.open("stop.png")
# tech_img.putalpha(200)
stop_img_resize = stop_img.resize((30, 30))
stop_img_resize_tk = ImageTk.PhotoImage(stop_img_resize)
# lbl_bg = tk.Label(root, image = tech_img_resize_tk)
# lbl_bg.place(x = 0, y = 0)
stop_img.close()
btn_stop_res = tk.Button(frame_result, image = stop_img_resize_tk, padx = 5, pady = 5, command = stop_search)
btn_stop_res.place(x = 610, y = 470)
btn_stop_res.bind("<Return>", stop_search)



# Open button
open_img = Image.open("open.png")
# tech_img.putalpha(200)
open_img_resize = open_img.resize((30, 30))
open_img_resize_tk = ImageTk.PhotoImage(open_img_resize)
# lbl_bg = tk.Label(root, image = tech_img_resize_tk)
# lbl_bg.place(x = 0, y = 0)
open_img.close()
btn_open_res = tk.Button(frame_result, image = open_img_resize_tk, padx = 5, pady = 5, command = open_file)
btn_open_res.place(x = 660, y = 470)
btn_open_res.bind("<Return>", open_file)


# Logout button
logout_img = Image.open("logout.png")
# tech_img.putalpha(200)
logout_img_resize = logout_img.resize((30, 30))
logout_img_resize_tk = ImageTk.PhotoImage(logout_img_resize)
# lbl_bg = tk.Label(root, image = tech_img_resize_tk)
# lbl_bg.place(x = 0, y = 0)
logout_img.close()
btn_logout_res = tk.Button(frame_result, image = logout_img_resize_tk, padx = 5, pady = 5, command = logout_res)
btn_logout_res.place(x = 710, y = 470)
btn_logout_res.bind("<Return>", logout_res)



# Execute main function -> Will execute before GUI is created!
# main_exe(target_stock)


# ## Run GUI

# In[17]:

print("Start executing ...")

root.mainloop()


# ## Convert to .py file

# In[19]:


#get_ipython().system('jupyter nbconvert American_Stock_Analysis_For_Sale.ipynb --to python')








# ## Convert to .py file

# In[ ]:


# get_ipython().system('jupyter nbconvert American_Stock_Analysis_For_Sale.ipynb --to python')


# In[87]:


# import matplotlib
# print(matplotlib.__file__)


# In[88]:


# import matplotlib.font_manager
 
# a = sorted([f.name for f in matplotlib.font_manager.fontManager.ttflist])
 
# for i in a:
#     print(i)


# In[3]:


# # 查看tkinter的font
# from tkinter import *
# from tkinter import font

# root = Tk()
# # root.title('Font Families')
# fonts=list(font.families())
# # fonts.sort()
# fonts_sort = sorted(fonts)
# print(fonts_sort)


# In[ ]:




