import pandas as pd
import numpy as np
from funcoes import create_distance_matrix
import time
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

def smape(y_true, y_pred):
    """
    Calculates the Symmetric Mean Absolute Percentage Error (sMAPE).
    """
    numerator = np.abs(y_pred - y_true)
    denominator = (np.abs(y_true) + np.abs(y_pred)) / 2
    # Handle the case where the denominator is zero
    return np.mean(np.divide(numerator, denominator, out=np.zeros_like(numerator, dtype=float), where=denominator!=0)) * 100

def run_pipeline(N_NEIGHBORS=5, ROW_LIMIT=20000):
    """
    Full pipeline: feature engineering, training with RandomForest, and evaluation.
    """
    # --- 1. Feature Engineering ---
    print("Loading data...")
    rain_df = pd.read_excel('dataset/dados_chuva_planicie.xlsx', index_col='Date')
    rain_df.columns = rain_df.columns.astype(str)

    features_df = pd.read_csv('dataset/station_features_clustered.csv', index_col='Gauge')
    features_df.index = features_df.index.astype(str)

    dist_matrix = create_distance_matrix(features_df)

    rain_long_df = rain_df.reset_index().melt(
        id_vars='Date', var_name='Gauge', value_name='Rainfall'
    ).dropna(subset=['Rainfall'])

    if ROW_LIMIT:
        rain_long_df = rain_long_df.head(ROW_LIMIT)

    print(f"Processing {len(rain_long_df)} measurements.")

    all_features = []
    nearest_neighbors = {
        gauge_id: dist_matrix[gauge_id].sort_values().drop(gauge_id).head(N_NEIGHBORS).index.tolist()
        for gauge_id in features_df.index
    }
    rain_by_date = rain_df.T.to_dict('series')

    print("Engineering features...")
    for _, row in rain_long_df.iterrows():
        date, current_gauge, target_rainfall = row['Date'], row['Gauge'], row['Rainfall']
        daily_rain = rain_by_date.get(date)
        if daily_rain is None: continue

        feature_row = {'Date': date, 'Gauge': current_gauge, 'Target_Rainfall': target_rainfall}
        neighbors = nearest_neighbors[current_gauge]
        for i, neighbor_id in enumerate(neighbors):
            feature_row[f'n{i+1}_rain'] = daily_rain.get(neighbor_id, 0) # Fillna with 0
            feature_row[f'n{i+1}_dist'] = dist_matrix.loc[current_gauge, neighbor_id]
            feature_row[f'n{i+1}_cluster'] = features_df.loc[neighbor_id, 'cluster']
        all_features.append(feature_row)

    supervised_df = pd.DataFrame(all_features)
    print("Feature engineering complete.")

    # --- 2. Data Splitting ---
    print("Splitting data...")
    supervised_df['Date'] = pd.to_datetime(supervised_df['Date'])

    unique_dates = sorted(supervised_df['Date'].unique())
    split_point = unique_dates[int(len(unique_dates) * 0.8)]

    train_df = supervised_df[supervised_df['Date'] < split_point]
    test_df = supervised_df[supervised_df['Date'] >= split_point]

    features = [col for col in supervised_df.columns if col not in ['Date', 'Gauge', 'Target_Rainfall']]
    X_train = train_df[features]
    y_train = train_df['Target_Rainfall']
    X_test = test_df[features]
    y_test = test_df['Target_Rainfall']

    print(f"Train set size: {len(X_train)}, Test set size: {len(X_test)}")

    # --- 3. Model Training ---
    print("Training RandomForestRegressor model...")
    model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1, max_depth=10)
    model.fit(X_train, y_train)

    # --- 4. Prediction and Verification ---
    print("Making predictions and evaluating...")
    predictions = model.predict(X_test)

    final_smape = smape(y_test, predictions)
    print(f"\n--- Supervised Model Results ---")
    print(f"sMAPE on test set: {final_smape:.4f}%")
    print("------------------------------")

if __name__ == '__main__':
    run_pipeline()
