# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# ======

import os
from pathlib import Path
from IPython.display import display, clear_output 
import pandas as pd
import shutil

from DCMsearch.file_main_processor import *
from DCMsearch.DCM_data import *

# ======

"""
    :param work_dir (str) : Current working directory
    :param main_dir (str) : Always be set to ./SuperBone_ver1
    :param output_dir (str) : The default directory where all outputs are stored
"""  

work_dir = os.getcwd()
main_dir = os.path.dirname(work_dir)
initial_dir = os.path.dirname(main_dir)
output_dir = os.path.join(initial_dir,'dcm_src')

# ======

import FileChooser

"""
======
Initialize the class and set the initial directory, file type, and the type of file/folder to choose
======
    :param initial_dir (str) : Initial directory to open the file dialog
    :param file_type (str) : The type of file to select (e.g. "Image", "DICOM",...)
    :param choose_type (str) : The type of file/folder to select ("File", "Folder", "Multiple Files")
"""  

choose_type = 'Folder'

selector = FileChooser.Selector(initial_dir, file_type = 'ZIP', choose_type = choose_type)

# ======

"""
======
Open a file dialog windows and return the source path
======
    :param file_src_path (tuple) : The absolute path of the input file

"""

file_src_path = selector.run()

if choose_type=='Folder':
    file_src_path = file_src_path+'.zip'

# ======

import sys

if sys.platform.startswith('linux'):
    # print('Linux')
    os.system('read -n 1 -p "Press enter key to continue..."')
elif sys.platform.startswith('darwin'):
    # print('macOS')
    pass
elif sys.platform.startswith('win32'):
    # print('Windows')
    os.system('pause')

# ======

# ======

"""
======
Get the width and height of the terminal window.
======
"""

width, height = shutil.get_terminal_size((80, 20))

# ======

# ======

"""
    :param dir_src_path (str) : The parent directory of the source file
    :param search_csv_path (str) : The absolute path of the CSV file that stores all data of 
                                   the source file
    :param file_name (str) : Name of the source file without its extension   
"""

dir_src_path = os.path.dirname(file_src_path)

search_csv_path = os.path.join(main_dir,'search_output.csv')
search_csv = pd.read_csv(search_csv_path,sep=',')
file_name = Path(file_src_path).stem

# ======

"""
======
Initialization method for the class
======
    :param file_src_path (str) : The absolute path of the source file
    :param dir_src_path (str) : The parent directory of the source file
    :param width (int) : The width of the terminal window
"""

files = file_main_preprocesser(file_src_path, dir_src_path, width)

# ======

"""
======
Unzipping the file. It also creates a list of all the directories contained in the file names.
======
"""

all_dirs = files.unzip()

# ======

data = DCM_analyze(all_dirs, file_src_path, dir_src_path, main_dir, search_csv, output_dir, width)

# ======

if file_name in list(search_csv['Order']):
 
    file_info_copy = data.read_exist_csv()
    print('CSV data exists for this ZIP file : {}'.format(os.path.basename(file_src_path)))
    
else:

    # ======

    file_info_copy = data.write_dataframe() 
    data.read_csv()
    print('All CSV data is saved in : {}'.format(os.path.basename(search_csv_path)))

    # ======

# ======

if file_info_copy['Part'].iloc[0]=='No Available DICOM File':
    print('There is no DICOM file in this ZIP file : {}'.format(Path(file_src_path).stem))
else:    
    data.copy_all_dcm(file_info_copy)

print('\n')
print('All done for this ZIP file: {}'.format(Path(file_src_path).stem)) 