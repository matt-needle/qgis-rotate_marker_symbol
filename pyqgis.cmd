@echo off
SET OSGEO4W_ROOT=C:\OSGeo4W
call "%OSGEO4W_ROOT%"\bin\o4w_env.bat
@echo off
path %PATH%;%OSGEO4W_ROOT%\apps\qgis-dev\bin
path %PATH%;C:\OSGeo4W3\apps\Qt5\bin
path %PATH%;C:\OSGeo4W3\apps\Python312\Scripts

set PYTHONPATH=%PYTHONPATH%;%OSGEO4W_ROOT%\apps\qgis-dev\python
set PYTHONHOME=%OSGEO4W_ROOT%\apps\Python312

cmd.exe