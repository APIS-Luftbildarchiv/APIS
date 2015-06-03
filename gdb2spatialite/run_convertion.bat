@echo off
echo Convert APIS ESRI GDB to QGIS Spatialite DB
call "C:\OSGeo4W64\bin\o4w_env.bat"
python gdb2spatialite.py
pause