@echo OFF

title SuperBone_main
ver
set old_root=%cd%
set pyfile_dir=%old_root%\SuperBone_main
echo Today is %date% and now time is %TIME%
pause

echo.
cd %pyfile_dir%
python %pyfile_dir%\program_generator.py %*

echo.
echo All done 
echo Today is %date% and now time is %TIME%
pause


