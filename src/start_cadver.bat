@echo off

SET VIRTUALENV_PATH=C:\Users\sa.tiainet2\Envs\testenv\
SET CADVER_PATH=C:\cadver
SET CREO_PATH=C:\Program Files\PTC\Creo 3.0\M110\Parametric\bin

start cmd /k "cd /d %VIRTUALENV_PATH%\Scripts & activate & cd /d %CADVER_PATH%\src\checker & python manage.py runserver 0.0.0.0:80 --insecure"
start cmd /k "cd /d %VIRTUALENV_PATH%\Scripts & activate & cd /d %CADVER_PATH%\src\checker & python manage.py celeryd"
start "" "%CREO_PATH%\parametric.exe"