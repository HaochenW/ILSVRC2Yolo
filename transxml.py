# -*- coding: utf-8 -*-
"""
Created on Tue Jul 23 14:40:21 2019

@author: haochen01.wang
"""

import os,sys
import xml.etree.ElementTree as Et
from xml.etree.ElementTree import Element, ElementTree
from xml.etree.ElementTree import dump
import argparse



# template for ILSVRC_VID xml file
'''
n02411705: sheep
<annotation>
        <folder>ILSVRC2015_VID_train_0000/ILSVRC2015_train_00060013</folder>
        <filename>000000</filename>
        <source>
                <database>ILSVRC_2015</database>
        </source>
        <size>
                <width>1280</width>
                <height>720</height>
        </size>
        <object>
                <trackid>0</trackid>
                <name>n02411705</name>
                <bndbox>
                        <xmax>1091</xmax>
                        <xmin>606</xmin>
                        <ymax>371</ymax>
                        <ymin>46</ymin>
                </bndbox>
                <occluded>0</occluded>
                <generated>0</generated>
        </object>
        <object>
                <trackid>1</trackid>
                <name>n02411705</name>
                <bndbox>
                        <xmax>604</xmax>
                        <xmin>467</xmin>
                        <ymax>376</ymax>
                        <ymin>213</ymin>
                </bndbox>
                <occluded>0</occluded>
                <generated>0</generated>
        </object>
</annotation>
'''

def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█'):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
    source: https://github.com/ssaru/convert2Yolo/blob/master/Format.py
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s|%s| %s%% (%s/%s)  %s' % (prefix, bar, percent, iteration, total, suffix), end = '\r')
    # Print New Line on Complete
    if iteration == total:
        print("\n")
    

def parse(path):
    '''
    Get the information from the .xml file in the path
    changed from: https://github.com/ssaru/convert2Yolo/blob/master/Format.py
    '''
    try:
        (dir_path, dir_names, filenames) = next(os.walk(os.path.abspath(path)))
        data = {}
        progress_cnt = 0
        progress_length = len(filenames)
        printProgressBar(0, progress_length, prefix='\nILSVRC Parsing:'.ljust(15), suffix='Complete', length=40)

        for filename in filenames:
            if '.xml' in filename:
                # get root
                xml = open(os.path.join(dir_path,filename),"r") 
                tree = Et.parse(xml)
                root = tree.getroot()
                
                # get size information of a picture
                xml_size = root.find("size")
                size = {               
                    "width": xml_size.find("width").text,
                    "height":xml_size.find("height").text
                }
                
                # get objects information of a picture: num_bbox, bbox_info
                xml_objects = root.findall("object")
                
                
                if len(xml_objects) == 0:
                    annotation = {
                        "size":size,
                        "objects": None
                    }
                    data[root.find("filename").text.split(".")[0]] = annotation
                
                obj = {                   
                    "num_obj":len(xml_objects)           
                }     
                obj_index = 0
                for _object in xml_objects:
                    tmp = {
                        "name":_object.find("name").text
                    }
                    
                    xml_bndbox = _object.find("bndbox")
                    bndbox = {
                        "xmin":xml_bndbox.find("xmin").text,
                        "xmax":xml_bndbox.find("xmax").text,
                        "ymin":xml_bndbox.find("ymin").text,
                        "ymax":xml_bndbox.find("ymax").text
                    }
                    tmp["bndbox"] = bndbox
                    obj[str(obj_index)] = tmp
                    
                    obj_index += 1
                
                # The whole annotation information of a picture
                annotation = {
                    "size":size,
                    "objects":obj
                }
                
                # The whole information of the folder
                data[root.find("filename").text.split(".")[0]] = annotation
                printProgressBar(progress_cnt + 1, progress_length, prefix='ILSVRC Parsing:'.ljust(15), suffix='Complete', length=40)
                progress_cnt += 1
        return True, data
    
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        
        msg = "ERROR : {}, moreInfo : {}\t{}\t{}".format(e, exc_type, fname, exc_tb.tb_lineno)
        
        return False, msg

def coordinateCvt2YOLO(size,box):
    '''
    translate xmin,xmax,ymin,ymax into x,y,w,h
    changed from: https://github.com/ssaru/convert2Yolo/blob/master/Format.py
    '''
    dw = 1. / size[0]
    dh = 1. / size[1]
    
    # center
    x = (box[0] + box[1]) / 2.0
    y = (box[2] + box[3]) / 2.0
    
    w = box[1] - box[0]
    h = box[3] - box[2]
    
    # normalize
    x = x * dw
    w = w * dw
    y = y * dh
    h = h * dh
    
    return (round(x,3),round(y,3),round(w,3),round(h,3))

def name_list(file_path):
    with open(file_path,'r') as file:
        f = file.read().splitlines()
    for idx in range(0,len(f)):
        f[idx] = f[idx].split()
        f[idx] = f[idx][0]
    return f

