
from osgeo import gdal




def calculation(file_name, factor, directory):
    ds = gdal.Open(file_name)
    ds_band = ds.GetRasterBand(1)

    #----------------------------------------------------
    pixel_values = ds.ReadAsArray()
    #----------Reduction factor----------------

    pixel_values_modified = pixel_values/ float(factor)
    indicator = pixel_values_modified.sum()
    gtiff_driver = gdal.GetDriverByName('GTiff')
    #print ()
    out_ds = gtiff_driver.Create(directory, ds_band.XSize, ds_band.YSize, 1, ds_band.DataType)
    out_ds.SetProjection(ds.GetProjection())
    out_ds.SetGeoTransform(ds.GetGeoTransform())

    out_ds_band = out_ds.GetRasterBand(1)
    out_ds_band.SetNoDataValue(0)
    out_ds_band.WriteArray(pixel_values_modified)

    del out_ds
    return indicator