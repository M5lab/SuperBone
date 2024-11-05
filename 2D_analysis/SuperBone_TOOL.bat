@echo OFF

title SuperBone_main
ver
set old_root=%cd%
set pyfile_dir=%old_root%\test_tool
echo Today is %date% and now time is %TIME%
pause

echo.
cd %pyfile_dir%
python %pyfile_dir%\tool_selector.py %*

echo.
echo All done 
echo Today is %date% and now time is %TIME%
pause


