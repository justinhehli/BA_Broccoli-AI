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
import matplotlib
import matplotlib.pyplot as pyplot
import numpy
import numpy.ma as ma
import geojson
import shapefile
import pandas as pd
import SimpleITK as sitk
from IPython.display import display, Markdown

def writeHTML(text):
    if createReport==True:
        htmlFile.writelines(text)

def saveImage(text):
    if createReport==True:
        if os.path.isfile(text):
            os.remove(text)
        pyplot.savefig(text, bbox_inches='tight')

def saveArray(array, path):
    if createReport==True:
        if os.path.isfile(path):
            os.remove(path)
        array.dump(path)

# get directory
dirname = os.path.dirname(__file__)

#Extract polygons from Voronoi Cells and convert into geojson
shape = shapefile.Reader(os.path.join(dirname, r'Voronoi/Voronoi.shp'))
#first feature of the shapefile
features = shape.shapeRecords()

#Extract Centroids from Voronoi Cells and convert into geojson
shape = shapefile.Reader(os.path.join(dirname, r'Voronoi/VoronoiCentroids.shp'))
#first feature of the shapefile
centroids_features = shape.shapeRecords()


# configurable parameters
#_____________________________________________________________________________________________________________________________________________

#use csv to load tif files??
useCSV = False
# create Report??
createReport = True
# show plots
showPlot = False
# create csv export
createCSVexport = True

#open images
#The only things that needs to be changed are the following 3 values. Dont forget to update the time!
if(useCSV == False):
    ndvi_src_string = r'\\fs004\ice\lehre\bachelorarbeiten\2019\Pflanzen\Drohnenaufnahmen\20190509\export\20190509RMC_index_ndvi_modified.tif'
    ndre_src_string = r'\\fs004\ice\lehre\bachelorarbeiten\2019\Pflanzen\Drohnenaufnahmen\20190509\export\20190509RMC_index_ndre_modified.tif'
    timestamp = '2019-04-18'
    data = pd.DataFrame({'ndviString':[ndvi_src_string], 'ndreString':[ndre_src_string], 'timestamp':[timestamp]})
else:
    data = pd.read_csv(r'C:\Bachelorthesis\DataAnalysis\SegmentationOfData\report.csv') 

#________________________________________________________________________________________________________________________________________________

