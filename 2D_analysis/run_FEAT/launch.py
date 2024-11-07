# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# ======

import os
import re
import argparse
from pathlib import Path
from itertools import chain
import pandas as pd

from modules.resize import resize
from modules.calculation import porosity, line_angle, line, pore

work_dir = Path.cwd()
main_dir = work_dir.parents[0]
root_dir = work_dir.parents[2]
output_dir = os.path.join(root_dir, 'dcm_output_2', 'pattern_feature')

def get_log():
    log_dir = os.path.join(main_dir, 'pattern_log')       
    record_lists = [os.path.join(log_dir, file) for file in os.listdir(log_dir) if file.endswith('.txt')]
    
    if len(record_lists)==0:
        record_imgs = []
    else:
        record_imgs = []
        for record in record_lists:
            with open(record, "r") as file:
                lines = file.read().split('\n')
                lines.pop()
                record_imgs.append(lines)
                
        record_imgs = list(chain(*record_imgs))   
        record_imgs = sorted(record_imgs)              
    return record_imgs

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', dest='img_path', metavar='image path', type=str, 
                        default='./resize.png', help='absolute or relative path of image file')    
    args = parser.parse_args()
    return args

def save_data(record_imgs, args):    
    img_path = args.img_path            
    img_name = Path(img_path).stem
    csv_file = ''.join([os.path.join(output_dir,img_name), '.csv'])
    if os.path.isfile(csv_file):
        print('Data csv file exist : {}'.format(img_name))
    elif ''.join([img_name, '.png']) in record_imgs:
        print('Data in log file : {}'.format(img_name))
    else:
        print('Processing for : {}'.format(img_name))
        class_species = {'A':'Aves','M':'Mammala'} 
        regex = re.compile(r'(\w)_(.+)_ID\[(.+)\]_s\[(.+)\]_x\[(.+)\]_y\[(.+)\]')
        match = regex.search(img_name)
        features = {
            'Class':[class_species[match.group(1)]], 
            'Patient Name':[match.group(2)], 
            'ID':[match.group(3)],
            'Section':[match.group(4)], 
            'Offset_X':[match.group(5)], 
            'Offset_Y':[match.group(6)]}     
           
        resize_img = resize(img_path)
        features['Porosity'] = [porosity(resize_img)]
        features['Ave Bone Angle'], features['Std Bone Angle'] = line_angle(resize_img)
        features = {**features, **line(resize_img), **pore(resize_img)}   

        features_df = pd.DataFrame(features)
        save_path = os.path.join(output_dir, '{}.csv'.format(img_name))
        features_df.to_csv(save_path, sep=',', index=0)    

def run():
    record_imgs = get_log()
    args = parse_args()
    save_data(record_imgs, args)

if __name__ == '__main__':
    run()