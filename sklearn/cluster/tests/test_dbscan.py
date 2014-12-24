"""
Tests for DBSCAN clustering algorithm
"""

import pickle

import numpy as np
from numpy.testing import assert_raises

from scipy.spatial import distance
from scipy import sparse

from sklearn.utils.testing import assert_equal
from sklearn.utils.testing import assert_array_equal
from sklearn.utils.testing import assert_raises
from sklearn.cluster.dbscan_ import DBSCAN
from sklearn.cluster.dbscan_ import dbscan
from .common import generate_clustered_data
from sklearn.metrics.pairwise import pairwise_distances


n_clusters = 3
X = generate_clustered_data(n_clusters=n_clusters)


def test_dbscan_similarity():
    """Tests the DBSCAN algorithm with a similarity array."""
    # Parameters chosen specifically for this task.
    eps = 0.15
    min_samples = 10
    # Compute similarities
    D = distance.squareform(distance.pdist(X))
    D /= np.max(D)
    # Compute DBSCAN
    core_samples, labels = dbscan(D, metric="precomputed", eps=eps,
                                  min_samples=min_samples)
    # number of clusters, ignoring noise if present
    n_clusters_1 = len(set(labels)) - (1 if -1 in labels else 0)

    assert_equal(n_clusters_1, n_clusters)

    db = DBSCAN(metric="precomputed", eps=eps, min_samples=min_samples)
    labels = db.fit(D).labels_

    n_clusters_2 = len(set(labels)) - int(-1 in labels)
    assert_equal(n_clusters_2, n_clusters)


def test_dbscan_feature():
    """Tests the DBSCAN algorithm with a feature vector array."""
    # Parameters chosen specifically for this task.
    # Different eps to other test, because distance is not normalised.
    eps = 0.8
    min_samples = 10
    metric = 'euclidean'
    # Compute DBSCAN
    # parameters chosen for task
    core_samples, labels = dbscan(X, metric=metric, eps=eps,
                                  min_samples=min_samples)

    # number of clusters, ignoring noise if present
    n_clusters_1 = len(set(labels)) - int(-1 in labels)
    assert_equal(n_clusters_1, n_clusters)

    db = DBSCAN(metric=metric, eps=eps, min_samples=min_samples)
    labels = db.fit(X).labels_

    n_clusters_2 = len(set(labels)) - int(-1 in labels)
    assert_equal(n_clusters_2, n_clusters)


def test_dbscan_sparse():
    core_sparse, labels_sparse = dbscan(sparse.lil_matrix(X), eps=.8,
                                        min_samples=10, random_state=0)
    core_dense, labels_dense = dbscan(X, eps=.8, min_samples=10,
                                      random_state=0)
    assert_array_equal(core_dense, core_sparse)
    assert_array_equal(labels_dense, labels_sparse)


def test_dbscan_callable():
    """Tests the DBSCAN algorithm with a callable metric."""
    # Parameters chosen specifically for this task.
    # Different eps to other test, because distance is not normalised.
    eps = 0.8
    min_samples = 10
    # metric is the function reference, not the string key.
    metric = distance.euclidean
    # Compute DBSCAN
    # parameters chosen for task
    core_samples, labels = dbscan(X, metric=metric, eps=eps,
                                  min_samples=min_samples,
                                  algorithm='ball_tree')

    # number of clusters, ignoring noise if present
    n_clusters_1 = len(set(labels)) - int(-1 in labels)
    assert_equal(n_clusters_1, n_clusters)

    db = DBSCAN(metric=metric, eps=eps, min_samples=min_samples,
                algorithm='ball_tree')
    labels = db.fit(X).labels_

    n_clusters_2 = len(set(labels)) - int(-1 in labels)
    assert_equal(n_clusters_2, n_clusters)