for index, row in data.iterrows():
    
    ndvi_src_string = row['ndviString']
    ndre_src_string = row['ndreString']
    timestamp = row['timestamp']

    cut_string_index = ndvi_src_string.index('export')
    output_root_dir = ndvi_src_string[0:cut_string_index]
    output_src_string = output_root_dir+'report'
    image_dir = output_src_string+'\images'
    


    ndvi_src = rasterio.open(ndvi_src_string)
    ndre_src = rasterio.open(ndre_src_string)

    if os.path.exists(image_dir) == False and createReport == True:
        os.mkdir(output_src_string)
        os.mkdir(image_dir)
    if createReport==True:
        htmlFile = open(os.path.join(output_src_string, r'report.html'),"w")
    writeHTML('<h1><strong>Segmentation and extraction of drone data</strong></h1>')
    writeHTML('<h2><strong>Information:</strong></h2>\
        <p>NDVI file: {}</p>\
        <p>NDRE file: {}</p>\
        <p>Date of measurement: {} </p>'.format(ndvi_src_string, ndre_src_string, timestamp))
    writeHTML('The following report shows the segmentation on all the broccolis with the help of the Voronoi \
        algorithm to encapsulate the broccoli and the growing seed algorithm to create a segmentation of the algorithm')

    writeHTML('<h2>Broccoli analysis</h2>')

    export_dataframe = pd.DataFrame()
    count = 0
    for feature in features:
        centroid_feature = centroids_features[count]
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
        latitude = centroid_feature.record.latitude_
        longitude = centroid_feature.record.longitude_

        writeHTML('<h3>Broccoli #{}</h3>'.format(id))

        writeHTML('<ul>\
                <li>id: {}</li>\
                <li>latitude: {}</li>\
                <li>longitude: {}</li>\
                </ul>'.format(id, latitude, longitude))
        
        writeHTML('<h4>Plot of NDVI and NDRE inside corresponding Voronoi Polygon</h4>')

        if createReport==True or showPlot==True:
            #create subfolder for images
            loop_img_dir = image_dir+'\{}'.format(id)
            relative_img_dir = r'images\{}'.format(id)
            if (os.path.exists(loop_img_dir) == False and createReport == True):
                os.mkdir(loop_img_dir)
            #normalize colors
            normalize = matplotlib.colors.Normalize(vmin=0, vmax=1)
            #plot the figures
            fig = pyplot.figure()
            pyplot.subplot(1,2,1)
            pyplot.imshow(croppedMaskedImageNDVI[0][0], norm=normalize)
            pyplot.title('NDVI image')

            pyplot.subplot(1,2,2)
            pyplot.imshow(croppedMaskedImageNDRE[0][0], norm=normalize)
            pyplot.title('NDRE image')
            if(showPlot==True):
                pyplot.show()
            if(createReport==True):
                saveImage((loop_img_dir+r'\ndvi_ndre_voronoi_{}.png'.format(id)))
            pyplot.close()
            writeHTML('<img src="'+relative_img_dir+r'\ndvi_ndre_voronoi_{}.png'.format(id)+'" alt="Voronoi" width="600" height="333">')

        
        #delete all minus values
        croppedMaskedImageNDVI[0][0][croppedMaskedImageNDVI[0][0]<0]=numpy.nan

        # create 8 bit array for segmentation
        maskedImage_8bit = croppedMaskedImageNDVI[0][0]
        maskedImage_8bit = maskedImage_8bit * 255
        maskedImage_8bit = maskedImage_8bit.astype('uint8')

        # Test Segmentation with grwoing seed
        growing_seed_Threshold_arr = SimpleThresholdSegmentation.connectedSeedGrowing(maskedImage_8bit)
        if numpy.amax(growing_seed_Threshold_arr) == 0:
            writeHTML('<p><span style="color: #ff0000;">No Broccoli was found inside this Voronoi Polygon. Please verify!</span></p>')
            count+=1
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

        writeHTML('<h4>Plot of the Segmentation threshold</h4>')

        if createReport==True or showPlot==True:
            #normalize colors
            normalize = matplotlib.colors.Normalize(vmin=0, vmax=1)
            pyplot.figure()
            pyplot.subplot(1,3,1)
            pyplot.imshow(croppedMaskedImageNDVI_array, norm=normalize)
            pyplot.title('NDVI image')

            pyplot.subplot(1,3,2)
            pyplot.imshow(croppedMaskedImageNDRE_array, norm=normalize)
            pyplot.title('NDRE image')

            pyplot.subplot(1,3,3)
            pyplot.imshow(growing_seed_Threshold_arr, norm=normalize)
            pyplot.title('Image Threshold')

            if(showPlot==True):
                pyplot.show()
            if(createReport==True):
                saveImage((loop_img_dir+r'\ndvi_ndre_thresholded_{}.png'.format(id)))
            pyplot.close()
            writeHTML('<img src="'+relative_img_dir+r'\ndvi_ndre_thresholded_{}.png'.format(id)+'" alt="Threshold" width="600" height="333">')


        if colum_mask > columnNDRE:
            empty_row = numpy.zeros(shape=(rowNDRE,colum_mask-columnNDRE))
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

        writeHTML('<h4>Comparision of thresholded cut out with original image</h4>')
        if createReport==True or showPlot==True:
            #normalize colors
            normalize = matplotlib.colors.Normalize(vmin=0, vmax=1)
            pyplot.figure(num=None, figsize=(15, 10), dpi=80, facecolor='w', edgecolor='k')
            pyplot.subplot(1,4,1)
            pyplot.imshow(croppedMaskedImageNDVI[0][0], norm=normalize)
            pyplot.title('NDVI image')
            #save numpy array
            saveArray(croppedMaskedImageNDVI[0][0], loop_img_dir+r'\ndvi_{}.npy'.format(id))

            pyplot.subplot(1,4,2)
            pyplot.imshow(maskedArray_ndvi,norm=normalize)
            pyplot.title('Masked Image NDVI')
            saveArray(maskedArray_ndvi, loop_img_dir+r'\ndvi_masked_{}.npy'.format(id))

            pyplot.subplot(1,4,3)
            pyplot.imshow(croppedMaskedImageNDRE[0][0],norm=normalize)
            pyplot.title('NDRE image')
            saveArray(croppedMaskedImageNDRE[0][0], loop_img_dir+r'\ndre_{}.npy'.format(id))

            pyplot.subplot(1,4,4)
            pyplot.imshow(maskedArray_ndre, norm=normalize)
            pyplot.title('Masked Image NDRE')
            saveArray(maskedArray_ndre, loop_img_dir+r'\ndre_masked_{}.npy'.format(id))

            if(showPlot==True):
                pyplot.show()
            if(createReport==True):
                saveImage((loop_img_dir+r'\ndvi_ndre_cutout_comparision_{}.png'.format(id)))
            writeHTML('<img src="'+relative_img_dir+r'\ndvi_ndre_cutout_comparision_{}.png'.format(id)+'" alt="Threshold" width="700" height="333">')
            pyplot.close()

        # mask the not masked values
        maskedArray_ndvi=numpy.extract(~numpy.isnan(maskedArray_ndvi),maskedArray_ndvi)
        maskedArray_ndre=numpy.extract(~numpy.isnan(maskedArray_ndre),maskedArray_ndre)

        # Get all interesting values
        writeHTML('<h4>Extracted Values of Broccoli #{}:</h4>'.format(id))

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
        ndvi_15_quantile = numpy.quantile(maskedArray_ndvi, 0.15)
        print("NDVI_15_Quantile: {}".format(ndvi_15_quantile))
        ndvi_25_quantile = numpy.quantile(maskedArray_ndvi, 0.25)
        print("NDVI_25_Quantile: {}".format(ndvi_25_quantile))
        ndvi_75_quantile = numpy.quantile(maskedArray_ndvi, 0.75)
        print("NDVI_75_Quantile: {}".format(ndvi_75_quantile))
        ndvi_85_quantile = numpy.quantile(maskedArray_ndvi, 0.85)
        print("NDVI_85_Quantile: {}".format(ndvi_85_quantile))
        
        minNDREValue = numpy.amin(maskedArray_ndre)
        print("minNDREValue: {}".format(minNDREValue))
        maxNDREValue = numpy.amax(maskedArray_ndre)
        print("maxNDREValue: {}".format(maxNDREValue))
        meanNDREValue = numpy.mean(maskedArray_ndre)
        print("meanNDREValue: {}".format(meanNDREValue))
        medianNDREValue = numpy.median(maskedArray_ndre)
        print("medianNDREValue: {}".format(medianNDREValue))
        ndre_15_quantile = numpy.quantile(maskedArray_ndre, 0.15)
        print("ndre_15_Quantile: {}".format(ndre_15_quantile))
        ndre_25_quantile = numpy.quantile(maskedArray_ndre, 0.25)
        print("ndre_25_Quantile: {}".format(ndre_25_quantile))
        ndre_75_quantile = numpy.quantile(maskedArray_ndre, 0.75)
        print("ndre_75_Quantile: {}".format(ndre_75_quantile))
        ndre_85_quantile = numpy.quantile(maskedArray_ndre, 0.85)
        print("ndre_85_Quantile: {}".format(ndre_85_quantile))

        writeHTML('<ul>\
                <li>Pixel count: {}</li>\
                <li>min NDVI value: {}</li>\
                <li>max NDVI value: {}</li>\
                <li>mean NDVI value: {}</li>\
                <li>median NDVI value: {}</li>\
                <li>15 quantilee NDVI value: {}</li>\
                <li>25 quantilee NDVI value: {}</li>\
                <li>75 quantilee NDVI value: {}</li>\
                <li>85 quantilee NDVI value: {}</li>\
                <li>min NDRE value: {}</li>\
                <li>max NDRE value: {}</li>\
                <li>mean NDRE value: {}</li>\
                <li>median NDRE value: {}</li>\
                <li>15 quantilee NDRE value: {}</li>\
                <li>25 quantilee NDRE value: {}</li>\
                <li>75 quantilee NDRE value: {}</li>\
                <li>85 quantilee NDRE value: {}</li>\
                </ul>'.format(pixelCount,minNDVIValue,maxNDVIValue,meanNDVIValue,medianNDVIValue, ndvi_15_quantile, ndvi_25_quantile, ndvi_75_quantile, ndvi_85_quantile,\
                minNDREValue,maxNDREValue,meanNDREValue,medianNDREValue,ndre_15_quantile,ndre_25_quantile,ndre_75_quantile,ndre_85_quantile))


        if  createCSVexport == True:

            dataframe = pd.DataFrame({'id':[id], 'lat':[latitude], 'long':[longitude], 'timestamp': timestamp, \
                            'pixelCount': [pixelCount], 'maxNDVI': [maxNDVIValue], 'minNDVI': [minNDVIValue],\
                                'meanNDVI':[meanNDVIValue], 'medianNDVI': [medianNDVIValue], 'NDVI_15_Quantile' : [ndvi_15_quantile],\
                                'NDVI_25_Quantile' : [ndvi_25_quantile], 'NDVI_75_Quantile' : [ndvi_75_quantile], 'NDVI_85_Quantile' : [ndvi_85_quantile],\
                                'maxNDRE': [maxNDREValue],'minNDRE':[minNDREValue], 'meanNDRE': [meanNDREValue], 'medianNDRE': [medianNDREValue],\
                                'NDRE_15_Quantile' : [ndre_15_quantile], 'NDRE_25_Quantile' : [ndre_25_quantile], 'NDRE_75_Quantile' : [ndre_75_quantile],\
                                'NDRE_85_Quantile' : [ndre_85_quantile]})

            if count == 0:
                export_dataframe = dataframe
            else:
                export_dataframe = export_dataframe.append(dataframe, ignore_index=True)
            count += 1

            export_dataframe.to_csv(output_src_string+'\export.csv', sep=';', index = False)

    if createReport==True:
        htmlFile.close()