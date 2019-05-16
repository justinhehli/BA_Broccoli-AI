import subprocess
import os.path as path 

realpath = path.relpath(r"C:\Bachelorthesis\DataAnalysis\Data2SQL\Data2SQL\bin\Debug\Data2SQL.exe")
print(realpath)
subprocess.call([r"Data2SQL\Data2SQL\bin\Debug\Data2SQL.exe",r"\\fs004\ice\lehre\bachelorarbeiten\2019\Pflanzen\Drohnenaufnahmen\20190509\report\export.csv"])