'''
May 18, 2020
Create a line shapefile from a series of points without arcpy
'''

import shapefile
import os
import csv

# SET UP CSV TO PARSE/EDIT
file = 'C:\\Users\\chr\\downloads\\elephant.csv'
r = csv.reader(open(file))
lines = list(r)

# LINES[4] AND LINES[5] ARE THE COLUMNS WE HAVE TO PARSE
new_lines = []
#new_lines = [['DateTime','YX']]
for line in lines:
    new_lines.append([line[4],line[5]])
new_csv_lines = []
#new_csv_lines = [['Date','Time','Y','X']]

# let's start parsing!
for line in new_lines:
    # let's pick apart date and time
    date = line[0].split(' ')[0]
    time = line[0].split(' ')[1]
    # let's pick apart lat and lon
    y = line[1].split(',')[0].strip()
    x = str(line[1].split(',')[len(line[1].split(','))-1]).strip()
    #print('Date: ' + str(date))
    #print('Time: ' + str(time))
    #print('Lat: ' + str(y))
    #print('Lon: ' + str(x))
    new_csv_lines.append([date,time,y,x])
new_csv_lines.remove(new_csv_lines[0])
#new_csv_lines.remove(new_csv_lines[1])

# FUNCTION TO CONVERT DMS TO DECIMAL DEG
def dms_to_decDeg(deg, min, sec):
    s = float(sec)/3600
    m = float(min)/60
    d = float(deg)
    return(d + m + s)

vertices = []

for line in new_csv_lines:
    # PARSE, ASSIGN VARIABLES FOR DEGREES, MINUTES, SECONDS
    deg = line[2].split('\xb0 ')[0]
    min = line[2].split('\xb0 ')[1].split('`')[0]
    sec = line[2].split('\xb0 ')[1].split('`')[1]
    line[2] = dms_to_decDeg(deg, min, sec)
    deg = line[3].split('\xb0 ')[0]
    min = line[3].split('\xb0 ')[1].split('`')[0]
    sec = line[3].split('\xb0 ')[1].split('`')[1]
    line[3] = dms_to_decDeg(deg, min, sec)
    #print(sec)
    #line[2] = dms_to_decDeg(deg, min, sec)
    print(str(line))
    vertices.append([line[3],line[2]])

for vertex in vertices:
    print(str(vertex))

# CREATE THE SHAPEFILE
w = shapefile.Writer(shp=r'C:\Users\chr\Desktop\Elephant_qgis\travel_line.shp', dbf=r'C:\Users\chr\Desktop\Elephant_qgis\travel_line.dbf', shx=r'C:\Users\chr\Desktop\Elephant_qgis\travel_line.shx')
p = open(r'C:\Users\chr\Desktop\Elephant_qgis\travel_line.prj', 'w')
prj_stringy = 'GEOGCS[\"GCS_WGS_1984\",DATUM[\"D_WGS_1984\",SPHEROID[\"WGS_1984\",6378137.0,298.257223563]],PRIMEM[\"Greenwich\",0.0],UNIT[\"Degree\",0.0174532925199433]]'
p.write(prj_stringy)
w.ShapeType = 3
w.field('TYPE', 'C', size=10)

# CREATE THE LINE FROM VERTICES
w.line([vertices])
w.record('MATRIARCH')
w.close()
