import os, sys
from PIL import Image
import numpy as np


# specifying integer code of land cover classes
green = 1
water = 2
builtup = 3
barrenland = 4

'''
This function is used to calculate the precision of each landcover class from confusion matrix
'''
def precision(label, confusion_matrix):
    col = confusion_matrix[:, label]
    return confusion_matrix[label, label] / col.sum()
   
'''
This function is used to calculate the recall value of each landcover class from confusion matrix
'''
def recall(label, confusion_matrix):
    row = confusion_matrix[label, :]
    return confusion_matrix[label, label] / row.sum()

'''
This function is used to calculate the overall accuracy of land cover classification in a district
'''
def accuracy(confusion_matrix):
    diagonal_sum = confusion_matrix.trace()
    sum_of_all_elements = confusion_matrix.sum()
    return diagonal_sum / sum_of_all_elements 


'''
Driver code begins here
'''
# list of districts for which the accuracy is to be calculated
districts = ['Gurgaon','Hyderabad','Mumbai']

# Name of the main folder where the cropped tif files of predictions are stored
main_folder = 'Classification_Accuracy_Test'

landcover_classes = ['Green','Water','Builtup','Barrenland']
for district in districts:
    confusion_matrix = [] # this is the confusion matrix against each district

    for landcover in landcover_classes:
        landcover_predicted_class_count = [0, 0, 0, 0] # this list stores the count of a particular class predicted as other classes 
        tif_files_path = main_folder+'/'+district+'/'+landcover        
        
        for tif_file in os.listdir(tif_files_path):
            tif_image = np.asarray(Image.open(tif_files_path+'/'+tif_file))
            
            if green in np.unique(tif_image, return_counts=True)[0]:
                landcover_predicted_class_count[0] += np.unique(tif_image, return_counts=True)[1][np.where(np.unique(tif_image,return_counts=True)[0]==green)[0][0]]
            
            if water in np.unique(tif_image, return_counts=True)[0]:
                landcover_predicted_class_count[1] += np.unique(tif_image, return_counts=True)[1][np.where(np.unique(tif_image,return_counts=True)[0]==water)[0][0]]
                
            if builtup in np.unique(tif_image, return_counts=True)[0]:
                landcover_predicted_class_count[2] += np.unique(tif_image, return_counts=True)[1][np.where(np.unique(tif_image,return_counts=True)[0]==builtup)[0][0]]
                
            if barrenland in np.unique(tif_image, return_counts=True)[0]:
                landcover_predicted_class_count[3] += np.unique(tif_image, return_counts=True)[1][np.where(np.unique(tif_image,return_counts=True)[0]==barrenland)[0][0]]
                
        confusion_matrix.append(landcover_predicted_class_count)
    
    confusion_matrix = np.array(confusion_matrix)
    print("Confusion Matrix for district ",district,"is: \n",confusion_matrix,"\n")
    
    print("Accuracy: ",accuracy(confusion_matrix),"\n")
    print("label precision recall")
    for label in range(4):
        print(f"{label+1:5d} {precision(label, confusion_matrix):9.3f} {recall(label, confusion_matrix):6.3f}")
    print("\n\n")





