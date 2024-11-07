#!/usr/bin/bash
PATH+=:/home/marshall323/miniconda3/bin

echo "Your bash version : $BASH_VERSION"  
imgsrc_dir="$PWD/img_src/pattern_src"
pyfile_dir="$PWD/SuperBone_main"
output_dir="$PWD/dcm_output"
cd $imgsrc_dir
d=`date +%m-%d-%Y` 
t=`date +%T` 
echo "Today is $d and now time is $t"
echo "All image file are stored in this directory : $PWD"
read -n 1 -p "Press enter key to continue..." 
echo ""
cd $pyfile_dir
python $pyfile_dir/program_feature.py
echo ""
echo "All done"
d=`date +%m-%d-%Y`
t=`date +%T`
echo "Today is $d and now time is $t"
read -n 1 -p "Press enter key to continue..." 



