@echo OFF

rem need to check python and conda environment installation TRUE or FALSE (default to FALSE)
set CHECK=

rem may be python or python3 (default to python)
set PYTHON=
rem the path where store Anaconda or Miniconda 
rem if you are using win10 or latest windows version, the path would be C:\Users\<username>\anaconda3 or miniconda3
set CONDAPATH=
rem the path where store conda.exe
set CONDA=
rem conda environment name (default to base)
set ENVNAME=

call run.bat

