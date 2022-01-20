# Import necessary packages
import csv
import fiona
#import ee          ## Does not work, because cannot install ee
import shapefile
import json
import os
from datetime import datetime
import shapely
import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
#import mpl_toolkits
#from mpl_toolkits.basemap import Basemap
import cartopy.crs as ccrs
import owslib
import dbfread
import geopandas as gpd
import cartopy.feature as cfeature
import requests
import contextily as ctx

# Read JSON data

# Reads one file
fn = 'X:\\317\\test.json'
f = open(fn)
pts = json.load(f)
pts_list_all = pts['locations']

# Reads all files in a folder
##json_folder = input('What folder has google point data in JSON files? Please enter fully qualified path name: ')
#json_folder = 'X:\\317'
#list_of_jsons = []
#for item in os.listdir(json_folder):
    #if item.endswith('.json'):
        #list_of_jsons.append(os.path.join(json_folder, item))
        #print(os.path.join(json_folder, item))
#pts_list_all = []
#for item in list_of_jsons:
    #f = open(item)
    #pts = json.load(f)
    #pts_list = pts['locations']
    #for pt in pts_list:
        #pts_list_all.append(pt)

# Create a shapefile in GCS WGS 1984
# No user input needed
w = shapefile.Writer(shp=r'V:\GEOG_Python\Projects\Big_Data\testfile.shp', dbf=r'V:\GEOG_Python\Projects\Big_Data\testfile.dbf', shx=r'V:\GEOG_Python\Projects\Big_Data\testfile.shx', prj=r'V:\GEOG_Python\Projects\Big_Data\testfile.prj')
p = open(r'V:\GEOG_Python\Projects\Big_Data\testfile.prj', 'w')
w.shapeType = 1
# Takes input
#shp_name = input('What would you like to name your shapefile? Please do not add extention (.shp, etc.): ')
#folder_path = input('Where would you like to generate it? Please enter fully qualified path name: ')
#w = shapefile.Writer(shp=os.path.join(folder_path, shp_name + '.shp'), dbf=os.path.join(folder_path, shp_name + '.dbf'), shx=os.path.join(folder_path, shp_name + '.shx'), prj=os.path.join(folder_path, shp_name + '.prj'))
#p = open(os.path.join(folder_path, shp_name + '.prj'), 'w')
#w.shapeType = 1
prj_stringy = 'GEOGCS[\"GCS_WGS_1984\",DATUM[\"D_WGS_1984\",SPHEROID[\"WGS_1984\",6378137.0,298.257223563]],PRIMEM[\"Greenwich\",0.0],UNIT[\"Degree\",0.0174532925199433]]'
p.write(prj_stringy)
w.field('LAT', 'N', decimal=7)
w.field('LON', 'N', decimal=7)
w.field('ACCURACY', 'C', size=6)
w.field('TIMESTAMP', 'N')
w.field('DATE', 'C', size=250)
w.field('TIME', 'C', size=250)
w.field('ACT_TIMEST', 'N')
w.field('ACT_LENGTH', 'N')
w.field('ACTIVITY', 'C', size=250)
w.field('ACT_1_TYPE', 'C', size=25)
w.field('ACT_1_CONF', 'N')
w.field('ACT_2_TYPE', 'C', size=25)
w.field('ACT_2_CONF', 'N')
w.field('ACT_3_TYPE', 'C', size=25)
w.field('ACT_3_CONF', 'N')
w.field('ACT_4_TYPE', 'C', size=25)
w.field('ACT_4_CONF', 'N')
w.field('ACT_5_TYPE', 'C', size=25)
w.field('ACT_5_CONF', 'N')

