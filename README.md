
# IndiaSat: An open dataset for land-cover classification in India for Sentinel-2

## Project Overview
In this project, we have addressed various challenges in land cover classification, which includes seasonal effects and temporal inconsistencies in prediction results. For this task, we created a pixel level dataset for India with the help of OSM data. We have created State-of-the-art pixel-level training dataset of 3 lakh points (for 30-meter resolution) capturing vast variation of demography across India. This unique dataset is constructed using OSM and visual interpretation to classify pixels into four classes- green, water, barren land, and built-up. Further, we created a rule-based technique on our classifier prediction to remove season effects. The temporal correction was done to remove the problem of temporal inconsistencies across years. Both the datasets and associated scripts to run classifiers are made available for open use.

## Prerequisites
* Google Earth Engine(GEE) account to run the google earth engine scripts for downloading and images and running the classifier
* Following python libraries to run the python scripts
    * PIL (Pillow)
    * scipy
    * numpy
    * pandas
* QGIS and Google Earth Pro for visualization of results

## Dataset
The training dataset is in the folder named **IndiaSat_dataset.zip**.

## Shapefiles used as Google Earth Engine Assets
The following shapefiles were used to download the images, train the classifier and predict the landcover in various Indian districts.
* **India_Boundary.zip / India_Boundary.geojson** - Boundary for India.
* **india_district_boundaries.zip** - Boundaries for all Indian districts. 

## Scripts
A detailed step-wise description of the implementation is present in the wiki pages of this repository. The following scripts are used for the project in order of execution-
* **monthly_prediction.js** -  To obtain monthly classification results of a given area using GEE (Google Earth Engine).
* **final_yearly_prediction.ipynb** -  To calculate the final prediction (land-cover classes) of a given area using the monthly prediction results. 

## Contact
If you have problems, questions, ideas or suggestions, please contact us by posting to this mailing list-
* Chahat Bansal- chahat.bansal@cse.iitd.ac.in
* Hariom Ahlawat- hariomahlawat@gmail.com
* Mayank Jain- mayank19j@gmail.com





