# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# ======

import os
from pathlib import Path
from IPython.display import display, clear_output 
import pandas as pd
import numpy as np
# from tqdm import tqdm
from time import sleep

from IMGtoParticle.lammps_file_processor import *
from IMGtoParticle.resize_image import *
from IMGtoParticle.Img2Particle_real import *
from IMGtoParticle.Img2Particle_si import *

from LAMMPStoDATA.mechanic_calculation import *
from LAMMPStoDATA.mechanic_data import *

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
output_dir = os.path.join(os.path.dirname(main_dir),'dcm_output','mechanical_feature')

unit = input('Please choose a unit (si or real) : ')
unit = unit.lower()
simulation = input('Please choose a simulation (LJ or LSM) : ')
simulation = simulation.upper()

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

files = lmpfile_preprocesser(main_dir, output_dir, dir_src_path, unit, simulation)

imgs_in_dir = files.find_all_img()

std_pixel_spacing = 0.35

if len(imgs_in_dir)==0:
     print('No section images saved from {}'.format(dir_src_path))
        
else:
    print('Number of section images saved from {} : {}'.format(os.path.relpath(dir_src_path,main_dir), len(imgs_in_dir)))
    for img_path in imgs_in_dir:
        img_name = Path(img_path).stem
        csv_file = os.path.join(output_dir,img_name)+'.csv'
        df = (pd.read_csv(csv_file,sep=',') if os.path.isfile(csv_file) 
              else pd.DataFrame({'Unit':['None'], 'Simulation':['None']})
             )
            
        if os.path.isfile(csv_file) and unit in list(df['Unit']) and simulation in list(df['Simulation']):
            print('Data file exist : {}'.format(os.path.relpath(csv_file,output_dir)))
                
        else:
            txt_output_dir = os.path.join(os.path.dirname(output_dir), 'mechanical_txt')
            ss_txt = os.path.join(txt_output_dir,'ss_'+img_name+'_{}_{}.txt'.format(unit, simulation))
            if os.path.isfile(ss_txt):
                pass
            else:
                img = Sect_resize(img_path)   
                resize_img = img.section_img()

                if unit == 'si':
                    particle = ImgtoParticle_si(img_path, resize_img, output_dir, std_pixel_spacing, simulation)             
                elif unit == 'real':
                    particle = ImgtoParticle_real(img_path, resize_img, output_dir, std_pixel_spacing, simulation)  
                particle.read_data()
                particle.run()  
                copy_lmp_path = files.lammps_copy(img_path)
                print('Write lammps input file : {}'.format(os.path.basename(copy_lmp_path))) 

                print('starting lammps...')
                
                os.chdir(os.path.dirname(copy_lmp_path))
                os.system('lmp -in {}'.format(copy_lmp_path))
                os.chdir(dir_src_path)
                
                #files.delete_files() 
            
            mechanic = cal_data(output_dir, img_name, unit, simulation)
            mechanic.set_dataframe()
            mechanic.cal_ss()
            mechanic.mechanic_to_df()
            
            print('Data file is saved : {}'.format(os.path.relpath(csv_file,output_dir)))
            
csvs_in_dir = files.find_all_csv()
        
for csv_path in csvs_in_dir:
    mechanic = Mechanic_analyze(main_dir, csv_path)
    mechanic.read_csv()
    
#files.delete_all_files()
   
# ======
        
print('\n')
print('All done for this directory: {}'.format(os.path.relpath(dir_src_path,main_dir)))    
print('Unit: {}, Simulation: {}'.format(unit, simulation))  
