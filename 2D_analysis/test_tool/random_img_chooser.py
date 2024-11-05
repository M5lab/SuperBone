# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# ======

import os
import re
from pathlib import Path
from IPython.display import display
import numpy as np
import pandas as pd
from random import sample
from tqdm import tqdm
import shutil
from itertools import chain

# ======

"""Get the width and height of the terminal window.
"""

width, height = shutil.get_terminal_size((80, 20))

"""
    :param work_dir (str) : Current working directory
    :param main_dir (str) : Always be set to ./SuperBone_ver1
    :param output_dir (str) : The default directory where all outputs are stored
"""  

work_dir = os.getcwd()
main_dir = os.path.dirname(work_dir)
initial_dir = os.path.join(os.path.dirname(main_dir),'img_src_all')   
output_dir = os.path.join(main_dir,'img_src') 

file_num = input('Please input number of files (greater than 40) : ')
file_num = int(file_num)
dir_num = input('Please input number of directories : ')
dir_num = int(dir_num)
aly_type = input('Please input type of analysis (pattern or mechanical) : ')

import FileChooser

"""Initialize the class and set the initial directory, file type, and the type of file/folder to choose

    :param initial_dir (str) : Initial directory to open the file dialog
    :param file_type (str) : The type of file to select (e.g. "Image", "DICOM",...)
    :param choose_type (str) : The type of file/folder to select ("File", "Folder", "Multiple Files")
"""

selector = FileChooser.Selector(initial_dir, file_type = "PNG", choose_type = "Folder")

"""Open a file dialog windows and return the source path

    :param file_src_path (str) : The absolute path of the source image
"""

dir_src_path = selector.run()

# ======

if aly_type=='pattern':
    csv_dir = os.path.join(os.path.dirname(main_dir),'dcm_output','pattern_feature')
elif aly_type=='mechanical':
    csv_dir = os.path.join(os.path.dirname(main_dir),'dcm_output','mechanical_feature')

name_list = []
for file in os.listdir(dir_src_path):
    regex = re.compile(r'\w_(.+)_ID.+')
    match = regex.search(file)
    name_list.append(match.group(1))
name_list = list(set(name_list))

dir_list = []
for num in range(1,dir_num+1):
    output_path = os.path.join(output_dir,'{}_src_{}'.format(aly_type, num))
    dir_list.append(output_path)
    if os.path.exists(output_path):
        shutil.rmtree(output_path)
    os.makedirs(output_path, exist_ok=True)

file_num_div = int(file_num/len(name_list))+1

select_list_all = []
for name in name_list:
    img_list = [img_path for img_path in tqdm(os.listdir(dir_src_path), desc='Procrssing File: {}'.format(name), position=0, ncols = width -40, leave=False)
                if re.search(r'(\w)_({})_+'.format(name), img_path)]
    img_list = [img_path for img_path in tqdm(img_list, desc='Procrssing File: {}'.format(name), position=0, ncols = width -40, leave=False) 
                if not os.path.isfile(os.path.join(csv_dir, Path(img_path).stem)+'.csv')]
    try:
        select_list = sample(img_list, file_num_div)
        select_list_all.append(select_list)
    except ValueError:
        file_num_div_new = len(img_list)
        select_list = sample(img_list, file_num_div_new)
        select_list_all.append(select_list)       
        # print("Choose too many files, the maxinum number of files you can choose : {}".format(len(img_list)))

select_list_all = list(chain(*select_list_all))          
print("Final number of files : {}".format(len(select_list_all)))

split_file = np.array_split(select_list_all, dir_num)        
        
for i, files in enumerate(split_file):
    print('Procrssing files for this directory : {}'.format(dir_list[i]))
    for img_path in tqdm(files, desc='Procrssing File', 
                         position=0, ncols = width -40, leave=False):
        file_path = os.path.join(dir_src_path, str(img_path))
        copy_file_path = os.path.join(dir_list[i], str(img_path))
        shutil.copyfile(file_path, copy_file_path)        

# ======

print('\n')     
print('All done')


