#!/usr/bin/env python3
# coding: utf-8

import pandas as pd
import numpy as np
import sys
from funcoes import create_distance_matrix, idw_all_vectorized
import time

def main():
    """
    Main function to run the IDW interpolation and sMAPE calculation.
    """
    if len(sys.argv) != 6:
        print('Usage: python method_IDW+.py <threshold> <alpha> <coord_file> <rain_file> <output_file_prefix>')
        sys.exit(1)

    # Command-line arguments
    threshold = int(sys.argv[1])
    alpha = int(sys.argv[2])
    coord_gauges_file = sys.argv[3]
    rainfall_data_file = sys.argv[4]
    output_prefix = sys.argv[5]

    # Load and prepare coordinates data
    try:
        df_coord = pd.read_excel(coord_gauges_file)
        df_coord['Gauge'] = df_coord['Gauge'].astype(str)
        df_coord = df_coord.set_index('Gauge')
        
        # FIX: The lat and lon columns are swapped in the source file.
        # Let's check if they exist before swapping.
        if 'lat' in df_coord.columns and 'lon' in df_coord.columns:
            df_coord.rename(columns={'lat': 'lon_temp', 'lon': 'lat'}, inplace=True)
            df_coord.rename(columns={'lon_temp': 'lon'}, inplace=True)
        else: # If they are named Latitude/Longitude
             df_coord.rename(columns={'Latitude': 'lon_temp', 'Longitude': 'lat'}, inplace=True)
             df_coord.rename(columns={'lon_temp': 'lon'}, inplace=True)

    except FileNotFoundError:
        print(f"Error: Coordinate file not found at {coord_gauges_file}")
        sys.exit(1)
    except Exception as e:
        print(f"Error loading or processing coordinate file: {e}")
        sys.exit(1)


    # Load and prepare rainfall data
    try:
        gauge_data = pd.read_excel(rainfall_data_file)
        gauge_data = gauge_data.set_index(['Date'])
        gauge_data.columns = [str(c) for c in gauge_data.columns]
        gauge_data.index = pd.to_datetime(gauge_data.index)
    except FileNotFoundError:
        print(f"Error: Rainfall data file not found at {rainfall_data_file}")
        sys.exit(1)
    except Exception as e:
        print(f"Error loading or processing rainfall data file: {e}")
        sys.exit(1)

    print("Data loaded successfully. Starting computation...")
    start_time = time.time()

    # Pre-compute the distance matrix
    dist_matrix = create_distance_matrix(df_coord)

    # Apply the vectorized IDW function to each row (day) of the rainfall data
    daily_results = gauge_data.apply(
        lambda row: idw_all_vectorized(row, dist_matrix, threshold, alpha),
        axis=1
    )

    # Filter out empty results and concatenate the rest into a single DataFrame
    valid_results = [res for res in daily_results if res is not None]
    if not valid_results:
        print("No valid data to process. Exiting.")
        sys.exit(0)

    results_df = pd.concat(valid_results)

    # Vectorized sMAPE calculation
    results_df['erro_abs'] = (results_df['idw_value'] - results_df['real_value']).abs()
    results_df['erro_rel'] = results_df['idw_value'] + results_df['real_value']

    # Group by the number of gauges used and calculate sMAPE
    sMAPE_df = results_df.groupby('n_gauges_used').agg(
        total_erro_abs=('erro_abs', 'sum'),
        total_erro_rel=('erro_rel', 'sum')
    ).reset_index()

    # Calculate final sMAPE score, handle division by zero
    sMAPE_df['sMAPE'] = sMAPE_df['total_erro_abs'] / sMAPE_df['total_erro_rel']
    sMAPE_df.loc[sMAPE_df['total_erro_rel'] == 0, 'sMAPE'] = 0 # Define sMAPE as 0 if sum is 0

    end_time = time.time()
    print(f"Computation finished in {end_time - start_time:.2f} seconds.")

    # Save the results to an Excel file
    output_filename = f"{output_prefix}_{alpha}_{threshold}_sMAPE.xlsx"
    try:
        sMAPE_df.to_excel(output_filename, index=False)
        print(f"Results saved to {output_filename}")
    except Exception as e:
        print(f"Error saving results to file: {e}")

if __name__ == '__main__':
    main()
