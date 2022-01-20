#   This is a script that documents GIS data in a given folder or
#   geodatabase. The user has the option of printing to the
#   console, appearing in ArcGIS, or being outputed to a new text
#   file. More instructions and help may be found in the ArcGIS
#   script tool help.

##################################################################
##################### Set environments here ######################
##################################################################

# Import modules
import arcpy
import os
import ntpath

# Make things over-write-able
arcpy.env.overwriteOutput = True

# Set the workspace
# Eventually you will want to adapt to use folders as a workspace
arcpy.env.workspace = arcpy.GetParameterAsText(0)
w_space = arcpy.GetParameterAsText(0)


##################################################################
################### Define functions here ########################
##################################################################

# This is for documenting geodatabases files
def present_datatype(datatypeList, caption, my_file):
    #if caption != 'Feature datasets':
    display(caption + ':', my_file)
    i = 0
    for xyz in datatypeList:
        if caption != 'Feature datasets':
            display('  ' + xyz, my_file)
        if caption == 'Feature classes' and arcpy.Exists(xyz):
            desc = arcpy.Describe(xyz)
            # Geometry type
            if desc.featureType == 'Simple':
                display('    Type: ' + desc.shapeType, my_file)
            else:
                display('    Type: ' + desc.featureType, my_file)
            # Coordinate system
            display('    Coordinate system: ' + desc.spatialReference.name + ' (Linear Unit: ' + desc.spatialReference.linearUnitName + ')', my_file)
            # Extent
            extent_list = []
            if desc.extent.XMin != None:
                extent_list.append('Xmin: ' + str(desc.extent.XMin))
            if desc.extent.XMax != None:
                extent_list.append('Xmax: ' + str(desc.extent.XMax))
            if desc.extent.YMin != None:
                extent_list.append('Ymin: ' + str(desc.extent.YMin))
            if desc.extent.YMax != None:
                extent_list.append('Ymax: ' + str(desc.extent.YMax))
            if desc.extent.ZMin != None:
                extent_list.append('Zmin: ' + str(desc.extent.ZMin))
            if desc.extent.ZMax != None:
                extent_list.append('Zmax: ' + str(desc.extent.ZMax))
            if desc.extent.MMin != None:
                extent_list.append('Mmin: ' + str(desc.extent.MMin))
            if desc.extent.MMax != None:
                extent_list.append('Mmax: ' + str(desc.extent.MMax))
            display('    Extent: ', my_file)
            for a in extent_list:
                display('      ' + a, my_file)
            #display('    Extent: ' + str(desc.extent), my_file) # this command is faster, but worse
            # Subtypes
            if len(subtypes(w_space + '\\' + xyz)) > 0:
                display('    Subtypes: ', my_file)
                for o in subtypes(w_space + '\\' + xyz):
                    display('      ' + str(o), my_file)
            # Contingent values
            if len(contingent_values(w_space + '\\' + xyz)) > 0:
                display('    Contingent values: ', my_file)
                for o in contingent_values(w_space + '\\' + xyz):
                    display('      Field group name: \'' + o + '\'', my_file)
            # Number of features
            display('    Number of features: ' + str(number_of_records(xyz)), my_file)
            # Fields, by name and type
            display('    Fields: ', my_file)
            fields = arcpy.ListFields(xyz)
            for field in fields:
                display('      ' + field.name + ', ' + field.type, my_file)
        elif caption == 'Raster datasets':
            desc = arcpy.Describe(w_space + '\\' + xyz)
            # Coordinate system
            display('    Coordinate system: ' + desc.spatialReference.name + ' (Linear Unit: ' + desc.spatialReference.linearUnitName + ')', my_file)
            # Cell dimentions
            cellsize_x = str(desc.children[0].meanCellHeight)
            cellsize_y = str(desc.children[0].meanCellWidth)
            display('    Cell Size X: ' + cellsize_x + ' - Cell Size Y: ' + cellsize_y, my_file)
            # Dataset dimentions (height and width)
            columns_count = str(desc.children[0].width)
            rows_count = str(desc.children[0].height)
            display('    Columns: ' + columns_count + ' - Rows: ' + rows_count, my_file)
            # Extent
            extent_list = []
            if desc.extent.XMin != None:
                extent_list.append('Xmin: ' + str(desc.extent.XMin))
            if desc.extent.XMax != None:
                extent_list.append('Xmax: ' + str(desc.extent.XMax))
            if desc.extent.YMin != None:
                extent_list.append('Ymin: ' + str(desc.extent.YMin))
            if desc.extent.YMax != None:
                extent_list.append('Ymax: ' + str(desc.extent.YMax))
            if desc.extent.ZMin != None:
                extent_list.append('Zmin: ' + str(desc.extent.ZMin))
            if desc.extent.ZMax != None:
                extent_list.append('Zmax: ' + str(desc.extent.ZMax))
            if desc.extent.MMin != None:
                extent_list.append('Mmin: ' + str(desc.extent.MMin))
            if desc.extent.MMax != None:
                extent_list.append('Mmax: ' + str(desc.extent.MMax))
            display('    Extent: ', my_file)
            for a in extent_list:
                display('      ' + a, my_file)
            #display('    Extent: ' + str(desc.extent), my_file) # this command is faster, but worse
        elif caption == 'Standalone tables' and arcpy.Exists(xyz):
            desc = arcpy.Describe(xyz)
            if len(subtypes(w_space + '\\' + xyz)) > 0:
                display('    Subtypes: ', my_file)
                for o in subtypes(w_space + '\\' + xyz):
                    display('      ' + str(o), my_file)
            if len(contingent_values(w_space + '\\' + xyz)) > 0:
                display('    Contingent values: ', my_file)
                for o in contingent_values(w_space + '\\' + xyz):
                    display('      Field group name: \'' + o + '\'', my_file)
            display('    Number of rows: ' + str(number_of_records(xyz)), my_file)
            display('    Fields: ', my_file)
            fields = arcpy.ListFields(xyz)
            for field in fields:
                display('      ' + field.name + ', ' + field.type, my_file)
        elif caption == 'Relationship classes':
            desc = arcpy.Describe(xyz)
            display('    Cardinality: ' + desc.cardinality, my_file)
            display('    Class names: Origin table name-\'' + str(desc.originClassNames[0]) + '\', Destination table name-\'' + str(desc.destinationClassNames[0]) + '\'', my_file)
            display('    Class keys: Primary key field-\'' + str(desc.originClassKeys[0][0]) + '\', Foreign key field-\'' + str(desc.originClassKeys[1][0]) + '\'', my_file)
            if desc.cardinality == 'ManyToMany' and (len(desc.destinationClassKeys[0][0])):
                display('    Destination class keys: Primary key-\'' + str(desc.destinationClassKeys[0][0]) + '\', Foreign key-\'' + str(desc.originClassKeys[1][0] + '\''), my_file)
        elif caption == 'Various datasets':
            print()
        elif caption == 'Feature datasets':
            i += 1
            display(str(i) + ') ' + xyz, my_file)
            # Coordinate System
            desc = arcpy.Describe(xyz)
            display('    Coordinate system: ' + desc.spatialReference.name + ' (Linear Unit: ' + desc.spatialReference.linearUnitName + ')',my_file)
            # List feature classes
            ds_fc_List = arcpy.da.Walk(xyz, datatype='FeatureClass')
            for o in ds_fc_List:
                if len(o[2]) > 0:
                    display('    Feature classes:', my_file)
                    for oo in o[2]:
                        display('      ' + oo, my_file)
            # List Networks
            ds_ntw_List = arcpy.da.Walk(xyz, datatype='NetworkDataset')
            for o in ds_ntw_List:
                for oo in o[2]:
                    display('    Network dataset: ' + oo, my_file)
            # List Parcel Fabrics
            ds_pf_List = arcpy.da.Walk(xyz, datatype='CadastralFabric')
            for o in ds_pf_List:
                for oo in o[2]:
                    display('    Parcel fabric: ' + oo, my_file)
            # List Geometry Networks
            ds_gm_List = arcpy.da.Walk(xyz, datatype='GeometricNetwork')
            for o in ds_gm_List:
                for oo in o[2]:
                    display('    Geometric network: ' + oo, my_file)
            # List Topologies
            ds_top_List = arcpy.da.Walk(xyz, datatype='Topology')
            for o in ds_top_List:
                for oo in o[2]:
                    display('    Topology: ' + oo, my_file)
    # Footer/separator
    display('', my_file)
    display('***', my_file)
    display('', my_file)

