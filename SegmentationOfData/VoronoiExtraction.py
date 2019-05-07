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
from IPython.display import display, Markdown


#%%
#Extract polygons from Voronoi Cells and convert into geojson
shape = shapefile.Reader("C:/DataAnalysis/SegmentationOfData/Voronoi/Voronoi.shp")
#first feature of the shapefile
features = shape.shapeRecords()

#open images
ndvi_src_string = r'C:\DataAnalysis\SegmentationOfData\export\20190501RMC_index_ndvi_modified.tif'
ndre_src_string = r'C:\DataAnalysis\SegmentationOfData\export\20190501RMC_index_ndre_modified.tif'
output_src_string = r'C:\DataAnalysis\SegmentationOfData\export'
image_dir = r'C:\DataAnalysis\SegmentationOfData\export\images'
timestamp = '2019-05-01'


ndvi_src = rasterio.open(ndvi_src_string)
ndre_src = rasterio.open(ndre_src_string)

if os.path.exists(image_dir) == False:
    os.mkdir(image_dir)
htmlFile = open(r"C:\DataAnalysis\SegmentationOfData\export\report.html","w")
htmlFile.writelines('<h1><strong>Segmentation and extraction of drone data</strong></h1>')
htmlFile.writelines('<h2><strong>Information:</strong></h2>\
    <p>NDVI file: {}</p>\
    <p>NDRE file: {}</p>\
    <p>Date of measurement: {} </p>'.format(ndvi_src_string, ndre_src_string, timestamp))
htmlFile.writelines('The following report shows the segmentation on all the broccolis with the help of the Voronoi \
    algorithm to encapsulate the broccoli and the growing seed algorithm to create a segmentation of the algorithm')

htmlFile.writelines('<h2>Broccoli analysis</h2>')

