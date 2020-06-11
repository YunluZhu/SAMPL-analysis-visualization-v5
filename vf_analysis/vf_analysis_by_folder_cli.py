'''
20.06.01 VF analysis cli - by folders
Take one command line input as the directory containing subfolders with .dlm files
Call grab_fish_angle and analysis .dlm files in the subfolders
Store analyzed values of .dlm files in subfolders within subfolders 
but not concatenate results across .dlm files in different subfolders
Note: The depth of subfolders containing .dlm files does not matter
'''

import sys
import os,glob
from grab_fish_angle import grab_fish_angle
import time

def main(root):
    all_folders = os.walk(root)
    for path, dir_list, file_list in all_folders:
        # loop through each subfolder
        for folder_name in dir_list:
            # get the folder dir by joining path and subfolder name 
            folder = os.path.join(path, folder_name)        
            filenames = glob.glob(f"{folder}/*.dlm") # subject to change
            # print(f"{len(filenames)} file(s) detected")
            if filenames:
                print(f"In {folder_name}")
                grab_fish_angle.run(filenames, folder)
                
if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) == 1:
        main(args[0])
        # main("/Users/yunluzhu/Lab/! Lab2/Python VF/script/vertical_fish_analysis/tests/test_data")
    else:
        print('too many/few args, should just be the file path!')
        