# This is for documenting folder GIS data
def present_datatype_folder(datatypeList, caption, my_file):
    #if caption != 'Feature datasets':
    display(caption + ':', my_file)
    i = 0
    for xyz in datatypeList:
        display('  ' + xyz, my_file)
        if caption == 'Shapefiles':
            desc = arcpy.Describe(xyz)
            # Geometry type
            display('    Type: ' + desc.shapeType, my_file)
            # Coordinate system
            display('    Coordinate system: ' + desc.spatialReference.name + ' (Linear Unit: ' + desc.spatialReference.linearUnitName + ')', my_file)
            # Extent
            extent_list = []
            if desc.extent.XMin != None:
                extent_list.append('Xmin: ' + str(desc.extent.XMin))
            if desc.extent.XMax != None:
                extent_list.append('Xmax: ' + str(desc.extent.XMax))
            if desc.extent.YMin != None:
                extent_list.append('Ymin: ' + str(desc.extent.YMin))
            if desc.extent.YMax != None:
                extent_list.append('Ymax: ' + str(desc.extent.YMax))
            if desc.extent.ZMin != None:
                extent_list.append('Zmin: ' + str(desc.extent.ZMin))
            if desc.extent.ZMax != None:
                extent_list.append('Zmax: ' + str(desc.extent.ZMax))
            if desc.extent.MMin != None:
                extent_list.append('Mmin: ' + str(desc.extent.MMin))
            if desc.extent.MMax != None:
                extent_list.append('Mmax: ' + str(desc.extent.MMax))
            display('    Extent: ', my_file)
            for a in extent_list:
                display('      ' + a, my_file)
            #display('    Extent: ' + str(desc.extent), my_file) # this command is faster, but worse
            # Number of features
            display('    Number of features: ' + str(number_of_records(xyz)), my_file)
            # Fields, by name and type
            display('    Fields: ', my_file)
            fields = arcpy.ListFields(xyz)
            for field in fields:
                display('      ' + field.name + ', ' + field.type, my_file)
        elif caption == 'Raster datasets':
            desc = arcpy.Describe(w_space + '\\' + xyz)
            # Coordinate system
            display('    Coordinate system: ' + desc.spatialReference.name + ' (Linear Unit: ' + desc.spatialReference.linearUnitName + ')', my_file)
            # Cell dimentions
            cellsize_x = str(desc.children[0].meanCellHeight)
            cellsize_y = str(desc.children[0].meanCellWidth)
            display('    Cell Size X: ' + cellsize_x + ' - Cell Size Y: ' + cellsize_y, my_file)
            # Dataset dimentions (height and width)
            columns_count = str(desc.children[0].width)
            rows_count = str(desc.children[0].height)
            display('    Columns: ' + columns_count + ' - Rows: ' + rows_count, my_file)
            # Extent
            extent_list = []
            if desc.extent.XMin != None:
                extent_list.append('Xmin: ' + str(desc.extent.XMin))
            if desc.extent.XMax != None:
                extent_list.append('Xmax: ' + str(desc.extent.XMax))
            if desc.extent.YMin != None:
                extent_list.append('Ymin: ' + str(desc.extent.YMin))
            if desc.extent.YMax != None:
                extent_list.append('Ymax: ' + str(desc.extent.YMax))
            if desc.extent.ZMin != None:
                extent_list.append('Zmin: ' + str(desc.extent.ZMin))
            if desc.extent.ZMax != None:
                extent_list.append('Zmax: ' + str(desc.extent.ZMax))
            if desc.extent.MMin != None:
                extent_list.append('Mmin: ' + str(desc.extent.MMin))
            if desc.extent.MMax != None:
                extent_list.append('Mmax: ' + str(desc.extent.MMax))
            display('    Extent: ', my_file)
            for a in extent_list:
                display('      ' + a, my_file)
            #display('    Extent: ' + str(desc.extent), my_file) # this command is faster, but worse
        elif caption == 'Standalone tables':
            desc = arcpy.Describe(xyz)
            display('    Number of rows: ' + str(number_of_records(xyz)), my_file)
            display('    Fields: ', my_file)
            fields = arcpy.ListFields(xyz)
            for field in fields:
                display('      ' + field.name + ', ' + field.type, my_file)
    # Footer/separator
    display('', my_file)
    display('***', my_file)
    display('', my_file)

