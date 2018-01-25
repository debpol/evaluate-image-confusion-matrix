#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Jan  9 11:49:11 2018

@author: deby
"""

import argparse
import numpy as np
from PIL import Image, ImageDraw
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sb
import os

SEA=0
DOLPHIN=255

parser = argparse.ArgumentParser(description='Draws the ROI as rectangle on binarized image, based on pixels distribution, according to minimum and maximum percentile given.')
parser.add_argument("-ib", dest="binarized_im", type=str, required=True, help=".jpg file binarized image")
parser.add_argument("-pmin", dest="p_min", type=int, required=True, help="minimum percentile. must be a integer numbre between [1-100]")
parser.add_argument("-pmax", dest="p_max", type=int, required=True, help="maximum percentile. must be a integer numbre between [1-100]")
args = parser.parse_args()


fn_im= args.binarized_im 
p_min=args.p_min
p_max=args.p_max

original_im = Image.open(fn_im).convert("L")

# convert to numpy 
np_im = np.asarray(original_im)

# binarize
np_im_bin=np.where(np_im == DOLPHIN,DOLPHIN,SEA)

# convert to DataFrame 
df_im_bin=pd.DataFrame(np_im_bin)

#calculate the sum of dolphin pixels by column
df_counts_x=pd.DataFrame(df_im_bin.apply(pd.value_counts).fillna(0).loc[DOLPHIN])
df_counts_x.columns =['dolphin_count_by_column']

#calculate the sum of dolphin pixels by row
df_im_bin_trasp= df_im_bin.transpose()
df_counts_y = pd.DataFrame(df_im_bin_trasp.apply(pd.value_counts).fillna(0).loc[DOLPHIN])
df_counts_y.columns =['dolphin_count_by_row']

#taking statistics in X axis (image's columns)
#with numpy and pandas
#guardo los indices de las columnas donde contabilizo mas del p_min y menos del p_max
perc_col=np.percentile(df_counts_x, [p_min,p_max])
index_col=pd.Series(df_counts_x.index[(df_counts_x['dolphin_count_by_column'] > int(perc_col[0])) & (df_counts_x['dolphin_count_by_column'] < int(perc_col[1]))].tolist())

#with pandas
#stats_columns=df_counts_x.describe()
#pd.Series(np.where(df_counts_x.dolphin_count_by_column>stats_columns.loc["25%","dolphin_count_by_column"]))

#plots X
#dict_sta_col, bp_col = pd.DataFrame.boxplot(df_counts_x, return_type='both',vert=True)
#df_counts_x.plot.area()

#taking statistics in Y axis (image's rows)
#with numpy and pandas
#guardo los indices de las filas donde contabilizo mas del p_min y menos del p_max
perc_row=np.percentile(df_counts_y, [p_min,p_max])
index_row=pd.Series(df_counts_y.index[(df_counts_y['dolphin_count_by_row'] > int(perc_row[0])) &(df_counts_y['dolphin_count_by_row'] < int(perc_row[1])) ].tolist())

#with pandas
#stats_rows=df_counts_y.describe()

#plots Y
#dict_sta_row, bp_row = pd.DataFrame.boxplot(df_counts_y, return_type='both',vert=True)
#df_counts_y.plot.area()


index_col_max=index_col.max()
index_col_min=index_col.min()
index_row_max=index_row.max()
index_row_min=index_row.min()

fn_roi_im="{}_{}_{}-{}{}".format(os.path.splitext(fn_im)[0],"ROI",p_min,p_max,os.path.splitext(fn_im)[1])

draw_roi_im = ImageDraw.Draw(original_im)
draw_roi_im.rectangle(((index_col_min,index_row_min),(index_col_max,index_row_max)), outline = "black")
original_im.save(fn_roi_im)


# ========= to cropp the ROI========================================================
# box = map(int, [index_col_min,index_row_min, index_col_max,index_row_max])
# cropped=b_im.crop(box)
# cropped.save(path_crop)
# =============================================================================
