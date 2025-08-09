import math
import numpy as np
import pandas as pd

import logging as logger
fmt = "%(filename)s:%(lineno)s - %(funcName)s() - %(message)s"
logger.basicConfig(filename='idw.log', level=logger.DEBUG, format=fmt)

def haversine_distance(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance in kilometers between two points
    on the earth (specified in decimal degrees).
    Vectorized version that supports broadcasting.
    """
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])

    R = 6378.1  # Using the same Earth radius as the original script

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = np.sin(dlat/2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2.0)**2
    c = 2 * np.arcsin(np.sqrt(a))
    km = R * c
    return km

def create_distance_matrix(coords_df):
    """
    Creates a distance matrix between all gauges using numpy broadcasting.
    coords_df: pandas DataFrame with 'lat' and 'lon' columns and gauge IDs as index.
    Returns a DataFrame with the distance matrix.
    """
    station_ids = coords_df.index
    lats = coords_df['lat'].values
    lons = coords_df['lon'].values

    # Reshape for broadcasting
    lats1 = lats[:, np.newaxis]
    lons1 = lons[:, np.newaxis]
    lats2 = lats[np.newaxis, :]
    lons2 = lons[np.newaxis, :]

    # Calculate all distances at once
    distances = haversine_distance(lons1, lats1, lons2, lats2)

    dist_matrix = pd.DataFrame(distances, index=station_ids, columns=station_ids)
    return dist_matrix

def idw_all_vectorized(daily_rain, dist_matrix, threshold, alpha):
    """
    Calculates IDW for all gauges in a vectorized manner for a single day.

    daily_rain: A pandas Series with rainfall data for one day. Index is gauge ID.
    dist_matrix: A pre-computed pandas DataFrame with distances between all gauges.
    threshold: The radius distance to consider gauges from.
    alpha: The exponent for IDW.

    Returns a DataFrame with 'idw_value', 'real_value', and 'n_gauges_used'.
    """
    # Find gauges with valid data for this day
    valid_gauges = daily_rain.dropna()
    valid_ids = valid_gauges.index

    # If less than 2 gauges have data, we can't interpolate
    if len(valid_ids) < 2:
        return None

    # Subset the distance matrix for valid gauges
    sub_dist_matrix = dist_matrix.loc[valid_ids, valid_ids]

    # Prepare results list
    results = []

    # Loop through each gauge to treat it as the unknown point
    for unknown_id in valid_ids:

        # Get real rainfall value for the unknown gauge
        real_value = valid_gauges[unknown_id]

        # Known points are all other valid gauges
        known_ids = valid_ids.drop(unknown_id)

        # If no other gauges, cannot interpolate
        if known_ids.empty:
            continue

        # Get distances from the unknown gauge to all known gauges
        distances = sub_dist_matrix.loc[unknown_id, known_ids]

        # Apply radius filter
        gauges_in_radius = distances[distances < threshold]

        # If no gauges are within the radius, skip
        if gauges_in_radius.empty:
            continue

        # Get rainfall values for the gauges in the radius
        known_rains = valid_gauges[gauges_in_radius.index]

        # Calculate IDW
        # Handle cases where distance is zero to avoid division by zero
        with np.errstate(divide='ignore'):
            weights = 1.0 / np.power(gauges_in_radius, alpha)

        # If a known point is at the same location as the unknown point, its weight will be inf.
        # In this case, the interpolated value is simply the value of that known point.
        if np.isinf(weights).any():
            idw_value = known_rains[weights == np.inf].values[0]
        else:
            idw_value = np.sum(weights * known_rains) / np.sum(weights)

        results.append({
            'unknown_id': unknown_id,
            'idw_value': idw_value,
            'real_value': real_value,
            'n_gauges_used': len(gauges_in_radius)
        })

    if not results:
        return None

    return pd.DataFrame(results)
