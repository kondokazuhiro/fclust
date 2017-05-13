setlocal

if "%~2"=="" (
   echo error: too few arguments.
   echo usage: %~0 target_src_dir result_dir
   exit 1
)
if not "%~3"=="" (
   echo error: extra argument: %3
   exit 1
)

REM target source dir.
set FCLS_TARGET=%~f1
REM result dir.
set FCLS_RESULT=%~f2

REM this script dir.
set FCLS_HOME=%~dp0
set FCLS_SCRIPT=%FCLS_HOME%script


REM (0) run gtags in the target source dir.
cd %FCLS_TARGET%
if errorlevel 1 exit
gtags
if errorlevel 1 exit

cd %FCLS_SCRIPT%
if errorlevel 1 exit

REM (1) make target source file list.
python gl_target_list.py "%FCLS_TARGET%" -o "%FCLS_RESULT%"
if errorlevel 1 exit

REM (2) extract tags(definitions, references, symbols)
python gl_extract_tags.py "%FCLS_TARGET%" -o "%FCLS_RESULT%"
if errorlevel 1 exit

REM (3) make document-set from extracted tags.
python tags_to_docs.py -o "%FCLS_RESULT%"
if errorlevel 1 exit

REM (4) clustering
python cluster.py -o "%FCLS_RESULT%"
if errorlevel 1 exit

  REM make a dendrogram image (optional).
  python dendrogram.py -o "%FCLS_RESULT%"

REM (5) resolve similar functions/definitions.
python resolve_similar.py -o "%FCLS_RESULT%"
if errorlevel 1 exit

REM (6) make html.
python make_html.py -s "%FCLS_TARGET%" -o "%FCLS_RESULT%"
if errorlevel 1 exit


echo successful.

endlocal
