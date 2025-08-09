import pandas as pd
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import numpy as np

def train_kmeans_and_find_k(features_path='dataset/station_features.csv'):
    """
    Loads the feature data, determines the optimal k for K-Means using the
    elbow method, and trains the final model.
    """
    try:
        df_features = pd.read_csv(features_path, index_col='Gauge')
    except FileNotFoundError:
        print(f"Error: Feature file not found at {features_path}")
        return

    # Select features for clustering
    # Using scaled coordinates and the one-hot encoded categorical features
    features_for_clustering = df_features[['lat_scaled', 'lon_scaled', 'region_planicie', 'density_menor', 'density_normal']]

    # --- Elbow Method to find optimal k ---
    print("Running Elbow Method to find optimal k...")
    inertia = []
    k_range = range(1, 11) # Test k from 1 to 10
    for k in k_range:
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        kmeans.fit(features_for_clustering)
        inertia.append(kmeans.inertia_)

    # Plot the elbow curve
    plt.figure(figsize=(8, 5))
    plt.plot(k_range, inertia, marker='o')
    plt.title('Elbow Method for Optimal k')
    plt.xlabel('Number of clusters (k)')
    plt.ylabel('Inertia')
    elbow_plot_path = 'elbow_method.png'
    plt.savefig(elbow_plot_path)
    print(f"Elbow method plot saved to {elbow_plot_path}")

    # Heuristically determine the "elbow" point
    # We can do this by finding the point with the maximum distance to a line
    # drawn between the first and last points.
    p1 = np.array([k_range[0], inertia[0]])
    p2 = np.array([k_range[-1], inertia[-1]])

    distances = []
    for i in range(len(k_range)):
        p3 = np.array([k_range[i], inertia[i]])
        dist = np.linalg.norm(np.cross(p2-p1, p1-p3))/np.linalg.norm(p2-p1)
        distances.append(dist)

    optimal_k = k_range[np.argmax(distances)]
    print(f"Optimal k determined to be: {optimal_k}")

    # --- Train final model with optimal k ---
    print(f"Training final KMeans model with k={optimal_k}...")
    kmeans_final = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
    df_features['cluster'] = kmeans_final.fit_predict(features_for_clustering)

    # Save the clustered features
    output_path = 'dataset/station_features_clustered.csv'
    df_features.to_csv(output_path)

    print("Clustering complete.")
    print(df_features[['lat', 'lon', 'cluster']].head())
    print(f"Clustered feature data saved to {output_path}")

if __name__ == '__main__':
    train_kmeans_and_find_k()
