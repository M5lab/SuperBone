# !/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import argparse
from pathlib import Path
from IPython.display import display
import numpy as np
import pandas as pd
from random import sample
import shutil
from itertools import chain
from datetime import date

from utils.tool import colorstr, print_args, tqdm_bar
  
work_dir = Path.cwd()
main_dir = work_dir.parents[0]
root_dir = work_dir.parents[1]
output_dir = os.path.join(main_dir, 'img_src')

IMG_FORMATS = ['.bmp', '.dng', '.jpeg', '.jpg', '.mpo', '.png', '.tif', '.tiff', '.webp', '.pfm']

def img_src_dir():
    dir_src_path = os.path.join(root_dir, 'img_src_all')
    return dir_src_path

def parse_args():
    parser = argparse.ArgumentParser()
    action1 = parser.add_argument('-f', dest='file_num', metavar='number of files', type=int, 
                                  default=100, help='number of files to choose')
    action2 = parser.add_argument('-d', dest='dir_num', metavar='number of directories', type=int, 
                                  default=5, help='number of directories to choose')  
    action3 = parser.add_argument('-aly', dest='aly_type', metavar='type of feature', type=str, 
                                  default='pattern', help='type of feature to analyze (pattern or mechanical)')
    action4 = parser.add_argument('-src', dest='dir_src_path', metavar='the directory where stores all images', type=str, 
                                  default='{}'.format(img_src_dir()), help='the directory where stores all images. default is img_src_all')  
    action5 = parser.add_argument('-l', dest='output_list', metavar='the list recorded the images name', type=str, 
                                  default=None, help='a txt file contains all output recorded')      
    action6 = parser.add_argument('-y', dest='refer', metavar='refer the list or not', type=bool, 
                                  default=False, help='refer the list recorded the images name or not')                                   
    args = parser.parse_args()
    metavars = [action1.metavar, action2.metavar, action3.metavar, action4.metavar, action5.metavar, action6.metavar]
    s = ''.join('{} : {}\n'.format(m, colorstr('bold', str(v))) for m, v in zip(metavars, vars(args).values()))
    print(colorstr('bright_green', 'All Argments :'))
    print_args(s)
    return args
    
def csv(args): 
    csv_dir = os.path.join(root_dir,'dcm_output','{}_feature'.format(args.aly_type))
    return csv_dir

  
def find_split_dirs(args):
    split_dirs = [os.path.join(output_dir, dir) for dir in os.listdir(output_dir) if dir.startswith(args.aly_type)]
    dir_index = [int(str(dir).split('_')[-1]) for dir in split_dirs] if len(split_dirs)>0 else [0]
    img_in_split_dirs = []
    for split_dir in split_dirs:
        img_in_split_dirs.append([file for file in os.listdir(split_dir) if Path(file).suffix.lower() in IMG_FORMATS])
    img_in_split_dirs = list(chain(*img_in_split_dirs))
    return img_in_split_dirs, dir_index


if __name__ == '__main__': 
    args = parse_args()
    
    img_in_split_dirs, dir_index = find_split_dirs(args)
    output_list_path = args.output_list
      
    dir_list = []
    max_dir_index = max(dir_index)
    for num in range(max_dir_index+1, max_dir_index+args.dir_num+1):
        output_path = os.path.join(output_dir,'{}_src_{}'.format(args.aly_type, num))
        dir_list.append(output_path)
        os.makedirs(output_path, exist_ok=True)
    
    if args.output_list is not None:
        with open(output_list_path, "r") as file:
            lines = file.read().split('\n')
        lines.pop()
        select_list_all = lines
              
    if not args.refer:
        name_list = []
        for file in os.listdir(args.dir_src_path):
            regex = re.compile(r'\w_(.+)_ID.+')
            name_list.append(regex.search(file).group(1))
        name_list = list(set(name_list))
        
        # len(name_list) should be 38
        file_num_div = int(args.file_num/(len(name_list)-1))
        # print(args.file_num, len(name_list)-1, file_num_div)
        
        selected_list_all = []
        for name in name_list:
            img_list = [img_path for img_path in tqdm_bar(os.listdir(args.dir_src_path), 'Procrssing {}'.format(name)) 
                        if re.search(r'(\w)_({})_+'.format(name), img_path)]
            img_list = [img_path for img_path in tqdm_bar(img_list, 'Procrssing {}'.format(name)) 
                        if (not os.path.isfile(os.path.join(csv(args), Path(img_path).stem)+'.csv')) 
                        and (img_path not in img_in_split_dirs)
                        and (img_path not in (select_list_all if args.output_list is not None else []))]
            try:
                if not len(img_list)<50:
                    select_list = sample(img_list, file_num_div)
                    selected_list_all.append(select_list)
            except ValueError:
                file_num_div_new = len(img_list)
                if not file_num_div_new<50:
                    select_list = sample(img_list, file_num_div_new)
                    selected_list_all.append(select_list)  
                
        selected_list_all = list(chain(*selected_list_all))   
        selected_list_all = sorted(selected_list_all)

        with open(os.path.join(work_dir, 'temp', '{}_output.txt'.format(date.today())),'w') as file:
            for name in selected_list_all:
                file.write(name+'\n')
    else:
        if len(select_list_all) % args.dir_num == 0:
            selected_list_all = select_list_all
           
    
    print("Final number of files : {}".format(len(selected_list_all))) 

    split_file = np.array_split(selected_list_all, args.dir_num) 

    for i, files in enumerate(split_file):
        print('Procrssing files for this directory : {}'.format(dir_list[i]))
        for img_path in tqdm_bar(files, 'Procrssing Files'):
            file_path = os.path.join(args.dir_src_path, str(img_path))
            copy_file_path = os.path.join(dir_list[i], str(img_path))
            shutil.copyfile(file_path, copy_file_path)
               

            
    
        
    
