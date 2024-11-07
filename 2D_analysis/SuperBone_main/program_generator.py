# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# ======

import os
from IPython.display import display, clear_output 
import pandas as pd
import numpy as np
from pathlib import Path
from tqdm import tqdm
import shutil

from DCMtoIMG.file_processor import *
from DCMtoIMG.DCM_processor import *
from DCMtoIMG.split_image import *
from DCMtoIMG.split_mask import *
from DCMtoIMG.save_section_image import *

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
initial_dir = os.path.join(os.path.dirname(main_dir),'dcm_src')   
output_dir = os.path.join(os.path.dirname(main_dir),'img_src_all')

import FileChooser

"""Initialize the class and set the initial directory, file type, and the type of file/folder to choose

    :param initial_dir (str) : Initial directory to open the file dialog
    :param file_type (str) : The type of file to select (e.g. "Image", "DICOM",...)
    :param choose_type (str) : The type of file/folder to select ("File", "Folder", "Multiple Files")
"""  

selector = FileChooser.Selector(initial_dir, file_type = "DICOM", choose_type = "Folder")

"""Open a file dialog windows and return the source path
    
    :param dir_path (str) : The absolute path of the directory where all input files are stored
"""

dir_path = selector.run()

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

os.chdir(dir_path)

# ======

search_csv_path = os.path.join(main_dir,'search_output.csv')
search_csv = pd.read_csv(search_csv_path,sep=',')

rel_dir_path = os.path.relpath(dir_path, initial_dir)
name_list = list(Path(rel_dir_path).parts)

def df_filter(name_list):
    search_filter = search_csv.iloc[:,[0,1,2,3,4,5,8]]
    search_filter = search_filter[search_csv['Scan Options']=='AXIAL MODE']
    try:
        search_filter = search_filter[search_filter['Class']==name_list[0]]
        search_filter = search_filter[search_filter['Order']==name_list[1]]
        search_filter = search_filter[search_filter['Family']==name_list[2]]
        search_filter = search_filter[search_filter['Genus-Species']==name_list[3]]
        search_filter = search_filter[search_filter['Part']==name_list[4]]
    except:
        pass
    return search_filter

def dcm_skeleton(dcm_srcfile, dir_save, rescale_num):
    file = Dcm(dcm_srcfile, dir_save)
    file.dcm_to_img()
    img_skeletionize = file.skeletionize_img() 
    if np.count_nonzero(img_skeletionize>0) > 2000:
        file.rescaled_img(rescale_num)
        file.cropped_img(rescale_num)
        file.cropped_mask() 

def split(dir_save, div_x, div_y, off_x, off_y, iteration):
    file = img_mask_all(dir_save, div_x, div_y, off_x, off_y)
    section_white_num = file.split_img()
    if section_white_num>0:
        file = img_all(dir_save, div_x, div_y, off_x, off_y)
        file.split_img()
        section_all, section_num = file.split_all_img()
        for section_index, sub_section in zip(section_num, section_all):
            save_section = Sect(dir_save, section_index, sub_section, off_x, off_y)
            section_img = save_section.save_section_img()   
        iteration = iteration+len(section_num)
    return iteration

"""
    :param offset_x, offset_y (numpy.ndarray) : The x and y ranges for the image offsets
    :param div_x, div_y (int) : The number of divisions along the x and y axis respectively (2,4,5,6,8)
    :param std_pixel_spacing (float) : The standardized pixel spacing for every image (Default value = 0.35mm)
    :param rescale_num (float) : The ratio of scaling image
"""

offset_x, offset_y = np.arange(-80,80+10,10), np.arange(-80,80+10,10)

div_x, div_y = 10, 10

std_pixel_spacing = 0.35

for index, row in df_filter(name_list).iterrows():
    rescale_num = std_pixel_spacing/float(row[6])
    print('Original pixel spacing : {} mm'.format(float(row[6])))

    files = file_preprocesser(main_dir, initial_dir, output_dir, row)    

    """Find all the DICOM files in the source directory and returns the file paths in a list.
    """
    dir_src_path, dcms_in_dir = files.find_all_dcm()
    print('Number of DICOM files from {} : {}'.format(os.path.relpath(dir_src_path, initial_dir), len(dcms_in_dir)))  

    iteration = 0

    for dcm_srcfile in tqdm(dcms_in_dir, desc='Procrssing File', 
                            position=0, ncols = width -40, leave=False):
        dir_save = files.save_dir(dcm_srcfile)
        imgs_in_dir = files.find_all_img()

        if len(imgs_in_dir)>0:
            print('Section images already exist. Number of images : {}'.format(len(imgs_in_dir)))
            files.delete_dir(dir_save)
            iteration = iteration+len(imgs_in_dir)
        else:
            try:
                dcm_skeleton(dcm_srcfile, dir_save, rescale_num)
                for off_x in offset_x:
                    for off_y in offset_y:
                        iteration = split(dir_save, div_x, div_y, off_x, off_y, iteration)

            except:
                pass

            if len(os.listdir(dir_save)) <= 4:                
                files.delete_dcm_img(dir_save)
                files.delete_dir(dir_save)
            else: 
                files.delete_dcm_img(dir_save)
                files.move_section_img(dir_save)
                files.delete_dir(dir_save)   

    print('Number of All Section Images for {} : {}'.format(os.path.relpath(dir_src_path, initial_dir), iteration))

    search_csv = pd.read_csv(search_csv_path,sep=',')
    search_csv['Number of Section Images'].iloc[index] = iteration
    search_csv.to_csv(search_csv_path,sep=',',index=0)  

print('\n')     
print('All done for this directory: {}'.format(os.path.relpath(dir_path,initial_dir)))        
    