# Parse the dictionary, add data to shapefile
for pt in pts_list_all:
    try:
        # parse
        print(str(pt))
        pt = dict(pt)
        # Time and Place #
        lat = pt['latitudeE7']/10000000
        lon = pt['longitudeE7']/10000000
        timestamp = int(pt['timestampMs'])
        # Accuracy #
        acc = pt['accuracy']
        accuracy = None
        try:
            if acc < 800:
                accuracy = 'HIGH'
            elif acc >= 800 and acc < 5000:
                accuracy = 'MEDIUM'
            elif acc >= 5000:
                accuracy = 'LOW'
        except:
            accuracy = 'UNKNOWN'

        # Not necessary, for reporting and errorchecking
        print('Milliseconds after point: ' + str(timestamp))
        print('Level of accuracy: ' + accuracy)
        print('Latitude: ' + str(lat) + ' -- Longitude: ' + str(lon))

        # Date and Time #
        date_base = str(datetime.utcfromtimestamp(timestamp/1000))
        date_base = date_base.split(' ')
        date_ = str(date_base[0])
        sep = '.'
        time = str(date_base[1]).split(sep, 1)[0]

        # ACTIVITY #
        if pt.get('activity') != None:
            # set up variables to add as fields
            act_timest = None
            act_length = None
            activity = None
            a1t = None
            a1c = None
            a2t = None
            a2c = None
            a3t = None
            a3c = None
            a4t = None
            a4c = None
            a5t = None
            a5c = None
            # parse for specific activity data
            try:
                act_timest = int(pt['activity'][0]['timestampMs'])
                act_length = len(pt['activity'][0]['activity'])
                activity = str(pt['activity'][0]['activity'])
                print(str(act_timest))
                try:
                    #if pt['activity'][0].get('activity') != None:
                    a1t = pt['activity'][0]['activity'][0]['type']
                    a1c = pt['activity'][0]['activity'][0]['confidence']
                    print('THIS IS WORKING')
                    try:
                        a2t = pt['activity'][0]['activity'][1]['type']
                        a2c = pt['activity'][0]['activity'][1]['confidence']
                        try:
                            a3t = pt['activity'][0]['activity'][2]['type']
                            a3c = pt['activity'][0]['activity'][2]['confidence']
                            try:
                                a4t = pt['activity'][0]['activity'][3]['type']
                                a4c = pt['activity'][0]['activity'][3]['confidence']
                                try:
                                    a5t = pt['activity'][0]['activity'][4]['type']
                                    a5c = pt['activity'][0]['activity'][4]['confidence']
                                except:
                                    print()
                            except:
                                print()
                        except:
                            print()
                    except:
                        print()
                except:
                    print()
            except:
                print()

        # Add data to the shapefile
            if act_timest == None:
                w.point(lon, lat)
                w.record(lat, lon, accuracy, int(timestamp), date_, time, None, 0, None, None, None, None, None, None, None, None, None, None, None)
            elif a1t == None:
                w.point(lon, lat)
                w.record(lat, lon, accuracy, int(timestamp), date_, time, act_timest, act_length, activity, None, None, None, None, None, None, None, None, None, None)
            elif a2t == None:
                w.point(lon, lat)
                w.record(lat, lon, accuracy, int(timestamp), date_, time, act_timest, act_length, activity, a1t, a1c, None, None, None, None, None, None, None, None)
            elif a3t == None:
                w.point(lon, lat)
                w.record(lat, lon, accuracy, int(timestamp), date_, time, act_timest, act_length, activity, a1t, a1c, a2t, a2c, None, None, None, None, None, None)
            elif a4t == None:
                w.point(lon, lat)
                w.record(lat, lon, accuracy, int(timestamp), date_, time, act_timest, act_length, activity, a1t, a1c, a2t, a2c, a3t, a3c, None, None, None, None)
            elif a5t == None:
                w.point(lon, lat)
                w.record(lat, lon, accuracy, int(timestamp), date_, time, act_timest, act_length, activity, a1t, a1c, a2t, a2c, a3t, a3c, a4t, a4c, None, None)
            else:
                w.point(lon, lat)
                w.record(lat, lon, accuracy, int(timestamp), date_, time, act_timest, act_length, activity, a1t, a1c, a2t, a2c, a3t, a3c, a4t, a4c, a5t, a5c)

        # add data to the shapefile when there is not activity listed
        else:
            w.point(lon, lat)
            w.record(lat, lon, accuracy, int(timestamp), date_, time, None, 0, None, None, None, None, None, None, None, None, None, None, None)
        print()
    except:
        print()
p.close()

# List number of points we should have in the shapefile
print('Number of records: ' + str(len(pts_list_all)))


# Convert dbf to csv
def dbf_to_csv(dbf_table_pth):#Input a dbf, output a csv, same name, same path, except extension
    csv_fn = dbf_table_pth[:-4]+ ".csv" #Set the csv file name
    table = dbfread.DBF(dbf_table_pth)# table variable is a DBF object
    with open(csv_fn, 'w', newline='') as f:# create a csv file, fill it with dbf content
        writer = csv.writer(f)
        writer.writerow(table.field_names)# write the column name
        for record in table:# write the rows
            writer.writerow(list(record.values()))
    return csv_fn # return the csv name

