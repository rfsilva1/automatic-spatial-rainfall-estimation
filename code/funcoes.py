import math
import numpy as np

import logging as logger
fmt = "%(filename)s:%(lineno)s - %(funcName)s() - %(message)s"
logger.basicConfig(filename='idw.log', level=logger.DEBUG, format=fmt)

def calc_distance(lon1, lat1, lon2, lat2):
    """
    source: rafatieppo 
    lon, lat: longitude and latitude in decimal degrees
    return the distance between two coordinates in km
    """
    rad = math.pi / 180  # degree to radian
    R = 6378.1  # earth average radius at equador (km)
    dlon = (lon2 - lon1) * rad
    dlat = (lat2 - lat1) * rad
    a = (math.sin(dlat / 2)) ** 2 + math.cos(lat1 * rad) * \
        math.cos(lat2 * rad) * (math.sin(dlon / 2)) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = R * c
    return d

def get_coord_by_id(id, coords):
    """
    id: gauge name
    coords: file with gauge names and respective coordinates
    return the gauge coordinates
    """
    return coords[id]['lat'], coords[id]['lon']

def get_coord_by_ids(ids, coords):
    """
    ids: list with gauge names 
    coods: file with gauge names and respective coordinates
    return the coordinates by gauge name
    """
    lat_list, lon_list = [], []
    for id in ids:
        lat, lon = get_coord_by_id(id, coords)
        lat_list.append(lat)
        lon_list.append(lon)
    return lat_list, lon_list

def idw(x, y, orig_rain, xi, yi, alpha):
    """
    x: latitude vector of known points
    y: longitude vector of known points
    orig_rain: vector w/ rainfall values of the known gauges
    xi: latitude vector of unknown points
    yi: longitude vector of unknown points
    return the interpolated rainfall value
    """
    idw_rain = []
    idw_only_rain = []
    lst_dist = []

    for s in range(len(x)):
        d = calc_distance(x[s], y[s], xi, yi)
        lst_dist.append(d)
    
    sumsup = list((1 / np.power(lst_dist, alpha)))
    suminf = np.sum(sumsup)

    sumsup = np.sum(np.array(sumsup) * np.array(orig_rain))
    u = sumsup / suminf
    return u

def radius_filter(gauges, rainfall, unknow_lat, unknow_lon, threshold, coords):
    """
    function that selects gauges that are within a defined distance radius
    return the coordinates, rainfall values and ids of gauges that are inside the threshold
    """
    ids_usados, new_lat_list, new_lon_list, new_rainfall = [],[],[],[]
    lat_list, lon_list = get_coord_by_ids(gauges, coords)
    for id, lat, lon, rain in zip(gauges, lat_list, lon_list, rainfall):
        distance = calc_distance(lat, lon, unknow_lat, unknow_lon)
#         print('distancia', distance)
        if distance < threshold:
            new_lat_list.append(lat)
            new_lon_list.append(lon)
            new_rainfall.append(rain)
            ids_usados.append(id)
    return new_lat_list, new_lon_list, new_rainfall, ids_usados

def get_original_values(list_gauges, list_rain):
    return list_gauges.copy(), list_rain.copy()

def idw_all(list_gauges, list_rain, threshold, coords, alpha):
    """
    function to calculate IDW for each line, switching each gauge as the unknown point at a time
    """
    lista_values = []
    lista_ids_usados = []
    lista_ids_unknows = []
    lista_rainfall_real = []
    # makes combinations to select the unknown point
    for id, rain in zip (list_gauges, list_rain):
#         print('========================================================')
        gauges, rainfall = get_original_values(list_gauges, list_rain)
        gauges.remove(id)
        rainfall.remove(rain)
        lat_list, lon_list = get_coord_by_ids(gauges, coords)
        unknow_lat, unknow_lon = get_coord_by_id(id, coords)
#         print('lat_list completa', lat_list)
#         print('lon_list completa', lon_list)
#         print('rainfall completa', rainfall)
#         print('ids completos', gauges)

        lat_list, lon_list, rainfall, ids_usados = radius_filter(gauges, rainfall, unknow_lat, unknow_lon, threshold, coords)

#         print('lon_list novo', lon_list)
#         print('rainfall novo', rainfall)
#         print('ids novo', ids_usados)
        if lat_list:
            value = idw(lat_list, lon_list, rainfall, unknow_lat, unknow_lon, alpha)
    #         print('idw:', value)
            lista_values.append(value)
            lista_ids_usados.append(ids_usados)
            lista_ids_unknows.append(id)
            lista_rainfall_real.append(rain)
    return lista_values, lista_ids_usados, lista_ids_unknows, lista_rainfall_real

def count_gauges(x):
    """
    count the number of gauges used to obtain the correspondent idw value
    """
    lista = []
    for i in x:
        lista.append(len(i))
    return lista