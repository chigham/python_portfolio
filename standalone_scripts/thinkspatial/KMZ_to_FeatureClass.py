'''
May 16, 2020
Sorts through a directory and 1 level of subdirectories for kmzs containing
individual points and labels. Appends the data to a feature class.

This workflow captures all the spatial data from *.kmz files in a folder
where only one point is used in each file. It also creates attributes in
the new feature class containing all points. One of the attributes saved
is reserved for a label or ID (ideally unique) that a client may have 
used as a label for the kml point. This is a great project for clients 
who may not use GIS or spatial data in formats other than Google Earth
kmls. One thing to keep in mind: this workflow utilizes the kml to layer
tool which creates excess files that need to be deleted later. I have 
not included code which deletes the *.lyr and *.gdb outputs. Since this 
is a heavy geoprocessing workflow, it will be slow, and is good to be 
left to run alone for hours at a time.

Credit: Christopher Higham, BYU ThinkSpatial, 2020
First used on Sloth Bear Data for Tom Smith, 2020
May be used appropriately in any part of the world
Important note: if you have many points, this workflow may take several hours
'''

import arcpy
import os
arcpy.env.overwriteOutput = True

# CREATE A NEW FEATURE CLASS, OR OVERWRITE IT, IN A GOOD LOCATION
# create the feature class
arcpy.CreateFeatureclass_management(r'O:\PROJECTS\Smith_Tom\India_Bear\India_Bear_Project\New_Bear_Points_03_27_2020.gdb', 'RNG_TMD_resting', 'point')
# saves the location of the new fc as a variable
folder_text = r'O:\PROJECTS\Smith_Tom\India_Bear\India_Bear_Project\New_Bear_Points_03_27_2020.gdb'
# saves the new fc as a variable
fc = r'O:\PROJECTS\Smith_Tom\India_Bear\India_Bear_Project\New_Bear_Points_03_27_2020.gdb\RNG_TMD_resting'
# add fields for point id
arcpy.management.AddField(fc, 'Den_ID', 'TEXT')

# READ MULTIPLE KML FILES
# folder with kml files
kml_folder = r'O:\PROJECTS\Smith_Tom\India_Bear\India_Bear_Project\India Projects\New_KMZs_03_27_2020'
# add kml file names into a list to be used later
list_of_kmzs = []
for file in os.listdir(kml_folder):
	if file.endswith('.kmz'):
		list_of_kmzs.append(os.path.join(kml_folder, file))
		arcpy.AddMessage(os.path.join(kml_folder, file))

# MAIN WORKFLOW: PROCESS THE POINTS IN THE FILES 
# AND POPULATE LABELS AS ID VALUES
# set a counter, make a list, and start a loop
i = 1
features_to_append = []
for kmz in list_of_kmzs:
    # note its label (may need to parse) # convert it to a feature class saved as a variable
	arcpy.AddMessage('KMZ #' + str(i))
	k = kmz
	# convert to layer
	# choose wisely where you dump output files
	arcpy.KMLToLayer_conversion(k, r'O:\PROJECTS\Smith_Tom\India_Bear\India_Bear_Project\KMZ_GIS_Folder_03_27_2020')
    # append point features from that new feature class to the main feature class # This requires setting up 2 cursors
	k_fc = os.path.join('O:\PROJECTS\Smith_Tom\India_Bear\India_Bear_Project\KMZ_GIS_Folder_03_27_2020', (os.path.basename(k)[:-3] + 'gdb'), 'Placemarks', 'Points')
	# add ID field for label
	arcpy.management.AddField(k_fc, 'Den_ID', 'TEXT')
	# set up cursors for data updates
	fc_cursor = arcpy.da.UpdateCursor(fc, ['Den_ID'])
	k_cursor = arcpy.da.UpdateCursor(k_fc, ['Name', 'Den_ID'])
	# save label as an attribute
	for row in k_cursor:
		row[1] = str(row[0])
		k_cursor.updateRow(row)
	# delete fields from k_fc to make schemas match
	arcpy.AddMessage('KMZ #' + str(i) + ' updating fields...')
	# delete unnecessary fields in layer for appending purposes
	# repeating this step makes the process take forever
	arcpy.DeleteField_management(k_fc, ['Name', 'FolderPath', 'SymbolID', 'AltMode', 'Base', 'Snippet', 'PopupInfo', 'HasLabel', 'LabelID'])
	# add the new layer to the list to append, increase count
	features_to_append.append(k_fc)
	i += 1

# append all k_fc points to fc
arcpy.AddMessage('Appending all points...')
arcpy.Append_management(features_to_append, fc, 'TEST')
# add any other appropriate fields to the new feature class
arcpy.AddMessage('Adding new fields...')
arcpy.management.AddFields(fc, [
	['Den_Usage', 'TEXT', 'Den usage'],
	['Dist2Roads', 'DOUBLE', 'Dist to road'],
	['Dist2Bound', 'DOUBLE', 'Dist to habitat boundary'],
	['Elevation', 'DOUBLE', 'Elevation'],
	['Aspect', 'DOUBLE', 'Aspect'],
	['Slope', 'DOUBLE', 'Slope'],
	['Ruggedness', 'DOUBLE', 'Ruggedness'],
	['Veg_Fract', 'DOUBLE', 'Vegetation fraction'],
	['Land_Cover', 'TEXT', 'Land cover'],
	['Dist2Settl', 'DOUBLE', 'Dist to settlement'],
	])




