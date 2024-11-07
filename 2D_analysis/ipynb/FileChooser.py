# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# ======

import os
from tkinter import filedialog, messagebox
from tkinter import *

# ======

class Selector:

    # ======
    
    def __init__(self, initial_dir, file_type, choose_type):     

        """
        ======
        Initialize the class and set the initial directory, file type, and the type of file/folder to choose
        ======
            :param initial_dir: Initial directory to open the file dialog
            :param file_type: The type of file to select (e.g. "Image", "DICOM",...)
            :param choose_type: The type of file/folder to select ("File", "Folder", "Multiple Files")
        """  
    
        self.initial_dir = initial_dir
        self.file_type = file_type
        self.choose_type = choose_type
        
        self.src_path = None
        self.root = Tk()
        self.root.title("Select {} {}".format(self.file_type, self.choose_type))

        lbl1 = Label(master=self.root,text="Selected {}:".format(self.choose_type))
        lbl1.grid(row=0, column=0, padx=10, pady=10)

        self.src_path_display = Label(master=self.root,text="")
        self.src_path_display.grid(row=0, column=1, padx=10, pady=10)

        button2 = Button(master=self.root, text="Choose {} {}".format(self.file_type, self.choose_type), 
                         command=self.browse_button)
        button2.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=3)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1) 

    # ======

    # ======    

    def browse_button(self):
    
        """
        ======
        Open a file dialog to select a file or folder
        ======
        """
        
        self.root.withdraw()
        if self.choose_type=="Folder":
            self.src_path = filedialog.askdirectory(initialdir=self.initial_dir)
        elif self.choose_type=="File":
            self.src_path = filedialog.askopenfilename(initialdir=self.initial_dir)
        elif self.choose_type=="Multiple Files":
            self.src_path = filedialog.askopenfilenames(initialdir=self.initial_dir)        
        self.root.deiconify()

        if not self.src_path:
            messagebox.showwarning("Error", "Please select {}".format(self.choose_type))
        else:
            if self.choose_type=="Multiple Files":
                self.src_path_display.config(text=[os.path.basename(file_name) for file_name in self.src_path])
            else:
                self.src_path_display.config(text=os.path.basename(self.src_path))
            print("Import {} : {}".format(self.choose_type, self.src_path))

    # ======
    
    # ======
    
    def run(self):
    
        """
        ======
        Open a file dialog windows and return the source path
        ======
        """

        self.root.mainloop()
        return self.src_path
        
    # ======    