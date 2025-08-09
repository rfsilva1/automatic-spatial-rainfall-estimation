import pandas as pd
from sklearn.preprocessing import StandardScaler
import numpy as np

def create_feature_dataframe():
    """
    Loads data from various source files, merges them, and engineers features
    for the machine learning model.
    """
    # Load the main station lists
    df_planicie = pd.read_excel('dataset/estacoes_planicie.xlsx')
    df_planalto = pd.read_excel('dataset/estacoes_planalto.xlsx')

    # Add the 'region' feature
    df_planicie['region'] = 'planicie'
    df_planalto['region'] = 'planalto'

    # Load the density files
    df_maior = pd.read_csv('dataset/maior_densidade.csv', delimiter=';')
    df_menor = pd.read_csv('dataset/menor_densidade.csv', delimiter=';')

    # Combine the main dataframes
    df_all_stations = pd.concat([df_planicie, df_planalto], ignore_index=True)
    df_all_stations.drop_duplicates(subset=['Gauge'], inplace=True)
    df_all_stations.set_index('Gauge', inplace=True)

    # Create the 'density' feature
    df_all_stations['density'] = 'normal'
    # Use .loc to safely assign to the index
    if df_maior['Gauge'].iloc[0] in df_all_stations.index:
        df_all_stations.loc[df_maior['Gauge'].iloc[0], 'density'] = 'maior'
    if df_menor['Gauge'].iloc[0] in df_all_stations.index:
        df_all_stations.loc[df_menor['Gauge'].iloc[0], 'density'] = 'menor'

    # --- Feature Correction and Engineering ---

    # As discovered, the lat/lon columns are swapped in the source files.
    # Correcting this for all stations.
    df_all_stations.rename(columns={'lat': 'lon_temp', 'lon': 'lat'}, inplace=True)
    df_all_stations.rename(columns={'lon_temp': 'lon'}, inplace=True)

    # --- Prepare for ML ---

    # One-hot encode categorical features
    df_features = pd.get_dummies(df_all_stations, columns=['region', 'density'], drop_first=True)

    # Scale numerical features
    scaler = StandardScaler()
    scaled_coords = scaler.fit_transform(df_features[['lat', 'lon']])
    df_features[['lat_scaled', 'lon_scaled']] = scaled_coords

    print("Feature DataFrame created successfully.")
    print(df_features.head())
    print(f"\nTotal stations: {len(df_features)}")

    # Save the final feature set
    output_path = 'dataset/station_features.csv'
    df_features.to_csv(output_path)
    print(f"Features saved to {output_path}")

    return df_features

if __name__ == '__main__':
    create_feature_dataframe()
