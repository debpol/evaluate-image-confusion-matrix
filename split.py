#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 14 16:34:58 2018

@author: deby
"""
import os, random, shutil, math, glob, argparse

parser = argparse.ArgumentParser(description='Slipt dataset into teat and training sets')
parser.add_argument("-dir", dest="all_data_dir", type=str,required=True, help="Directory with all data to split")
parser.add_argument("-trdir", dest="training_data_dir", type=str,required=True, help="Directory to put the training data. If it not exist, will be created")
parser.add_argument("-tsdir", dest="testing_data_dir", type=str,required=True, help="Directory to put the test data. If it not exist, will be created")
parser.add_argument("-trpct", dest="trainning_pct", type=float,required=True, help="percentage for training. It must be: 0 < pct < 1 ")
parser.add_argument("-ext", dest="file_ext", type=str,required=True, help="file extension")
args = parser.parse_args()



def copyFiles(fn_list, dir_destination):
    if not os.path.exists(dir_destination):
            os.mkdir(dir_destination)
    for fn in fn_list:        
        shutil.copy2(fn, dir_destination)


def splitData(fn_list, perc):
    random.shuffle(fn_list)
    if ((0.0 < perc < 1 ) and len(fn_list) > 1 ):
        training_count= int(math.ceil(len(fn_list)*perc))
    training_list = fn_list[:training_count]
    test_list = fn_list[training_count:]
    return training_list, test_list


def split_dataset_into_test_and_train_sets(all_data_dir, training_data_dir, testing_data_dir, trainning_pct, file_ext):
    fn_list=[]
    if os.path.exists(all_data_dir):
        fn_list = glob.glob("{}{}{}".format(all_data_dir,"/*.",file_ext))
        
        training_list, test_list = splitData(fn_list, trainning_pct)
        copyFiles(training_list, training_data_dir)
        copyFiles(test_list,testing_data_dir)
        
split_dataset_into_test_and_train_sets(args.all_data_dir, args.training_data_dir, args.testing_data_dir, args.trainning_pct, args.file_ext)
