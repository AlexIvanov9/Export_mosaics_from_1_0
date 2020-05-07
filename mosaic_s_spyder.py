import improc
from improc import dbops
from improc.dbops import find, parse, utils, spatial
from improc.gen import wcutils, osops, dirfuncs

import os,glob,shutil,json,tempfile,datetime,csv 
import pandas as pd
import geopandas as gp



def get_flights(daysback = 0):
    """
    get flights from days back. 0 is today. 
    running function in different time zones might need adjustment on daysback

    """
    dbops.dbio.reload_database()
    flights = dbops.dbio.get_table("Flights")
    today = pd.to_datetime("today").date()
    past_date = pd.datetime(today.year,today.month, today.day - daysback).date()
    f = flights[flights.Date == past_date]
    past_flights = list(f.index.values)
    print("\nFlights from Date {}: ".format(past_date))
    
    return past_flights


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
            psz_camera_list = [x for x in psz_list if camera.lower in x.lower()]
            psz_watch_list.extend(psz_camera_list)
        print(psz_watch_list)
        # gather .psz id info and write to JSON to pass on to photoscan 1.0
        for psz in psz_watch_list:
            mosaic = psz.replace('.psz', '.tif')
            mosaic = mosaic.replace('processing', 'mosaic/alternate')
            if not os.path.isfile(mosaic):
                print('will export photoscan 1.0 mosaic for {}'.format(psz))
                block_id = dbops.parse.get_block_id(psz)
                camera = dbops.parse.get_camera(psz)[1]
                
                # write code to pass on flight_id, block_id and camera info to JSON, which will be read by photoscan console
                
                
                
                
                
                ###############   

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
                print('Registering {}''.format(mosaic))
                improc.georeference.to_current_vnir(mosaic)

    dirfuncs.watch_directories(flight_alternate_mosaic_paths,subroutine)