export_dataframe = pd.DataFrame()
count = 0
for feature in features:
    
    print("Brokkoli Nr. {}".format(count+1))
    # geo interface of the shape
    featureGeoInterface = feature.shape.__geo_interface__  
    geoJsonString = geojson.dumps(featureGeoInterface, sort_keys=True)
    geoJsonObject = geojson.loads(geoJsonString)

    # mask and crop image
    croppedMaskedImageNDVI = rasterio.mask.mask(ndvi_src, [geoJsonObject], crop=True, nodata=-1000.)
    croppedMaskedImageNDVI[0][0][croppedMaskedImageNDVI[0][0] == -1000] = numpy.nan
    croppedMaskedImageNDRE = rasterio.mask.mask(ndre_src, [geoJsonObject], crop=True, nodata=-1000.)
    croppedMaskedImageNDRE[0][0][croppedMaskedImageNDRE[0][0] == -1000] = numpy.nan

    # meta information
    id = feature.record.id
    latitude = feature.record.latitude
    longitude = feature.record.longitude

    htmlFile.writelines('<h3>Broccoli #{}</h3>'.format(id))

    htmlFile.writelines('<ul>\
            <li>id: {}</li>\
            <li>latitude: {}</li>\
            <li>longitude: {}</li>\
            </ul>'.format(id, latitude, longitude))
    
    htmlFile.writelines('<h4>Plot of NDVI and NDRE inside corresponding Voronoi Polygon</h4>')

    #create subfolder for images
    loop_img_dir = image_dir+'\{}'.format(id)
    script_dir = os.path.dirname(__file__)
    relative_img_dir = script_dir+r'\export\images\{}'.format(id)
    if os.path.exists(loop_img_dir) == False:
        os.mkdir(loop_img_dir)

    #plot the figures
    fig = pyplot.figure()
    pyplot.subplot(1,2,1)
    pyplot.imshow(croppedMaskedImageNDVI[0][0])
    pyplot.title('NDVI image')

    pyplot.subplot(1,2,2)
    pyplot.imshow(croppedMaskedImageNDRE[0][0])
    pyplot.title('NDRE image')

    pyplot.savefig(relative_img_dir+r'\ndvi_ndre_voronoi_{}.png'.format(id),  bbox_inches='tight')
    pyplot.close()
    htmlFile.writelines('<img src="'+relative_img_dir+r'\ndvi_ndre_voronoi_{}.png'.format(id)+'" alt="Voronoi" width="600" height="333">')

    
    #delete all minus values
    croppedMaskedImageNDVI[0][0][croppedMaskedImageNDVI[0][0]<0]=numpy.nan

    # create 8 bit array for segmentation
    maskedImage_8bit = croppedMaskedImageNDVI[0][0]
    maskedImage_8bit = maskedImage_8bit * 255
    maskedImage_8bit = maskedImage_8bit.astype('uint8')

    # Test Segmentation with grwoing seed
    growing_seed_Threshold_arr = SimpleThresholdSegmentation.connectedSeedGrowing(maskedImage_8bit)
    if numpy.amax(growing_seed_Threshold_arr) == 0:
        htmlFile.writelines('<p><span style="color: #ff0000;">No Broccoli was found inside this Voronoi Polygon. Please verify!</span></p>')
        continue

    # mask Array
    maskedArray = growing_seed_Threshold_arr
    maskedArray[maskedArray==1]=2
    maskedArray[maskedArray==0]=1
    maskedArray[maskedArray==2]=0
    croppedMaskedImageNDVI_array= numpy.array(croppedMaskedImageNDVI[0][0])
    croppedMaskedImageNDRE_array= numpy.array(croppedMaskedImageNDRE[0][0])

    shape_maskedarray = maskedArray.shape
    shapeNDRE = croppedMaskedImageNDRE_array.shape

    row_mask = shape_maskedarray[0]
    colum_mask = shape_maskedarray[1]

    rowNDRE = shapeNDRE[0]
    columnNDRE = shapeNDRE[1]

    #plot Threshold

    htmlFile.writelines('<h4>Plot of the Segmentation threshold</h4>')

    pyplot.figure()
    pyplot.subplot(1,3,1)
    pyplot.imshow(croppedMaskedImageNDVI_array)
    pyplot.title('NDVI image')

    pyplot.subplot(1,3,2)
    pyplot.imshow(croppedMaskedImageNDRE_array)
    pyplot.title('NDRE image')

    pyplot.subplot(1,3,3)
    pyplot.imshow(growing_seed_Threshold_arr)
    pyplot.title('Image Threshold')

    pyplot.savefig(relative_img_dir+r'\ndvi_ndre_thresholded_{}.png'.format(id),  bbox_inches='tight')
    pyplot.close()
    htmlFile.writelines('<img src="'+relative_img_dir+r'\ndvi_ndre_thresholded_{}.png'.format(id)+'" alt="Threshold" width="600" height="333">')


    if colum_mask > columnNDRE:
        empty_row = numpy.zeros(shape=(rowNDRE,1))
        empty_row[empty_row==0]=numpy.nan
        croppedMaskedImageNDRE_array = numpy.append(croppedMaskedImageNDRE_array,empty_row, axis=1)

    if columnNDRE > colum_mask:
        while columnNDRE > colum_mask:
            croppedMaskedImageNDRE_array = numpy.delete(croppedMaskedImageNDRE_array, columnNDRE-1, axis=1)
            columnNDRE -= 1

    if row_mask > rowNDRE:
        empty_column = numpy.zeros(shape=(1,colum_mask))
        empty_column[empty_column==0]=numpy.nan
        croppedMaskedImageNDRE_array = numpy.append(croppedMaskedImageNDRE_array,empty_column, axis=0)

    if rowNDRE > row_mask:
        while rowNDRE > row_mask:
            croppedMaskedImageNDRE_array = numpy.delete(croppedMaskedImageNDRE_array, rowNDRE-1, axis=0)
            rowNDRE -= 1


    maskedArray_ndvi= ma.array(croppedMaskedImageNDVI_array, mask=maskedArray, copy=True)
    maskedArray_ndre= ma.array(croppedMaskedImageNDRE_array, mask=maskedArray, copy=True)


    #plot the figures

    htmlFile.writelines('<h4>Comparision of thresholded cut out with original image</h4>')

    pyplot.figure(num=None, figsize=(15, 10), dpi=80, facecolor='w', edgecolor='k')
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

    pyplot.savefig(relative_img_dir+r'\ndvi_ndre_cutout_comparision_{}.png'.format(id),  bbox_inches='tight')
    pyplot.close()
    htmlFile.writelines('<img src="'+relative_img_dir+r'\ndvi_ndre_cutout_comparision_{}.png'.format(id)+'" alt="Threshold" width="700" height="333">')

    # mask the not masked values
    maskedArray_ndvi=numpy.extract(~numpy.isnan(maskedArray_ndvi),maskedArray_ndvi)
    maskedArray_ndre=numpy.extract(~numpy.isnan(maskedArray_ndre),maskedArray_ndre)

    # Get all interesting values
    htmlFile.writelines('<h4>Extracted Values of Broccoli #{}:</h4>'.format(id))

    pixelCount = maskedArray_ndvi.count()
    print("pixel count: {}".format(pixelCount))
    minNDVIValue = numpy.amin(maskedArray_ndvi)
    print("minNDVIValue: {}".format(minNDVIValue))
    maxNDVIValue = numpy.amax(maskedArray_ndvi)
    print("maxNDVIValue: {}".format(maxNDVIValue))
    meanNDVIValue = numpy.mean(maskedArray_ndvi)
    print("meanNDVIValue: {}".format(meanNDVIValue))
    medianNDVIValue = numpy.median(maskedArray_ndvi)
    print("medianNDVIValue: {}".format(medianNDVIValue))
    minNDREValue = numpy.amin(maskedArray_ndre)
    print("minNDREValue: {}".format(minNDREValue))
    maxNDREValue = numpy.amax(maskedArray_ndre)
    print("maxNDREValue: {}".format(maxNDREValue))
    meanNDREValue = numpy.mean(maskedArray_ndre)
    print("meanNDREValue: {}".format(meanNDREValue))
    medianNDREValue = numpy.median(maskedArray_ndre)
    print("medianNDREValue: {}".format(medianNDREValue))

    htmlFile.writelines('<ul>\
            <li>Pixel count: {}</li>\
            <li>min NDVI value: {}</li>\
            <li>max NDVI value: {}</li>\
            <li>mean NDVI value: {}</li>\
            <li>median NDVI value: {}</li>\
            <li>min NDRE value: {}</li>\
            <li>max NDRE value: {}</li>\
            <li>mean NDRE value: {}</li>\
            <li>median NDRE value: {}</li>\
            </ul>'.format(pixelCount,minNDVIValue,maxNDVIValue,meanNDVIValue,medianNDVIValue,minNDREValue,maxNDREValue,meanNDREValue,medianNDREValue))



    dataframe = pd.DataFrame({'id':[id], 'lat':[latitude], 'long':[longitude], 'timestamp': timestamp, \
                    'pixelCount': [pixelCount], 'maxNDVI': [maxNDVIValue], 'minNDVI': [minNDVIValue],\
                        'meanNDVI':[meanNDVIValue], 'medianNDVI': [medianNDVIValue], 'maxNDRE': [maxNDREValue],\
                            'minNDRE':[minNDREValue], 'meanNDRE': [meanNDREValue], 'medianNDRE': [medianNDREValue]})

    if count == 0:
        export_dataframe = dataframe
    else:
        export_dataframe = export_dataframe.append(dataframe, ignore_index=True)
    count += 1

    export_dataframe.to_csv(output_src_string+'/export.csv', sep=';', index = False)

htmlFile.close()
