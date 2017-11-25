@echo off
start cmd /k "cd /d C:\Users\PTKON\Envs\dipl\Scripts & activate & cd /d    C:\cadver-private\src\checker & python manage.py runserver"
start cmd /k "cd /d C:\Users\PTKON\Envs\dipl\Scripts & activate & cd /d    C:\cadver-private\src\checker & python manage.py celeryd"
start "" "C:\Program Files\PTC\Creo 3.0\M110\Parametric\bin\parametric.exe"