# Import libraries
import arcpy, os
from arcgis.gis import GIS
import openpyxl             # Working on this one

# Set CWD and desktop GIS workspace
arcpy.env.workspace = r'U:\Departments\LiDAR-GIS\Python_File_Templates\AGOL_updates_template' \
                      r'\acquisition_update_template\acquisition_update_template.gdb'
os.chdir(r'U:\Departments\LiDAR-GIS\Python_File_Templates\AGOL_updates_template')

# Identify desktop GIS files, join field
# This is where you modify most of your work for each individual project
xlsx_file = r'U:\Departments\LiDAR-GIS\Python_File_Templates\AGOL_updates_template\data_template.xlsx'
aprx_file = r'U:\Departments\LiDAR-GIS\Python_File_Templates\AGOL_updates_template\acquisition_update_template' \
            r'\acquisition_update_template.aprx'
polyg_file = r'U:\Departments\LiDAR-GIS\Python_File_Templates\AGOL_updates_template\acquisition_update_template' \
             r'\acquisition_update_template.gdb\Ownerships'
csv_path = r'U:\Departments\LiDAR-GIS\Python_File_Templates\AGOL_updates_template\temp.csv'
# Join field assumes both tables use the exact same name for their join fields.
# Otherwise, a change has to be made in the gis layer, excel spreadsheet, or this script.
join_field = 'ID'

# ArcGIS Online variables
sd_fs_name = "Acquisition Template"
portal = 'https://meiamerica.maps.arcgis.com/'
user = "chigham_mei"
password = "Kingchr23!"
shrOrg = True
shrEveryone = True
shrGroups = ""
# Local paths to create temporary content
relPath = os.path.dirname(aprx_file)
sddraft = os.path.join(relPath, "WebUpdate.sddraft")
sd = os.path.join(relPath, "WebUpdate.sd")
print('\n' + 'Copy table data to GIS data')

# Function for updating fields in GIS
def update_field(polyg_file, updateFld, IdFld, csv_path, joinValFld, joinIdFld):
    valueDi = dict([(key, val) for key, val in arcpy.da.SearchCursor(csv_path, [joinIdFld, joinValFld])])
    with arcpy.da.UpdateCursor(polyg_file, [updateFld, IdFld]) as cursor:
        for update, key in cursor:
            # skip if key value is not in dictionary
            if not key in valueDi:
                continue
            row = (valueDi[key], key)  # create row tuple
            cursor.updateRow(row) #update row
    del cursor

# Function for reading xlsx file in a new dataframe
def xlsx(fname):
    import zipfile
    from xml.etree.ElementTree import iterparse
    z = zipfile.ZipFile(fname)
    strings = [el.text for e, el in iterparse(z.open('xl/sharedStrings.xml')) if el.tag.endswith('}t')]
    rows = []
    row = {}
    value = ''
    for e, el in iterparse(z.open('xl/worksheets/sheet1.xml')):
        if el.tag.endswith('}v'):  # <v>84</v>
            value = el.text
        if el.tag.endswith('}c'):  # <c r="A3" t="s"><v>84</v></c>
            if el.attrib.get('t') == 's':
                value = strings[int(value)]
            letter = el.attrib['r'] # AZ22
            while letter[-1].isdigit():
                letter = letter[:-1]
            row[letter] = value
            value = ''
        if el.tag.endswith('}row'):
            rows.append(row)
            row = {}
    return rows

# Convert excel file to a csv
print('Reading excel spreadsheet as a CSV…')
xlsx_df = xlsx(xlsx_file)
csv_rows = []
for a in xlsx_df:
    csv_rows.append('{},{},{},{}'.format(a['A'],a['B'],a['C'],a['D']))
for b in csv_rows:
    continue
csv_file = open('temp.csv', 'w')
for row in csv_rows:
    csv_file.writelines(row + '\n')
csv_file.close()
print('CSV join table created')

# Identify fields to update
first_list = arcpy.ListFields(csv_path)
field_list = []
for field in first_list:
    field_list.append(field.name)

# Apply updates to file GIS layer using update function
# For all fields
print('Updating file geodatabase…')
for f in field_list:
    update_field(polyg_file, f, join_field, csv_path, f, join_field)
print('File geodatabase updated')

## ArcGIS Online component ##
print("\n" + "Publish to ArcGIS Online...")

# Create a new SDDraft and stage to SD
print("Creating SD file")
arcpy.env.overwriteOutput = True
prj = arcpy.mp.ArcGISProject(aprx_file)
mp = prj.listMaps()[0]
arcpy.mp.CreateWebLayerSDDraft(mp, sddraft, sd_fs_name, 'MY_HOSTED_SERVICES', 'FEATURE_ACCESS','', True, True)
arcpy.StageService_server(sddraft, sd)
print("Connecting to {}".format(portal))
gis = GIS(portal, user, password)

# Find the SD, update it, publish /w overwrite and set sharing and metadata
print("Search for original SD on portal…")
sdItem = gis.content.search("{} AND owner:{}".format(sd_fs_name, user), item_type="Service Definition")[0]
print("Found SD: {}, ID: {} n Uploading and overwriting…".format(sdItem.title, sdItem.id))
sdItem.update(data=sd)

# Overwrite web layer
print("Overwriting existing feature service…")
fs = sdItem.publish(overwrite=True)
if shrOrg or shrEveryone or shrGroups:
    print("Setting sharing options…")
    fs.share(org=shrOrg, everyone=shrEveryone, groups=shrGroups)
print("Finished updating: {} – ID: {}".format(fs.title, fs.id))

# Delete any temporary files
print('\n' + 'Clearing unnecessary data files…')
os.remove(csv_path)
os.remove(sddraft)
os.remove(sd)
print('Data cleanup complete')
