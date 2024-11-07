# !/usr/bin/env python3
# -*- coding: utf-8 -*-

from tqdm import tqdm
import traceback
import shutil

def colorstr(color, string):
    # Colors a string https://en.wikipedia.org/wiki/ANSI_escape_code, i.e.  colorstr('blue', 'hello world')
    # Function is refered from YOLOv5 files
    colors = {
        'black': '\033[30m',  # basic colors
        'red': '\033[31m',
        'green': '\033[32m',
        'yellow': '\033[33m',
        'blue': '\033[34m',
        'magenta': '\033[35m',
        'cyan': '\033[36m',
        'white': '\033[37m',
        'bright_black': '\033[90m',  # bright colors
        'bright_red': '\033[91m',
        'bright_green': '\033[92m',
        'bright_yellow': '\033[93m',
        'bright_blue': '\033[94m',
        'bright_magenta': '\033[95m',
        'bright_cyan': '\033[96m',
        'bright_white': '\033[97m',
        'end': '\033[0m',  # misc
        'bold': '\033[1m',
        'underline': '\033[4m'}
    
    return colors[color] + string + colors['end']

def print_args(s):
    lines = s.strip().split("\n")
    max_len = max([len(x) for x in lines])

    print('=' * max_len)
    for line in lines:
        print(line)
    print('=' * max_len)
    
def print_err(e:Exception):
    err_type = e.__class__.__name__
    print(err_type)
    print(traceback.format_exc(), file=sys.stderr)
    
def get_windows_size():
    """Get the width and height of the terminal window.
    """
    width, height = shutil.get_terminal_size((80, 20))
    return width, height
    
def tqdm_bar(iterator, desc=''):
    width, _ = get_windows_size()
    return tqdm(iterator, desc=desc, position=0, ncols = width -40, leave=False)
    