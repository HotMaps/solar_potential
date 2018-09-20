
from osgeo import gdal
import uuid
from ..helper import generate_output_file_tif
""" Entry point of the calculation module function"""

#TODO: CM provider must "change this code"
#TODO: CM provider must "not change input_raster_selection,output_raster  1 raster input => 1 raster output"
#TODO: CM provider can "add all the parameters he needs to run his CM
#TODO: CM provider can "return as many indicators as he wants"
def calculation(output_directory, inputs_raster_selection, inputs_parameter_selection):
    #TODO the folowing code must be changed by the code of the calculation module

    # generate the output raster file
    output_raster1 = generate_output_file_tif(output_directory)

     #retrieve the inputs layes
    input_raster_selection =  inputs_raster_selection["heat_tot_curr_density"]
    #retrieve the inputs all input defined in the signature
    factor =  int(inputs_parameter_selection["reduction_factor"])


    # TODO this part bellow must be change by the CM provider
    ds = gdal.Open(input_raster_selection)
    ds_band = ds.GetRasterBand(1)

    #----------------------------------------------------
    pixel_values = ds.ReadAsArray()
    #----------Reduction factor----------------

    pixel_values_modified = pixel_values/ float(factor)
    hdm_sum  = pixel_values_modified.sum()

    gtiff_driver = gdal.GetDriverByName('GTiff')
    #print ()
    out_ds = gtiff_driver.Create(output_raster1, ds_band.XSize, ds_band.YSize, 1, gdal.GDT_UInt16, ['compress=DEFLATE',
                                                                                                         'TILED=YES',
                                                                                                         'TFW=YES',
                                                                                                         'ZLEVEL=9',
                                                                                                         'PREDICTOR=1'])
    out_ds.SetProjection(ds.GetProjection())
    out_ds.SetGeoTransform(ds.GetGeoTransform())

    ct = gdal.ColorTable()
    ct.SetColorEntry(0, (0,0,0,255))
    ct.SetColorEntry(1, (110,220,110,255))
    out_ds.GetRasterBand(1).SetColorTable(ct)

    out_ds_band = out_ds.GetRasterBand(1)
    out_ds_band.SetNoDataValue(0)
    out_ds_band.WriteArray(pixel_values_modified)

    del out_ds
    # output geneneration of the output
    graphics = []
    vector_layers = []
    result = dict()
    result['name'] = 'CM Heat density divider'
    result['indicator'] = [{"unit": "KWh", "name": "Heat density total divided by  {}".format(factor),"value": str(hdm_sum)}]
    result['graphics'] = graphics
    result['vector_layers'] = vector_layers
    result['raster_layers'] = [{"name": "layers of heat_densiy {}".format(factor),"path": output_raster1} ]
    return result


def colorizeMyOutputRaster(out_ds):
    ct = gdal.ColorTable()
    ct.SetColorEntry(0, (0,0,0,255))
    ct.SetColorEntry(1, (110,220,110,255))
    out_ds.SetColorTable(ct)
    return out_ds
