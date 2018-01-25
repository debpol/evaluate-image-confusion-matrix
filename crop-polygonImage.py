#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  7 11:19:00 2017

@author: deby
"""
import json
import os
import argparse
import numpy
from PIL import Image, ImageDraw


def print_list(lst):
    print "imprimiendo poligono"
    for item in lst:
        print str(item) 


parser = argparse.ArgumentParser(description='Crop a polygon (indicated in a json file)in the image given')

parser.add_argument("-i", dest="image", type=str, required=True, help=".jpg file image to be cropped")
parser.add_argument("-jf", dest="jsonfile", type=str,required=True, help=".json file with annotations over the images. We assumed that the set of images are under /imgs folder in current path")

args = parser.parse_args()


print args.jsonfile
print args.image
jsonrecords = json.loads(open(args.jsonfile).read())

polygon=[]


for record in jsonrecords:
    fn = record['filename']    
    if (fn == args.image):
        print fn
        for anotattion in record['annotations']:
            if(anotattion['class'] == "polygon"):
                xpoints=anotattion["xn"]
                ypoints=anotattion["yn"]
                
                splited_xpoints = xpoints.split(";")                
                splited_ypoints = ypoints.split(";")
                
                for i in range (len(splited_xpoints)):
                    polygon.append(((int (float(str(splited_xpoints[i])))),(int (float(str(splited_ypoints[i]))))))
               
#print_list(polygon)
                    
# read image as RGB and add alpha (transparency)
im = Image.open(args.image).convert("RGBA")

# convert to numpy (for convenience)
np_im = numpy.asarray(im)

print np_im.shape 
#(filas= y, col=x, capas)

# create maskIm (x,y) in black
maskIm = Image.new('L', (np_im.shape[1], np_im.shape[0]), 0)

#maskIm keeps black backgroud and withe polygon figure
ImageDraw.Draw(maskIm).polygon(polygon, outline=1, fill=1)

np_mask = numpy.array(maskIm)

# assemble new image (uint8: 0-255)
newImArray = numpy.empty(np_im.shape,dtype='uint8')

# colors (three first columns, RGB)
newImArray[:,:,:3] = np_im[:,:,:3]

# transparency (4th column)
newImArray[:,:,3] = np_mask*255

# back to Image from numpy
newIm = Image.fromarray(newImArray, "RGBA")
fn_polygon_im="{}{}".format(os.path.splitext(args.image)[0],"_polygon.png")
newIm.save(fn_polygon_im)