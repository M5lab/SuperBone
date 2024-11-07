@echo OFF

ver
echo Today is %DATE% and now time is %TIME%

if not defined CHECK (set CHECK=FALSE)

if not defined PYTHON (set PYTHON=python)
if not defined CONDAPATH (set CONDAPATH=C:\ProgramData\Anaconda3)
if not defined CONDA (set CONDA=%CONDAPATH%\Scripts\conda.exe)
if not defined ENVNAME (set ENVNAME=base)
if %ENVNAME%==base (set ENVPATH=%CONDAPATH%) else (set ENVPATH=%CONDAPATH%\envs\%ENVNAME%)

mkdir temp 2>NUL

:check_or_not
if ["%CHECK%"] == ["FALSE"] goto :launch python

:check_python
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
if %ERRORLEVEL% == 0 goto :launch python
echo Couldn't find conda environment
goto :show_error

:launch python
%PYTHON% launch.py -f %FILE_NUM% -d %DIR_NUM% -aly %ANALYZE_TYPE%
if %ERRORLEVEL% == 0 goto :end
%PYTHON% launch.py 2>temp\stderr.txt
echo Couldn't find python script "launch.py"
goto :show_error

:show_error
echo.
echo error:
type temp\stderr.txt
echo exit code: %ERRORLEVEL%

:end
echo.
echo All done 
echo Today is %DATE% and now time is %TIME%
pause

