


def generate_output_file_tif(output_directory):
    return generate_output_file_with_extension(output_directory,'.tif')


def generate_output_file_with_extension(output_directory,extension):
    filename = str(uuid.uuid4()) + extension
    output_raster_path = output_directory+'/'+filename  # output raster
    return output_raster_path