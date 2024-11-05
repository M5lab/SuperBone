# ======

import os
from IPython.display import display, clear_output 
import pandas as pd
import numpy as np
from tqdm import tqdm
# from time import sleep

from LAMMPStoDATA.ss_draw_curve import *

work_dir = os.getcwd()

from tkinter import filedialog
from tkinter import *
    
def browse_button():
    global folder_path
    global ss_path
    ss_path = filedialog.askopenfilename(initialdir=os.path.join(os.path.dirname(work_dir),'dcm_output','mechanical_feature'))
    folder_path.set(ss_path)
    print("Import file : {}".format(ss_path))

root = Tk()
folder_path = StringVar()
lbl1 = Label(master=root,textvariable=folder_path)
lbl1.grid(row=0, column=1)
button2 = Button(text="Choose a ss.txt file", command=browse_button)
button2.grid(row=0, column=3)

mainloop()

dir_src_path = os.path.dirname(ss_path)

# ======

ss = Draw(dir_src_path, ss_path)
ss.draw_ss()
        
print('all done')

# ======