# Simplifies closing process. Just for fun.
def close(t_file_path):
    t_file_path.close()

# Prints, Add(s)Message to ArcGIS, and writes to file if specified
def display(something = '', my_file = None):
    arcpy.AddMessage('' + str(something))
    if arcpy.GetParameterAsText(1) != None:
        my_file.write(something + '\n')

# Returns a list of subtype dictionaries in a geodatabase table
def subtypes(fc_or_table):
    try:
        subtypes_dictionary = arcpy.da.ListSubtypes(fc_or_table)
        subtypes_list = list(subtypes_dictionary.items())
        if len(subtypes_list) == 0:
            return []
        else:
            return subtypes_list
    except:
        return []

# Returns a list of contingent values in a geodatabase table
def contingent_values(fc_or_table):
    try:
        c_v_object = arcpy.da.ListContingentValues(fc_or_table)
        c_v_list = []
        for o in c_v_object:
            c_v_list.append(o.fieldGroupName)
        if len(c_v_list) == 0:
            return []
        else:
            return c_v_list
    except:
        return []

# This is for documenting geodatabases domains
def domains(w_space):
    domainList = arcpy.da.ListDomains(w_space)
    for domain in domainList:
        display('Domain: ' + domain.name, doc)
        display('  Type: ' + domain.domainType, doc)
        if domain.domainType == 'CodedValue':
            display('  Values: ' + str(domain.codedValues), doc)
        elif domain.domainType == 'Range':
            display('  Values: ' + str(domain.Range), doc)
        display('\n', doc)

