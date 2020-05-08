import improc
from improc import dbops
from improc.dbops import find, parse, utils, spatial
from improc.gen import wcutils, osops, dirfuncs

import os,glob,shutil,json,tempfile,datetime,csv,time
import pandas as pd
import geopandas as gp



def get_flights(daysback = 0):
    """
    get flights from days back. 0 is today. 
    running function in different time zones might need adjustment on daysback
    """
    import worksclient as wc
    
    now_time = datetime.datetime.today()
    today_date = now_time.strftime("%Y-%m-%d")
    target_time = now_time - datetime.timedelta(daysback)
    target_date = target_time.strftime("%Y-%m-%d")
    print("Today is {} \nGetting Flights from {}: ".format(today_date, target_date))
    
    flight_list = []
    flight_dic_list = wc.Flight.list(target_date)
    for i in flight_dic_list:
        flight_list.append(i['id'])
    flight_list.sort()
    
    return flight_list





def write_to_json(psz,flight_id,field_id,camera,mosaic):
    """
    add information about project to json 
    sleep for 5 sec 
    check if fields already in json file, just added to list one more field for export
    """
    #if run form Jupiter to save json for read from Photoscan
    txtpath = os.path.join("/home/",os.path.join(os.environ['USER'],"flights/Distributer team/ProjectPath9.txt"))
    #txtpath = 'C:\Daily artifacts\ProjectPath.txt'
    fieldinfo = [{'ProjectPath': psz,
                'Flight_id' : flight_id,
                'Field': field_id,
                'Camera': camera.lower(),
                'Mosaic': mosaic}]
    try:
        # first time will be empty, just temporary solution
        content = json.loads(open(txtpath).read())
    except Exception as e:
        content = []
        print(e)
    
    f= open(txtpath,"w+")
    if len(content) == 0:
        json.dump(fieldinfo,f)
        f.close
        return
    
    if type(content).__name__ == "list":
        content.append(fieldinfo[0])
        json.dump(content,f)
        f.close
        return
    # add log file with a note about error or exception
    
    

def watch_new_psz(flight_list, camera_list=['jenoptik']):
    
    """
    Watches for new psz files in a group of flight_dirs.

    Parameters
    ----------
    flight_list : list
        List of flight_id integers

    """

    flight_processing_paths = []
    for flight_id in flight_list:
        flight_processing_paths.append(dirfuncs.guess_flight_dir(flight_id,'processing'))
    flight_processing_paths = [x for x in flight_processing_paths if x is not None]

    def subroutine(filenames):
        #filter psz files,
        psz_watch_list = []
        psz_list = [x for x in filenames if x.endswith('.psz')]
        for camera in camera_list:
            psz_camera_list = [x for x in psz_list if camera.lower() in x.lower()]
            psz_watch_list.extend(psz_camera_list)
        print(psz_watch_list)
        # gather .psz id info and write to JSON to pass on to photoscan 1.0
        for psz in psz_watch_list:
            mosaic = psz.replace('.psz', '.tif')
            mosaic = mosaic.replace('processing', 'mosaic/alternate')
            if not os.path.isfile(mosaic):
                print('will export photoscan 1.0 mosaic for {}'.format(psz))
                flight_id = dbops.parse.get_flight_id(psz)
                block_id = dbops.parse.get_block_id(psz)
                camera = dbops.parse.get_camera(psz)[1]
                # write code to pass on flight_id, block_id and camera info to JSON, which will be read by photoscan console
                write_to_json(psz,flight_id,block_id,camera,mosaic)

    dirfuncs.watch_directories(flight_processing_paths,subroutine)


def watch_register_alternate_tr_mosaics(flight_list):
    
    """
    Watches for new alternate mosaics in a group of flight_dirs.

    Parameters
    ----------
    flight_list : list
        List of flight_id integers

    """

    flight_alternate_mosaic_paths = []
    for flight_id in flight_list:
        flight_mosaic_path = dirfuncs.guess_flight_dir(flight_id,'mosaic')
        flight_alternate_mosaic_paths.append(os.path.join(flight_mosaic_path, 'alternate'))
    flight_alternate_mosaic_paths = [x for x in flight_alternate_mosaic_paths if x is not None]

    def subroutine(filenames):
        #filter tif files
        tr_mosaic_list = [x for x in filenames if x.endswith(".tif") and 'jenoptik' in x.lower()]
        print(tr_mosaic_list)
        #register mosaic if it hasn't been registered yet
        for mosaic in tr_mosaic_list:
            if not os.path.isfile(mosaic.replace('mosaic','registered')):
                print('Registering {}'.format(mosaic))
                improc.georeference.to_current_vnir(mosaic)

    dirfuncs.watch_directories(flight_alternate_mosaic_paths,subroutine)



# how to detect if all fileds was exported and to add new flights 

    
watch_new_psz(get_flights())
#watch_register_alternate_tr_mosaics(get_flights())