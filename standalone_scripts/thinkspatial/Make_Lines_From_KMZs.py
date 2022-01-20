'''
May 16, 2020
Elephant KML to line feature class in file geodatabase

This is a powerful workflow that converts lines from several kmls to a single
feature class. It only works on files that have individual line features. One 
important limitation to note is that it does not maintain geometric curves in
the features, meaning they will look jagged and a little janky. In that sense,
this workflow as written could be improved. An example of how you could use 
this script is to compile several trails or roads, each with their own kml 
file, into a single feature class. Another improvement that can be made is 
code to delete excess *.lyr and *.gdb files created in the KML to Layer tool.

Credit: Christopher Higham, BYU ThinkSpatial, 2020
First used on Sloth Bear Data for Tom Smith, 2020
May be used appropriately in any part of the world
Important note: if you have many lines, this workflow may take several hours
'''


# SET ENVIRONMENTS AND VARIABLES
import arcpy, os
arcpy.env.overwriteOutput = True
# create a new feature class, or overwrite it, in a good location
arcpy.CreateFeatureclass_management(r'O:\ThinkSpatial\PROJECTS\Smith_Tom\India_Bear\India_Bear_Project\New_Bear_Points_03_27_2020.gdb', 'Borders_All_But_TMD', 'Polyline')
# save new fc as a variable
fc = r'O:\ThinkSpatial\PROJECTS\Smith_Tom\India_Bear\India_Bear_Project\New_Bear_Points_03_27_2020.gdb\Borders_All_But_TMD'
arcpy.AddMessage('Created Borders feature class...')
arcpy.AddMessage('fc = ' + str(fc))

# FUNCTION TO PARSE FOR KMLS
def parse_for_kmzs(file_path, a_list):
	'''Appends file names with .kmz extension to a list
	Parameters:
		file_path: A directory or folder path
		a_list: A list of string file names containing kmzs to extract geometry and labels from
	Returns: nothing
	'''
	for file in os.listdir(file_path):
		# add appropriate files to a list for processing
		#if 'road' in os.path.basename(file) == False and 'Road' in os.path.basename(file) == False and 'ROad' in os.path.basename(file) == False:
		if 'Arisikere' in os.path.basename(file) or 'Border' in os.path.basename(file):
			a_list.append(os.path.join(file_path, os.path.basename(file)))

# MAKE A LIST OF KMLS
list_of_kmzs = []
#parse_for_kmzs(r'O:\ThinkSpatial\PROJECTS\Smith_Tom\India_Bear\India_Bear_Project\India Projects\New_KMZs\Tumakuru', list_of_kmzs)
parse_for_kmzs(r'O:\ThinkSpatial\PROJECTS\Smith_Tom\India_Bear\India_Bear_Project\India Projects\New_KMZs\Arisikere_and_HAD', list_of_kmzs)
parse_for_kmzs(r'O:\ThinkSpatial\PROJECTS\Smith_Tom\India_Bear\India_Bear_Project\India Projects\New_KMZs\Daroji', list_of_kmzs)
parse_for_kmzs(r'O:\ThinkSpatial\PROJECTS\Smith_Tom\India_Bear\India_Bear_Project\India Projects\New_KMZs\Gudekote', list_of_kmzs)
parse_for_kmzs(r'O:\ThinkSpatial\PROJECTS\Smith_Tom\India_Bear\India_Bear_Project\India Projects\New_KMZs\Ramanagara', list_of_kmzs)
parse_for_kmzs(r'O:\ThinkSpatial\PROJECTS\Smith_Tom\India_Bear\India_Bear_Project\India Projects\New_KMZs\Ramdurg', list_of_kmzs)

# List kmzs to parse
for km in list_of_kmzs:
	arcpy.AddMessage('kmz: ' + str(os.path.basename(km)))


# Create feature classes for KMZs
i = 1
features_to_append = []
for kmz in list_of_kmzs:
	arcpy.AddMessage('KMZ #' + str(i))
	arcpy.KMLToLayer_conversion(kmz, r'O:\ThinkSpatial\PROJECTS\Smith_Tom\India_Bear\India_Bear_Project\KMZ_GIS_Folder_03_27_2020')
	k_fc_string = os.path.join('O:\\ThinkSpatial\\PROJECTS\\Smith_Tom\\India_Bear\\India_Bear_Project\\KMZ_GIS_Folder_03_27_2020', (os.path.basename(kmz)[:-3] + 'gdb'), 'Placemarks', 'Polylines')
	arcpy.AddMessage(k_fc_string)
	k_fc = k_fc_string
	arcpy.AddMessage('KMZ #' + str(i) + ' feature class created')
	features_to_append.append(k_fc)
	for field in arcpy.ListFields(k_fc):
                arcpy.AddMessage(str(field))
                if field.name.upper() != 'OBJECTID':
                        if field.name.upper() != 'SHAPE':
                                if field.name.upper() != 'SHAPE_LENGTH':
                                        if field.name.upper() != 'OID':
                                                arcpy.DeleteField_management(k_fc, field.name)
	i += 1
	arcpy.AddMessage('Appending features...')
	arcpy.Append_management(k_fc, fc, 'TEST')
# Append all k_fc points to fc
#arcpy.AddMessage('Appending features...')
#arcpy.Append_management(features_to_append, fc, 'TEST')
