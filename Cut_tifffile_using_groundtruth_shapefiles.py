import json
import sys
import rasterio
from rasterio.mask import mask
from json import loads
import sys
import os
from os import listdir
from os.path import isfile, join
from tqdm import tqdm


'''
The ground truth is manually created for 3 districts for the year 2018
'''
districts = ['Gurgaon','Hyderabad','Mumbai']

for district in districts:
    print(district)
    
    folder_containing_tifffiles = "Landcover_Predictions_Using_IndiaSat/"+district+"/tifs"
    tiff_file_name = district+'_prediction_2018.tif'
    
    
    folder_containing_groundtruth_shapefiles = 'groundtruth_shapefiles/'+district+'_groundtruth_shapes'

    for shapefile in listdir(folder_containing_groundtruth_shapefiles):
        if shapefile[-4:] == 'json':
            json_data = json.loads(open(folder_containing_groundtruth_shapefiles+'/'+shapefile).read())
            
            output_directory = 'Classification_Accuracy_Test/'+district+'/'+shapefile[:-5]
            if not os.path.exists(output_directory):
                os.makedirs(output_directory)
            i = 0            
            for currFeature in json_data["features"]:
                i += 1
                try:
                    geoms = [currFeature["geometry"]]

                    with rasterio.open(folder_containing_tifffiles+'/'+tiff_file_name) as src:
                        out_image, out_transform = mask(src, geoms, crop = True)
                        out_meta = src.meta

                        # save the resulting raster
                        out_meta.update({ "driver": "GTiff", "height": out_image.shape[1], "width": out_image.shape[2], "transform": out_transform})

                        saveFileName = output_directory+"/"+str(i)+".tif"
                        with rasterio.open(saveFileName, "w", **out_meta) as dest:
                            dest.write(out_image)
                except:
                    continue
                           
print('done')    





