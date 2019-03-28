import os
import pandas as pd

path = r'G:\Evaluation Group\National Transit Database\2018 NTD\Pre-populated Excel Files'

os_lists = os.listdir(r'G:\Evaluation Group\National Transit Database\2018 NTD\Pre-populated Excel Files')
for folder in os_lists:
    folder_list = os.listdir(r'G:\Evaluation Group\National Transit Database\2018 NTD\Pre-populated Excel Files' +'\\' +folder)
    folder_path = r'G:\Evaluation Group\National Transit Database\2018 NTD\Pre-populated Excel Files' +'\\' +folder
    for file in folder_list:
        if 'A-15' in file:
            os.rename(folder_path+'\\' +file, folder_path+'\\' +'A-15 Facilities.xlsx')
        elif 'A-90' in file:
            os.rename(folder_path+'\\' +file, folder_path+'\\' +'A-90 Transit Asset Management Performance Targets.xlsx')
        elif 'A-35' in file:
            os.rename(folder_path+'\\' +file, folder_path+'\\' +'A-35 Equipment.xlsx')
