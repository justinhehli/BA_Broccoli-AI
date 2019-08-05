s = open("InstallationPackages.txt").read()
s = s.replace('rasterio==1.0.22', ".\\_whl\\rasterio-1.0.22-cp37-cp37m-win_amd64.whl")
s = s.replace('GDAL==2.4.1', ".\\_whl\\GDAL-2.4.1-cp37-cp37m-win_amd64.whl")
s = s.replace('Shapely==1.6.4.post1', ".\\_whl\\Shapely-1.6.4.post1-cp37-cp37m-win_amd64.whl")

f = open("InstallationPackages.txt", 'w')
f.write(s)
f.close()