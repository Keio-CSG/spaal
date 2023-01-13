from typing import Tuple

import numpy as np


def split_injection_remained_points(
        observed_all_points: np.ndarray,
        observed_truth_points: np.ndarray
) -> Tuple[np.ndarray, np.ndarray]:
    op1 = (observed_all_points[:,0] * 1000).astype(int) * 1000 + (observed_all_points[:,1] * 10).astype(int)
    op2 = (observed_truth_points[:,0] * 1000).astype(int) * 1000 + (observed_truth_points[:,1] * 10).astype(int)
    inter, op1_indices, op2_indices = np.intersect1d(op1, op2, assume_unique=True, return_indices=True)
    remained_points = observed_all_points[op1_indices,:]
    injection_mask = np.full((observed_all_points.shape[0],), True)
    injection_mask[op1_indices] = False
    injection_points = observed_all_points[injection_mask,:]
    return injection_points, remained_points