# Gives a basename its appropriate file name
def basenameList_to_filenameList(list, w_space):
    for y in list:
        y = w_space + '\\' + y

# Faster than arcpy.GetCount_management
def number_of_records(table):
    try:
        fields = arcpy.ListFields(table)
        first_field = fields[0].name
        cursor = arcpy.da.SearchCursor(table, first_field)
        i = 0
        for x in cursor:
            i += 1
        return i
    except:
        return 'Unknown'


##################################################################
##################### Document.txt setup #########################
##################################################################

# Start the process, create or recreate text file if specified
doc_text = None
doc = None
if arcpy.GetParameterAsText(1) != None:
    doc_text = arcpy.GetParameterAsText(1)
    if os.path.exists(doc_text):
        os.remove(doc_text)
        arcpy.AddMessage('Deleted...')
        open(doc_text, 'x')
    arcpy.AddMessage('Text file created...')
    doc = open(doc_text, 'w')
display(w_space, doc)

# List file name and workspace type
if w_space.endswith('.gdb'):
    display('File geodatabase (ESRI)' + '\n', doc)
elif w_space.endswith('.mdb'):
    display('Personal geodatabase (Microsoft)' + '\n', doc)
else:
    display('File folder' + '\n', doc)


##################################################################
################## Geoprocessing happens here ####################
##################################################################

# make list of feature classes, sort alphabetically, and display
fcList = arcpy.ListFeatureClasses()
fcList.sort()
if w_space.endswith('.gdb'):
    present_datatype(fcList, 'Feature classes', doc)
else:
    present_datatype_folder(fcList, 'Shapefiles', doc)

# make a list of raster datasets, sort alphabetically, and display
rdList = arcpy.ListRasters()
rdList.sort()
if w_space.endswith('.gdb'):
    present_datatype(rdList, 'Raster datasets', doc)
else:
    present_datatype_folder(rdList, 'Raster datasets', doc)

# make a list of tables, sort alphabetically, and display
tableList = list(set(arcpy.ListTables()) - (set(arcpy.ListTables('*.txt'))))
tableList.sort()
if w_space.endswith('.gdb'):
    present_datatype(tableList, 'Standalone tables', doc)
else:
    present_datatype_folder(tableList, 'Standalone tables', doc)


########### These processes are only for geodatabases ############

# make a list of relationship classes, sort alphabetically, and display
rs_clList = arcpy.da.Walk(w_space, datatype='RelationshipClass')
rs_clList2 = []
for ob in rs_clList:
    for o in ob[2]:
        rs_clList2.append(o)
if w_space.endswith('.gdb'):
    present_datatype(rs_clList2, 'Relationship classes', doc)
else:
    print()
    #present_datatype_folder(rs_clList2, 'Relationship classes', doc)

# mosaic datasets in gdb
if w_space.endswith('.gdb'):
    var_dataList = arcpy.da.Walk(w_space, True, None, True, datatype=['MosaicDataset'])
    if var_dataList != None:
        display('Mosaic datasets:', doc)
        for x in var_dataList:
            if x[0] == w_space:
                new_list = []
                for y in x[2]:
                    new_list.append(w_space + '\\' + y)
                for y in new_list:
                    result = arcpy.GetCount_management(y)
                    display('  ' + ntpath.basename(y) + ' (# of rasters: ' + str(result[0]) + ')', doc)
                    #display('  ' + ntpath.basename(y) + ' (# of rasters: ' + str(number_of_records(y)) + ')', doc)
        display('', doc)
        display('***', doc)
        display('', doc)
