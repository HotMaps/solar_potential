import uuid
import ast
import json
import zipfile
import os

import shutil
from zipfile import ZipFile
from os import path

import zipfile
def generate_output_file_tif(output_directory):
    return generate_output_file_with_extension(output_directory,'.tif')

def generate_output_file_zip(output_directory):
    return generate_output_file_with_extension(output_directory,'.zip')
def generate_output_file_csv(output_directory):
    return generate_output_file_with_extension(output_directory, '.csv')

def generate_output_file_shp(output_directory):
    return generate_output_file_with_extension(output_directory, '.shp')


def generate_output_file_with_extension(output_directory,extension):
    filename = str(uuid.uuid4()) + extension
    output_raster_path = output_directory+'/'+filename  # output raster
    return output_raster_path

def validateJSON(value):
    #print (message + 'type', type(value))
    response = ast.literal_eval(json.dumps(value))

    return response

def create_zip_shapefiles(output_directory, shapefile):
    print ("shafefile",shapefile)
    os.chdir(output_directory)
    # determine file name
    import sys
    #modify the coding in fly for writing
    sys.getfilesystemencoding = lambda: 'UTF-8'
    filename = shapefile.replace(output_directory+'/', "")
    zip_file = filename.replace('.shp', '.zip')
    shp_file = filename
    dbf_file = filename.replace('.shp', '.dbf')
    prj_file = filename.replace('.shp', '.prj')
    shx_file = filename.replace('.shp', '.shx')
    zf = ZipFile(zip_file, 'w')
    try:
        zf.write(dbf_file)
        zf.write(prj_file)
        zf.write(shx_file)
        zf.write(shp_file)
    finally:
        zf.close()
    return zip_file



def generate_directory(tile_path):
    access_rights = 0o755
    print ('***********WILL gENERATE DIRECTORY AT {} *******************************',tile_path)

    try:
        os.mkdir(tile_path, access_rights)
    except OSError:
        print ("Creation of the directory %s failed" % tile_path)
    else:
        print ("Successfully created the directory %s" % tile_path)







