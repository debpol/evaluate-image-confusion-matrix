#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  7 11:19:00 2017

@author: deby
"""
import os
import json
import argparse
import numpy
from PIL import Image, ImageDraw

SEA=0
DOLPHIN=255

def print_list(lst):
    for item in lst:
        print str(item) 


parser = argparse.ArgumentParser(description='Calcule confusion matrix, from orginal image vs binarized dolphin image. Use the dolphin polygon annotation to delimit true condition positive.Crop and save it as .png image')

parser.add_argument("-io", dest="original_im", type=str, required=True, help=".jpg file orginal image")
parser.add_argument("-ib", dest="binarized_im", type=str, required=True, help=".jpg file binarized image")
parser.add_argument("-jf", dest="jsonfile", type=str,required=True, help=".json file with annotations over the images. We assumed that the image is in the current path")

args = parser.parse_args()


print args.jsonfile
print args.original_im
print args.binarized_im

jsonrecords = json.loads(open(args.jsonfile).read())

polygon=[]


for record in jsonrecords:
    fn = record['filename']    
    if (fn == args.original_im):
        for anotattion in record['annotations']:
            if(anotattion['class'] == "polygon"):
                                
                xpoints=anotattion["xn"]
                ypoints=anotattion["yn"]
                
                splited_xpoints = xpoints.split(";")                
                splited_ypoints = ypoints.split(";")
                
                for i in range (len(splited_xpoints)):
                    polygon.append(((int (float(str(splited_xpoints[i])))),(int (float(str(splited_ypoints[i]))))))
                  
#print_list(polygon)
                    
# read original image as RGB and add alpha (transparency)
o_im = Image.open(args.original_im)
rgba_o_im=o_im.convert("RGBA")

#predict value binarized dolphin image
b_im = Image.open(args.binarized_im)

# convert to numpy (for convenience)
np_predict_value = numpy.asarray(b_im)

# convert to numpy (for convenience)
np_im = numpy.asarray(rgba_o_im)

print  "image shape{}".format(np_im.shape)
print  "total pixels = {} x {} = {}".format(np_im.shape[0], np_im.shape[1], np_im.shape[1]* np_im.shape[0])
#(row= y, col=x, layers)

# create a image of shape (x,y) in black
maskIm = Image.new('L', (np_im.shape[1], np_im.shape[0]), 0)

#maskIm keeps values: 0 for black backgroud  and 1 for withe polygon figure 
ImageDraw.Draw(maskIm).polygon(polygon, outline=1, fill=1)

np_mask = numpy.array(maskIm)

# assemble new image (uint8: 0-255) 
np_new_im = numpy.empty(np_im.shape,dtype='uint8')

# copy layers RGB from original image
np_new_im[:,:,:3] = np_im[:,:,:3]

np_real_value = np_mask*255  #pone en 255 los valores 1 que son del poligono

# transparency (4th layer) 
np_new_im[:,:,3] = np_real_value

# back to Image from numpy and save it
newIm = Image.fromarray(np_new_im, "RGBA")
fn_polygon_im="{}{}".format(os.path.splitext(args.original_im)[0],"_polygon.png")
newIm.save(fn_polygon_im)


#### calule confusion matrix ############
high, width = np_predict_value.shape

# counters
trueNegative = falseNegative = falsePositive = truePositive = 0

for row in range(high):
    for column in range(width):
        if np_predict_value[row,column] != DOLPHIN and np_real_value[row,column] == SEA:
            trueNegative += 1
        if np_predict_value[row,column] != DOLPHIN and np_real_value[row,column] == DOLPHIN:
            falseNegative += 1
        if np_predict_value[row,column] == DOLPHIN and np_real_value[row,column] == SEA:
            falsePositive += 1
        if np_predict_value[row,column] == DOLPHIN and np_real_value[row,column] == DOLPHIN:
            truePositive += 1

mask_predict_dolphin = np_predict_value == DOLPHIN
predict_dolphin = np_predict_value [mask_predict_dolphin]
amount_predict_dolphin = predict_dolphin.shape[0]

mask_predict_non_dolphin = numpy.logical_not(mask_predict_dolphin)
predict_non_dolphin = np_predict_value [mask_predict_non_dolphin]
amount_predict_non_dolphin = predict_non_dolphin.shape[0]

mask_real_dolphin = np_real_value == DOLPHIN
real_dolphin = np_real_value [mask_real_dolphin]
amount_real_dolphin = real_dolphin.shape[0]

mask_real_non_dolphin = numpy.logical_not(mask_real_dolphin)
real_non_dolphin = np_real_value [mask_real_non_dolphin]
amount_real_non_dolphin = real_non_dolphin.shape[0]

print "amount_real_dolphin = {}".format(amount_real_dolphin)
print "amount_real_non_dolphin = {}".format(amount_real_non_dolphin)

print "amount_predict_dolphin = {}".format(amount_predict_dolphin)
print "amount_predict_non_dolphin = {}".format(amount_predict_non_dolphin)

# rates
true_positive_rate = truePositive * 1.0 / amount_real_dolphin

true_negative_rate = trueNegative * 1.0/ ((high*width)-amount_real_dolphin)

false_positive_rate = falsePositive * 1.0/ ((high*width)-amount_real_dolphin)

false_negative_rate = falseNegative * 1.0 / amount_real_dolphin


accuracy = (truePositive + trueNegative)*1.0 / (high*width)

precision = truePositive*1.0 / amount_predict_dolphin

print "***************"

print "true_positive = {}".format(truePositive)
print "false_positive = {}".format(falsePositive)
print "false_negative = {}".format(falseNegative)
print "true_negative = {}".format(trueNegative)

print "TP + FP + FN +TN = {}".format(trueNegative + falsePositive + falseNegative + trueNegative)

print "***************"

print "true_positive_rate or sensitivity  or recall = {}".format(true_positive_rate)
print "true_negative_rate or specificity = {}".format(true_negative_rate)

print "false_positive_rate = {}".format(false_positive_rate)
print "false_negative_rate = {}".format(false_negative_rate)

print "accuracy = {}".format(accuracy)
print "precision or positive predictive value = {}".format(precision)

