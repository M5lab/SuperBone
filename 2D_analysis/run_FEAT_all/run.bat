@echo OFF

ver

setlocal enableextensions enabledelayedexpansion

set DATE_FORMAT=%date:~0,4%-%date:~5,2%-%date:~8,2%
set TIME_FORMAT=%time:~0,2%:%time:~3,2%:%time:~6,2%
echo Today is %DATE_FORMAT% and now time is %TIME_FORMAT%
set record_txt=%DATE_FORMAT%_run_current.txt

if not defined CHECK (set CHECK=FALSE)

if not defined PYTHON (set PYTHON=python)
if not defined CONDAPATH (set CONDAPATH=C:\ProgramData\Anaconda3)
if not defined CONDA (set CONDA=%CONDAPATH%\Scripts\conda.exe)
if not defined ENVNAME (set ENVNAME=base)
if %ENVNAME%==base (set ENVPATH=%CONDAPATH%) else (set ENVPATH=%CONDAPATH%\envs\%ENVNAME%)
if not defined LAMMPS (set LAMMPS=lmp)

mkdir temp 2>NUL

rem check_or_not
if ["%CHECK%"] == ["FALSE"] goto :launch_python

rem check_python
%PYTHON% --version >temp\stdout.txt 2>temp\stderr.txt
if %ERRORLEVEL% == 0 goto :check_conda
echo Couldn't launch python
goto :show_error

:check_conda
%CONDA% --version >temp\stdout.txt 2>temp\stderr.txt
if %ERRORLEVEL% == 0 goto :check_conda_env
echo Couldn't launch conda
goto :show_error

:check_conda_env
call %CONDAPATH%\Scripts\activate.bat %ENVPATH% >temp\stdout.txt 2>temp\stderr.txt
if %ERRORLEVEL% == 0 goto :check_lammps
echo Couldn't find conda environment
goto :show_error

:launch_python
	
rem launch python
%PYTHON% launch.py
if %ERRORLEVEL% == 0 goto :end
goto :show_error

:show_error
echo.
echo error:
type temp\stderr.txt
echo exit code: %ERRORLEVEL%

:end
echo.
echo All done 
set DATE_FORMAT=%date:~0,4%-%date:~5,2%-%date:~8,2%
set TIME_FORMAT=%time:~0,2%:%time:~3,2%:%time:~6,2%
echo Today is %DATE_FORMAT% and now time is %TIME_FORMAT%
pause

