#!/usr/bin/bash
PATH+=:/home/marshall323/miniconda3/bin

echo "Your bash version : $BASH_VERSION"  
pyfile_dir="$PWD/SuperBone_main"
d=`date +%m-%d-%Y` 
t=`date +%T` 
echo "Today is $d and now time is $t"
read -n 1 -p "Press enter key to continue..." 

cd $pyfile_dir
echo ""
python $pyfile_dir/program_generator.py

echo ""
echo "All done"
d=`date +%m-%d-%Y`
t=`date +%T`
echo "Today is $d and now time is $t"
read -n 1 -p "Press enter key to continue..." 



