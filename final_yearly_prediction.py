#We are taking prediction results of a district, taken at different point of time (different months within a year). We are going to combine all prediction results to make a final prediction for that year.

# import all required packages
from PIL import Image
import math
from PIL import Image
from scipy import misc
from scipy import ndimage
import pandas as pd
import unittest
import os, sys
import shutil #for copying files
import numpy as np


'''
Change districts, and years accordingly
''' 
districts = ['Bangalore','Chennai','Delhi','Gurgaon','Hyderabad','Kolkata','Mumbai']
years=['2016','2017','2018','2019']


'''
Covert monthly predictions from .tif to .png
'''
for district in districts:
    main_folder = 'Classification_'+district     #we have stored monthly predections in a folder named by district name
    print(district)
    os.makedirs(main_folder+"/pngs",exist_ok=True)
    for infile in os.listdir(main_folder):
        if infile[-4:] == ".tif":                   #reading all tif files in given folder
            im = Image.open(main_folder+"/"+infile)
            im.save(main_folder+"/pngs/"+infile[:-4]+'.png')


# Defining all required functions
'''
Rule-based post-classification correction

merge the monthly predictions and overall median prediction to get a single prediction for year
Pixel value 0 denotes Background, 1 denotes greenery, 2 denotes water, 3 benotes Built-Up, 4 denotes Barren land
Input-
1) monthly_pixel_predictions = list of predicted value of a particular pixel in the best 5 months of a particular year
2) median_pixel_prediction = predicted value of the above pixel over the year median image
'''  
def merge_prediction(monthly_pixel_predictions, median_pixel_prediction):    
    total_predictions = len(monthly_pixel_predictions)
    
    #find the count of each kind of pixel value for a pixel across all the given years
    background_count = monthly_pixel_predictions.count(0)
    green_count = monthly_pixel_predictions.count(1)
    water_count = monthly_pixel_predictions.count(2)
    builtup_count = monthly_pixel_predictions.count(3)
    barrenland_count = monthly_pixel_predictions.count(4)
    
    #Applying different rules for post-classification error correction
    
    # Rule1: If pixel is predicted as background in all 5 months, consider it background for the entire year
    if (background_count == total_predictions):
        return '0'
    
    # Rule2: If pixel is predicted as water more times than green in 5 months, consider it water for the entire year
    elif (water_count > 0 and green_count > 0 and water_count > 2 * green_count):
        return '2'
    
    # Rule3: If pixel is predicted as water more than 50% times, consider it water for the entire year
    elif (water_count >= 0.5 * total_predictions):
        return '2'
    
    # Rule4: If pixel is predicted as green more times than water in 5 months, consider it green for the entire year
    elif (water_count>0 and green_count>0 and water_count <= 2 * green_count ):
        return '1'
    
    # Rule5: This rule helps to eliminate shadows which are mis-interpreted as water
    elif (water_count != 0 and green_count == 0 ):
        return str(median_pixel_prediction)
    
    # Rule6: After identifying water, if a pixel is predicted as green atleast once, consider it green for the entire year
    elif ( green_count >=1 ):
        return '1'
    
    # Rule7: If a pixel is neither green nor water, then it is barrenland or builtup as per majority for the entire year
    elif((barrenland_count > builtup_count) and green_count==0 and water_count==0 ):
        return '4'
    
    # Rule8: If a pixel is neither green nor water, then it is barrenland or builtup as per majority for the entire year
    else:
        return '3'
    
'''
This function is used to find a future year whose image can be used to replicate a bad year with no good monthly images
Input:
a) bad_index- index of a year which needs replication
b) years- list of available years under analysis
c) replication_required_years- list of corrupt years for a district

Output: target year whose image can be replicated to cover bad year. It is 0 when no such year is available   
'''
def find_non_corrupt_forward(bad_index, years, replication_required_years):
    for k in range( bad_index+1, len(years) ):
        if years[k] not in replication_required_years:
            return years[k]
    return 0 

'''
This function is used to find a past year whose image can be used to replicate a bad year with no good monthly images
Input:
a) bad_index- index of a year which needs replication
b) years- list of available years under analysis
c) replication_required_years- list of corrupt years for a district

Output: target year whose image can be replicated to cover bad year. It is 0 when no such year is available
'''
def find_non_corrupt_backward(bad_index, years, replication_required_years):
    for k in range( bad_index-1, -1, -1 ):
        if years[k] not in replication_required_years:
            return years[k]
    return 0


