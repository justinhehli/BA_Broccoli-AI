#%%
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
    croppedMaskedImage = rasterio.mask.mask(src, [geoJsonObject], crop=True, nodata=-1000.)
    croppedMaskedImage[0][0][croppedMaskedImage[0][0] == -1000] = 'nan'

#%%
# create 8 bit array for segmentation
maskedImage_8bit = croppedMaskedImage[0][0]
maskedImage_8bit = maskedImage_8bit * 255
maskedImage_8bit = maskedImage_8bit.astype('uint8')

#%%
# Test Segmentation with simple threshold
# The only segmentation that can be done with 32 bit float values
simple_Segmentation_arr = SimpleThresholdSegmentation.simple_threshold(croppedMaskedImage[0][0])
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
pyplot.imshow(growing_seed_Threshold_arr)
pyplot.show()