'''
May 9, 2020
Convert a csv containing records for point features and their 
attributes to a shapefile without arcpy
'''

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

csv_write_lines = [['Date','Time','Y','X']]
for line in new_csv_lines:
    csv_write_lines.append(line)

# MAKE A NEW CSV WITH THE CHANGES
new_file = 'C:\\Users\\chr\\downloads\\new_elephant.csv'
writer = csv.writer(open(new_file, 'w'))
writer.writerows(csv_write_lines)