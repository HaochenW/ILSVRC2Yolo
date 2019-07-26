# ILSVRC2Yolo
A format translator used for object detection label translation, which could translate ILSVRC2015_VID file into Yolo Darknet file.

## Installation and Utilization 
##### Clone
    $ git clone https://github.com/HaochenW/ILSVRC2Yolo
    $ cd ILSVRC2Yolo/
	
##### Direct utilization
    $ python transxml.py --dataset_path your_ILSVRC_dataset_path


## Required Parameters
1. --dataset_path
- ILSVRC_VID dataset path, for example:

     ```bash
     --dataset_path ./ILSVRC2015
     ```
	 
 2. --convert_output_path
- The output path after the conversion, for example, you could use: 
- 
     ```bash
     --convert_output_path ./ILSVRC2015/Annotation_yolo
     ```
	 
 3.  --abs_path
- The output path of the image absolute path file, which is needed in training yolo model.
     ```bash
     --abs_path ./ILSVRC2015/Annotation_yolo
     ```
	 
 4. --cls_list_file
- The file that gives the name and number of the classes, the file is given in the folder
     ```bash
     --abs_path ./classes_ILSVRC.names
     ```
 5. --img_type
 - The type of the dataset image, in ILSVRC, it is .JPEG.
     ```bash
     --image_type .JPEG
     ```

## Results

- The results will in the folder: "--convert_output_path"
- The folder nesting format will be the same as the folder in "Annotation", but the ".xml" format will be translated into ".txt' format

**`000465.txt`**

     ```bash
	  22 0.438 0.497 0.496 0.994
     ```
	 
**`valid.txt`**

	```bash
	/home/users/../code/ILSVRC2015/Data/VID/val/ILSVRC2015_val_00138000/000247.JPEG
	/home/users/../code/ILSVRC2015/Data/VID/val/ILSVRC2015_val_00138000/000078.JPEG
	/home/users/../code/ILSVRC2015/Data/VID/val/ILSVRC2015_val_00138000/000075.JPEG
	/home/users/../code/ILSVRC2015/Data/VID/val/ILSVRC2015_val_00138000/000043.JPEG
	/home/users/../code/ILSVRC2015/Data/VID/val/ILSVRC2015_val_00138000/000013.JPEG
	```
