# !/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import argparse
from pathlib import Path
import pandas as pd

from utils.tool import tqdm_bar

work_dir = Path.cwd()
main_dir = work_dir.parents[0]
root_dir = work_dir.parents[1]
csv_dir = os.path.join(root_dir, 'dcm_output_2', 'pattern_feature')

csv_file = os.path.join(main_dir,'feature_output.csv')
csv_df = pd.read_csv(csv_file,sep=',') 

def find_csv():
    csvs = [os.path.join(csv_dir, csv) for csv in os.listdir(csv_dir) if csv.endswith('.csv')]

    def combine(row):
        if len(str(row['ID']))==1:
            return '{}_{}_ID[00{}]_s[{}]_x[{}]_y[{}]'.format(row[0][0].upper(), *list(row[1:6]))    
        elif len(str(row['ID']))==2:
            return '{}_{}_ID[0{}]_s[{}]_x[{}]_y[{}]'.format(row[0][0].upper(), *list(row[1:6]))
        elif len(str(row['ID']))==3:
            return '{}_{}_ID[{}]_s[{}]_x[{}]_y[{}]'.format(row[0][0].upper(), *list(row[1:6]))
    
    imgs = []
    for index, row in csv_df.iterrows():
        imgs.append(combine(row))
     
    csvs = [csv for csv in csvs if Path(csv).stem not in imgs] 
    return csvs

def write_data(csv_path):
    csv_df = pd.read_csv(csv_file,sep=',') 

    features_df = pd.read_csv(csv_path,sep=',')
    df_all = pd.concat([csv_df, features_df], axis = 0, ignore_index = True)
    df_new = df_all.drop_duplicates(subset=['Class', 'Patient Name', 'ID', 'Section', 'Offset_X', 'Offset_Y'])
    df_new_sort = df_new.sort_values(by=['Class', 'Patient Name', 'ID', 'Section', 'Offset_X', 'Offset_Y'], ignore_index=True)
    df_new_sort.to_csv(csv_file, sep=',', index=0)   

def run():
    csvs = find_csv()
    for csv_path in tqdm_bar(csvs, 'Procrssing CSV Data'): 
        write_data(csv_path)       
    
if __name__ == '__main__':
    run()