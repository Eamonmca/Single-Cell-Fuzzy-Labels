# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/02_KNN_Label_transfer.ipynb.

# %% auto 0
__all__ = ['knn_majority_voting', 'knn_weighted_voting', 'calculate_centroids', 'assign_labels_by_nearest_centroid', 'labels']

# %% ../nbs/02_KNN_Label_transfer.ipynb 5
from typing import List as List
from collections import Counter

def knn_majority_voting(indices: List[List[int]], # A list of lists, where each sublist contains the indices of the k-nearest neighbors in the reference dataset for a given query point.
                        reference_labels: List[str] # A list of labels corresponding to the points in the reference dataset.
                        ) -> List[str]: # A list of labels for each point in the query dataset, determined by majority voting.
    """
    Assigns labels to query dataset points using majority voting from k-nearest neighbors.
    """
    query_labels = []
    for ind in indices:
        neighbor_labels = [reference_labels[i] for i in ind]
        label_counts = Counter(neighbor_labels)
        most_common_label = label_counts.most_common(1)[0][0]
        query_labels.append(most_common_label)
    return query_labels


# %% ../nbs/02_KNN_Label_transfer.ipynb 7
from typing import List as List
from typing import Dict as Dict
from collections import Counter

def knn_weighted_voting(indices: List, # A list of lists, where each sublist contains the indices of the k-nearest neighbors in the reference dataset for a given query point.
                        distances: List, # A list of lists, where each sublist contains the distances of the k-nearest neighbors from a given query point.
                        reference_labels: List # A list of labels corresponding to the points in the reference dataset.
                        ) -> List[str]: # A list of labels for each point in the query dataset, determined by weighted voting.
    """
    Assigns labels to query dataset points using weighted voting from k-nearest neighbors.
    """
    query_labels = []
    for ind, dist in zip(indices, distances):
        weighted_votes: Dict[str, float] = {}
        for i, d in zip(ind, dist):
            label = reference_labels[i]
            weight = 1 / (d + 1e-6)  # Adding a small constant to avoid division by zero
            weighted_votes[label] = weighted_votes.get(label, 0) + weight
        most_common_label = max(weighted_votes, key=weighted_votes.get)
        query_labels.append(most_common_label)
    return query_labels


# %% ../nbs/02_KNN_Label_transfer.ipynb 9
import numpy as np
from collections import defaultdict, Counter


def calculate_centroids(reference_data: List[List[float]], # A list of lists, where each sublist represents a data point in the reference dataset.
                        reference_labels: List[str] # A list of labels corresponding to the points in the reference dataset.
                        ) -> Dict[str, np.ndarray]: # Returns a dictionary where each key is a label and the corresponding value is the centroid of that label.
    """
    Calculates the centroids for each label in the reference dataset.
    """
    

    # Initialize a dictionary to store the sum of data points for each label.
    label_sums = defaultdict(lambda: np.zeros(len(reference_data[0])))
    
    # Count the number of occurrences of each label in the reference dataset.
    label_counts = Counter(reference_labels)
    
    # For each data point and its corresponding label in the reference dataset,
    # add the data point to the sum of data points for that label.
    for data, label in zip(reference_data, reference_labels):
        label_sums[label] += np.array(data)
    
    # Calculate the centroid for each label by dividing the sum of data points for that label by the count of that label.
    centroids = {label: label_sums[label] / count for label, count in label_counts.items()}
    
    return centroids


# %% ../nbs/02_KNN_Label_transfer.ipynb 10
def assign_labels_by_nearest_centroid(query_data: List[List[float]], # A list of lists, where each sublist represents a data point in the query dataset.
                                      centroids: Dict[str, np.ndarray] # A dictionary where each key is a label and the corresponding value is the centroid of that label.
                                      ) -> List[str]: # Returns a list of labels assigned to each point in the query dataset based on the nearest centroid.
    """
    Assigns labels to each point in the query dataset based on the nearest centroid.
    """
    # Initialize an empty list to store the labels for the query data points.
    query_labels = []
    
    # For each data point in the query dataset,
    for data in query_data:
        # Convert the data point to a numpy array.
        data_point = np.array(data)
        
        # Find the label of the centroid closest to the data point.
        # The closest centroid is the one with the least Euclidean distance from the data point.
        closest_label = min(centroids.keys(), key=lambda label: np.linalg.norm(data_point - centroids[label]))
        
        # Append the label of the closest centroid to the list of labels for the query data points.
        query_labels.append(closest_label)
    
    # Return the list of labels for the query data points.
    return query_labels

# %% ../nbs/02_KNN_Label_transfer.ipynb 12
from typing import List, Optional, Union, Tuple


def labels(embedding_array_reference: np.ndarray, # A numpy array representing the reference dataset.
                       embedding_array_query: np.ndarray, # A numpy array representing the query dataset.
                       reference_labels: List[str], # A list of labels for the reference dataset.
                       k: int = 1, # The number of nearest neighbors to consider for label assignment.
                       use_gpu: bool = True, # Whether to use GPU for computation.
                       batch_size: Optional[int] = None, # The size of the batch for computation. If None, the entire query dataset is processed in one batch.
                       distance_metric: str = 'L2', # The distance metric to use. Can be 'L2' or 'IP'.
                       label_consensus: str = 'majority_voting', # The label consensus method to use. Can be 'majority_voting', 'weighted_voting', or 'centroid_based'.
                       timed: bool = False # Whether to return the time taken for label transfer.
                       ) -> Union[List[str], Tuple[List[str], float]]: # Returns a list of labels for the query dataset. If timed is True, also returns the time taken for label transfer.
    
    "Transfers labels from a reference dataset to a query dataset using FAISS."
    
    
    from collections import Counter, defaultdict
    import numpy as np
    import faiss
    import time
    
    start_time = time.time()
    dimension = embedding_array_reference.shape[1]
    res = faiss.StandardGpuResources() if use_gpu else None
    if use_gpu:
        res.noTempMemory()
    if distance_metric == 'L2':
        index = faiss.GpuIndexFlatL2(res, dimension) if use_gpu else faiss.IndexFlatL2(dimension)
    elif distance_metric == 'IP':
        index = faiss.GpuIndexFlatIP(res, dimension) if use_gpu else faiss.IndexFlatIP(dimension)
    else:
        raise ValueError("Invalid distance metric. Choose 'L2' or 'IP'.")
    index.add(embedding_array_reference)
    num_query_points = embedding_array_query.shape[0]
    batch_size = batch_size or num_query_points
    query_labels = []
    for i in range(0, num_query_points, batch_size):
        batch_query = embedding_array_query[i:i + batch_size]
        distances, indices = index.search(batch_query, k)
        if k > 1 and label_consensus == 'majority_voting':
            batch_labels = knn_majority_voting(indices, reference_labels)
        elif k > 1 and label_consensus == 'weighted_voting':
            batch_labels = knn_weighted_voting(indices, distances, reference_labels)
        elif label_consensus == 'centroid_based':
            if i == 0:  # Calculate centroids only once
                centroids = calculate_centroids(embedding_array_reference, reference_labels)
            batch_labels = assign_labels_by_nearest_centroid(batch_query, centroids)
        else:
            batch_labels = [reference_labels[i[0]] for i in indices]
        query_labels.extend(batch_labels)
    end_time = time.time()
    duration_minutes = (end_time - start_time) / 60
    if timed:
        return query_labels, duration_minutes
    else:
        return query_labels
# End of Selection