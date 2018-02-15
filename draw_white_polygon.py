#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 15 11:09:11 2018

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


parser = argparse.ArgumentParser(description='Draws a white polygon (indicated in a json file annotation) in the images under the path')

parser.add_argument("-p", dest="path", type=str, required=True, help="directory path where are .jpg file images to be drawed")
parser.add_argument("-jf", dest="jsonfile", type=str,required=True, help=".json file with annotations over the images. We assumed that the set of images are under /imgs folder in current path")

args = parser.parse_args()

print args.jsonfile
print args.path

jsonrecords = json.loads(open(args.jsonfile).read())

if (os.path.exists(args.path)):

    # create result dir inside path 
    result_dir=args.path + "/"+ "GT"
    
    try:
        os.makedirs(result_dir)
    except OSError as err:
        print(err)
    
    #take polygon annotation
    for record in jsonrecords:
           
        # read image as RGB and add alpha (transparency)
        im = Image.open(args.path + "/" + record['filename']).convert("RGBA")
  
        for anotattion in record['annotations']:
            polygon=[]
            if(anotattion['class'] == "polygon"):
                xpoints=anotattion["xn"]
                ypoints=anotattion["yn"]
                    
                splited_xpoints = xpoints.split(";")                
                splited_ypoints = ypoints.split(";")
                    
            for i in range (len(splited_xpoints)):
                polygon.append(((int (float(str(splited_xpoints[i])))),(int (float(str(splited_ypoints[i]))))))
                   
            #print_list(polygon)
           
            # draw withe polygon figure in im
            ImageDraw.Draw(im).polygon(polygon, outline="white", fill="white")
    
        # new name file
        fn_GT="{}{}{}{}{}".format(result_dir,"/",os.path.splitext(record['filename'])[0],"_GT",os.path.splitext(record['filename'])[1])
        im.save(fn_GT)