else:
    print()

# make a list of feature datasets, as well as their content (indented), sort alphabetically, and display
# networks, parcel fabrics, schematic, terrains, tin, topology
dataset_List = arcpy.ListDatasets(feature_type='feature')
dataset_List.sort()
if w_space.endswith('.gdb'):
    present_datatype(dataset_List, 'Feature datasets', doc)
else:
    print()


############ The following mostly applies to folders #############

# If the workspace is a folder, list:
# List
w_space_within_List = list(set(arcpy.ListWorkspaces('*', 'Access')) | set(arcpy.ListWorkspaces('*', 'FileGDB')) | set(arcpy.ListWorkspaces('*', 'Folder')))
w_space_within_List.sort()
lyr_list = list(set(arcpy.ListFiles('*.lyr')) | set(arcpy.ListFiles('*.lyrx')))
lyr_list.sort()
map_list = list(set(arcpy.ListFiles('*.mxd')) | set(arcpy.ListFiles('*.aprx')))
map_list.sort()
pdf_list = list(set(arcpy.ListFiles('*.pdf')))
pdf_list.sort()
dwg_list = list(set(arcpy.ListFiles('*.dwg')))
dwg_list.sort()
kml_list = list(set(arcpy.ListFiles('*.kml')) | set(arcpy.ListFiles('*.kmz')))
kml_list.sort()
tbx_list = list(set(arcpy.ListFiles('*.tbx')))
tbx_list.sort()

# This process is for various GIS-y files in a folder. Does not run on a geodatabase
w_space_desc = arcpy.Describe(w_space)
if w_space_desc.workspaceType == 'FileSystem':
    present_datatype_folder(w_space_within_List, 'Folders and geodatabases (you can document GIS data in these workspaces too)', doc)
    present_datatype_folder(lyr_list, 'Layer files', doc)
    present_datatype_folder(map_list, 'ArcGIS Desktop map files and projects', doc)
    present_datatype_folder(pdf_list, 'Adobe PDFs', doc)
    present_datatype_folder(dwg_list, 'AutoDesk CAD drawing files', doc)
    present_datatype_folder(kml_list, 'Google Earth zipped KML files', doc)
    present_datatype_folder(tbx_list, 'Toolboxes', doc)
    # Make previous lists compatable for the present 'all other files' command
    basenameList_to_filenameList(rdList, w_space)
    basenameList_to_filenameList(tableList, w_space)
    basenameList_to_filenameList(w_space_within_List, w_space)
    basenameList_to_filenameList(lyr_list, w_space)
    basenameList_to_filenameList(map_list, w_space)
    basenameList_to_filenameList(pdf_list, w_space)
    basenameList_to_filenameList(dwg_list, w_space)
    basenameList_to_filenameList(kml_list, w_space)
    basenameList_to_filenameList(tbx_list, w_space)

# Make a list of all other files, sort alphabetically, and display
# This excludes necessary geodatabase files, such as a000000* files,
# gdb, timestamps and currently open-and-locked GIS files

if w_space.endswith('.gdb') or w_space.endswith('.mdb'):
    # geodatabases
    fileList = list(set(arcpy.ListFiles()) - set(arcpy.ListFiles('a000*')) - set(arcpy.ListFiles('timestamps')) - set(arcpy.ListFiles('gdb')) - set(arcpy.ListFiles('*.lock')))
    present_datatype(fileList, 'All other files', doc)
else:
    # folders
    fileList = list(set(arcpy.ListFiles()) - set(arcpy.ListFiles('*.shp')) - set(rdList) - set(tableList) - set(arcpy.ListFiles('*.gdb')) - set(lyr_list) - set(map_list) - set(pdf_list) - set(dwg_list) - set(kml_list) - set(tbx_list))
    fileList.sort()
    present_datatype_folder(fileList, 'All other files', doc)

# List the domains in a geodatabase
arcpy.AddMessage(w_space)
if w_space.endswith('.gdb'):
    domains(w_space)


##################################################################
################## All done! Now time to close ###################
##################################################################

# Close for file writing
if arcpy.GetParameterAsText(1) != None:
    doc.close()

# Open file in notepad B)
if arcpy.GetParameterAsText(1) != None:
    os.system('start notepad.exe ' + doc_text)
