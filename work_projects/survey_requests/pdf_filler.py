#
# Fill values in a pdf form (survey requests) #
#
#########################################################################################

import pdfrw, os, arcpy
from reportlab.pdfgen import canvas

def create_overlay(a, b, cc, d, e, f, g, h, i, j, k, oly_bn):       # Create the data that will be overlayed on top of the form that we want to fill
    # This needs to be heavily customized
    c = canvas.Canvas(oly_bn)
    #c.drawString(115, 650, str(a))
    #c.drawString(115, 600, str(b))
    #c.drawString(115, 550, str(cc))
    #c.drawString(115, 500, str(d))
    #c.drawString(355, 500, str(e))
    #c.drawString(115, 450, str(f))
    c.drawString(255, 661, str(a))
    c.drawString(255, 642, str(b))
    c.drawString(255, 623, str(cc))
    c.drawString(255, 604, str(d))
    c.drawString(255, 585, str(e))
    c.drawString(255, 566, str(f))
    if g != None:
        c.drawString(152, 527, 'X')
    if str(h) == 'Yes':
        c.drawString(335, 527, 'X')
    if str(i) == 'Yes':
        c.drawString(491, 527, 'X')
    if j != None:
        print_list = ['']
        j_list = j.split(' ')
        ii = 0
        for item in j_list:
            if len(list(print_list[ii])) < 74:
                print_list[ii] += (' ' + item)
            else:
                ii += 1
                print_list.append([''])
                print_list[ii] += (' ' + item)
        ii = 0
        for item in print_list:
            item_modified = ''
            for char in item:
                item_modified += char
            item = item_modified
            c.drawString(116, 450 - ii, str(item))
            ii += 18
    if k != None:                       # CHANGE TO K !!!
        print_list = ['']
        k_list = k.split(' ')
        ii = 0
        for item in k_list:
            if len(list(print_list[ii])) < 74:
                print_list[ii] += (' ' + item)
            else:
                ii += 1
                print_list.append([''])
                print_list[ii] += (' ' + item)
        ii = 0
        for item in print_list:
            item_modified = ''
            for char in item:
                item_modified += char
            item = item_modified
            c.drawString(116, 229 - ii, str(item))
            ii += 18
        #c.drawString(116, 229, str(k))  # CHANGE TO K !!!

    c.save()


def merge_pdfs(form_pdf, overlay_pdf, output):      # Merge the specified fillable form PDF with the overlay PDF and save the output
    form = pdfrw.PdfReader(form_pdf)
    olay = pdfrw.PdfReader(overlay_pdf)

    for form_page, overlay_page in zip(form.pages, olay.pages):
        merge_obj = pdfrw.PageMerge()
        overlay = merge_obj.add(overlay_page)[0]
        pdfrw.PageMerge(form_page).add(overlay).render()

    writer = pdfrw.PdfWriter()
    writer.write(output, form)

column_list = ['ProjectNumber', 'ProjectName', 'ProjectManager', 'DateRequired', 'EstimatedHours', 'TaskCode', 'AttachedScope', 'SitePhotos', 'Inverts', 'AddSurveyInstruct', 'Comments']
cursor = arcpy.da.SearchCursor('https://services5.arcgis.com/mvnrDxfOCq0CsVom/arcgis/rest/services/Survey_Requests/FeatureServer/0', column_list)

a = None
b = None
cc = None
d = None
e = None
f = None
g = None
h = None
i = None
j = None
k = None
form_template = r'U:\Departments\LiDAR-GIS\Python_File_Templates\Scripts\Specifics\survey_requests\_Template Survey - Request Form.pdf'
overlay_form = None
completed_form = None

for survey_request in cursor:
    a = cursor[0]
    b = cursor[1]
    cc = cursor[2]
    d = cursor[3]
    e = cursor[4]
    f = cursor[5]
    g = cursor[6]
    h = cursor[7]
    i = cursor[8]
    j = cursor[9]
    k = cursor[10]
    oly_basename = a + '_oly.pdf'
    final_basename = a + '.pdf'
    overlay_form = os.path.join('U:\Departments\LiDAR-GIS\Python_File_Templates\Scripts\Specifics\survey_requests', oly_basename)
    completed_form = os.path.join('U:\Departments\LiDAR-GIS\Python_File_Templates\Scripts\Specifics\survey_requests', final_basename)
    if __name__ == '__main__':
        create_overlay(a, b, cc, d, e, f, g, h, i, j, k, overlay_form)
        merge_pdfs(form_template, overlay_form, completed_form)
        os.remove(overlay_form)