dbf_to_csv('V:\\GEOG_Python\\Projects\\Big_Data\\testfile.dbf')
csv_opener = open('V:\\GEOG_Python\\Projects\\Big_Data\\testfile.csv', 'r')

# Make a map, plot points

# Set up points in list
csv_points = []
lon_pts = []
lat_pts = []
with csv_opener as file:
    reader = csv.reader(file)
    for row in reader:
        try:
            csv_latitude = row[0]
            csv_longitude = row[1]
            #print(row)
            #print(csv_latitude + ' ' + csv_longitude)
            csv_points.append([float(csv_latitude), float(csv_longitude)])
            lon_pts.append(float(csv_longitude))
            lat_pts.append(float(csv_latitude))
        except:
            print('First Line: ' + str(row))
    csv_opener.close()
print(lat_pts)
points_dic_list = []
# Set up points in list of dictionaries
# This may not be needed
for lst in csv_points:
    points_dic_list.append({'geometry': lst})
    #print(str({'geometry': lst}))


#def load_point_data(point_path='V:\\GEOG_Python\\Projects\\Big_Data'):
    #csv_path = os.path.join(point_path, "testfile.csv")
    #return pd.read_csv(csv_path)
#point_data = load_point_data()
#axe = plt.axes(projection=ccrs.Miller())
#ax = point_data.plot(kind='scatter', x='LON', y='LAT', label='Points', alpha=0.5, color='black', marker='.', s=2)
#plt.show()

# geopandas plotting...proplem is you never see a map
#new_geometries = [ccrs.epsg('4326').project_geometry(ii, ccrs.Miller()) for ii in point_data.values]#points_dic_list['geometry'].values]
#axe = plt.axes(projection=ccrs.Miller())
#axe.stock_img()
#axe.add_geometries(point_data, ccrs.Miller())

#plt.show()

# Matplotlib mapping...problem is does not convert to map coordinates
ax = plt.axes(projection=ccrs.PlateCarree())
#ax = plt.axes(projection=ccrs.InterruptedGoodeHomolosine())

# Cartopy integration
ax.stock_img()
#ctx.add_basemap(ax, url='http://tile.stamen.com/watercolor/tileZ/tileX/tileY.png')#url=ctx.providers.Stamen.TerrainBackground)
#ctx.add_basemap(ax, zoom=12, url=ctx.providers.Stamen.WATERCOLOR)#url=ctx.providers.Stamen.Terrain_Background, zoom=12)
ax.set_xticks([-179.9, -90, 0, 90, 179.9], crs=ccrs.PlateCarree())
ax.set_yticks([-89.9, -45, 0, 45, 89.9], crs=ccrs.PlateCarree())
#ax.set_axis_off()

#ax.add_wmts(wmts="https://basemap.nationalmap.gov/arcgis/rest/services/USGSTopo/MapServer/wmts", layer_name=['USGSTopo'])
#ax.add_wms(wms='http://vmap0.tiles.osgeo.org/wms/vmap0', layers=['basic'])
#page = requests.get('https://basemap.nationalmap.gov/arcgis/rest/services/USGSHydroCached/MapServer', verify=False)
#ax.add_wms(wms=page, layers=['Layers'])
#ax.add_wms(wms='http://ows.mundialis.de/services/service?', layers=['TOPO-OSM-WMS'])
#ax.add_wms(layers='Layers', wms=owslib.wms.WebMapService('https://basemap.nationalmap.gov/arcgis/services/USGSTopo/MapServer/wmsserver', version='1.1.1'))
#ax.add_wms(wms='http://www.osm-wms.de/', layers=['Layers'])
# Look into basemaps more

#world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))

#world.crs = {'init': 'epsg:4326'}
#world_proj = world.to_crs(ccrs.Miller().proj4_init)
#print(world_proj)
#ax.add_geometries(world['geometry'], ccrs.PlateCarree())

#world.boundary.plot()

#ax.add_geometries(world['geometry'], ccrs.PlateCarree(), alpha=0.7)
ax.scatter(lon_pts, lat_pts, color='purple', marker='.', s=2, alpha=0.05)
plt.show()




