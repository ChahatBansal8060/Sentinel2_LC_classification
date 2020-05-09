from osgeo import gdal
import os, sys
import imageio
import numpy as np
from PIL import Image

# load GDAL (Geospatial Data Abstraction Library) driver for tiff files
driver = gdal.GetDriverByName('GTiff')

# districts for which ground truth is available
districts = ['Gurgaon','Hyderabad','Mumbai']

for district in districts:
    main_folder = 'Classification_'+district
    print(district)
    
    # Get one tif file of this district for reference. This can be the initial tif files downloaded from GEE 
    for infile in os.listdir(main_folder):
        if (infile[-4:] == ".tif"):
            filepath = main_folder+"/"+infile
            break
    
    reference_image = gdal.Open(filepath)
    
    #1 because we have information in a single band (prediction classes) 
    pixel_predictions = (reference_image.GetRasterBand(1)).ReadAsArray()
    [cols, rows] = pixel_predictions.shape
#     print("Rows: ",rows," Cols: ",cols)
            
    path_for_final_prediction_pngs = "Landcover_Predictions_Using_IndiaSat/"+district
    os.makedirs(path_for_final_prediction_pngs+'/tifs',exist_ok=True)
    
    for infile in os.listdir(path_for_final_prediction_pngs):
        if infile[-4:] == ".png":
            print(infile)
            
            pngImage = np.array( Image.open( path_for_final_prediction_pngs+'/'+infile ))
            print("The unique labels in png image are: ", np.unique(pngImage) )
            print("The shape of png image is: ", pngImage.shape )
            
            destination_filename = path_for_final_prediction_pngs+'/tifs/'+infile[:-4]+'.tif'
            
            #Setting the structure for the destination tif file
            dst_ds = driver.Create(destination_filename, rows, cols, 1, gdal.GDT_UInt16)
            dst_ds.SetGeoTransform(reference_image.GetGeoTransform())
            dst_ds.SetProjection(reference_image.GetProjection())
            dst_ds.GetRasterBand(1).WriteArray(pngImage)
            dst_ds.FlushCache()
            
            #Checking the validity of created tif file
            tiffImage = np.asarray( Image.open(destination_filename) )
            print("The unique labels in tiff image are: ", np.unique(tiffImage) )
            print("The shape of tiff image is: ", tiffImage.shape )
            print('\n')
            





