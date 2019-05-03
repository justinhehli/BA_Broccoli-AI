import rasterio
import rasterio.features
import rasterio.warp
import rasterio.drivers
import matplotlib.pyplot as pyplot
import numpy
import geojson


import shapefile
shape = shapefile.Reader("C:/DataAnalysis/SegmentationOfData/Voronoi.shp")
#first feature of the shapefile
shapes = shape.shapes()
print(len(shapes))
feature = shape.shapeRecords()[0]
first = feature.shape.__geo_interface__  
print(first) # (GeoJSON format)
{'type': 'LineString', 'coordinates': ((0.0, 0.0), (25.0, 10.0), (50.0, 50.0))}
firstgeoJson = geojson.dumps(first, sort_keys=True)
firstGeoJsonObject = geojson.loads(firstgeoJson)
print(firstgeoJson)


# Burn polygons to image, apply masks

    # Generate mask using first image for metadata
with rasterio.open('C:/DataAnalysis/SegmentationOfData/20190425MSC_index_ndvi_transformed.tif') as src:
    mask = rasterio.features.rasterize([firstGeoJsonObject] , 
            out_shape=src.shape, 
            transform=src.transform)
    # Make masked array for each 
with rasterio.open('C:/DataAnalysis/SegmentationOfData/20190425MSC_index_ndvi_transformed.tif') as src:
    maskedImage = numpy.ma.MaskedArray(src.read(1), mask=numpy.logical_not(mask))
    maskedImage.shape
    pyplot.imshow(maskedImage)
    pyplot.show()






