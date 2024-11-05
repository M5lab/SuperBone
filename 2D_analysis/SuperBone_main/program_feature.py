# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# ======

import os
from pathlib import Path
from IPython.display import display, clear_output 
import pandas as pd
import numpy as np
from tqdm import tqdm
from time import sleep

from IMGtoFeature.feature_calculation import *
from IMGtoFeature.feature_data import *
from IMGtoFeature.file_processor import *
from IMGtoFeature.resize_image import *

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)       

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
initial_dir = os.path.join(main_dir,'img_src')   
output_dir = os.path.join(os.path.dirname(main_dir),'dcm_output','pattern_feature')

import FileChooser

"""Initialize the class and set the initial directory, file type, and the type of file/folder to choose

    :param initial_dir (str) : Initial directory to open the file dialog
    :param file_type (str) : The type of file to select (e.g. "Image", "DICOM",...)
    :param choose_type (str) : The type of file/folder to select ("File", "Folder", "Multiple Files")
"""  

selector = FileChooser.Selector(initial_dir, file_type = "PNG", choose_type = "Folder")

"""Open a file dialog windows and return the source path
    
    :param dir_path (str) : The absolute path of the directory where all input files are stored
"""

dir_src_path = selector.run()

# ======

import sys

if sys.platform.startswith('linux'):
    # print('Linux')
    # os.system('read -n 1 -p "Press enter key to continue..."')
    pass
elif sys.platform.startswith('darwin'):
    # print('macOS')
    pass
elif sys.platform.startswith('win32'):
    # print('Windows')
    os.system('pause')

# ======

os.chdir(dir_src_path)

# ======

files = file_preprocesser(main_dir, output_dir, dir_src_path)

imgs_in_dir = files.find_all_img()

if len(imgs_in_dir)==0:
     print('No section images saved from {}'.format(dir_src_path))
else:
    print('Number of section images saved from {} : {}'.format(os.path.relpath(dir_src_path,main_dir), len(imgs_in_dir)))
    for img_path in tqdm(imgs_in_dir, desc='Procrssing File', 
                         position=0, ncols = width -40, leave=False):
        img_name = Path(img_path).stem
        csv_file = os.path.join(output_dir,img_name)+'.csv'
        if os.path.isfile(csv_file):
            print('Data file exist : {}'.format(os.path.relpath(csv_file,main_dir)))
        else:
            img = Sect_resize(img_path)
            resize_img = img.section_img()
            # img_show(resize_img)  

            features = cal_data(resize_img, dir_src_path, output_dir, img_name)
            features.set_dataframe()
            features.cal_porosity()
            features.cal_line_angle()
            features.cal_line()
            features.cal_pore()
            features.features_to_df()
            # print('Data file is saved : {}'.format(os.path.relpath(csv_file,output_dir))) 
   
'''   
csvs_in_dir = files.find_all_csv()
        
for csv_path in tqdm(csvs_in_dir, desc='Procrssing CSV Data', 
                     position=0, ncols = width -40, leave=False):
    features = Feature_analyze(main_dir, csv_path)
    features.read_csv()       
'''

# ======

print('\n')
print('All done for this directory: {}'.format(os.path.relpath(dir_src_path,main_dir)))   
