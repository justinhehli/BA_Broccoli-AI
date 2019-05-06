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
import tkinter.filedialog
import tkinter.messagebox
import tkinter.simpledialog

display(Markdown('# Segmentation and extraction of drone data'))

#%%
#Extract polygons from Voronoi Cells and convert into geojson
shape = shapefile.Reader("C:/DataAnalysis/SegmentationOfData/Voronoi/Voronoi.shp")
#first feature of the shapefile
features = shape.shapeRecords()

#open images

# ndvi_src_string = tkinter.filedialog.askopenfilename(title='Select NDVI tif')
# display(Markdown('Source file of the ndvi measurement: ' + ndvi_src_string))
# ndre_src_string = tkinter.filedialog.askopenfilename(title='Select NDRE tif')
# display(Markdown('Source file of the ndre measurement: ' + ndre_src_string))
# output_src_string = tkinter.filedialog.askdirectory()
# display(Markdown('export path: ' + output_src_string + '/export.csv'))
# timestamp = tkinter.simpledialog.askstring('Input','date of measurement in (yyyy-mm-dd)?')
# display(Markdown('measurement timestamp: ' + timestamp))

ndvi_src_string = r'C:\DataAnalysis\SegmentationOfData\export\20190501RMC_index_ndvi_modified.tif'
ndre_src_string = r'C:\DataAnalysis\SegmentationOfData\export\20190501RMC_index_ndre_modified.tif'
output_src_string = r'C:\DataAnalysis\SegmentationOfData\export'
timestamp = '2019-05-01'


ndvi_src = rasterio.open(ndvi_src_string)
ndre_src = rasterio.open(ndre_src_string)

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

    display(Markdown("## Broccoli Nr. {}".format(id)))
    display(Markdown("latitude: {}".format(latitude)))
    display(Markdown("longitude: {}".format(longitude)))

    display(Markdown('Plot of NDVI and NDRE image inside corresponding Voronoi polygon'))

    # #plot the figures
    # pyplot.figure()
    # pyplot.subplot(1,2,1)
    # pyplot.imshow(croppedMaskedImageNDVI[0][0])
    # pyplot.title('NDVI image')

    # pyplot.subplot(1,2,2)
    # pyplot.imshow(croppedMaskedImageNDRE[0][0])
    # pyplot.title('NDRE image')
    # pyplot.show()

    #delete all minus values
    croppedMaskedImageNDVI[0][0][croppedMaskedImageNDVI[0][0]<0]=numpy.nan

    # create 8 bit array for segmentation
    maskedImage_8bit = croppedMaskedImageNDVI[0][0]
    maskedImage_8bit = maskedImage_8bit * 255
    maskedImage_8bit = maskedImage_8bit.astype('uint8')

    if id == 282:
        print('bla') 

    # Test Segmentation with grwoing seed
    growing_seed_Threshold_arr = SimpleThresholdSegmentation.connectedSeedGrowing(maskedImage_8bit)
    if numpy.amax(growing_seed_Threshold_arr) == 0:
        continue
    #plot the figures
    display(Markdown('## Cut out broccoli from seed growing algorithm'))

    if id == 1:
        print('bla') 

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

    if id == 1:
        print('bla') 

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

        pyplot.show()

    if colum_mask > columnNDRE:
        #croppedMaskedImageNDRE_array = numpy.resize(croppedMaskedImageNDRE_array, maskedArray.shape)
        #croppedMaskedImageNDRE_array.resize(maskedArray.shape, refcheck=False)
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
    
    if id == 1:
        print('bla') 

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

        pyplot.show()


    maskedArray_ndvi= ma.array(croppedMaskedImageNDVI_array, mask=maskedArray, copy=True)
    maskedArray_ndre= ma.array(croppedMaskedImageNDRE_array, mask=maskedArray, copy=True)

    # mask the not masked values
    maskedArray_ndvi=numpy.extract(~numpy.isnan(maskedArray_ndvi),maskedArray_ndvi)
    maskedArray_ndre=numpy.extract(~numpy.isnan(maskedArray_ndre),maskedArray_ndre)


    #plot the figures

    display(Markdown('## Compare cut out broccoli with original image'))

    # pyplot.figure()
    # pyplot.subplot(1,4,1)
    # pyplot.imshow(croppedMaskedImageNDVI[0][0])
    # pyplot.title('NDVI image')

    # pyplot.subplot(1,4,2)
    # pyplot.imshow(maskedArray_ndvi)
    # pyplot.title('Masked Image NDVI')

    # pyplot.subplot(1,4,3)
    # pyplot.imshow(croppedMaskedImageNDRE[0][0])
    # pyplot.title('NDRE image')

    # pyplot.subplot(1,4,4)
    # pyplot.imshow(maskedArray_ndre)
    # pyplot.title('Masked Image NDRE')
    # pyplot.show()

    # Get all interesting values

    pixelCount = maskedArray_ndvi.count()
    display(Markdown("pixel count: {}".format(pixelCount)))
    print("pixel count: {}".format(pixelCount))
    minNDVIValue = numpy.amin(maskedArray_ndvi)
    display(Markdown("minNDVIValue: {}".format(minNDVIValue)))
    print("minNDVIValue: {}".format(minNDVIValue))
    maxNDVIValue = numpy.amax(maskedArray_ndvi)
    display(Markdown("maxNDVIValue: {}".format(maxNDVIValue)))
    print("maxNDVIValue: {}".format(maxNDVIValue))
    meanNDVIValue = numpy.mean(maskedArray_ndvi)
    display(Markdown("meanNDVIValue: {}".format(meanNDVIValue)))
    print("meanNDVIValue: {}".format(meanNDVIValue))
    medianNDVIValue = numpy.median(maskedArray_ndvi)
    display(Markdown("medianNDVIValue: {}".format(medianNDVIValue)))
    print("medianNDVIValue: {}".format(medianNDVIValue))
    minNDREValue = numpy.amin(maskedArray_ndre)
    display(Markdown("minNDREValue: {}".format(minNDREValue)))
    print("minNDREValue: {}".format(minNDREValue))
    maxNDREValue = numpy.amax(maskedArray_ndre)
    display(Markdown("maxNDREValue: {}".format(maxNDREValue)))
    print("maxNDREValue: {}".format(maxNDREValue))
    meanNDREValue = numpy.mean(maskedArray_ndre)
    display(Markdown("meanNDREValue: {}".format(meanNDREValue)))
    print("meanNDREValue: {}".format(meanNDREValue))
    medianNDREValue = numpy.median(maskedArray_ndre)
    display(Markdown("medianNDREValue: {}".format(medianNDREValue)))
    print("medianNDREValue: {}".format(medianNDREValue))

    dataframe = pd.DataFrame({'id':[id], 'lat':[latitude], 'long':[longitude], 'timestamp': timestamp, \
                    'pixelCount': [pixelCount], 'maxNDVI': [maxNDVIValue], 'minNDVI': [minNDVIValue],\
                        'meanNDVI':[meanNDVIValue], 'medianNDVI': [medianNDVIValue], 'maxNDRE': [maxNDREValue],\
                            'minNDRE':[minNDREValue], 'meanNDRE': [meanNDREValue], 'medianNDRE': [medianNDREValue]})

    if count == 0:
        export_dataframe = dataframe
    else:
        export_dataframe = export_dataframe.append(dataframe, ignore_index=True)
    count += 1

    display(Markdown('## Cut out broccoli from seed growing algorithm'))
    export_dataframe.to_csv(output_src_string+'/export.csv', sep=';', index = False)
