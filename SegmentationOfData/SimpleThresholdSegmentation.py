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


def connectedSeedGrowing(arr):

    #convert array to image
    img = sitk.GetImageFromArray(arr)
    # find seed -> highest value
    index = np.where(arr == np.amax(arr))
    seed = np.array([index[1][0],index[0][0]], dtype='int').tolist()
    seg = sitk.Image(img.GetSize(), sitk.sitkUInt8)
    seg.CopyInformation(img)
    seg[seed] = 1

    #show if seed is in correct position
    #myshow(sitk.LabelOverlay(img, seg))

    #calculate threshold
    seg_con = sitk.ConnectedThreshold(img, seedList=[seed],lower=120, upper=255)

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