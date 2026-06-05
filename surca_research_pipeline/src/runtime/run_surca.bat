@echo off
setlocal EnableExtensions EnableDelayedExpansion

set "SCRIPT_ROOT=%~dp0"
if "%SCRIPT_ROOT:~-1%"=="\" set "SCRIPT_ROOT=%SCRIPT_ROOT:~0,-1%"
for %%I in ("%SCRIPT_ROOT%\..") do set "SRC_ROOT=%%~fI"
for %%I in ("%SRC_ROOT%\..") do set "PACKAGE_ROOT=%%~fI"

set "CONFIG_PATH=%SCRIPT_ROOT%\run_config.json"
set "CONFIG_LOADER=%SCRIPT_ROOT%\load_run_config.py"
set "PIPELINE_SCRIPT=%SRC_ROOT%\pipeline\special_ed_pipeline_hardened.py"

set "ACTION=%~1"
if not defined ACTION goto usage
shift

set "RUN_ID_OVERRIDE="
set "OVERWRITE="

:parse_args
if "%~1"=="" goto args_done
if /I "%~1"=="--run-id" (
    set "RUN_ID_OVERRIDE=%~2"
    shift
    shift
    goto parse_args
)
if /I "%~1"=="--overwrite" (
    set "OVERWRITE=1"
    shift
    goto parse_args
)
echo Unknown option: %~1
goto usage

:args_done
if not exist "%CONFIG_PATH%" (
    echo Missing config file: %CONFIG_PATH%
    exit /b 1
)

for /f "usebackq tokens=1,* delims==" %%A in (`python "%CONFIG_LOADER%" "%CONFIG_PATH%"`) do (
    set "%%A=%%B"
)

if /I "%ACTION%"=="setup" goto setup

if not exist "%PYTHON%" (
    echo Python environment not found at %PYTHON%
    echo Run: surca_research_pipeline\src\runtime\run_surca.bat setup
    exit /b 1
)

if not defined RUN_CASES if defined PILOT_CASES set "RUN_CASES=%PILOT_CASES%"
if not defined RUN_ID if defined PILOT_RUN_ID set "RUN_ID=%PILOT_RUN_ID%"
if not defined RUN_ID set "RUN_ID=trace_ed_run_01"
if defined RUN_ID_OVERRIDE set "RUN_ID=%RUN_ID_OVERRIDE%"

if /I "%ACTION%"=="verify" goto verify
if /I "%ACTION%"=="run" goto run
if /I "%ACTION%"=="demo" goto demo

echo Unknown action: %ACTION%
goto usage

:setup
if not exist "%PYTHON%" (
    python -m venv "%VENV_DIR%"
    if errorlevel 1 exit /b 1
)

"%PYTHON%" -m pip install --upgrade pip
if errorlevel 1 exit /b 1

"%PYTHON%" -m pip install -r "%REQUIREMENTS%"
if errorlevel 1 exit /b 1
exit /b 0

:verify
call :pipeline --mode validate --base-dir "%BASE_DIR%"
if errorlevel 1 exit /b 1
call :pipeline --mode verify --base-dir "%BASE_DIR%" --base-url "%BASE_URL%" --models "%MODEL%"
if errorlevel 1 exit /b 1
echo.
echo TRACE-ED is ready.
echo Model: %MODEL%
echo Server: %BASE_URL%
if defined RUN_CASES (
    echo Cases: %RUN_CASES%
) else (
    echo Cases: all cases in the study folder
)
exit /b 0

:run
call :show_context_reminder
call :pipeline --mode validate --base-dir "%BASE_DIR%"
if errorlevel 1 exit /b 1
call :pipeline --mode verify --base-dir "%BASE_DIR%" --base-url "%BASE_URL%" --models "%MODEL%"
if errorlevel 1 exit /b 1

set "SELECTED_RUN_ID=%RUN_ID%"

if defined RUN_CASES (
    if defined OVERWRITE (
        call :pipeline --mode run --base-dir "%BASE_DIR%" --base-url "%BASE_URL%" --models "%MODEL%" --run-id "%SELECTED_RUN_ID%" --cases "%RUN_CASES%" --overwrite-run
    ) else (
        call :pipeline --mode run --base-dir "%BASE_DIR%" --base-url "%BASE_URL%" --models "%MODEL%" --run-id "%SELECTED_RUN_ID%" --cases "%RUN_CASES%"
    )
 ) else (
    if defined OVERWRITE (
        call :pipeline --mode run --base-dir "%BASE_DIR%" --base-url "%BASE_URL%" --models "%MODEL%" --run-id "%SELECTED_RUN_ID%" --overwrite-run
    ) else (
        call :pipeline --mode run --base-dir "%BASE_DIR%" --base-url "%BASE_URL%" --models "%MODEL%" --run-id "%SELECTED_RUN_ID%"
    )
)
if errorlevel 1 exit /b 1

call :pipeline --mode export-demo --base-dir "%BASE_DIR%"
if errorlevel 1 exit /b 1

echo.
echo TRACE-ED run completed.
echo Run ID: %SELECTED_RUN_ID%
echo Demo data exported.
exit /b 0

:demo
pushd "%DEMO_DIR%"
call "%NPM_CMD%" install
if errorlevel 1 (
    popd
    exit /b 1
)
call "%NPM_CMD%" run dev
set "ERR=%errorlevel%"
popd
exit /b %ERR%

:pipeline
"%PYTHON%" "%PIPELINE_SCRIPT%" %*
exit /b %errorlevel%

:show_context_reminder
echo.
echo Reminder:
echo This pipeline sends the full extracted IEP and BIP into the model.
echo If LM Studio loads the model with a small context, the run can fail.
echo Use a larger context length in LM Studio before running tests.
echo.
exit /b 0

:usage
echo.
echo Usage:
echo   surca_research_pipeline\src\runtime\run_surca.bat setup
echo   surca_research_pipeline\src\runtime\run_surca.bat verify
echo   surca_research_pipeline\src\runtime\run_surca.bat run [--run-id NAME] [--overwrite]
echo   surca_research_pipeline\src\runtime\run_surca.bat demo
echo.
exit /b 1
