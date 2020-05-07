# -*- coding: utf-8 -*-
"""
Run from Photoscan 1.0
1. Watch JSON file (every 60 sec at this moment):
    - if there is more than one element take this element proccess and delete this element from JSON file
2. Open project and export 1.0 mosaic

"""

import PhotoScan
import os
import time
import mosaic
import json



def export_ortho(fieldinfo):
    """
    Read JSON file with flight path, flight id and field id
    Using this information Run export mosaic 1.0
    """
    
    export_path = fieldinfo['ProjectPath']
    try:
        project = PhotoScan.app.document
        project.open(fieldinfo['ProjectPath'])
        
        dx, dy = mosaic.get_resolution(fieldinfo['Flight_id'], fieldinfo['Field'], fieldinfo['Camera'])
        
        status = project.activeChunk.exportOrthophoto(
        export_path, format="tif", color_correction=False, blending='average', dx=dx, dy=dy,
        projection=project.activeChunk.projection)
        if status is False:
            print("Bad")
            # Need add log file with errors 
    except Exception as e:
        # Need add log file with errors 
        print(e)
        
    return


def get_path_from_json (txtpath):
    """
    take path project from json file
    
    return
    ------
    list with infromation about project and another part of json for overwrite txt doc
    """
    f= open(txtpath,"r")
    contents = json.load(f)
    f.close        
    return contents[0],contents[1:]



def deleted_first_element(txtpath,contentjson):
    """
    write to the json another projects
    """
    f= open(txtpath,"w")
    if len(contentjson) == 0:
        f.close
        return
    json.dump(contentjson,f)
    f.close
    return



def check_lines(txt_file):
    """
    check txt file for count of project
    if there are more then 1 path return true
    if there is no path freeze script for 60 sec
    """
    file = open(txt_file).read()
    if len(file) >= 1:
        return True
    else:
        time.sleep(60)
        return False
    

projectpath = 'C:\Daily artifacts\ProjectPath.txt'



while True:
    if check_lines(projectpath):
        content = get_path_from_json (projectpath)
        deleted_first_element(projectpath, content[1])
        export_ortho(content[0])
        

    
