import cv2 as cv
import numpy as np
import matplotlib.pyplot as pyplot
import sys
import SimpleITK as sitk
from myshow import myshow

def simple_threshold(arrayValue):
    img = arrayValue
    ret,thresh = cv.threshold(img,0.5,1,cv.THRESH_TOZERO)
    return thresh

def  adaptive_threshold(arrayValue):
    img = cv.medianBlur(arrayValue,5)
    img[img==0] = 100
    th2 = cv.adaptiveThreshold(img,255,cv.ADAPTIVE_THRESH_MEAN_C,cv.THRESH_BINARY,7,2)
    th3 = cv.adaptiveThreshold(img,255,cv.ADAPTIVE_THRESH_GAUSSIAN_C,cv.THRESH_BINARY,7,2)
    return th2, th3
    

def otsu_threshold(arrayValue):
    arrayValue[arrayValue==0] = 127
    # Otsu's thresholding
    ret2,th2 = cv.threshold(arrayValue,0,255,cv.THRESH_BINARY+cv.THRESH_OTSU)
    # Otsu's thresholding after Gaussian filtering
    blur = cv.GaussianBlur(arrayValue,(5,5),0)
    ret3,th3 = cv.threshold(blur,0,255,cv.THRESH_BINARY+cv.THRESH_OTSU)
    return th2, th3


def get_highest_value_nearest_middle(array):
    shape_array = array.shape
    row_length = shape_array[0]
    column_length = shape_array[1]

    max_index_row = round(row_length / 2)
    rest_length_row = row_length - max_index_row
    max_index_column = round(column_length/2)
    rest_length_column = column_length - max_index_column

    row_steps_up = (1 - 0.6) / max_index_row
    row_steps_down = (1 - 0.6) / rest_length_row
    column_steps_up = (1 - 0.6) / max_index_column
    column_steps_down = (1 - 0.6) / rest_length_column

    rowpower = np.zeros(row_length)
    columnpower = np.zeros(column_length)

    count = 0
    countNeg=0
    for element in rowpower:
        if(count<max_index_row):
            rowpower[count] = ((count) * row_steps_up) + 0.6
        else:
            rowpower[count] = 1-((countNeg) * row_steps_down)
            countNeg = countNeg + 1
        count = count + 1

    count = 0
    countNeg=0
    for element in columnpower:
        if(count<max_index_column):
            columnpower[count] = ((count) * column_steps_up) + 0.6
        else:
            columnpower[count] = 1-((countNeg) * column_steps_down)
            countNeg = countNeg + 1
        count = count + 1

    maxValue = 0
    row_index = 0
    column_index = 0
    i = 0
    j = 0
    for rowelement in rowpower:
        for columnelement in columnpower:
            tempvalue = rowelement * columnelement * array[j][i]
            i += 1
            if tempvalue > maxValue:
                maxValue = tempvalue
                row_index = i
                column_index = j
        j += 1
        i = 0
    return row_index, column_index


def connectedSeedGrowing(arr):

    #convert array to image
    img = sitk.GetImageFromArray(arr)
    # find seed -> highest value
    #index = np.where(arr == np.amax(arr))
    index = get_highest_value_nearest_middle(arr)
    #seed = np.array([index[1][0],index[0][0]], dtype='int').tolist()
    seed = np.array([index[0],index[1]], dtype='int').tolist()
    seg = sitk.Image(img.GetSize(), sitk.sitkUInt8)
    seg.CopyInformation(img)
    seg[seed] = 1

    #show if seed is in correct position
    #myshow(sitk.LabelOverlay(img, seg))
    testarr=np.extract(arr!=0,arr)
    quantile_75 = round(np.amax(testarr)*0.7)
    #pyplot.hist(testarr)
    #pyplot.show()
    
    #plot histogram

    #calculate threshold
    seg_con = sitk.ConnectedThreshold(img, seedList=[seed],lower=quantile_75, upper=255)

    #clean up
    vectorRadius = (1, 1)
    kernel = sitk.sitkBall
    seg_clean = sitk.BinaryMorphologicalClosing(seg_con,
                                            vectorRadius,
                                            kernel)
    
    #show if thresholding is correct
    #myshow(sitk.LabelOverlay(img, seg_clean))

    #convert back to array
    new_arr = sitk.GetArrayFromImage(seg_con)                             
    return new_arr