'''
Read all the different predictions of a district. 
Out of the 12 months for each year, we see which months have the maximum number of green pixels (Assuming them to be most accurate). 
The top 5 months are chosen to create the final pixel-level predictions for each year.
'''
for district in districts:
    print(district)
    main_folder = 'Classification_'+district     #we have downloaded monthly predections in a folder named by district name from google drive
    os.makedirs(main_folder+"/final",exist_ok=True)
    replication_required_years = [] #List of years for which this district cannot do month-wise correction due to bad satellite images
    for year in years:
        print(year)
        
        #Find the minimum number of background pixels in the images of all months for this year
        dataset = [ np.asarray(Image.open(main_folder+"/pngs/"+infile)) for infile in os.listdir(main_folder+"/pngs/") ]
        backgroundPixels = [ np.unique(dataset[k],return_counts=True)[1][0] for k in range(len(dataset)) ]      
        min_background_count = min(backgroundPixels) #All complete images of this district will have this number of background pixels only
        
        Green_pixs = []  #This list will store the key-value pairs where key=month and value=(#green pixels, #builtup pixels) predicted in that month   
        
        for infile in os.listdir(main_folder+"/pngs/"):
            if 'Classification_'+district in infile and year in infile and 'median' not in infile: #reading all monthly predictions
                im = np.asarray(Image.open(main_folder+"/pngs/"+infile))
                if np.unique(im,return_counts=True)[1][0] > min_background_count:
                    # Check that the if background pixels are increased by atmost 5%, include those months 
                    if ((np.unique(im,return_counts=True)[1][0] - min_background_count)/min_background_count) <= 0.05 :
                        month = infile[-6:-4]
                        Green_pixs.append((month, ( np.unique(im,return_counts=True)[1][1] , np.unique(im,return_counts=True)[1][3])))

                else:
                    month = infile[-6:-4]
                    Green_pixs.append((month, ( np.unique(im,return_counts=True)[1][1] , np.unique(im,return_counts=True)[1][3])))
            
            # find the builtup threshold on the year median image
            elif 'Classification_'+district in infile and year in infile and 'median' in infile:
                im = np.asarray(Image.open(main_folder+"/pngs/"+infile))
                BU_threshold = np.unique(im,return_counts=True)[1][3]
                
        Green_pixs.sort(key=lambda x:x[1],reverse=True) #sort the dictionary by values of #green pixels         
        print("Number of months available after filtering on background pixels: ",len(Green_pixs))
        
        #Filter on the basis of tolerance against increase in builtup pixels i.e increase/decrease by atmost 150%                
        for entry in Green_pixs:
            if abs(entry[1][1] - BU_threshold)/BU_threshold > 1.5:
                Green_pixs.remove(entry)
                
        print("Number of months available after filtering on BU pixels: ",len(Green_pixs))
        
        best_months = [Green_pixs[i][0] for i in range(min(5,len(Green_pixs)))] #taking best 5 months on the basis of greenery
        
        
        if not len(best_months) < 3:             
            print("The best months (max 5 and min 3) of this year are: ",best_months)

            best_month_paths = [main_folder+'/pngs/Classification_'+district+'_'+year+'_30mtr_'+best_month+'.png' for best_month in best_months]
            best_predictions = [np.asarray(Image.open(best_month_path)) for best_month_path in best_month_paths]

            year_median_path = main_folder+'/pngs/'+'Classification_'+district+'_'+year+'_30mtr_year_median.png'
            year_median_prediction = np.asarray(Image.open(year_median_path))

            image_dimension = best_predictions[0].shape
            #print(image_dimension)

            #Initializing the final prediction matrix for a particular year
            final_prediction = np.zeros(image_dimension[0] * image_dimension[1]).reshape(image_dimension)
            #print(final_prediction)

            for i in range(image_dimension[0]):
                for j in range(image_dimension[1]):
                    x = [ best_predictions[k][i][j] for k in range(len(best_predictions)) ]
                    final_prediction[i,j] = merge_prediction(x, year_median_prediction[i][j])

            print("final_prediction ",np.unique(final_prediction,return_counts=True))

            final_prediction = (Image.fromarray(final_prediction)).convert("L")
            final_prediction.save(main_folder+'/final/'+district+'_prediction_'+year+'.png')
        
        else: #If we did not get atleast 3 best months for this year
            replication_required_years.append(year)
    
    print("Years that require replication for distirct ",district," are: ",replication_required_years)
    for year in years:
        if year in replication_required_years:
            bad_index = years.index(year)
            if(bad_index == 0 or bad_index == 1):
                target_year = find_non_corrupt_forward(bad_index, years, replication_required_years)
            elif(bad_index == len(years)-1 or bad_index == len(years)-2):
                target_year = find_non_corrupt_backward(bad_index, years, replication_required_years)
            else:
                target_year = find_non_corrupt_forward(bad_index, years, replication_required_years)
            
            if(target_year == 0): #no replication found
                print("Error! No way for replication. Discard district ",district," from analysis")
            else:
                copy = Image.open(main_folder+'/final/'+district+'_prediction_'+target_year+'.png')
                copy.save(main_folder+'/final/'+district+'_prediction_'+year+'.png')
        
print("Done!")


'''
Color coding the final prediction maps for a particular year. Uptill here the pixel values contain greyscale values. For easier visualization, we assign intuitive colors to different land-cover classes. These images will be stored at final/Color_coded_final_predictions subfolder for each district 
'''
for district in districts:
    print(district)
    main_folder = 'Classification_'+district+"/final"     #we have downloaded monthly predections in a folder named by district name from google drive
    os.makedirs(main_folder+"/Color_coded_final_predictions",exist_ok=True)
    for year in years:
        image_path = main_folder+'/'+district+'_prediction_'+year+'.png'  
        img = Image.open(image_path)
        img = img.convert("RGBA")
        pixdata = img.load()
        #print(img.getcolors()) #use this command to visualize already assigned colors to each label
        
        for y in range(img.size[1]):
            for x in range(img.size[0]):
                if pixdata[x, y] == (0, 0, 0, 255):      # background 
                    pixdata[x, y] = (0,0,0,0)            # black color
                elif pixdata[x, y] == (1, 1, 1, 255):    # green
                    pixdata[x, y] = (34,139,34, 255)     # green color
                elif pixdata[x, y] == (2, 2, 2, 255):    # water
                    pixdata[x, y] = (2, 4, 251, 255)     # blue color
                elif pixdata[x, y] == (3, 3, 3, 255):    # built-up 
                    pixdata[x, y] = (255, 255, 102, 255) # yellow color
                elif pixdata[x, y] == (4, 4, 4, 255):    # bareland
                    pixdata[x, y] = (255, 80, 80, 255)   # red color

        img.save(main_folder+"/Color_coded_final_predictions/"+district+'_colored_prediction_'+year+'.png')
print("Done")