def test_dbscan_balltree():
    """Tests the DBSCAN algorithm with balltree for neighbor calculation."""
    eps = 0.8
    min_samples = 10

    D = pairwise_distances(X)
    core_samples, labels = dbscan(D, metric="precomputed", eps=eps,
                                  min_samples=min_samples)

    # number of clusters, ignoring noise if present
    n_clusters_1 = len(set(labels)) - int(-1 in labels)
    assert_equal(n_clusters_1, n_clusters)

    db = DBSCAN(p=2.0, eps=eps, min_samples=min_samples, algorithm='ball_tree')
    labels = db.fit(X).labels_

    n_clusters_2 = len(set(labels)) - int(-1 in labels)
    assert_equal(n_clusters_2, n_clusters)

    db = DBSCAN(p=2.0, eps=eps, min_samples=min_samples, algorithm='kd_tree')
    labels = db.fit(X).labels_

    n_clusters_3 = len(set(labels)) - int(-1 in labels)
    assert_equal(n_clusters_3, n_clusters)

    db = DBSCAN(p=1.0, eps=eps, min_samples=min_samples, algorithm='ball_tree')
    labels = db.fit(X).labels_

    n_clusters_4 = len(set(labels)) - int(-1 in labels)
    assert_equal(n_clusters_4, n_clusters)

    db = DBSCAN(leaf_size=20, eps=eps, min_samples=min_samples,
                algorithm='ball_tree')
    labels = db.fit(X).labels_

    n_clusters_5 = len(set(labels)) - int(-1 in labels)
    assert_equal(n_clusters_5, n_clusters)


def test_input_validation():
    """DBSCAN.fit should accept a list of lists."""
    X = [[1., 2.], [3., 4.]]
    DBSCAN().fit(X)             # must not raise exception


def test_dbscan_badargs():
    """Test bad argument values: these should all raise ValueErrors"""
    assert_raises(ValueError,
                  dbscan,
                  X, eps=-1.0)
    assert_raises(ValueError,
                  dbscan,
                  X, algorithm='blah')
    assert_raises(ValueError,
                  dbscan,
                  X, metric='blah')
    assert_raises(ValueError,
                  dbscan,
                  X, leaf_size=-1)
    assert_raises(ValueError,
                  dbscan,
                  X, p=-1)


def test_pickle():
    obj = DBSCAN()
    s = pickle.dumps(obj)
    assert_equal(type(pickle.loads(s)), obj.__class__)


def test_weighted_dbscan():
    sample_weight = np.random.randint(0, 5, X.shape[0])

    # ensure sample_weight is validated
    assert_raises(ValueError, dbscan, [[0], [1]], sample_weight=[2])
    assert_raises(ValueError, dbscan, [[0], [1]], sample_weight=[2, 3, 4])

    # ensure sample_weight has an effect
    assert_array_equal([], dbscan([[0], [1]], sample_weight=None,
                                  min_samples=5)[0])
    assert_array_equal([], dbscan([[0], [1]], sample_weight=[5, 5],
                                  min_samples=5)[0])
    assert_array_equal([0], dbscan([[0], [1]], sample_weight=[6, 5],
                                   min_samples=5)[0])
    assert_array_equal([0, 1], dbscan([[0], [1]], sample_weight=[6, 6],
                                      min_samples=5)[0])

    # points within eps of each other:
    assert_array_equal([0, 1], dbscan([[0], [1]], eps=1.5,
                                      sample_weight=[5, 1], min_samples=5)[0])
    # and effect of non-positive and non-integer sample_weight:
    assert_array_equal([], dbscan([[0], [1]], sample_weight=[5, 0],
                                  eps=1.5, min_samples=5)[0])
    assert_array_equal([0, 1], dbscan([[0], [1]], sample_weight=[5, 0.1],
                                      eps=1.5, min_samples=5)[0])
    assert_array_equal([0, 1], dbscan([[0], [1]], sample_weight=[6, 0],
                                      eps=1.5, min_samples=5)[0])
    assert_array_equal([], dbscan([[0], [1]], sample_weight=[6, -1],
                                  eps=1.5, min_samples=5)[0])

    # for non-negative sample_weight, cores should be identical to repetition
    core1, label1 = dbscan(X, sample_weight=sample_weight, random_state=42)
    assert_equal(len(label1), len(X))

    X_repeated = np.repeat(X, sample_weight, axis=0)
    core_repeated, label_repeated = dbscan(X_repeated)
    core_repeated_mask = np.zeros(X_repeated.shape[0], dtype=bool)
    core_repeated_mask[core_repeated] = True
    core_mask = np.zeros(X.shape[0], dtype=bool)
    core_mask[core1] = True
    assert_array_equal(np.repeat(core_mask, sample_weight), core_repeated_mask)

    # sample_weight should work with precomputed distance matrix
    D = pairwise_distances(X)
    core3, label3 = dbscan(D, sample_weight=sample_weight,
                           metric='precomputed', random_state=42)
    assert_array_equal(core1, core3)
    assert_array_equal(label1, label3)

    # sample_weight should work with estimator
    est = DBSCAN(random_state=42).fit(X, sample_weight=sample_weight)
    core4 = est.core_sample_indices_
    label4 = est.labels_
    assert_array_equal(core1, core4)
    assert_array_equal(label1, label4)
