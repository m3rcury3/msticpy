@echo off
if "%1" equ "" goto usage
if "%2" equ "" goto usage
if "%1" equ "/?" goto usage
if /I "%1" equ "--help" goto usage
if /I "%1" equ "-h" goto usage
if "%3" equ "" goto no_ver
set mp_pkg=msticpy==%3
goto ver_spec
:no_ver
set mp_pkg=msticpy
:ver_spec

set h_rule=------------------------------------------------------------
echo %h_rule%
echo MSTICPY Package release test
echo %h_rule%
if "%3" neq "" echo testing with version %3


REM test folder
pushd %2 > nul 2>&1
if %ERRORLEVEL% equ 0 goto check_env
echo %2 is not a valid directory
goto :EOF

:check_env
conda env list | findstr "%1"
if %ERRORLEVEL% neq 0 goto create_env
echo %1 is a current conda environment.
echo You should run this test in a clean environment.
echo Ctrl-C to abort or
pause

:create_env
echo %h_rule%
echo Creating environment %1...
call conda create --yes --name %1
echo Activating environment %1...
call conda activate %1
echo.
echo %h_rule%
echo Install Python
call conda install --yes python==3.7.6
call conda install --yes pip
echo.
echo %h_rule%
echo Installing msticpy...
pip install --upgrade --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple %mp_pkg%

echo %h_rule%
echo Preparing to run notebooks. Crtl-C to abort.
echo.
echo Installing nbconvert and jupyter extensions...
call conda install --yes nbconvert
call conda install --yes jupyter_contrib_nbextensions
pip install --upgrade ipython
set nb_path=docs/notebooks
if "%2" neq "" set nb_path=%2
pushd %nb_path%
echo.
echo %h_rule%
echo Running notebooks from %nb_path%...
set nbconver_opts=--execute --ExecutePreprocessor.timeout=60 --ExecutePreprocessor.kernel_name=python3 --to notebook
set NB=Base64Unpack.ipynb
jupyter nbconvert %nbconver_opts% --execute %NB%
if ERRORLEVEL 1 goto nb_error
set NB=EventTimeline.ipynb
jupyter nbconvert %nbconver_opts% --execute %NB%
if ERRORLEVEL 1 goto nb_error
set NB=FoliumMap.ipynb
jupyter nbconvert %nbconver_opts% --execute %NB%
if ERRORLEVEL 1 goto nb_error
set NB=GeoIPLookups.ipynb
jupyter nbconvert %nbconver_opts% --execute %NB%
if ERRORLEVEL 1 goto nb_error
set NB=NotebookWidgets.ipynb
jupyter nbconvert %nbconver_opts% --execute %NB%
if ERRORLEVEL 1 goto nb_error
set NB=ProcessTree.ipynb
jupyter nbconvert %nbconver_opts% --execute %NB%
if ERRORLEVEL 1 goto nb_error

echo %h_rule%
echo All notebooks ran successfully.


echo.
echo %h_rule%
echo Cleaning up...
echo removing notebook output files
del *.nbconvert.ipynb
call conda deactivate
echo.
echo About to remove the %1 environment. Ctrl-C to abort
pause
call conda env remove -n %1
popd
echo %h_rule%
echo Test completed.
echo %h_rule%

goto end

:nb_error
echo %h_rule%
echo Error encountered running notebook %NB%
echo Test Failed
echo %h_rule%
popd
goto end

:usage
echo Usage:
echo    %~n0 test-env-name [path-to-notebooks] [package-version]
echo.

:end

