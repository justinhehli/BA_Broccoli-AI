#%%

import os
import sys

sys.path.append(os.getcwd() + '/SegmentationOfData')

import SimpleThresholdSegmentation
import rasterio
import rasterio.features
import rasterio.warp
import rasterio.drivers
import rasterio.mask
import matplotlib.pyplot as pyplot
import numpy
import numpy.ma as ma
import geojson
import shapefile
import pandas as pd
import SimpleITK as sitk


#%%
#Extract polygons from Voronoi Cells and convert into geojson
shape = shapefile.Reader("C:/DataAnalysis/SegmentationOfData/Voronoi/Voronoi.shp")
#first feature of the shapefile
feature = shape.shapeRecords()[0]
# geo interface of the shape
featureGeoInterface = feature.shape.__geo_interface__  
geoJsonString = geojson.dumps(featureGeoInterface, sort_keys=True)
geoJsonObject = geojson.loads(geoJsonString)

#%%
# mask and crop image
with rasterio.open('C:/DataAnalysis/SegmentationOfData/20190425MSC_index_ndvi_transformed.tif') as src:
    croppedMaskedImageNDVI = rasterio.mask.mask(src, [geoJsonObject], crop=True, nodata=-1000.)
    croppedMaskedImageNDVI[0][0][croppedMaskedImageNDVI[0][0] == -1000] = 'nan'

with rasterio.open('C:/DataAnalysis/SegmentationOfData/20190425MSC_index_ndre_transformed.tif') as src:
    croppedMaskedImageNDRE = rasterio.mask.mask(src, [geoJsonObject], crop=True, nodata=-1000.)
    croppedMaskedImageNDRE[0][0][croppedMaskedImageNDRE[0][0] == -1000] = 'nan'

#plot the figures
pyplot.figure()
pyplot.subplot(1,2,1)
pyplot.imshow(croppedMaskedImageNDVI[0][0])
pyplot.title('NDVI image')

pyplot.subplot(1,2,2)
pyplot.imshow(croppedMaskedImageNDRE[0][0])
pyplot.title('NDRE image')
pyplot.show()
#%%
# create 8 bit array for segmentation
maskedImage_8bit = croppedMaskedImageNDVI[0][0]
maskedImage_8bit = maskedImage_8bit * 255
maskedImage_8bit = maskedImage_8bit.astype('uint8')
pyplot.imshow(maskedImage_8bit)
pyplot.show()

#%%
# Test Segmentation with simple threshold
# The only segmentation that can be done with 32 bit float values
simple_Segmentation_arr = SimpleThresholdSegmentation.simple_threshold(croppedMaskedImageNDVI[0][0])
pyplot.imshow(simple_Segmentation_arr)
pyplot.show()
#%%
# Test Segmentation with adaptive threshold
adaptive_Threshold_arr_mean, adaptive_Threshold_arr_gauss = SimpleThresholdSegmentation.adaptive_threshold(maskedImage_8bit)
pyplot.imshow(adaptive_Threshold_arr_mean)
pyplot.show()
pyplot.imshow(adaptive_Threshold_arr_gauss)
pyplot.show()
#%%
# Test Segmentation with otsu threshold
otsu_Threshold_arr, otsu_Threshold_arr_blurr = SimpleThresholdSegmentation.otsu_threshold(maskedImage_8bit)
pyplot.imshow(otsu_Threshold_arr)
pyplot.show()
pyplot.imshow(otsu_Threshold_arr_blurr)
pyplot.show()

#%%
# Test Segmentation with grwoing seed
growing_seed_Threshold_arr = SimpleThresholdSegmentation.connectedSeedGrowing(maskedImage_8bit)
#plot the figures
pyplot.figure()
pyplot.subplot(1,3,1)
pyplot.imshow(croppedMaskedImageNDVI[0][0])
pyplot.title('NDVI image')

pyplot.subplot(1,3,2)
pyplot.imshow(croppedMaskedImageNDRE[0][0])
pyplot.title('NDRE image')

pyplot.subplot(1,3,3)
pyplot.imshow(growing_seed_Threshold_arr)
pyplot.title('Image Threshold')

pyplot.show()

#%%
# mask Array
maskedArray = growing_seed_Threshold_arr
maskedArray[maskedArray==1]=2
maskedArray[maskedArray==0]=1
maskedArray[maskedArray==2]=0
croppedMaskedImageNDVI_array= numpy.array(croppedMaskedImageNDVI[0][0])
croppedMaskedImageNDRE_array= numpy.array(croppedMaskedImageNDRE[0][0])
maskedArray_ndvi= ma.array(croppedMaskedImageNDVI_array, mask=maskedArray, copy=True)
maskedArray_ndre= ma.array(croppedMaskedImageNDRE_array, mask=maskedArray, copy=True)
#plot the figures

pyplot.figure()
pyplot.subplot(1,4,1)
pyplot.imshow(croppedMaskedImageNDVI[0][0])
pyplot.title('NDVI image')

pyplot.subplot(1,4,2)
pyplot.imshow(maskedArray_ndvi)
pyplot.title('Masked Image NDVI')

pyplot.subplot(1,4,3)
pyplot.imshow(croppedMaskedImageNDRE[0][0])
pyplot.title('NDRE image')

pyplot.subplot(1,4,4)
pyplot.imshow(maskedArray_ndre)
pyplot.title('Masked Image NDRE')


#%% 
# Get all interesting values

id = feature.record.id
latitude = feature.record.latitude
longitude = feature.record.latitude
pixelNumbers = maskedArray_ndvi.count()
minNDVIValue = ma.min(maskedArray_ndvi)
maxNDVIValue = ma.max(maskedArray_ndvi)
meanNDVIValue = ma.mean(maskedArray_ndvi)
medianNDVIValue = ma.median(maskedArray_ndvi)
minNDREValue = ma.min(maskedArray_ndre)
maxNDREValue = ma.max(maskedArray_ndre)
meanNDREValue = ma.mean(maskedArray_ndre)
medianNDREValue = ma.median(maskedArray_ndre)