def generate(data,file_path):
    '''
    from the dict, translate into output format
    changed from: https://github.com/ssaru/convert2Yolo/blob/master/Format.py
    '''
    try:
        progress_cnt = 0
        result = {}
        for key in data:
            img_width = int(data[key]["size"]["width"])
            img_height = int(data[key]["size"]["height"])
            
            contents = ""
            
            for idx in range(0, int(data[key]["objects"]["num_obj"])):
                xmin = data[key]["objects"][str(idx)]["bndbox"]["xmin"]
                ymin = data[key]["objects"][str(idx)]["bndbox"]["ymin"]
                xmax = data[key]["objects"][str(idx)]["bndbox"]["xmax"]
                ymax = data[key]["objects"][str(idx)]["bndbox"]["ymax"]
                
                b = (float(xmin),float(xmax),float(ymin),float(ymax))
                bb = coordinateCvt2YOLO((img_width, img_height), b)
                
                cls_list = name_list(file_path)
                cls_id = cls_list.index(data[key]["objects"][str(idx)]["name"]) + 1
                
                bndbox = "".join(["".join([str(e), " "]) for e in bb])       
                contents = "".join([contents, str(cls_id), " ", bndbox[:-1], "\n"])
                
            result[key] = contents
            progress_cnt += 1    
        return True, result
    
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]

        msg = "ERROR : {}, moreInfo : {}\t{}\t{}".format(e, exc_type, fname, exc_tb.tb_lineno)

        return False, msg   

def save(data, save_path, img_path, img_type, abs_path, flag):
    '''
    save the file
    changed from: https://github.com/ssaru/convert2Yolo/blob/master/Format.py
    '''
    if flag == False:
        return False, "info"
    try:
        progress_length = len(data)
        progress_cnt = 0
        printProgressBar(0, progress_length, prefix='\nYOLO Saving:'.ljust(15), suffix='Complete', length=40)
        
        if os.path.exists(os.path.abspath(os.path.join(abs_path, "train.txt"))) is False:
            f = open(os.path.abspath(os.path.join(abs_path, "train.txt")),"w")
            f.close()
            
        if os.path.exists(os.path.abspath(os.path.join(abs_path, "valid.txt"))) is False:
            f = open(os.path.abspath(os.path.join(abs_path, "valid.txt")),"w")
            f.close()
        
        # seperate the train file and valid file
        if 'train' in img_path:
            write_file = "train.txt"
        else:
            write_file = "valid.txt"
            
        with open(os.path.abspath(os.path.join(abs_path, write_file)),"a") as abs_path_file:
            for key in data:
                abs_path_file.write(os.path.abspath(os.path.join(img_path,"".join([key, img_type, "\n"]))))
                
                with open(os.path.abspath(os.path.join(save_path, "".join([key, ".txt"]))), "w")as output_txt_file:
                    output_txt_file.write(data[key])
        
                printProgressBar(progress_cnt + 1, progress_length, prefix='YOLO Saving:'.ljust(15),
                                 suffix='Complete',
                                 length=40)
                progress_cnt += 1
        return True, None
    
    except Exception as e:

        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]

        msg = "ERROR : {}, moreInfo : {}\t{}\t{}".format(e, exc_type, fname, exc_tb.tb_lineno)

        return False, msg
    

def list_dir(cur_path):
    '''
    recurrently list all the folder in a given path
    final_output: a dict, the key represent the folder name
    '''
    lsdir = os.listdir(cur_path)
    dirs = [i for i in lsdir if os.path.isdir(os.path.join(cur_path,i))]
    dirs_dict = {}
    
    if dirs:
        for folder in dirs:
            dirs_dict[folder] = list_dir(os.path.abspath(os.path.join(cur_path,folder)))  
            
    return dirs_dict

def translate2txt(save_path, label_path, img_path, folder_dict,abs_path):
    '''
    Recurrently save all the txt file into save_path, the folder form is the same as the .xml file
    in the Annotations file.
    The absolute path of all the Image file will be saved in the abs_path.txt
    '''
    save_path = os.path.abspath(save_path)
    if os.path.exists(save_path) is False:
        os.makedirs(save_path)
    label_path = os.path.abspath(label_path)
    img_path = os.path.abspath(img_path)
    
    if folder_dict:       
        for key in folder_dict:
            tmp = folder_dict[key]
            tmp_save_path = os.path.join(save_path,key)
            tmp_label_path = os.path.join(label_path, key)
            tmp_img_path = os.path.join(img_path, key)
            msg = translate2txt(tmp_save_path, tmp_label_path, tmp_img_path, tmp, abs_path)
    
    _, data = parse(label_path)
    flag, data = generate(data,names_path)
    _, msg = save(data, save_path, img_path, img_type, abs_path, flag)
    
    return msg
    
        
    
'''
please execute the code only once! Or you will see the empty folder with nothing!
'''

parser = argparse.ArgumentParser(description='label Converting example.')
parser.add_argument('--dataset_path', type=str, help='directory of image folder',default="./ILSVRC2015")
parser.add_argument('--convert_output_path', type=str, help='directory of label folder',default="./output")
parser.add_argument('--img_type', type=str, help='type of image',default=".JPEG")
parser.add_argument('--abs_path', type=str, help='directory of store all the absolute path of label file', default="./")
parser.add_argument('--cls_list_file', type=str, help='directory of *.names file', default="./classes_ILSVRC.names")

args = parser.parse_args()

if __name__ == '__main__':


    config ={
        "dataset_path":args.dataset_path,
        "img_type": args.img_type,
        "abs_path": args.abs_path,
        "output_path": args.convert_output_path,
        "cls_list": args.cls_list_file,
       }
    
    img_path = os.path.join(config["dataset_path"],'Data')
    label_path = os.path.join(config["dataset_path"],'Annotations')
    img_type = config["img_type"]
    abs_path = config["abs_path"]
    save_path = config["output_path"]
    names_path = config["cls_list"]
    
    '''
    1. List all the file folder in a given dict
    '''
    folder_dict = list_dir(label_path)     
    '''
    2. find the xml file in each folder
    3. change the name of the outermost folder name, then trans the file and save into new path;
       This step will execute with step 2 at the same time.
    '''
    abs_path = os.path.abspath(abs_path)
    msg = translate2txt(save_path, label_path, img_path, folder_dict,abs_path)
    

        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        