#!/usr/bin/env python3
# coding: utf-8

import pandas as pd
import numpy as np
import sys
from funcoes import create_distance_matrix, idw_all_clustered
import time

def main():
    """
    Main function to run the cluster-aware IDW interpolation and sMAPE calculation.
    """
    if len(sys.argv) != 6:
        print('Usage: python method_IDW_clustered.py <threshold> <alpha> <rain_file> <output_file_prefix> <cluster_bonus>')
        sys.exit(1)

    # Command-line arguments
    threshold = int(sys.argv[1])
    alpha = int(sys.argv[2])
    rainfall_data_file = sys.argv[3]
    output_prefix = sys.argv[4]
    cluster_bonus = float(sys.argv[5])

    # Load clustered station features
    features_path = 'dataset/station_features_clustered.csv'
    try:
        df_features = pd.read_csv(features_path, index_col='Gauge')
        # The gauge ID might be read as a generic number, ensure it's a string for consistency
        df_features.index = df_features.index.astype(str)
    except FileNotFoundError:
        print(f"Error: Clustered features file not found at {features_path}")
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

    print("Data loaded successfully. Starting cluster-aware computation...")
    start_time = time.time()

    # Pre-compute the distance matrix from the 'lat' and 'lon' in the feature file
    dist_matrix = create_distance_matrix(df_features)

    # Get the cluster labels
    clusters = df_features['cluster']

    # Apply the clustered IDW function to each row (day) of the rainfall data
    daily_results = gauge_data.apply(
        lambda row: idw_all_clustered(row, dist_matrix, threshold, alpha, clusters, cluster_bonus),
        axis=1
    )

    # Filter out empty results and concatenate
    valid_results = [res for res in daily_results if res is not None]
    if not valid_results:
        print("No valid data to process. Exiting.")
        sys.exit(0)

    results_df = pd.concat(valid_results)

    # Vectorized sMAPE calculation
    results_df['erro_abs'] = (results_df['idw_value'] - results_df['real_value']).abs()
    results_df['erro_rel'] = results_df['idw_value'] + results_df['real_value']

    sMAPE_df = results_df.groupby('n_gauges_used').agg(
        total_erro_abs=('erro_abs', 'sum'),
        total_erro_rel=('erro_rel', 'sum')
    ).reset_index()

    sMAPE_df['sMAPE'] = sMAPE_df['total_erro_abs'] / sMAPE_df['total_erro_rel']
    sMAPE_df.loc[sMAPE_df['total_erro_rel'] == 0, 'sMAPE'] = 0

    end_time = time.time()
    print(f"Computation finished in {end_time - start_time:.2f} seconds.")

    output_filename = f"{output_prefix}_{alpha}_{threshold}_bonus_{cluster_bonus}_sMAPE.xlsx"
    sMAPE_df.to_excel(output_filename, index=False)
    print(f"Results saved to {output_filename}")

if __name__ == '__main__':
    main()
