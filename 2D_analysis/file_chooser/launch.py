# !/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import re
import argparse
from pathlib import Path
import numpy as np
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
    img_src_dir = os.path.join(root_dir, 'img_src_all')
    return img_src_dir
    
def get_log():
    log_dir = os.path.join(work_dir, 'log')
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
    return record_lists, record_imgs

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
    action5 = parser.add_argument('-y', dest='refer', metavar='refer the list or not', type=bool, 
                                  default=False, help='refer the list recorded the images name or not')                                   
    action6 = parser.add_argument('-l', dest='output_list', metavar='the list recorded the images name', type=str, 
                                  default=None, help='a txt file contains all output recorded')                                     
    args = parser.parse_args()
    metavars = [action1.metavar, action2.metavar, action3.metavar, action4.metavar, action5.metavar, action6.metavar]
    s = ''.join('{} : {}\n'.format(m, colorstr('bold', str(v))) for m, v in zip(metavars, vars(args).values()))
    print(colorstr('bright_green', 'All Argments :'))
    print_args(s)
    return args
    
def csv(args): 
    csv_dir = os.path.join(root_dir,'dcm_output','{}_feature'.format(args.aly_type))
    return csv_dir    
   
def split_files(record_imgs, args):
    name_list = []
    for file in os.listdir(args.dir_src_path):
        regex = re.compile(r'\w_(.+)_ID.+')
        name_list.append(regex.search(file).group(1))
    name_list = list(set(name_list))
    
    # len(name_list) should be 38
    file_num_div = int(args.file_num/(len(name_list)-1))
    # print(args.file_num, len(name_list)-1, file_num_div)
    
    select_imgs = []
    for name in name_list:
        img_list = [img_name for img_name in tqdm_bar(os.listdir(args.dir_src_path), 'Procrssing {}'.format(name)) 
                    if re.search(r'(\w)_({})_+'.format(name), img_name)]
        img_list = [img_name for img_name in tqdm_bar(img_list, 'Procrssing {}'.format(name)) 
                    if (not os.path.isfile(os.path.join(csv(args), Path(img_name).stem)+'.csv')) 
                    and (img_name not in record_imgs)]
        if not len(img_list)<50:            
            try:
                select_list = sample(img_list, file_num_div)
                select_imgs.append(select_list)
            except ValueError:
                file_num_div_new = len(img_list)
                select_list = sample(img_list, file_num_div_new)
                select_imgs.append(select_list)  
                
    select_imgs = list(chain(*select_imgs))   
    select_imgs = sorted(select_imgs)   
    return select_imgs
        
def record(record_lists, select_imgs):
    tmp_dir = os.path.join(work_dir, 'temp')
    if len(record_lists)==0:
        index = 1
    else:
        def find_index(file):
            regex = re.compile(r'.+_output_(.+).txt')
            match = regex.search(file)
            return int(match.group(1))
        indexs = list(map(find_index, record_lists))
        
        index = 1
        while True:
            if index not in indexs:
                break
            else:
                index = index+1
           
    with open(os.path.join(tmp_dir, '{}_output_{}.txt'.format(date.today(), index)),'w') as file:
        for name in select_imgs:
            file.write(name+'\n')       

def split_dirs(args, select_imgs):
    split_files = np.array_split(select_imgs, args.dir_num)    
    index = 1
    while True:
        split_dir = os.path.join(output_dir, '{}_src_{}'.format(args.aly_type, index))
        if not os.path.exists(split_dir):
            break
        else:
            index = index+1
    for i, files in enumerate(split_files):
        split_dir = os.path.join(output_dir, '{}_src_{}'.format(args.aly_type, i+index))
        img_src = os.path.join(split_dir, 'img_src')
        os.makedirs(img_src, exist_ok=True)
        print('Procrssing files for this directory : {}'.format(split_dir))
        for img_name in tqdm_bar(files, 'Procrssing Files'):
            file_path = os.path.join(args.dir_src_path, str(img_name))
            copy_file_path = os.path.join(img_src, str(img_name))
            shutil.copyfile(file_path, copy_file_path) 

        need_dir = os.path.join(main_dir, 'run_FEAT')   
        for files in os.listdir(need_dir):
            if os.path.isdir(os.path.join(need_dir, files)):
                shutil.copytree(
                    os.path.join(need_dir, files),
                    os.path.join(split_dir, files)) 
            else:
                shutil.copyfile(
                    os.path.join(need_dir, files),
                    os.path.join(split_dir, files))                 
 
def run():
    record_lists, record_imgs = get_log()
    
    args = parse_args()
    
    if not args.refer:
        select_imgs = split_files(record_imgs, args)
        record(record_lists, select_imgs)
    else:
        with open(args.output_list, "r") as file:
            lines = file.read().split('\n')
            lines.pop()
            select_imgs = lines
    print("Final number of files : {}".format(len(select_imgs))) 
    split_dirs(args, select_imgs)
    

if __name__ == '__main__':     
    run()

            
    
    
    
    

            
    
        
    
