#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 29 11:19:23 2018

@author: deby
"""

import json
import os
import argparse
import numpy
from PIL import Image, ImageDraw

from matplotlib import pyplot as plt

from math import sqrt, pi
from poisson_disc import Grid
import random
import pandas as pd


polygon_tag="sample-point-dolphin"
backgroud_tag="sample-point-sea"
max_size_box_sampling=86
default_radius=40

def inside_polygon(x, y, points):
    """
    Return True if a coordinate (x, y) is inside a polygon defined by
    a list of verticies [(x1, y1), (x2, x2), ... , (xN, yN)].

    Reference: http://www.ariel.com.au/a/python-point-int-poly.html
    """
    n = len(points)
    inside = False
    p1x, p1y = points[0]
    for i in range(1, n + 1):
        p2x, p2y = points[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    return inside

def print_list(lst):
    print "printing polygon list ... "
    for item in lst:
        print str(item) 

def tag_sample_points(items, polygon, polygon_tag, backgroud_tag,radius):
    tagged_sample_points=[]
    for item in items:
        if inside_polygon(item[0],item[1],polygon):
             tagged_sample_points.append((item,polygon_tag, radius))
        else:
            tagged_sample_points.append((item,backgroud_tag, radius))
    return tagged_sample_points


parser = argparse.ArgumentParser(description='generates sampling points with poisson disc over an image.It process all images under "/ imgs" folder in current work directory. The points generated are tagged according to these are outside or inside of polygon indicated in the json file annotations')
parser.add_argument("-jf", dest="jsonfile", type=str,required=True, help=".json file with polygon ROI annotations over the images")
parser.add_argument("-r", dest="r", type=int,required=False, help="r is the minimum allowable distance between any two samples. By default it is 40")

args = parser.parse_args()

jsonrecords = json.loads(open(args.jsonfile).read())


for index in range(len(jsonrecords)):
    polygon=[]
    record=jsonrecords[index]
    fn = 'imgs/'+ record['filename']
    print 'Processing {}'.format(fn)

    if record['annotations']:
        record_index=index
        for anotattion in record['annotations']:
            if(anotattion['class'] == "polygon"):
                xpoints=anotattion["xn"]
                ypoints=anotattion["yn"]
                
                splited_xpoints = xpoints.split(";")                
                splited_ypoints = ypoints.split(";")
                
                for i in range (len(splited_xpoints)):
                    polygon.append(((int (float(str(splited_xpoints[i])))),(int (float(str(splited_ypoints[i]))))))
               
                    
# read image as RGB and add alpha (transparency)
        im = Image.open(fn).convert("RGBA")

        im_to_draw = Image.open(fn)
        r_point=2
        im_draw=ImageDraw.Draw(im)

# convert to numpy (for convenience)
        np_im = numpy.asarray(im)

#set values for poisson-disc
# =============================================================================
# - r is the minimum allowable distance between any two samples
# - width and height are rectangular bounds
# - Grid is a class that will generate poisson disc samples with rejection
# - based on the input r and the rectangular bounds.
# =============================================================================

#(row= y, col=x, layers) =np_im.shape
        height,width,_= np_im.shape 
        radius = args.r if (0 < args.r < max_size_box_sampling) else default_radius
        grid = Grid(radius, width, height)
        seed = (int(random.uniform(0, width)),int(random.uniform(0, height)))

#generate points sampling
        sample_points = grid.poisson_int(seed)

#tagged each point and save it as dataframe: ["sample_point", "tag", "radius_size"]
        df_tagged_sample_points = pd.DataFrame(tag_sample_points(sample_points, polygon, polygon_tag, backgroud_tag, radius))

#change the columns names of dataframe
        df_tagged_sample_points.columns=["sample_point", "tag", "radius_size"]

#break down a tuple point
        df_tagged_sample_points[['x_sample_point','y_sample_point']]=df_tagged_sample_points['sample_point'].apply(pd.Series)

#get the amount of points for each tag 
        df_counts= pd.DataFrame(df_tagged_sample_points["tag"].value_counts())

#change the columns names of dataframe
        df_counts.columns=["count"]

        sampling_backgroud_points_count=df_counts.loc[backgroud_tag,"count"]
        sampling_polygon_points_count=df_counts.loc[polygon_tag,"count"]

#take the previous value in this annotation
        new_annotation=jsonrecords[record_index]['annotations']

#add new points in json annotation and in image
        for row in df_tagged_sample_points.itertuples():
        #unpack tuple
            index,sample_point,tag,radius_size,x_sample_point,y_sample_point = row
        #get a sample point to append in annotation json file
            new_annotation.append({
                        "class": tag,
                        "x": x_sample_point,
                        "y": y_sample_point})
            if(tag == polygon_tag):
                im_draw.ellipse([(x_sample_point - r_point, y_sample_point - r_point),(x_sample_point + r_point, y_sample_point + r_point)], fill="yellow", outline="yellow")
            elif (tag == backgroud_tag):
                im_draw.ellipse([(x_sample_point - r_point, y_sample_point - r_point),(x_sample_point + r_point, y_sample_point + r_point)], fill="red", outline="red")

#set the updated annotation (previous + points sampling)
        jsonrecords[record_index]['annotations']=new_annotation

#save a new image with sample points
        fn_im_samples_points="{}_{}_{}{}".format(os.path.splitext(fn)[0],"samples-point",radius,os.path.splitext(fn)[1])

        im.save(fn_im_samples_points)

#save a new json file with annotations sample points
        fn_json_samples_points="{}_{}_{}{}".format(os.path.splitext(args.jsonfile)[0],"samples-point",radius,os.path.splitext(args.jsonfile)[1])

        with open(fn_json_samples_points, 'w') as f:
            json.dump(jsonrecords, f,indent=4)

#cut de polygon and save it as .png image
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
        fn_polygon_im="{}{}".format(os.path.splitext(fn)[0],"_polygon.png")
        newIm.save(fn_polygon_im)